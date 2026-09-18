# musescore-tweaks

A few small command-line tools for working with [MuseScore](https://musescore.org/) files: batch-exporting scores to PDF and MusicXML, stripping baked-in layout breaks so a score reflows freely, and swapping out the default notation font.

The three `clean-*`/`replace_font` scripts are plain Python 3 using only the standard library — no `pip install`, no dependencies — and each operates on copies (or writes a backup), leaving your originals intact. The batch export runs through a [fish](https://fishshell.com/) script that drives the MuseScore application itself; its one-time setup is described below.

## Installing the MuseScore AppImage

`export.fish` drives MuseScore Studio in converter mode, so it needs the application on disk. It expects a **portable AppImage** at a fixed path:

```
~/AppImages/musescore_studio_4.7_portable.appimage
```

Set it up once:

```bash
mkdir -p ~/AppImages
# Download the MuseScore Studio portable AppImage from https://musescore.org/download
# and save it to the path below, then make it executable:
mv ~/Downloads/MuseScore-Studio-*.AppImage ~/AppImages/musescore_studio_4.7_portable.appimage
chmod +x ~/AppImages/musescore_studio_4.7_portable.appimage
```

The path (and version) is hard-coded in `export.fish` via:

```fish
set APP ~/AppImages/musescore_studio_4.7_portable.appimage
```

If your AppImage lives elsewhere or is a different version, edit that line to match — or place your AppImage at the path above so the script works unchanged.

## Scripts

### `export.fish` — batch-export every `.mscz` to PDF and MusicXML

Run from a directory full of `.mscz` files. For each score it invokes the MuseScore AppImage with a generated [batch-conversion job](https://musescore.org/en/handbook/4/command-line-options) and writes the results into `exports/`:

```fish
./export.fish
```

Per score (`<name>.mscz`) it produces:

- `exports/pdf/<name>.pdf` — the full score as a single PDF
- `exports/pdf/<name>_1.pdf`, `<name>_2.pdf`, … — one PDF per page (via MuseScore's `[prefix, suffix]` split-output form)
- `exports/mxml/<name>.musicxml` — a MusicXML export

The output directories are created automatically. The script also points the MuseSampler instrument folder at `~/Muse Sounds` (`set -x MUSESAMPLER_INSTRUMENT_FOLDER "/home/$USER/Muse Sounds"`) so MuseScore can find the Muse Sounds libraries if they're installed; PDF and MusicXML export doesn't require them, so this is harmless if you don't have them.

Requires the [fish shell](https://fishshell.com/) and the AppImage set up as described above. It reads `.mscz` files only from the current directory (no recursion) and leaves them untouched.

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

It takes one or more files and **edits each in place**, writing a backup of every original first (see below). Pass a single score, several, or a glob to process every `.mscz` in the current directory at once:

```bash
python3 replace_font.py score.mscz              # one file
python3 replace_font.py a.mscz b.mscz c.mscz    # several
python3 replace_font.py *.mscz                  # every .mscz in this directory
```

Each backup is written to `_archive/tmp/<name>.mscz.bak` next to the file (the directory is created if needed), and the script reports the replacement count per file.

The fonts are set by two constants at the top of the file:

```python
OLD_FONT = "Edwin"        # MuseScore 4's default text font
NEW_FONT = "aBGRSerif"
```

Change `NEW_FONT` to whatever font you want to switch to (for example `"Liberation Serif"`), and adjust `OLD_FONT` if your score uses a different starting font.

## Notes

- The two `clean-*` scripts never touch your originals — they emit copies into `./cleaned/`. `replace_font.py` modifies each target file in place but backs it up to `_archive/tmp/<name>.mscz.bak` first.
- Tested against the MuseScore 4 file format. The `.mss` style files and the `Edwin` default font in particular are MuseScore 4 conventions.
