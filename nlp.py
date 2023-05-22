import nltk, string, random, sys, os, argparse
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

def load_text(file_path: str) -> str:
    """Load text from a file.

    Args:
        file_path (str): Path to the file.

    Raises:
        FileNotFoundError: File not found.

    Returns:
        str: Text from the file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found")
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def lemmatize_tokens(tokens: list[str]) -> list:
    """Lemmatize tokens using WordNet.

    Args:
        tokens (str): Tokens to lemmatize.

    Returns:
        list: Lemmatized tokens.
    """
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token, pos=wordnet.NOUN) if pos_tag.startswith('N') else
                     lemmatizer.lemmatize(token, pos=wordnet.VERB) if pos_tag.startswith('V') else
                     lemmatizer.lemmatize(token, pos=wordnet.ADJ) if pos_tag.startswith('J') else
                     lemmatizer.lemmatize(token, pos=wordnet.ADV) if pos_tag.startswith('R') else
                     token for token, pos_tag in nltk.pos_tag(tokens)]
    return lemmatized_tokens

def correct_word(word: str, pos_tag: str) -> str | list[str]:
    """Correct a word using WordNet.

    Args:
        word (str): Word to correct.
        pos_tag (str): Part of speech tag of the word.

    Returns:
        str | list[str]: Corrected word or list of similar words.
    """
    if pos_tag[0] in ('N', 'V', 'J'):
        if pos_tag.startswith('J'):
            pos_tag = 'a'  # Use 'a' instead of 'j' for adjectives to match wordnet's format
        synsets = wordnet.synsets(word, pos=pos_tag[0].lower())
        if synsets:
            lemmas = {lemma.name() for synset in synsets for lemma in synset.lemmas()} # pyright: ignore[reportOptionalMemberAccess]
            if lemmas:
                synset_id = f'{pos_tag[0].lower()}.{synsets[0].offset():08d}.{synsets[0].pos()}.{lemmas.pop()}' # pyright: ignore[reportOptionalMemberAccess]
                try:
                    most_similar = sorted(lemmas, key=lambda x: wordnet.wup_similarity(synsets[0], wordnet.synset(synset_id)) or 0, reverse=True)
                    return most_similar if most_similar else word #Return the most similar word if it exists
                except (ValueError, nltk.corpus.reader.wordnet.WordNetError):
                    return word
    return word

def semantic_analysis(text: str) -> str:
    """Perform semantic analysis on a text.

    Args:
        text (str): Text to perform semantic analysis on.

    Returns:
        str: Text with semantic analysis performed.
    """
    tokens = word_tokenize(text)
    lemmatized_tokens = lemmatize_tokens(tokens)
    return ' '.join(lemmatized_tokens)

def generate_text(seed_text: str, length: int, order: int, verbose: bool, temperature: float) -> str:
    """Generate text based on a seed text with Markov chains.

    Args:
        seed_text (str): Seed text to generate text from.
        length (int): Length of the generated text.
        order (int): Order of the Markov chain.
        verbose (bool): Verbose mode.

    Returns:
        str: Generated text.
    """
    nltk.download('wordnet punkt averaged_perceptron_tagger'.split(), quiet=not(verbose))

    generated_text = seed_text
    original_text = seed_text
    corrected_text = semantic_analysis(generated_text)
    corrected_tokens = word_tokenize(corrected_text)
    lemmatized_tokens = lemmatize_tokens(corrected_tokens)

    chain = {}
    for i in range(len(lemmatized_tokens)-order):
        current_words = tuple(lemmatized_tokens[i:i+order])
        next_word = lemmatized_tokens[i+order]
        chain.setdefault(current_words, {}).setdefault(next_word, 0)
        chain[current_words][next_word] += 1
    
    current_words = tuple(lemmatized_tokens[:order])
    for i in range(length):
        if current_words not in chain:
            current_words = tuple(random.choice(lemmatized_tokens) for i in range(order))

        weights = list(chain[current_words].values())
        weights = [w ** (1 / temperature) for w in weights]
        
        next_word = random.choices(list(chain[current_words].keys()), weights=weights)[0]
        if next_word in string.punctuation or next_word in ["'s","'t","'ve","n't"]:
            generated_text += next_word
        else:
            generated_text += ' ' + next_word
        current_words = current_words[1:] + tuple([next_word])

    return generated_text.replace(original_text, '').replace(' ``','')

def check_positive(value: float | int) -> float | int:
    """Check if a value is positive.

    Args:
        value (float | int): Value to check.

    Raises:
        argparse.ArgumentTypeError: Not a positive number.
        Exception: Not a number.

    Returns:
        float | int: Value if it is positive.
    """
    try:
        value = float(value)
        if value <= 0:
            raise argparse.ArgumentTypeError("{} is not a positive number".format(value))
    except ValueError:
        raise Exception("{} is not a number".format(value))
    return value

def main() -> None:
    """Main function.

    Raises:
        ValueError: Order must be greater than 1
        ValueError: Length must be greater than 0
    """
    file_path, order, length, verbose, temperature = None, 1, 200, False, 0.5

    parser = argparse.ArgumentParser(description='Perform semantic analysis and generate text using Markov chains.')
    parser.add_argument('-i', '--input', '-f', '--file', type=str, help='Input file path')
    parser.add_argument('-o', '--order', type=check_positive, default=1, help='Order of the Markov chain')
    parser.add_argument('-l', '--length', type=check_positive, default=200, help='Length of the generated text')
    parser.add_argument('-t', '--temperature', type=check_positive, default=0.5, help='Temperature for the Markov chain')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    
    try:
        args = parser.parse_args()
    except argparse.ArgumentTypeError as e:
        print(e)
        sys.exit(2)
    
    if not args.input:
        file_path = 'corpora/' + input('Enter the text file name: ')
    else:
        file_path = args.input

    order = int(args.order)
    length = int(args.length)
    temperature = args.temperature
    verbose = args.verbose

    if not(file_path):
        file_path = 'corpora/'+input('Enter the text file name: ')
    try:
        seed_text = load_text(file_path)
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        sys.exit(2)
    
    generated_text = generate_text(seed_text, length, order, verbose, temperature)
    leading=0
    for i in generated_text:
        if not(i.lower() in string.ascii_lowercase):
            leading+=1
        else:
            break
    
    print("\nThe results:---------------------------------------------------------------------")
    print(generated_text[0+leading].upper()+generated_text[1+leading:])

    filename = input("\nEnter filename to write output to <Enter for skip>: ")
    if filename:
        with open(filename, 'w') as file:
            words = (generated_text[0+leading].upper()+generated_text[1+leading:]).split()
            line_length = 0
            for word in words:
                if line_length + len(word) + 1 > 80:
                    file.write('\n')
                    line_length = 0
                file.write(word + ' ')
                line_length += len(word) + 1

def test() -> None:
    """Test the program."""
    for i in [1,2,3]:
        generated_text = generate_text(load_text("corpora/treasureisland.txt"), 200, i, True, 0.5)
        leading=0
        for i in generated_text:
            if not(i.lower() in string.ascii_lowercase):
                leading+=1
            else:
                break
        x=generated_text[0+leading].upper()+generated_text[1+leading:]
        assert x[0] in string.ascii_uppercase
        print(x)
        
if __name__ == '__main__':
    main()
