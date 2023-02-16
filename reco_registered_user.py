import pandas as pd
import numpy as np

# generate recommendation for existing users' recommendation
movies_with_genres_df = pd.read_csv('processed/movies_with_genres_df_processed.csv')

movies_df = pd.read_csv("processed/movies_processed.csv", header=0)
ratings_df = pd.read_csv('processed/ratings_processed.csv', header=0)
genres = pd.read_csv('processed/genres_for_movies_processed.csv', header=0)
movies = pd.read_csv("dataset/movies.csv", header=0)

def get_recommendation():
    user_rated_movies_df = ratings_df.loc[ratings_df['userId'].isin([1])]
    
    existing_user_movies = movies_with_genres_df[movies_with_genres_df['movieId'].isin(user_rated_movies_df['movieId'].tolist())]
    existing_user_genres = existing_user_movies.drop(columns = ['movieId', 'title', 'genres', 'year'])
    existing_user_profile = np.matmul(existing_user_genres.transpose(), user_rated_movies_df['rating'])

    existing_recommendation_df = ((genres * existing_user_profile).sum(axis = 1)) / (existing_user_profile.sum())
    
    # Recommendation System, sort the weighted average descendingly
    existing_recommendation_df = existing_recommendation_df.sort_values(ascending = False)

    existing_top_reco = movies_df.loc[movies_df['movieId'].isin(existing_recommendation_df.head(50).keys())]
    # Filter out the movies that the existing user has already rated
    existing_top_reco = existing_top_reco[~existing_top_reco['movieId'].isin(existing_user_movies['movieId'])]
    existing_top_reco.to_csv('processed/top_user1.csv', encoding='utf-8', index=False)
