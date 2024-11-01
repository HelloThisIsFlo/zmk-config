# Define the keyboard layout as a dictionary, where each key corresponds to a finger or a set of fingers.
# Layout: Naquadah
LAYOUT = {
    'j': {1}, 'w': {2}, 'm': {3}, 'p': {4}, 'x': {4},
    'c': {1}, 's': {2}, 'n': {3}, 't': {4}, 'k': {4},
    'f': {1}, 'g': {2}, 'l': {3}, 'd': {4}, 'v': {4},

    '=': {5}, '.': {5}, ";": {6}, '/': {7}, "'": {8},
    ',': {5}, 'a': {5}, 'e': {6}, 'i': {7}, 'h': {8},
    '-': {5}, 'u': {5}, 'o': {6}, 'y': {7}, 'b': {8},

    'r': {9},

    'z': {2, 3},
    'q': {3, 4},
}

"""
Notes on some bigrams/trigrams:
- NPL: Not very common, mostly for un- words (unplug, unplanned, ...), and other words like "downplay"
"""

# TODO: Remember to update AKs w/ symbols if symbols change position in the layout
AK = [
    ## SFB AKs ###################################
    "A, => AU",
    "U- => UA",

    "E/ => EO",
    "O' => OE", # Better than OH because of "Oh! really?"

    "GF => GS",

    "LG => LL",
    "LX => LM",
    "LJ => LG", # To remove SFB caused by LG => LM (aLGorithm)

    "NP => NL", # NP is rarely used in "flow", essentially mostly in "input". The rest is "un-" words

    "MT => MN",
    "NX => NM", # To remove SFB caused by NP => NL (iNPut)

    "PX => PT",

    "SR => SW",
    "WJ => WS",

    "YH => YI", # More comfortable than YB => YI
    "IH => IB", # Definitely better than YB => IB (because of maYBe)
    "B; => BI",
    ##############################################



    ## IMPOSSIBLE Movements (on Chocofi) #########
    "SJ => SF",
    ##############################################


    ## Comfort AKs ###############################
    "DV => LV",
    "DK => LK",
    "DF => DV", # To remove SFB caused by DV => LV

    "TK => NK",
    "KT => KN",
    "TV => NV",

    "SX => SK",
    "PG => PL", # For M->P->L, but also for regular P->L
    ##############################################


    ## Repeat AKs ################################
    ## Only for pinkies & ring fingers (skipped II because it's so rare)
    "E. => EE",
    "FG => FF",
    "SD => SS",
    "YB => BB", # It's ok to use YB because YB is most often surrounded by vowels, so anyway I have to break the rhythm a bit (e.g. "maYBe", "keYBoard", "plaYBook", "plaYBack", ...)
    "CG => CC", # CD would technically work, but it would make using the terminal a nightmare
    "GC => GG",
    "PW => PP", # Not using PM because of 6PM, 7PM, ...
    "MW => MM",
    "NW => NN",
    "O. => OO", # May need to increase the timing of adaptive keys to make this one more reliable
    "RX => RR",
    "TG => TT",
    "DC => DD",
    ##############################################

    # TODO: Find a way to take into account: hE. => hEI and hEU => hEY (or not 🤷‍♂️)
]
ALT_FINGERING = [
    "XP",
    "XT",
    # "DV" # Actually, the alt fingering of this is LV (for comfort)
]
IMPOSSIBLE = [ # These are impossible to actually do in one move on my keyboard (Chocofi)), so they're equivalent to SFBs
    # TODO: Migrate this to key positions instead of bigrams
    "FS",
    "SF",
    "FW",
    "WF",

    "CW",
    "WC",

    "BI",
    "IB",
    "B/",
    "/B",

    "H/",
    "/H",
]
COMFORTABLE_REPEAT = [
    # "EE",
    # "TT",
    # "NN",
    # "DD",
]