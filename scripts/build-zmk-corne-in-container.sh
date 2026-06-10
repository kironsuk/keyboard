#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${CONFIG_DIR:-corne4.1Bluetooth}"
BOARD="${BOARD:-nice_nano}"
OUT_DIR="${OUT_DIR:-firmware/corne4.1Bluetooth}"
SHIELDS="${SHIELDS:-corne_left corne_right}"
CACHE_DIR="${CACHE_DIR:-/cache}"

if [ -d "$CACHE_DIR" ]; then
  work_dir="$CACHE_DIR/workspace"
  if [ "${FRESH:-0}" = "1" ]; then
    rm -rf "$work_dir"
  fi
  mkdir -p "$work_dir"
else
  # No cache volume mounted; fall back to a throwaway workspace.
  work_dir="$(mktemp -d)"
fi

rm -rf "${work_dir:?}/$CONFIG_DIR"
cp -R "/work/$CONFIG_DIR" "$work_dir/$CONFIG_DIR"

cd "$work_dir"

if [ ! -d .west ]; then
  west init -l "$CONFIG_DIR"
fi

# Re-fetch Zephyr modules only when the manifest changes.
manifest_hash="$(sha256sum "$CONFIG_DIR/west.yml" | cut -d' ' -f1)"
stamp_file=".west-manifest-hash"
if [ ! -f "$stamp_file" ] || [ "$(cat "$stamp_file")" != "$manifest_hash" ]; then
  west update --fetch-opt=--filter=tree:0
  west zephyr-export
  echo "$manifest_hash" > "$stamp_file"
fi

mkdir -p "/work/$OUT_DIR"

for shield in $SHIELDS; do
  west build -s zmk/app -d "build-$shield" -b "$BOARD" -- \
    -DZMK_CONFIG="$work_dir/$CONFIG_DIR" \
    -DZMK_EXTRA_MODULES=/work \
    -DSHIELD="$shield"

  cp "build-$shield/zephyr/zmk.uf2" "/work/$OUT_DIR/$shield-$BOARD-zmk.uf2"
done
