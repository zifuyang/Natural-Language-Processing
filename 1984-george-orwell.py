import random

def read_file(filename):
    """Reads an input text file and returns a list of all words."""
    with open(filename, 'r') as file:
        text = file.read().replace('\n', ' ')
    return text.split()

def build_markov_chain(words):
    """Constructs a dictionary that represents a Markov chain based on a list of words."""
    markov_chain = {}
    for i in range(len(words)-2):
        key = words[i] + ' ' + words[i+1]
        value = words[i+2]
        if key in markov_chain:
            markov_chain[key].append(value)
        else:
            markov_chain[key] = [value]
    return markov_chain

def generate_text(markov_chain, max_words=500):
    """Uses a Markov chain to generate a new text document."""
    key = random.choice(list(markov_chain.keys()))
    words = key.split()
    text = ' '.join(words)

    while len(text.split()) < max_words:
        if key in markov_chain:
            next_word = random.choice(markov_chain[key])
            text += ' ' + next_word
            words = words[1:] + [next_word]
            key = ' '.join(words)
        else:
            break

    return text

def output_text(text):
    """Displays the generated text and prompts for an output file name."""
    print("The results:\n---------------------------------------------------------------------")
    print(text)

    filename = input("\nEnter filename to write output to <Enter for skip>: ")
    if filename:
        with open(filename, 'w') as file:
            words = text.split()
            line_length = 0
            for word in words:
                if line_length + len(word) + 1 > 80:
                    file.write('\n')
                    line_length = 0
                file.write(word + ' ')
                line_length += len(word) + 1

def main():
    filename = "TreasureIsland.txt"
    words = read_file(filename)
    markov_chain = build_markov_chain(words)
    text = generate_text(markov_chain)
    output_text(text)

if __name__ == "__main__":
    main()
