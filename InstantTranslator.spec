# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller derleme tarifi (PyInstaller 6.x).

Tek dosya (onefile), konsolsuz (windowed) bir exe üretir.
Derlemek için: build.bat  ya da  pyinstaller --clean InstantTranslator.spec
"""
import os
from PyInstaller.utils.hooks import collect_submodules

# deep-translator, bs4 ve requests'i dinamik kullandığından tüm alt modüllerini topla
hiddenimports = collect_submodules('deep_translator')
hiddenimports += ['bs4', 'requests', 'keyboard', 'pyperclip']

# Kullanılmayan ağır Qt modüllerini hariç tut (exe boyutunu küçültür)
excludes = [
    'tkinter',
    'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets', 'PySide6.QtWebEngineQuick',
    'PySide6.QtQuick', 'PySide6.QtQml', 'PySide6.QtQuick3D',
    'PySide6.Qt3DCore', 'PySide6.Qt3DRender', 'PySide6.Qt3DInput',
    'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets',
    'PySide6.QtCharts', 'PySide6.QtDataVisualization',
    'PySide6.QtPdf', 'PySide6.QtPdfWidgets', 'PySide6.QtSql',
    'PySide6.QtTest', 'PySide6.QtDesigner', 'PySide6.QtBluetooth',
    'PySide6.QtPositioning', 'PySide6.QtSensors',
]

icon_path = 'assets/icon.ico' if os.path.exists('assets/icon.ico') else None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='InstantTranslator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                 # UPX bazı Qt DLL'lerini bozabildiği için kapalı
    runtime_tmpdir=None,
    console=False,             # --noconsole / --windowed karşılığı
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)
