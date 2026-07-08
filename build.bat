@echo off
REM ============================================================
REM  Instant Translator - Tek tikla EXE derleyici
REM  Cikti: dist\InstantTranslator.exe (Python gerektirmez)
REM ============================================================
setlocal
cd /d "%~dp0"

REM venv varsa onun Python'unu kullan, yoksa sistemdekini
if exist "venv\Scripts\python.exe" (
    set "PY=venv\Scripts\python.exe"
) else (
    set "PY=python"
)

echo.
echo [1/4] Bagimliliklar kuruluyor...
%PY% -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo.
echo [2/4] PyInstaller kuruluyor...
%PY% -m pip install --upgrade pyinstaller
if errorlevel 1 goto :error

echo.
echo [3/4] Uygulama simgesi olusturuluyor...
%PY% make_icon.py

echo.
echo [4/4] EXE derleniyor (bu islem birkac dakika surebilir)...
%PY% -m PyInstaller --noconfirm --clean InstantTranslator.spec
if errorlevel 1 goto :error

echo.
echo ============================================================
echo  BASARILI!  Cikti dosyasi:
echo    %CD%\dist\InstantTranslator.exe
echo  Bu exe'yi baska bir Windows bilgisayara kopyalayip
echo  cift tiklayarak calistirabilirsiniz (Python gerekmez).
echo ============================================================
goto :end

:error
echo.
echo HATA: Derleme sirasinda bir sorun olustu. Yukaridaki mesajlari kontrol edin.

:end
pause
endlocal
