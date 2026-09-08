#!/usr/bin/env python3
"""Strip system and page breaks from exported MusicXML.

MusicXML encodes breaks as <print new-system="yes"/> and
<print new-page="yes"/>. This removes those directives so the file
reflows freely in whatever program opens it. Any other layout a
<print> element carries (system-layout, page-number, etc.) is kept;
a <print> that held only a break is dropped entirely.

Handles both .musicxml (plain) and .mxl (zipped). Cleaned copies go to
./cleaned/ with the same filenames; originals are untouched.
Standard library only.
"""
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT_RE = re.compile(rb"<score-(?:partwise|timewise)\b")


def strip_breaks_xml(data: bytes):
    """Return (cleaned_bytes, system_breaks_removed, page_breaks_removed)."""
    m = ROOT_RE.search(data)
    if not m:                      # not a MusicXML score part; leave alone
        return data, 0, 0
    prolog = data[:m.start()]      # keep <?xml?>, <!DOCTYPE>, leading comments

    # keep comments/PIs so nothing else in the file is lost on rewrite
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True, insert_pis=True))
    root = ET.fromstring(data, parser=parser)
    parent = {c: p for p in root.iter() for c in p}

    sysb = pgb = 0
    for pr in list(root.iter("print")):
        if pr.get("new-system") is not None:
            if pr.get("new-system") == "yes":
                sysb += 1
            del pr.attrib["new-system"]
        if pr.get("new-page") is not None:
            if pr.get("new-page") == "yes":
                pgb += 1
            del pr.attrib["new-page"]
        # if the <print> now carries nothing, remove it
        if len(pr) == 0 and not pr.attrib and (pr.text is None or not pr.text.strip()):
            parent[pr].remove(pr)

    body = ET.tostring(root, encoding="utf-8", xml_declaration=False)
    out = prolog + body
    if data.endswith(b"\n") and not out.endswith(b"\n"):
        out += b"\n"
    return out, sysb, pgb


def process_musicxml(src: Path, dst: Path):
    out, s, p = strip_breaks_xml(src.read_bytes())
    dst.write_bytes(out)
    return s, p


def process_mxl(src: Path, dst: Path):
    ts = tp = 0
    with zipfile.ZipFile(src, "r") as zin, \
         zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            name = item.filename
            if name.endswith((".xml", ".musicxml")) and not name.startswith("META-INF/"):
                data, s, p = strip_breaks_xml(data)
                ts += s
                tp += p
            zout.writestr(item, data)
    return ts, tp


def main():
    out_dir = Path("cleaned")
    out_dir.mkdir(exist_ok=True)
    files = sorted(p for p in Path(".").glob("*")
                   if p.suffix.lower() in (".mxl", ".musicxml"))
    if not files:
        print("No .mxl or .musicxml files in the current directory.")
        return
    for f in files:
        if f.suffix.lower() == ".mxl":
            s, p = process_mxl(f, out_dir / f.name)
        else:
            s, p = process_musicxml(f, out_dir / f.name)
        print(f"{f.name}: removed {s} system break(s), {p} page break(s)")


if __name__ == "__main__":
    main()
