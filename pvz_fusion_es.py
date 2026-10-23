#!/usr/bin/env python3
"""Instalación, arranque y actualizaciones compatibles de PvZ Fusion ES."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import shlex
import subprocess
import sys
import webbrowser

ROOT = Path(__file__).resolve().parent
VERSION = "v0.1"
SUPPORT = "https://www.instagram.com/_shun._05/"
BASE_GAME_FILES = {
    "GameAssembly.dll": "48096b917ee6aaf6e35c95c98e666a4399a9e0c3d5adbab727cee941eccf2d42",
    "PlantsVsZombiesRH.exe": "d38afabdc98f8d910dba495fc8eb0868965aa0251a96db190ffba3773704f5b1",
}
WRAPPER = Path("/Applications/Sikarugir/PvZ Fusion.app")
GAME = (
    WRAPPER
    / "Contents/SharedSupport/prefix/drive_c/Games/PvZ_Fusion/Game Files"
)


def read_json(path: Path) -> dict:
    """Lee JSON UTF-8 con o sin marca BOM."""
    return json.loads(path.read_text(encoding="utf-8-sig"))


def set_preference(text: str, section: str, key: str, value: str) -> str:
    """Cambia una preferencia sin borrar ajustes ajenos."""
    pattern = re.compile(
        r"(?ms)^\[" + re.escape(section) + r"\][ \t]*\n(.*?)(?=^\[|\Z)"
    )
    match = pattern.search(text)
    line = f"{key} = {value}\n"
    if not match:
        return text.rstrip() + f"\n\n[{section}]\n" + line
    body = match.group(1)
    key_pattern = re.compile(r"(?m)^" + re.escape(key) + r"[ \t]*=.*(?:\n|$)")
    body = (
        key_pattern.sub(lambda _: line, body)
        if key_pattern.search(body)
        else body.rstrip() + "\n" + line
    )
    return text[: match.start(1)] + body + text[match.end(1) :]


def check_game(game: Path) -> None:
    """Evita instalar en una carpeta equivocada o sin el mod base."""
    required = [
        "PlantsVsZombiesRH.exe",
        "version.dll",
        "Mods/PvZ_Fusion_Translator.dll",
    ]
    for name in required:
        if not (game / name).is_file():
            raise RuntimeError(
                f"Falta {name} en {game}. Instala primero PvZ Fusion Multi-lang 4.0.5.2."
            )
    for name, expected in BASE_GAME_FILES.items():
        path = game / name
        if (
            not path.is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest() != expected
        ):
            raise RuntimeError(
                "La base no corresponde a Multi-lang 4.0.5.2. No se ha instalado el parche."
            )
    if sys.platform == "darwin" and game.resolve() == GAME.resolve():
        processes = subprocess.check_output(
            ["ps", "-axo", "command"], text=True
        )
        if any(
            line.startswith(
                "C:\\Games\\PvZ_Fusion\\Game Files\\PlantsVsZombiesRH.exe"
            )
            for line in processes.splitlines()
        ):
            raise RuntimeError(
                "Cierra PvZ Fusion desde su menú antes de instalar o reparar. Tus partidas se conservan."
            )


def verify_package() -> dict:
    """Verifica todos los archivos antes de modificar la instalación."""
    manifest = read_json(ROOT / "manifest.json")
    package = ROOT / "paquete"
    for relative, expected in manifest["files"].items():
        path = package / relative
        if (
            path.is_symlink()
            or not path.is_file()
            or package.resolve() not in path.resolve().parents
        ):
            raise RuntimeError(f"Archivo de paquete inválido: {relative}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(
                f"El paquete está incompleto o modificado: {relative}"
            )
    return manifest


def install(game: Path, configure_wrapper: bool = True) -> None:
    """Copia solo la localización y modifica las preferencias necesarias."""
    check_game(game)
    manifest = verify_package()
    destination = game / "Mods/PvZ_Fusion_Translator"
    for relative in manifest["files"]:
        source = ROOT / "paquete" / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + ".pvzes-tmp")
        shutil.copyfile(source, temporary)
        os.replace(temporary, target)
    preferences = game / "UserData/MelonPreferences.cfg"
    preferences.parent.mkdir(parents=True, exist_ok=True)
    text = (
        preferences.read_text(encoding="utf-8-sig")
        if preferences.exists()
        else ""
    )
    for key, value in {
        "Language": '"Spanish"',
        "UseLocal": "true",
        "DefaultTextures": "false",
    }.items():
        text = set_preference(text, "PvZ_Fusion_Translator", key, value)
    preferences.write_text(text, encoding="utf-8")
    loader = game / "UserData/Loader.cfg"
    text = loader.read_text(encoding="utf-8-sig") if loader.exists() else ""
    text = set_preference(text, "console", "hide_console", "true")
    text = set_preference(text, "loader", "disable_start_screen", "true")
    loader.write_text(text, encoding="utf-8")
    (game / "UserData/PvZ-Fusion-ES.json").write_text(
        json.dumps(
            {
                "version": VERSION,
                "game_version": manifest["game_version"],
                "contact": SUPPORT,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    if (
        configure_wrapper
        and sys.platform == "darwin"
        and game.resolve() == GAME.resolve()
    ):
        repair_wrapper()
        install_command()
    print(
        f"PvZ Fusion ES {VERSION}: traducción instalada. Las partidas y los demás ajustes se conservan."
    )
    print(f"Contacto: {SUPPORT}")


def repair_wrapper() -> None:
    """Usa exclusivamente el motor y los renderizadores de la botella instalada."""
    contents = WRAPPER / "Contents"
    prefix = contents / "SharedSupport/prefix"
    for architecture, system in [
        ("x86_64-windows", "system32"),
        ("i386-windows", "syswow64"),
    ]:
        for name in [
            "d3d10core.dll",
            "d3d11.dll",
            "dxgi.dll",
            "winemetal.dll",
        ]:
            source = (
                contents
                / "SharedSupport/renderer/dxmt/wine"
                / architecture
                / name
            )
            if not source.is_file():
                raise RuntimeError(
                    f"El envoltorio no incluye el renderizador necesario: {source.name}"
                )
            shutil.copy2(source, prefix / "drive_c/windows" / system / name)
    registry = prefix / "user.reg"
    text = registry.read_text(encoding="utf-8")
    # Eliminar únicamente el bloqueo D3D12 del juego y del ámbito global.
    sections = [
        r"Software\\Wine\\DllOverrides",
        r"Software\\Wine\\AppDefaults\\PlantsVsZombiesRH.exe\\DllOverrides",
    ]
    for section in sections:
        pattern = re.compile(
            r"(?ms)^\[" + re.escape(section) + r"\][^\n]*\n(.*?)(?=^\[|\Z)"
        )
        match = pattern.search(text)
        if match:
            body = re.sub(r'(?m)^"d3d12"=""\n?', "", match.group(1))
            body = (
                re.sub(r'(?m)^"version"=.*\n?', "", body).rstrip()
                + '\n"version"="native,builtin"\n\n'
            )
            text = text[: match.start(1)] + body + text[match.end(1) :]
    registry.write_text(text, encoding="utf-8")
    info = contents / "Info.plist"
    data = plistlib.loads(info.read_bytes())
    flags = data.get("Program Flags", "")
    if "--melonloader.hideconsole" not in flags:
        data["Program Flags"] = (flags + " --melonloader.hideconsole").strip()
    data["WINEDEBUG"] = "-all"
    info.write_bytes(plistlib.dumps(data))
    startup = contents / "Resources/Scripts/StartupScript"
    text = startup.read_text(encoding="utf-8")
    text = re.sub(
        r"(?ms)\n# PvZ Fusion ES: inicio actualización.*?# Fin PvZ Fusion ES\n?",
        "\n",
        text,
    )
    command = shlex.quote(str(ROOT / "pvz_fusion_es.py"))
    log_directory = Path.home() / "Documents/Entorno_Temporal/PvZ-Fusion-ES"
    log_directory.mkdir(parents=True, exist_ok=True)
    log = shlex.quote(str(log_directory / "actualizacion.log"))
    text = (
        text.rstrip()
        + f"\n\n# PvZ Fusion ES: inicio actualización\n/usr/bin/python3 {command} actualizar >> {log} 2>&1\n# Fin PvZ Fusion ES\n"
    )
    startup.write_text(text, encoding="utf-8")


def install_command() -> None:
    """Instala un único acceso al código canónico y lo añade al PATH si falta."""
    directory = Path.home() / ".local/bin"
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / "pvz-fusion"
    source = ROOT / "pvz-fusion"
    if target.is_symlink():
        target.unlink()
    elif target.exists():
        raise RuntimeError(
            "Ya existe un archivo pvz-fusion que no es un enlace; no se ha sobrescrito."
        )
    target.symlink_to(source)
    rc = Path.home() / ".zshrc"
    text = rc.read_text(encoding="utf-8") if rc.exists() else ""
    if ".local/bin" not in text:
        rc.write_text(
            text.rstrip() + '\nexport PATH="$HOME/.local/bin:$PATH"\n',
            encoding="utf-8",
        )


def launch() -> None:
    """Arranca el envoltorio; su inicio comprueba actualizaciones compatibles."""
    if sys.platform != "darwin":
        raise RuntimeError(
            "En Windows usa Jugar_Windows.bat en la carpeta del juego."
        )
    if not (GAME / "PlantsVsZombiesRH.exe").exists():
        raise RuntimeError("No se encuentra PvZ Fusion en Sikarugir.")
    installed = GAME / "UserData/PvZ-Fusion-ES.json"
    if not installed.exists():
        raise RuntimeError(
            "Instala primero el parche con Instalar_macOS.command."
        )
    print(f"Abriendo PvZ Fusion ES {VERSION}…")
    subprocess.run(["open", str(WRAPPER)], check=True)


def diagnostic() -> None:
    """Expone rutas y versiones, sin credenciales ni datos de partidas."""
    manifest = verify_package()
    print(f"PvZ Fusion ES {VERSION} | Base: {manifest['game_version']}")
    print(f"Paquete: {len(manifest['files'])} archivos verificados")
    print(
        f"Envoltorio: {'encontrado' if WRAPPER.exists() else 'no instalado'}"
    )
    if WRAPPER.exists():
        data = plistlib.loads((WRAPPER / "Contents/Info.plist").read_bytes())
        print(f"Opciones de arranque: {data.get('Program Flags', '')}")
    print(f"Contacto: {SUPPORT}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=f"PvZ Fusion ES {VERSION} — traducción e inicio manual"
    )
    parser.add_argument(
        "action",
        nargs="?",
        choices=["jugar", "instalar", "actualizar", "diagnostico", "contacto"],
        default="jugar",
    )
    parser.add_argument(
        "--game-dir",
        type=Path,
        default=GAME,
        help="Carpeta Game Files de una instalación Multi-lang",
    )
    parser.add_argument(
        "--version", action="version", version=f"PvZ Fusion ES {VERSION}"
    )
    args = parser.parse_args()
    try:
        if args.action == "instalar":
            install(args.game_dir.expanduser().resolve())
        elif args.action == "diagnostico":
            diagnostic()
        elif args.action == "actualizar":
            from actualizaciones import update

            try:
                update(ROOT, args.game_dir.expanduser().resolve(), VERSION)
            except Exception as error:
                # Una caída de red no impide jugar con la instalación anterior.
                print(f"Actualización aplazada: {error}")
                return 0
        elif args.action == "contacto":
            if not webbrowser.open(SUPPORT):
                raise RuntimeError("No se pudo abrir el enlace de contacto.")
        else:
            launch()
        return 0
    except (
        OSError,
        ValueError,
        RuntimeError,
        subprocess.SubprocessError,
    ) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
