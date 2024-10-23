import argparse
import re
from collections import defaultdict
from operator import itemgetter

from bigrams import compute_bigrams
from generate_bigrams_from_corpus import get_corpus

# Define the keyboard layout as a dictionary, where each key corresponds to a finger or a set of fingers.
# Layout: Naquadah
LAYOUT = {
    'j': {1}, 'w': {2}, 'm': {3}, 'p': {4}, 'x': {4},
    'c': {1}, 's': {2}, 'n': {3}, 't': {4}, 'k': {4},
    'f': {1}, 'g': {2}, 'l': {3}, 'd': {4}, 'v': {4},

    ',': {5}, '.': {5}, ";": {6}, '/': {7}, "'": {8},
    '=': {5}, 'a': {5}, 'e': {6}, 'i': {7}, 'h': {8},
    '-': {5}, 'u': {5}, 'o': {6}, 'y': {7}, 'b': {8},

    'z': {2, 3},
    'q': {3, 4},
}
AK = [
    "A' => AU",
    "DF => DV",
    "DK => LK",
    "DV => LV",
    "E/ => EO",
    "GF => GS",
    "KT => KD",
    "LG => LM",
    "MW => MN",
    "NP => NL",
    "NW => NM",
    "O/ => OE",
    "PX => PT",
    "SD => SW",
    "SX => SK",
    "TK => NK",
    "TV => NV",
    "U' => UA",
    "WJ => WS",
    "YB => YI",
]
ALT_FINGERING = [
    "XP",
    "XT",
    # "DV" # Actually, the alt fingering of this is LV (for comfort)
]

MAYZNER_BIGRAMS_FILE = "../Data/ALL bigrams.html"


def get_args():
    parser = argparse.ArgumentParser(
        description="SFB analysis tool."
    )
    parser.add_argument(
        '-c', '--clipboard', action='store_true',
        help='Read text from clipboard instead of file'
    )
    parser.add_argument(
        '-m', '--use-mayzner', action='store_true',
        help='Uses Mayzner data instead of corpus'
    )
    return parser.parse_args()


def is_same_finger(bigram):
    sfb_ak_added = set()
    sfb_ak_removed = set()
    for mapping in AK:
        original, replacement = mapping.split(' => ')
        sfb_ak_removed.add(replacement.lower())
        sfb_ak_added.add(original.lower())
    removed_by_another_ak = sfb_ak_removed.intersection(sfb_ak_added)
    sfb_ak_added.difference_update(removed_by_another_ak)

    if bigram in sfb_ak_added:
        return True
    if bigram in sfb_ak_removed:
        return False

    for alt_fingering_bigram in ALT_FINGERING:
        if bigram in alt_fingering_bigram.lower():
            return False

    if bigram[0] not in LAYOUT or bigram[1] not in LAYOUT:
        return False
    if bigram[0] == bigram[1]:  # Exclude repeated letters
        return False

    # Check if the two keys share any finger
    return not LAYOUT[bigram[0]].isdisjoint(LAYOUT[bigram[1]])


def parse_bigrams(bigrams_text):
    bigrams = defaultdict(float)
    for line in bigrams_text.strip().split('\n'):
        match = re.match(r"([0-9.]+)%\s+-\s+([A-Z]{2})", line)
        if match:
            frequency = round(float(match.group(1)), 3)
            bigram = match.group(2).lower()  # Convert bigram to lowercase
            bigrams[bigram] = frequency
    return bigrams


def load_mayzner_bigrams():
    with open(MAYZNER_BIGRAMS_FILE, "r") as file:
        bigrams_text = file.read()
    return parse_bigrams(bigrams_text)


def load_bigrams(args):
    if args.use_mayzner:
        return load_mayzner_bigrams()

    corpus = get_corpus(args.clipboard)
    return compute_bigrams(corpus)


if __name__ == '__main__':
    bigram_freq = load_bigrams(get_args())

    sfb_frequencies = defaultdict(float)

    for bigram, frequency in bigram_freq.items():
        if is_same_finger(bigram):
            sfb_frequencies[bigram] = round(frequency, 3)

    sorted_sfb = sorted(
        sfb_frequencies.items(), key=itemgetter(1), reverse=False
    )

    print("Same Finger Bigrams (only >= 0.009% are shown)")
    print("----------------------------------------------")
    for bigram, frequency in sorted_sfb:
        if frequency >= 0.009:  # Hide bigrams that are less than 0.009% after rounding
            print(f"{bigram.upper()}: {frequency:.3f}%")

    sfb_sum = sum(sfb_frequencies.values())
    print()
    print(f"Total SFB: {sfb_sum:.3f}%")
    print()
