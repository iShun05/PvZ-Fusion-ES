#!/usr/bin/env python3
"""Audita valores visibles, manifiesto y cobertura frente al juego instalado."""

from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys
import struct

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pvz_fusion_es import verify_package


def leaves(value, path=()):
    """Identifica cada texto por su clave o ID estable de planta/zombi."""
    if isinstance(value, dict):
        for key, child in value.items():
            yield from leaves(child, path + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            identifier = str(index)
            if isinstance(child, dict):
                for key in ("seedType", "theZombieType"):
                    if key in child:
                        identifier = "id:" + str(child[key])
                        break
            yield from leaves(child, path + (identifier,))
    elif isinstance(value, str):
        yield path, value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--game-dir",
        type=Path,
        help="Game Files para comparar con inglés y volcados reales",
    )
    args = parser.parse_args()
    manifest = verify_package()
    root = ROOT / "paquete/Localization/Spanish"
    errors = []
    dimensions = json.loads((ROOT / "assets/texturas.json").read_text())[
        "dimensiones"
    ]
    for relative, expected in dimensions.items():
        path = root / relative
        header = path.read_bytes()[:24]
        actual = list(struct.unpack(">II", header[16:24]))
        if header[:8] != b"\x89PNG\r\n\x1a\n" or actual != expected:
            errors.append(f"Dimensiones PNG incorrectas: {relative}")
    for file in root.rglob("*.txt"):
        if re.search(r"[\u4e00-\u9fff]", file.read_text(encoding="utf-8-sig")):
            errors.append(f"Texto chino visible: {file.name}")
    counts = {}
    for file in root.rglob("*.json"):
        data = json.loads(file.read_text(encoding="utf-8-sig"))
        relative = str(file.relative_to(root))
        if relative.startswith("Textures/"):
            continue
        texts = dict(leaves(data))
        counts[relative] = len(texts)
        for path, text in texts.items():
            if re.search(r"ZXQ\d+QXZ", text):
                errors.append(f"Marcador residual: {relative} {path}")
            if re.search(r"[\u4e00-\u9fff]", text):
                errors.append(f"Texto chino visible: {relative} {path}")
        if isinstance(data, dict):
            for key, idkey in [
                ("plants", "seedType"),
                ("zombies", "theZombieType"),
            ]:
                if key in data:
                    ids = [entry[idkey] for entry in data[key]]
                    if len(ids) != len(set(ids)):
                        errors.append(f"IDs duplicados en {relative}")
    if args.game_dir:
        translator = args.game_dir / "Mods/PvZ_Fusion_Translator"
        references = []
        for file in (translator / "Localization/English").rglob("*.json"):
            relative = str(
                file.relative_to(translator / "Localization/English")
            )
            if relative.startswith("Textures/"):
                continue
            try:
                source = json.loads(file.read_text(encoding="utf-8-sig"))
            except json.JSONDecodeError:
                # Algunos archivos históricos del upstream no son JSON válido ni se cargan.
                continue
            references.append((relative, source))
        dumps = {
            "LawnStrings.json": "Almanac/LawnStringsTranslate.json",
            "ZombieStrings.json": "Almanac/ZombieStringsTranslate.json",
            "DetailStrings.json": "Almanac/DetailStringsTranslate.json",
            "UntranslatedStrings.json": "Strings/translation_strings.json",
            "travel_buffs.json": "Strings/travel_buffs.json",
            "tips_fs.json": "Strings/tips_fs.json",
            "tips_iz.json": "Strings/tips_iz.json",
        }
        for name, relative in dumps.items():
            file = translator / "Dumps" / name
            if file.is_file():
                references.append(
                    (
                        relative,
                        json.loads(file.read_text(encoding="utf-8-sig")),
                    )
                )
        for relative, source in references:
            destination = root / relative
            if not destination.exists():
                errors.append(f"Archivo ausente: {relative}")
                continue
            translated = dict(
                leaves(json.loads(destination.read_text(encoding="utf-8-sig")))
            )
            for path, text in leaves(source):
                if path not in translated:
                    errors.append(f"Entrada ausente: {relative} {path}")
                elif text.strip() and not translated[path].strip():
                    errors.append(f"Traducción vacía: {relative} {path}")
    print(
        json.dumps(
            {
                "version": manifest["version"],
                "strings": counts,
                "total_strings": sum(counts.values()),
                "errors": errors,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
