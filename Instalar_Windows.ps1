param([string]$GameDir)
$ErrorActionPreference = 'Stop'
# Instala el español y su base compatible conservando los datos del jugador.
try {
    $Root = $PSScriptRoot
    if (-not $GameDir) {
        Add-Type -AssemblyName System.Windows.Forms
        $Dialog = New-Object System.Windows.Forms.FolderBrowserDialog
        $Dialog.Description = 'Selecciona Game Files de PvZ Fusion Multi-lang 4.0.5.2'
        if ($Dialog.ShowDialog() -ne 'OK') { exit 1 }
        $GameDir = $Dialog.SelectedPath
    }
    $GameDir = [IO.Path]::GetFullPath($GameDir).TrimEnd([IO.Path]::DirectorySeparatorChar)
    foreach ($Name in @('PlantsVsZombiesRH.exe', 'version.dll', 'Mods\PvZ_Fusion_Translator.dll')) {
        if (-not (Test-Path -LiteralPath (Join-Path $GameDir $Name) -PathType Leaf)) {
            throw "Falta $Name. Selecciona la carpeta Game Files de PvZ Fusion Multi-lang 4.0.5.2."
        }
    }
    if (Get-Process -Name PlantsVsZombiesRH -ErrorAction SilentlyContinue) {
        throw 'Cierra PvZ Fusion desde su menú antes de instalar.'
    }
    $Manifest = Get-Content -LiteralPath (Join-Path $Root 'manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    $Package = [System.IO.Path]::GetFullPath((Join-Path $Root 'paquete')) + [System.IO.Path]::DirectorySeparatorChar
    foreach ($Entry in $Manifest.files.PSObject.Properties) {
        $Source = [System.IO.Path]::GetFullPath((Join-Path $Package $Entry.Name))
        if (-not $Source.StartsWith($Package, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw 'El paquete contiene una ruta no válida.'
        }
        if ((Get-FileHash -LiteralPath $Source -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Entry.Value) {
            throw "Archivo incompleto o modificado: $($Entry.Name)"
        }
    }
    $UpdateConfig = Get-Content -LiteralPath (Join-Path $Root 'actualizacion.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    $Compatible = $true
    foreach ($Entry in $UpdateConfig.base_files.PSObject.Properties) {
        $BaseFile = Join-Path $GameDir $Entry.Name
        if (-not (Test-Path -LiteralPath $BaseFile -PathType Leaf) -or (Get-FileHash -LiteralPath $BaseFile -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Entry.Value) { $Compatible = $false }
    }
    if (-not $Compatible) {
        if ($UpdateConfig.base_repository -ne 'Teyliu/PVZF-Translation') { throw 'Repositorio base no autorizado.' }
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $Release = Invoke-RestMethod -Uri ('https://api.github.com/repos/Teyliu/PVZF-Translation/releases/tags/' + $UpdateConfig.base_tag) -Headers @{ 'User-Agent'='PvZ-Fusion-ES' }
        $Asset = $Release.assets | Where-Object name -eq $UpdateConfig.base_asset | Select-Object -First 1
        if (-not $Asset -or $Asset.browser_download_url -notlike 'https://github.com/Teyliu/PVZF-Translation/releases/download/*') { throw 'Descarga base no autorizada.' }
        $Work = Join-Path $env:TEMP ('PvZ-Fusion-ES-base-' + [guid]::NewGuid().ToString('N'))
        [IO.Directory]::CreateDirectory($Work) | Out-Null
        try {
            $Zip = Join-Path $Work 'juego.zip'
            Write-Host 'Descargando la base compatible. Se conservarán tus datos.'
            Invoke-WebRequest -Uri $Asset.browser_download_url -OutFile $Zip -UseBasicParsing
            if ((Get-FileHash -LiteralPath $Zip -Algorithm SHA256).Hash.ToLowerInvariant() -ne $UpdateConfig.base_sha256) { throw 'La base descargada no coincide con su SHA-256.' }
            Add-Type -AssemblyName System.IO.Compression.FileSystem
            $Archive = [IO.Compression.ZipFile]::OpenRead($Zip)
            try {
                foreach ($Entry in $Archive.Entries) {
                    if ($Entry.FullName -match '(^[/\\]|(^|[/\\])\.\.([/\\]|$))') { throw 'Ruta ZIP no válida.' }
                }
            } finally { $Archive.Dispose() }
            Expand-Archive -LiteralPath $Zip -DestinationPath (Join-Path $Work 'base')
            $Candidate = Join-Path $Work 'base\Game Files'
            foreach ($Entry in $UpdateConfig.base_files.PSObject.Properties) {
                if ((Get-FileHash -LiteralPath (Join-Path $Candidate $Entry.Name) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Entry.Value) { throw 'Binario base incompatible.' }
            }
            foreach ($Source in Get-ChildItem -LiteralPath $GameDir -Recurse -File) {
                $Relative = $Source.FullName.Substring($GameDir.TrimEnd('\').Length + 1)
                $Target = Join-Path $Candidate $Relative
                if ($Relative -like 'UserData\*' -or -not (Test-Path -LiteralPath $Target)) {
                    [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($Target)) | Out-Null
                    Copy-Item -LiteralPath $Source.FullName -Destination $Target -Force
                }
            }
            $Previous = Join-Path (Split-Path -Parent $GameDir) '.PvZ-Fusion-ES-transaccion'
            if (Test-Path -LiteralPath $Previous) { throw 'Hay una transacción anterior pendiente.' }
            Move-Item -LiteralPath $GameDir -Destination $Previous
            try { Move-Item -LiteralPath $Candidate -Destination $GameDir }
            catch { Move-Item -LiteralPath $Previous -Destination $GameDir; throw }
            Remove-Item -LiteralPath $Previous -Recurse -Force
        } finally { Remove-Item -LiteralPath $Work -Recurse -Force -ErrorAction SilentlyContinue }
    }
    foreach ($Entry in $Manifest.files.PSObject.Properties) {
        $Destination = Join-Path (Join-Path $GameDir 'Mods\PvZ_Fusion_Translator') $Entry.Name
        [System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($Destination)) | Out-Null
        Copy-Item -LiteralPath (Join-Path $Package $Entry.Name) -Destination $Destination -Force
    }
    function Set-Preference([string]$Text, [string]$Section, [string]$Key, [string]$Value) {
        $Pattern = '(?ms)^\[' + [regex]::Escape($Section) + '\][ \t]*\r?\n(.*?)(?=^\[|\z)'
        $Match = [regex]::Match($Text, $Pattern)
        $Line = "$Key = $Value`r`n"
        if (-not $Match.Success) { return $Text.TrimEnd() + "`r`n`r`n[$Section]`r`n" + $Line }
        $Body = $Match.Groups[1].Value
        $KeyPattern = '(?m)^' + [regex]::Escape($Key) + '[ \t]*=.*(?:\r?\n|$)'
        if ([regex]::IsMatch($Body, $KeyPattern)) {
            $Body = [regex]::Replace($Body, $KeyPattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $Line })
        } else { $Body = $Body.TrimEnd() + "`r`n" + $Line }
        return $Text.Substring(0, $Match.Groups[1].Index) + $Body + $Text.Substring($Match.Groups[1].Index + $Match.Groups[1].Length)
    }
    $Utf8 = New-Object System.Text.UTF8Encoding($false)
    $UserData = Join-Path $GameDir 'UserData'
    [System.IO.Directory]::CreateDirectory($UserData) | Out-Null
    $Preferences = Join-Path $UserData 'MelonPreferences.cfg'
    $Text = if (Test-Path -LiteralPath $Preferences) { [System.IO.File]::ReadAllText($Preferences) } else { '' }
    foreach ($Entry in @{ Language='"Spanish"'; UseLocal='true'; DefaultTextures='false' }.GetEnumerator()) {
        $Text = Set-Preference $Text 'PvZ_Fusion_Translator' $Entry.Key $Entry.Value
    }
    [System.IO.File]::WriteAllText($Preferences, $Text, $Utf8)
    $Loader = Join-Path $UserData 'Loader.cfg'
    $Text = if (Test-Path -LiteralPath $Loader) { [System.IO.File]::ReadAllText($Loader) } else { '' }
    $Text = Set-Preference $Text 'console' 'hide_console' 'true'
    [System.IO.File]::WriteAllText($Loader, $Text, $Utf8)
    $Info = @{ version='v0.1'; game_version=$Manifest.game_version; contact='https://www.instagram.com/_shun._05/' } | ConvertTo-Json
    [System.IO.File]::WriteAllText((Join-Path $UserData 'PvZ-Fusion-ES.json'), $Info, $Utf8)
    Copy-Item -LiteralPath (Join-Path $Root 'Jugar_Windows.bat') -Destination (Join-Path $GameDir 'Jugar_Windows.bat') -Force
    Copy-Item -LiteralPath (Join-Path $Root 'Actualizar_Windows.ps1') -Destination (Join-Path $GameDir 'Actualizar_Windows.ps1') -Force
    Write-Host 'PvZ Fusion ES v0.1 instalado. Abre Jugar_Windows.bat en Game Files.' -ForegroundColor Green
    Write-Host 'Tus partidas y los demás ajustes se conservan.'
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}
