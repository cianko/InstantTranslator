"""Aktif programdaki seçili metni panoya alarak yakalar.

Mantık: mevcut pano içeriğini yedekle -> panoya bir 'sentinel' yaz ->
Ctrl+C gönder -> pano değişene kadar bekle -> yakala -> eski panoyu geri yükle.
"""
import time

import keyboard
import pyperclip

_SENTINEL = "\x00__IT_SENTINEL__\x00"


def _wait_modifiers_released(timeout: float = 0.4):
    """Kısayolun değiştirici tuşları (Ctrl/Shift/Alt) fiziksel olarak bırakılana
    kadar bekler. Böylece gönderilen Ctrl+C, hâlâ basılı Shift yüzünden
    Ctrl+Shift+C'ye dönüşüp kopyalamayı düşürmez (yanlış-pozitif snip önlenir)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            still = (keyboard.is_pressed("ctrl") or keyboard.is_pressed("shift")
                     or keyboard.is_pressed("alt") or keyboard.is_pressed("windows"))
        except Exception:
            still = False
        if not still:
            return
        time.sleep(0.02)


def get_selected_text(wait_ms: int = 300, attempts: int = 3) -> str:
    """Seçili metni panoya alıp döndürür (pano doğrulaması + tekrar deneme).

    Panoya önce bir 'sentinel' yazılır, sonra Ctrl+C gönderilir ve pano
    SENTINEL'DEN farklı bir değere dönene kadar (en fazla wait_ms ms) beklenir.
    Böylece yalnızca TAZE kopyalanan metin yakalanır; eski pano içeriği asla
    çeviriye gönderilmez.

    Metin alınamazsa Ctrl+C tekrar tetiklenir (toplam 'attempts' deneme).
    Bu sabır sayesinde NORMAL kopyalanabilir metin snip'e düşmez; snip yalnızca
    içerik GERÇEKTEN kopyalamaya izin vermediğinde (izinli olmayan PDF) devreye girer.
    """
    # Kullanıcının panosunu yedekle
    try:
        original = pyperclip.paste()
    except Exception:
        original = ""

    # Önce kısayol tuşlarının bırakılmasını bekle (Ctrl+C temiz gitsin)
    _wait_modifiers_released(0.4)

    captured = ""
    for attempt in range(attempts):
        # Panoyu benzersiz bir işaretle; Ctrl+C bunun üzerine yazacak
        try:
            pyperclip.copy(_SENTINEL)
        except Exception:
            pass

        # Kalan değiştiricileri de programatik olarak bırak, sonra kopyala.
        for mod in ("ctrl", "shift", "alt", "windows"):
            try:
                keyboard.release(mod)
            except Exception:
                pass
        time.sleep(0.05 if attempt == 0 else 0.10)
        keyboard.send("ctrl+c")

        # Pano SENTINEL'den farklı bir değere dönene kadar bekle (maks. wait_ms)
        deadline = time.time() + (wait_ms / 1000.0)
        while time.time() < deadline:
            try:
                current = pyperclip.paste()
            except Exception:
                current = ""
            if current and current != _SENTINEL:  # taze kopya geldi
                captured = current
                break
            time.sleep(0.02)

        if captured:
            break  # başarılı; tekrar denemeye gerek yok

    # Kullanıcının eski panosunu geri yükle
    try:
        pyperclip.copy(original)
    except Exception:
        pass

    return captured.strip()
