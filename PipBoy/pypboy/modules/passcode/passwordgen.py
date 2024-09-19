# Format a file of English words so they are valid data
# for "password" options in the RobCo terminal game
import random

with open('./pypboy/modules/passcode/google-10000-english-usa-no-swears.txt', 'r') as file:

    raw_text = file.readlines()
    clean_text = ['secretsecretwords'] # Add one 17 character string to this set :)

    for lines, word in enumerate(raw_text):
        clean_text.append(raw_text[lines].rstrip('\n'))

word_groups = {} # Holds the block of indices and entries that follow
sorted_text = []


def arrange_words_by_length(unsorted_text):

    global sorted_text
    sorted_text = sorted(unsorted_text, key=len)
    last_word_length = 0

    # Keep track of the blocks of words and where they start
    for idx, words in enumerate(sorted_text):

        # Passwords in the terminal game are ALLCAPS
        sorted_text[idx] = words.upper()
        word_length = len(words)

        if word_length > last_word_length:
            word_groups[word_length] = [idx, 0]
            last_word_length = word_length

        # Figure out the number of words in each group
        # This dict is naturally ordered, so this works ok through word length of 16
        for group in range(1, len(word_groups)-1):
            word_groups[group][1] = word_groups[group+1][0] - word_groups[group][0]
"""
    for key in word_groups:
        print('Words of length {0}, '
              'have {1} entries at index {2}'.format(str(key),
                                                     str(word_groups[key][1]),
                                                     str(word_groups[key][0])))
"""

def get_list_of_words(num_words, length_of_words):
    # For the game it's best that words have a length between 4 and 12,
    # but I'm leaving the option for any choice.
    # Words of length 15 or more are impractical though

    arrange_words_by_length(clean_text)
    random_list = []
    word_block_index = word_groups[length_of_words][0]
    word_block_size = word_groups[length_of_words][1]
    rand_block_selection = random.randint(word_block_index,
                                          (word_block_index + word_block_size - num_words))

    for word in range(rand_block_selection, rand_block_selection+num_words):
        random_list.append(sorted_text[word])

    return random_list


if __name__ == '__main__':

    random_passwords = get_list_of_words(4, 8)
    print(random_passwords)