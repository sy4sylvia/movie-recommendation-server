from pandas import *

data = read_csv('processed/movies_processed.csv')
genres = data['genres'].tolist()

data['genres'] = genres
data.to_csv('processed/updated_movies_processed.csv', encoding='utf-8', index=False)
