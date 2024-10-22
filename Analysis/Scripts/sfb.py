import re
from collections import defaultdict

# Define the keyboard layout as a dictionary, where each key corresponds to a finger.
# Layout: NAQUADAH
keyboard_layout = {
    'j': 1, 'w': 2, 'm': 3, 'p': 4, 'k': 4,
    'c': 1, 's': 2, 'n': 3, 't': 4, 'x': 4,
    'f': 1, 'g': 2, 'l': 3, 'd': 4, 'v': 4,
    ',': 5, '.': 5, '\'': 6, '/': 7, ';': 8,
    '=': 5, 'a': 5, 'e': 6, 'i': 7, 'h': 8,
    '-': 5, 'u': 5, 'o': 6, 'y': 7, 'b': 8
}

# Define a function to check if a bigram is typed with the same finger.
def is_same_finger(bigram):
    if bigram[0] not in keyboard_layout or bigram[1] not in keyboard_layout:
        return False
    return keyboard_layout[bigram[0]] == keyboard_layout[bigram[1]]

# Define a function to parse the bigrams and their frequencies.
def parse_bigrams(bigrams_text):
    bigrams = defaultdict(float)
    for line in bigrams_text.strip().split('\n'):
        match = re.match(r"([0-9.]+)%\s+-\s+([A-Z]{2})", line)
        if match:
            frequency = float(match.group(1))
            bigram = match.group(2).lower()  # Convert bigram to lowercase
            bigrams[bigram] = frequency
    return bigrams

# Load the bigram list from a file
with open("../Data/Bigrams.txt", "r") as file:
    bigrams_text = file.read()

# Parse the bigrams
bigrams = parse_bigrams(bigrams_text)

# Calculate the Same Finger Bigrams (SFBs)
sfb_frequencies = defaultdict(float)

for bigram, frequency in bigrams.items():
    if is_same_finger(bigram):
        sfb_frequencies[bigram] = frequency

# Sort SFBs by percentage
sorted_sfb = sorted(sfb_frequencies.items(), key=lambda x: x[1], reverse=True)

# Print the results
print("Same Finger Bigrams (sorted by percentage):")
for bigram, frequency in sorted_sfb:
    print(f"{bigram.upper()}: {frequency:.3f}%")
