# Keyboard Firmware

Firmware configurations for custom split ergonomic keyboards.

The **wired Corne** (`corne-wired/`) is the keyboard currently in active use and is
the focus of this README. Other keyboards Kiron owns or has configured live under
[`archive/`](archive/) — see [`archive/README.md`](archive/README.md).

```
keyboard/
  corne-wired/          # ACTIVE — Corne crkbd/rev1, Pro Micro, QMK
    keymap.json           Source of truth (QMK Configurator JSON)
    keymap.c              Compiled C keymap with per-layer RGB colors
    config.h              RGBLIGHT, split keyboard config
    rules.mk              Build flags
    firmware.hex          Latest compiled firmware
    layout.txt            ASCII layout reference for all layers
    layout.pdf            Visual layout reference
    flash-corne-linux.sh  Linux flash helper (avrdude)
  archive/              # Not in active use — see archive/README.md
    corne-zmk/            Future nice!nano Corne (ZMK), self-contained
    yivu-corne-4.1/       YIVU wireless Corne Kiron owns (Vial backup)
    moonlander/           ZSA Moonlander QMK config
```

## Wired Corne Layout

6 layers, bottom row mods. Hold a bottom row key for the modifier, tap for the letter.

| Layer | Purpose | RGB Color | Activate |
|-------|---------|-----------|----------|
| 0 | Base QWERTY with bottom row mods | Cyan | Default |
| 1 | Numbers on top and home rows | Blue | Hold left thumb MO(1) |
| 2 | Symbols: brackets/operators on top, shifted symbols on home | Magenta | Hold left thumb MO(2) |
| 3 | Function keys: F1-F10 top, F11-F20 home | Green | MO(1)+MO(3) or MO(4)+MO(3) |
| 4 | Navigation: clipboard on home, arrows/pgup/pgdn | Orange | Hold right thumb MO(4) |
| 5 | RGB controls, bootloader reset | Red | DF(5) from Layer 3 |

Bottom row mod-taps (Layer 0):

| Key | Tap | Hold |
|-----|-----|------|
| Left 2 | Z | Shift |
| Left 3 | X | Ctrl |
| Left 4 | C | Alt |
| Left 5 | V | Gui |
| Right 2 | M | Gui |
| Right 3 | , | Alt |
| Right 4 | . | Ctrl |
| Right 5 | / | Shift |

See `corne-wired/layout.txt` for the full visual layout of every layer.

RGB settings (brightness, saturation, effects) persist across all layers — only the hue changes per layer.

## Making Changes to the Wired Corne Keymap

### Quick reference

```bash
# 1. Edit the keymap JSON (in QMK Configurator or by hand)
#    Save the export to corne-wired/keymap.json

# 2. Update keymap.c with the new layer definitions
#    (keep the RGB color code at the bottom of keymap.c unchanged)

# 3. Copy files to QMK and compile
cp corne-wired/{keymap.c,config.h,rules.mk} ~/qmk_firmware/keyboards/crkbd/keymaps/kiron_corne/
cd ~/qmk_firmware && make crkbd/rev1:kiron_corne

# 4. Copy the compiled hex back to the repo
cp ~/qmk_firmware/crkbd_rev1_kiron_corne.hex corne-wired/firmware.hex

# 5. Flash both halves (run once per half)
while true; do
  PORT=$(ls /dev/cu.usbmodem* 2>/dev/null | head -1)
  if [ -n "$PORT" ]; then
    sleep 1
    avrdude -p atmega32u4 -c avr109 -b 57600 -D -P "$PORT" \
      -U flash:w:corne-wired/firmware.hex:i
    break
  fi
  sleep 0.2
done
# Then short RST+GND on the Pro Micro to enter bootloader (~8 second window)
# Repeat for the other half
```

### Step-by-step walkthrough

#### 1. Edit the keymap

Edit `corne-wired/keymap.json` in the [QMK Configurator](https://config.qmk.fm/) (import the file, make changes, export) or edit the JSON by hand.

#### 2. Update keymap.c

The JSON only defines key assignments. `corne-wired/keymap.c` also contains custom C code for per-layer RGB colors that must be preserved. When updating `keymap.c`:

- Replace only the `keymaps[]` array (layers 0-5) with the new key definitions
- Keep everything below the array unchanged (the `layer_hues[]`, `set_layer_color()`, `keyboard_post_init_user()`, `layer_state_set_user()` functions)
- If the JSON uses `UG_` keycodes (newer QMK), replace them with `RGB_` equivalents for QMK 0.23.2:
  - `UG_TOGG` → `RGB_TOG`, `UG_NEXT` → `RGB_MOD`, `UG_PREV` → `RGB_RMOD`
  - `UG_HUEU` → `RGB_HUI`, `UG_HUED` → `RGB_HUD`
  - `UG_SATU` → `RGB_SAI`, `UG_SATD` → `RGB_SAD`
  - `UG_VALU` → `RGB_VAI`, `UG_VALD` → `RGB_VAD`
  - `UG_SPDU` → `RGB_SPI`, `UG_SPDD` → `RGB_SPD`
- Strip `ANY()` wrappers from mod-tap keys (e.g., `ANY(MT(MOD_LSFT, KC_Z))` → `MT(MOD_LSFT, KC_Z)`)

#### 3. Compile

```bash
cp corne-wired/{keymap.c,config.h,rules.mk} ~/qmk_firmware/keyboards/crkbd/keymaps/kiron_corne/
cd ~/qmk_firmware
make crkbd/rev1:kiron_corne
```

The compiled hex lands at `~/qmk_firmware/crkbd_rev1_kiron_corne.hex`. Copy it back:

```bash
cp ~/qmk_firmware/crkbd_rev1_kiron_corne.hex corne-wired/firmware.hex
```

#### 4. Flash

Both halves must be flashed separately. For each half:

1. Run the flash command below — it will poll for the bootloader port:
```bash
while true; do
  PORT=$(ls /dev/cu.usbmodem* 2>/dev/null | head -1)
  if [ -n "$PORT" ]; then
    sleep 1
    avrdude -p atmega32u4 -c avr109 -b 57600 -D -P "$PORT" \
      -U flash:w:corne-wired/firmware.hex:i
    break
  fi
  sleep 0.2
done
```
2. Short the RST and GND pins on the Pro Micro to enter bootloader mode. You have about 8 seconds before it times out.
3. Wait for "avrdude done" confirmation, then repeat for the other half.

On Linux, `corne-wired/flash-corne-linux.sh` automates the same flow against `/dev/ttyACM*`.

**Important notes:**
- Use `/dev/cu.usbmodem*` (not `/dev/tty.usbmodem*`) on macOS
- The 1-second sleep after port detection is necessary for the port to stabilize
- If flashing fails mid-write, retry — the keyboard is not bricked, just reset again

#### 5. Update layout.txt

After changing the keymap, update `corne-wired/layout.txt` to keep the visual reference in sync.

### Prerequisites

- [QMK CLI](https://docs.qmk.fm/newbs_getting_started) installed via `pipx install qmk`
- [QMK Toolbox](https://github.com/qmk/qmk_toolbox) for GUI flashing (optional)
- `arm-none-eabi-gcc` in PATH — add to `~/.zshrc`:
  ```bash
  export PATH="/usr/local/opt/arm-none-eabi-gcc@8/bin:$PATH"
  ```
- Run `qmk doctor` to verify your environment is ready

## Other keyboards

The Moonlander, the YIVU wireless Corne, and the future-nice!nano ZMK Corne configs
live under [`archive/`](archive/), each with its own README.
