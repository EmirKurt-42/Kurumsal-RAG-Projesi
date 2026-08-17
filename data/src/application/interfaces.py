"""
Tum katmanlar icin ortak arayuzler (Interfaces / Ports).

Onceki versiyonda IScraperGateway hem "sayfayi cek" hem "HTML'i temizle"
sorumluluklarini tek metotta (fetch_and_clean_content) birlestiriyordu.
Bu, her gateway dosyasinda ayni trafilatura kodunun tekrar etmesine yol
aciyordu. Simdi bu ikisini ayirdik: IWebFetcher ve IContentCleaner ortak,
tek yerde (infrastructure/web, infrastructure/cleaning) yaziliyor; her
gateway sadece "bu sitenin linkleri nerede" bilgisini tasiyor.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from src.domain.entities.news import News


class IWebFetcher(ABC):
    """Ham HTML cekme sozlesmesi. robots.txt + rate-limit burada uygulanir."""

    @abstractmethod
    def fetch(self, url: str, check_robots: bool = True) -> Optional[str]:
        ...


class IContentCleaner(ABC):
    """Ham HTML'den temiz Markdown metni cikarma sozlesmesi."""

    @abstractmethod
    def clean(self, html: str) -> Optional[str]:
        ...


class IScraperGateway(ABC):
    """Bir sitenin link kesfetme mantigini tasir. Fetch/clean ARTIK burada
degil - gateway'ler kendilerine enjekte edilen IWebFetcher/IContentCleaner'i
kullanir (asagidaki gateway ornekerine bak)."""

    @abstractmethod
    def get_static_links(self) -> List[Dict[str, str]]:
        ...

    @abstractmethod
    def get_news_links(self) -> List[Dict[str, str]]:
        ...


class INewsRepository(ABC):
    """Depolama sozlesmesi. Hash karsilastirmasi HIZLI olmali (dosya var mi
diye bakip frontmatter'daki hash'i okumak yeterli - tum klasoru
fuzzy-compare ile taramak YAVAS ve YANLIS POZITIF riskli, bu yuzden
kaldirildi)."""

    @abstractmethod
    def get_existing_hash(self, news: News, folder_path: str) -> Optional[str]:
        ...

    @abstractmethod
    def save(self, news: News, folder_path: str) -> None:
        ...

    @abstractmethod
    def list_all(self, data_root: str) -> List[Dict[str, Any]]:
        ...


class IVectorStore(ABC):
    """Vektor veritabani sozlesmesi (RAG icin)."""

    @abstractmethod
    def reset(self) -> None:
        ...

    @abstractmethod
    def delete_by_file(self, file_id: str) -> None:
        ...

    @abstractmethod
    def add(self, ids: List[str], texts: List[str], metadatas: List[Dict[str, Any]]) -> None:
        ...

    @abstractmethod
    def query(self, question: str, n_results: int = 4) -> List[Dict[str, Any]]:
        ...


class ILLMClient(ABC):
    """LLM cagirma sozlesmesi (RAG icin)."""

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        ...
