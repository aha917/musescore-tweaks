# musescore-tweaks

A few small command-line scripts for post-processing [MuseScore](https://musescore.org/) files and MusicXML exports: stripping baked-in layout breaks so a score reflows freely, and swapping out the default notation font.

Everything here is plain Python 3 using only the standard library — no `pip install`, no dependencies. Each script operates on copies (or writes a backup) and leaves your originals intact.

## Scripts

### `clean-mscz.py` — remove system breaks from `.mscz` files

MuseScore stores manual breaks as `<LayoutBreak>` elements inside the `.mscx` score that lives within each `.mscz` zip. This script removes them so the music can reflow instead of being locked to a fixed line layout.

Run it with no arguments; it processes every `.mscz` in the current directory and writes cleaned copies to `./cleaned/` under the same filenames:

```bash
python3 clean-mscz.py
```

By default only **system (line) breaks** are stripped. To remove page and/or section breaks as well, edit the `STRIP` set near the top of the file:

```python
STRIP = {"line", "page", "section"}
```

### `clean-mxml.py` — remove breaks from MusicXML exports

The MusicXML equivalent of the above. MusicXML encodes breaks as `<print new-system="yes"/>` and `<print new-page="yes"/>`; this script removes those directives so the file reflows in whatever program opens it. Any other layout a `<print>` element carries (system-layout, page-number, and so on) is preserved, and a `<print>` left carrying nothing is dropped entirely.

It handles both plain `.musicxml` and zipped `.mxl` files, processing everything in the current directory into `./cleaned/`:

```bash
python3 clean-mxml.py
```

Unlike `clean-mscz.py`, this one strips **both system and page breaks**. It reports how many of each it removed per file.

### `replace_font.py` — swap the default score font

MuseScore 4 stores font choices as `<...FontFace>` entries inside the `.mss` style files bundled in a `.mscz` (the main score style plus one per linked part). This script rewrites every such occurrence across all `.mss` members and leaves the rest of the archive byte-identical.

It takes a single file and **edits it in place**, writing a `.bak` backup alongside first:

```bash
python3 replace_font.py score.mscz
```

The fonts are set by two constants at the top of the file:

```python
OLD_FONT = "Edwin"        # MuseScore 4's default text font
NEW_FONT = "Liberation Serif"
```

Change `NEW_FONT` to whatever font you want to switch to (for example `"Liberation Serif"`), and adjust `OLD_FONT` if your score uses a different starting font.

## Notes

- The two `clean-*` scripts never touch your originals — they emit copies into `./cleaned/`. `replace_font.py` modifies the target file but backs it up to `<name>.mscz.bak` first.
- Tested against the MuseScore 4 file format. The `.mss` style files and the `Edwin` default font in particular are MuseScore 4 conventions.
