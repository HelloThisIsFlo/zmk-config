import argparse
import re
from collections import defaultdict

from bigrams import compute_bigrams
from generate_bigrams_from_corpus import get_corpus

# Define the keyboard layout as a dictionary, where each key corresponds to a finger.
# Layout: Naquadah
LAYOUT = {
    'j': 1, 'w': 2, 'm': 3, 'p': 4, 'k': 4,
    'c': 1, 's': 2, 'n': 3, 't': 4, 'x': 4,
    'f': 1, 'g': 2, 'l': 3, 'd': 4, 'v': 4,

    ',': 5, '.': 5, "'": 6, '/': 7, ';': 8,
    '=': 5, 'a': 5, 'e': 6, 'i': 7, 'h': 8,
    '-': 5, 'u': 5, 'o': 6, 'y': 7, 'b': 8
}

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
    if bigram[0] not in LAYOUT or bigram[1] not in LAYOUT:
        return False
    return LAYOUT[bigram[0]] == LAYOUT[bigram[1]]


def parse_bigrams(bigrams_text):
    bigrams = defaultdict(float)
    for line in bigrams_text.strip().split('\n'):
        match = re.match(r"([0-9.]+)%\s+-\s+([A-Z]{2})", line)
        if match:
            frequency = float(match.group(1))
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
            sfb_frequencies[bigram] = frequency

    sorted_sfb = sorted(sfb_frequencies.items(), key=lambda x: x[1], reverse=True)

    print("Same Finger Bigrams (sorted by percentage):")
    for bigram, frequency in sorted_sfb:
        print(f"{bigram.upper()}: {frequency:.3f}%")
