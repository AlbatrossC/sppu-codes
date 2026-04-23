import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset
df = pd.read_csv("movie_dataset.csv")

# Fill missing values
features = ['genres', 'keywords', 'cast', 'director']
for feature in features:
    df[feature] = df[feature].fillna('')

# Combine features into one column
def combine_features(row):
    return row['genres'] + " " + row['keywords'] + " " + row['cast'] + " " + row['director']

df["combined_features"] = df.apply(combine_features, axis=1)

# Convert text to matrix
cv = CountVectorizer()
count_matrix = cv.fit_transform(df["combined_features"])

# Compute similarity
cosine_sim = cosine_similarity(count_matrix)

# Function to get movie title from index
def get_title_from_index(index):
    return df[df.index == index]["title"].values[0]

# Function to get index from title
def get_index_from_title(title):
    return df[df.title == title]["index"].values[0]

# Recommend movies
def recommend(movie_name):
    movie_index = get_index_from_title(movie_name)
    similar_movies = list(enumerate(cosine_sim[movie_index]))

    # Sort by similarity score
    sorted_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)

    print("\nTop 5 similar movies:\n")
    i = 0
    for movie in sorted_movies[1:6]:
        print(get_title_from_index(movie[0]))
        i += 1

recommend("The Avengers")
