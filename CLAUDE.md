# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Firmware configurations for custom split ergonomic keyboards:
- **YIVU Corne 4.1 Wireless** (the keyboard Kiron actually owns, Amazon ASIN B0FZGV71WM) — 46-key Corne clone running vendor QMK/Vial firmware; wireless is a proprietary 2.4GHz dongle driven by a TNT-BT_M V2 module (nRF51822). NOT a nice!nano, NOT ZMK-flashable, no UF2 bootloader. Layout is managed live via Vial (`corne/corne4.1vial/`), no firmware flashing involved.
- **Bluetooth Corne 4.1 (ZMK config)** — ZMK config originally written for this keyboard before discovering it isn't a nice!nano board. Kept for a future true nice!nano Corne; builds work (see scripts).
- **Corne (crkbd/rev1)** — compact 3x6+3 split keyboard, Pro Micro (ATmega32U4), Caterina bootloader
- **Moonlander** — ZSA's larger split ergonomic keyboard, ARM STM32

## Directory Structure

- `build.yaml` — ZMK build matrix for Bluetooth Corne left/right halves
- `.github/workflows/zmk-build.yml` — GitHub Actions workflow for ZMK firmware artifacts
- `corne/corne4.1vial/kiron-layout.vil` — Source of truth for the YIVU Corne 4.1 layout (load with Vial or `vitaly load -f`)
- `corne/corne4.1vial/Initial.vil` — Kiron's first manual Vial export (had bottom-row-mod and symbols-layer bugs; superseded)
- `corne4.1Bluetooth/corne.keymap` — ZMK keymap port of Kiron's Corne layout, no lighting layer
- `corne4.1Bluetooth/corne.conf` — ZMK keyboard name and sleep settings
- `corne4.1Bluetooth/west.yml` — ZMK manifest
- `corne/keymap.json` — Source of truth for the Corne keymap (QMK Configurator JSON)
- `corne/keymap.c` — Compiled C keymap with per-layer RGB color code
- `corne/config.h` — RGBLIGHT config, split keyboard settings
- `corne/rules.mk` — Build flags (RGBLIGHT_ENABLE=yes)
- `corne/firmware.hex` — Latest compiled firmware
- `corne/layout.txt` — ASCII visual reference for all layers
- `moonlander/source/` — Moonlander keymap source (keymap.c, config.h, rules.mk)
- `moonlander/firmware.bin` — Latest compiled firmware

## Build & Flash

### Bluetooth Corne 4.1 / ZMK
The ZMK config uses:
- `board: nice_nano`
- `shield: corne_left`
- `shield: corne_right`

The keymap has 5 layers: Base, Numbers, Symbols, Function, Navigation. It intentionally does not include the old RGB/backlight layer. The nav layer top row includes Bluetooth clear/select profile controls, USB/Bluetooth output toggle, previous/next profile controls, and a custom battery-percent output key. If a vendor-specific Corne 4.1 shield exposes extra physical key positions, keep those bindings as `&none`.

Build through GitHub Actions using `.github/workflows/zmk-build.yml`, which passes `config_path: corne4.1Bluetooth`; download the `firmware` artifact and flash the left/right UF2 files to each half in bootloader mode.

#### Status update, 2026-06-09 (evening): keyboard is not a nice!nano board

A photo of the actual PCB revealed the "Bluetooth Corne 4.1" Kiron bought is a YIVU Corne clone: vendor QMK/Vial firmware on the main MCU, with a soldered TNT-BT_M V2 module (nRF51822) providing a proprietary 2.4GHz dongle link (this is also how Vial configures it wirelessly). There is no UF2 bootloader and ZMK cannot run on it. **Never attempt to flash the ZMK UF2s to this keyboard.**

The layout was recreated in Vial instead. `corne/corne4.1vial/kiron-layout.vil` is the corrected source of truth (fixes vs `Initial.vil`: left bottom-row mods were off by one — C/V positions had TD(3)/TD(4); symbols layer restored to old layout using the two extra inner-column keys for `|` and `^`; MO(0) no-ops made transparent; nav layer got Home/PgDn/PgUp/End back). Kiron loaded it onto the board via the Vial web app on 2026-06-09. CLI alternative: `vitaly load -f corne/corne4.1vial/kiron-layout.vil` (binary verified at /tmp/vitaly.tar.xz, install pending user approval).

