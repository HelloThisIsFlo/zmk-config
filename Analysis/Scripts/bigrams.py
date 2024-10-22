from collections import Counter
import re
import itertools

def compute_bigrams(corpus):
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

    bigram_freq = {}
    for bigram, count in bigram_counts.items():
        frequency = count / total_bigrams * 100
        bigram_freq[bigram] = frequency

    sorted_bigram_freq = sorted(bigram_freq.items(), key=lambda x: x[1], reverse=True)
    return sorted_bigram_freq

