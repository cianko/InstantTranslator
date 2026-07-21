"""Windows yerleşik OCR (Windows.Media.Ocr) sarmalayıcısı.

Harici program (Tesseract vb.) GEREKTİRMEZ; OCR dil paketleri Windows'ta yerleşik.
winsdk tembel (lazy) import edilir; herhangi bir sorunda uygulama çökmez, OCR
sadece "" döner ve çağıran taraf kullanıcıya hata gösterir.
"""
import asyncio


def _winsdk():
    from winsdk.windows.media.ocr import OcrEngine
    from winsdk.windows.globalization import Language
    from winsdk.windows.graphics.imaging import BitmapDecoder
    from winsdk.windows.storage.streams import InMemoryRandomAccessStream, DataWriter
    return OcrEngine, Language, BitmapDecoder, InMemoryRandomAccessStream, DataWriter


def _make_engine(OcrEngine, Language, source_lang):
    # 1) İstenen kaynak dil (auto değilse)
    if source_lang and source_lang != "auto":
        try:
            eng = OcrEngine.try_create_from_language(Language(source_lang))
            if eng:
                return eng
        except Exception:
            pass
    # 2) Kullanıcı profili dilleri
    try:
        eng = OcrEngine.try_create_from_user_profile_languages()
        if eng:
            return eng
    except Exception:
        pass
    # 3) Kurulu ilk tanıyıcı dil (Latin alfabesi İngilizceyi de okur)
    try:
        langs = list(OcrEngine.available_recognizer_languages)
        if langs:
            return OcrEngine.try_create_from_language(langs[0])
    except Exception:
        pass
    return None


async def _ocr_async(png_bytes, source_lang):
    OcrEngine, Language, BitmapDecoder, InMemoryRandomAccessStream, DataWriter = _winsdk()
    stream = InMemoryRandomAccessStream()
    writer = DataWriter(stream)
    writer.write_bytes(png_bytes)
    await writer.store_async()
    await writer.flush_async()
    stream.seek(0)
    decoder = await BitmapDecoder.create_async(stream)
    bmp = await decoder.get_software_bitmap_async()
    eng = _make_engine(OcrEngine, Language, source_lang)
    if eng is None:
        raise RuntimeError("no-ocr-engine")
    result = await eng.recognize_async(bmp)
    # Satırları birleştir (kelimeler tek boşlukla, satırlar yeni satırla)
    try:
        lines = [ln.text for ln in result.lines]
        text = "\n".join(lines)
    except Exception:
        text = result.text or ""
    return text.strip()


def ocr_png(png_bytes: bytes, source_lang: str = "auto") -> str:
    """PNG bayt dizisinden metin çıkarır. Sorun olursa "" döner (çökmez)."""
    try:
        return asyncio.run(_ocr_async(png_bytes, source_lang))
    except Exception:
        return ""


def is_available() -> bool:
    """Windows OCR bu makinede kullanılabilir mi?"""
    try:
        OcrEngine, Language, _, _, _ = _winsdk()
        return len(list(OcrEngine.available_recognizer_languages)) > 0
    except Exception:
        return False
