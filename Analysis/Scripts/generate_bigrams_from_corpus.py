from collections import Counter
import re
import pyperclip
import argparse
import itertools

# Set up argument parser
parser = argparse.ArgumentParser(description="Bigram frequency analysis tool.")
parser.add_argument('-c', '--clipboard', action='store_true', help='Read text from clipboard instead of file')
args = parser.parse_args()

# Read the text from clipboard or file
if args.clipboard:
    corpus = pyperclip.paste()
else:
    with open('../Data/Corpus.txt', 'r') as file:
        corpus = file.read()

# Preprocess the text: lowercase and remove unwanted characters
processed_text = re.sub(r'[^a-zA-Z!]', '', corpus.lower())

# Create a list of bigrams
bigrams = [processed_text[i:i+2] for i in range(len(processed_text) - 1)]

# Prepopulate bigram_counts with all possible [a-z][a-z] bigrams
all_bigrams = [''.join(bigram) for bigram in itertools.product('abcdefghijklmnopqrstuvwxyz', repeat=2)]
bigram_counts = Counter({bigram: 0 for bigram in all_bigrams})

# Count the frequency of each bigram in the text
bigram_counts.update(bigrams)

# Calculate the total number of bigrams for frequency calculation
total_bigrams = sum(bigram_counts.values())

# Calculate the frequency of each bigram and sort them by frequency in descending order
sorted_bigrams = sorted(bigram_counts.items(), key=lambda x: x[1], reverse=True)

# Write the frequency of each bigram to a file
with open('../Data/Bigrams.txt', 'w') as output_file:
    for bigram, count in sorted_bigrams:
        frequency = count / total_bigrams * 100
        output_file.write(f"{frequency:.3f}% - {bigram.upper()}\n")
