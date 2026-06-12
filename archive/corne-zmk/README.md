# Corne 4.1 — ZMK (future nice!nano build)

A ZMK config originally written for the "Bluetooth Corne 4.1," before a PCB photo
revealed that board is a YIVU clone running vendor QMK/Vial on an nRF51822 dongle
module — **not** a nice!nano, no UF2 bootloader. **ZMK cannot run on the keyboard
Kiron owns. Never flash these UF2s to it.** (See
[`../yivu-corne-4.1/`](../yivu-corne-4.1/) for that board.)

This config is kept intact for a *future* real nice!nano Corne. It builds today.

## Layout

This folder is a self-contained ZMK config + custom Zephyr module:

```
corne-zmk/
  config/                 ZMK user config (corne.keymap, corne.conf, west.yml)
  zephyr/module.yml       module manifest (makes this dir a Zephyr module)
  CMakeLists.txt  Kconfig  module build files
  dts/  src/              custom &batt battery-output behavior
  scripts/               local Docker build + UF2 flash helpers
  firmware/              last-built UF2s (corne_left/right-nice_nano-zmk.uf2)
  build.yaml             ZMK build matrix (template — see CI note below)
  workflows/zmk-build.yml GitHub Actions workflow (template — see CI note below)
```

The keymap has 5 layers: Base, Numbers, Symbols, Function, Navigation (no RGB
layer). The nav layer top row has Bluetooth profile controls, USB/BT output
toggle, and a custom `&batt` key that types the current battery percentage.

## Local build (works today)

```bash
bash scripts/build-zmk-corne.sh                 # both halves
SHIELDS=corne_right bash scripts/build-zmk-corne.sh   # one half
FRESH=1 bash scripts/build-zmk-corne.sh         # wipe cached Zephyr workspace
```

Outputs land in `firmware/`. The scripts mount this folder as the Zephyr extra
module and cache the workspace in the `zmk-corne-cache` Docker volume.

Flash (only ever to a real nice!nano Corne, never the YIVU board):

```bash
bash scripts/flash-zmk-uf2.sh firmware/corne_left-nice_nano-zmk.uf2
```

## CI note — GitHub Actions is intentionally disabled

ZMK's reusable cloud build (`build-user-config.yml`) requires `build.yaml` **and**
the module files at the **repo root**. They were moved here to declutter the root,
which disables the cloud build. `build.yaml` and `workflows/zmk-build.yml` are kept
as templates. To re-enable CI for a future nice!nano build, move `build.yaml`, the
module files (`CMakeLists.txt`, `Kconfig`, `zephyr/`, `dts/`, `src/`), and
`workflows/zmk-build.yml → .github/workflows/` back to the repo root, and point
`config_path` at the config dir.
