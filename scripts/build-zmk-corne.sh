#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

CONFIG_DIR="${CONFIG_DIR:-corne4.1Bluetooth}"
BOARD="${BOARD:-nice_nano}"
OUT_DIR="${OUT_DIR:-firmware/corne4.1Bluetooth}"
SHIELDS="${SHIELDS:-corne_left corne_right}"
ZMK_DOCKER_IMAGE="${ZMK_DOCKER_IMAGE:-zmkfirmware/zmk-build-arm:stable}"
ZMK_CACHE_VOLUME="${ZMK_CACHE_VOLUME:-zmk-corne-cache}"

# FRESH=1 wipes the cached Zephyr workspace before building.
docker run --rm \
  -e CONFIG_DIR="$CONFIG_DIR" \
  -e BOARD="$BOARD" \
  -e OUT_DIR="$OUT_DIR" \
  -e SHIELDS="$SHIELDS" \
  -e FRESH="${FRESH:-0}" \
  -v "$repo_root:/work" \
  -v "$ZMK_CACHE_VOLUME:/cache" \
  -w /work \
  "$ZMK_DOCKER_IMAGE" \
  bash scripts/build-zmk-corne-in-container.sh
