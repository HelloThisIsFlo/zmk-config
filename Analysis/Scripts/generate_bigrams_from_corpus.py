import pyperclip
import argparse

from bigrams import compute_bigrams


def get_corpus(from_clipboard=False):
    if from_clipboard:
        return pyperclip.paste()

    with open('../Data/Corpus.txt', 'r') as file:
        return file.read()


def get_args():
    parser = argparse.ArgumentParser(
        description="Bigram frequency analysis tool."
    )
    parser.add_argument(
        '-c', '--clipboard', action='store_true',
        help='Read text from clipboard instead of file'
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    corpus = get_corpus(from_clipboard=args.clipboard)

    bigram_freq = compute_bigrams(corpus)

    # Write the frequency of each bigram to a file
    with open('../Data/Bigrams.txt', 'w') as output_file:
        for bigram, freq in bigram_freq:
            output_file.write(f"{freq:.3f}% - {bigram.upper()}\n")
