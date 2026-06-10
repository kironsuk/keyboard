// SPDX-License-Identifier: MIT

#define DT_DRV_COMPAT zmk_behavior_battery_output

#include <zephyr/device.h>
#include <zephyr/logging/log.h>

#include <drivers/behavior.h>
#include <dt-bindings/zmk/keys.h>
#include <zmk/battery.h>
#include <zmk/behavior.h>
#include <zmk/events/keycode_state_changed.h>

LOG_MODULE_DECLARE(zmk, CONFIG_ZMK_LOG_LEVEL);

#if DT_HAS_COMPAT_STATUS_OKAY(DT_DRV_COMPAT)

static const uint32_t digit_keycodes[] = {
    N0, N1, N2, N3, N4, N5, N6, N7, N8, N9,
};

static int tap_keycode(uint32_t keycode, int64_t timestamp) {
    int err = raise_zmk_keycode_state_changed_from_encoded(keycode, true, timestamp);
    if (err) {
        return err;
    }

    return raise_zmk_keycode_state_changed_from_encoded(keycode, false, timestamp);
}

static int output_number(uint8_t value, int64_t timestamp) {
    int err;

    if (value >= 100) {
        err = tap_keycode(N1, timestamp);
        if (err) {
            return err;
        }
        err = tap_keycode(N0, timestamp);
        if (err) {
            return err;
        }
        return tap_keycode(N0, timestamp);
    }

    if (value >= 10) {
        err = tap_keycode(digit_keycodes[value / 10], timestamp);
        if (err) {
            return err;
        }
    }

    return tap_keycode(digit_keycodes[value % 10], timestamp);
}

static int on_battery_output_binding_pressed(struct zmk_behavior_binding *binding,
                                             struct zmk_behavior_binding_event event) {
    ARG_UNUSED(binding);

    uint8_t state_of_charge = zmk_battery_state_of_charge();
    int err = output_number(state_of_charge, event.timestamp);
    if (err) {
        return err;
    }

    err = tap_keycode(PRCNT, event.timestamp);
    if (err) {
        return err;
    }

    return ZMK_BEHAVIOR_OPAQUE;
}

static int on_battery_output_binding_released(struct zmk_behavior_binding *binding,
                                              struct zmk_behavior_binding_event event) {
    ARG_UNUSED(binding);
    ARG_UNUSED(event);

    return ZMK_BEHAVIOR_OPAQUE;
}

static const struct behavior_driver_api behavior_battery_output_driver_api = {
    .binding_pressed = on_battery_output_binding_pressed,
    .binding_released = on_battery_output_binding_released,
};

BEHAVIOR_DT_INST_DEFINE(0, NULL, NULL, NULL, NULL, POST_KERNEL,
                        CONFIG_KERNEL_INIT_PRIORITY_DEFAULT,
                        &behavior_battery_output_driver_api);

#endif
