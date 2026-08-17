"""
Haberleri cekip dosya sistemine kaydetme is akisini (Use Case) yonetir.
"""
import hashlib
from datetime import datetime
from src.domain.entities.news import News
from src.application.interfaces import IWebFetcher, IContentCleaner, INewsRepository, IScraperGateway


class FetchNewsUseCase:
    def __init__(self, scraper, fetcher, cleaner, repo):
        self.scraper = scraper
        self.fetcher = fetcher
        self.cleaner = cleaner
        self.repo = repo

    def _generate_hash(self, text):
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def execute_static(self, source_name, folder_path):
        links = self.scraper.get_static_links()
        return self._process_links(links, source_name, folder_path)

    def execute_news(self, source_name, folder_path):
        links = self.scraper.get_news_links()
        return self._process_links(links, source_name, folder_path)

    def _process_links(self, links, source_name, folder_path):
        results = {'yeni': 0, 'degisti': 0, 'aynı': 0, 'hata': 0}
        for link_info in links:
            url = link_info['url']
            title = link_info['title']
            filename_hint = link_info.get('filename_hint') or None

            html = self.fetcher.fetch(url)
            content = self.cleaner.clean(html) if html else None
            if not content:
                results['hata'] += 1
                continue

            publish_date = link_info.get('publish_date') or None
            if not publish_date:
                publish_date = self.cleaner.extract_publish_date(html)

            news = News(
                source=source_name,
                url=url,
                title=title,
                fetch_date=datetime.now().strftime('%Y-%m-%d'),
                body=content,
                hash=self._generate_hash(content),
                publish_date=publish_date,
                filename_hint=filename_hint,
            )
            previous_hash = self.repo.get_existing_hash(news, folder_path)
            if previous_hash == news.hash:
                results['aynı'] += 1
                continue
            self.repo.save(news, folder_path)
            results['yeni' if previous_hash is None else 'degisti'] += 1
        return results