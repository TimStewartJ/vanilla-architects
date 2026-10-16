from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

from verify_pack import download_and_verify, load_locks, verify_archive


def normalize_archive(path: Path) -> None:
    temporary = path.with_suffix(".normalized")
    try:
        with zipfile.ZipFile(path) as source:
            with zipfile.ZipFile(
                temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
            ) as destination:
                for name in sorted(source.namelist()):
                    if source.getinfo(name).is_dir():
                        continue
                    content = source.read(name)
                    if name == "modrinth.index.json":
                        manifest = json.loads(content)
                        manifest["files"].sort(key=lambda entry: entry["path"])
                        content = json.dumps(
                            manifest, sort_keys=True, separators=(",", ":")
                        ).encode("utf-8")
                    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.create_system = 3
                    info.external_attr = 0o100644 << 16
                    destination.writestr(info, content)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packwiz", default="packwiz")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--install-dir", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    pack, locks = load_locks(root)
    output = root / "dist" / f"Vanilla-Architects-{pack['version']}.mrpack"
    output.parent.mkdir(exist_ok=True)
    subprocess.run(
        [args.packwiz, "modrinth", "export", "--output", str(output)],
        cwd=root, check=True,
    )
    verify_archive(output, pack, locks)
    normalize_archive(output)
    manifest = verify_archive(output, pack, locks)
    if args.download or args.install_dir:
        install_dir = args.install_dir.resolve() if args.install_dir else None
        download_and_verify(root, locks, manifest, install_dir)
    checksum = hashlib.sha512(output.read_bytes()).hexdigest()
    output.with_suffix(".mrpack.sha512").write_text(
        f"{checksum}  {output.name}\n", encoding="ascii"
    )
    print(f"Built {output.name}\nSHA-512 {checksum}")


if __name__ == "__main__":
    main()
