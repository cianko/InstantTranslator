"""Kısayol, dil ve tema seçimi için ayar penceresi (İngilizce/Türkçe).

Kısayol yakalama, özel HotkeyEdit (QLineEdit türevi) ile yapılır. Tuş yakalama
YALNIZCA kutu odaktayken (kullanıcı içine tıkladığında) aktiftir; kutu odağını
kaybedince (başka yere tıklayınca) anında pasifleşir. Sadece modifier'a basılınca
kaydedilmez, ana tuşa basılınca tüm kombinasyon bir bütün olarak kaydedilir.
"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox, QDialog, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QVBoxLayout,
)

from src.i18n import t

# Kaynak/hedef dil kodları (adları i18n'den gelir)
LANG_CODES = ["auto", "en", "tr", "de", "fr", "es", "it", "ru", "ar"]
TARGET_CODES = [c for c in LANG_CODES if c != "auto"]

# Görünen ad karşılıkları (kısayol gösterimi)
_DISPLAY = {"ctrl": "Ctrl", "shift": "Shift", "alt": "Alt", "windows": "Win"}

# Modifier olmayan özel tuşlar (Qt.Key -> keyboard kütüphanesi adı)
_SPECIAL_KEYS = {
    Qt.Key_Space: "space", Qt.Key_Tab: "tab", Qt.Key_Backspace: "backspace",
    Qt.Key_Return: "enter", Qt.Key_Enter: "enter", Qt.Key_Insert: "insert",
    Qt.Key_Delete: "delete", Qt.Key_Home: "home", Qt.Key_End: "end",
    Qt.Key_PageUp: "page up", Qt.Key_PageDown: "page down",
    Qt.Key_Up: "up", Qt.Key_Down: "down", Qt.Key_Left: "left", Qt.Key_Right: "right",
    Qt.Key_F1: "f1", Qt.Key_F2: "f2", Qt.Key_F3: "f3", Qt.Key_F4: "f4",
    Qt.Key_F5: "f5", Qt.Key_F6: "f6", Qt.Key_F7: "f7", Qt.Key_F8: "f8",
    Qt.Key_F9: "f9", Qt.Key_F10: "f10", Qt.Key_F11: "f11", Qt.Key_F12: "f12",
}


def _to_display(kb_str: str) -> str:
    if not kb_str:
        return ""
    parts = []
    for p in kb_str.split("+"):
        p = p.strip().lower()
        parts.append(_DISPLAY.get(p, p.upper() if len(p) == 1 else p.capitalize()))
    return " + ".join(parts)


class HotkeyEdit(QLineEdit):
    """Yalnızca odaktayken tuş kombinasyonu yakalayan salt-okunur kutu."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFocusPolicy(Qt.ClickFocus)  # yalnızca tıklayınca odak
        self.setPlaceholderText(t("hotkey_placeholder"))
        self._capturing = False
        self._sequence = ""  # keyboard biçimi, ör. "ctrl+shift+t"

    def set_hotkey(self, kb_str: str):
        self._sequence = (kb_str or "").strip().lower()
        self._render()

    def hotkey(self) -> str:
        return self._sequence

    def _render(self):
        self.setText(_to_display(self._sequence))

    def focusInEvent(self, event):
        self._capturing = True
        self.setText(t("hotkey_press"))
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self._capturing = False
        self._render()
        super().focusOutEvent(event)

    def _modifier_parts(self, mods):
        parts = []
        if mods & Qt.ControlModifier:
            parts.append("ctrl")
        if mods & Qt.ShiftModifier:
            parts.append("shift")
        if mods & Qt.AltModifier:
            parts.append("alt")
        if mods & Qt.MetaModifier:
            parts.append("windows")
        return parts

    def _key_name(self, key, event):
        """Ana tuş adı; modifier altında event.text() güvenilmez olduğundan
        önce TUŞ KODUNDAN türetilir."""
        if Qt.Key_A <= key <= Qt.Key_Z:
            return chr(key).lower()
        if Qt.Key_0 <= key <= Qt.Key_9:
            return chr(key)
        if key in _SPECIAL_KEYS:
            return _SPECIAL_KEYS[key]
        txt = event.text()
        if txt and len(txt) == 1 and txt.isprintable() and not txt.isspace():
            return txt.lower()
        return None

    def keyPressEvent(self, event):
        if not self._capturing:
            event.ignore()
            return

        key = event.key()

        # Yalnızca modifier -> kaydetme, devamını bekle (canlı önizleme göster)
        if key in (Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta):
            preview = self._modifier_parts(event.modifiers())
            add = {Qt.Key_Control: "ctrl", Qt.Key_Shift: "shift",
                   Qt.Key_Alt: "alt", Qt.Key_Meta: "windows"}[key]
            if add not in preview:
                preview.append(add)
            self.setText(_to_display("+".join(preview)) + " + …")
            event.accept()
            return

        # Ana tuş -> tüm modifier'larla birlikte bir bütün olarak kaydet
        parts = self._modifier_parts(event.modifiers())
        name = self._key_name(key, event)
        if name:
            parts.append(name)
            self._sequence = "+".join(parts)
            self._render()
            self.clearFocus()  # kaydet ve odağı kaldır
        event.accept()


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle(t("window_title_settings"))
        self.setMinimumWidth(400)
        self.setFocusPolicy(Qt.StrongFocus)
        self._build()
        self._apply_theme(config.get("theme"))

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(16)

        title = QLabel(t("settings"))
        title.setObjectName("title")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)

        self.hotkey_edit = HotkeyEdit()
        self.hotkey_edit.set_hotkey(self.config.get("hotkey"))
        form.addRow(t("lbl_shortcut"), self.hotkey_edit)

        self.source_combo = QComboBox()
        for code in LANG_CODES:
            self.source_combo.addItem(t("lang_" + code), code)
        self._select(self.source_combo, self.config.get("source_lang"))
        form.addRow(t("lbl_source"), self.source_combo)

        self.target_combo = QComboBox()
        for code in TARGET_CODES:
            self.target_combo.addItem(t("lang_" + code), code)
        self._select(self.target_combo, self.config.get("target_lang"))
        form.addRow(t("lbl_target"), self.target_combo)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem(t("theme_dark"), "dark")
        self.theme_combo.addItem(t("theme_light"), "light")
        self._select(self.theme_combo, self.config.get("theme"))
        form.addRow(t("lbl_theme"), self.theme_combo)

        self.ui_lang_combo = QComboBox()
        self.ui_lang_combo.addItem(t("ui_lang_auto"), "auto")
        self.ui_lang_combo.addItem(t("ui_lang_en"), "en")
        self.ui_lang_combo.addItem(t("ui_lang_tr"), "tr")
        self._select(self.ui_lang_combo, self.config.get("language"))
        form.addRow(t("lbl_ui_language"), self.ui_lang_combo)

        layout.addLayout(form)

        hint = QLabel(t("settings_hint"))
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = QPushButton(t("cancel"))
        cancel.clicked.connect(self.reject)
        save = QPushButton(t("save"))
        save.setObjectName("save")
        save.setDefault(True)
        save.clicked.connect(self.accept)
        btn_row.addWidget(cancel)
        btn_row.addWidget(save)
        layout.addLayout(btn_row)

        # --- Geliştirici imzası (tıklanabilir LinkedIn bağlantısı) ---
        layout.addSpacing(6)
        credit = QLabel(
            '<a href="https://www.linkedin.com/in/ahmet-zan-a746a929a" '
            'style="color:#8a8f98; text-decoration:none;">Developed by Ahmet Zan</a>'
        )
        credit.setObjectName("credit")
        credit.setAlignment(Qt.AlignCenter)
        credit.setOpenExternalLinks(True)  # tıklayınca tarayıcıda açar
        credit.setTextInteractionFlags(Qt.TextBrowserInteraction)
        credit.setCursor(Qt.PointingHandCursor)
        credit.setStyleSheet("font-size: 11px; padding-top: 2px;")
        layout.addWidget(credit)

    def _select(self, combo, value):
        idx = combo.findData(value)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    def showEvent(self, event):
        super().showEvent(event)
        # Açılışta odağı nötrle; kısayol kutusu odakta olmasın.
        QTimer.singleShot(0, self.setFocus)

    def get_values(self):
        return {
            "hotkey": self.hotkey_edit.hotkey() or self.config.get("hotkey"),
            "source_lang": self.source_combo.currentData(),
            "target_lang": self.target_combo.currentData(),
            "theme": self.theme_combo.currentData(),
            "language": self.ui_lang_combo.currentData(),
        }

    def _apply_theme(self, theme):
        if theme == "dark":
            self.setStyleSheet("""
                QDialog { background-color: #1e1f22; }
                QLabel { color: #e6e7ea; font-size: 13px; }
                #title { font-size: 18px; font-weight: 700; color: #ffffff; }
                #hint { color: #9aa0a6; font-size: 11px; }
                QComboBox, QLineEdit {
                    background-color: #2b2d31; color: #f2f3f5;
                    border: 1px solid #3a3c42; border-radius: 8px; padding: 6px 8px;
                }
                QComboBox QAbstractItemView {
                    background-color: #2b2d31; color: #f2f3f5; selection-background-color: #4f8cff;
                }
                QLineEdit:focus { border: 1px solid #4f8cff; }
                QPushButton {
                    background-color: #33353a; color: #f2f3f5;
                    border: none; border-radius: 8px; padding: 8px 18px; font-size: 13px;
                }
                QPushButton:hover { background-color: #3e4046; }
                #save { background-color: #4f8cff; color: white; font-weight: 600; }
                #save:hover { background-color: #3b7bff; }
            """)
        else:
            self.setStyleSheet("""
                QDialog { background-color: #f7f8fa; }
                QLabel { color: #1a1a1a; font-size: 13px; }
                #title { font-size: 18px; font-weight: 700; color: #111; }
                #hint { color: #6b7075; font-size: 11px; }
                QComboBox, QLineEdit {
                    background-color: #ffffff; color: #1a1a1a;
                    border: 1px solid #d7dae0; border-radius: 8px; padding: 6px 8px;
                }
                QLineEdit:focus { border: 1px solid #2563eb; }
                QPushButton {
                    background-color: #eceef1; color: #1a1a1a;
                    border: none; border-radius: 8px; padding: 8px 18px; font-size: 13px;
                }
                QPushButton:hover { background-color: #e0e3e7; }
                #save { background-color: #2563eb; color: white; font-weight: 600; }
                #save:hover { background-color: #1d4ed8; }
            """)
