"""Helpers for working on src/Localize/en/msg/*.txt.

  python3 tools/loc.py init FILE        create src/Localize/en/msg/FILE as a copy of the English original
                                        (X_pad.txt if the file has a twin); refuses to overwrite
  python3 tools/loc.py show FILE [A B]  print entries A..B (1-based line numbers) as EN / JA / RU
  python3 tools/loc.py apply FILE EDITS replace entries listed in EDITS: "KEY,text" for keyed files,
                                        "@LINE|text" for positional ones; lines starting with # are ignored
  python3 tools/loc.py map FILE TABLE   translate every entry whose English text appears in TABLE ("English|Russian")
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


def src_name(name: str) -> str:
    pad = name.replace(".txt", "_pad.txt")
    return pad if (ORIG / "en" / "msg" / pad).exists() else name


def read(path: Path) -> list[str]:
    return path.read_bytes().removeprefix(BOM).decode("utf-8").split("\r\n")


def write(name: str, lines: list[str]) -> None:
    bom = BOM if (ORIG / LANG / "msg" / name).read_bytes().startswith(BOM) else b""
    (OUT / name).write_bytes(bom + "\r\n".join(lines).encode("utf-8"))


def key(line: str) -> str | None:
    m = KEY_RE.match(line)
    return m.group(1) if m else None


def init(name: str) -> None:
    if (OUT / name).exists():
        sys.exit(f"{name} already exists in {OUT}")
    en = read(ORIG / "en" / "msg" / src_name(name))
    OUT.mkdir(parents=True, exist_ok=True)
    write(name, en)
    print(f"{name}: {len(en)} lines copied from {src_name(name)}")


def show(name: str, a: int = 1, b: int = 10**9) -> None:
    en = read(ORIG / "en" / "msg" / src_name(name))
    ja = read(ORIG / "ja" / "msg" / src_name(name))
    ru = read(OUT / name)
    for i in range(a - 1, min(b, len(en))):
        if not en[i].split(",", 1)[-1].strip() and not ru[i].split(",", 1)[-1].strip():
            continue
        print(f"@{i + 1}\nEN {en[i]}\nJA {ja[i] if i < len(ja) else ''}\nRU {ru[i]}\n")


def apply(name: str, edits: Path) -> None:
    ru = read(OUT / name)
    idx = {key(l): i for i, l in enumerate(ru) if key(l)}
    n = 0
    for e in edits.read_text(encoding="utf-8").splitlines():
        if not e.strip() or e.startswith("#"):
            continue
        if e.startswith("@"):
            num, text = e[1:].split("|", 1)
            ru[int(num) - 1] = text
        else:
            k = key(e)
            if k not in idx:
                sys.exit(f"unknown key in edits: {e[:60]}")
            ru[idx[k]] = e
        n += 1
    write(name, ru)
    print(f"{name}: {n} entries replaced")


def map_text(name: str, table: Path) -> None:
    pairs = dict(l.split("|", 1) for l in table.read_text(encoding="utf-8").splitlines() if "|" in l)
    en = read(ORIG / "en" / "msg" / src_name(name))
    ru = read(OUT / name)
    n = 0
    for i, line in enumerate(en):
        k = key(line)
        text = line.split(",", 1)[1] if k else line
        if text in pairs:
            ru[i] = f"{k},{pairs[text]}" if k else pairs[text]
            n += 1
    write(name, ru)
    print(f"{name}: {n} entries mapped")


if __name__ == "__main__":
    cmd, name, *rest = sys.argv[1:]
    if cmd == "init":
        init(name)
    elif cmd == "show":
        show(name, *map(int, rest))
    elif cmd == "apply":
        apply(name, Path(rest[0]))
    elif cmd == "map":
        map_text(name, Path(rest[0]))
