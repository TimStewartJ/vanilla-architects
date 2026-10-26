import copy
import hashlib
import json
import sys
import tempfile
import tomllib
import unittest
import zipfile
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from verify_pack import (
    ARCHITECT_PALETTES, ARCHITECT_THEMES, LockedFile, safe_path, validate_manifest,
    validate_versions, verify_archive, verify_download,
)
from architect_theme import pack_theme, validate_packed_theme, validate_palette
from build_pack import normalize_archive


class PackTests(unittest.TestCase):
    def setUp(self):
        self.lock = LockedFile(
            "iris", "mods/iris.jar", "iris-project", "iris-version",
            "https://cdn.modrinth.com/data/iris.jar", "a" * 128,
        )
        self.pack = {
            "name": "Vanilla Architects", "version": "0.1.0",
            "versions": {"minecraft": "26.3", "fabric": "0.19.5"},
        }
        self.manifest = {
            "formatVersion": 1, "game": "minecraft", "name": self.pack["name"],
            "versionId": "0.1.0",
            "dependencies": {"minecraft": "26.3", "fabric-loader": "0.19.5"},
            "files": [{
                "path": self.lock.path, "hashes": {"sha512": self.lock.sha512},
                "downloads": [self.lock.url], "fileSize": 100,
                "env": {"client": "required", "server": "unsupported"},
            }],
        }

    def test_valid_manifest(self):
        validate_manifest(self.manifest, self.pack, [self.lock])

    def test_unsafe_paths(self):
        for value in ("../save", "/mods/a.jar", "mods\\a.jar", "C:/a", "a//b", "./a"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "Unsafe"):
                safe_path(value)

    def test_duplicate_and_missing_downloads(self):
        duplicate = copy.deepcopy(self.manifest)
        duplicate["files"] *= 2
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_manifest(duplicate, self.pack, [self.lock])
        self.manifest["files"] = []
        with self.assertRaisesRegex(ValueError, "missing"):
            validate_manifest(self.manifest, self.pack, [self.lock])

    def test_wrong_target_and_server_environment(self):
        self.manifest["dependencies"]["minecraft"] = "26.2"
        with self.assertRaisesRegex(ValueError, "versions"):
            validate_manifest(self.manifest, self.pack, [self.lock])
        self.manifest["dependencies"]["minecraft"] = "26.3"
        self.manifest["files"][0]["env"]["server"] = "required"
        with self.assertRaisesRegex(ValueError, "environment"):
            validate_manifest(self.manifest, self.pack, [self.lock])

    def test_gameplay_mods_and_dependencies_require_server_installation(self):
        for slug in (
            "tax-free-levels", "grind-enchantments", "fabric-api", "cloth-config",
            "double-doors", "collective",
        ):
            with self.subTest(slug=slug):
                lock = replace(self.lock, slug=slug)
                manifest = copy.deepcopy(self.manifest)
                manifest["files"][0]["env"]["server"] = "required"
                validate_manifest(manifest, self.pack, [lock])
                manifest["files"][0]["env"]["server"] = "unsupported"
                with self.assertRaisesRegex(ValueError, "environment"):
                    validate_manifest(manifest, self.pack, [lock])

    def test_missing_and_wrong_required_dependencies(self):
        version = {
            "project_id": self.lock.project, "id": self.lock.version,
            "game_versions": ["26.3"], "loaders": ["fabric"],
            "files": [{"url": self.lock.url, "hashes": {"sha512": self.lock.sha512}}],
            "dependencies": [{
                "dependency_type": "required", "project_id": "sodium-project",
                "version_id": "required-sodium",
            }],
        }
        with self.assertRaisesRegex(ValueError, "Missing required dependency"):
            validate_versions([(self.lock, version)])
        sodium = LockedFile("sodium", "mods/sodium.jar", "sodium-project", "wrong", "", "")
        with self.assertRaisesRegex(ValueError, "Wrong required dependency version"):
            validate_versions([(self.lock, version), (sodium, {})])

    def test_resource_packs_are_client_only_vanilla_packs(self):
        lock = LockedFile(
            "fresh-animations", "resourcepacks/fa.zip", "fa-project", "fa-version",
            "https://cdn.modrinth.com/data/fa.zip", "b" * 128,
        )
        manifest = copy.deepcopy(self.manifest)
        manifest["files"][0].update(
            path=lock.path, downloads=[lock.url], hashes={"sha512": lock.sha512},
        )
        validate_manifest(manifest, self.pack, [lock])
        manifest["files"][0]["env"]["server"] = "required"
        with self.assertRaisesRegex(ValueError, "environment"):
            validate_manifest(manifest, self.pack, [lock])
        version = {
            "project_id": lock.project, "id": lock.version, "game_versions": ["26.3"],
            "loaders": ["fabric"], "dependencies": [],
            "files": [{"url": lock.url, "hashes": {"sha512": lock.sha512}}],
        }
        with self.assertRaisesRegex(ValueError, "minecraft support"):
            validate_versions([(lock, version)])
        version["loaders"] = ["minecraft"]
        validate_versions([(lock, version)])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pack.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("assets/minecraft/textures/a.png", b"")
            entry = {
                "path": lock.path, "fileSize": path.stat().st_size,
                "hashes": {"sha512": hashlib.sha512(path.read_bytes()).hexdigest()},
            }
            with self.assertRaises(KeyError):
                verify_download(path, entry)
            with zipfile.ZipFile(path, "a") as archive:
                archive.writestr("pack.mcmeta", '\ufeff{"pack": {"description": "x"}}')
            entry["fileSize"] = path.stat().st_size
            entry["hashes"]["sha512"] = hashlib.sha512(path.read_bytes()).hexdigest()
            verify_download(path, entry)

    def test_download_hash_is_checked_before_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mod.jar"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr(
                    "fabric.mod.json",
                    '{"id": "test", "version": "1", "description": "two\nlines"}',
                )
            entry = {
                "path": "mods/test.jar", "fileSize": path.stat().st_size,
                "hashes": {"sha512": hashlib.sha512(path.read_bytes()).hexdigest()},
            }
            verify_download(path, entry)
            entry["hashes"]["sha512"] = "0" * 128
            with self.assertRaisesRegex(ValueError, "sha512 mismatch"):
                verify_download(path, entry)

    def test_packwiz_directory_entry_and_reproducible_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pack.mrpack"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("overrides/", b"")
                archive.writestr("modrinth.index.json", json.dumps(self.manifest))
                archive.writestr("overrides/config/iris.properties", "enableShaders=false\n")
                archive.writestr(
                    "overrides/config/sodium-options.json",
                    '{"performance":{"use_no_error_g_l_context":false}}',
                )
                archive.writestr(
                    "overrides/config/DistantHorizons.toml",
                    '_version=5\n[client.advanced.autoUpdater]\nenableAutoUpdater=false\n'
                    '[common.logging.warning]\nlogGarbageCollectorWarning=true\n'
                    'showGarbageCollectorWarning=false\n',
                )
                root = Path(__file__).resolve().parents[1]
                for name in sorted(ARCHITECT_THEMES | ARCHITECT_PALETTES):
                    archive.write(root / name.removeprefix("overrides/"), name)
            verify_archive(path, self.pack, [self.lock])
            normalize_archive(path)
            first = path.read_bytes()
            verify_archive(path, self.pack, [self.lock])
            normalize_archive(path)
            self.assertEqual(first, path.read_bytes())

    def test_sodium_compatibility_setting_keeps_its_literal_shape(self):
        root = Path(__file__).resolve().parents[1]
        settings = json.loads((root / "config" / "sodium-options.json").read_text())
        self.assertEqual(settings, {"performance": {"use_no_error_g_l_context": False}})

    def test_dh_compatibility_settings_keep_diagnostics_and_pinned_updates(self):
        root = Path(__file__).resolve().parents[1]
        with (root / "config" / "DistantHorizons.toml").open("rb") as source:
            settings = tomllib.load(source)
        self.assertEqual(settings, {
            "_version": 5,
            "client": {"advanced": {"autoUpdater": {"enableAutoUpdater": False}}},
            "common": {"logging": {"warning": {
                "logGarbageCollectorWarning": True,
                "showGarbageCollectorWarning": False,
            }}},
        })


