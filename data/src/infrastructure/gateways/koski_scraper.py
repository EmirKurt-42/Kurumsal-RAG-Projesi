"""
KOSKI (koski.gov.tr) icin veri cekme adaptoru.

Site yapisi (canli siteye bakilarak dogrulandi):
  - Statik sayfalar: /sayfa/{slug} ve /koski/{slug}
  - Haberler: /haber/{slug}-{tarih}-{id}, listeleme /haberler
  - Duyurular: /duyuru/{slug}-{tarih}-{id}, listeleme /duyurular
    (ikisi de haber-benzeri duyuru sayildigi icin birlikte toplaniyor)

Not: Baslik metninin tam yapisi ilk canli calistirmada dogrulanmali - "en
uzun metni tut" sezgisi en azindan anlamli bir baslik garanti ediyor
(konya_bel_tr'de de ayni yontem kullanildi ve calisti).
"""
import re
from typing import Dict, List
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from src.application.interfaces import IScraperGateway
from src.infrastructure.web.requests_fetcher import USER_AGENT

STATIC_PATTERNS = [
    '/sayfa/[a-z0-9-]+$',
    '/koski/[a-z0-9-]+$',
]
NEWS_PATTERNS = [
    '/haber/[a-z0-9-]+$',
    '/duyuru/[a-z0-9-]+$',
]
LISTING_URLS = [
    'https://www.koski.gov.tr/haberler',
    'https://www.koski.gov.tr/duyurular',
]


class KoskiScraper(IScraperGateway):
    BASE_URL = 'https://www.koski.gov.tr/'

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

    def get_news_links(self):
        headers = {'User-Agent': USER_AGENT}
        found = {}
        for listing_url in LISTING_URLS:
            r = requests.get(listing_url, headers=headers, timeout=15)
            r.encoding = r.apparent_encoding
            soup = BeautifulSoup(r.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                full_url = urljoin(self.BASE_URL, a['href'])
                for pattern in NEWS_PATTERNS:
                    if not re.search(pattern, full_url):
                        continue
                    text = a.get_text(strip=True)
                    if full_url not in found or len(text) > len(found[full_url]):
                        found[full_url] = text or 'Baslik yok'
                    break
        return [{'url': u, 'title': t, 'filename_hint': ''} for u, t in found.items()]
