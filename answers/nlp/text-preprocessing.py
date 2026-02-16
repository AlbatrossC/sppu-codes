import nltk
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')

text = "The students are studying Natural Language Processing in the university, and they are learning many interesting concepts easily!"

print("Original Text:")
print(text)

# Remove Special Characters
text = re.sub(r'[!()]', '', text)
print("\nAfter Removing Special Characters:")
print(text)

# Tokenization
tokens = word_tokenize(text)
print("\nTokens:")
print(tokens)

# Stopword Removal
stop_words = set(stopwords.words('english'))
filtered = [word for word in tokens if word.lower() not in stop_words]
print("\nAfter Stopword Removal:")
print(filtered)

# Stemming
stemmer = PorterStemmer()
stemmed = [stemmer.stem(word) for word in filtered]
print("\nAfter Stemming:")
print(stemmed)

# Lemmatization
lemmatizer = WordNetLemmatizer()
lemmatized = [lemmatizer.lemmatize(word) for word in filtered]
print("\nAfter Lemmatization:")
print(lemmatized)
