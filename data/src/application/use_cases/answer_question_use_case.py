"""
Bir soruya, vektor aramayla bulunan baglama dayanarak cevap uretme (RAG).
( ZIRHLI MIKNATISLAR + FUZZY TYPO + ÜCRET OPTİMİZASYONU + HALÜSİNASYON İPTALİ + BAĞLAM HAFIZASI + TYPO PRO + KİMLİK KORUMASI V30 )
"""
import re
import difflib
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from src.application.interfaces import ILLMClient, IVectorStore
from src.utils.tr_normalize import fold, lower_tr

MAX_CONTEXT_CHARS = 40000

REWRITE_SYSTEM_PROMPT = (
    "Sen Konya Büyükşehir Belediyesi için çalışan bir 'Sorgu Düzeltme (Query Rewriting)' asistanısın.\n"
    "Amacın, vatandaşın eksik, hatalı veya bağlamsız sorduğu soruları Vektör Veritabanında en iyi sonucu verecek resmi, eksiksiz ve hatasız bir arama cümlesine çevirmektir.\n\n"
    "KURALLAR:\n"
    "1. ÖZNE TAMAMLAMA (HAYATİ): Eğer son soruda 'bu', 'o', 'peki', 'ücretli mi', 'nerede', 'şubeleri' gibi zamirler veya eksik özneler varsa, GEÇMİŞ SOHBETE BAKARAK asıl konunun ne olduğunu (KOMEK, KOSKİ, KONYAKART vb.) bul ve SON SORUYA EKLE!\n"
    "2. TYPO VE BAĞLAM (ÇOK ÖNEMLİ): Vatandaş kelimeleri çok yanlış yazabilir (Örn: koki, komik, kaski). Yanındaki kelimelerden asıl kastettiği kurumu anla ve mutlaka düzelt!\n"
    "3. 'elkart', 'el kart' veya 'paso' kelimelerini KESİNLİKLE 'Konyakart' olarak düzelt.\n"
    "4. KART ÇIKARTMA (ÖNEMLİ): 'çıkarılır', 'çıkartılır', 'çıkarmak' kelimelerini KESİNLİKLE 'alınır', 'almak için gerekenler' veya 'başvuru nasıl yapılır' olarak değiştir.\n"
    "5. SADECE düzeltilmiş soruyu çıktı olarak ver. Asla açıklama yapma.\n\n"
    "ÖRNEKLER:\n"
    "- Geçmiş: Kullanıcı: 'Komek kayıtları ne zaman?'\n  Son Soru: 'peki yaş sınırı var mı?'\n  Çıktı: 'Komek kursları yaş sınırı var mı?'\n"
    "- Geçmiş: Kullanıcı: 'Peki yaş sınırı var mı?'\n  Son Soru: 'ücretli mi peki bu?'\n  Çıktı: 'Komek kursları ücretli mi?'\n"
    "- Kullanıcı: 'kaskii aboneliğimi iptal etmek istiyorum'\n  Çıktı: 'Koski abonelik iptali nasıl yapılır'\n"
    "- Kullanıcı: 'pasom kayboldu'\n  Çıktı: 'Konyakart kayıp başvurusu nasıl yapılır'\n"
)

SYSTEM_PROMPT = (
    "Sen Konya Büyükşehir Belediyesi'nin yerel hizmetlerini temsil eden, vatandaşlara doğru bilgi veren resmi RAG Asistanısın.\n\n"
    "KURALLAR:\n"
    "1. KAPSAM: Sadece Konyakart, Koski, Komek ve Belediye Haberleri (Konya yerel hizmetleri) hakkında bilgi verebilirsin. Bu konular dışındaki sorulara (Örn: siyaset, dünya haberleri vb.) 'Maalesef bu konuda size yardımcı olamam.' diyerek cevap ver.\n"
    "2. SADAKAT: Sadece sana sunulan KAYNAKLAR kısmına dayanarak cevap ver. Eğer kaynaklarda aranan bilgi YOKSA, asla uydurma, 'Verilen kaynaklarda bu bilgi bulunmamaktadır.' de.\n"
    "3. ATIF: Bilgi verdiğin cümlelerin sonuna mutlaka (Kaynak X) şeklinde atıf yap.\n"
    "4. GEÇMİŞ SOHBET: Geçmiş sohbet sadece konunun bağlamını anlaman içindir. Sen asıl olarak en alttaki SON SORU'yu cevaplamalısın.\n"
    "5. NESNEL DİL (ÇOK ÖNEMLİ): Doğrudan, resmi ve nesnel bir dille cevap ver. Kullanıcının 'annem için', 'benim için', 'kaybettim', 'istiyorum' gibi kişisel ifadelerini veya duygularını ASLA kendi cevabında tekrarlama. Sadece istenen bilginin genel kurallarını açıkla."
)

