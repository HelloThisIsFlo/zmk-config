#!/usr/bin/env python3
"""ARB-* arbitration cases (F2 on R2, F3 on R1 / R1_nohack). Templates copied, never edited."""
import shutil, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1] / "cases"  # tests/timing/cases (was zmk/app/tests/ak-truth in the fork)
R1, R1N, R2 = ROOT/"_rig_R1", ROOT/"_rig_R1_nohack", ROOT/"_rig_R2"

# ---------- F2: RM1 (1,7) + RM3 (1,9) at +12, then what ends the stall (R2, hack ON) ----------
F2 = {
 # t = 12 abs (e0.ms 11 → boot 12, gap 12): RM3 at 24 = t+12
 "ARB-F2-press40": """
/* ARB-F2 (a): RM1 t, RM3 t+12 (R10 stall), UNRELATED press LM1 (T, pos 13) at t+40 → exit (3) 'press sharing no live candidate / after all deadlines'. */
&kscan {
    events = <
        ZMK_MOCK_PRESS(1,7,11)      /* RM1 A   abs  12 = t      */
        ZMK_MOCK_PRESS(1,9,27)      /* RM3 I   abs  24 = t+12   */
        ZMK_MOCK_PRESS(1,4,100)     /* LM1 T   abs  52 = t+40   */
        ZMK_MOCK_RELEASE(1,7,10)    /* RM1 up  abs 153          */
        ZMK_MOCK_RELEASE(1,9,10)    /* RM3 up  abs 164          */
        ZMK_MOCK_RELEASE(1,4,300)   /* LM1 up  abs 175, exit 476 */
    >;
};
""",
 "ARB-F2-press14": """
/* ARB-F2 (b): RM1 t, RM3 t+12, UNRELATED press LM1 at t+14 (before the t+18 deadlines) → exit (3) 'press sharing no live candidate'. */
&kscan {
    events = <
        ZMK_MOCK_PRESS(1,7,11)      /* RM1 A   abs  12 = t      */
        ZMK_MOCK_PRESS(1,9,1)       /* RM3 I   abs  24 = t+12   */
        ZMK_MOCK_PRESS(1,4,100)     /* LM1 T   abs  26 = t+14   */
        ZMK_MOCK_RELEASE(1,7,10)    /* RM1 up  abs 127          */
        ZMK_MOCK_RELEASE(1,9,10)    /* RM3 up  abs 138          */
        ZMK_MOCK_RELEASE(1,4,300)   /* LM1 up  abs 149, exit 450 */
    >;
};
""",
 "ARB-F2-release40": """
/* ARB-F2 (c): RM1 t, RM3 t+12, no other press; RM1 released at t+40 → exit (4) 'any release'. Control for B-08 'until the first release'. */
&kscan {
    events = <
        ZMK_MOCK_PRESS(1,7,11)      /* RM1 A   abs  12 = t      */
        ZMK_MOCK_PRESS(1,9,27)      /* RM3 I   abs  24 = t+12   */
        ZMK_MOCK_RELEASE(1,7,100)   /* RM1 up  abs  52 = t+40   */
        ZMK_MOCK_RELEASE(1,9,300)   /* RM3 up  abs 153, exit 454 */
    >;
};
""",
}

# ---------- F3: replace-macro dead window endpoints (R1) ----------
REPLACE = """
/* T-21's REPLACE_CHAR_WITH_BIGRAM(L, B) verbatim (preprocessor_macros.c:12-28), nested &ak 3 B → layer 3 (akH in R1). */
/ {
    macros {
        replace_char_with_bigram_LB: replace_char_with_bigramLB {
                label = "flo-macro-replace-char-with-bigram-LB";
                compatible = "zmk,behavior-macro";
                #binding-cells = <0>;
                wait-ms = <0>;
                tap-ms = <10>;
                bindings =
                        <&macro_tap &kp BACKSPACE>,
                        <&macro_tap &kp L>,
                        <&macro_release &kp LSHFT>,
                        <&macro_release &kp RSHFT>,
                        <&macro_tap &ak 3 B>;
        };
    };
};
/ {
    keymap {
        akA {          /* 1: after A — pos 4 = replace LB, pos 3 = &bk L (as T-21) */
            bindings = <
                &trans      &bk K       &trans          &bk L
                &replace_char_with_bigram_LB  &trans  &trans  &bk O
                &trans      &trans      &trans          &bk M
            >;
        };
        akH {          /* 3: the nested &ak's layer — pos 3 = &kp Z (0x1D) so a resolution on the NEW layer is visible in HID */
            bindings = <
                &bk U       &bk T       &trans          &kp Z
                &trans      &trans      &trans          &trans
                &trans      &trans      &trans          &trans
            >;
        };
    };
};
"""
def ev(e1ms, note):
    return f"""
/* {note}
 * A-key pos 0 at abs 31 = t (R16 rung → delivered t+17, layer 1 ON t+28). E-key pos 4 at abs 62 = t+31, delivered by its own Q18 rung at abs 81 = t+50 = F (replace starts).
 * Native replace timeline: ⌫↓ F=81 · ⌫↑ + layer 1 OFF + L↓ 92 (F+11) · L↑ + ak↓ 103 (F+22) · B↓ 114 (F+33) · B↑ + layer 3 ON 125 (F+44). */
&kscan {{
    events = <
        ZMK_MOCK_PRESS(0,0,30)      /* A-key  pos 0  abs  31 = t      */
        ZMK_MOCK_PRESS(1,0,{e1ms})      /* E-key  pos 4  abs  62 = t+31   */
        ZMK_MOCK_PRESS(0,3,300)     /* D-key  pos 3  abs  {62+e1ms+1} */
        ZMK_MOCK_RELEASE(0,0,10)
        ZMK_MOCK_RELEASE(1,0,10)
        ZMK_MOCK_RELEASE(0,3,300)
    >;
}};
"""
F3 = {
 "ARB-F3-a-rung-F44": (R1,  [REPLACE, ev(50, "ARB-F3 (a) hack ON: D pressed at abs 113 = F+32, hack-only → its rung lands at 113+11+1 = 125 = F+44, same ms as the B↑/layer-3-ON tick (armed at 114). Rung armed earlier → expect rung first → D on base.")]),
 "ARB-F3-b-key-F44":  (R1N, [REPLACE, ev(62, "ARB-F3 (b) hack OFF: D (no combos) pressed at abs 125 = F+44 exactly, key-driven. Same-ms rule: timer (layer 3 ON) before key → expect D resolved on layer 3 → Z.")]),
 "ARB-F3-c-key-F5":   (R1N, [REPLACE, ev(23, "ARB-F3 (c) hack OFF: D (no combos) pressed at abs 86 = F+5, key-driven, inside [F, F+11) → expect old layer 1 still ON → &bk L.")]),
 "ARB-F3-d-key-F11":  (R1N, [REPLACE, ev(29, "ARB-F3 (d) hack OFF: D (no combos) pressed at abs 92 = F+11 exactly, key-driven. Same-ms rule: ⌫↑ tick (layer 1 OFF) before key → expect base D.")]),
}

def make(name, tpl, parts):
    d = ROOT/name
    if d.exists():
        print("exists, skipping", d); return
    shutil.copytree(tpl, d)
    with (d/"native_posix_64.keymap").open("a") as f:
        f.write(f"\n/* ===== {name} overlay (arbitration case, built from {tpl.name}) ===== */\n")
        for p in parts: f.write(p)
    print("created", d)

for n, p in F2.items(): make(n, R2, [p])
for n, (tpl, parts) in F3.items(): make(n, tpl, parts)
