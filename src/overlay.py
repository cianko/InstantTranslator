"""İmlecin yanında beliren, beyaz arka planlı, X kapatma butonlu yüzen pencere.

Qt.Popup bayrağı sayesinde pencere dışına (başka uygulama/masaüstü) tıklandığında,
yani odak kaybedildiğinde otomatik kapanır. Ayrıca sağ üstteki X butonu ve Esc
tuşu da pencereyi kapatır.

Önemli: Bu pencere, metin panoya ALINDIKTAN SONRA gösterilir (bkz. main.py).
Böylece açılırken kaynak programın odağını/seçimini bozmaz.
"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QCursor, QGuiApplication
from PySide6.QtWidgets import (
    QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QPushButton,
    QVBoxLayout, QWidget,
)
import pyperclip

from src.i18n import t


class TranslationOverlay(QWidget):
    def __init__(self, theme="dark"):
        super().__init__(None)
        self.theme = theme  # geriye dönük uyumluluk için tutuluyor (artık pencere hep beyaz)
        self._translated_text = ""
        self._cancelled = False
        self.on_settings = None  # main.py tarafından atanır (çark ikonu için)
        self._dragging = False   # sürükleme durumu
        self._drag_offset = None
        # Qt.Popup: dışarı tıklanınca / odak kaybında otomatik kapanır
        self.setWindowFlags(
            Qt.Popup | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(18, 18, 18, 18)  # gölge için boşluk

        self.card = QFrame()
        self.card.setObjectName("card")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(18, 12, 12, 16)
        card_layout.setSpacing(10)

        # --- Üst satır: dil etiketi + X kapatma butonu ---
        header = QHBoxLayout()
        header.setSpacing(8)
        self.lang_label = QLabel("EN → TR")
        self.lang_label.setObjectName("lang")
        header.addWidget(self.lang_label)
        header.addStretch()
        # Çark (Ayarlar) ikonu — X butonunun hemen soluna
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setObjectName("gear")
        self.settings_btn.setFixedSize(26, 26)
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.setToolTip(t("tip_settings"))
        self.settings_btn.clicked.connect(self._open_settings)
        header.addWidget(self.settings_btn, 0, Qt.AlignTop)
        # X kapatma butonu
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("close")
        self.close_btn.setFixedSize(26, 26)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setToolTip(t("tip_close"))
        self.close_btn.clicked.connect(self.close)
        header.addWidget(self.close_btn, 0, Qt.AlignTop)
        card_layout.addLayout(header)

        self.original_label = QLabel("")
        self.original_label.setObjectName("original")
        self.original_label.setWordWrap(True)
        card_layout.addWidget(self.original_label)

        self.sep = QFrame()
        self.sep.setObjectName("sep")
        self.sep.setFrameShape(QFrame.HLine)
        card_layout.addWidget(self.sep)

        self.translated_label = QLabel("")
        self.translated_label.setObjectName("translated")
        self.translated_label.setWordWrap(True)
        card_layout.addWidget(self.translated_label)

        # --- Alt satir: Kopyala ---
        footer = QHBoxLayout()
        footer.addStretch()
        self.copy_btn = QPushButton(t("copy"))
        self.copy_btn.setObjectName("copy")
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.clicked.connect(self._copy)
        footer.addWidget(self.copy_btn)
        card_layout.addLayout(footer)

        # --- Geliştirici imzası (tıklanabilir LinkedIn bağlantısı) ---
        self.credit = QLabel(
            '<a href="https://www.linkedin.com/in/ahmet-zan-a746a929a" '
            'style="color:#a0a4ab; text-decoration:none;">Developed by Ahmet Zan</a>'
        )
        self.credit.setObjectName("credit")
        self.credit.setAlignment(Qt.AlignCenter)
        self.credit.setOpenExternalLinks(True)  # tıklayınca tarayıcıda açar
        self.credit.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.credit.setCursor(Qt.PointingHandCursor)
        self.credit.setStyleSheet("font-size: 10px; padding-top: 2px;")
        card_layout.addWidget(self.credit)

        outer.addWidget(self.card)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(34)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 70))
        self.card.setGraphicsEffect(shadow)

        self.setMaximumWidth(480)
        self._apply_style()

    def _apply_style(self):
        # Gereksinim 1: açılır pencere arka planı TAMAMEN BEYAZ
        self.setStyleSheet("""
            #card {
                background-color: #ffffff;
                border: 1px solid #e3e5e8;
                border-radius: 14px;
            }
            #lang {
                color: #2563eb; font-size: 12px; font-weight: 600;
                letter-spacing: 0.5px; padding-top: 5px;
            }
            #original { color: #6b7075; font-size: 13px; }
            #translated { color: #111111; font-size: 15px; font-weight: 500; }
            #sep { border: none; background-color: #ececf0; max-height: 1px; }
            #gear {
                color: #6b7075; background-color: transparent;
                border: none; border-radius: 13px; font-size: 15px;
            }
            #gear:hover { background-color: #e7efff; color: #2563eb; }
            #close {
                color: #6b7075; background-color: transparent;
                border: none; border-radius: 13px; font-size: 14px; font-weight: bold;
            }
            #close:hover { background-color: #f6d9d9; color: #c0392b; }
            #copy {
                color: #ffffff; background-color: #2563eb;
                border: none; border-radius: 8px; padding: 5px 14px; font-size: 12px;
            }
            #copy:hover { background-color: #1d4ed8; }
        """)

    def _copy(self):
        if self._translated_text:
            pyperclip.copy(self._translated_text)
            self.copy_btn.setText(t("copied"))
            QTimer.singleShot(1200, lambda: self.copy_btn.setText(t("copy")))

    def retranslate(self):
        """Dil değişince statik metinleri günceller (main.py tarafından çağrılır)."""
        self.settings_btn.setToolTip(t("tip_settings"))
        self.close_btn.setToolTip(t("tip_close"))
        self.copy_btn.setText(t("copy"))

    def _open_settings(self):
        # Popup'ı kapat, sonra ayar penceresini aç (grab çakışmasını önlemek için ertelenir)
        self.close()
        if callable(self.on_settings):
            QTimer.singleShot(0, self.on_settings)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    # --- Sürükleme (boş beyaz alandan tutup taşıma) ---
    # Etiketler (QLabel) fareyi tüketmediği için tıklama buraya gelir; butonlar
    # (⚙, ✕, Kopyala) kendi tıklamalarını işler, bu yüzden onlardan sürükleme başlamaz.
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging and (event.buttons() & Qt.LeftButton):
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._dragging = False
        event.accept()

    def closeEvent(self, event):
        self._cancelled = True
        super().closeEvent(event)

    def force_close(self):
        """Kural 1 (Tekil Pencere): Açık bir çeviri penceresi varsa anında kapatır.

        Yeni bir çeviri tetiklendiğinde çağrılır; böylece ekranda aynı anda
        birden fazla pencere kalması imkânsız olur.
        """
        self._cancelled = True
        if self.isVisible():
            self.hide()

    # ---- Genel API (ana thread'den sinyallerle çağrılır) ----
    def show_loading(self, source, target):
        self._cancelled = False
        self.translated_label.setStyleSheet("")  # normal renk
        self.lang_label.setText(f"{source.upper()} → {target.upper()}")
        self.original_label.hide()
        self.sep.hide()
        self.copy_btn.hide()
        self.translated_label.setText(t("translating"))
        self._popup()

    def show_result(self, original, translated, source, target):
        if self._cancelled:
            return
        self._translated_text = translated
        self.translated_label.setStyleSheet("")  # normal (siyah) renk
        self.copy_btn.setText(t("copy"))
        self.lang_label.setText(f"{source.upper()} → {target.upper()}")
        self.original_label.setText(original)
        self.original_label.show()
        self.sep.show()
        self.copy_btn.show()
        self.translated_label.setText(translated)
        self._popup()

    def show_error(self, message):
        if self._cancelled:
            return
        self.original_label.hide()
        self.sep.hide()
        self.copy_btn.hide()
        # Kırmızı ton hata mesajı
        self.translated_label.setStyleSheet("color: #c0392b; font-size: 14px; font-weight: 600;")
        self.translated_label.setText(message)
        self._popup()

    def _popup(self):
        self.adjustSize()
        self._place_window()
        if not self.isVisible():
            self.show()
        self.raise_()
        self.activateWindow()

    def _place_window(self):
        """Pencereyi HER ZAMAN ekranın SAĞ ORTASINA yerleştirir (sabit konum).

        (Ekran boşluğu tespiti kaldırıldı — gereksiz karmaşa/performans yükü.)
        Kullanıcı, pencereyi tutup dilediği yere sürükleyebilir.

        X = EkranGenişliği - PencereGenişliği - 40  (sağdan boşluk)
        Y = (EkranYüksekliği - PencereYüksekliği) / 2
        """
        self.adjustSize()
        screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        geo = screen.availableGeometry()  # görev çubuğu hariç kullanılabilir alan
        w, h = self.width(), self.height()
        x = geo.x() + geo.width() - w - 40
        y = geo.y() + (geo.height() - h) // 2
        if x < geo.x():
            x = geo.x() + 8
        if y < geo.y():
            y = geo.y() + 8
        self.move(x, y)
