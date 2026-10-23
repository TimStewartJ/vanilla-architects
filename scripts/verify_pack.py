from __future__ import annotations

import hashlib
import json
import re
import shutil
import tomllib
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

USER_AGENT = "VanillaArchitects/0.1 (github.com/TimStewartJ/vanilla-architects)"
MODS = {
    "3dskinlayers", "appleskin", "buildprint", "cloth-config", "collective",
    "continuity", "distanthorizons", "double-doors", "entity-model-features",
    "entityculling", "entitytexturefeatures", "fabric-api", "fallingleaves",
    "ferrite-core", "grind-enchantments", "immediatelyfast", "iris", "jade",
    "lambdynamiclights", "lithium", "modmenu", "mouse-tweaks",
    "not-enough-animations", "placeholder-api", "presence-footsteps",
    "shulkerboxtooltip", "sodium", "sorted", "sound-physics-remastered",
    "spyglass-improvements", "tax-free-levels", "the-mighty-architectury", "yacl",
}
SERVER_MODS = {
    "fabric-api", "cloth-config", "tax-free-levels", "grind-enchantments",
    "double-doors", "collective",
}
SHADERS = {"bliss-shader", "complementary-reimagined", "i-like-vanilla"}
RESOURCEPACKS = {
    "coffeepbr", "fa-player-extension", "fresh-animations", "fresh-animations-details",
}
# Enabled only in the disposable test client, lowest priority first; players choose their own packs.
SMOKE_RESOURCEPACKS = ("fresh-animations", "fresh-animations-details", "fa-player-extension")
LOCK_FOLDERS = {"mods": MODS, "shaderpacks": SHADERS, "resourcepacks": RESOURCEPACKS}
LOADERS = {"mods": "fabric", "shaderpacks": "iris", "resourcepacks": "minecraft"}
OVERRIDES = {
    "overrides/config/DistantHorizons.toml",
    "overrides/config/iris.properties",
    "overrides/config/sodium-options.json",
}


@dataclass(frozen=True)
class LockedFile:
    slug: str
    path: str
    project: str
    version: str
    url: str
    sha512: str


def read_toml(path: Path) -> dict:
    with path.open("rb") as source:
        return tomllib.load(source)


def safe_path(value: str) -> str:
    path = PurePosixPath(value)
    if (
        not value or "\\" in value or ":" in value or path.is_absolute()
        or any(part in {"", ".", ".."} for part in value.split("/"))
    ):
        raise ValueError(f"Unsafe archive path: {value!r}")
    return value


def digest(path: Path, algorithm: str) -> str:
    result = hashlib.new(algorithm)
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def load_locks(root: Path) -> tuple[dict, list[LockedFile]]:
    pack = read_toml(root / "pack.toml")
    if pack["versions"].get("minecraft") != "26.3":
        raise ValueError("This pack must target Minecraft 26.3")
    if set(pack["versions"]) != {"minecraft", "fabric"}:
        raise ValueError("This is a Fabric-only pack")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", pack["version"]):
        raise ValueError("Pack version must be a three-part release version")
    index_path = root / pack["index"]["file"]
    if digest(index_path, pack["index"]["hash-format"]) != pack["index"]["hash"]:
        raise ValueError("Stale pack index: run packwiz refresh")
    index = read_toml(index_path)
    locks = []
    seen = set()
    for entry in index["files"]:
        relative = safe_path(entry["file"])
        source = root / relative
        if digest(source, index["hash-format"]) != entry["hash"]:
            raise ValueError(f"Stale indexed file: {relative}; run packwiz refresh")
        if not entry.get("metafile"):
            if f"overrides/{relative}" not in OVERRIDES:
                raise ValueError(f"Unexpected override: {relative}")
            continue
        meta = read_toml(source)
        slug = source.name.removesuffix(".pw.toml")
        folder = source.parent.name
        expected = LOCK_FOLDERS.get(folder, set())
        if slug not in expected or slug in seen:
            raise ValueError(f"Unexpected or duplicate project: {slug}")
        seen.add(slug)
        expected_side = "both" if slug in SERVER_MODS else "client"
        if meta["side"] != expected_side:
            raise ValueError(f"{slug} must have side = {expected_side!r} in this pack")
        download = meta["download"]
        if download["hash-format"] != "sha512" or not re.fullmatch(
            r"[0-9a-f]{128}", download["hash"]
        ):
            raise ValueError(f"Invalid SHA-512 lock for {slug}")
        if not download["url"].startswith("https://cdn.modrinth.com/data/"):
            raise ValueError(f"Unexpected download host for {slug}")
        filename = safe_path(meta["filename"])
        if "/" in filename:
            raise ValueError(f"Filename must not contain directories: {filename}")
        update = meta["update"]["modrinth"]
        locks.append(LockedFile(
            slug, f"{folder}/{filename}", update["mod-id"], update["version"],
            download["url"], download["hash"],
        ))
    missing = (MODS | SHADERS | RESOURCEPACKS) - seen
    if missing:
        raise ValueError(f"Missing pinned projects: {', '.join(sorted(missing))}")
    return pack, locks


