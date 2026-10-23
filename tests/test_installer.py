"""Regresiones de conservación de ajustes, partidas e integridad del paquete."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "pvz_es", ROOT / "pvz_fusion_es.py"
)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallerTests(unittest.TestCase):
    @patch.object(
        installer,
        "BASE_GAME_FILES",
        {
            name: hashlib.sha256(b"").hexdigest()
            for name in ["PlantsVsZombiesRH.exe", "GameAssembly.dll"]
        },
    )
    def test_install_preserves_settings_and_saves(self):
        with tempfile.TemporaryDirectory(
            dir=os.environ["PVZ_TEST_TEMP"]
        ) as temporary:
            game = Path(temporary) / "Game Files"
            for name in [
                "PlantsVsZombiesRH.exe",
                "GameAssembly.dll",
                "version.dll",
                "Mods/PvZ_Fusion_Translator.dll",
            ]:
                target = game / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.touch()
            data = game / "UserData"
            data.mkdir()
            (data / "MelonPreferences.cfg").write_text(
                '[BloomsQOL]\nShowPlantHP = 2\n\n[PvZ_Fusion_Translator]\nLanguage = "English"\nUseLocal = false\nCustomPreference = 42\n'
            )
            (data / "partida.json").write_text('{"nivel": 25}')
            installer.install(game, configure_wrapper=False)
            content = (data / "MelonPreferences.cfg").read_text()
            self.assertIn("ShowPlantHP = 2", content)
            self.assertIn("CustomPreference = 42", content)
            self.assertIn('Language = "Spanish"', content)
            self.assertIn("UseLocal = true", content)
            self.assertEqual(
                (data / "partida.json").read_text(), '{"nivel": 25}'
            )
            self.assertTrue(
                (
                    game
                    / "Mods/PvZ_Fusion_Translator/Localization/Spanish/Strings/translation_strings.json"
                ).is_file()
            )
            # Reinstalar no duplica claves ni cambia las opciones del jugador.
            installer.install(game, configure_wrapper=False)
            self.assertEqual(
                (data / "MelonPreferences.cfg")
                .read_text()
                .count("Language ="),
                1,
            )

    def test_corrupt_package_is_rejected_before_installing(self):
        with tempfile.TemporaryDirectory(
            dir=os.environ["PVZ_TEST_TEMP"]
        ) as temporary:
            root = Path(temporary)
            (root / "paquete").mkdir()
            (root / "paquete/text.json").write_text("modificado")
            (root / "manifest.json").write_text(
                json.dumps({"files": {"text.json": "0" * 64}})
            )
            with patch.object(installer, "ROOT", root), self.assertRaises(
                RuntimeError
            ):
                installer.verify_package()

    def test_incompatible_game_is_rejected(self):
        with tempfile.TemporaryDirectory(
            dir=os.environ["PVZ_TEST_TEMP"]
        ) as temporary:
            game = Path(temporary)
            for name in [
                "PlantsVsZombiesRH.exe",
                "GameAssembly.dll",
                "version.dll",
                "Mods/PvZ_Fusion_Translator.dll",
            ]:
                path = game / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
            with self.assertRaisesRegex(RuntimeError, "base no corresponde"):
                installer.check_game(game)
            self.assertFalse((game / "UserData").exists())

    def test_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory(
            dir=os.environ["PVZ_TEST_TEMP"]
        ) as temporary:
            root = Path(temporary)
            (root / "paquete").mkdir()
            (root / "outside").write_text("privado")
            (root / "manifest.json").write_text(
                json.dumps({"files": {"../outside": "0" * 64}})
            )
            with patch.object(installer, "ROOT", root), self.assertRaises(
                RuntimeError
            ):
                installer.verify_package()


if __name__ == "__main__":
    unittest.main()
