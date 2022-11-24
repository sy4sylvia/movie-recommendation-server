from flask import Flask
import pandas as pd

app = Flask(__name__)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


# read from local
movies = pd.read_csv('processed/movies_processed.csv')
movies.drop_duplicates(inplace=True)

ratings = pd.read_csv('processed/ratings_processed.csv')

df_predict = pd.read_csv('data/TFIDF.csv')

user_profile = pd.read_csv('data/user_profile.csv')

def recommend_system(user_no):
    return
    # user predicted rating to all films
    # user_predicted_rating = df_predict[['movieId', df_predict.columns[user_no]]]
    # # combine film rating and film detail
    # user_rating_film = pd.merge(user_predicted_rating, movies, left_on='movieId', right_on='id')
    # # films already watched by user
    # already_watched = ratings[ratings['userId'].isin([user_no])]['movieId']
    # # recommendation without films being watched by user
    # all_rec = user_rating_film[~user_rating_film.index.isin(already_watched)]
    # return all_rec.sort_values(by=str(user_no), ascending=False, axis=0).iloc[0:10][['movieId', 'title']]


if __name__ == '__main__':
    app.run()
