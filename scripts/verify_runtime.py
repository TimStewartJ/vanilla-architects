import argparse
import json
import re
import zipfile
from pathlib import Path

from verify_pack import MODS, read_toml


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("harness", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    log = (
        args.harness / "build" / "prod-client-test-results" / "26.3"
        / "fabric" / "client.log"
    ).read_text(encoding="utf-8")
    jars = sorted((root / "build" / "instance" / "mods").glob("*.jar"))
    if len(jars) != len(MODS):
        raise ValueError(f"Expected {len(MODS)} runtime jars, found {len(jars)}")
    for jar in jars:
        with zipfile.ZipFile(jar) as archive:
            metadata = json.loads(archive.read("fabric.mod.json"), strict=False)
        pattern = rf"\b{re.escape(metadata['id'])}\s+{re.escape(metadata['version'])}(?:\s|$)"
        if not re.search(pattern, log, re.MULTILINE):
            raise ValueError(f"Jar not confirmed in runtime: {jar.name}")
    shader = (root / "build" / "instance" / "smoke-shader.txt").read_text(encoding="utf-8")
    if f"Using shaderpack: {shader}" not in log:
        raise ValueError("The selected shader was not confirmed active in the client log")
    packs = json.loads(
        (root / "build" / "instance" / "smoke-resourcepacks.json").read_text(encoding="utf-8")
    )
    reloads = re.findall(r"Reloading ResourceManager: (.*)$", log, re.MULTILINE)
    if not reloads or any(pack not in reloads[-1].split(", ") for pack in packs):
        raise ValueError(f"Fresh Animations packs were not active in the client: {reloads[-1:]}")
    for error in (
        "Mod appleskin provides a broken implementation of ModMenuApi",
        "ran into an unexpected error running a GL call",
    ):
        if error in log:
            raise ValueError(f"Runtime integration error: {error}")
    settings = read_toml(
        args.harness / "fabric" / "versions" / "26.3" / "run-prod-client-test"
        / "config" / "DistantHorizons.toml"
    )
    warning = settings["common"]["logging"]["warning"]
    if warning["showGarbageCollectorWarning"] is not False or warning["logGarbageCollectorWarning"] is not True:
        raise ValueError("DH did not retain the intended effective warning preferences")
    if re.search(r"\[CHAT\].*Garbage collector detected", log):
        raise ValueError("DH displayed the GC advice popup instead of keeping it in the log")
    print(
        f"Confirmed all {len(jars)} runtime mod versions, active shader {shader} "
        f"and resource packs {', '.join(packs)}"
    )


if __name__ == "__main__":
    main()
