import nltk, string, random, getopt, sys, os
from nltk.corpus import wordnet, PlaintextCorpusReader
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
    corpus = PlaintextCorpusReader(os.path.dirname(file_path), os.path.basename(file_path))
    return corpus.raw()

def tokenize_text(text: str) -> list:
    """Tokenize text.

    Args:
        text (str): Text to tokenize.

    Returns:
        list: Tokens.
    """
    return word_tokenize(text)

def lemmatize_tokens(tokens: str) -> list:
    """Lemmatize tokens using WordNet.

    Args:
        tokens (str): Tokens to lemmatize.

    Returns:
        list: Lemmatized tokens.
    """
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = []
    for token in tokens:
        pos_tag = nltk.pos_tag([token])[0][1]
        if pos_tag.startswith('N'):
            lemmatized_token = lemmatizer.lemmatize(token, pos=wordnet.NOUN)
        elif pos_tag.startswith('V'):
            lemmatized_token = lemmatizer.lemmatize(token, pos=wordnet.VERB)
        elif pos_tag.startswith('J'):
            lemmatized_token = lemmatizer.lemmatize(token, pos=wordnet.ADJ)
        elif pos_tag.startswith('R'):
            lemmatized_token = lemmatizer.lemmatize(token, pos=wordnet.ADV)
        else:
            lemmatized_token = token
        corrected_token = correct_word(lemmatized_token, pos_tag)
        lemmatized_tokens.append(corrected_token)
    return lemmatized_tokens

def correct_word(word: str, pos_tag: str) -> str:
    """Correct a word using WordNet.

    Args:
        word (str): Word to correct.
        pos_tag (str): Part-of-speech tag of the word.

    Returns:
        str: Corrected word.
    """
    if pos_tag.startswith('N') or pos_tag.startswith('V') or pos_tag.startswith('J'):
        if pos_tag.startswith('J'):
            pos_tag = 'a'  # Use 'a' instead of 'j' for adjectives
        synsets = wordnet.synsets(word, pos=pos_tag[0].lower())
        if synsets:
            lemmas = set()
            for synset in synsets:
                for lemma in synset.lemmas():
                    lemmas.add(lemma.name())
            if lemmas:
                if pos_tag.startswith('J'):
                    synset_id = f'{pos_tag[0].lower()}.{synsets[0].offset():08d}.{synsets[0].pos()}.{lemmas.pop()}'
                else:
                    synset_id = f'{pos_tag[0].lower()}.{synsets[0].offset():08d}.{synsets[0].pos()}.{lemmas.pop()}'
                try:
                    most_similar = sorted(lemmas, key=lambda x: wordnet.wup_similarity(synsets[0], wordnet.synset(synset_id)) or 0, reverse=True)
                    if most_similar:
                        return most_similar[0]
                    else:
                        return word
                except (ValueError, nltk.corpus.reader.wordnet.WordNetError):
                    return word
            else:
                return word
    return word

def semantic_analysis(text: str) -> str:
    """Perform semantic analysis on a text.

    Args:
        text (str): Text to perform semantic analysis on.

    Returns:
        str: Text with semantic analysis performed.
    """
    tokens = tokenize_text(text)
    lemmatized_tokens = lemmatize_tokens(tokens)
    return ' '.join(lemmatized_tokens)

def generate_text(seed_text: str, length: int, order: int, verbose: bool) -> str:
    """Generate text based on a seed text with Markov chains.

    Args:
        seed_text (str): Seed text to generate text from.
        length (int): Length of the generated text.
        order (int): Order of the Markov chain.
        verbose (bool): Verbose mode.

    Returns:
        str: Generated text.
    """
    nltk.download('wordnet', quiet=not(verbose))
    nltk.download('punkt', quiet=not(verbose))
    nltk.download('averaged_perceptron_tagger', quiet=not(verbose))

    generated_text = seed_text
    original_text = seed_text
    corrected_text = semantic_analysis(generated_text)
    corrected_tokens = tokenize_text(corrected_text)
    lemmatized_tokens = lemmatize_tokens(corrected_tokens)

    chain = {}
    for i in range(len(lemmatized_tokens)-order):
        current_words = tuple(lemmatized_tokens[i:i+order])
        next_word = lemmatized_tokens[i+order]
        if current_words not in chain:
            chain[current_words] = {}
        if next_word not in chain[current_words]:
            chain[current_words][next_word] = 0
        chain[current_words][next_word] += 1
    
    current_words = tuple(lemmatized_tokens[:order])
    for i in range(length):
        if current_words not in chain:
            current_words = tuple(random.choice(lemmatized_tokens) for i in range(order))
        next_word = random.choices(list(chain[current_words].keys()), weights=list(chain[current_words].values()))[0]
        if next_word in string.punctuation or next_word in ["'s","'t","'ve","n't"]:
            generated_text += next_word
        else:
            generated_text += ' ' + next_word
        current_words = current_words[1:] + tuple([next_word])

    return generated_text.replace(original_text, '').replace(' ``','')

def main() -> None:
    """Main function.

    Raises:
        ValueError: Order must be greater than 1
        ValueError: Length must be greater than 0
    """
    argumentList = sys.argv[1:]
    file_path = None
    order = 1
    length=200
    verbose=False

    try:
        arguments, _ = getopt.getopt(argumentList, "hvi:o:f:l:", ["ifile=", "order=", "file=", "length="])
        if len(arguments) > 0:
            for currentArgument, currentValue in arguments:
                if currentArgument == "-h":
                    print("Usage: python program.py -i <inputfile> -o <order>")
                    sys.exit()
                if currentArgument == "-v":
                    verbose=True
                elif currentArgument in ("-i", "--ifile", "-f", "--file"):
                    file_path = currentValue
                if currentArgument in ("-o", "--order"):
                    try:
                        order = int(currentValue)
                        if order <= 1:
                            raise ValueError("Order must be greater than 1")
                    except ValueError as e:
                        print(f"Invalid value for order: {e}")
                        sys.exit(2)
                elif currentArgument in ("-l", "--length"):
                    try:
                        length = int(currentValue)
                        if length <= 1:
                            raise ValueError("Length must be greater than 0")
                    except ValueError as e:
                        print(f"Invalid value for length: {e}")
                        sys.exit(2)

    except getopt.error as err:
        print(str(err))
        print("Usage: python program.py -i <inputfile> -o <order>")
        sys.exit(2)

    if not(file_path):
        file_path = 'corpora/'+input('Enter the text file name: ')
    try:
        seed_text = load_text(file_path)
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        sys.exit(2)
    
    generated_text = generate_text(seed_text, length, order, verbose)
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
        generated_text = generate_text(load_text("corpora/treasureisland.txt"), 200, i, True)
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
