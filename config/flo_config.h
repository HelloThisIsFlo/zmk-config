/*    KEY POSITION Numbers for Zaphod
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

#define LH0 30
#define LH1 31
#define LH2 32
#define RH0 33
#define RH1 34
#define RH2 35

#define KEYS_L LT0 LT1 LT2 LT3 LT4 LM0 LM1 LM2 LM3 LM4 LB0 LB1 LB2 LB3 LB4  // left-hand keys
#define KEYS_R RT0 RT1 RT2 RT3 RT4 RM0 RM1 RM2 RM3 RM4 RB0 RB1 RB2 RB3 RB4  // right-hand keys
#define THUMBS LH0 LH1 LH2 RH0 RH1 RH2                                      // thumb keys

// my layers
#define l_any   (-1)
#define l_alpha 0
#define l_akA   1
#define l_akB   2
#define l_akD   3
#define l_akE   4
#define l_akF   5
#define l_akG   6
#define l_akI   7
#define l_akK   8
#define l_akM   9
#define l_akO   10
#define l_akP   11
#define l_akT   12
#define l_akU   13
#define l_akW   14
#define l_akX   15
#define l_akY   16
#define l_akDOT 17
#define l_nav   18
#define l_sym   19
#define l_fn    20
#define l_num   21
#define l_cfg   22
#define APTmak  23

#define l_alpha_aks l_alpha l_akA l_akB l_akD l_akE l_akF l_akG l_akI l_akK l_akM l_akO l_akP l_akT l_akU l_akW l_akX l_akY l_akDOT

#define my_tapping_term 170


#define TEMP_macro_tap_time 10 // TODO: Actually there is a setting to configure that already. Use it.

// #define my_ak_window 200 // tmp debug, revert to 85
#define my_ak_window my_tapping_term // tmp debug, revert to 85
// #define expected_debug_ak_window 2000
#define expected_debug_ak_window my_ak_window
#define debug_ak_window (expected_debug_ak_window / 2) // This is because the ak_window is doubled in the macro. I may be able to fix this later.




// AK Window
// - Needs to be less than 225ms (min repeat term for Mac OS, larger and it'll repeat the key on some systems)
// - Ideally small to prevent other keys from being pressed before the AK action, in case the AK action is a macro (like lg, lm, lk, ...)
// TODO: Trying to fix this ⤴ at the moment (bullet #2)

// #define my_quick_tapping_term 112 // Unused atm
// #define my_ak_delay 40 // Unused atm

// #define my_combo_timeout 17
#define my_combo_timeout_one_hand 30

#define my_global_quick_tap_window 130 // Measured w/ logs, 130ms is a comfortable quick double-tap for me

&mt {
    tapping-term-ms = <my_tapping_term>;
};
&sl {
    release-after-ms = <expected_debug_ak_window>;
};
&caps_word {
    continue-list = <UNDER MINUS BSPC DEL LEFT RIGHT>;
};


#define EN_PRONOUN_COMBOS //  (I, I'm, I've I'd I'll etc)
