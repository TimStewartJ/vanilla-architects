import argparse
import json
import os
import re
import shutil
from pathlib import Path

from build_server import SERVER_COMPONENTS
from verify_pack import SHADERS, load_locks, read_toml, safe_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("harness", type=Path)
    parser.add_argument("--shader", choices=sorted(SHADERS), default="i-like-vanilla")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    pack = read_toml(root / "pack.toml")
    shader = read_toml(root / "shaderpacks" / f"{args.shader}.pw.toml")
    filename = safe_path(shader["filename"])
    if "/" in filename or "\n" in filename or "\r" in filename:
        raise ValueError("Smoke shader must be a single filename")
    instance = Path(os.environ["VANILLA_ARCHITECTS_INSTANCE"])
    (instance / "smoke-shader.txt").write_text(filename, encoding="utf-8")
    _, locks = load_locks(root)
    (instance / "server-mods.json").write_text(
        json.dumps(sorted(
            lock.path for lock in locks
            if lock.slug in SERVER_COMPONENTS - {"the-mighty-architectury"}
        )),
        encoding="utf-8",
    )
    properties = args.harness / "versions" / "26.3" / "gradle.properties"
    text, count = re.subn(
        r"(?m)^fabric_loader_version=.*$",
        f"fabric_loader_version={pack['versions']['fabric']}",
        properties.read_text(encoding="utf-8"),
    )
    if count != 1:
        raise ValueError("Expected one Fabric Loader pin in the smoke harness")
    properties.write_text(text, encoding="utf-8")
    init_dir = Path(os.environ["GRADLE_USER_HOME"]) / "init.d"
    init_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / "scripts" / "pack-smoke.gradle", init_dir / "pack-smoke.gradle")


if __name__ == "__main__":
    main()
