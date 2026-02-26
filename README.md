# Keyboard Firmware

QMK firmware configurations for two custom split ergonomic keyboards.

## Directory Structure

```
keyboard/
  corne/              # Corne (crkbd/rev1) - compact 3x6+3 split
    keymap.json         Source of truth (QMK Configurator JSON)
    keymap.c            Compiled C keymap with per-layer RGB colors
    config.h            RGBLIGHT, split keyboard config
    rules.mk            Build flags
    firmware.hex        Latest compiled firmware
    layout.pdf          Visual layout reference
  moonlander/         # ZSA Moonlander - larger split ergonomic
    source/
      keymap.c          Keymap with tap dance and RGB matrix
      config.h          Timing/feature config
      rules.mk          Build flags
    firmware.bin        Latest compiled firmware
    layout.pdf          Visual layout reference
    README.md           ZSA's build instructions
```

## Layer System (6 layers, shared across both keyboards)

| Layer | Purpose | Color (Corne) |
|-------|---------|---------------|
| 0 | Base QWERTY with home row mods | Cyan |
| 1 | Numbers (1-0) | Blue |
| 2 | Symbols and special characters | Magenta |
| 3 | Function keys (F1-F20) | Green |
| 4 | Navigation, arrows, clipboard | Orange |
| 5 | RGB controls, bootloader reset | Red |

## Building & Flashing

### Prerequisites

- [QMK CLI](https://docs.qmk.fm/newbs_getting_started) installed via `pipx install qmk`
- [QMK Toolbox](https://github.com/qmk/qmk_toolbox) for GUI flashing (optional)
- `arm-none-eabi-gcc` in PATH (for Moonlander ARM builds)

### Corne

The Corne uses a Pro Micro (ATmega32U4) with the Caterina bootloader.

**Edit the keymap:**
1. Edit `corne/keymap.json` in the [QMK Configurator](https://config.qmk.fm/) or by hand
2. Convert to C: `qmk json2c corne/keymap.json > corne/keymap.c`
3. Add any custom code (e.g., per-layer RGB) to `keymap.c`

**Compile:**
```bash
# Copy files to QMK directory
cp corne/{keymap.c,config.h,rules.mk} ~/qmk_firmware/keyboards/crkbd/keymaps/kiron_corne/

# Compile
cd ~/qmk_firmware
make crkbd/rev1:kiron_corne
```

**Flash via command line:**

1. Plug in the keyboard half you want to flash
2. Run the flash command (it will wait for bootloader mode):
```bash
while true; do
  PORT=$(ls /dev/cu.usbmodem* 2>/dev/null | head -1)
  if [ -n "$PORT" ]; then
    sleep 1
    avrdude -p atmega32u4 -c avr109 -b 57600 -D -P "$PORT" \
      -U flash:w:corne/firmware.hex:i
    break
  fi
  sleep 0.2
done
```
3. Short the RST and GND pins on the Pro Micro to enter bootloader mode (you have ~8 seconds)
4. Repeat for the other half

### Moonlander

Built against [ZSA's QMK fork](https://github.com/zsa/qmk_firmware/) (not upstream).

```bash
cp moonlander/source/* ~/qmk_firmware/keyboards/moonlander/keymaps/kiron/
cd ~/qmk_firmware
make moonlander:kiron
```

Flash the `.bin` file using [Wally](https://configure.zsa.io/wally) or QMK Toolbox.

Original Oryx layout: https://configure.zsa.io/moonlander/layouts/65yQL/WOAdM/0
