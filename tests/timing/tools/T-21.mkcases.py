#!/usr/bin/env python3
"""Generate T-21 case directories from _rig_R1 (template is copied, never edited)."""
import shutil, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1] / "cases"  # tests/timing/cases (was zmk/app/tests/ak-truth in the fork)
TPL = ROOT / "_rig_R1"

REPLACE = """
/* T-21 — REPLACE_CHAR_WITH_BIGRAM(L, B) expanded verbatim from Flo's config
 * (preprocessor_macros.c:12-28, TEMP_macro_tap_time = 10, ak_B = &ak l_akB B = &ak 3 B).
 * NOTE: in R1 layer 3 is akH (B's own AK layer is 2); kept verbatim, irrelevant here
 * because no key is pressed after the macro finishes. */
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
"""

def akA(pos3):
    return f"""
/ {{
    keymap {{
        akA {{          /* 1: after A — T-21: pos 4 = replace LB, pos 3 = {pos3} */
            bindings = <
                &trans      &bk K       &trans          {pos3}
                &replace_char_with_bigram_LB  &trans  &trans  &bk O
                &trans      &trans      &trans          &bk M
            >;
        }};
    }};
}};
"""

def base(pos3):
    return f"""
/ {{
    keymap {{
        base {{          /* 0 — T-21: pos 3 = {pos3} */
            bindings = <
                &ak 1 A     &ak 2 B     &kp C           {pos3}
                &kp E       &kp F       &kp G           &ak 3 H
                &kp I       &lk X Y     &blt_akR 5 0    &kp J
            >;
        }};
    }};
}};
"""

EV_SPEC = """
&kscan {
    events = <
        ZMK_MOCK_PRESS(0,0,30)      /* A-key  pos 0  abs  31 = t      */
        ZMK_MOCK_PRESS(1,0,15)      /* E-key  pos 4  abs  62 = t+31   */
        ZMK_MOCK_PRESS(0,3,300)     /* D-key  pos 3  abs  78 = t+47   */
        ZMK_MOCK_RELEASE(0,0,10)    /* A up          abs 379 = t+348  */
        ZMK_MOCK_RELEASE(1,0,10)    /* E up          abs 390 = t+359  */
        ZMK_MOCK_RELEASE(0,3,300)   /* D up          abs 401 = t+370, exit abs 702 */
    >;
};
"""

EV_LATE = """
&kscan {
    events = <
        ZMK_MOCK_PRESS(0,0,30)      /* A-key  pos 0  abs  31 = t      */
        ZMK_MOCK_PRESS(1,0,33)      /* E-key  pos 4  abs  62 = t+31 (delivered by its own Q18 timer at t+50) */
        ZMK_MOCK_PRESS(0,3,300)     /* D-key  pos 3  abs  96 = t+65   */
        ZMK_MOCK_RELEASE(0,0,10)    /* A up          abs 397 = t+366  */
        ZMK_MOCK_RELEASE(1,0,10)    /* E up          abs 408 = t+377  */
        ZMK_MOCK_RELEASE(0,3,300)   /* D up          abs 419 = t+388, exit abs 720 */
    >;
};
"""

EV_WIN = """
&kscan {
    events = <
        ZMK_MOCK_PRESS(0,0,30)      /* A-key  pos 0  abs  31 = t      */
        ZMK_MOCK_PRESS(1,0,5)       /* E-key  pos 4  abs  62 = t+31   */
        ZMK_MOCK_PRESS(0,3,300)     /* D-key  pos 3  abs  68 = t+37 (E+6, inside E's hack window) */
        ZMK_MOCK_RELEASE(0,0,10)    /* A up          abs 369 = t+338  */
        ZMK_MOCK_RELEASE(1,0,10)    /* E up          abs 380 = t+349  */
        ZMK_MOCK_RELEASE(0,3,300)   /* D up          abs 391 = t+360, exit abs 692 */
    >;
};
"""

CASES = {
    # spec, two builds: follower on layer 1 pos 3 = &bk L (template) vs &kp L
    "T-21-a-spec-bk":   [REPLACE, akA("&bk L"), EV_SPEC],
    "T-21-b-spec-kp":   [REPLACE, akA("&kp L"), EV_SPEC],
    # spec timing, base pos 3 buffered (&bk D) — the binding the follower actually resolves to
    "T-21-c-spec-baseBk": [REPLACE, akA("&bk L"), base("&bk D"), EV_SPEC],
    # late follower: E delivered by its own timer, D delivered after the nested &ak expanded
    "T-21-d-late-kp":   [REPLACE, akA("&bk L"), EV_LATE],
    "T-21-e-late-bk":   [REPLACE, akA("&bk L"), base("&bk D"), EV_LATE],
    # in-window follower: D pressed E+6, bypass → resolves on layer 1 in E's dispatch
    "T-21-f-win-bk":    [REPLACE, akA("&bk L"), EV_WIN],
    "T-21-g-win-kp":    [REPLACE, akA("&kp L"), EV_WIN],
    "T-21-h-win-kpM":   [REPLACE, akA("&kp M"), EV_WIN],
}

for name, parts in CASES.items():
    d = ROOT / name
    if d.exists():
        print("exists, skipping", d)
        continue
    shutil.copytree(TPL, d)
    km = d / "native_posix_64.keymap"
    with km.open("a") as f:
        f.write("\n/* ===== T-21 case " + name + " overlay ===== */\n")
        for p in parts:
            f.write(p)
    print("created", d)