def validate_manifest(manifest: dict, pack: dict, locks: list[LockedFile]) -> None:
    if manifest.get("formatVersion") != 1 or manifest.get("game") != "minecraft":
        raise ValueError("Not a Modrinth format-1 Minecraft pack")
    if manifest.get("name") != pack["name"] or manifest.get("versionId") != pack["version"]:
        raise ValueError("Export name/version does not match pack.toml")
    if manifest.get("dependencies") != {
        "minecraft": pack["versions"]["minecraft"],
        "fabric-loader": pack["versions"]["fabric"],
    }:
        raise ValueError("Export Minecraft/Fabric versions do not match pack.toml")
    expected = {lock.path: lock for lock in locks}
    seen = set()
    for entry in manifest["files"]:
        path = safe_path(entry["path"])
        if path in seen or path not in expected:
            raise ValueError(f"Unexpected or duplicate download: {path}")
        seen.add(path)
        lock = expected[path]
        server_environment = "required" if lock.slug in SERVER_MODS else "unsupported"
        if entry.get("env") != {"client": "required", "server": server_environment}:
            raise ValueError(f"Incorrect client/server environment for {path}")
        if entry.get("downloads") != [lock.url]:
            raise ValueError(f"Download URL differs from the lock for {path}")
        if entry.get("hashes", {}).get("sha512") != lock.sha512:
            raise ValueError(f"Export hash differs from the lock for {path}")
        if not isinstance(entry.get("fileSize"), int) or entry["fileSize"] <= 0:
            raise ValueError(f"Missing download size for {path}")
    if seen != set(expected):
        raise ValueError(f"Export is missing files: {', '.join(sorted(set(expected) - seen))}")


def verify_archive(archive_path: Path, pack: dict, locks: list[LockedFile]) -> dict:
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        files = []
        for entry in archive.infolist():
            if entry.is_dir():
                directory = safe_path(entry.filename.removesuffix("/"))
                if directory not in {"overrides", "overrides/config"}:
                    raise ValueError(f"Unexpected archive directory: {directory}")
            else:
                safe_path(entry.filename)
                files.append(entry.filename)
        if len(names) != len(set(names)):
            raise ValueError("Duplicate archive entries")
        if set(files) != OVERRIDES | {"modrinth.index.json"}:
            raise ValueError(f"Unexpected archive contents: {sorted(files)}")
        manifest = json.loads(archive.read("modrinth.index.json"))
        validate_manifest(manifest, pack, locks)
        iris = archive.read("overrides/config/iris.properties").decode("utf-8")
        if "enableShaders=false" not in iris.splitlines():
            raise ValueError("Shaders must be disabled for the first launch")
        sodium = json.loads(archive.read("overrides/config/sodium-options.json"))
        if sodium.get("performance", {}).get("use_no_error_g_l_context") is not False:
            raise ValueError("Sodium's no-error GL context must be disabled for Iris compatibility")
        dh = tomllib.loads(archive.read("overrides/config/DistantHorizons.toml").decode("utf-8"))
        warning = dh.get("common", {}).get("logging", {}).get("warning", {})
        updater = dh.get("client", {}).get("advanced", {}).get("autoUpdater", {})
        if (
            dh.get("_version") != 5
            or warning.get("logGarbageCollectorWarning") is not True
            or warning.get("showGarbageCollectorWarning") is not False
            or updater.get("enableAutoUpdater") is not False
        ):
            raise ValueError("DH must retain GC diagnostics in logs, avoid the broken popup and keep updates pinned")
    return manifest


