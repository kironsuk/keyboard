# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Firmware configurations for custom split ergonomic keyboards. **Only the wired
Corne is in active use.** It lives at the repo root in `corne-wired/`. The other
three keyboards are not in active use and live under `archive/`, each with its own
README:

- **Corne (crkbd/rev1)** — *active.* Compact 3x6+3 split, Pro Micro (ATmega32U4), Caterina bootloader, QMK with RGBLIGHT. Source of truth: `corne-wired/`.
- **YIVU Corne 4.1 Wireless** (the keyboard Kiron physically owns, Amazon ASIN B0FZGV71WM) — *archived/reference.* 46-key Corne clone running vendor QMK/Vial; wireless is a proprietary 2.4GHz dongle driven by a TNT-BT_M V2 module (nRF51822). NOT a nice!nano, NOT ZMK-flashable, no UF2 bootloader. Layout is managed live via Vial — see `archive/yivu-corne-4.1/`.
- **Corne 4.1 ZMK (future nice!nano)** — *archived.* ZMK config originally written for the YIVU board before discovering it isn't a nice!nano. Kept for a future true nice!nano Corne; local Docker builds work. See `archive/corne-zmk/`.
- **Moonlander** — *archived.* ZSA's larger split ergonomic keyboard, ARM STM32, QMK (ZSA fork). See `archive/moonlander/`.

> Repo was reorganized 2026-06-12: the single active board (`corne-wired/`) is at
> the root; everything else moved under `archive/`. Old paths (`corne/`,
> `corne4.1Bluetooth/`, root-level ZMK scaffolding) no longer exist.

## Directory Structure

```
corne-wired/            ACTIVE — Corne crkbd/rev1 (QMK)
  keymap.json             Source of truth (QMK Configurator JSON)
  keymap.c                Compiled C keymap + per-layer RGB color code
  config.h                RGBLIGHT, split keyboard settings
  rules.mk                Build flags (RGBLIGHT_ENABLE=yes)
  firmware.hex            Latest compiled firmware
  layout.txt              ASCII visual reference for all layers
  layout.pdf              Visual layout reference
  flash-corne-linux.sh    Linux flash helper (avrdude on /dev/ttyACM*)
archive/
  README.md               Index of archived keyboards
  yivu-corne-4.1/         YIVU wireless Corne (owned) — Vial backups
    kiron-layout.vil        Source of truth for the YIVU layout (Vial / vitaly load -f)
    Initial.vil             First manual export; buggy, superseded
  corne-zmk/              Future nice!nano Corne (ZMK), self-contained module
    config/                 ZMK user config (corne.keymap, corne.conf, west.yml)
    zephyr/ CMakeLists.txt Kconfig dts/ src/   Zephyr module + custom &batt behavior
    scripts/               Local Docker build + UF2 flash helpers
    firmware/              Last-built UF2s
    build.yaml workflows/  CI templates (disabled — see archive/corne-zmk/README.md)
  moonlander/             ZSA Moonlander (QMK ZSA fork)
    source/ firmware.bin layout.pdf README.md
```

## Build & Flash

### Corne (active) — `corne-wired/`

**`keymap.c` is the source of truth** — edit the `keymaps[]` array by hand
(use `layout.txt`/`layout.pdf` as the position map; each layer is exactly 42
keys in `LAYOUT_split_3x6_3` order). The per-layer RGB code lives only below the
array in `keymap.c`, so do NOT round-trip through `qmk json2c` (it regenerates
the whole file and wipes that code). Keep `keymap.json` (the QMK Configurator
export) and `layout.txt`/`layout.pdf` in sync by hand after editing.

**Toolchain note:** `avr-gcc@8` is keg-only; it must be on `PATH`
(`export PATH="/opt/homebrew/opt/avr-gcc@8/bin:$PATH"`, added to `~/.zshrc`).
The qmk CLI is a pipx install at `~/.local/bin/qmk`.

Build + flash on macOS — `corne-wired/build-and-flash-mac.sh`:
- `./build-and-flash-mac.sh` — copies `keymap.c`/`config.h`/`rules.mk` into the
  QMK tree, runs `qmk compile -kb crkbd/rev1 -km kiron_corne`, copies the hex
  back to `firmware.hex`.
- `./build-and-flash-mac.sh --flash` — after building, watches for the
  Caterina bootloader port and flashes ONE half. Run it once per half (left,
  then right), each plugged **directly into USB** (TRRS can't carry the
  programming signal). avrdude args: `-p atmega32u4 -c avr109 -b 57600 -D`.
- Bootloader: short RST+GND on the Pro Micro (~8s window). Must use
  `/dev/cu.usbmodem*` (not `/dev/tty.usbmodem*`). The script auto-detects it.

