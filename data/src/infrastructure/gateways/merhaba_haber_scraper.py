"""
Merhaba Haber (merhabahaber.com) icin veri cekme adaptoru.

Site yapisi: genel bir haber portali (CM News CMS), Konya disinda ulusal/
uluslararasi icerik de yayinliyor. "Konya ile alakali" filtresini KELIME
ARAMASI ile degil, SITENIN KENDI KATEGORILERINI kullanarak yapiyoruz - bu
cok daha guvenilir, cunku site zaten haberleri editoryal olarak Konya'ya
ozel kategorilere ayirmis durumda.

Haber URL formati: {slug}-{sayisal-id}h.htm
"""
import re
from typing import Dict, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from src.application.interfaces import IScraperGateway
from src.infrastructure.web.requests_fetcher import USER_AGENT

BASE_URL = "https://www.merhabahaber.com/"

# Sadece Konya'ya ozel kategoriler - Turkiye/Dunya/Ekonomi/Otomobil gibi
# genel kategoriler BILEREK disinda birakildi.
KONYA_KATEGORI_URLLERI = [
    "https://www.merhabahaber.com/konya-haberleri-141hk.htm",
    "https://www.merhabahaber.com/ilceler-haberleri-35hk.htm",
    "https://www.merhabahaber.com/konya-spor-haberleri-10hk.htm",
    "https://www.merhabahaber.com/merhaba-sehir-haberleri-17hk.htm",
]

ARTICLE_PATTERN = r"-\d+h\.htm$"

# Sitenin kurumsal/hakkinda sayfalari - sabit, kucuk bir liste, tarama gerekmiyor
STATIC_PAGES = [
    ("https://www.merhabahaber.com/kunye", "Künye"),
    ("https://www.merhabahaber.com/iletisim", "İletişim"),
    ("https://www.merhabahaber.com/gizlilik-ilkeleri", "Gizlilik İlkeleri"),
    ("https://www.merhabahaber.com/kullanim-sartlari", "Kullanım Şartları"),
]


class MerhabaHaberScraper(IScraperGateway):
    def get_static_links(self) -> List[Dict[str, str]]:
        return [{"url": u, "title": t, "filename_hint": ""} for u, t in STATIC_PAGES]

    def get_news_links(self) -> List[Dict[str, str]]:
        headers = {"User-Agent": USER_AGENT}
        found = {}

        for kategori_url in KONYA_KATEGORI_URLLERI:
            r = requests.get(kategori_url, headers=headers, timeout=15)
            r.encoding = r.apparent_encoding
            soup = BeautifulSoup(r.text, "html.parser")

            for a in soup.find_all("a", href=True):
                full_url = urljoin(BASE_URL, a["href"])
                if re.search(ARTICLE_PATTERN, full_url):
                    text = a.get_text(strip=True)
                    if full_url not in found or len(text) > len(found[full_url]):
                        found[full_url] = text or "Başlıksız"

        return [{"url": u, "title": t, "filename_hint": ""} for u, t in found.items()]