#define STRINGIFY(ARG) #ARG



#define REPLACE_CHAR_WITH_BIGRAM(BIGRAM_0, BIGRAM_1) \
        replace_char_with_bigram_##BIGRAM_0##BIGRAM_1: replace_char_with_bigram##BIGRAM_0##BIGRAM_1 { \
                label = STRINGIFY(flo-macro-replace-char-with-bigram-##BIGRAM_0##BIGRAM_1); \
                compatible = "zmk,behavior-macro"; \
                #binding-cells = <0>; \
                wait-ms = <0>; \
                tap-ms = <10>; \
                bindings = \
                        <&macro_tap &kp BACKSPACE>, \
\
                        <&macro_tap &kp BIGRAM_0>, \
\
                        <&macro_release &kp LSHFT>, \
                        <&macro_release &kp RSHFT>, \
\
                        <&macro_tap ak_##BIGRAM_1>; \
        };



#define COMBO_LAY_BASE(LAYERS, NAME, BINDINGS, KEYPOS, TIMEOUT) \
  combo_##NAME { \
    bindings = <BINDINGS>; \
    key-positions = <KEYPOS>; \
    layers = <LAYERS>; \
    timeout-ms = <TIMEOUT>; \
};

// TODO: Rename to COMBO_ANY_ADJACENT
#define COMBO_ANY_ONE_HAND(NAME, BINDINGS, KEYPOS) \
  COMBO_LAY_BASE(l_all_except_winpc_lock, NAME, BINDINGS, KEYPOS, my_combo_timeout_adjacent)
#define COMBO_ANY_NON_ADJC(NAME, BINDINGS, KEYPOS) \
  COMBO_LAY_BASE(l_all_except_winpc_lock, NAME, BINDINGS, KEYPOS, my_combo_timeout_non_adjc)
// TODO: Rename to COMBO_ANY_TWO_HNDS
#define COMBO_ANY_TWO_HAND(NAME, BINDINGS, KEYPOS) \
  COMBO_LAY_BASE(l_all_except_winpc_lock, NAME, BINDINGS, KEYPOS, my_combo_timeout_two_hnds)

// TODO: Rename to COMBO_LAY_ADJACENT
#define COMBO_LAY_ONE_HAND(LAYERS, NAME, BINDINGS, KEYPOS) \
  COMBO_LAY_BASE(LAYERS, NAME, BINDINGS, KEYPOS, my_combo_timeout_adjacent)
#define COMBO_LAY_NON_ADJC(LAYERS, NAME, BINDINGS, KEYPOS) \
  COMBO_LAY_BASE(LAYERS, NAME, BINDINGS, KEYPOS, my_combo_timeout_non_adjc)
// TODO: Rename to COMBO_LAY_TWO_HNDS
#define COMBO_LAY_TWO_HAND(LAYERS, NAME, BINDINGS, KEYPOS) \
  COMBO_LAY_BASE(LAYERS, NAME, BINDINGS, KEYPOS, my_combo_timeout_two_hnds)



#define TYPING_MACRO(NAME, KP_BINDINGS) \
ZMK_MACRO(NAME, \
        wait-ms = <10>; \
        tap-ms = <10>; \
        bindings = <KP_BINDINGS>; \
)



#define LK(NAME, TAP_BINDING, LINGER_BINDING) \
    lk_##NAME: lk_##NAME { \
        compatible = "zmk,behavior-hold-tap"; \
        label = STRINGIFY(lk_##NAME); \
        #binding-cells = <2>; \
        tapping-term-ms = <linger_term>; \
        flavor = "tap-preferred"; \
        bindings = <LINGER_BINDING>, <TAP_BINDING>; \
    };
