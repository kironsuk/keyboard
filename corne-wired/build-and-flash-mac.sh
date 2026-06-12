#!/usr/bin/env bash
# Build (and optionally flash) the active wired Corne firmware on macOS.
#
#   ./build-and-flash-mac.sh            # build only -> updates firmware.hex
#   ./build-and-flash-mac.sh --flash    # build, then flash ONE half over USB
#
# keymap.c is the source of truth. The script copies it (plus config.h/rules.mk)
# into the QMK tree, compiles, and copies the hex back to firmware.hex.
# Flashing is split: run with --flash once per half (left, then right), each
# time plugged directly into USB (TRRS can't carry the programming signal).
set -euo pipefail
cd "$(dirname "$0")"

KB="crkbd/rev1"
KM="kiron_corne"
FW="firmware.hex"
QMK_KM="$HOME/qmk_firmware/keyboards/crkbd/keymaps/$KM"
HEX_OUT="$HOME/qmk_firmware/crkbd_rev1_kiron_corne.hex"

# avr-gcc@8 is keg-only; make sure it's on PATH regardless of shell config.
export PATH="/opt/homebrew/opt/avr-gcc@8/bin:$PATH"

echo "==> Copying sources into QMK ($QMK_KM)"
mkdir -p "$QMK_KM"
cp keymap.c config.h rules.mk "$QMK_KM/"

echo "==> Compiling $KB:$KM"
qmk compile -kb "$KB" -km "$KM"

echo "==> Copying hex back to $FW"
cp "$HEX_OUT" "$FW"
echo "==> Build OK: $FW"

if [ "${1:-}" != "--flash" ]; then
  echo "Done (build only). Re-run with --flash to flash a half."
  exit 0
fi

echo
echo "==> FLASH MODE — plug ONE half directly into USB."
BASELINE="$(ls /dev/cu.usbmodem* 2>/dev/null | sort -u || true)"
echo "    Current ports: ${BASELINE:-<none>}"
echo "    Short RST+GND on that half now (waiting up to 120s)..."
for _ in $(seq 1 1200); do
  CUR="$(ls /dev/cu.usbmodem* 2>/dev/null | sort -u || true)"
  NEW="$(comm -13 <(printf '%s\n' "$BASELINE") <(printf '%s\n' "$CUR") | grep -v '^$' | head -n1 || true)"
  if [ -n "$NEW" ]; then
    echo ">>> Bootloader detected: $NEW"
    sleep 1
    avrdude -p atmega32u4 -c avr109 -b 57600 -D -P "$NEW" -U "flash:w:$FW:i"
    echo ">>> Flash complete. Re-run with --flash for the other half."
    exit 0
  fi
  sleep 0.1
done
echo ">>> Timed out waiting for bootloader port." >&2
exit 1
