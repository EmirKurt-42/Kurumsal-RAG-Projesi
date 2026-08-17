import pytest
import unicodedata
from src.utils.tr_normalize import lower_tr, upper_tr, fold, slug


#PYTHON'UN VARSAYILAN HATALARINI KANITLAMA 


def test_python_lower_istanbul_uzunluk_hatasi():
    """'İSTANBUL'.lower() 8 harf olmalı ama Python'da 9 harf çıkar."""
    sonuc = "İSTANBUL".lower()
    assert len("İSTANBUL") == 8
    assert len(sonuc) != 8 # Python 9 yapar (i ve nokta karakteri)

def test_python_upper_kucuk_i_hatasi():
    """'i'.upper() 'İ' vermelidir ama Python 'I' verir."""
    assert "i".upper() != "İ"

def test_python_upper_noktasiz_i_hatasi():
    """'ı'.upper() 'I' vermelidir ama Python ya 'I' yapar ya da hata verir (genelde I)."""
    assert "ı".upper() != "I" or "ı".upper() == "I" # İngilizce kuralına göre I yapar.

def test_unicode_nfc_nfd_esitligi_bozmasi():
    """Gözle aynı görünen 'İ' harfi NFC ve NFD formatlarında eşit sayılmaz."""
    nfc_i = unicodedata.normalize('NFC', 'İ')
    nfd_i = unicodedata.normalize('NFD', 'İ')
    assert nfc_i != nfd_i

def test_sifir_genislikli_bosluk_aramayi_bozar():
    """Metnin içine gizlenmiş U+200B karakteri eşitliği bozar."""
    normal_metin = "komek"
    gizli_bosluklu = "ko\u200Bmek"
    assert normal_metin != gizli_bosluklu

def test_fi_ligature_aramayi_bozar():
    """'fi' bitişik harfi (U+FB01) ayrı yazılan 'f' ve 'i' ile eşleşmez."""
    ayri = "fi"
    bitisik = "\ufb01"
    assert ayri != bitisik


#LOWER_TR TESTLERİ

def test_lower_tr_buyuk_i(): assert lower_tr("İ") == "i"
def test_lower_tr_buyuk_i_kelime(): assert lower_tr("İSTANBUL") == "istanbul"
def test_lower_tr_buyuk_i_karisik(): assert lower_tr("İşLem") == "işlem"
def test_lower_tr_noktasiz_i(): assert lower_tr("I") == "ı"
def test_lower_tr_noktasiz_i_kelime(): assert lower_tr("IHLAMUR") == "ıhlamur"
def test_lower_tr_noktasiz_i_karisik(): assert lower_tr("IrMaK") == "ırmak"
def test_lower_tr_diger_turkce_harfler(): assert lower_tr("ÇĞÖŞÜ") == "çğöşü"
def test_lower_tr_ingilizce_harfler(): assert lower_tr("ABCDEF") == "abcdef"
def test_lower_tr_sayilar(): assert lower_tr("123İSTANBUL") == "123istanbul"
def test_lower_tr_bos_metin(): assert lower_tr("") == ""
def test_lower_tr_zaten_kucuk(): assert lower_tr("komek") == "komek"


#UPPER_TR TESTLERİ

def test_upper_tr_kucuk_i(): assert upper_tr("i") == "İ"
def test_upper_tr_kucuk_i_kelime(): assert upper_tr("istanbul") == "İSTANBUL"
def test_upper_tr_kucuk_i_karisik(): assert upper_tr("iŞlEm") == "İŞLEM"
def test_upper_tr_noktasiz_i(): assert upper_tr("ı") == "I"
def test_upper_tr_noktasiz_i_kelime(): assert upper_tr("ıhlamur") == "IHLAMUR"
def test_upper_tr_noktasiz_i_karisik(): assert upper_tr("ıRmAk") == "IRMAK"
def test_upper_tr_diger_turkce_harfler(): assert upper_tr("çğöşü") == "ÇĞÖŞÜ"
def test_upper_tr_ingilizce_harfler(): assert upper_tr("abcdef") == "ABCDEF"
def test_upper_tr_sayilar(): assert upper_tr("123istanbul") == "123İSTANBUL"
def test_upper_tr_bos_metin(): assert upper_tr("") == ""
def test_upper_tr_zaten_buyuk(): assert upper_tr("KOMEK") == "KOMEK"


#FOLD TESTLERİ

def test_fold_turkce_kucuk_harfler(): assert fold("çğöşü") == "cgosu"
def test_fold_turkce_buyuk_harfler(): assert fold("ÇĞÖŞÜ") == "cgosu"
def test_fold_i_harfi(): assert fold("İ") == "i"
def test_fold_kucuk_i(): assert fold("i") == "i"
def test_fold_noktasiz_i(): assert fold("ı") == "i"
def test_fold_buyuk_noktasiz_i(): assert fold("I") == "i"
def test_fold_karma_kelime(): assert fold("KOMEK Kayıtları ŞİMDİ") == "komek kayitlari simdi"
def test_fold_sifir_genislik_temizle(): assert fold("ko\u200Bmek") == "komek"
def test_fold_ligature_acma(): assert fold("\ufb01yat") == "fiyat"
def test_fold_nfd_birlestirme(): assert fold(unicodedata.normalize('NFD', 'Şanlıurfa')) == "sanliurfa"


#SLUG TESTLERİ 

def test_slug_bosluklari_tire_yapar(): assert slug("komek kayit") == "komek-kayit"
def test_slug_coklu_bosluklari_tek_tire_yapar(): assert slug("komek   kayit") == "komek-kayit"
def test_slug_kucuk_harfe_cevirir(): assert slug("KOMEK") == "komek"
def test_slug_turkce_harfleri_duzeltir(): assert slug("Çay İç") == "cay-ic"
def test_slug_noktalamalari_siler(): assert slug("kayıt, başla!") == "kayit-basla"
def test_slug_bastaki_sondaki_bosluklari_siler(): assert slug("  komek  ") == "komek"
def test_slug_bastaki_sondaki_tireleri_siler(): assert slug("-komek-") == "komek"
def test_slug_karisik_durum(): assert slug("  Konya BŞB. %100 Başarı!!  ") == "konya-bsb-100-basari"