import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk import pos_tag
from sklearn.feature_extraction.text import TfidfVectorizer

# Download once
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')

text = "Natural language processing is very interesting and useful"

# Tokenization
tokens = word_tokenize(text)
print("Tokens:", tokens)

# POS Tagging
print("POS:", pos_tag(tokens))

# Stopwords removal
stop_words = set(stopwords.words('english'))
filtered = []
for word in tokens:
    if word.lower() not in stop_words:
        filtered.append(word)
print("After Stopwords:", filtered)

# Stemming
stemmer = PorterStemmer()
stemmed = []
for word in filtered:
    stemmed.append(stemmer.stem(word))
print("Stemming:", stemmed)

# Lemmatization
lemmatizer = WordNetLemmatizer()
lemmatized = []
for word in filtered:
    lemmatized.append(lemmatizer.lemmatize(word))
print("Lemmatization:", lemmatized)

# TF-IDF
docs = ["I love NLP", "NLP is useful"]
vectorizer = TfidfVectorizer()
tfidf = vectorizer.fit_transform(docs)

print("Words:", vectorizer.get_feature_names_out())
print("TF-IDF:\n", tfidf.toarray())
