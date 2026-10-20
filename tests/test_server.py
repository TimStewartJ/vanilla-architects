import copy
import json
import sys
import tempfile
import unittest
import zipfile
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_server import (
    SERVER_COMPONENTS, manifest_bytes, select_server_locks, server_manifest,
    verify_server_environment,
)
from verify_pack import LockedFile, SERVER_MODS, load_locks


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.pack = {
            "name": "Vanilla Architects", "version": "0.3.0",
            "versions": {"minecraft": "26.3", "fabric": "0.19.5"},
        }
        self.locks = [
            LockedFile(
                slug, f"mods/{slug}.jar", f"project-{slug}", f"version-{slug}",
                f"https://cdn.modrinth.com/data/{slug}.jar", "a" * 128,
            )
            for slug in sorted(SERVER_COMPONENTS)
        ]
        self.versions = [
            (lock, {
                "project_id": lock.project, "id": lock.version,
                "version_number": "1.0", "game_versions": ["26.3"],
                "loaders": ["fabric"], "dependencies": [],
                "files": [{
                    "url": lock.url, "hashes": {"sha512": lock.sha512},
                    "size": 100,
                }],
            })
            for lock in self.locks
        ]

    def test_server_subset_uses_existing_pins_and_excludes_rendering(self):
        root = Path(__file__).resolve().parents[1]
        pack, locks = load_locks(root)
        selected = select_server_locks(locks)
        self.assertEqual({lock.slug for lock in selected}, SERVER_COMPONENTS)
        self.assertTrue(SERVER_MODS <= SERVER_COMPONENTS)
        self.assertEqual(len(selected), 9)
        self.assertFalse(
            {"iris", "sodium", "buildprint", "sorted", "modmenu"} & SERVER_COMPONENTS
        )
        self.assertEqual(pack["versions"], self.pack["versions"])

    def test_missing_or_duplicate_server_component_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "exactly once"):
            select_server_locks(self.locks[:-1])
        with self.assertRaisesRegex(ValueError, "exactly once"):
            select_server_locks(self.locks + [self.locks[0]])

    def test_client_locks_are_not_exported(self):
        client = replace(self.locks[0], slug="iris", path="mods/iris.jar")
        self.assertEqual(select_server_locks(self.locks + [client]), self.locks)

    def test_server_manifest_retains_exact_downloads_and_loader(self):
        manifest = server_manifest(self.pack, self.versions)
        self.assertEqual(manifest["dependencies"], {
            "minecraft": "26.3", "fabric-loader": "0.19.5",
        })
        for entry, lock in zip(manifest["files"], self.locks, strict=True):
            self.assertEqual(entry["downloads"], [lock.url])
            self.assertEqual(entry["hashes"]["sha512"], lock.sha512)
            self.assertEqual(entry["versionId"], lock.version)
        reverse = server_manifest(self.pack, list(reversed(self.versions)))
        self.assertEqual(manifest_bytes(manifest), manifest_bytes(reverse))
        self.assertEqual(json.loads(manifest_bytes(manifest)), manifest)

    def test_upstream_dependencies_and_target_are_still_checked(self):
        broken = copy.deepcopy(self.versions)
        broken[0][1]["game_versions"] = ["26.1.2"]
        with self.assertRaisesRegex(ValueError, "26.3"):
            server_manifest(self.pack, broken)
        broken = copy.deepcopy(self.versions)
        broken[0][1]["dependencies"] = [{
            "dependency_type": "required", "project_id": "missing-project",
            "version_id": None,
        }]
        with self.assertRaisesRegex(ValueError, "Missing required"):
            server_manifest(self.pack, broken)

    def test_server_environment_rejects_client_only_mods(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mod.jar"
            for environment in ("*", "server", "client"):
                with zipfile.ZipFile(path, "w") as archive:
                    archive.writestr("fabric.mod.json", json.dumps({
                        "id": "test", "version": "1", "environment": environment,
                    }))
                if environment == "client":
                    with self.assertRaisesRegex(ValueError, "Client-only"):
                        verify_server_environment(path)
                else:
                    verify_server_environment(path)


if __name__ == "__main__":
    unittest.main()