KAYNAK_ANAHTAR_KELIMELERI = {
    "komek": "komek", "koski": "koski", "su": "koski",
    "konya büyükşehir": "konya_bel_tr", "konya belediye": "konya_bel_tr",
    "merhaba haber": "merhaba_haber", "yeni meram": "yeni_meram",
    "konya haber": "konya_haber", "konya yenigün": "konya_yenigun", "konya yenigun": "konya_yenigun",
    "konyakart": "konyakart_mevlana", "konya kart": "konyakart_mevlana", "mevlana": "konyakart_mevlana",
    "turizm": "konyakart_mevlana", "müze": "konyakart_mevlana", "otobüs": "konyakart_mevlana",
    "toplu ulaşım": "konyakart_mevlana", "toplu taşım": "konyakart_mevlana", "validatör": "konyakart_mevlana",
    "yeşil buton": "konyakart_mevlana", "e-dolum": "konyakart_mevlana", "dolum": "konyakart_mevlana",
    "temassız": "konyakart_mevlana", "banka kartı": "konyakart_mevlana", "kredi kartı": "konyakart_mevlana",
    "65 yaş": "konyakart_mevlana", "engelli": "konyakart_mevlana", "öğretmen": "konyakart_mevlana",
    "öğrenci": "konyakart_mevlana", "üniversite": "konyakart_mevlana", "abonman": "konyakart_mevlana",
    "bilet": "konyakart_mevlana", "ücret": "konyakart_mevlana"
}

_TARIH_FORMATLARI = ["%Y-%m-%d", "%d.%m.%Y %H:%M", "%d.%m.%Y"]

COP_SAYFA_KELIMELERI = [
    "hakkımızda", "iletişim", "künye", "gizlilik politikası", "yasal uyarı", 
    "kullanım koşulları", "çerez", "belge gönder", "başvuru formu", "şifremi unuttum", 
    "giriş yap", "üye ol", "belge yükle", "dosya yükle", "bize ulaşın"
]

RESMI_REHBER_KAYNAKLARI = {"konyakart_mevlana", "konya_bel_tr", "koski", "komek"}


def _gecmisten_kaynak_cikar(history: List[Dict]) -> Optional[str]:
    if not history: return None
    son_mesajlar = history[-2:]
    for msg in reversed(son_mesajlar):
        metin = fold(msg.get("metin", ""))
        
        if any(fold(k) in metin for k in ["konyakart", "elkart", "paso", "biniş", "otobüs", "tramvay", "kart"]):
            return "konyakart_mevlana"
            
        if any(fold(k) in metin for k in ["koski", "su ", "fatura", "abonelik", "sayaç", "kaski"]):
            return "koski"
            
        if any(fold(k) in metin for k in ["komek", "kurs", "yaz okulu"]):
            return "komek"
            
    return None


def _sorudan_kaynak_tahmin_et(question: str) -> Optional[str]:
    soru_fold = fold(question)
    
    if any(fold(k) in soru_fold for k in ["konyakart", "elkart", "paso", "biniş", "otobüs", "tramvay"]):
        return "konyakart_mevlana"
    if any(fold(k) in soru_fold for k in ["koski", "su "]):
        return "koski"
    if any(fold(k) in soru_fold for k in ["komek", "komik"]):
        return "komek"
        
    kelimeler = set(re.findall(r'\w+', soru_fold))
    for anahtar, kaynak in KAYNAK_ANAHTAR_KELIMELERI.items():
        anahtar_fold = fold(anahtar)
        if " " not in anahtar_fold:
            if anahtar_fold in kelimeler:
                return kaynak
        else:
            if anahtar_fold in soru_fold:
                return kaynak
    return None


