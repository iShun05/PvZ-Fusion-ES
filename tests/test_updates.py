"""Pruebas de actualización compatible sin red ni partidas reales."""

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import actualizaciones as updater


class UpdateTests(unittest.TestCase):
    def test_extract_rejects_external_path(self):
        with tempfile.TemporaryDirectory(
            dir=os.environ["PVZ_TEST_TEMP"]
        ) as temporary:
            root = Path(temporary)
            with zipfile.ZipFile(root / "bad.zip", "w") as archive:
                archive.writestr("../outside", "no")
            with self.assertRaises(RuntimeError):
                updater.extract(root / "bad.zip", root / "out")
            self.assertFalse((root / "outside").exists())

    def test_player_data_wins_over_base_defaults(self):
        with tempfile.TemporaryDirectory(
            dir=os.environ["PVZ_TEST_TEMP"]
        ) as temporary:
            root = Path(temporary)
            game, candidate = root / "old", root / "new"
            for folder in [game, candidate]:
                (folder / "UserData").mkdir(parents=True)
            (game / "UserData/partida.json").write_text("partida real")
            (candidate / "UserData/partida.json").write_text("predeterminado")
            (game / "GameAssembly.dll").write_text("antiguo")
            (candidate / "GameAssembly.dll").write_text("nuevo")
            (game / "mi-config.json").write_text("personal")
            updater.preserve_player_files(game, candidate)
            self.assertEqual(
                (candidate / "UserData/partida.json").read_text(),
                "partida real",
            )
            self.assertEqual(
                (candidate / "GameAssembly.dll").read_text(), "nuevo"
            )
            self.assertEqual(
                (candidate / "mi-config.json").read_text(), "personal"
            )

    @patch.object(
        updater.subprocess,
        "check_output",
        return_value="C:\\Games\\PvZ_Fusion\\Game Files\\PlantsVsZombiesRH.exe\n",
    )
    @patch.object(updater, "release")
    def test_open_game_defers_update_without_network(
        self, release_mock, process_mock
    ):
        self.assertFalse(updater.update(ROOT, Path("/unused"), "v0.1"))
        release_mock.assert_not_called()

    @patch.object(updater.subprocess, "check_output", return_value="")
    @patch.object(updater, "release", return_value={"tag_name": "v0.1"})
    def test_same_version_does_not_download(self, release_mock, process_mock):
        with patch.object(updater, "download") as download_mock:
            self.assertFalse(updater.update(ROOT, Path("/unused"), "v0.1"))
            download_mock.assert_not_called()

    def test_numeric_versions(self):
        self.assertGreater(
            updater.version_number("v1.0"), updater.version_number("v0.9")
        )
        with self.assertRaises(RuntimeError):
            updater.version_number("../../ruta")

    def test_full_base_and_patch_upgrade_preserves_player(self):
        with tempfile.TemporaryDirectory(
            dir=os.environ["PVZ_TEST_TEMP"]
        ) as temporary:
            root = Path(temporary)
            project, game = root / "proyecto", root / "Game Files"
            project.mkdir()
            (game / "UserData").mkdir(parents=True)
            (game / "UserData/partida.json").write_text("partida conservada")
            (game / "GameAssembly.dll").write_bytes(b"anterior")
            digest = hashlib.sha256(b"nuevo").hexdigest()
            config = {
                "base_repository": updater.BASE_REPOSITORY,
                "base_tag": "base-nueva",
                "base_asset": "base.zip",
                "base_sha256": "0" * 64,
                "base_files": {
                    "GameAssembly.dll": digest,
                    "PlantsVsZombiesRH.exe": digest,
                },
            }
            script = (
                (ROOT / "pvz_fusion_es.py")
                .read_text()
                .replace('VERSION = "v0.1"', 'VERSION = "v0.2"')
            )
            for old in [
                "48096b917ee6aaf6e35c95c98e666a4399a9e0c3d5adbab727cee941eccf2d42",
                "d38afabdc98f8d910dba495fc8eb0868965aa0251a96db190ffba3773704f5b1",
            ]:
                script = script.replace(old, digest)
            text = b'{"hola":"mundo"}'
            relative = "Localization/Spanish/Strings/translation_strings.json"
            manifest = {
                "version": "v0.2",
                "game_version": "base nueva",
                "files": {relative: hashlib.sha256(text).hexdigest()},
            }

            def fake_download(asset, target, repository, expected=""):
                with zipfile.ZipFile(target, "w") as archive:
                    if repository == updater.REPOSITORY:
                        for name, content in {
                            "actualizacion.json": json.dumps(config),
                            "manifest.json": json.dumps(manifest),
                            "pvz_fusion_es.py": script,
                            "paquete/" + relative: text,
                        }.items():
                            archive.writestr("PvZ-Fusion-ES/" + name, content)
                    else:
                        for name in [
                            "GameAssembly.dll",
                            "PlantsVsZombiesRH.exe",
                            "version.dll",
                            "Mods/PvZ_Fusion_Translator.dll",
                        ]:
                            archive.writestr("Game Files/" + name, b"nuevo")
                        archive.writestr(
                            "Game Files/UserData/partida.json",
                            "valor predeterminado",
                        )

            latest = {
                "tag_name": "v0.2",
                "assets": [{"name": "PvZ-Fusion-ES.zip"}],
            }
            base = {"assets": [{"name": "base.zip"}]}
            with patch.object(
                updater, "release", side_effect=[latest, base]
            ), patch.object(
                updater, "download", side_effect=fake_download
            ), patch.object(
                updater.subprocess, "check_output", return_value=""
            ), patch.object(
                updater.subprocess, "run"
            ) as run_mock, patch.object(
                Path, "home", return_value=root
            ):
                self.assertTrue(updater.update(project, game, "v0.1"))
            self.assertEqual(
                (game / "UserData/partida.json").read_text(),
                "partida conservada",
            )
            self.assertEqual(
                (game / "GameAssembly.dll").read_bytes(), b"nuevo"
            )
            self.assertEqual(
                (game / "Mods/PvZ_Fusion_Translator" / relative).read_bytes(),
                text,
            )
            self.assertFalse(
                game.with_name(".PvZ-Fusion-ES-transaccion").exists()
            )
            self.assertEqual(
                json.loads((project / "manifest.json").read_text())["version"],
                "v0.2",
            )
            run_mock.assert_called_once()

    def test_download_rejects_untrusted_origin(self):
        with self.assertRaises(RuntimeError):
            updater.download(
                {"browser_download_url": "https://example.com/juego.zip"},
                Path("/unused"),
                updater.REPOSITORY,
            )


if __name__ == "__main__":
    unittest.main()
