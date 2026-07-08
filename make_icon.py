"""assets/icon.ico dosyasını üretir (exe simgesi için). PySide6 gerektirir.

Simge oluşturulamazsa build.bat simgesiz devam eder — kritik değildir.
"""
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap
from PySide6.QtWidgets import QApplication


def main():
    QApplication([])  # QPixmap/font işlemleri için bir uygulama nesnesi gerekir
    os.makedirs("assets", exist_ok=True)

    pix = QPixmap(256, 256)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor("#4f8cff"))
    p.setPen(Qt.NoPen)
    p.drawRoundedRect(16, 16, 224, 224, 56, 56)
    p.setPen(QColor("#ffffff"))
    p.setFont(QFont("Segoe UI", 120, QFont.Bold))
    p.drawText(pix.rect(), Qt.AlignCenter, "文")
    p.end()

    ok = pix.save("assets/icon.ico", "ICO")
    print("icon.ico oluşturuldu." if ok else "UYARI: icon.ico oluşturulamadı; simgesiz devam edilecek.")


if __name__ == "__main__":
    main()