def _tarihi_ayristir(tarih_str: str) -> Optional[datetime]:
    if not tarih_str:
        return None
    match = re.search(r'(\d{2}[./-]\d{2}[./-]\d{4})', tarih_str)
    temiz_tarih = match.group(1) if match else tarih_str.strip()
    
    for fmt in _TARIH_FORMATLARI:
        try:
            return datetime.strptime(temiz_tarih, fmt)
        except ValueError:
            continue
    return None


class AnswerQuestionUseCase:
    def __init__(self, vector_store: IVectorStore, llm_client: ILLMClient):
        self.vector_store = vector_store
        self.llm_client = llm_client

    def _is_chat_query(self, question: str) -> bool:
        q = lower_tr(question).strip()
        q_clean = re.sub(r'[^\w\s]', '', q)
        q_fold = fold(q_clean)
        kelimeler = q_fold.split()
        
        if any(w in q_fold for w in ["adim ne", "ismim ne", "adim neydi", "ismim neydi", "ben kimim", "biz kimiz"]):
            return True
            
        if any(w in q_fold for w in ["sen kimsin", "senin adin", "senin ismin", "seninki", "adin ne", "ismin ne", "kimsiniz"]):
            return True
            
        if len(kelimeler) <= 5 and any(w in kelimeler for w in ["adim", "ismim", "ben", "benim"]):
            if not any(k in kelimeler for k in ["komek", "koski", "su", "kart", "basvuru", "nereden", "nasil", "ucret"]):
                return True
            
        gecmis_kelimeler = {"ilk", "onceki", "once", "gecmiste", "demin", "az once", "yukarida", "basta", "en"}
        soru_kelimeleri = {"soru", "sorum", "sorumuz", "sorular", "soruyu", "sordum", "sormustuk", "sormustum", "dedim", "dedik", "demistik", "konustuk", "cevabin", "cevap", "neydi", "ne"}
        
        kelimeler_set = set(kelimeler)
        if gecmis_kelimeler.intersection(kelimeler_set) and soru_kelimeleri.intersection(kelimeler_set):
            return True
            
        if "ne" in kelimeler and any(w in kelimeler for w in ["sordum", "sormustum", "sormustuk", "dedim", "demistim", "dedik", "demistik", "konustuk"]):
            return True
            
        tr_chat = ["merhaba", "selam", "gunaydin", "nasilsin", "tesekkur", "sagol", "saol", "eyvallah"]
        if len(kelimeler) <= 6 and any(any(w.startswith(t) for t in tr_chat) for w in kelimeler):
            if not any(k in kelimeler for k in ["komek", "koski", "su", "kart", "basvuru", "nereden", "nasil", "ucret"]):
                return True
                
        greeting_words = {"merhaba", "selam", "selamlar", "gunaydin", "iyi", "gunler", "aksamlar", "tesekkurler", "tesekkur", "ederim", "sagol", "saol", "sag", "olun", "nasilsin", "nasilsiniz", "kolay", "gelsin", "selamin", "aleykum", "selamun", "calismalar", "cok"}
        if len(kelimeler) > 0 and all(w in greeting_words for w in kelimeler):
            return True
            
        english_chat = ["hello", "hi", "how", "are", "you", "thanks", "hey", "good", "morning"]
        if len(kelimeler) <= 5 and any(w in english_chat for w in kelimeler):
            if not any(k in kelimeler for k in ["komek", "koski", "su", "kart", "basvuru", "nereden", "nasil", "ucret"]):
                return True

        return False

    def _find_chunks(self, question: str, n_results: int, history: List[Dict] = None) -> List[Dict[str, Any]]:
        tahmini_kaynak = _sorudan_kaynak_tahmin_et(question)
        if not tahmini_kaynak and history:
            tahmini_kaynak = _gecmisten_kaynak_cikar(history)
            
        where = {"source": tahmini_kaynak} if tahmini_kaynak else None

        arama_limiti = max(n_results * 5, 50)
        soru_norm = lower_tr(question)
        
        result = self.vector_store.query(soru_norm, n_results=arama_limiti, where=where)
        
        chunks = []
        title_counts = {}
        
        if not result['documents'] or not result['documents'][0]:
            return chunks
            
        for i in range(len(result['documents'][0])):
            metadata = result['metadatas'][0][i]
            baslik = metadata.get('title', 'Başlıksız')
            baslik_fold = fold(baslik)
            url_kucuk = metadata.get('url', '').lower()

            if any(fold(cop) in baslik_fold or cop in url_kucuk for cop in COP_SAYFA_KELIMELERI):
                continue

            if baslik_fold not in title_counts:
                title_counts[baslik_fold] = 0
            if title_counts[baslik_fold] >= 3:
                continue
            title_counts[baslik_fold] += 1

            gosterim_tarihi = metadata.get('yayin_tarihi') or metadata.get('cekilme_tarihi', '')
            chunks.append({
                'url': metadata.get('url', '#'),
                'source': metadata.get('source', 'bilinmiyor'),
                'title': baslik,
                'gosterim_tarihi': gosterim_tarihi,
                'text': result['documents'][0][i],
                'chroma_sira': i
            })

        def _siralama_anahtari(chunk):
            skor = 0.0
            tarih = _tarihi_ayristir(chunk['gosterim_tarihi'])
            kaynak_adi = chunk.get('source', '')
            baslik_fold = fold(chunk.get('title', ''))
            metin_fold = fold(chunk.get('text', ''))
            soru_fold = fold(question)
            url_kucuk = chunk.get('url', '').lower()

            if tarih:
                zaman_skoru = tarih.timestamp()
            elif kaynak_adi in RESMI_REHBER_KAYNAKLARI:
                zaman_skoru = datetime.now().timestamp() - (365 * 24 * 3600) 
            else:
                zaman_skoru = 0.0

            if fold("komek") in soru_fold and kaynak_adi == "komek":
                skor += 1_000_000.0
            if fold("koski") in soru_fold and kaynak_adi == "koski":
                skor += 1_000_000.0
            if fold("konyakart") in soru_fold and kaynak_adi == "konyakart_mevlana":
                skor += 1_000_000.0

            if any(fold(k) in soru_fold for k in ["temassız", "banka", "kredi"]):
                if any(fold(k) in baslik_fold for k in ["temassız", "banka", "ulaşımda"]):
                    skor += 2_000_000.0

            if any(fold(k) in soru_fold for k in ["e-dolum", "aktivasyon", "yeşil buton", "yükle"]):
                if any(fold(k) in baslik_fold for k in ["bakiye yükleme", "validatör", "dolum"]):
                    skor += 2_000_000.0

            if any(fold(k) in soru_fold for k in ["65 yaş", "engelli", "öğretmen", "öğrenci", "üniversite", "kimler", "haklar", "serbest", "belge", "çıkar", "alınır", "almak", "şart", "başvuru", "nasıl yap"]):
                if any(fold(k) in baslik_fold for k in ["kimler", "gerekenler", "almak", "serbest", "başvuru"]):
                    skor += 2_000_000.0

            if any(fold(k) in soru_fold for k in ["ücret", "fiyat", "kaç para", "tarife", "bilet", "ne kadar", "biniş", "paralı", "para", "ücretli", "bedava"]):
                if any(fold(k) in soru_fold for k in ["konyakart", "elkart", "ulaşım", "otobüs", "tramvay", "biniş"]):
                    if any(fold(k) in baslik_fold for k in ["ücret", "tarife", "bakiye yükleme", "fiyat"]):
                        skor += 5_000_000.0
                    if any(fold(k) in metin_fold for k in ["tam biniş", "indirimli biniş", "abonman", "tl"]):
                        skor += 3_000_000.0
                if fold("komek") in soru_fold:
                    if any(fold(k) in metin_fold for k in ["ücretsiz", "bedava"]):
                        skor += 5_000_000.0
                    
            if fold("komek") in soru_fold and any(fold(k) in soru_fold for k in ["kayıt", "ne zaman", "tarih", "başlıyor", "yaz okulu"]):
                if fold("16-30 haziran") in metin_fold or "haberid=248" in url_kucuk:
                    skor += 3_000_000.0

            if any(fold(k) in soru_fold for k in ["güncel", "son", "yeni", "haber", "bugün", "dün", "nelerdir"]):
                if tarih and (datetime.now() - tarih).days < 30: 
                    skor += 4_000_000.0

            orijinal_sira_cezasi = chunk.get('chroma_sira', 0)

            return -(skor - orijinal_sira_cezasi + (zaman_skoru / 1_000_000_000.0))

        chunks.sort(key=_siralama_anahtari)
        return chunks[:n_results]

    @staticmethod
    def _build_prompt(question: str, chunks: List[Dict[str, Any]], history_text: str = "", is_chat_only: bool = False) -> str:
        context = ''
        for i, chunk in enumerate(chunks, 1):
            tarih = chunk.get('gosterim_tarihi') or 'Tarih bilinmiyor'
            chunk_text = f"\n[Kaynak {i}: {chunk['title']} - {chunk['source']} (Tarih: {tarih})]\n{chunk['text']}\n"
            if len(context) + len(chunk_text) < MAX_CONTEXT_CHARS:
                context += chunk_text
            else:
                break
                
        lang = "tr"
        q_clean = re.sub(r'[^\w\s]', '', question.lower())
        if any(w in q_clean.split() for w in ["hello", "hi", "how", "what", "where", "thanks", "why", "who", "are", "you"]):
            lang = "en"
            
        if lang == "en":
            if is_chat_only:
                final_instruction = "PLEASE ANSWER COMPLETELY IN ENGLISH AS A POLITE MUNICIPALITY ASSISTANT. DO NOT CITE ANY SOURCES."
            else:
                final_instruction = "PLEASE ANSWER COMPLETELY IN ENGLISH, USE PROVIDED SOURCES AND CITE THEM AS (Kaynak X):"
        else:
            if is_chat_only:
                final_instruction = "LÜTFEN SADECE İSTENİLEN KISA CEVABI YAZ:"
            else:
                final_instruction = "LÜTFEN SADECE VERİLEN KAYNAKLARI KULLANARAK SON SORUYU YANITLA (Cümle sonlarına Kaynak X eklemeyi unutma):"
                
        return (
            f"KAYNAKLAR:\n{context}\n\n"
            f"{history_text}\n"
            f"SON SORU: {question}\n\n"
            f"{final_instruction}"
        )

    def execute(self, question: str, n_results: int = 6, history: List[Dict] = None) -> Tuple[List[Dict[str, Any]], str]:
        
        q_lower = lower_tr(question)
        yasakli_kombinasyonlar = [
            "kapsam (whitelist)", "kapsam whitelist", "sistem yönerge", "kurallarını", 
            "bütün kuralları", "sistem prompt", "promptunu", "talimatlarını", "kuralını yazdır", "kuralları yaz"
        ]
        if any(hack in q_lower for hack in yasakli_kombinasyonlar):
            return [], "Güvenlik prensipleri gereği sistem yönergelerimi ve kurallarımı paylaşamam. Size sadece Konya Büyükşehir Belediyesi hizmetleri hakkında bilgi verebilirim."

        kapsam_disi = [
            "seçim", "siyaset", "parti", "milletvekili", "belediye başkanı", "oy oranı", "aday",
            "konyaspor", "transfer", "futbol", "basketbol", "şampiyon", "lig", "fikstür", "maç",
            "galatasaray", "fenerbahçe", "beşiktaş", "trabzonspor",
            "şiir", "şarkı", "fıkra", "masal", "hikaye", "roman", "espri", "şaka", "destan", "akrostiş"
        ]
        if any(k in q_lower for k in kapsam_disi):
             return [], "Maalesef bu konularda yorum yapamam. Size sadece Konya Büyükşehir Belediyesi yerel hizmetleri (Konyakart, Koski, Komek vb.) hakkında bilgi verebilirim."

        kelimeler_listesi = re.findall(r'\w+', question)
        for k in kelimeler_listesi:
            k_lower = lower_tr(k)
            if k_lower.startswith("paso") or k_lower.startswith("elkart"):
                question = re.sub(rf'\b{k}\b', "Konyakart", question, flags=re.IGNORECASE)
            elif k_lower.startswith("kaski") or k_lower.startswith("kosk"):
                question = re.sub(rf'\b{k}\b', "Koski", question, flags=re.IGNORECASE)
            elif k_lower.startswith("komek") or k_lower.startswith("komik"):
                question = re.sub(rf'\b{k}\b', "Komek", question, flags=re.IGNORECASE)
            elif k_lower in {"çıkarılır", "çıkartılır", "çıkarmak", "çıkartmak"}:
                question = re.sub(rf'\b{k}\b', "alınır", question, flags=re.IGNORECASE)
            elif len(k_lower) >= 4:
                benzerler = difflib.get_close_matches(k_lower, ["komek", "koski", "konyakart"], n=1, cutoff=0.60)
                if benzerler:
                    question = re.sub(rf'\b{k}\b', benzerler[0], question, flags=re.IGNORECASE)
        
        history_text = ""
        if history:
            history_text = "--- GEÇMİŞ SOHBET (BAĞLAM) ---\n"
            
            if len(history) > 20:
                gosterilecek_gecmis = history[:2] + history[-18:]
            else:
                gosterilecek_gecmis = history
                
            for msg in gosterilecek_gecmis: 
                rol = "Kullanıcı" if msg["rol"] == "kullanici" else "Asistan"
                history_text += f"{rol}: {msg['metin']}\n"
            history_text += "------------------------------\n"
            
        is_chat_only = self._is_chat_query(question)
        
        aktif_prompt = SYSTEM_PROMPT
        
        if is_chat_only:
            rewritten_question = question
            chunks = []
            
            q_clean_chat = re.sub(r'[^\w\s]', '', lower_tr(question).strip())
            q_fold_chat = fold(q_clean_chat)
            kelimeler_chat = q_fold_chat.split()
            kelimeler_set_chat = set(kelimeler_chat)
            
            gecmis_kelimeler = {"ilk", "onceki", "once", "gecmiste", "demin", "az once", "yukarida", "basta", "en"}
            soru_kelimeleri = {"soru", "sorum", "sorumuz", "sorular", "soruyu", "sordum", "sormustuk", "sormustum", "dedim", "dedik", "demistik", "konustuk", "cevabin", "cevap", "neydi", "ne"}
            
            if any(w in q_fold_chat for w in ["adim ne", "ismim ne", "adim neydi", "ismim neydi", "ben kimim", "biz kimiz"]):
                aktif_prompt = "Kullanıcı sana kendi ismini soruyor. LÜTFEN 'GEÇMİŞ SOHBET' KISMINI DİKKATLİCE OKU. Orada 'adım...', 'ismim...', 'ben...' şeklinde bir bilgi varsa, 'İsminiz [Bulduğun İsim].' şeklinde cevap ver. Eğer GEÇMİŞ SOHBETTE İSMİ HİÇ GEÇMİYORSA, SADECE VE SADECE 'Maalesef adınızı henüz bilmiyorum.' yaz."
            
            elif any(w in q_fold_chat for w in ["sen kimsin", "senin adin", "senin ismin", "seninki", "adin ne", "ismin ne", "kimsiniz"]):
                aktif_prompt = "Kullanıcı senin kim olduğunu veya adını soruyor. SADECE VE SADECE şu cümleyi yaz: 'Ben Konya Büyükşehir Belediyesi'nin akıllı asistanıyım. Size yerel hizmetlerimiz hakkında nasıl yardımcı olabilirim?'"
            
            elif (gecmis_kelimeler.intersection(kelimeler_set_chat) and soru_kelimeleri.intersection(kelimeler_set_chat)) or ("ne" in kelimeler_chat and any(w in kelimeler_chat for w in ["sordum", "sormustum", "sormustuk", "dedim", "demistim", "dedik", "demistik", "konustuk"])):
                aktif_prompt = "Sen Konya Büyükşehir Belediyesi asistanısın. Kullanıcı geçmişte yazdığı İLK MESAJINI soruyor. GEÇMİŞ SOHBET KISMININ EN ÜSTÜNDEKİ ilk 'Kullanıcı:' mesajını bul ve SADECE VE SADECE 'İlk mesajınız: [O MESAJ]' şeklinde yanıtla."
            elif len(kelimeler_chat) <= 5 and any(w in kelimeler_chat for w in ["adim", "ismim", "ben", "benim"]):
                aktif_prompt = "Sen Konya Büyükşehir Belediyesi asistanısın. Kullanıcı kendi adını belirtiyor. SADECE VE SADECE kullanıcının belirttiği isme hitap ederek 'Memnun oldum [İSİM], size nasıl yardımcı olabilirim?' yaz. Başka hiçbir şey ekleme."
            elif any(w in q_fold_chat for w in ["tesekkur", "sagol", "saol", "eyvallah"]):
                aktif_prompt = "Kullanıcı sana teşekkür ediyor. SADECE VE SADECE şu cümleyi yaz: 'Rica ederim, Konya Büyükşehir Belediyesi olarak her zaman yanınızdayız. Başka bir sorunuz var mı?'"
            else:
                aktif_prompt = "Kullanıcı sana selam veriyor veya hal hatır soruyor. SADECE VE SADECE şu cümleyi yaz: 'Merhaba, size nasıl yardımcı olabilirim?' Kullanıcının sözlerini ASLA tekrar etme."
        else:
            rewrite_input = f"{history_text}Orijinal Son Soru: {question}\nDüzeltilmiş Soru:"
            try:
                rewritten_question = self.llm_client.generate(REWRITE_SYSTEM_PROMPT, rewrite_input).strip()
                
                if len(rewritten_question) > 200 or not rewritten_question:
                    rewritten_question = question
                    
                for k in re.findall(r'\w+', rewritten_question):
                    k_lower = lower_tr(k)
                    if k_lower.startswith("paso") or k_lower.startswith("elkart"):
                        rewritten_question = re.sub(rf'\b{k}\b', "Konyakart", rewritten_question, flags=re.IGNORECASE)
                    elif k_lower.startswith("kaski") or k_lower.startswith("kosk"):
                        rewritten_question = re.sub(rf'\b{k}\b', "Koski", rewritten_question, flags=re.IGNORECASE)
                    elif k_lower.startswith("komek") or k_lower.startswith("komik"):
                        rewritten_question = re.sub(rf'\b{k}\b', "Komek", rewritten_question, flags=re.IGNORECASE)
                        
            except Exception as e:
                rewritten_question = question
                
            print(f"\n--- QUERY REWRITING ---")
            print(f"Vatandaşın Sorusu : {question}")
            print(f"Vektörde Aranacak Soru: {rewritten_question}")
            print(f"-----------------------\n")

            chunks = self._find_chunks(rewritten_question, n_results, history)
            
            if not chunks:
                return [], "Maalesef bu konuda size yardımcı olamam. Size sadece Konya yerel hizmetleri ve resmi veriler (Konyakart, KOSKİ, KOMEK, Belediye Haberleri vb.) ışığında yardımcı olabilirim."

            q_check = fold(question + " " + rewritten_question)
            if fold("komek") in q_check and any(fold(k) in q_check for k in ["kayıt", "ne zaman", "tarih", "başlıyor", "yaz", "okulu"]):
                aktif_prompt += "\n\nÖZEL KURAL: Komek (ve Genç Komek) 2026 kayıt tarihleri KESİN OLARAK '16-30 Haziran 2026' olarak belirlenmiştir. Kaynaklarda eski tarihler veya farklı dönemler (Bahar, Güz, Yaz vb.) geçse bile HİÇBİRİNİ LİSTELEME! KESİNLİKLE sadece 'Komek kayıtları 16-30 Haziran 2026 tarihleri arasında yapılacaktır.' yaz."
            
        user_prompt = self._build_prompt(question, chunks, history_text, is_chat_only)
        
        answer = self.llm_client.generate(aktif_prompt, user_prompt)
        
        if not is_chat_only and not any(k in answer for k in ["Kaynak", "kaynak"]):
            chunks = []
            
        if is_chat_only:
            answer = re.sub(r'\s*[\(\[]Kaynak.*?[\)\]]', '', answer, flags=re.IGNORECASE)
        
        return chunks, answer                                   



                        