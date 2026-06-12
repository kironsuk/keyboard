#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

FIRMWARE="firmware.hex"

if ! command -v avrdude >/dev/null 2>&1; then
  echo "avrdude is not installed. Install it with: sudo apt-get install avrdude" >&2
  exit 1
fi

if [ ! -f "$FIRMWARE" ]; then
  echo "Firmware not found: $FIRMWARE" >&2
  exit 1
fi

echo "Preparing sudo access for avrdude..."
sudo -v

echo
echo "Waiting for Corne bootloader on /dev/ttyACM*..."
echo "Plug in one half, then double-tap reset or short RST to GND."
echo

while true; do
  PORT="$(find /dev -maxdepth 1 -name 'ttyACM*' -print | head -n1)"

  if [ -n "$PORT" ]; then
    echo "Found bootloader port: $PORT"
    sleep 1
    sudo avrdude -p atmega32u4 -c avr109 -b 57600 -D -P "$PORT" \
      -U "flash:w:$FIRMWARE:i"
    echo
    echo "Flash complete. Repeat this script for the other half."
    exit 0
  fi

  sleep 0.1
done
