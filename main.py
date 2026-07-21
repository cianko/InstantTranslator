"""Instant Translator — sistem tepsisinde çalışan anlık çeviri aracı.

Akış:
  Global kısayol (keyboard thread) -> Bridge.trigger sinyali (ana thread) ->
  worker thread: seçili metni yakala + çevir -> Bridge.result sinyali ->
  overlay imlecin yanında belirir.
"""
import os
import subprocess
import sys
import threading
import time

from PySide6.QtCore import QObject, Qt, QSharedMemory, Signal
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMenu, QMessageBox, QSystemTrayIcon,
)
import keyboard

from src.capture import get_selected_text
from src.config_manager import CONFIG_PATH, ConfigManager
from src.i18n import set_language, t
from src.ocr import ocr_png
from src.overlay import TranslationOverlay
from src.settings_dialog import SettingsDialog
from src.snip import SnipOverlay
from src.translator import TranslationError, translate_text, warmup

APP_NAME = "Instant Translator"  # marka adı — çevrilmez


class Bridge(QObject):
    """Thread'ler arası güvenli iletişim için Qt sinyalleri."""
    trigger = Signal()                    # kısayol thread'i -> ana thread
    loading = Signal(str, str)            # source, target
    result = Signal(str, str, str, str)   # original, translated, source, target
    error = Signal(str)
    request_snip = Signal(str, str)       # kopyalama başarısız -> OCR snip modu (source, target)


def make_icon() -> QIcon:
    """Basit, dosyasız bir tepsi/uygulama simgesi üretir."""
    pix = QPixmap(64, 64)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor("#4f8cff"))
    p.setPen(Qt.NoPen)
    p.drawRoundedRect(4, 4, 56, 56, 16, 16)
    p.setPen(QColor("#ffffff"))
    p.setFont(QFont("Segoe UI", 30, QFont.Bold))
    p.drawText(pix.rect(), Qt.AlignCenter, "文")
    p.end()
    return QIcon(pix)


