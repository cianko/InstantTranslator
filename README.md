# Instant Translator

**A lightweight Windows tray app that instantly translates any selected text with a keyboard shortcut.**
_Seçili metni bir kısayol tuşuyla anında çeviren hafif bir Windows tepsi uygulaması._

**🌐 Language / Dil:** [English](#english) · [Türkçe](#türkçe)

---

<a name="english"></a>
## English

Select text anywhere in Windows, press your shortcut (default `Ctrl+Shift+T`), and the translation pops up instantly in a floating window — no browser, no copy-paste, no interruption.

### ✨ Features
- ⚡ **Instant** — translation appears in ~0.2–0.5 s (persistent connection + warm-up).
- ⌨️ **Custom shortcut** — set any combo (e.g. `Ctrl+Shift+T`, `Alt+Q`) from Settings.
- 🪟 **Floating window** — frameless, right-center of the screen, **draggable**.
- ❌ **Easy close** — click outside, press `Esc`, or the `X` button.
- 🌍 **Bilingual UI** — English & Turkish, auto-detected from your Windows language.
- 🎨 **Modern design** — clean white popup, light/dark settings themes.
- 🔁 **Reliable** — 3-engine fallback, 5 s timeout, never freezes.
- 🚫 **No Python required** for end users — ships as a single `.exe` / installer.

### 📥 Download & Install (for users)
1. Go to the [**Releases**](../../releases) page.
2. Download **`InstantTranslator_Setup.exe`**.
3. Run it, pick your language, optionally check **"Start with Windows"**, and install.
4. A blue icon appears in the system tray. Select text anywhere → press `Ctrl+Shift+T`.

> If Windows SmartScreen appears, click **More info → Run anyway** (the app is unsigned).

### 🖱️ Usage
1. **Select** any text in any program.
2. Press the shortcut (default **`Ctrl+Shift+T`**).
3. The translation appears on the right-center of the screen.
4. Close it by clicking outside, pressing `Esc`, or the `X` button. Drag it anywhere by its empty area.

### ⚙️ Settings
Open Settings via the **gear icon** in the translation window, or **right-click the tray icon → Settings**. You can change the shortcut, source/target languages, theme, and interface language. Settings are stored in `%APPDATA%\InstantTranslator\config.json`.

### 🛠️ Build from source (for developers)
Requires **Python 3.10+** on Windows.
```powershell
git clone https://github.com/<your-username>/InstantTranslator.git
cd InstantTranslator
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```
Build a standalone `.exe`:
```powershell
.\build.bat            # -> dist\InstantTranslator.exe
```
Build the installer (needs [Inno Setup 6](https://jrsoftware.org/isdl.php)):
```powershell
ISCC InstantTranslator.iss   # -> installer\InstantTranslator_Setup.exe
```

### 🧰 Tech stack
Python · PySide6 (Qt6) · keyboard · pyperclip · Google Translate (via requests) · PyInstaller · Inno Setup

### 👤 Developer
Developed by **Ahmet Zan** — [LinkedIn](https://www.linkedin.com/in/ahmet-zan-a746a929a)

### 📄 License
[MIT](LICENSE) © 2026 Ahmet Zan

---

<a name="türkçe"></a>
## Türkçe

Windows'ta herhangi bir yerde metin seçin, kısayola basın (varsayılan `Ctrl+Shift+T`), çeviri anında yüzen bir pencerede belirsin — tarayıcı yok, kopyala-yapıştır yok, dikkat dağınıklığı yok.

### ✨ Özellikler
- ⚡ **Anında** — çeviri ~0,2–0,5 sn'de gelir (kalıcı bağlantı + ısıtma).
- ⌨️ **Özel kısayol** — Ayarlar'dan istediğiniz kombinasyonu atayın (ör. `Ctrl+Shift+T`, `Alt+Q`).
- 🪟 **Yüzen pencere** — çerçevesiz, ekranın sağ ortasında, **sürüklenebilir**.
- ❌ **Kolay kapatma** — dışarı tıkla, `Esc` veya `X` butonu.
- 🌍 **İki dilli arayüz** — Türkçe ve İngilizce, Windows dilinize göre otomatik.
- 🎨 **Modern tasarım** — sade beyaz pencere, açık/koyu ayar temaları.
- 🔁 **Kararlı** — 3 kademeli motor yedeği, 5 sn zaman aşımı, asla donmaz.
- 🚫 Son kullanıcı için **Python gerektirmez** — tek `.exe` / kurulum olarak gelir.

### 📥 İndirme & Kurulum (kullanıcılar için)
1. [**Releases**](../../releases) sayfasına gidin.
2. **`InstantTranslator_Setup.exe`** dosyasını indirin.
3. Çalıştırın, dilinizi seçin, isterseniz **"Windows başladığında çalıştır"** kutusunu işaretleyin ve kurun.
4. Sistem tepsisinde mavi bir simge belirir. Bir yerde metin seçin → `Ctrl+Shift+T`.

> Windows SmartScreen uyarısı çıkarsa **Ek bilgi → Yine de çalıştır**'a tıklayın (uygulama imzasızdır).

### 🖱️ Kullanım
1. Herhangi bir programda metni **seçin**.
2. Kısayola basın (varsayılan **`Ctrl+Shift+T`**).
3. Çeviri ekranın sağ ortasında belirir.
4. Kapatmak için dışarı tıklayın, `Esc` veya `X`'e basın. Boş alanından tutup istediğiniz yere sürükleyin.

### ⚙️ Ayarlar
Ayarları, çeviri penceresindeki **çark ikonundan** ya da **tepsi simgesine sağ tıklayıp → Ayarlar** ile açın. Kısayol, kaynak/hedef dil, tema ve arayüz dilini değiştirebilirsiniz. Ayarlar `%APPDATA%\InstantTranslator\config.json` içinde tutulur.

### 🛠️ Kaynaktan derleme (geliştiriciler için)
Windows'ta **Python 3.10+** gerekir.
```powershell
git clone https://github.com/<kullanici-adiniz>/InstantTranslator.git
cd InstantTranslator
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```
Bağımsız `.exe` derleme:
```powershell
.\build.bat            # -> dist\InstantTranslator.exe
```
Kurulum dosyası derleme ([Inno Setup 6](https://jrsoftware.org/isdl.php) gerekir):
```powershell
ISCC InstantTranslator.iss   # -> installer\InstantTranslator_Setup.exe
```

### 🧰 Kullanılan teknolojiler
Python · PySide6 (Qt6) · keyboard · pyperclip · Google Çeviri (requests ile) · PyInstaller · Inno Setup

### 👤 Geliştirici
**Ahmet Zan** tarafından geliştirilmiştir — [LinkedIn](https://www.linkedin.com/in/ahmet-zan-a746a929a)

### 📄 Lisans
[MIT](LICENSE) © 2026 Ahmet Zan
