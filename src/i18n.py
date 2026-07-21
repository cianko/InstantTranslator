"""Basit i18n (İngilizce / Türkçe) altyapısı.

Kullanım:
    from src.i18n import t, set_language
    set_language("auto")   # "auto" -> Windows sistem dilinden algılar
    t("save")              # -> "Kaydet" veya "Save"

Metinler tek yerde (TRANSLATIONS) tutulur; arayüz bileşenleri t(...) çağırır.
Dil değişince set_language(...) çağrılır ve bileşenler kendini yeniden çevirir.
"""
import ctypes
import locale

TRANSLATIONS = {
    "en": {
        # --- Tray / genel ---
        "window_title_settings": "Settings — Instant Translator",
        "settings": "Settings",
        "open_config": "Open settings file (Notepad)",
        "about": "About",
        "quit": "Quit",
        "error": "Error",
        "tray_running": "Running. Shortcut: {hotkey}",
        "settings_saved": "Settings saved. Shortcut: {hotkey}",
        "hotkey_failed": "Could not register the shortcut ({hotkey}): {err}",
        "already_running": ("Instant Translator is already running.\n"
                            "Check the icon in the system tray (near the clock)."),
        "no_tray": "The system tray is not available on this system.",
        "config_open_failed": "Could not open the settings file: {err}",
        "about_body": ("Instant Translator\n\n"
                       "Instantly translates selected text with a shortcut.\n"
                       "Built with PySide6."),
        # --- Çeviri penceresi (overlay) ---
        "translating": "Translating…",
        "copy": "Copy",
        "copied": "Copied ✓",
        "tip_settings": "Settings",
        "tip_close": "Close (Esc)",
        "err_no_text": "No text selected.\nSelect some text and try again.",
        "err_engine": "Error: Cannot reach the translation engine.\nPlease try again.",
        "err_ocr": "Could not read text from the selection.\nTry selecting a clearer area.",
        "snip_hint": "Copy is blocked — draw a box over the text to translate (OCR)   •   Esc to cancel",
        # --- Ayarlar penceresi ---
        "lbl_shortcut": "Shortcut:",
        "lbl_source": "Source language:",
        "lbl_target": "Target language:",
        "lbl_theme": "Theme:",
        "lbl_ui_language": "Interface language:",
        "theme_dark": "Dark",
        "theme_light": "Light",
        "hotkey_placeholder": "Click and press a key combination",
        "hotkey_press": "Press keys…",
        "settings_hint": "Click the shortcut box and press your desired key combination.",
        "save": "Save",
        "cancel": "Cancel",
        "ui_lang_auto": "System (Auto)",
        "ui_lang_en": "English",
        "ui_lang_tr": "Turkish",
        # --- Dil adları (kaynak/hedef listeleri) ---
        "lang_auto": "Auto Detect",
        "lang_en": "English", "lang_tr": "Turkish", "lang_de": "German",
        "lang_fr": "French", "lang_es": "Spanish", "lang_it": "Italian",
        "lang_ru": "Russian", "lang_ar": "Arabic",
    },
    "tr": {
        "window_title_settings": "Ayarlar — Instant Translator",
        "settings": "Ayarlar",
        "open_config": "Ayar dosyasını aç (Notepad)",
        "about": "Hakkında",
        "quit": "Çıkış",
        "error": "Hata",
        "tray_running": "Çalışıyor. Kısayol: {hotkey}",
        "settings_saved": "Ayarlar kaydedildi. Kısayol: {hotkey}",
        "hotkey_failed": "Kısayol kaydedilemedi ({hotkey}): {err}",
        "already_running": ("Instant Translator zaten çalışıyor.\n"
                            "Sistem tepsisindeki (saatin yanındaki) simgeyi kontrol edin."),
        "no_tray": "Sistem tepsisi bu sistemde bulunamadı.",
        "config_open_failed": "Ayar dosyası açılamadı: {err}",
        "about_body": ("Instant Translator\n\n"
                       "Seçili metni kısayol ile anında çevirir.\n"
                       "PySide6 ile geliştirilmiştir."),
        "translating": "Çevriliyor…",
        "copy": "Kopyala",
        "copied": "Kopyalandı ✓",
        "tip_settings": "Ayarlar",
        "tip_close": "Kapat (Esc)",
        "err_no_text": "Seçili metin bulunamadı.\nÖnce bir metin seçip tekrar deneyin.",
        "err_engine": "Hata: Çeviri motoruna ulaşılamadı.\nLütfen tekrar deneyin.",
        "err_ocr": "Seçimden metin okunamadı.\nDaha net bir alan seçmeyi deneyin.",
        "snip_hint": "Kopyalama engelli — çevirmek için metnin üzerine bir kutu çizin (OCR)   •   İptal: Esc",
        "lbl_shortcut": "Kısayol:",
        "lbl_source": "Kaynak dil:",
        "lbl_target": "Hedef dil:",
        "lbl_theme": "Tema:",
        "lbl_ui_language": "Arayüz dili:",
        "theme_dark": "Koyu (Dark)",
        "theme_light": "Açık (Light)",
        "hotkey_placeholder": "Tıklayın ve tuş kombinasyonuna basın",
        "hotkey_press": "Tuşlara basın…",
        "settings_hint": "Kısayol kutusuna tıklayıp istediğiniz tuş kombinasyonuna basın.",
        "save": "Kaydet",
        "cancel": "İptal",
        "ui_lang_auto": "Sistem (Otomatik)",
        "ui_lang_en": "İngilizce",
        "ui_lang_tr": "Türkçe",
        "lang_auto": "Otomatik Algıla",
        "lang_en": "İngilizce", "lang_tr": "Türkçe", "lang_de": "Almanca",
        "lang_fr": "Fransızca", "lang_es": "İspanyolca", "lang_it": "İtalyanca",
        "lang_ru": "Rusça", "lang_ar": "Arapça",
    },
}


def detect_system_language() -> str:
    """Windows arayüz dilini algılar; Türkçe ise 'tr', değilse 'en' döner."""
    try:
        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        if (lang_id & 0x3FF) == 0x1F:  # LANG_TURKISH
            return "tr"
        return "en"
    except Exception:
        pass
    try:
        loc = (locale.getdefaultlocale()[0] or "").lower()
        if loc.startswith("tr"):
            return "tr"
    except Exception:
        pass
    return "en"


_current_lang = "en"


def set_language(lang: str) -> str:
    """Arayüz dilini ayarlar. 'auto'/geçersiz -> sistem dilinden algılar."""
    global _current_lang
    if not lang or lang == "auto" or lang not in TRANSLATIONS:
        lang = detect_system_language()
    _current_lang = lang if lang in TRANSLATIONS else "en"
    return _current_lang


def current_language() -> str:
    return _current_lang


def t(key: str, **kwargs) -> str:
    s = TRANSLATIONS.get(_current_lang, TRANSLATIONS["en"]).get(key)
    if s is None:
        s = TRANSLATIONS["en"].get(key, key)
    return s.format(**kwargs) if kwargs else s
