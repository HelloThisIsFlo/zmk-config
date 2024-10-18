/****************************************************/
/****                 Config                     ****/
/****************************************************/
#define linger_term 100 // Tuned ✅
#define my_tapping_term_main 500 // For the longest time, it was 130. But by separating hrm and thumb, I can afford to have the HRM longer, as I believe it's mostly the Layer that needs to be quick.
#define my_tapping_term_thumb 200 // NOT TUNED YET - UPDATE: Actually, maybe the same as the main one is OK actually, because we're using 'balanced' flavor anyway, maybe same as linger_term would be good (to keep the same intuition)
#define require_prior_idle_ms 100 // NOT USED ANYMORE!! When typing at 50wpm, there is on average 240ms between keys: 1/(50*5/60000). But that was too long, so I'm trying the same as the linger_term
#define my_ak_window 100 // I think it makes sense to have it equal to the linger term, it's the same sort of "feeling"
#define my_combo_timeout_adjacent 16
#define my_combo_timeout_non_adjc 18 // Tuned at 18ms, but sometimes missing the combo, so trying a bit higher. 20ms was too long, so trying again at 18ms
#define my_combo_timeout_two_hnds 30 // 30ms was good but sometimes it would trigger when I didn't want it to
#define sticky_key_release_timeout 1000
#define sticky_key_release_timeout_long 3000
#define action_mod_tapping_term 130 // Slightly longer than htls, to allow for rolls
#define action_lay_tapping_term 90 // See explanation in 'htls'

// Calibration Tips
// ----------------
// linger_term
//  => Try 'th' / 'tion' see if it the switch between the 2 is intuitive
//
// tapping_term
//  - To make sure it's not too long  ⇒ ???
//  - To make sure it's not too short ⇒ Try typing 'sl...'. 's' is on the pinkie so that's as slow as it gets

// See explanation in 'adaptive_keys/combos.dtsi'
#define ak_tap_time 10
#define hold_key_event_delay 11 // ak_tap_time + 1ms buffer




/****************************************************/
/****         !! TMP REMOVE / MIGRATE !!         ****/
/****************************************************/
#define TEMP_macro_tap_time 10 // TODO: Actually there is a setting to configure that already. Use it.
&mt {
    tapping-term-ms = <my_tapping_term_main>;
};



/* Uncoment to enable the experiment layer */
// #define EXPERIMENT

/* Uncoment to enable the rhodium variant */
#define RHODIUM