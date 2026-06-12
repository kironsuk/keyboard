# YIVU Corne 4.1 Wireless (Vial)

The 46-key wireless Corne clone Kiron owns (Amazon ASIN B0FZGV71WM). It runs
vendor QMK/Vial firmware on its main MCU, with a soldered TNT-BT_M V2 module
(nRF51822) providing a proprietary 2.4GHz dongle link. It is **not** a nice!nano,
has **no UF2 bootloader**, and **cannot run ZMK**.

The layout is managed **live via Vial** — there is no firmware to flash from this
repo. The `.vil` files here are backups / source of truth for that layout:

- `kiron-layout.vil` — corrected source of truth. Load with the Vial web app, or
  the `vitaly` CLI: `vitaly load -f kiron-layout.vil`.
- `Initial.vil` — Kiron's first manual export. Had bottom-row-mod and
  symbols-layer bugs; superseded by `kiron-layout.vil`. Kept for history.

## Bluetooth status (concluded 2026-06-09)

The keyboard has **no Bluetooth support as shipped** — wireless is the proprietary
2.4GHz dongle only (wired USB-C also works). Evidence: the Vial definition pulled
from the device over raw HID (VID 0x55D4 "Pilot", PID 0x0461 "W-CORNE") contains
no custom BT keycodes, and BLE scans across power cycles showed the keyboard never
advertises.

For true Bluetooth: ask YIVU support about BT firmware for the TNT-BT_M V2 module,
or build a real nice!nano ZMK Corne (config kept in [`../corne-zmk/`](../corne-zmk/)).