Bluetooth investigation, concluded 2026-06-09: the keyboard has NO Bluetooth support as shipped. Evidence: (1) the Vial definition pulled from the device over raw HID (VID 0x55D4 "Pilot", PID 0x0461 "W-CORNE") contains no custom keycodes — unlike YMDK/Cornix cousins which expose BT0/BT1/BT2/Switch Output in Vial's User tab; (2) BLE scans across keyboard power cycles with the dongle unplugged show the keyboard never advertises (BLE devices found nearby were Tractive pet trackers and other household gear). Wireless is the proprietary 2.4GHz dongle link only; wired USB-C also works. If Kiron ever wants true BT: ask YIVU support about a BT firmware for the TNT-BT_M V2 module, or build a real nice!nano ZMK Corne (config in this repo is ready). Useful tooling from this session: `vitaly` CLI (~/.local/bin) loads/saves Vial layouts headlessly.

#### Prior ZMK handoff status, 2026-06-09 (afternoon) — superseded, kept for context

Both halves now build successfully (right-half peripheral link fix verified). UF2s in `firmware/corne4.1Bluetooth/` are for a future real nice!nano Corne only.

What has been changed so far:
- Old wired QMK Corne config in `corne/` is still present and should be preserved.
- New Bluetooth Corne 4.1 ZMK config lives in `corne4.1Bluetooth/`.
- ZMK board name was corrected from `nice_nano_v2` to `nice_nano`, because the current ZMK Docker image exposes the board as `nice_nano` with revision `2.0.0`.
- `corne4.1Bluetooth/corne.keymap` includes output and battery behavior headers. The nav layer top row includes `&out OUT_TOG`, `&bt BT_PRV`, `&bt BT_NXT`, and custom `&batt`.
- `corne4.1Bluetooth/corne.conf` enables `CONFIG_ZMK_BATTERY_REPORTING=y`, which is required by the custom battery behavior.
- A custom ZMK module was added at repo root:
  - `zephyr/module.yml`
  - `CMakeLists.txt`
  - `Kconfig`
  - `dts/behaviors/battery_output.dtsi`
  - `dts/bindings/behaviors/zmk,behavior-battery-output.yaml`
  - `src/behaviors/behavior_battery_output.c`
- `scripts/build-zmk-corne.sh` and `scripts/build-zmk-corne-in-container.sh` build with Docker image `zmkfirmware/zmk-build-arm:stable`. They default to both shields, but accept `SHIELDS=corne_right` or `SHIELDS=corne_left` for focused rebuilds.
- The Zephyr workspace is cached in the `zmk-corne-cache` Docker volume, so only the first build pays the full `west update` fetch; later builds skip it unless `corne4.1Bluetooth/west.yml` changes and reuse incremental build dirs. Use `FRESH=1 bash scripts/build-zmk-corne.sh` to wipe the cached workspace, or `docker volume rm zmk-corne-cache` to delete it entirely.

Build history and next steps:
- First build failed before keymap compile because `nice_nano_v2` is not a valid board in this ZMK image.
- After switching to `nice_nano`, the left build reached link and failed because `zmk_battery_state_of_charge` was missing.
- After enabling `CONFIG_ZMK_BATTERY_REPORTING=y`, the left half built and produced `firmware/corne4.1Bluetooth/corne_left-nice_nano-zmk.uf2`.
- The right half then failed because peripherals do not link `raise_zmk_keycode_state_changed`, which the custom battery-output behavior uses.
- `CMakeLists.txt` was updated to compile `behavior_battery_output.c` only for non-split or central builds:
  `if(NOT CONFIG_ZMK_SPLIT OR CONFIG_ZMK_SPLIT_ROLE_CENTRAL)`.
- A focused `SHIELDS=corne_right bash scripts/build-zmk-corne.sh` run was started to verify that fix, but Kiron asked to stop. The Docker container was stopped during the Zephyr fetch, before right-half compile completed.

Recommended next command:

```bash
SHIELDS=corne_right bash scripts/build-zmk-corne.sh
```

If that succeeds, run the full default build once:

```bash
bash scripts/build-zmk-corne.sh
```

Expected final UF2s:
- `firmware/corne4.1Bluetooth/corne_left-nice_nano-zmk.uf2`
- `firmware/corne4.1Bluetooth/corne_right-nice_nano-zmk.uf2`

Notes on the battery key:
- Upstream ZMK has built-in `&out OUT_TOG`, `&bt BT_NXT`, and `&bt BT_PRV`, but no stock binding that types the current battery percentage.
- The custom `&batt` behavior types the current battery percentage, e.g. `85%`, by reading `zmk_battery_state_of_charge()` and raising keycode events.
- This behavior is intentionally central-only because the right half is a split peripheral and cannot emit keycode events directly.

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
