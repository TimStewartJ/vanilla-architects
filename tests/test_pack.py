import copy
import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from verify_pack import (
    LockedFile, safe_path, validate_manifest, validate_versions, verify_archive,
    verify_download,
)
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

    def test_download_hash_is_checked_before_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mod.jar"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("fabric.mod.json", json.dumps({"id": "test", "version": "1"}))
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
            verify_archive(path, self.pack, [self.lock])
            normalize_archive(path)
            first = path.read_bytes()
            verify_archive(path, self.pack, [self.lock])
            normalize_archive(path)
            self.assertEqual(first, path.read_bytes())


if __name__ == "__main__":
    unittest.main()
