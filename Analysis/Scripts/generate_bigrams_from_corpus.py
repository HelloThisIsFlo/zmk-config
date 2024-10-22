import argparse

import pyperclip

from bigrams import compute_bigrams

CORPUS_FILE = './Corpus.txt'
BIGRAM_FILE = './Bigrams.txt'


def get_args():
    parser = argparse.ArgumentParser(
        description="Bigram frequency analysis tool."
    )
    parser.add_argument(
        '-c', '--clipboard', action='store_true',
        help='Read text from clipboard instead of file'
    )
    return parser.parse_args()


def get_corpus(from_clipboard=False):
    if from_clipboard:
        return pyperclip.paste()

    with open(CORPUS_FILE, 'r') as file:
        return file.read()


def compute_bigram_freq_from_corpus(from_clipboard=False):
    corpus = get_corpus(from_clipboard)
    return compute_bigrams(corpus)


if __name__ == '__main__':
    args = get_args()

    bigram_freq = compute_bigram_freq_from_corpus(from_clipboard=args.clipboard)

    # Write the frequency of each bigram to a file
    with open(BIGRAM_FILE, 'w') as output_file:
        for bigram, freq in bigram_freq:
            output_file.write(f"{freq:.3f}% - {bigram.upper()}\n")
