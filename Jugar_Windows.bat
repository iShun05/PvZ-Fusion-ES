@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist "PlantsVsZombiesRH.exe" (
    echo Ejecuta este archivo desde Game Files. Instalar_Windows.bat lo copia a esa carpeta.
    pause
    exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Actualizar_Windows.ps1" -GameDir "%~dp0."
start "PvZ Fusion ES v0.1" "PlantsVsZombiesRH.exe" --melonloader.hideconsole
