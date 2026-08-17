"""
Adapter: INewsRepository'nin Markdown dosyalari ile gerceklestirimi.
"""
import glob
import os
import re
from src.domain.entities.news import News
from src.application.interfaces import INewsRepository


def _slugify(text):
    tr_map = str.maketrans('çğıöşüÇĞİÖŞÜ', 'cgiosuCGIOSU')
    text = text.translate(tr_map).lower()
    text = re.sub('[^a-z0-9]+', '-', text)
    return text.strip('-')[:80] or 'sayfa'


def _build_file_path(folder_path, title, filename_hint):
    if filename_hint:
        stem = f"{filename_hint}-{_slugify(title)}"
    else:
        stem = _slugify(title)
    return os.path.join(folder_path, stem + '.md')


def _parse_frontmatter(content):
    match = re.match(r'^---\n(.*?)\n---\n\n(.*)$', content, re.DOTALL)
    if not match:
        return {}, content
    header, body = match.groups()
    metadata = {}
    for line in header.split('\n'):
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        metadata[key.strip()] = value.strip()
    return metadata, body


class FileRepository(INewsRepository):
    def get_existing_hash(self, news, folder_path):
        file_path = _build_file_path(folder_path, news.title, news.filename_hint)
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'hash:\s*(\S+)', content)
        if match:
            return match.group(1)
        return None

    def save(self, news, folder_path):
        os.makedirs(folder_path, exist_ok=True)
        file_path = _build_file_path(folder_path, news.title, news.filename_hint)
        frontmatter = f"---\nkaynak: {news.source}\nkaynak_url: {news.url}\nbaslik: {news.title}\n"
        if news.publish_date:
            frontmatter += f"yayin_tarihi: {news.publish_date}\n"
        frontmatter += f"cekilme_tarihi: {news.fetch_date}\nhash: {news.hash}\n---\n\n"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter + news.body)
        return file_path

    def list_all(self, data_root='data'):
        results = []
        for file_path in glob.glob(os.path.join(data_root, '**', '*.md'), recursive=True):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            metadata, body = _parse_frontmatter(content)
            file_id = os.path.splitext(os.path.basename(file_path))[0]
            results.append({
                'file_path': file_path,
                'file_id': file_id,
                'source': metadata.get('kaynak', 'unknown'),
                'url': metadata.get('kaynak_url', ''),
                'title': metadata.get('baslik', file_id),
                'content_hash': metadata.get('hash', ''),
                'cekilme_tarihi': metadata.get('cekilme_tarihi', ''),
                'yayin_tarihi': metadata.get('yayin_tarihi', ''),
                'body': body,
            })
        return results