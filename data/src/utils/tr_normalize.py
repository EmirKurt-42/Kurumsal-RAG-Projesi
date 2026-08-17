import re
import unicodedata

def lower_tr(text: str) -> str:
    """Metni Türkçe kurallarına göre küçük harfe çevirir."""
    if not text:
        return ""
    return text.replace("İ", "i").replace("I", "ı").lower()

def upper_tr(text: str) -> str:
    """Metni Türkçe kurallarına göre büyük harfe çevirir."""
    if not text:
        return ""
    return text.replace("i", "İ").replace("ı", "I").upper()

def fold(text: str) -> str:
    """Aramada kullanılmak üzere, Türkçe harflerin şapkasını ve noktasını kaldırır."""
    if not text:
        return ""
    text = text.replace("\u200B", "")
    text = unicodedata.normalize("NFKC", text)
    text = lower_tr(text)
    ceviri_tablosu = str.maketrans("çğışöü", "cgisou")
    return text.translate(ceviri_tablosu)

def slug(text: str) -> str:
    """Bir başlığı, internet adresinde kullanılabilecek sade bir metne çevirir."""
    if not text:
        return ""
    text = fold(text)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')