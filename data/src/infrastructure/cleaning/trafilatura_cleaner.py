"""
Adapter: IContentCleaner'in trafilatura ile gerceklestirimi.
"""
from typing import Optional
import trafilatura

from src.application.interfaces import IContentCleaner

MIN_LENGTH = 30


class TrafilaturaCleaner(IContentCleaner):
    def clean(self, html: str) -> Optional[str]:
        if html is None:
            return None

        content = trafilatura.extract(
            html,
            output_format="markdown",
            include_tables=True,
            include_links=False,
            include_images=False,
            favor_recall=False,
        )

        if not content or len(content.strip()) < MIN_LENGTH:
            return None

        return content.strip()

    def extract_publish_date(self, html: str) -> Optional[str]:
        if html is None:
            return None
        try:
            metadata = trafilatura.extract_metadata(html)
            if metadata and metadata.date:
                return metadata.date
        except Exception:
            pass
        return None