"""Actualización automática al abrir: parche español y su base compatible."""

from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import tempfile
import urllib.error
import urllib.request
import zipfile

REPOSITORY = "iShun05/PvZ-Fusion-ES"
BASE_REPOSITORY = "Teyliu/PVZF-Translation"


def release(repository: str, suffix: str = "latest") -> dict:
    """Consulta solo los dos repositorios de distribución autorizados."""
    if repository not in {REPOSITORY, BASE_REPOSITORY}:
        raise RuntimeError("Repositorio de actualización no autorizado.")
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}/releases/{suffix}",
        headers={
            "User-Agent": "PvZ-Fusion-ES",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.load(response)


def version_number(value: str) -> tuple:
    """Compara únicamente versiones numéricas publicadas del parche."""
    if not re.fullmatch(r"v\d+\.\d+", value):
        raise RuntimeError(
            "La versión publicada tiene un formato no admitido."
        )
    return tuple(int(part) for part in value[1:].split("."))


def download(
    asset: dict, target: Path, repository: str, expected: str = ""
) -> None:
    """Comprueba origen y SHA-256 antes de abrir un archivo descargado."""
    url = asset["browser_download_url"]
    if not url.startswith(
        f"https://github.com/{repository}/releases/download/"
    ):
        raise RuntimeError(
            "La descarga no pertenece al repositorio autorizado."
        )
    digest = expected or asset.get("digest", "").removeprefix("sha256:")
    if not re.fullmatch(r"[a-f0-9]{64}", digest):
        raise RuntimeError("La descarga no ofrece un SHA-256 verificable.")
    request = urllib.request.Request(
        url, headers={"User-Agent": "PvZ-Fusion-ES"}
    )
    hasher = hashlib.sha256()
    with urllib.request.urlopen(request, timeout=60) as response, target.open(
        "wb"
    ) as output:
        while chunk := response.read(1024 * 1024):
            hasher.update(chunk)
            output.write(chunk)
    if hasher.hexdigest() != digest:
        raise RuntimeError("La descarga no coincide con su SHA-256.")


def extract(source: Path, destination: Path) -> None:
    """Extrae sin rutas externas, enlaces ni expansión desmesurada."""
    with zipfile.ZipFile(source) as archive:
        if sum(item.file_size for item in archive.infolist()) > 12 * 1024**3:
            raise RuntimeError(
                "El ZIP supera el tamaño de instalación admitido."
            )
        for item in archive.infolist():
            path = PurePosixPath(item.filename)
            mode = item.external_attr >> 16
            if (
                path.is_absolute()
                or ".." in path.parts
                or "\\" in item.filename
                or stat.S_ISLNK(mode)
            ):
                raise RuntimeError(
                    "El ZIP contiene una ruta o enlace no permitido."
                )
            target = destination.joinpath(*path.parts)
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(item) as input_file, target.open(
                    "wb"
                ) as output:
                    shutil.copyfileobj(input_file, output)
                if mode & 0o111:
                    target.chmod(0o755)


def matches_base(game: Path, config: dict) -> bool:
    """Compara la base con los binarios declarados por el parche español."""
    return all(
        (game / name).is_file()
        and hashlib.sha256((game / name).read_bytes()).hexdigest() == digest
        for name, digest in config["base_files"].items()
    )


def preserve_player_files(game: Path, candidate: Path) -> None:
    """La base nueva aporta sus librerías; los datos del jugador prevalecen."""
    for source in game.rglob("*"):
        if not source.is_file():
            continue
        relative = source.relative_to(game)
        target = candidate / relative
        # UserData contiene ajustes, mods auxiliares y posibles partidas.
        # Los archivos adicionales del jugador también se conservan.
        if relative.parts[0] == "UserData" or not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def update(root: Path, game: Path, current_version: str) -> bool:
    """Actualiza solo con el juego cerrado y una combinación publicada compatible."""
    processes = subprocess.check_output(["ps", "-axo", "command"], text=True)
    if any(
        line.startswith(
            "C:\\Games\\PvZ_Fusion\\Game Files\\PlantsVsZombiesRH.exe"
        )
        for line in processes.splitlines()
    ):
        print("Actualización aplazada: el juego sigue abierto.")
        return False
    latest = release(REPOSITORY)
    if version_number(latest["tag_name"]) <= version_number(current_version):
        print("PvZ Fusion ES está actualizado.")
        return False
    if (root / ".git").exists():
        dirty = subprocess.check_output(
            ["git", "-C", str(root), "status", "--porcelain"], text=True
        )
        if dirty.strip():
            raise RuntimeError(
                "Hay cambios locales en el proyecto; se conservan y se aplaza la actualización."
            )
    asset = next(
        (
            item
            for item in latest["assets"]
            if item["name"] == "PvZ-Fusion-ES.zip"
        ),
        None,
    )
    if not asset:
        raise RuntimeError(
            "La versión nueva aún no tiene un paquete listo para instalar."
        )
    temporary_root = Path.home() / "Documents/Entorno_Temporal/PvZ-Fusion-ES"
    temporary_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="actualizacion-", dir=temporary_root
    ) as temporary:
        work = Path(temporary)
        download(asset, work / "parche.zip", REPOSITORY)
        extract(work / "parche.zip", work / "parche")
        package = work / "parche/PvZ-Fusion-ES"
        config = json.loads((package / "actualizacion.json").read_text())
        if config["base_repository"] != BASE_REPOSITORY:
            raise RuntimeError(
                "La base propuesta no procede del proyecto autorizado."
            )
        spec = importlib.util.spec_from_file_location(
            "pvz_es_nuevo", package / "pvz_fusion_es.py"
        )
        installer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(installer)
        if installer.VERSION != latest["tag_name"]:
            raise RuntimeError(
                "La versión del ZIP no coincide con la release."
            )
        installer.verify_package()
        if not matches_base(game, config):
            base_release = release(
                BASE_REPOSITORY, "tags/" + config["base_tag"]
            )
            base_asset = next(
                item
                for item in base_release["assets"]
                if item["name"] == config["base_asset"]
            )
            print(
                "Descargando la nueva base compatible y conservando los datos del jugador…"
            )
            download(
                base_asset,
                work / "juego.zip",
                BASE_REPOSITORY,
                config["base_sha256"],
            )
            extract(work / "juego.zip", work / "base")
            candidate = work / "base/Game Files"
            if not matches_base(candidate, config):
                raise RuntimeError(
                    "La base descargada no coincide con el parche."
                )
            preserve_player_files(game, candidate)
            installer.install(candidate, configure_wrapper=False)
            previous = game.with_name(".PvZ-Fusion-ES-transaccion")
            if previous.exists():
                raise RuntimeError(
                    "Existe una transacción anterior sin resolver; no se sobrescribe."
                )
            game.rename(previous)
            try:
                shutil.move(str(candidate), str(game))
            except BaseException:
                previous.rename(game)
                raise
            shutil.rmtree(previous)
        else:
            installer.install(game, configure_wrapper=False)
        # Un checkout canónico avanza al tag de la release; nunca se sobrescribe con otra copia.
        if (root / ".git").exists():
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(root),
                    "fetch",
                    "origin",
                    "tag",
                    latest["tag_name"],
                ],
                check=True,
            )
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(root),
                    "merge",
                    "--ff-only",
                    latest["tag_name"],
                ],
                check=True,
            )
        else:
            for source in package.rglob("*"):
                if source.is_file():
                    target = root / source.relative_to(package)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)
        # Reparar la botella desde la ruta permanente, no desde el directorio temporal.
        subprocess.run(
            [
                "/usr/bin/python3",
                str(root / "pvz_fusion_es.py"),
                "instalar",
                "--game-dir",
                str(game),
            ],
            check=True,
        )
    print(f"Actualizado a {latest['tag_name']} con su base compatible.")
    return True
