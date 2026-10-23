#!/usr/bin/env python3
"""Genera el inventario reproducible de la distribución del parche."""

from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
package = root / "paquete"
files = {
    str(path.relative_to(package)): hashlib.sha256(
        path.read_bytes()
    ).hexdigest()
    for path in sorted(package.rglob("*"))
    if path.is_file() and not path.name.startswith(".")
}
(root / "manifest.json").write_text(
    json.dumps(
        {
            "version": "v0.1",
            "game_version": "4.0.5.2 Multi-lang Alpha",
            "files": files,
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
print(f"Manifiesto: {len(files)} archivos")
