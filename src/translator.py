"""Hızlı, çok yedekli ve ASLA askıda kalmayan çeviri sarmalayıcısı.

Kararlılık ilkeleri:
- Tek, kalıcı (keep-alive) requests.Session -> hızlı.
- HER istek katı bir timeout ile sınırlı (varsayılan 5 sn). Hiçbir yol sonsuza
  kadar donup kalamaz.
- 3 kademeli yedek: biri engellenir/başarısız olursa diğeri denenir.
    1) Google JSON uç noktası (translate_a/single)  -> en hızlı ve sağlam
    2) Google /m HTML uç noktası                     -> yedek
    3) deep-translator (socket timeout ile sınırlı)  -> son çare
- Hepsi başarısız olursa TranslationError fırlar; çağıran taraf kırmızı hata
  mesajı gösterir.
"""
import socket

import requests
from bs4 import BeautifulSoup


class TranslationError(Exception):
    pass


_session = requests.Session()
_session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
})

_GTX_URL = "https://translate.googleapis.com/translate_a/single"
_M_URL = "https://translate.google.com/m"


def _google_gtx(text: str, source: str, target: str, timeout: float) -> str:
    """Google JSON uç noktası — hızlı ve çok cümleyi düzgün birleştirir."""
    params = {"client": "gtx", "sl": source or "auto", "tl": target, "dt": "t", "q": text}
    resp = _session.get(_GTX_URL, params=params, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    parts = [seg[0] for seg in data[0] if seg and seg[0]]
    result = "".join(parts).strip()
    if not result:
        raise ValueError("boş sonuç")
    return result


def _google_m(text: str, source: str, target: str, timeout: float) -> str:
    """Google /m HTML uç noktası — yedek yol."""
    params = {"sl": source or "auto", "tl": target, "q": text}
    resp = _session.get(_M_URL, params=params, timeout=timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    container = soup.find("div", class_="result-container")
    if container and container.get_text(strip=True):
        return container.get_text(strip=True)
    raise ValueError("ayrıştırılamadı")


def _deep(text: str, source: str, target: str, timeout: float) -> str:
    """deep-translator son çare — socket timeout ile sınırlandırılır (asılı kalmaz)."""
    from deep_translator import GoogleTranslator
    old = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    try:
        out = GoogleTranslator(source=source or "auto", target=target).translate(text)
        if not out or not out.strip():
            raise ValueError("boş sonuç")
        return out.strip()
    finally:
        socket.setdefaulttimeout(old)


def translate_text(text: str, source: str = "auto", target: str = "tr",
                   timeout: float = 5.0) -> str:
    """Metni çevirir; tüm motorlar denenir. Hepsi başarısız olursa TranslationError."""
    text = (text or "").strip()
    if not text:
        raise TranslationError("empty")

    errors = []
    for engine in (_google_gtx, _google_m, _deep):
        try:
            result = engine(text, source, target, timeout)
            if result and result.strip():
                return result.strip()
        except Exception as e:
            errors.append(f"{engine.__name__}: {e}")
            continue

    raise TranslationError(" | ".join(errors) or "bilinmeyen hata")


def warmup():
    """Açılışta arka planda bağlantıyı ısıtır (ilk çeviri gecikmesini yok eder)."""
    try:
        _google_gtx("hello", "auto", "tr", 5.0)
    except Exception:
        pass
