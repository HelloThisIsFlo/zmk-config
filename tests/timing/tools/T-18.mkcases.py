#!/usr/bin/env python3
"""Create T-18 case dirs by copying rig templates and appending overlays (templates never edited)."""
import shutil, pathlib
T = pathlib.Path(__file__).resolve().parents[1] / "cases"  # tests/timing/cases (was zmk/app/tests/ak-truth in the fork)

BASE_HTLS = """
/* T-18: pos 10 (thumb, mock (2,2)) = &htls 4 LSHIFT instead of &blt_akR 5 0 (CLAIMS T-17/T-18 rig). */
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

MOD_POS3_CTRL = """
/* T-18 control: layer 4 (mod) pos 3 (mock (0,3), hack-only on base like real LM4) = &htm LCTRL LCTRL.
 * pos 3 has no combo candidate while layer 4 is the highest layer (hack is layers 0-3 only). */
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

MOD_POS3_SHIFT = """
/* T-18 shift: layer 4 (mod) pos 3 = &htm LSHIFT LSHIFT (real l_mod LM1/RM1 shape: tap -> &skm LSHIFT sticky 1500,
 * ignore-modifiers). pos 3 has no combo candidate on layer 4, so the tap reaches the keymap at once. */
/ {
    keymap {
        mod {
            bindings = <
                &trans      &trans      &trans          &htm LSHIFT LSHIFT
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
    "T-18-a-spec": ("_rig_R1", [BASE_HTLS],
        "(a) spec: thumb t..t+121, pos 1 (&ak 2 B) down t+262 up t+273",
        ["ZMK_MOCK_PRESS(2,2,120)", "ZMK_MOCK_RELEASE(2,2,140)", "ZMK_MOCK_PRESS(0,1,10)", "ZMK_MOCK_RELEASE(0,1,300)"]),
    "T-18-a2-bheld": ("_rig_R1", [BASE_HTLS],
        "(a2) extra: as (a) but pos 1 held 30 (up t+293) so the hack timer, not the key-up, delivers it",
        ["ZMK_MOCK_PRESS(2,2,120)", "ZMK_MOCK_RELEASE(2,2,140)", "ZMK_MOCK_PRESS(0,1,30)", "ZMK_MOCK_RELEASE(0,1,300)"]),
    "T-18-b-htm240": ("_rig_R1", [BASE_HTLS],
        "(b) spec variant: thumb t..t+121, pos 5 (base &kp F / mod &htm LCTRL) down t+240 up t+270",
        ["ZMK_MOCK_PRESS(2,2,120)", "ZMK_MOCK_RELEASE(2,2,118)", "ZMK_MOCK_PRESS(1,1,29)", "ZMK_MOCK_RELEASE(1,1,300)"]),
    "T-18-b2-htm240-nocombo": ("_rig_R1", [BASE_HTLS, MOD_POS3_CTRL],
        "(b2) control: as (b) but the htm is on pos 3 (no combo on layer 4), down t+240 up t+270",
        ["ZMK_MOCK_PRESS(2,2,120)", "ZMK_MOCK_RELEASE(2,2,118)", "ZMK_MOCK_PRESS(0,3,29)", "ZMK_MOCK_RELEASE(0,3,300)"]),
    "T-18-b3-htm240-short": ("_rig_R1", [BASE_HTLS],
        "(b3) extra: as (b) but a 10 ms tap (pos 5 down t+240 up t+250, before layer OFF)",
        ["ZMK_MOCK_PRESS(2,2,120)", "ZMK_MOCK_RELEASE(2,2,118)", "ZMK_MOCK_PRESS(1,1,9)", "ZMK_MOCK_RELEASE(1,1,300)"]),
    "T-18-c-F262": ("_rig_R1", [BASE_HTLS],
        "(c) spec variant: thumb t..t+121, pos 5 (&kp F) down t+262 up t+293, no shift",
        ["ZMK_MOCK_PRESS(2,2,120)", "ZMK_MOCK_RELEASE(2,2,140)", "ZMK_MOCK_PRESS(1,1,30)", "ZMK_MOCK_RELEASE(1,1,300)"]),
    "T-18-d-shift-F262": ("_rig_R1", [BASE_HTLS, MOD_POS3_SHIFT],
        "(d) spec variant: thumb t..t+121, shift tap (layer 4 pos 3 &htm LSHIFT) t+100..t+115, pos 5 (&kp F) t+262..t+293",
        ["ZMK_MOCK_PRESS(2,2,99)", "ZMK_MOCK_PRESS(0,3,14)", "ZMK_MOCK_RELEASE(0,3,5)", "ZMK_MOCK_RELEASE(2,2,140)",
         "ZMK_MOCK_PRESS(1,1,30)", "ZMK_MOCK_RELEASE(1,1,300)"]),
    "T-18-e-shift-B262": ("_rig_R1", [BASE_HTLS, MOD_POS3_SHIFT],
        "(e) extra: as (d) but the late key is pos 1 (&ak 2 B, parked by the queue) t+262..t+293",
        ["ZMK_MOCK_PRESS(2,2,99)", "ZMK_MOCK_PRESS(0,3,14)", "ZMK_MOCK_RELEASE(0,3,5)", "ZMK_MOCK_RELEASE(2,2,140)",
         "ZMK_MOCK_PRESS(0,1,30)", "ZMK_MOCK_RELEASE(0,1,300)"]),
    "T-18-f-r2-page": ("_rig_R2", [],
        "(f) real keymap, page late scenario: LH1 (&htls 26 LSHIFT) t..t+121, LM1 (l_mod &htm LSHIFT) t+100..t+115, RM1 (&ak A) t+262..t+293",
        ["ZMK_MOCK_PRESS(3,4,99)", "ZMK_MOCK_PRESS(1,4,14)", "ZMK_MOCK_RELEASE(1,4,5)", "ZMK_MOCK_RELEASE(3,4,140)",
         "ZMK_MOCK_PRESS(1,7,30)", "ZMK_MOCK_RELEASE(1,7,300)"]),
    "T-18-g-r2-lm1-240": ("_rig_R2", [],
        "(g) real keymap extra: LH1 (&htls 26 LSHIFT) t..t+121, LM1 (l_mod &htm LSHIFT / base &ak 19 T, in entr) t+240..t+270",
        ["ZMK_MOCK_PRESS(3,4,120)", "ZMK_MOCK_RELEASE(3,4,118)", "ZMK_MOCK_PRESS(1,4,29)", "ZMK_MOCK_RELEASE(1,4,300)"]),
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