class TranslatorApp:
    def __init__(self, app: QApplication, config=None):
        self.app = app
        self.config = config or ConfigManager()
        # Arayüz dilini uygula ("auto" -> Windows sistem dili)
        set_language(self.config.get("language"))
        self.bridge = Bridge()
        self.overlay = TranslationOverlay(self.config.get("theme"))
        self.overlay.on_settings = self.open_settings  # çark ikonu -> ayarlar
        self._busy = False              # Kural 2: işlem kilidi
        self._last_trigger = 0.0        # Kural 2: tuş tekrarına karşı debounce

        # Ayar dosyasının diskte var olduğundan emin ol (kullanıcı elle düzenleyebilsin)
        self.config.save()

        self.bridge.trigger.connect(self.on_trigger)
        self.bridge.loading.connect(self.overlay.show_loading)
        self.bridge.result.connect(self.overlay.show_result)
        self.bridge.error.connect(self.overlay.show_error)
        self.bridge.request_snip.connect(self.start_snip)
        self._snip = None

        self._icon = make_icon()
        self._build_tray()
        self._register_hotkey()

        # Çeviri motorunu arka planda ısıt (ilk çeviri de anlık gelsin)
        threading.Thread(target=warmup, daemon=True).start()

    def _build_tray(self):
        self.tray = QSystemTrayIcon(self._icon, self.app)
        self.tray.setToolTip(APP_NAME)

        menu = QMenu()
        self.act_settings = QAction(t("settings"), self.app)
        self.act_settings.triggered.connect(self.open_settings)
        self.act_openfile = QAction(t("open_config"), self.app)
        self.act_openfile.triggered.connect(self.open_config_file)
        self.act_about = QAction(t("about"), self.app)
        self.act_about.triggered.connect(self.show_about)
        self.act_quit = QAction(t("quit"), self.app)
        self.act_quit.triggered.connect(self.quit)
        menu.addAction(self.act_settings)
        menu.addAction(self.act_openfile)
        menu.addAction(self.act_about)
        menu.addSeparator()
        menu.addAction(self.act_quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()
        self.tray.showMessage(
            APP_NAME,
            t("tray_running", hotkey=self.config.get("hotkey")),
            self._icon, 3000,
        )

    def _retranslate_tray(self):
        """Dil değişince tepsi menüsü metinlerini günceller."""
        self.act_settings.setText(t("settings"))
        self.act_openfile.setText(t("open_config"))
        self.act_about.setText(t("about"))
        self.act_quit.setText(t("quit"))

    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.open_settings()

    def _register_hotkey(self):
        try:
            keyboard.remove_all_hotkeys()
        except Exception:
            pass
        hk = self.config.get("hotkey")
        try:
            keyboard.add_hotkey(hk, lambda: self.bridge.trigger.emit())
        except Exception as e:
            self.tray.showMessage(
                t("error"), t("hotkey_failed", hotkey=hk, err=e),
                QSystemTrayIcon.Critical, 4000,
            )

    def on_trigger(self):
        # --- Kural 2: Kilit + Debounce ---
        # Zaten bir işlem sürüyorsa yok say.
        if self._busy:
            return
        # Tuş tekrarı / çok hızlı ard arda tetiklenmeleri (0.4 sn) yok say.
        now = time.monotonic()
        if (now - self._last_trigger) < 0.4:
            return
        self._last_trigger = now
        self._busy = True

        # --- Kural 1: Tekil Pencere ---
        # Ekranda açık bir çeviri penceresi varsa önce onu kapat.
        self.overlay.force_close()

        source = self.config.get("source_lang")
        target = self.config.get("target_lang")
        # DİKKAT: Pencereyi burada GÖSTERMİYORUZ. Önce arka planda metni
        # panoya alıp (odak kaynak programdayken), ardından pencereyi açıyoruz.
        threading.Thread(target=self._worker, args=(source, target), daemon=True).start()

    def _worker(self, source, target):
        handoff = False
        try:
            # 1) Kaynak program hâlâ odaktayken seçili metni panoya al
            text = get_selected_text()
            if not text:
                # Kopyalama engelli olabilir (ör. izinleri kısıtlı PDF) ->
                # OCR ile ekran bölgesinden okuma moduna geç.
                handoff = True
                self.bridge.request_snip.emit(source, target)
                return
            # 2) Metin alındı; artık pencereyi açıp "Çevriliyor…" gösterebiliriz
            self.bridge.loading.emit(source, target)
            # 3) Çeviriyi yap ve sonucu göster (maks. 5 sn timeout, asılı kalmaz)
            translated = translate_text(text, source, target, timeout=5.0)
            self.bridge.result.emit(text, translated, source, target)
        except TranslationError:
            self.bridge.error.emit(t("err_engine"))
        except Exception:
            self.bridge.error.emit(t("err_engine"))
        finally:
            if not handoff:
                self._busy = False

    # --- OCR yedek yakalama (kopyalama engelliyse) ---
    def start_snip(self, source, target):
        """Tam ekran bölge seçici açar (ana thread)."""
        self.overlay.force_close()
        self._snip = SnipOverlay()
        self._snip.captured.connect(lambda png: self._on_snip(png, source, target))
        self._snip.cancelled.connect(self._on_snip_cancel)
        self._snip.start()

    def _on_snip_cancel(self):
        self._busy = False

    def _on_snip(self, png, source, target):
        self.bridge.loading.emit(source, target)
        threading.Thread(target=self._ocr_worker, args=(png, source, target), daemon=True).start()

    def _ocr_worker(self, png, source, target):
        try:
            text = ocr_png(png, source)
            if not text.strip():
                self.bridge.error.emit(t("err_ocr"))
                return
            translated = translate_text(text, source, target, timeout=5.0)
            self.bridge.result.emit(text, translated, source, target)
        except TranslationError:
            self.bridge.error.emit(t("err_engine"))
        except Exception:
            self.bridge.error.emit(t("err_engine"))
        finally:
            self._busy = False

    def open_settings(self):
        dlg = SettingsDialog(self.config)
        if dlg.exec():
            values = dlg.get_values()
            for k, v in values.items():
                self.config.set(k, v)
            # Arayüz dilini uygula ve tüm görünür metinleri yenile
            set_language(values["language"])
            self._retranslate_tray()
            self.overlay.retranslate()
            self.overlay.theme = values["theme"]
            self.overlay._apply_style()
            self._register_hotkey()
            self.tray.showMessage(
                APP_NAME,
                t("settings_saved", hotkey=values["hotkey"]),
                self._icon, 2500,
            )

    def open_config_file(self):
        """Ayar dosyasını (config.json) Notepad ile açar."""
        self.config.save()  # dosyanın var olduğundan emin ol
        try:
            subprocess.Popen(["notepad.exe", str(CONFIG_PATH)])
        except Exception:
            try:
                os.startfile(str(CONFIG_PATH))  # yedek: varsayılan uygulama
            except Exception as e:
                self.tray.showMessage(t("error"), t("config_open_failed", err=e),
                                      QSystemTrayIcon.Critical, 4000)

    def show_about(self):
        QMessageBox.information(None, t("about"), t("about_body"))

    def quit(self):
        try:
            keyboard.remove_all_hotkeys()
        except Exception:
            pass
        self.tray.hide()
        self.app.quit()


def _run_ocr_selftest():
    """Donmuş exe'de Windows OCR'ın çalışıp çalışmadığını dosyaya yazar.
    Kullanım: InstantTranslator.exe --selftest-ocr  ->  %TEMP%\\it_ocr_selftest.txt
    """
    import os
    import tempfile
    from PySide6.QtCore import Qt, QBuffer, QByteArray
    from PySide6.QtGui import QImage, QPainter, QFont
    from src.ocr import ocr_png, is_available

    img = QImage(720, 120, QImage.Format_RGB32)
    img.fill(Qt.white)
    p = QPainter(img)
    p.setPen(Qt.black)
    p.setFont(QFont("Arial", 24))
    p.drawText(img.rect(), Qt.AlignCenter, "Instant Translator OCR self test")
    p.end()
    ba = QByteArray()
    buf = QBuffer(ba)
    buf.open(QBuffer.WriteOnly)
    img.save(buf, "PNG")

    out = "available={} result={!r}".format(is_available(), ocr_png(bytes(ba), "en"))
    path = os.path.join(tempfile.gettempdir(), "it_ocr_selftest.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # pencere kapansa da tepside kal

    # Gizli tanılama: OCR öz-testi (donmuş exe'yi doğrulamak için)
    if "--selftest-ocr" in sys.argv:
        _run_ocr_selftest()
        sys.exit(0)

    # Arayüz dilini erkenden ayarla (aşağıdaki mesaj kutuları için)
    config = ConfigManager()
    set_language(config.get("language"))

    # --- Tek Örnek (Single Instance) Kilidi ---
    # Aynı anda yalnızca TEK bir InstantTranslator process'i çalışabilir.
    # Böylece iki process'in aynı kısayolu dinleyip üst üste pencere açması
    # (çift tetiklenme / race condition) kökten engellenir.
    global _single_instance_lock
    _single_instance_lock = QSharedMemory("InstantTranslator_SingleInstance_v1")
    if not _single_instance_lock.create(1):
        QMessageBox.information(None, APP_NAME, t("already_running"))
        sys.exit(0)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, t("error"), t("no_tray"))
        sys.exit(1)

    TranslatorApp(app, config)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
