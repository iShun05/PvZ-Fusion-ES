param([string]$GameDir = $PSScriptRoot)
$ErrorActionPreference = 'Stop'
# La actualización se ejecuta al abrir el juego y nunca durante una partida.
try {
    if (Get-Process -Name PlantsVsZombiesRH -ErrorAction SilentlyContinue) { return }
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $Installed = Get-Content -LiteralPath (Join-Path $GameDir 'UserData\PvZ-Fusion-ES.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    $Release = Invoke-RestMethod -Uri 'https://api.github.com/repos/iShun05/PvZ-Fusion-ES/releases/latest' -Headers @{ 'User-Agent'='PvZ-Fusion-ES' }
    if ($Release.tag_name -notmatch '^v\d+\.\d+$') { throw 'Versión publicada no válida.' }
    if ([version]$Release.tag_name.Substring(1) -le [version]$Installed.version.Substring(1)) { return }
    $Asset = $Release.assets | Where-Object name -eq 'PvZ-Fusion-ES.zip' | Select-Object -First 1
    if (-not $Asset -or $Asset.browser_download_url -notlike 'https://github.com/iShun05/PvZ-Fusion-ES/releases/download/*') { throw 'No hay un paquete compatible listo.' }
    if ($Asset.digest -notmatch '^sha256:[a-f0-9]{64}$') { throw 'Falta la suma de integridad.' }
    $Work = Join-Path $env:TEMP ('PvZ-Fusion-ES-' + [guid]::NewGuid().ToString('N'))
    [IO.Directory]::CreateDirectory($Work) | Out-Null
    try {
        $Zip = Join-Path $Work 'parche.zip'
        Invoke-WebRequest -Uri $Asset.browser_download_url -OutFile $Zip -UseBasicParsing
        if ((Get-FileHash -LiteralPath $Zip -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Asset.digest.Substring(7)) { throw 'Descarga dañada.' }
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $Archive = [IO.Compression.ZipFile]::OpenRead($Zip)
        try {
            foreach ($Entry in $Archive.Entries) {
                if ($Entry.FullName -match '(^[/\\]|(^|[/\\])\.\.([/\\]|$))') { throw 'Ruta ZIP no válida.' }
            }
        } finally { $Archive.Dispose() }
        $Extracted = Join-Path $Work 'parche'
        Expand-Archive -LiteralPath $Zip -DestinationPath $Extracted
        $Package = Join-Path $Extracted 'PvZ-Fusion-ES'
        $Manifest = Get-Content -LiteralPath (Join-Path $Package 'manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($Manifest.version -ne $Release.tag_name) { throw 'El ZIP no coincide con la release.' }
        & (Join-Path $Package 'Instalar_Windows.ps1') -GameDir $GameDir
        if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw 'La instalación no terminó correctamente.' }
    } finally { Remove-Item -LiteralPath $Work -Recurse -Force -ErrorAction SilentlyContinue }
} catch {
    Write-Host "Actualización aplazada: $_. Se conserva la instalación actual."
}
