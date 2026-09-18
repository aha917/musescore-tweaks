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


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <score.mscz>")
        sys.exit(1)

    src = Path(sys.argv[1])
    if not src.exists():
        print(f"File not found: {src}")
        sys.exit(1)

    backup = src.with_suffix(src.suffix + ".bak")
    shutil.copy2(src, backup)
    print(f"Backup written to: {backup}")

    tmp_out = src.with_suffix(".tmp.mscz")
    n = replace_font_in_mscz(src, tmp_out)
    tmp_out.replace(src)
    print(f"Replaced {n} occurrences of '{OLD_FONT}' -> '{NEW_FONT}' in: {src}")


if __name__ == "__main__":
    main()
