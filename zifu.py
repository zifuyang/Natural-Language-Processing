import nltk, string, random, getopt, sys
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

def load_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return text

def tokenize_text(text):
    return word_tokenize(text)

def lemmatize_tokens(tokens):
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

def correct_word(word, pos_tag):
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

def semantic_analysis(text):
    tokens = tokenize_text(text)
    lemmatized_tokens = lemmatize_tokens(tokens)
    return ' '.join(lemmatized_tokens)

def generate_text(seed_text, length, order):
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

def main():
    argumentList = sys.argv[1:]

    options = "o:"
    long_options = ["order="]
    order=1

    try:
        arguments = getopt.getopt(argumentList, options, long_options)
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-o", "--order"):
                order = int(currentValue) if int(currentValue) > 1 else 1
    except getopt.error as err:
        print (str(err))
        sys.exit(2)
    file_path = 'corpora/'+input('Enter the text file name: ')
    seed_text = load_text(file_path)
    generated_text = generate_text(seed_text, 200, order)
    leading=0
    for i in generated_text:
        if not(i.lower() in string.ascii_lowercase):
            leading+=1
        else:
            break
    
    print("\nThe results:---------------------------------------------------------------------")
    print(generated_text[0+leading].upper()+generated_text[1+leading:])

if __name__ == '__main__':
    main()