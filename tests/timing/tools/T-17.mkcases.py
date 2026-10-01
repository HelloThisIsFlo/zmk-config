#!/usr/bin/env python3
"""Create T-17 case dirs by copying rig templates and appending overlays (templates never edited)."""
import shutil, pathlib
T = pathlib.Path(__file__).resolve().parents[1] / "cases"  # tests/timing/cases (was zmk/app/tests/ak-truth in the fork)

BASE_HTLS = """
/* T-17: pos 10 (thumb, mock (2,2)) = &htls 4 LSHIFT instead of &blt_akR 5 0 (CLAIMS T-17 rig). */
/ {
    keymap {
        base {
            bindings = <
                &ak 1 A     &ak 2 B     &kp C           &kp D
                &kp E       &kp F       &kp G           &ak 3 H
                &kp I       &lk X Y     &htls 4 LSHIFT  &kp J
            >;
        };
    };
};
"""

MOD_POS3 = """
/* T-17 control: layer 4 (mod) pos 3 (mock (0,3), hack-only on base like real LM4) = &htm LCTRL LCTRL.
 * pos 3 has no combo on layer 4 (hack is layers 0-3 only), so it reaches the keymap with 0 ms combo delay. */
/ {
    keymap {
        mod {
            bindings = <
                &trans      &trans      &trans          &htm LCTRL LCTRL
                &trans      &htm LCTRL LCTRL  &trans    &trans
                &trans      &trans      &trans          &trans
            >;
        };
    };
};
"""

def events(comment, evs):
    body = "\n".join(f"        {e}" for e in evs)
    return f"\n/* {comment} */\n&kscan {{\n    events = <\n{body}\n    >;\n}};\n"

cases = {
    "T-17-a-interrupt": ("_rig_R1", [BASE_HTLS], "(a) spec: thumb t, pos 5 (F; mod: &htm LCTRL) at t+31, pos5 up t+52, thumb up t+63",
        ["ZMK_MOCK_PRESS(2,2,30)", "ZMK_MOCK_PRESS(1,1,20)", "ZMK_MOCK_RELEASE(1,1,10)", "ZMK_MOCK_RELEASE(2,2,300)"]),
    "T-17-a2-nocombo": ("_rig_R1", [BASE_HTLS, MOD_POS3], "(a2) control: same shape, interrupting key = pos 3 (no combo on layer 4)",
        ["ZMK_MOCK_PRESS(2,2,30)", "ZMK_MOCK_PRESS(0,3,20)", "ZMK_MOCK_RELEASE(0,3,10)", "ZMK_MOCK_RELEASE(2,2,300)"]),
    "T-17-a3-r2": ("_rig_R2", [], "(a3) real keymap: LH1 (pos 31, &htls 26 LSHIFT) t, LM4 (pos 10; l_mod: &htm LCTRL) t+31, LM4 up t+52, LH1 up t+63",
        ["ZMK_MOCK_PRESS(3,4,30)", "ZMK_MOCK_PRESS(1,1,20)", "ZMK_MOCK_RELEASE(1,1,10)", "ZMK_MOCK_RELEASE(3,4,300)"]),
    "T-17-b-tap": ("_rig_R1", [BASE_HTLS], "(b) spec: thumb tapped alone, up at t+51",
        ["ZMK_MOCK_PRESS(2,2,50)", "ZMK_MOCK_RELEASE(2,2,300)"]),
    "T-17-b2-tap-long": ("_rig_R1", [BASE_HTLS], "(b2) extra: (b) with a 1700 ms tail to observe the 1500 ms sticky LSHIFT expiry",
        ["ZMK_MOCK_PRESS(2,2,50)", "ZMK_MOCK_RELEASE(2,2,1700)"]),
    "T-17-c-hold120": ("_rig_R1", [BASE_HTLS], "(c) spec: thumb held alone 120 ms (up at t+121)",
        ["ZMK_MOCK_PRESS(2,2,120)", "ZMK_MOCK_RELEASE(2,2,300)"]),
    "T-17-d-buffered": ("_rig_R1", [BASE_HTLS, MOD_POS3], "(d) extra: thumb t, pos 3 at t+6 (both buffered by the hack, flushed together at t+12)",
        ["ZMK_MOCK_PRESS(2,2,5)", "ZMK_MOCK_PRESS(0,3,40)", "ZMK_MOCK_RELEASE(0,3,10)", "ZMK_MOCK_RELEASE(2,2,300)"]),
}

for name, (tmpl, overlays, comment, evs) in cases.items():
    d = T / name
    if d.exists():
        print("exists, skipping", d); continue
    shutil.copytree(T / tmpl, d)
    km = d / "native_posix_64.keymap"
    with km.open("a") as f:
        for o in overlays:
            f.write(o)
        f.write(events(comment, evs))
    print("created", d)
