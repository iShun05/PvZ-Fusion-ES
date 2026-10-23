#!/usr/bin/env python3
"""Compatibilidad con el acceso antiguo: iniciar y actualizar solo combinaciones compatibles."""

import sys
from pvz_fusion_es import main

if __name__ == "__main__":
    if len(sys.argv) == 2:
        actions = {
            "--launch": "jugar",
            "--check": "diagnostico",
            "--update": "actualizar",
        }
        sys.argv[1] = actions.get(sys.argv[1], sys.argv[1])
    raise SystemExit(main())
