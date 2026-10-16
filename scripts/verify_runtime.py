import argparse
import json
import re
import zipfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("harness", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    log = (
        args.harness / "build" / "prod-client-test-results" / "26.3"
        / "fabric" / "client.log"
    ).read_text(encoding="utf-8")
    for jar in sorted((root / "build" / "instance" / "mods").glob("*.jar")):
        with zipfile.ZipFile(jar) as archive:
            metadata = json.loads(archive.read("fabric.mod.json"))
        pattern = rf"\b{re.escape(metadata['id'])}\s+{re.escape(metadata['version'])}(?:\s|$)"
        if not re.search(pattern, log, re.MULTILINE):
            raise ValueError(f"Released jar not confirmed in runtime: {jar.name}")
    if "Using shaderpack: I Like Vanilla v1.5.0b.zip" not in log:
        raise ValueError("The selected shader was not confirmed active in the client log")
    print("Confirmed all 16 released mod versions and the active I Like Vanilla shader")


if __name__ == "__main__":
    main()
