"""Build the ct_nx mod archive from src/Localize/en/ (msg texts and png images).

  python3 tools/build_ctp.py [OUTPUT]   (default: build/ct_russian.ctp)

The layout matches ct_nx's own tools/generate_text_ctp.py: resources.bin paths
(Localize/en/msg/<file>.txt, Localize/en/png/<file>.png) in a DEFLATE zip.
Files kept in English (check.KEEP_ENGLISH) are left out: the game reads them from
resources.bin anyway, and the mod should not redistribute untouched original text.
The texts are validated with tools/check.py first when original/ is available
(it is not in CI: run tools/check.py locally before tagging a release).
"""
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from check import KEEP_ENGLISH, LANG, ORIG  # noqa: E402

SRC = ROOT / "src" / "Localize" / LANG
BUILD = ROOT / "build"


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else BUILD / "ct_russian.ctp"
    if ORIG.is_dir():
        if subprocess.run([sys.executable, str(ROOT / "tools" / "check.py")]).returncode:
            sys.exit("check.py failed; archive not built")
    else:
        print(f"{ORIG} not found: skipping validation (run tools/check.py locally before releasing)")
    files = sorted(f for f in SRC.rglob("*") if f.is_file() and f.name not in KEEP_ENGLISH)
    if not files:
        sys.exit(f"no files in {SRC}")
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.writestr(f"Localize/{LANG}/{f.relative_to(SRC).as_posix()}", f.read_bytes())
    print(f"{out}: {len(files)} files")


if __name__ == "__main__":
    main()
