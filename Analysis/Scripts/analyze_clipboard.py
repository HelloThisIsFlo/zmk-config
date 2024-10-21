import pyperclip
import collections

def analyze_clipboard():
    # Step 1: Get clipboard content
    clipboard_content = pyperclip.paste()

    following_letters = {}
    words_with_ss = []
    for word in clipboard_content.split():
        index = 0

        while (index := word.find('ss', index)) != -1:

            if index + 2 < len(word):
                following_letter = word[index + 2]

                if following_letter in following_letters:
                    following_letters[following_letter] += 1
                else:
                    following_letters[following_letter] = 1

                words_with_ss.append(word)
            index += 2

    # Display the results in order of frequency
    following_letters = collections.OrderedDict(sorted(following_letters.items(), key=lambda x: x[1], reverse=True))
    for letter, count in following_letters.items():
        print(f"{letter}: {count}")

    print(f"Words with 'ss': {words_with_ss}")



if __name__ == '__main__':
    analyze_clipboard()
