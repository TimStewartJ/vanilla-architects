import argparse
import os
import re
import shutil
import tomllib
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("harness", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    with (root / "pack.toml").open("rb") as source:
        pack = tomllib.load(source)
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
