"""
Konya Haber (konhaber.com) icin veri cekme adaptoru.
"""
import re
from typing import Dict, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from src.application.interfaces import IScraperGateway
from src.infrastructure.web.requests_fetcher import USER_AGENT

BASE_URL = "https://www.konhaber.com/"
ARTICLE_PATTERN = r"-\d+h$"

STATIC_PAGES = [
    ("https://www.konhaber.com/iletisim", "İletişim"),
    ("https://www.konhaber.com/cerez-politikasi", "Çerez Politikası"),
    ("https://www.konhaber.com/gizlilik-ilkeleri", "Gizlilik İlkeleri"),
]


def _konya_ile_ilgili_mi(baslik: str) -> bool:
    return "konya" in baslik.lower()


class KonyaHaberScraper(IScraperGateway):
    def get_static_links(self) -> List[Dict[str, str]]:
        return [{"url": u, "title": t, "filename_hint": ""} for u, t in STATIC_PAGES]

    def get_news_links(self) -> List[Dict[str, str]]:
        headers = {"User-Agent": USER_AGENT}
        r = requests.get(BASE_URL, headers=headers, timeout=15)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "html.parser")

        found = {}
        for a in soup.find_all("a", href=True):
            full_url = urljoin(BASE_URL, a["href"])
            if re.search(ARTICLE_PATTERN, full_url):
                text = a.get_text(strip=True)
                if not _konya_ile_ilgili_mi(text):
                    continue
                if full_url not in found or len(text) > len(found[full_url]):
                    found[full_url] = text or "Başlıksız"

        return [{"url": u, "title": t, "filename_hint": ""} for u, t in found.items()]