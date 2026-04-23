import kagglehub
import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Download VADER lexicon
nltk.download('vader_lexicon')

# Download dataset
path = kagglehub.dataset_download("ruchi798/data-science-tweets")

# Load dataset
df = pd.read_csv(path + "/tweets/data_science.csv")

# Keep only tweet column
df = df[['tweet']].dropna()

# Initialize analyzer
sia = SentimentIntensityAnalyzer()

# Function to classify sentiment
def classify_sentiment(text):
    score = sia.polarity_scores(text)['compound']
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    return "Neutral"

# Take sample tweets
sample_df = df.sample(3)

print("\n--- Sample Tweet Classification ---\n")

# Loop through sample tweets
for i, row in sample_df.iterrows():
    tweet = row['tweet']
    sentiment = classify_sentiment(tweet)
    
    print("Tweet:", tweet + "...")
    print("Sentiment:", sentiment)
    print("-" * 50)

# Input a user tweet for classification
user_tweet = input("Enter a tweet: ")
print("Sentiment:", classify_sentiment(user_tweet))