def get_version(lock: LockedFile) -> tuple[LockedFile, dict]:
    request = urllib.request.Request(
        f"https://api.modrinth.com/v2/version/{lock.version}",
        headers={"User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return lock, json.load(response)


def validate_versions(versions: list[tuple[LockedFile, dict]]) -> None:
    by_project = {lock.project: lock for lock, _ in versions}
    for lock, version in versions:
        if version["project_id"] != lock.project or version["id"] != lock.version:
            raise ValueError(f"Upstream project/version mismatch for {lock.slug}")
        if "26.3" not in version["game_versions"]:
            raise ValueError(f"{lock.slug} does not declare Minecraft 26.3 support")
        loader = LOADERS[lock.path.split("/", 1)[0]]
        if loader not in version["loaders"]:
            raise ValueError(f"{lock.slug} does not declare {loader} support")
        matching = [
            file for file in version["files"]
            if file["url"] == lock.url and file["hashes"]["sha512"] == lock.sha512
        ]
        if len(matching) != 1:
            raise ValueError(f"Upstream file/hash mismatch for {lock.slug}")
        for dependency in version["dependencies"]:
            if dependency["dependency_type"] != "required":
                continue
            project = dependency["project_id"]
            if project not in by_project:
                raise ValueError(
                    f"Missing required dependency: {lock.slug} -> {project}"
                )
            required_version = dependency["version_id"]
            if required_version and by_project[project].version != required_version:
                raise ValueError(f"Wrong required dependency version for {lock.slug}")


def download_file(entry: dict, cache: Path) -> Path:
    destination = cache / entry["hashes"]["sha512"]
    if not destination.exists():
        temporary = destination.with_suffix(".part")
        request = urllib.request.Request(
            entry["downloads"][0], headers={"User-Agent": USER_AGENT}
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                with temporary.open("wb") as output:
                    shutil.copyfileobj(response, output)
            verify_download(temporary, entry)
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)
    verify_download(destination, entry)
    return destination


def verify_download(path: Path, entry: dict) -> None:
    if path.stat().st_size != entry["fileSize"]:
        raise ValueError(f"Download size mismatch for {entry['path']}")
    for algorithm in ("sha512", "sha1"):
        expected = entry["hashes"].get(algorithm)
        if expected and digest(path, algorithm) != expected:
            raise ValueError(f"Download {algorithm} mismatch for {entry['path']}")
    with zipfile.ZipFile(path) as archive:
        if entry["path"].startswith("mods/"):
            metadata = json.loads(archive.read("fabric.mod.json"), strict=False)
            if not metadata.get("id") or not metadata.get("version"):
                raise ValueError(f"Invalid Fabric metadata in {entry['path']}")
        elif entry["path"].startswith("resourcepacks/"):
            metadata = json.loads(archive.read("pack.mcmeta").decode("utf-8-sig"))
            if not isinstance(metadata.get("pack"), dict):
                raise ValueError(f"Invalid resource pack metadata in {entry['path']}")
        else:
            if not any(
                "shaders/" in name and "dh_terrain" in name
                for name in archive.namelist()
            ):
                raise ValueError(f"No Distant Horizons terrain program in {entry['path']}")


def download_and_verify(
    root: Path, locks: list[LockedFile], manifest: dict, install_dir: Path | None
) -> None:
    if install_dir and install_dir.exists() and any(install_dir.iterdir()):
        raise ValueError(f"Installation destination is not empty: {install_dir}")
    cache = root / "build" / "downloads"
    cache.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        validate_versions(list(pool.map(get_version, locks)))
        entries = manifest["files"]
        downloads = list(pool.map(lambda entry: download_file(entry, cache), entries))
    if install_dir:
        install_dir.mkdir(parents=True, exist_ok=True)
        for entry, source in zip(entries, downloads, strict=True):
            destination = install_dir / entry["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        for override in sorted(OVERRIDES):
            relative = PurePosixPath(override).relative_to("overrides")
            destination = install_dir / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / relative, destination)
    print(
        f"Verified {len(MODS)} mods, {len(SHADERS)} shaders, {len(RESOURCEPACKS)} "
        "resource packs and all required dependencies"
    )
