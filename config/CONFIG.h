/****************************************************/
/****                 Config                     ****/
/****************************************************/
#define linger_term 100 // Tuned ✅
#define my_tapping_term 120 // Now trying the tapping term to be the same as the linger term. UPDATE: It was too short, so trying 120ms
#define my_ak_window 100 // I think it makes sense to have it equal to the linger term, it's the same sort of "feeling"
#define my_combo_timeout_adjacent 15
#define my_combo_timeout_non_adjc 20 // Tuned at 18ms, but sometimes missing the combo, so trying a bit higher. 20ms was too long, so trying again at 18ms
#define my_combo_timeout_two_hnds 25 // 30ms was good but sometimes it would trigger when I didn't want it to
#define sticky_key_release_timeout 1000
#define sticky_key_release_timeout_long 3000
// Calibration Tips
// ----------------
// linger_term
//  => Try 'th' / 'tion' see if it the switch between the 2 is intuitive
//
// tapping_term
//  - To make sure it's not too long  ⇒ ???
//  - To make sure it's not too short ⇒ Try typing 'sl...'. 's' is on the pinkie so that's as slow as it gets

// See explanation in flo_combos.dtsi
#define ak_tap_time 10
#define hold_key_event_delay 15 // ak_tap_time + 5ms buffer




/****************************************************/
/****         !! TMP REMOVE / MIGRATE !!         ****/
/****************************************************/
#define TEMP_macro_tap_time 10 // TODO: Actually there is a setting to configure that already. Use it.
&mt {
    tapping-term-ms = <my_tapping_term>;
};



/* Uncoment to enable the experiment layer */
// #define EXPERIMENT