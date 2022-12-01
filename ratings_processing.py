import pandas as pd

# userId,movieId,rating,timestamp

ratings_df = pd.read_csv('dataset/ratings.csv')

# drop unnecessary columns
ratings_df = ratings_df.drop(columns=['timestamp'])

ratings_df.to_csv('processed/ratings_processed.csv', encoding='utf-8', index=False)
