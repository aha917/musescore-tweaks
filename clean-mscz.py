#!/usr/bin/env python3
"""Remove system (line) breaks from every .mscz in the current directory.

Cleaned copies are written to ./cleaned/ with the same filenames.
Only system breaks are removed; page and section breaks are kept.
Uses the Python standard library only -- no pip installs needed.
"""
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

# Which LayoutBreak subtypes to strip. "line" == system break.
# Add "page" and/or "section" here if you want those gone too.
STRIP = {"line"}


def clean_mscx(data: bytes):
    """Return (cleaned_xml_bytes, number_of_breaks_removed)."""
    root = ET.fromstring(data)
    parent = {c: p for p in root.iter() for c in p}
    removed = 0
    for lb in list(root.iter("LayoutBreak")):
        st = lb.find("subtype")
        if st is not None and (st.text or "").strip() in STRIP:
            parent[lb].remove(lb)
            removed += 1
    out = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
    return out, removed


def process(src: Path, dst: Path):
    """Copy the .mscz, rewriting any .mscx entries inside it."""
    total = 0
    with zipfile.ZipFile(src, "r") as zin, \
         zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith(".mscx"):
                data, n = clean_mscx(data)
                total += n
            zout.writestr(item, data)
    return total


def main():
    out_dir = Path("cleaned")
    out_dir.mkdir(exist_ok=True)
    files = sorted(p for p in Path(".").glob("*.mscz"))
    if not files:
        print("No .mscz files in the current directory.")
        return
    for src in files:
        removed = process(src, out_dir / src.name)
        print(f"{src.name}: removed {removed} system break(s)")


if __name__ == "__main__":
    main()
