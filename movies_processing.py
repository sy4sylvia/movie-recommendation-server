import pandas as pd
import os    

# reconstruction of the movies dataframe and the genres dataframe
movies_df = pd.read_csv('dataset/movies.csv')

# drop as many duplicates as possible
movies_df.drop_duplicates(inplace=True)

# get_year extracts year from the title column
def get_year(title):
    year = title[len(title) - 5:len(title) - 1]
    return year

# get_title extracts the movie title from the title column
def get_title(title):
    return title[: len(title) - 7]

# separating the title and year from the provided dataset
movies_df.rename(columns = {'title': 'movie_year'}, inplace = True)

movies_df['title'] = movies_df['movie_year'].apply(get_title)
movies_df['year'] = movies_df['movie_year'].apply(get_year)

movies_df = movies_df.drop(columns=['movie_year'])
movies_df = movies_df[['movieId', 'title', 'genres', 'year']]
movies_df['genres'] = movies_df.genres.str.split('|')

os.makedirs('processed', exist_ok=True)  
movies_df.to_csv('processed/movies_processed.csv', encoding='utf-8', index=False)

movies_with_genres_df = movies_df.copy()

# For every row in the dataframe, iterate through the list of genres and place a 1 if the movie belongs to the genre
for index, row in movies_df.iterrows():
    for genre in row['genres']:
        movies_with_genres_df.at[index, genre] = 1
        
# Fill in the NaN with 0 if the movie does not belong to the genre
movies_with_genres_df = movies_with_genres_df.fillna(0)

genres = movies_with_genres_df.set_index(movies_with_genres_df['movieId'])
# drop the duplicate movieId column and other unnecessary ones
genres = genres.drop(columns = ['movieId', 'title', 'genres', 'year'])
genres.to_csv('processed/genres_for_movies_processed.csv', encoding='utf-8', index=False)
