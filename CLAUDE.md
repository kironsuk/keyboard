# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

QMK firmware configurations for two custom split ergonomic keyboards:
- **Corne (crkbd/rev1)** — compact 3x6+3 split keyboard, Pro Micro (ATmega32U4), Caterina bootloader
- **Moonlander** — ZSA's larger split ergonomic keyboard, ARM STM32

## Directory Structure

- `corne/keymap.json` — Source of truth for the Corne keymap (QMK Configurator JSON)
- `corne/keymap.c` — Compiled C keymap with per-layer RGB color code
- `corne/config.h` — RGBLIGHT config, split keyboard settings
- `corne/rules.mk` — Build flags (RGBLIGHT_ENABLE=yes)
- `corne/firmware.hex` — Latest compiled firmware
- `corne/layout.txt` — ASCII visual reference for all layers
- `moonlander/source/` — Moonlander keymap source (keymap.c, config.h, rules.mk)
- `moonlander/firmware.bin` — Latest compiled firmware

## Build & Flash

### Corne
1. Edit `corne/keymap.json` in the [QMK Configurator](https://config.qmk.fm/) or by hand
2. Convert: `qmk json2c corne/keymap.json > corne/keymap.c`
3. Add custom code (per-layer RGB) back to `keymap.c`
4. Copy to QMK: `cp corne/{keymap.c,config.h,rules.mk} ~/qmk_firmware/keyboards/crkbd/keymaps/kiron_corne/`
5. Compile: `cd ~/qmk_firmware && make crkbd/rev1:kiron_corne`
6. Flash: use avrdude with `-p atmega32u4 -c avr109 -b 57600` on `/dev/cu.usbmodem*` port
7. Must use `/dev/cu.usbmodem*` (not `/dev/tty.usbmodem*`) on macOS
8. Short RST+GND on Pro Micro for bootloader (~8 second window)

### Moonlander
Built against [ZSA's QMK fork](https://github.com/zsa/qmk_firmware/), not upstream.
1. Copy `moonlander/source/` to `qmk_firmware/keyboards/moonlander/keymaps/<name>/`
2. Compile: `make moonlander:<name>`
3. Flash `.bin` with Wally or QMK Toolbox

Oryx layout: https://configure.zsa.io/moonlander/layouts/65yQL/WOAdM/0

## Architecture

### Corne Layer System (6 layers)
- **Layer 0**: Base QWERTY with bottom row mods (mod-tap on Z/X/C/F and M/,/.//)
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
