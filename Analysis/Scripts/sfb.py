import argparse
import re
from collections import defaultdict
from operator import itemgetter

from bigrams import compute_bigrams
from generate_bigrams_from_corpus import get_corpus

from layout_naquadah import LAYOUT, AK, ALT_FINGERING, IMPOSSIBLE, COMFORTABLE_REPEAT


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
    parser.add_argument(
        '-r', '--include-repeat', action='store_true',
        help='Includes SFB due to letter repeated twice'
    )
    return parser.parse_args()


def is_same_finger(bigram, include_repeat=False):
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

    for impossible_bigram in IMPOSSIBLE:
        if bigram in impossible_bigram.lower():
            return True

    if bigram[0] not in LAYOUT or bigram[1] not in LAYOUT:
        return False
    if bigram[0] == bigram[1]:
        if not include_repeat:
            return False
        if bigram.upper() in COMFORTABLE_REPEAT:
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
    args = get_args()
    bigram_freq = load_bigrams(get_args())

    sfb_frequencies = defaultdict(float)

    for bigram, frequency in bigram_freq.items():
        if is_same_finger(bigram, args.include_repeat):
            sfb_frequencies[bigram] = round(frequency, 3)

    sorted_sfb = sorted(
        sfb_frequencies.items(), key=itemgetter(1), reverse=False
    )

    cutoff_frequency = 0.009
    cutoff_frequency = 0.007
    cutoff_frequency = 0.005
    # cutoff_frequency = 0
    print(f"Same Finger Bigrams (only >= {cutoff_frequency:.3f}% are shown)")
    print("----------------------------------------------")
    for bigram, frequency in sorted_sfb:
        if frequency >= cutoff_frequency:  # Hide bigrams that are less than 0.009% after rounding
            print(f"{bigram.upper()}: {frequency:.3f}%")

    sfb_sum = sum(sfb_frequencies.values())
    print()
    print(f"Total SFB: {sfb_sum:.3f}%")
    print()
