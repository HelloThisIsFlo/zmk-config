/*    KEY POSITION Numbers for Chocofi
╭────────────────────╮ ╭────────────────────╮
│  0   1   2   3   4 │ │  5   6   7   8   9 │
│ 10  11  12  13  14 │ │ 15  16  17  18  19 |
| 20  21  22  23  24 │ │ 25  26  27  28  29 |
╰───────╮ 30  31  32 | | 33  34  35 ╭───────╯
        ╰────────────╯ ╰────────────╯
*/
/*    KEY POSITION Names
╭─────────────────────╮ ╭─────────────────────╮
│ LT4 LT3 LT2 LT1 LT0 │ │ RT0 RT1 RT2 RT3 RT4 │
│ LM4 LM3 LM2 LM1 LM0 │ │ RM0 RM1 RM2 RM3 RM4 │
│ LB4 LB3 LB2 LB1 LB0 │ │ RB0 RB1 RB2 RB3 RB4 |
╰───────╮ LH2 LH1 LH0 | | RH0 RH1 RH2 ╭───────╯
        ╰─────────────╯ ╰────────────╯
*/

/****************************************************/
/****              Key Positions                 ****/
/****************************************************/
#define LT0 4
#define LT1 3
#define LT2 2
#define LT3 1
#define LT4 0
#define RT0 5
#define RT1 6
#define RT2 7
#define RT3 8
#define RT4 9

#define LM0 14
#define LM1 13
#define LM2 12
#define LM3 11
#define LM4 10
#define RM0 15
#define RM1 16
#define RM2 17
#define RM3 18
#define RM4 19

#define LB0 24
#define LB1 23
#define LB2 22
#define LB3 21
#define LB4 20
#define RB0 25
#define RB1 26
#define RB2 27
#define RB3 28
#define RB4 29

#define LH0 32
#define LH1 31
#define LH2 30
#define RH0 33
#define RH1 34
#define RH2 35

#define KEYS_L LT0 LT1 LT2 LT3 LT4 LM0 LM1 LM2 LM3 LM4 LB0 LB1 LB2 LB3 LB4  // left-hand keys
#define KEYS_R RT0 RT1 RT2 RT3 RT4 RM0 RM1 RM2 RM3 RM4 RB0 RB1 RB2 RB3 RB4  // right-hand keys
#define THUMBS LH0 LH1 LH2 RH0 RH1 RH2                                      // thumb keys





/****************************************************/
/****                  Layers                    ****/
/****************************************************/
/* IMPORTANT NOTE

Max layer length is 32 (so max layer idx is 31). 


This is because the active layer is stored in a 'uint32_t' bit array. 
See: keymap.c::set_layer_state (92)

    WRITE_BIT(_zmk_keymap_layer_state, layer, state);

Here, `_zmk_keymap_layer_state` is the 'uint32_t' bit array.
 */
#define l_any    (-1)
#define l_alpha  0
#define l_winpc  1
#define l_akA    2
#define l_akB    3
#define l_akC    4
#define l_akD    5
#define l_akE    6
#define l_akF    7
#define l_akG    8
#define l_akI    9
#define l_akJ    10
#define l_akK    11
#define l_akL    12
#define l_akM    13
#define l_akN    14
#define l_akO    15
#define l_akP    16
#define l_akS    17
#define l_akT    18
#define l_akU    19
#define l_akW    20
#define l_akX    21
#define l_akY    22
#define l_akDOT  23
#define l_nav    24
#define l_sym    25
#define l_fn     26
#define l_num    27
#define l_cfg    28
#define l_lock   30

#define l_alpha_aks l_alpha l_winpc l_akA l_akB l_akC l_akD l_akE l_akF l_akG l_akI l_akJ l_akK l_akL l_akM l_akN l_akO l_akP l_akS l_akT l_akU l_akW l_akX l_akY l_akDOT
#define l_all_except_lock l_alpha_aks l_nav l_sym l_fn l_num l_cfg l_winpc





/****************************************************/
/****               Adaptive Keys                ****/
/****************************************************/
#define ak_A &ak l_akA A
#define ak_B &ak l_akB B
#define ak_C &ak l_akC C
#define ak_D &ak l_akD D
#define ak_E &ak l_akE E
#define ak_F &ak l_akF F
#define ak_G &ak l_akG G
#define ak_H &ak l_akH H
#define ak_I &ak l_akI I
#define ak_J &ak l_akJ J
#define ak_K &ak l_akK K
#define ak_L &ak l_akL L
#define ak_M &ak l_akM M
#define ak_N &ak l_akN N
#define ak_O &ak l_akO O
#define ak_P &ak l_akP P
#define ak_Q &ak l_akQ Q
#define ak_R &ak l_akR R
#define ak_S &ak l_akS S
#define ak_T &ak l_akT T
#define ak_U &ak l_akU U
#define ak_V &ak l_akV V
#define ak_W &ak l_akW W
#define ak_X &ak l_akX X
#define ak_Y &ak l_akY Y
#define ak_Z &ak l_akZ Z
#define ak_DOT &ak l_akDOT DOT





/****************************************************/
/****                 Config                     ****/
/****************************************************/
#define linger_term 100 // Tuned ✅
#define my_tapping_term 150
#define my_ak_window 220
#define my_combo_timeout_one_hand 20 // Tuned at 18ms, but sometimes missing the combo, so trying a bit higher
#define my_combo_timeout_two_hands 40
#define my_global_quick_tap_window 130 // Measured w/ logs, 130ms is a comfortable quick double-tap for me
#define sticky_key_release_timeout 750
// Calibration Tips
// ----------------
// linger_term
//  => Try 'th' / 'tion' see if it the switch between the 2 is intuitive
//
// tapping_term
//  - To make sure it's not too long  ⇒ ???
//  - To make sure it's not too short ⇒ Try typing 'sl...'. 's' is on the pinkie so that's as slow as it gets





/****************************************************/
/****             Behavior Config                ****/
/****************************************************/
&caps_word {
    continue-list = <UNDER MINUS BSPC DEL LEFT RIGHT>;
};

&sk {
    release-after-ms = <sticky_key_release_timeout>;
    quick-release;
};





/****************************************************/
/****         !! TMP REMOVE / MIGRATE !!         ****/
/****************************************************/
#define TEMP_macro_tap_time 10 // TODO: Actually there is a setting to configure that already. Use it.
&mt {
    tapping-term-ms = <my_tapping_term>;
};
