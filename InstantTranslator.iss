; ============================================================
;  Instant Translator - Inno Setup Kurulum Scripti
;  Inno Setup 6+ ile derlenir (https://jrsoftware.org/isdl.php)
; ============================================================

#define MyAppName        "Instant Translator"
#define MyAppVersion     "1.0.0"
#define MyAppPublisher   "Ahmet Zan"
#define MyAppExeName     "InstantTranslator.exe"
#define MyAppURL         "https://www.linkedin.com/in/ahmet-zan-a746a929a"

[Setup]
; AppId benzersiz olmalidir; bu GUID'i koruyun (guncellemelerde ayni kalsin).
AppId={{9F2A7C31-4B8E-4E2A-9C6D-InstantTranslator}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppCopyright=© 2026 Ahmet Zan
VersionInfoCompany={#MyAppPublisher}
VersionInfoCopyright=© 2026 Ahmet Zan
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
; Yonetici gerektirmez; kullanici bazinda kurar (UAC penceresi cikmaz)
PrivilegesRequired=lowest
; Kurulum ciktisi (Setup.exe) buraya olusur
OutputDir=installer
OutputBaseFilename=InstantTranslator_Setup
SetupIconFile=assets\icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

; ------------------------------------------------------------
; 1) COKLU DIL: Varsayilan Ingilizce + Turkce secenegi
; ------------------------------------------------------------
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

; Ozel (dile gore) metinler
[CustomMessages]
english.StartupTask=Start with Windows (run on startup)
turkish.StartupTask=Windows başladığında çalıştır
english.AutoStartGroup=Startup options:
turkish.AutoStartGroup=Başlangıç seçenekleri:

; ------------------------------------------------------------
; 3) KISAYOLLAR ve BASLANGICTA CALISMA (onay kutulari)
; ------------------------------------------------------------
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startupicon"; Description: "{cm:StartupTask}"; GroupDescription: "{cm:AutoStartGroup}"

; ------------------------------------------------------------
; 2) DOSYALAR: exe + iki kilavuz (ana kurulum dizinine)
; ------------------------------------------------------------
[Files]
Source: "dist\InstantTranslator.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\README.txt";            DestDir: "{app}"; Flags: ignoreversion
Source: "dist\KULLANIM.txt";          DestDir: "{app}"; Flags: ignoreversion

; ------------------------------------------------------------
; Kisayollar: Baslat Menusu + Masaustu
; ------------------------------------------------------------
[Icons]
Name: "{group}\{#MyAppName}";                        Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}";  Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}";                  Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; ------------------------------------------------------------
; Windows acilisinda otomatik baslatma (HKCU Run - yonetici gerektirmez)
; Yalnizca kullanici "startupicon" kutusunu isaretlerse yazilir.
; ------------------------------------------------------------
[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
    ValueType: string; ValueName: "{#MyAppName}"; \
    ValueData: """{app}\{#MyAppExeName}"""; \
    Flags: uninsdeletevalue; Tasks: startupicon

; ------------------------------------------------------------
; 4) KURULUM SONRASI: "Uygulamayi simdi baslat" secenegi
; ------------------------------------------------------------
[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; \
    Flags: nowait postinstall skipifsilent

; Kaldirmada calisan uygulamayi kapat (tepside acik kalmasin)
[UninstallRun]
Filename: "{cmd}"; Parameters: "/C taskkill /IM {#MyAppExeName} /F"; \
    Flags: runhidden; RunOnceId: "KillApp"
