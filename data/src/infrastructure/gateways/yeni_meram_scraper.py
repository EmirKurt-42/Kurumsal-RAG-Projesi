"""
Yeni Meram (yenimeram.com.tr) icin veri cekme adaptoru.
"""
import re
from typing import Dict, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from src.application.interfaces import IScraperGateway
from src.infrastructure.web.requests_fetcher import USER_AGENT

BASE_URL = "https://www.yenimeram.com.tr/"
KONYA_KATEGORI_URL = "https://www.yenimeram.com.tr/haberler/konya/"
ARTICLE_PATTERN = r"/[a-z0-9-]+/\d+/$"

STATIC_PAGES = [
    ("https://www.yenimeram.com.tr/sayfa/hakkimizda/", "Hakkımızda"),
    ("https://www.yenimeram.com.tr/sayfa/kunye/", "Künye"),
    ("https://www.yenimeram.com.tr/sayfa/reklam/", "Reklam"),
    ("https://www.yenimeram.com.tr/sayfa/kullanim-kosullari/", "Kullanım Koşulları"),
    ("https://www.yenimeram.com.tr/sayfa/gizlilik-politikasi/", "Gizlilik Politikası"),
    ("https://www.yenimeram.com.tr/sayfa/cerez-politikasi/", "Çerez Politikası"),
    ("https://www.yenimeram.com.tr/sayfa/kvkk-metni/", "KVKK Metni"),
    ("https://www.yenimeram.com.tr/iletisim/", "İletişim Bilgileri"),
]


class YeniMeramScraper(IScraperGateway):
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
            if re.search(ARTICLE_PATTERN, full_url):
                text = a.get_text(strip=True)
                if full_url not in found or len(text) > len(found[full_url]):
                    found[full_url] = text or "Başlıksız"

        return [{"url": u, "title": t, "filename_hint": ""} for u, t in found.items()]