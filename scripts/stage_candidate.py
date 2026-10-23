import argparse
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

from verify_pack import digest


def mod_id(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        return json.loads(archive.read("fabric.mod.json"), strict=False)["id"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("harness", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    jars = args.harness / "fabric" / "versions" / "26.3" / "build" / "libs"
    candidates = [
        path for path in jars.glob("*-fabric.jar") if mod_id(path) == "mightyarchitect"
    ]
    installed = [
        path for path in (root / "build" / "instance" / "mods").glob("*.jar")
        if mod_id(path) == "mightyarchitect"
    ]
    if len(candidates) != 1 or len(installed) != 1:
        raise ValueError("Expected exactly one built candidate and one staged Mighty Architectury jar")
    shutil.copyfile(candidates[0], installed[0])
    commit = subprocess.check_output(
        ["git", "-C", str(args.harness), "rev-parse", "HEAD"], text=True
    ).strip()
    print(f"Testing TMA source commit {commit}")
    print(f"Candidate jar SHA-512: {digest(installed[0], 'sha512')}")
    print("Only the disposable runtime fixture was changed; no candidate .mrpack is distributed")


if __name__ == "__main__":
    main()
