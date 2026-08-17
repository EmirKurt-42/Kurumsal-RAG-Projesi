"""
KOMEK (komek.org.tr) icin veri cekme adaptoru.

Site yapisi (birlikte canli siteye bakarak dogruladigimiz gercek yapi):
  - Statik sayfalar: page.php?PageID=X&SubPageID=Y (+ alanlar.php, merkezler.php)
  - Haberler: haberdetay.php?HaberID=N, SIRALI ID ile - listeleme sayfasi YOK.
    Gecersiz bir ID HATA vermiyor, hep AYNI sahte/varsayilan sayfaya
    yonlendiriyor. Bu yuzden "gecerli mi" kontrolu HTTP durum koduyla degil,
    ICERIK HASH'I ile yapiliyor: ayni hash tekrar gorulurse gecersiz ID'ye
    gelindi demektir.

Not: get_news_links() burada kendisi de fetch+clean yapiyor (ID'nin gercek/
sahte oldugunu anlamak icin) - FetchNewsUseCase da ayni URL'yi tekrar
fetch+clean edecek. Bu, bu sitenin garip "sahte sayfa" davranisi icin
kabul edilen bir maliyet, diger gateway'lerin izlemesi gereken bir kural degil.
"""
import hashlib
import re
from typing import Dict, List
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from src.application.interfaces import IContentCleaner, IScraperGateway, IWebFetcher
from src.infrastructure.web.requests_fetcher import USER_AGENT

STATIC_PATTERNS = [
    r'page\.php\?PageID=\d+&SubPageID=\d+',
    r'alanlar\.php',
    r'merkezler\.php',
]


class KomekScraper(IScraperGateway):
    BASE_URL = 'https://komek.org.tr/'
    NEWS_URL_TEMPLATE = 'https://komek.org.tr/haberdetay.php?HaberID={}&lng=tr'
    STATE_FILE = 'data/komek_son_haber_id.txt'
    CONSECUTIVE_EMPTY_LIMIT = 10

    def __init__(self, fetcher, cleaner):
        self.fetcher = fetcher
        self.cleaner = cleaner

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

    def _read_last_id(self):
        try:
            with open(self.STATE_FILE, 'r') as f:
                return int(f.read().strip())
        except FileNotFoundError:
            return 0

    def _write_last_id(self, news_id):
        with open(self.STATE_FILE, 'w') as f:
            f.write(str(news_id))

    def get_news_links(self):
        start_id = self._read_last_id() + 1
        candidates = []
        seen_hashes = set()
        consecutive_empty = 0
        news_id = start_id
        last_successful_id = start_id - 1
        while consecutive_empty < self.CONSECUTIVE_EMPTY_LIMIT:
            url = self.NEWS_URL_TEMPLATE.format(news_id)
            html = self.fetcher.fetch(url)
            body = self.cleaner.clean(html) if html else None
            if body is None:
                consecutive_empty += 1
                news_id += 1
                continue
            fingerprint = hashlib.md5(body.encode('utf-8')).hexdigest()
            if fingerprint in seen_hashes:
                consecutive_empty += 1
                news_id += 1
                continue
            seen_hashes.add(fingerprint)
            consecutive_empty = 0
            title = body.strip().split('\n')[0].replace('#', '').strip() or f"Haber {news_id}"
            candidates.append({
                'url': url,
                'title': title,
                'filename_hint': f"haber-{news_id}",
            })
            last_successful_id = news_id
            news_id += 1
        self._write_last_id(last_successful_id)
        return candidates
