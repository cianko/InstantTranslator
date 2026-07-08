"""Aktif programdaki seçili metni panoya alarak yakalar.

Mantık: mevcut pano içeriğini yedekle -> panoya bir 'sentinel' yaz ->
Ctrl+C gönder -> pano değişene kadar bekle -> yakala -> eski panoyu geri yükle.
"""
import time

import keyboard
import pyperclip

_SENTINEL = "\x00__IT_SENTINEL__\x00"


def get_selected_text(wait_ms: int = 250, attempts: int = 2) -> str:
    """Seçili metni panoya alıp döndürür (pano doğrulaması + tekrar deneme).

    Panoya önce bir 'sentinel' yazılır, sonra Ctrl+C gönderilir ve pano
    SENTINEL'DEN farklı bir değere dönene kadar (en fazla wait_ms ms) beklenir.
    Böylece yalnızca TAZE kopyalanan metin yakalanır; eski pano içeriği asla
    çeviriye gönderilmez.

    Eğer metin alınamazsa (kopyalama düşerse), 0.1 sn gecikmeyle Ctrl+C tekrar
    tetiklenir (toplam 'attempts' deneme). Bu, ara sıra kopyalamanın kaçırılıp
    çevirinin hiç gelmemesi sorununu giderir.
    """
    # Kullanıcının panosunu yedekle
    try:
        original = pyperclip.paste()
    except Exception:
        original = ""

    captured = ""
    for attempt in range(attempts):
        # Panoyu benzersiz bir işaretle; Ctrl+C bunun üzerine yazacak
        try:
            pyperclip.copy(_SENTINEL)
        except Exception:
            pass

        # Basılı olabilecek değiştirici tuşları bırak, sonra kopyala.
        for mod in ("ctrl", "shift", "alt", "windows"):
            try:
                keyboard.release(mod)
            except Exception:
                pass
        # İlk denemede minik, sonraki denemelerde 0.1 sn gecikme
        time.sleep(0.1 if attempt > 0 else 0.05)
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
