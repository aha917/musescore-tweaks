#!/usr/bin/env python3
"""Replace the default score font (Edwin -> aBGRSerif) inside a MuseScore .mscz file.

MuseScore stores font choices as <xxxFontFace>Edwin</xxxFontFace> entries inside the
*.mss style files bundled in the .mscz zip (the main score_style.mss plus one .mss
per linked part/excerpt). This rewrites every such occurrence in every .mss member,
leaving all other archive members byte-identical.
"""
import shutil
import sys
import zipfile
from pathlib import Path

OLD_FONT = "Edwin"
NEW_FONT = "aBGRSerif"


def replace_font_in_mscz(src: Path, dst: Path, old: str = OLD_FONT, new: str = NEW_FONT) -> int:
    total_replacements = 0
    with zipfile.ZipFile(src, "r") as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith(".mss"):
                text = data.decode("utf-8")
                count = text.count(f">{old}<")
                if count:
                    text = text.replace(f">{old}<", f">{new}<")
                    total_replacements += count
                    data = text.encode("utf-8")
            zout.writestr(item, data)
    return total_replacements


def process_one(src: Path) -> None:
    if not src.exists():
        print(f"File not found: {src}")
        return

    backup_dir = src.parent / "_archive" / "tmp"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / (src.name + ".bak")
    shutil.copy2(src, backup)

    tmp_out = src.with_suffix(".tmp.mscz")
    n = replace_font_in_mscz(src, tmp_out)
    tmp_out.replace(src)
    print(f"{src.name}: replaced {n} occurrences (backup: {backup.relative_to(src.parent)})")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <score1.mscz> [score2.mscz ...]")
        print(f"       {sys.argv[0]} *.mscz")
        sys.exit(1)

    for arg in sys.argv[1:]:
        process_one(Path(arg))


if __name__ == "__main__":
    main()
