"""
Konya Yenigün (konyayenigun.com) icin veri cekme adaptoru.
"""
import re
from typing import Dict, List
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from src.application.interfaces import IScraperGateway
from src.infrastructure.web.requests_fetcher import USER_AGENT

BASE_URL = "https://www.konyayenigun.com/"
KONYA_KATEGORI_URL = "https://www.konyayenigun.com/konya"
MIN_TIRE_SAYISI = 4

STATIC_PAGES = [
    ("https://www.konyayenigun.com/kunye", "Künye"),
    ("https://www.konyayenigun.com/iletisim", "İletişim"),
]


def _muhtemel_haber_mi(url: str) -> bool:
    path = urlparse(url).path.strip("/")
    if "/" in path or not path:
        return False
    return path.count("-") >= MIN_TIRE_SAYISI


class KonyaYenigunScraper(IScraperGateway):
    def get_static_links(self) -> List[Dict[str, str]]:
        return [{"url": u, "title": t, "filename_hint": ""} for u, t in STATIC_PAGES]

    def get_news_links(self) -> List[Dict[str, str]]:
        headers = {"User-Agent": USER_AGENT}
        r = requests.get(KONYA_KATEGORI_URL, headers=headers, timeout=15)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "html.parser")

        found = {}
        for a in soup.find_all("a", href=True):
            full_url = urljoin(BASE_URL, a["href"])
            if _muhtemel_haber_mi(full_url):
                text = a.get_text(strip=True)
                if full_url not in found or len(text) > len(found[full_url]):
                    found[full_url] = text or "Başlıksız"

        return [{"url": u, "title": t, "filename_hint": ""} for u, t in found.items()]