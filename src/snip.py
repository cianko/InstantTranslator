"""Ekran bölgesi seçici (snip) — kopyalama engelli içerikte OCR için.

Kullanıcı fareyle bir dikdörtgen çizer; seçilen bölgenin ekran görüntüsü
PNG bayt dizisi olarak 'captured' sinyaliyle verilir. Karartma efektinin
görüntüye karışmaması için ekran, karartmadan ÖNCE yakalanır ve seçim o
temiz görüntüden kırpılır. Üstte kullanıcıya ne yapacağını anlatan bir
yönerge şeridi gösterilir.
"""
from PySide6.QtCore import Qt, QRect, QBuffer, QByteArray, Signal
from PySide6.QtGui import QPainter, QColor, QGuiApplication, QCursor, QPen, QFont
from PySide6.QtWidgets import QWidget

from src.i18n import t


class SnipOverlay(QWidget):
    captured = Signal(bytes)   # seçilen bölgenin PNG baytları
    cancelled = Signal()

    def __init__(self):
        super().__init__(None)
        # Tam ekran, çerçevesiz, en üstte; odak alabilsin diye normal Window
        self.setWindowFlags(
            Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        self.setCursor(Qt.CrossCursor)
        self._origin = None
        self._rect = QRect()
        self._pixmap = None  # karartılmamış ekran görüntüsü

    def start(self):
        """İmlecin bulunduğu ekranı tam ekran kaplayıp seçim moduna geçer."""
        screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        geo = screen.geometry()
        self._pixmap = screen.grabWindow(0)  # temiz (dim'siz) görüntüyü önce al
        self._origin = None
        self._rect = QRect()
        self.setGeometry(geo)
        self.showFullScreen()
        self.raise_()
        self.activateWindow()
        self.setFocus()
        # Windows ön plan kilidini aşmak için klavyeyi zorla yakala (Esc çalışsın)
        try:
            self.grabKeyboard()
        except Exception:
            pass

    def _finish(self, png=None):
        try:
            self.releaseKeyboard()
        except Exception:
            pass
        self.hide()
        if png is not None:
            self.captured.emit(png)
        else:
            self.cancelled.emit()
        self.close()

    def paintEvent(self, event):
        p = QPainter(self)
        if self._pixmap is not None:
            p.drawPixmap(self.rect(), self._pixmap)
        overlay = QColor(0, 0, 0, 120)
        r = self._rect.normalized()
        if r.isNull() or r.width() == 0:
            p.fillRect(self.rect(), overlay)
        else:
            # Seçim dışını karart, seçili bölgeyi net bırak
            p.fillRect(QRect(0, 0, self.width(), r.top()), overlay)
            p.fillRect(QRect(0, r.bottom(), self.width(), self.height() - r.bottom()), overlay)
            p.fillRect(QRect(0, r.top(), r.left(), r.height()), overlay)
            p.fillRect(QRect(r.right(), r.top(), self.width() - r.right(), r.height()), overlay)
            p.setPen(QPen(QColor("#4f8cff"), 2))
            p.drawRect(r)

        self._draw_hint(p)
        p.end()

    def _draw_hint(self, p):
        """Üst ortada yönerge şeridi çizer."""
        text = t("snip_hint")
        font = QFont("Segoe UI", 12)
        font.setBold(True)
        p.setFont(font)
        fm = p.fontMetrics()
        tw = fm.horizontalAdvance(text)
        th = fm.height()
        pad_x, pad_y = 22, 12
        bw, bh = tw + pad_x * 2, th + pad_y * 2
        bx = (self.width() - bw) // 2
        by = 40
        # Arka plan kutusu
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(37, 99, 235, 235))  # mavi, hafif saydam
        p.drawRoundedRect(QRect(bx, by, bw, bh), 10, 10)
        # Metin
        p.setPen(QColor("#ffffff"))
        p.drawText(QRect(bx, by, bw, bh), Qt.AlignCenter, text)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._origin = e.position().toPoint()
            self._rect = QRect(self._origin, self._origin)
            self.update()

    def mouseMoveEvent(self, e):
        if self._origin is not None and (e.buttons() & Qt.LeftButton):
            self._rect = QRect(self._origin, e.position().toPoint())
            self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self._origin is not None:
            rect = self._rect.normalized()
            if rect.width() > 6 and rect.height() > 6:
                self._finish(self._grab_region(rect))
            else:
                # Sürüklemeden tek tık -> iptal
                self._finish(None)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self._finish(None)
        else:
            super().keyPressEvent(e)

    def _grab_region(self, rect: QRect) -> bytes:
        # Mantıksal (widget) koordinatları -> fiziksel piksellere ölçekle (DPI güvenli)
        sx = self._pixmap.width() / max(1, self.width())
        sy = self._pixmap.height() / max(1, self.height())
        phys = QRect(int(rect.x() * sx), int(rect.y() * sy),
                     int(rect.width() * sx), int(rect.height() * sy))
        cropped = self._pixmap.copy(phys)
        ba = QByteArray()
        buf = QBuffer(ba)
        buf.open(QBuffer.WriteOnly)
        cropped.save(buf, "PNG")
        return bytes(ba)