class ArchitectThemeTests(unittest.TestCase):
    root = Path(__file__).resolve().parents[1]

    def palette(self, name):
        return {"Palette": {"Name": name, "CLEAR": {"Name": "minecraft:air"}}}

    def design(self, blocks="A"):
        return {"Size": {"X": 1, "Y": 1, "Z": 1}, "Layers": [{"Blocks": blocks, "Facing": "A"}]}

    def test_shipped_theme_and_palette_are_valid(self):
        theme = json.loads((self.root / "mightyarchitect/themes/cattingham_poplar.json").read_text("utf-8"))
        self.assertEqual(theme["Theme"]["Name"], "Cattingham Poplar")
        self.assertEqual(validate_packed_theme(theme), 184)
        palette = json.loads((self.root / "mightyarchitect/palettes/poplar_cattingham.json").read_text("utf-8"))
        validate_palette(palette, "palette")
        self.assertEqual(palette, theme["Palette"])

    def test_folder_is_packed_with_enum_keys_in_declared_order(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory) / "castle"
            theme = {"Name": "Castle", "Layers": ["Roofing", "Regular"], "Types": ["WALL", "FLAT_ROOF"]}
            files = {
                "theme.json": theme, "palette.json": self.palette("A"),
                "regular/wall/design_10.json": self.design("10"),
                "regular/wall/design_2.json": self.design("2"),
                "regular/wall/design.json": self.design("0"),
                "roofing/flatroof/design.json": {**self.design("r"), "DataVersion": 1},
            }
            for name, content in files.items():
                (folder / name).parent.mkdir(parents=True, exist_ok=True)
                (folder / name).write_text(json.dumps(content), "utf-8")
            packed = pack_theme(folder)
            self.assertEqual(list(packed["Designs"]), ["Roofing", "Regular"])
            self.assertEqual(
                [design["Layers"][0]["Blocks"] for design in packed["Designs"]["Regular"]["WALL"]],
                ["0", "2", "10"],
            )
            self.assertNotIn("DataVersion", packed["Designs"]["Roofing"]["FLAT_ROOF"][0])
            self.assertNotIn("SecondaryPalette", packed)
            (folder / "open/wall").mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, "does not declare layers"):
                pack_theme(folder)

    def test_invalid_packed_themes_are_rejected(self):
        valid = {
            "Theme": {"Name": "T", "Layers": ["Regular"], "Types": ["WALL"]},
            "Palette": self.palette("T"),
            "Designs": {"Regular": {"WALL": [self.design()]}},
        }
        self.assertEqual(validate_packed_theme(valid), 1)
        for change, message in (
            (lambda data: data["Designs"].update(Open={"WALL": [self.design()]}), "undeclared layer"),
            (lambda data: data["Designs"]["Regular"].update(ROOF=[self.design()]), "undeclared type"),
            (lambda data: data["Designs"]["Regular"]["WALL"][0]["Size"].update(X=0), "Invalid design"),
            (lambda data: data["Palette"]["Palette"].pop("Name"), "named"),
            (lambda data: data.update(Designs={}), "no designs"),
        ):
            data = copy.deepcopy(valid)
            change(data)
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                validate_packed_theme(data)


if __name__ == "__main__":
    unittest.main()
