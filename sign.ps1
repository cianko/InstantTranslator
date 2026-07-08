<#
============================================================
 Instant Translator - Kod Imzalama (Code Signing) Scripti
============================================================
 Gercek bir kod imzalama sertifikasi (.pfx) ile hem uygulamayi
 (dist\InstantTranslator.exe) hem de kurulumu
 (installer\InstantTranslator_Setup.exe) imzalar ve zaman damgalar.

 KULLANIM:
   powershell -ExecutionPolicy Bypass -File .\sign.ps1 `
       -PfxPath "C:\yol\sertifikam.pfx" -PfxPassword "PAROLA"

 ONEMLI:
 - SmartScreen / "Bilinmeyen yayimci" uyarisini KALDIRMAK icin sertifika
   guvenilir bir CA'dan (Sectigo, DigiCert, GlobalSign vb.) alinmis olmalidir.
 - Self-signed (kendinden imzali) sertifika SmartScreen'i GECMEZ; yalnizca
   test/ic kullanim icindir.
 - EV (Extended Validation) sertifikalari SmartScreen itibarini ANINDA saglar;
   OV (standart) sertifikalarda itibar zamanla (indirme sayisiyla) olusur.

 DOGRU SIRA (installer imzali exe icersin):
   1) build.bat            -> dist\InstantTranslator.exe uretir
   2) sign.ps1 (bu script) -> exe'yi imzalar   <-- once exe
   3) ISCC InstantTranslator.iss -> installer'i derler (imzali exe'yi paketler)
   4) sign.ps1 tekrar      -> installer'i da imzalar
   (Basitce: bu scripti 1. adimdan sonra ve 3. adimdan sonra calistirin.)
============================================================
#>
param(
    [Parameter(Mandatory = $true)][string] $PfxPath,
    [Parameter(Mandatory = $true)][string] $PfxPassword,
    [string] $TimestampServer = "http://timestamp.digicert.com"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

$targets = @(
    (Join-Path $root "dist\InstantTranslator.exe"),
    (Join-Path $root "installer\InstantTranslator_Setup.exe")
)

if (-not (Test-Path $PfxPath)) {
    Write-Error "PFX bulunamadi: $PfxPath"
    exit 1
}

# PFX sertifikasini parola ile yukle (Windows PowerShell 5.1 uyumlu)
$flags = [System.Security.Cryptography.X509Certificates.X509KeyStorageFlags]"Exportable,PersistKeySet"
try {
    $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($PfxPath, $PfxPassword, $flags)
} catch {
    Write-Error "PFX yuklenemedi (parola yanlis olabilir): $($_.Exception.Message)"
    exit 1
}
Write-Host "Sertifika yuklendi: $($cert.Subject)" -ForegroundColor Cyan

$allOk = $true
foreach ($file in $targets) {
    if (-not (Test-Path $file)) {
        Write-Warning "Atlandi (bulunamadi): $file"
        continue
    }
    Write-Host "Imzalaniyor: $(Split-Path $file -Leaf) ..." -NoNewline
    $sig = Set-AuthenticodeSignature -FilePath $file -Certificate $cert `
           -TimestampServer $TimestampServer -HashAlgorithm SHA256
    if ($sig.Status -eq "Valid") {
        Write-Host "  [Valid]" -ForegroundColor Green
    } else {
        Write-Host "  [$($sig.Status)]" -ForegroundColor Yellow
        Write-Host "    Not: Sertifika guvenilir bir CA'dan degilse durum 'UnknownError' gorunur;" -ForegroundColor DarkGray
        Write-Host "    imza yine de gomulur. Gercek CA sertifikasiyla 'Valid' olur." -ForegroundColor DarkGray
        $allOk = $false
    }
}

Write-Host ""
if ($allOk) {
    Write-Host "TAMAM: Tum dosyalar gecerli sekilde imzalandi ve zaman damgalandi." -ForegroundColor Green
} else {
    Write-Host "Imzalama tamamlandi (yukaridaki durum notlarina bakin)." -ForegroundColor Yellow
}
