
# Define the keyboard layout as a dictionary, where each key corresponds to a finger or a set of fingers.
# Layout: Naquadah
LAYOUT = {
    'x': {1}, 'w': {2}, 'm': {3}, 'p': {4}, 'k': {4},
    'c': {1}, 's': {2}, 'n': {3}, 't': {4}, 'b': {4},
    'f': {1}, 'g': {2}, 'l': {3}, 'd': {4}, 'v': {4},

    '/': {5}, '.': {5}, "-": {6}, '=': {7}, "'": {8},
    ',': {5}, 'a': {5}, 'e': {6}, 'i': {7}, 'h': {8},
    '_': {5}, 'u': {5}, 'o': {6}, 'y': {7}, 'j': {8},

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
    "U_ => UA",

    "E= => EO",
    "O' => OE", # Better than OH because of "Oh! really?"

    "GF => GS",

    "LG => LL",
    "LX => LG", # To remove SFB caused by LG => LM (aLGorithm)

    "NP => NL", # NP is rarely used in "flow", essentially mostly in "input". The rest is "un-" words

    "MT => MN",
    "NX => NM",

    "PK => PT",

    "SR => SW",
    "WX => WS",

    "YH => YI", # More comfortable than YJ => YI
    "XS => XC",
    
    "WM => LM",
    ##############################################



    ## IMPOSSIBLE Movements (on Chocofi) #########
    "SX => SF",
    "MK => MB",
    "KM => BM", # Useful because of the "MK => MB" muscle memory
    "PB => NB", # & Use alt-fingering
    ##############################################


    ## Comfort AKs ###############################
    "DV => LV",
    "DK => LK",
    "VD => VL",
    "KD => KL",
    "DB => LB",
    "BD => BL",
    "DF => DV", # To remove SFB caused by DV => LV


    "TV => NV",
    "VT => VN",

    "PG => PL", # For M->P->L, but also for regular P->L
    "BG => BL", # For M->B(k)->L
    ##############################################


    ## Repeat AKs ################################
    ## Only for pinkies & ring fingers (skipped II because it's so rare)
    "E. => EE",
    "FG => FF",
    "SD => SS",
    "BC => BB",
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


    ## NOT SIMULATED #############################
    # TODO: Find a way to take into account: hE. => hEI and hEU => hEY (or not 🤷‍♂️)
    # "hE. => hEI",
    # "hEU => hEY",
    ##############################################

]
ALT_FINGERING = [
    # "XP",
    # "XT",
    # "DV" # Actually, the alt fingering of this is LV (for comfort)
    "BT",
    # "LM"
]
IMPOSSIBLE = [ # These are impossible to actually do in one move on my keyboard (Chocofi)), so they're equivalent to SFBs
    # TODO: Migrate this to key positions instead of bigrams
    ### Left Hand
    ## Pinky
    "FS",
    "FW",
    "CW",

    ## Ring
    "GB",
    "GV",
    "SB",
    "SV",

    ## Middle
    "LB",
    "LV",
    "NB",
    "NV",
    "MB",


    ### Right Hand
    ## Pinky
    "JI",
    "J=",
    "H=",

    ## Ring
    "Y_",
    "Y,",
    "I_",
    "I,",

    ## Middle
    "O_",
    "O,",
    "E_",
    "E,",
    "-_",
]
IGNORE = [
    "II"
    # "EE",
    # "TT",
    # "NN",
    # "DD",
]