"""
Composition root: soyut arayuzlerin somut implementasyonlarla bulustugu TEK yer.
"""
import os
from dotenv import load_dotenv

load_dotenv()

from src.application.use_cases.fetch_news_use_case import FetchNewsUseCase
from src.application.use_cases.build_index_use_case import BuildIndexUseCase
from src.application.use_cases.answer_question_use_case import AnswerQuestionUseCase
from src.infrastructure.web.requests_fetcher import RequestsFetcher
from src.infrastructure.cleaning.trafilatura_cleaner import TrafilaturaCleaner
from src.infrastructure.repositories.file_repository import FileRepository
from src.infrastructure.vector_store.chroma_vector_store import ChromaVectorStore
from src.infrastructure.llm.openai_compatible_client import OpenAICompatibleClient
from src.infrastructure.gateways.komek_scraper import KomekScraper
from src.infrastructure.gateways.konya_bel_tr_scraper import KonyaBelTrScraper
from src.infrastructure.gateways.koski_scraper import KoskiScraper
from src.infrastructure.gateways.merhaba_haber_scraper import MerhabaHaberScraper
from src.infrastructure.gateways.yeni_meram_scraper import YeniMeramScraper
from src.infrastructure.gateways.konya_haber_scraper import KonyaHaberScraper
from src.infrastructure.gateways.konya_yenigun_scraper import KonyaYenigunScraper
#  İŞTE BİZİM YENİ BÜYÜLÜ TURİZM REHBERİMİZ KADROYA DAHİL EDİLDİ!
from src.infrastructure.gateways.konya_kart_scraper import MevlanaTurizmScraper


class Container:
    def __init__(self):
        self.fetcher = RequestsFetcher()
        self.cleaner = TrafilaturaCleaner()
        self.repository = FileRepository()
        self.vector_store = ChromaVectorStore(
            db_folder='chroma_db',
            collection_name='konya_veri',
            embedding_model='paraphrase-multilingual-MiniLM-L12-v2',
        )
        self.llm_client = OpenAICompatibleClient(
            base_url=os.getenv('LLM_BASE_URL'),
            api_key=os.getenv('LLM_API_KEY'),
            model_name=os.getenv('LLM_MODEL_NAME', 'qwen2.5-coder'),
        )
        self.build_index = BuildIndexUseCase(self.repository, self.vector_store)
        self.answer_question = AnswerQuestionUseCase(self.vector_store, self.llm_client)
        self.sources = {
            'komek': (KomekScraper(self.fetcher, self.cleaner), 'data/komek', 'data/komek_haberler'),
            'konya_bel_tr': (KonyaBelTrScraper(), 'data/konya_bel_tr', 'data/konya_bel_tr_haberler'),
            'koski': (KoskiScraper(), 'data/koski', 'data/koski_haberler'),
            'merhaba_haber': (MerhabaHaberScraper(), 'data/merhaba_haber', 'data/merhaba_haber_haberler'),
            'yeni_meram': (YeniMeramScraper(), 'data/yeni_meram', 'data/yeni_meram_haberler'),
            'konya_haber': (KonyaHaberScraper(), 'data/konya_haber', 'data/konya_haber_haberler'),
            'konya_yenigun': (KonyaYenigunScraper(), 'data/konya_yenigun', 'data/konya_yenigun_haberler'),
            #  YEPYENİ HABER KAYNAĞI ŞİFRESİ VE KÖKLERİ
            'konyakart_mevlana': (MevlanaTurizmScraper(self.fetcher, self.cleaner), 'data/konyakart_mevlana', 'data/konyakart_mevlana_haberler'),
        }

    def fetch_use_case_for(self, gateway):
        return FetchNewsUseCase(gateway, self.fetcher, self.cleaner, self.repository)