Manual fallback / Linux: `cd ~/qmk_firmware && make crkbd/rev1:kiron_corne`, then
`corne-wired/flash-corne-linux.sh`. See `README.md` for the full walkthrough and
UG_→RGB_ keycode notes.

### YIVU Corne 4.1 (owned) — `archive/yivu-corne-4.1/`
No firmware flashing — the layout is managed **live via Vial**. `kiron-layout.vil`
is the source of truth (load with the Vial web app or `vitaly load -f`). The board
is NOT a nice!nano and ZMK cannot run on it; it has no UF2 bootloader. It has no
Bluetooth as shipped — wireless is the proprietary 2.4GHz dongle only (wired USB-C
also works). Full hardware/Bluetooth investigation notes are in
`archive/yivu-corne-4.1/README.md`. **Never flash the ZMK UF2s to this keyboard.**

### Corne 4.1 ZMK (future nice!nano) — `archive/corne-zmk/`
Self-contained ZMK config + custom Zephyr module. Local Docker build:
`bash archive/corne-zmk/scripts/build-zmk-corne.sh` (accepts `SHIELDS=corne_left`/
`corne_right`, `FRESH=1`). Outputs to `archive/corne-zmk/firmware/`. GitHub Actions
CI is intentionally disabled by the reorg (ZMK requires `build.yaml` + module files
at repo root); see `archive/corne-zmk/README.md` for the custom `&batt` behavior,
the `nice_nano` board note, and how to re-enable CI for a real nice!nano build.

### Moonlander — `archive/moonlander/`
Built against [ZSA's QMK fork](https://github.com/zsa/qmk_firmware/), not upstream.
1. Copy `archive/moonlander/source/` to `qmk_firmware/keyboards/moonlander/keymaps/<name>/`
2. Compile: `make moonlander:<name>`
3. Flash `.bin` with Wally or QMK Toolbox

Oryx layout: https://configure.zsa.io/moonlander/layouts/65yQL/WOAdM/0

## Architecture

### Corne Layer System (6 layers)
- **Layer 0**: Base QWERTY with bottom row mods (mod-tap on Z/X/C/V and M/,/.//)
- **Layer 1**: Numbers on both top and home rows
- **Layer 2**: Symbols — brackets/operators on top (`` ` { } < > | - + ( ) \ ``), shifted symbols on home (`! @ # $ % ^ & * [ ] =`)
- **Layer 3**: Function keys — F1–F10 on top, F11–F20 on home
- **Layer 4**: Navigation — clipboard (undo/cut/copy/paste) on home, arrows on right home, Home/PgDn/PgUp/End on bottom
- **Layer 5**: RGB lighting controls, bootloader reset

### Key QMK Features
- **Mod-tap (`MT`)**: Hold for modifier, tap for keypress — bottom row mods on layer 0
- **Layer switching**: `MO()` momentary, `DF()` default
- **Per-layer RGB hue** (Corne): Only hue changes per layer (cyan/blue/magenta/green/orange/red); brightness, saturation, and effects persist across layers via `rgblight_sethsv_noeeprom`
- **Tap dance** (Moonlander only): 12 dances with single/hold/double/triple tap
- **RGB matrix** (Moonlander only): Per-layer LED schemes via `ledmap`, 72 LEDs

### QMK Version Notes
- QMK 0.23.2 uses older `RGB_` keycodes (not newer `UG_` prefix) — replace `UG_` with `RGB_` equivalents when converting from JSON
- Strip `ANY()` wrappers from mod-tap keys in JSON exports (e.g., `ANY(MT(...))` → `MT(...)`)
- When updating `keymap.c`, only replace the `keymaps[]` array — preserve the RGB color code below it
- Corne uses `RGBLIGHT_ENABLE`, Moonlander uses `RGB_MATRIX_ENABLE`

### Moonlander Config
- `TAPPING_TERM`: 300ms
- `IGNORE_MOD_TAP_INTERRUPT` enabled
- Oryx integration enabled (`ORYX_ENABLE`)
- RGB timeout: 15 minutes

### ZMK `&batt` behavior (archive/corne-zmk)
- Upstream ZMK has built-in `&out OUT_TOG`, `&bt BT_NXT`, `&bt BT_PRV`, but no stock binding that types the current battery percentage.
- The custom `&batt` behavior types the current battery percentage (e.g. `85%`) by reading `zmk_battery_state_of_charge()` and raising keycode events. Requires `CONFIG_ZMK_BATTERY_REPORTING=y`.
- It is intentionally central-only (`CMakeLists.txt`: `if(NOT CONFIG_ZMK_SPLIT OR CONFIG_ZMK_SPLIT_ROLE_CENTRAL)`) because a split peripheral cannot emit keycode events directly.
