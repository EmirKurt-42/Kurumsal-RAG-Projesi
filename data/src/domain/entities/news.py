"""
Sistemde dolaşacak olan standart Haber veri modeli.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class News:
    source: str
    url: str
    title: str
    fetch_date: str
    body: str
    hash: str
    publish_date: Optional[str] = None
    category: Optional[str] = None
    author: Optional[str] = None
    filename_hint: Optional[str] = None
