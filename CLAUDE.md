# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Russian translation of **Chrono Trigger** for the Nintendo Switch port **ct_nx** (https://github.com/NaGaa95/ct_nx), shipped as a mod.

ct_nx runs the Android build (v2.1.5) on Switch. It loads mods from the `mods/` folder (set by `mods_dir` in `config.ini`) at startup without touching `resources.bin`. It accepts ChronoMod `.ctp` patches (zip archives whose paths mirror `resources.bin`, such as `Localize/en/msg/cmes0.txt`) and folder mods (`mods/<Name>/<resources.bin path>`). When both change the same file, the folder mod wins. The game language is set with `language=` in `config.ini`. Accepted values are `en fr de it es ja ko zh zh-Hant`, plus `default`.

**Target slot: English (`en`).** There is no Russian option, and none can be added: ct_nx maps `language=` to one of the engine's 9 fixed slot numbers (anything unknown falls back to English), and the mod loader only overrides paths that already exist in `resources.bin` (a new `Localize/ru/` would be silently ignored). So the translation replaces the English slot (`Localize/en/`), and players set `language=en` (or `default` on an English console).

**Controller (pad / Switch) interface only.** The touch interface isn't supported. Lines describing tapping, swiping, or the stylus must not appear in the translation. Every button-related line uses the controller wording with `<BTN_*>` tokens.

The port includes its own `tools/generate_text_ctp.py`, which builds a `.ctp` that replaces touch-screen wording with button prompts for the official languages. It's the reference for which keys to change (see "Touch-to-button keys" below).

**Task list: `TASKS.md`. Glossary and character voices: `GLOSSARY.md`.** Read both at the start of a session; update `TASKS.md` as work is done, add every new term to `GLOSSARY.md` before using it.

## Layout

- `original/Localize/<lang>/{msg,cell,png}`: the game's original localization files for all 9 language slots. Read-only reference, **not in git** (Square Enix's files; `.gitignore`d, keep a local copy). `original/Localize/en/msg` is both the English source text and the slot being replaced; `original/Localize/ja/msg` is the secondary reference.
- `src/Localize/en/`: **the translation**, mirroring `resources.bin` paths. This is the only place to edit.
  - `msg/`: all 77 text files (the `en` set minus the `_pad` twins). `debug_map.txt`/`debug_evt.txt` stay English (developer menus) and are left out of the mod; `MSG_GAMECLEAR_03` ("times") is deliberately empty.
  - `png/`: 3 redrawn images (`bad_end.png` end screen, `race_o_0.png` race HUD, `wcmn.png` era labels).
- `tools/`: helper scripts (below). `tools/monster_names.py`, `tools/terms.py`, `tools/montec_terms.py` hold EN→RU dictionaries for list files.
- `.github/workflows/release.yml`: pushing a tag `vX.Y.Z` builds the mod and publishes a GitHub release.
- `README.md`: player-facing install instructions (also used as the release notes). Credits: translation by Sergei, made with Claude (Anthropic).
- Licenses: `LICENSE` (MIT, English, authoritative) + `LICENSE.ru.md` (unofficial Russian translation) for `tools/` and `.github/`; `src/LICENSE.md` (CC BY-NC-SA 4.0, English and Russian sections) for the translation. Square Enix keeps all rights to the game; never ship untouched original text or files.
- `build/`: build output (git-ignored).

## Tools

- `python3 tools/check.py [files]`: validates `src/Localize/en/msg/` against `original/` (keys, tags, BOM, CRLF, box size, no touch wording, no untranslated or emptied lines).
- `python3 tools/loc.py init|show|apply|map FILE ...`: create a file from the English original, print EN/JA/RU side by side, apply `KEY,text` edits, map whole English texts through a table.
- `python3 tools/build_ctp.py [OUTPUT]`: runs `check.py` when `original/` exists, then packs `src/Localize/en/` (minus `KEEP_ENGLISH` files) into `build/ct_russian.ctp`. Same layout as ct_nx's own generator: `Localize/en/msg/<file>.txt`, `Localize/en/png/<file>.png`, DEFLATE zip.

## Releasing

Run `python3 tools/check.py` locally first (CI has no `original/`, so it cannot validate). Then tag and push: `git tag v1.0.0 && git push origin v1.0.0`. The workflow builds `build/ct_russian_<tag>.ctp` and attaches it to a release with `README.md` as the notes.

## Text file format

- Most files hold one entry per line: `KEY,text` (for example `FLD_CMES0_094,...`). The key prefix matches the file name. Some files have no keys and rely on line position: `menu.txt`, `item.txt`, `monster.txt`, `tech.txt`, `battle.txt`, and others. In those files the line count and order must match the original exactly.
- All language slots have the same file set, the same line counts, and the same keys; only the text differs.
- Files are UTF-8 with **CRLF** line endings. Some files, such as `menu.txt`, start with a UTF-8 BOM. Keep the line endings and the BOM exactly as they are.
- Inside the text, `\` is a line break and `<PAGE>` starts a new dialogue box. Other control tags include `<WAIT>xx</WAIT>`, `<AUTO_END>`, `<AUTO_PAGE>`, `<SHARP>`, `<C1>`…`</C1>`, `<CT>`, `<NUMBER>`, and `<NAME_CRO>`/`<NAME_PT1>` (character names). Keep every tag from the original line.
- Name tags insert the (renamable) name in the nominative; write lines so the tag stays in the nominative (see `GLOSSARY.md`).
- The button tokens are `<BTN_CONF>`, `<BTN_DASH>`, `<BTN_MENU>`, `<BTN_WARP>`, `<BTN_L>`, and `<BTN_R>`. The game swaps them for the bound button glyphs.
- In the game files, each base file (such as `cmes0.txt`) has the touch-screen wording, and its `*_pad.txt` twin (such as `cmes0_pad.txt`) has the controller wording. There are 9 such pairs: `cmes0`, `cmes1`, `cmes2`, `mesi0`, `mesk0`, `mesk1`, `mesk3`, `mess0`, `mest3`. In each pair, the two files have the same keys in the same order.
- **There are no `_pad` files in the translation.** The translated `X_pad.txt` is saved as `X.txt` without the suffix and replaces the base file. Never put `*_pad.txt` files in `Localize/`.

## Working on the translation

- To check a line, compare it with the original English: `original/Localize/en/msg/X_pad.txt` for files with a twin, `original/Localize/en/msg/X.txt` for the rest. Use `original/Localize/ja/msg/` when the English loses meaning (wordplay, tone, abbreviations).
- `python3 tools/loc.py show X.txt A B` prints lines A..B in all three languages.
- To list the lines with button tokens, run `grep -H '<BTN_' original/Localize/en/msg/*.txt`.

## Touch-to-button keys

ct_nx's `tools/generate_text_ctp.py` names the lines that need changing for the controller interface:

- **Copied from `_pad`:** 32 message IDs across `cmes0`, `cmes1`, `cmes2`, `mesi0`, `mesk0`, `mesk1`, `mesk3`, `mess0`, `mest3`. Covered by translating each `X_pad.txt` into `X.txt`.
- **Hand-rewritten touch text:** one line in `start.txt`, one in `cmes0.txt`, six in `tutorial.txt`, and one in `menu.txt`. These have no `_pad` twin, so the Russian text is written for buttons by hand. To find the exact keys, read that script.
