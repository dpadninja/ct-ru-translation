"""Validate src/Localize/en/msg/*.txt against the original game files.

Usage: python3 tools/check.py [file.txt ...]   (default: every file in src/Localize/en/msg)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANG = "en"  # language slot the translation replaces (see CLAUDE.md)
OUT = ROOT / "src" / "Localize" / LANG / "msg"
ORIG = ROOT / "original" / "Localize"
BOM = b"\xef\xbb\xbf"
KEY_RE = re.compile(r"^([A-Z][A-Z0-9_]*),")
TAG_RE = re.compile(r"<(/?[A-Z][A-Z0-9_]*)>")
# Tags whose count may legitimately change in translation: page breaks, button glyphs
# (touch-screen lines are rewritten for the controller) and name placeholders
# (Russian word order and case often need a name dropped, added or repeated).
FREE_TAGS = {"PAGE"}
FREE_PREFIX = ("BTN_", "NAME_", "NICK_")
# Dialogue box limits, measured on the English text (names count as 5 characters).
MAX_WIDTH = 56
MAX_ROWS = 4
# Touch-screen wording is not allowed: the translation targets the controller interface only.
TOUCH_RE = re.compile(r"стилус|сенсорн|касани|коснит|косну|тапн|свайп|проведи(те)? пальцем", re.I)
# Entries that stay in Latin script: placeholders and language abbreviations.
KEEP_LATIN = {"Dummy", "JPN", "ENG", "Chrono Trigger", "SQUARE ENIX, INC.", "SQUARE ENIX, LTD.", "TOSE CO., LTD."}
DIALOGUE_RE = re.compile(r"^(cmes|mes|mest|kmes|exms|msg|comu|ques)")
# Developer debug menus: never shown to players, shipped in English.
KEEP_ENGLISH = {"debug_map.txt", "debug_evt.txt"}
# Entries deliberately left empty: "times" after the clear count cannot agree with every number in Russian.
ALLOW_EMPTY = {"MSG_GAMECLEAR_03"}


def source_path(name: str) -> Path:
    """English reference for a translated file: the _pad twin if it exists."""
    msg = ORIG / "en" / "msg"
    pad = msg / name.replace(".txt", "_pad.txt")
    return pad if pad.exists() else msg / name


def split_lines(data: bytes) -> list[str]:
    return data.decode("utf-8").split("\r\n")


def tags(text: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for t in TAG_RE.findall(text):
        if t not in FREE_TAGS and not t.startswith(FREE_PREFIX):
            out[t] = out.get(t, 0) + 1
    return out


def box_problems(text: str) -> list[str]:
    """Rows wider than MAX_WIDTH and boxes taller than MAX_ROWS in one dialogue entry."""
    t = re.sub(r"<WAIT>[0-9a-f]+</WAIT>", "", text)
    t = re.sub(r"<(NAME|NICK)_[A-Z0-9]+>", "XXXXX", t)
    t = t.replace("<S10>", "  ")
    out = []
    for box in re.split(r"<PAGE>|<AUTO_PAGE>|<SHARP>", t):
        rows = box.strip("\\").split("\\")
        if len(rows) > MAX_ROWS:
            out.append(f"{len(rows)} rows in one box")
        for row in rows:
            row = re.sub(r"<[^>]+>", "", row)
            if len(row) > MAX_WIDTH:
                out.append(f"row of {len(row)} chars: {row[:40]}...")
    return out


def check(path: Path) -> list[str]:
    errs = []
    name = path.name
    if name.endswith("_pad.txt"):
        return [f"{name}: _pad files must not be shipped (rename to {name.replace('_pad', '')})"]
    slot = ORIG / LANG / "msg" / name
    if not slot.exists():
        return [f"{name}: no such file in original/Localize/{LANG}/msg"]
    src = source_path(name)
    data, ref = path.read_bytes(), src.read_bytes()
    if data.startswith(BOM) != slot.read_bytes().startswith(BOM):
        errs.append(f"{name}: BOM differs from original {LANG} file")
    if b"\n" in data.replace(b"\r\n", b"") or b"\r" in data.replace(b"\r\n", b""):
        errs.append(f"{name}: line endings are not pure CRLF")
    a, b = split_lines(data.removeprefix(BOM)), split_lines(ref.removeprefix(BOM))
    if len(a) != len(b):
        errs.append(f"{name}: {len(a)} lines, original has {len(b)}")
    for i, (ru, en) in enumerate(zip(a, b), 1):
        km, ke = KEY_RE.match(ru), KEY_RE.match(en)
        if (km and km.group(1)) != (ke and ke.group(1)):
            errs.append(f"{name}:{i}: key {km and km.group(1)!r}, original {ke and ke.group(1)!r}")
            continue
        if tags(ru) != tags(en):
            errs.append(f"{name}:{i}: tags differ: {tags(ru)} vs original {tags(en)}")
        if km and not en.split(",", 1)[1].strip() and ru.split(",", 1)[1].strip():
            errs.append(f"{name}:{i}: text in an entry that is empty in the original")
        if km and km.group(1) not in ALLOW_EMPTY and en.split(",", 1)[1].strip() and not ru.split(",", 1)[1].strip():
            errs.append(f"{name}:{i}: empty entry, original has text")
        if en.strip() and not ru.strip():
            errs.append(f"{name}:{i}: empty line, original has text")
        text = re.sub(r"<[^>]+>", "", ru.split(",", 1)[1] if km else ru)
        if ru == en and name not in KEEP_ENGLISH and text not in KEEP_LATIN and not (km and km.group(1).startswith("MSG_FONT_")) and re.search(r"[A-Za-z]{3}", text) and not re.search(r"[А-Яа-яЁё]", text):
            errs.append(f"{name}:{i}: untranslated: {text[:50]}")
        if TOUCH_RE.search(ru):
            errs.append(f"{name}:{i}: touch-screen wording: {TOUCH_RE.search(ru).group(0)}")
        if DIALOGUE_RE.match(name) and km:
            errs += [f"{name}:{i}: {p}" for p in box_problems(ru.split(",", 1)[1]) if p not in box_problems(en.split(",", 1)[1])]
    return errs


def main() -> int:
    if not ORIG.is_dir():
        print(f"{ORIG} not found: the original game files are needed for validation")
        return 1
    files = [OUT / f for f in sys.argv[1:]] or sorted(OUT.glob("*.txt"))
    if not files:
        print(f"no files to check in {OUT}")
        return 1
    errs = [e for f in files for e in check(f)]
    print("\n".join(errs) or f"OK: {len(files)} file(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
