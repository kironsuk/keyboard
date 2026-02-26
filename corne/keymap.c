#include QMK_KEYBOARD_H

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
	[0] = LAYOUT_split_3x6_3(KC_TAB, KC_Q, KC_W, KC_E, KC_R, KC_T, KC_Y, KC_U, KC_I, KC_O, KC_P, KC_BSLS, KC_ESC, MT(MOD_LSFT, KC_A), MT(MOD_LCTL, KC_S), MT(MOD_LALT, KC_D), MT(MOD_LGUI, KC_F), KC_G, KC_H, MT(MOD_RGUI, KC_J), MT(MOD_RALT, KC_K), MT(MOD_RCTL, KC_L), MT(MOD_RSFT, KC_SEMICOLON), KC_QUOT, KC_LSFT, KC_Z, KC_X, KC_C, KC_V, KC_B, KC_N, KC_M, KC_COMM, KC_DOT, KC_SLSH, KC_RSFT, MO(1), MO(2), KC_BSPC, KC_ENT, KC_SPC, MO(4)),
	[1] = LAYOUT_split_3x6_3(KC_TRNS, KC_1, KC_2, KC_3, KC_4, KC_5, KC_6, KC_7, KC_8, KC_9, KC_0, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, MO(3)),
	[2] = LAYOUT_split_3x6_3(KC_TRNS, KC_GRV, KC_PIPE, KC_MINS, KC_NO, KC_NO, KC_NO, KC_PLUS, KC_SLSH, KC_LBRC, KC_RBRC, KC_NO, KC_TRNS, MT(MOD_LSFT, KC_EXCLAIM), MT(MOD_LCTL, KC_AT), MT(MOD_LALT, KC_HASH), MT(MOD_LGUI, KC_DOLLAR), KC_PERC, KC_CIRC, MT(MOD_RGUI, KC_AMPERSAND), MT(MOD_RALT, KC_ASTERISK), MT(MOD_RCTL, KC_LEFT_PAREN), MT(MOD_RSFT, KC_RIGHT_PAREN), KC_QUES, KC_TRNS, KC_TILD, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_UNDS, KC_EQL, KC_LCBR, KC_RCBR, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS),
	[3] = LAYOUT_split_3x6_3(KC_TRNS, KC_F1, KC_F2, KC_F3, KC_F4, KC_F5, KC_F6, KC_F7, KC_F8, KC_F9, KC_F10, DF(5), KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_F11, KC_F12, KC_F13, KC_F14, KC_F15, KC_F16, KC_F17, KC_F18, KC_F19, KC_F20, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS),
	[4] = LAYOUT_split_3x6_3(KC_TRNS, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_LEFT, KC_DOWN, KC_UP, KC_RGHT, KC_TRNS, KC_TRNS, KC_TRNS, KC_UNDO, KC_NO, KC_CUT, KC_COPY, KC_PSTE, KC_HOME, KC_PGDN, KC_PGUP, KC_END, KC_NO, KC_TRNS, MO(3), KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS, KC_TRNS),
	[5] = LAYOUT_split_3x6_3(QK_BOOT, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_TRNS, RGB_TOG, RGB_MOD, RGB_HUI, RGB_SAI, RGB_VAI, RGB_SPI, RGB_M_P, RGB_M_B, RGB_M_R, RGB_M_K, RGB_M_G, RGB_M_T, KC_NO, RGB_RMOD, RGB_HUD, RGB_SAD, RGB_VAD, RGB_SPD, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, KC_NO, DF(0), DF(0), DF(0), KC_NO, KC_NO, KC_NO)
};

// Per-layer hue values (only hue changes per layer; brightness/saturation/effects persist)
static const uint8_t layer_hues[] = {
    128,  // Layer 0: Cyan
    170,  // Layer 1: Blue
    213,  // Layer 2: Magenta
    85,   // Layer 3: Green
    28,   // Layer 4: Orange
    0,    // Layer 5: Red
};

void set_layer_color(uint8_t layer) {
    rgblight_sethsv_noeeprom(layer_hues[layer], rgblight_get_sat(), rgblight_get_val());
}

void keyboard_post_init_user(void) {
    rgblight_sethsv(128, 255, 120); // Start with Cyan, full sat, default brightness
}

layer_state_t default_layer_state_set_user(layer_state_t state) {
    set_layer_color(get_highest_layer(state));
    return state;
}

layer_state_t layer_state_set_user(layer_state_t state) {
    uint8_t layer = get_highest_layer(state | default_layer_state);
    set_layer_color(layer);
    return state;
}
