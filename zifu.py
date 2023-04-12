import nltk, string, random
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

def generate_text(seed_text, length):
    generated_text = seed_text
    original_text = seed_text
    corrected_text = semantic_analysis(generated_text)
    corrected_tokens = tokenize_text(corrected_text)
    lemmatized_tokens = lemmatize_tokens(corrected_tokens)

    chain = {}
    for i in range(len(lemmatized_tokens)-1):
        current_word = lemmatized_tokens[i]
        next_word = lemmatized_tokens[i+1]
        if current_word not in chain:
            chain[current_word] = {}
        if next_word not in chain[current_word]:
            chain[current_word][next_word] = 0
        chain[current_word][next_word] += 1
    
    for i in range(length):
        if current_word not in chain:
            current_word = random.choice(lemmatized_tokens)
        next_word = random.choices(list(chain[current_word].keys()), weights=list(chain[current_word].values()))[0]
        if next_word in string.punctuation or next_word in ["'s","'t","'ve","n't"]:
            generated_text += next_word
        else:
            generated_text += ' ' + next_word
        current_word = next_word

    return generated_text.replace(original_text, '').replace(' ``','')

def main():
    file_path = 'corpora/treasureisland.txt'
    seed_text = load_text(file_path)
    generated_text = generate_text(seed_text, 100)
    print(generated_text[2].upper()+generated_text[3:])

if __name__ == '__main__':
    main()