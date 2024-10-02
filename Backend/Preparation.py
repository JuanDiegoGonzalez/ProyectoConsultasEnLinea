# Instalación de librerias
import pandas as pd
import re, unicodedata
import contractions
import inflect, nltk

from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

def remove_non_ascii(words):
    """Remove non-ASCII characters from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)
    return new_words

def to_lowercase(words):
    """Convert all characters to lowercase from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = word.lower()
        new_words.append(new_word)
    return new_words

def remove_punctuation(words):
    """Remove punctuation from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = re.sub(r'[^\w\s]', '', word)
        if new_word != '':
            new_words.append(new_word)
    return new_words

def replace_numbers(words):
    """Replace all interger occurrences in list of tokenized words with textual representation"""
    p = inflect.engine()
    new_words = []
    for word in words:
        if word.isdigit():
            new_word = p.number_to_words(word)
            new_words.append(new_word)
        else:
            new_words.append(word)
    return new_words

def remove_stopwords(words):
    """Remove stop words from list of tokenized words"""
    new_words = []
    for word in words:
        if word not in stopwords.words('english'):
            new_words.append(word)
    return new_words

def preprocessing(words):
    words = to_lowercase(words)
    words = replace_numbers(words)
    words = remove_punctuation(words)
    words = remove_non_ascii(words)
    words = remove_stopwords(words)
    return words

def stem_words(words):
    """Stem words in list of tokenized words"""
    stemmer = LancasterStemmer()
    stems = []
    for word in words:
        stem = stemmer.stem(word)
        stems.append(stem)
    return stems

def lemmatize_verbs(words):
    """Lemmatize verbs in list of tokenized words"""
    lemmatizer = WordNetLemmatizer()
    lemmas = []
    for word in words:
        lemma = lemmatizer.lemmatize(word, pos='v')
        lemmas.append(lemma)
    return lemmas

def stem_and_lemmatize(words):
    stems = stem_words(words)
    lemmas = lemmatize_verbs(words)
    return stems + lemmas

def prepare(data_t):
    data_t['study_and_condition'] = data_t['study_and_condition'].apply(contractions.fix) #Aplica la corrección de las contracciones
    data_t['words'] = data_t['study_and_condition'].apply(word_tokenize).apply(preprocessing) #Aplica la eliminación del ruido
    data_t['words'] = data_t['words'].apply(stem_and_lemmatize) #Aplica lematización y Eliminación de Prefijos y Sufijos.
    data_t['words'] = data_t['words'].apply(lambda x: ' '.join(map(str, x)))
    X_data = data_t['words']
    count = CountVectorizer()
    X_count = count.fit_transform(X_data)
    X_count.toarray()[0]

    # Se realiza el ajuste tf-idf
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(X_data)
    feature_names = vectorizer.get_feature_names_out()
    dense = vectors.todense()
    denselist = dense.tolist()
    X_tfidf = pd.DataFrame(denselist, columns=feature_names)
    df = None

    with open("assets/columns.txt",'r',encoding = 'utf-8') as f:
        txt = f.read()
        words = txt.replace(" ", "").replace("[", "").replace("]", "").replace("'", "").split(",")
        for i in X_tfidf.columns:
            if i in words:
                words.remove(i)
            else:
                X_tfidf.drop([i],axis=1,inplace=True)

        values = [[0 for i in range(len(words))]]
        df = pd.DataFrame(values, columns =words)

    return pd.concat([df, X_tfidf], axis=1)
    