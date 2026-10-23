from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from verify_pack import (
    SERVER_MODS, LockedFile, download_file, get_version, load_locks,
    validate_versions,
)

SERVER_COMPONENTS = SERVER_MODS | {
    "distanthorizons", "ferrite-core", "jade", "lithium",
    "the-mighty-architectury",
}


def select_server_locks(locks: list[LockedFile]) -> list[LockedFile]:
    selected = sorted(
        (lock for lock in locks if lock.slug in SERVER_COMPONENTS),
        key=lambda lock: lock.path,
    )
    if len(selected) != len(SERVER_COMPONENTS) or {
        lock.slug for lock in selected
    } != SERVER_COMPONENTS:
        raise ValueError("Server export requires every pinned server component exactly once")
    return selected


def server_manifest(pack: dict, versions: list[tuple[LockedFile, dict]]) -> dict:
    selected = select_server_locks([lock for lock, _ in versions])
    validate_versions(versions)
    by_slug = {lock.slug: version for lock, version in versions}
    files = []
    for lock in selected:
        version = by_slug[lock.slug]
        source = next(file for file in version["files"] if file["url"] == lock.url)
        files.append({
            "slug": lock.slug,
            "path": lock.path,
            "projectId": lock.project,
            "versionId": lock.version,
            "version": version["version_number"],
            "downloads": [lock.url],
            "hashes": source["hashes"],
            "fileSize": source["size"],
        })
    return {
        "formatVersion": 1,
        "name": f"{pack['name']} Server",
        "version": pack["version"],
        "dependencies": {
            "minecraft": pack["versions"]["minecraft"],
            "fabric-loader": pack["versions"]["fabric"],
        },
        "files": files,
    }


def verify_server_environment(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        metadata = json.loads(archive.read("fabric.mod.json"), strict=False)
    if metadata.get("environment", "*") == "client":
        raise ValueError(f"Client-only mod cannot be installed on the server: {path.name}")


def manifest_bytes(manifest: dict) -> bytes:
    return (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--install-dir", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    pack, locks = load_locks(root)
    selected = select_server_locks(locks)
    destination = args.install_dir.resolve() if args.install_dir else None
    if destination and destination.exists() and any(destination.iterdir()):
        raise ValueError(f"Installation destination is not empty: {destination}")
    cache = root / "build" / "downloads"
    cache.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        manifest = server_manifest(pack, list(pool.map(get_version, selected)))
        entries = manifest["files"]
        downloads = list(pool.map(lambda entry: download_file(entry, cache), entries))
    for path in downloads:
        verify_server_environment(path)
    content = manifest_bytes(manifest)
    output = root / "dist" / f"Vanilla-Architects-{pack['version']}-server.json"
    output.parent.mkdir(exist_ok=True)
    output.write_bytes(content)
    checksum = hashlib.sha512(content).hexdigest()
    output.with_suffix(".json.sha512").write_text(
        f"{checksum}  {output.name}\n", encoding="ascii"
    )
    if destination:
        for entry, source in zip(entries, downloads, strict=True):
            target = destination / entry["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        (destination / "server-pack.json").write_bytes(content)
    print(f"Verified {len(selected)} pinned server mods; built {output.name}")
    print(f"SHA-512 {checksum}")


if __name__ == "__main__":
    main()
