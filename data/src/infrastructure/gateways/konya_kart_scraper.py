"""
KonyaKart Rehberi
(konyakart.konya.bel.tr) için veri çekme adaptörü.
"""
import re
from typing import Dict, List
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from src.application.interfaces import IScraperGateway
from src.infrastructure.web.requests_fetcher import USER_AGENT


class MevlanaTurizmScraper(IScraperGateway):
    BASE_URL = 'https://konyakart.konya.bel.tr/'
    
    # Sitede dinamik duyuru/etkinlik veya haberleri statik kılavuzlardan ayıran kelimeler
    NEWS_PATTERNS = ['haber', 'duyuru', 'haberler', 'duyurular', 'kampanya', 'etkinlik', 'bulten']
    
    def __init__(self, fetcher, cleaner):
        self.fetcher = fetcher
        self.cleaner = cleaner

    def _is_valid_url(self, url: str) -> bool:
        """Gereksiz dosya indirme, giriş mekanizmaları ve harici sitelerin çöplerini eler."""
        parsed = urlparse(url)
        # Sadece kendi turizm ve kart alan adlarımız içeriklerinde gezinebiliriz
        if parsed.netloc and 'konyakart.konya.bel.tr' not in parsed.netloc and 'konya.bel.tr' not in parsed.netloc:
            return False
        if any(url.lower().endswith(ext) for ext in ['.pdf', '.png', '.jpg', '.jpeg', '.gif', '.zip', '.mp4', '.doc']):
            return False
        if any(junk in url.lower() for junk in ['login', 'admin', 'logout', 'javascript:', 'mailto:', 'tel:']):
            return False
        return True

    def get_static_links(self) -> List[Dict[str, str]]:
        """Web sitemizdeki tüm sabit rehber, tarife, turizm kartı, mevlana ve kullanım rehberi sayfalarını kucaklar."""
        headers = {'User-Agent': USER_AGENT}
        try:
            r = requests.get(self.BASE_URL, headers=headers, timeout=15)
            r.encoding = r.apparent_encoding
            soup = BeautifulSoup(r.text, 'html.parser')
        except Exception as e:
            print(f"[MevlanaTurizmScraper] Ana sayfa okunamadı: {e}")
            return []

        found = {}
        for a in soup.find_all('a', href=True):
            full_url = urljoin(self.BASE_URL, a['href']).split('#')[0].rstrip('/')
            if not self._is_valid_url(full_url):
                continue
            
            # Eğer link bir haber veya duyuruyorsa onu get_news_links fonksiyonu yapacağı için pas geçer
            if any(pattern in full_url.lower() for pattern in self.NEWS_PATTERNS):
                continue

            title = a.get_text(strip=True)
            if not title or len(title) < 3:
                continue
                
            # Daha açıklayıcı başlığı olan versiyonunu ya da ilk rastlananı kaydet
            if full_url not in found or len(title) > len(found[full_url]):
                found[full_url] = title

        # Ana sayfanın kendini de genel tarifeler için ana hazine olarak ekliyoruz
        ana_adres = self.BASE_URL.rstrip('/')
        if ana_adres not in found:
            found[ana_adres] = "KonyaKart ve Turizm Bilgilendirme ve Hizmet Portalı"

        return [{'url': u, 'title': t, 'filename_hint': f"turizm-{u.split('/')[-1] or 'anasifa'}"} for u, t in found.items()]

    def get_news_links(self) -> List[Dict[str, str]]:
        """Sitedeki duyurular, turizm etkinlikleri ve bülten bağlantılarını toplar."""
        headers = {'User-Agent': USER_AGENT}
        try:
            r = requests.get(self.BASE_URL, headers=headers, timeout=15)
            r.encoding = r.apparent_encoding
            soup = BeautifulSoup(r.text, 'html.parser')
        except Exception:
            return []

        news_candidates = {}
        for a in soup.find_all('a', href=True):
            full_url = urljoin(self.BASE_URL, a['href']).split('#')[0].rstrip('/')
            if not self._is_valid_url(full_url):
                continue
                
            # Yalnızca haber/duyuru/kampanya stili olan dinamik yazıları çek
            if not any(pattern in full_url.lower() for pattern in self.NEWS_PATTERNS):
                continue

            title = a.get_text(strip=True) or "Turizm ve Kart Duyurusu"
            if full_url not in news_candidates:
                news_candidates[full_url] = title

        return [{'url': u, 'title': t, 'filename_hint': f"duyuru-{u.split('/')[-1]}"} for u, t in news_candidates.items()]