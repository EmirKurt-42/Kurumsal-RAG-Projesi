
"""
data/ altindaki tum belgeleri chunk'layip vektor veritabanina indeksleme.
(OPTİMİZE EDİLMİŞ VERSİYON: Contextual Chunking + Geliştirilmiş Boyutlar + Başlık Kurtarma)
"""
import json
import os
import re
from src.application.interfaces import INewsRepository, IVectorStore

STATE_FILE = 'islenmis_dosyalar.json'
# Optimizasyon: Daha büyük bağlam (1200 harf) ve daha yumuşak geçiş (250 harf overlap)
MAX_CHARS = 1200
OVERLAP_CHARS = 250


class BuildIndexUseCase:
    def __init__(self, repository, vector_store):
        self.repository = repository
        self.vector_store = vector_store

    @staticmethod
    def _chunk(text):
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunks = []
        current = ''
        for paragraph in paragraphs:
            if len(current) + len(paragraph) <= MAX_CHARS:
                current += ('\n\n' if current else '') + paragraph
                continue
            if current:
                chunks.append(current)
            overlap = current[-OVERLAP_CHARS:] if current else ''
            current = (overlap + '\n\n' + paragraph).strip()
        if current:
            chunks.append(current)
        return chunks

    @staticmethod
    def _load_state():
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    @staticmethod
    def _save_state(state):
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def execute(self, reset=False):
        if reset:
            self.vector_store.reset()
            state = {}
        else:
            state = self._load_state()
        all_documents = self.repository.list_all()
        print(f"data/ altinda {len(all_documents)} belge bulundu.")
        to_process = [
            d for d in all_documents
            if state.get(d['file_path']) != d['content_hash']
        ]
        print(f"Islenecek (Optimize edilecek): {len(to_process)} yeni/degismis belge.")
        for doc in to_process:
            already_indexed = doc['file_path'] in state
            if already_indexed:
                self.vector_store.delete_by_file(doc['file_id'])
            
            body_text = doc['body']
            
            # BASLIK KURTARMA (Title Extraction): Çöp başlıkları eziyoruz
            match = re.search(r'^#+\s+(.+)$', body_text, flags=re.MULTILINE)
            if match:
                doc['title'] = match.group(1).strip()
                
            # Gelen saf metni parçalara ayır
            ham_chunks = self._chunk(body_text)
            
            # CONTEXTUAL OPTIMIZATION: Her chunk'ın en başına Başlık ve Kaynak adını ekliyoruz! 
            # Artık makinenin gözünden hiçbir genel soru kaçmaz!
            chunks = [f"[{doc.get('title', 'Başlıksız')}] {chunk_text}" for chunk_text in ham_chunks]

            ids = [f"{doc['source']}_{doc['file_id']}_{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    'source': doc['source'],
                    'url': doc['url'],
                    'title': doc['title'],
                    'file_id': doc['file_id'],
                    'chunk_no': i,
                    'cekilme_tarihi': doc.get('cekilme_tarihi', ''),
                    'yayin_tarihi': doc.get('yayin_tarihi', ''),
                }
                for i in range(len(chunks))
            ]
            self.vector_store.add(ids, chunks, metadatas)
            state[doc['file_path']] = doc['content_hash']
            print(f"  ({doc['source']}) {doc['file_id']}: {len(chunks)} optimize chunk")
        self._save_state(state)
        print(f"Tamamlandı! {len(to_process)} belge süper-indekse alındı.")