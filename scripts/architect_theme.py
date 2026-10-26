"""Pack a Mighty Architectury theme folder into the mod's single-file .json theme format.

The output is what the mod's own "export as single file" writes (PackedTheme in 3.0.0):
{"Theme": theme.json, "Palette": palette.json, "SecondaryPalette": palette2.json,
 "Designs": {LayerEnum: {TypeEnum: [design.json, ...]}}}. Shipped as an override under
mightyarchitect/themes/, it appears in every player's theme list as a read-only snapshot, and a
pack update replaces the whole file instead of leaving stale design files behind.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

DATA_VERSION = 1
# DesignLayer / DesignType in TMA 3.0.0: folder name on disk -> enum name used in packed themes.
LAYERS = {
    "foundation": "Foundation", "regular": "Regular", "open": "Open",
    "special": "Special", "none": "None", "roofing": "Roofing",
}
TYPES = {
    "wall": "WALL", "facade": "FACADE", "corner": "CORNER", "tower": "TOWER",
    "trim": "TRIM", "roof": "ROOF", "flatroof": "FLAT_ROOF", "towerroof": "TOWER_ROOF",
    "towerflatroof": "TOWER_FLAT_ROOF", "none": "NONE",
}


def natural_key(name: str) -> list:
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", name)]


def read_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    data.pop("DataVersion", None)
    return data


def pack_theme(folder: Path) -> dict:
    theme = read_json(folder / "theme.json")
    layers = {LAYERS.get(path.name): path for path in folder.iterdir() if path.is_dir()}
    if None in layers:
        raise ValueError(f"Unknown layer folder in {folder}")
    undeclared = set(layers) - set(theme["Layers"])
    if undeclared:
        raise ValueError(f"Theme does not declare layers {sorted(undeclared)}; the mod would drop them")
    designs = {}
    for layer in theme["Layers"]:
        if layer not in layers:
            continue
        types = {TYPES.get(path.name): path for path in layers[layer].iterdir() if path.is_dir()}
        if None in types:
            raise ValueError(f"Unknown design type folder under {layers[layer]}")
        undeclared = set(types) - set(theme["Types"])
        if undeclared:
            raise ValueError(f"Theme does not declare types {sorted(undeclared)}; the mod would drop them")
        by_type = {}
        for kind in theme["Types"]:
            files = sorted(types[kind].glob("*.json"), key=lambda path: natural_key(path.name)) if kind in types else []
            if files:
                by_type[kind] = [read_json(path) for path in files]
        if by_type:
            designs[layer] = by_type
    packed = {"Theme": theme, "Palette": read_json(folder / "palette.json")}
    if (folder / "palette2.json").exists():
        packed["SecondaryPalette"] = read_json(folder / "palette2.json")
    packed["Designs"] = designs
    packed["DataVersion"] = DATA_VERSION
    validate_packed_theme(packed)
    return packed


def validate_palette(palette: object, where: str) -> None:
    entries = palette.get("Palette") if isinstance(palette, dict) else None
    if not isinstance(entries, dict) or not isinstance(entries.get("Name"), str):
        raise ValueError(f"{where} is not a named Mighty Architectury palette")
    for key, state in entries.items():
        if key != "Name" and (not isinstance(state, dict) or not isinstance(state.get("Name"), str)):
            raise ValueError(f"{where} has an invalid block state for {key}")


def validate_packed_theme(packed: object) -> int:
    """Checks the shape the mod's codecs need; returns the number of designs."""
    if not isinstance(packed, dict) or not isinstance(packed.get("Theme"), dict):
        raise ValueError("Packed theme has no Theme object")
    theme = packed["Theme"]
    if not isinstance(theme.get("Name"), str) or not theme["Name"]:
        raise ValueError("Packed theme has no name")
    if not set(theme.get("Layers", [])) <= set(LAYERS.values()) or not theme.get("Layers"):
        raise ValueError(f"Packed theme declares unknown layers: {theme.get('Layers')}")
    if not set(theme.get("Types", [])) <= set(TYPES.values()) or not theme.get("Types"):
        raise ValueError(f"Packed theme declares unknown types: {theme.get('Types')}")
    validate_palette(packed.get("Palette"), "Palette")
    if "SecondaryPalette" in packed:
        validate_palette(packed["SecondaryPalette"], "SecondaryPalette")
    count = 0
    for layer, by_type in packed.get("Designs", {}).items():
        if layer not in theme["Layers"] or not isinstance(by_type, dict):
            raise ValueError(f"Designs for undeclared layer {layer}")
        for kind, designs in by_type.items():
            if kind not in theme["Types"] or not isinstance(designs, list):
                raise ValueError(f"Designs for undeclared type {layer}/{kind}")
            for design in designs:
                size = design.get("Size") if isinstance(design, dict) else None
                if (
                    not isinstance(size, dict)
                    or not all(isinstance(size.get(axis), int) and size[axis] > 0 for axis in "XYZ")
                    or not isinstance(design.get("Layers"), list)
                    or not all(
                        isinstance(row, dict) and isinstance(row.get("Blocks"), str)
                        for row in design["Layers"]
                    )
                ):
                    raise ValueError(f"Invalid design in {layer}/{kind}")
                count += 1
    if not count:
        raise ValueError("Packed theme has no designs")
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("folder", type=Path, help="theme folder, e.g. <instance>/mightyarchitect/themes/x")
    parser.add_argument("--output", type=Path, help="defaults to mightyarchitect/themes/<folder>.json")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output or root / "mightyarchitect" / "themes" / f"{args.folder.name}.json"
    packed = pack_theme(args.folder)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(packed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"Packed {validate_packed_theme(packed)} designs from {args.folder.name} into {output}")


if __name__ == "__main__":
    main()
