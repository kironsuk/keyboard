#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: $0 path/to/firmware.uf2" >&2
  exit 2
fi

firmware="$1"

if [ ! -f "$firmware" ]; then
  echo "firmware not found: $firmware" >&2
  exit 1
fi

echo "Waiting for a UF2 bootloader volume..."
echo "Put one keyboard half into bootloader mode."

while true; do
  for volume in /Volumes/*; do
    [ -d "$volume" ] || continue
    if [ -f "$volume/INFO_UF2.TXT" ]; then
      echo "Found UF2 volume: $volume"
      cp "$firmware" "$volume/"
      sync
      echo "Copied $(basename "$firmware") to $volume"
      exit 0
    fi
  done
  sleep 0.5
done
