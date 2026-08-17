"""
konya.bel.tr icin veri cekme adaptoru.

Site yapisi:
  - Statik sayfalar: /s/{slug} ve /k/{slug}
  - Haberler: /haber/{slug}, listeleme ?sayfa=N ile sayfalanmis (~1428 sayfa
    gecmis var). Sadece EN YENI sayfayi kontrol ediyoruz - gunluk artimli
    kullanim icin yeterli, tam arsivi taramak gereksiz ve yavas olurdu.
"""
import re
from typing import Dict, List
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from src.application.interfaces import IScraperGateway
from src.infrastructure.web.requests_fetcher import USER_AGENT

STATIC_PATTERNS = [
    '/s/[a-z0-9-]+$',
    '/k/[a-z0-9-]+$',
]
NEWS_PATTERN = '/haber/[a-z0-9-]+$'
TRAILING_DATE_PATTERN = re.compile(r'\s*(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2})\s*$')


class KonyaBelTrScraper(IScraperGateway):
    BASE_URL = 'https://www.konya.bel.tr/'
    NEWS_LISTING_URL = 'https://www.konya.bel.tr/haber'
    PAGES_TO_CHECK = 1

    def get_static_links(self):
        headers = {'User-Agent': USER_AGENT}
        r = requests.get(self.BASE_URL, headers=headers, timeout=15)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'html.parser')
        found = {}
        for a in soup.find_all('a', href=True):
            full_url = urljoin(self.BASE_URL, a['href'])
            for pattern in STATIC_PATTERNS:
                if not re.search(pattern, full_url):
                    continue
                found[full_url] = a.get_text(strip=True) or 'Baslik yok'
                break
        return [{'url': u, 'title': t, 'filename_hint': ''} for u, t in found.items()]

    def _news_links_on_page(self, page):
        if page == 1:
            url = self.NEWS_LISTING_URL
        else:
            url = f"{self.NEWS_LISTING_URL}?sayfa={page}"
        headers = {'User-Agent': USER_AGENT}
        r = requests.get(url, headers=headers, timeout=15)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'html.parser')
        found = {}
        for a in soup.find_all('a', href=True):
            full_url = urljoin(self.BASE_URL, a['href'])
            if not re.search(NEWS_PATTERN, full_url):
                continue
            text = a.get_text(strip=True)
            if full_url not in found or len(text) > len(found[full_url]):
                found[full_url] = text or 'Baslik yok'
        results = []
        for u, raw_title in found.items():
            match = TRAILING_DATE_PATTERN.search(raw_title)
            if match:
                publish_date = match.group(1)
                title = TRAILING_DATE_PATTERN.sub('', raw_title).strip()
            else:
                title, publish_date = raw_title, None
            results.append({
                'url': u,
                'title': title,
                'filename_hint': '',
                'publish_date': publish_date,
            })
        return results

    def get_news_links(self):
        all_candidates = []
        for page in range(1, self.PAGES_TO_CHECK + 1):
            all_candidates.extend(self._news_links_on_page(page))
        return all_candidates
