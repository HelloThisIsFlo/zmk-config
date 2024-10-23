
# Flo's Magic ZMK Config

## Structure
- **`config`**: Contains almost everything
  - See the `features` directory for a hierarchally organized list of features
- **`Analysis`**: Bigram analysis used to find AKs (Adaptive Keys)

## Alpha Layout: Naquadah
> **The driving question:** What if we built a layout that _required_ adaptive keys?

Naquadah is a heavy variation of HandsDown Titanium, it's so modified as a matter of fact, it's practically unrecognizable.
Its core principles are:
- Extremely low SFB: **0.082%** (See `sfb.py` in `Analysis/scripts`)
- Low Redirects (~<2%)
- IN Rolls >> OUT Rolls
- Adaptive Keys are **NOT** optional (this layout is useless without AKs)

## Concepts
_Many concepts are based on Alan's amazing work: [Hands Down Layouts](https://sites.google.com/alanreiser.com/handsdown/home/hands-down-neu)_


### Adaptive Keys (Alan Reiser)
Key behaving differently if pressed in quick successions. Virtually removes any remaining SFB
- It works with a combination of layers, macros, and behaviors
- It relies on the inner workings of the Macro queue implementation in ZMK
  - Very reliable (no missed keys in more than a year), but
    - It is sort of a hack
    - There are some very minor caveats, [combo hack](config/features/hands_down/adaptive_keys/combos.dtsi), and some issues in very specific cases when using HRMs)
    - Maintaining and debugging issues with this requires understading the inner workings of ZMK
    - Eventually I'd may implement this in ZMK directly, but for now this has worked flawlessly so I'm keeping it as is.
  - That being said, it works, and it works well (tested on burst words at 200wpm+)

<br/>

### Callum Style Mods (Callum)
After using HRMs for about a year, and tweaking everything I could tweak about it I felt it was a bottleneck. I had always looked down on Callum style mods until .... I actually tried it 😅. It's been love at first sight.
- One shot mods
- On tap, they chain and stack up
- On hold, they act as regular mods. With a special feature in ZMK to enable the mod being pressed while tap/hold is decided (useful for mouse actions)
- The mods layer (action layer) stay active for a few milliseconds after releasing
  - This is to ensure the correct tap/hold resolution
  - It guarantees we never have to think about the timing.
  - As long as the order is correct, it will work as expected
    - Correct order: 
      - Mod Layer Press -> Mod 1 -> Mod 2 -> Mod Layer Release 
      - Mod Layer Press -> Mod 1 -> Mod 2 press -> Mod Layer Release -> Mod 2 release
      - ...
    - Incorrect order:
      - Mod Layer Press -> Mod 1 -> Mod Layer Release -> Mod 2 press & release
      - ...
        
<br/>

### Other
- **Switch Device**: Switch the device and uses the associated layer
- **Linger Keys (Alan Reiser)**: Does 2 different action on short tap vs hold. Essentially a tap-hold.
- **Magic parenthesis**: One combo does 4 different types of parenthesis
  - Depends on how long it's held and whether or not it's shifted
- And probably more ...


# Layout
TODO: Fix visualization
![3x5 layout](./keymap-drawer/corne.svg)


<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>

---
#### Note to self

- Try urob's timeless HRMs (?): https://www.reddit.com/r/ErgoMechKeyboards/comments/11gejh3/lpt_try_urobs_zmk_timeless_homerow_mods_combos/  
(and other small features)
