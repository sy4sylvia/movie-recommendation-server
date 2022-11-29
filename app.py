from flask import Flask, request
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
import pandas as pd
import numpy as np
import json

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

client = MongoClient('localhost', 27017)

db = client.movieRecoDB
todos = db.todos
movies_collection = db.movies

movies_with_genres_df = pd.read_csv('processed/movies_with_genres_df_processed.csv')

movies_df = pd.read_csv("processed/movies_processed.csv", header=0)
ratings_df = pd.read_csv('processed/ratings_processed.csv', header=0)
genres = pd.read_csv('processed/genres_for_movies_processed.csv', header=0)
movies = pd.read_csv("dataset/movies.csv", header=0)


# home page 
@app.route('/')
@cross_origin()
def dummy_function():  # put application's code here
    return 'Hello World?'


# profile page
@app.route('/profile', methods=['GET'])
def api_profile():  # put application's code here
    dummy_response_body = {
        'id': 680333
    }
    return dummy_response_body


@app.route('/user', methods=['POST'])
def post_userid():
    req_data = request.get_json()

    _userId = req_data.get('userId')

    print(type(_userId))

    # begin processing...
    user_rated_movies_df = ratings_df.loc[ratings_df['userId'].isin([_userId])]
    # existing_user_movies = genres[genres['movieId'].isin(user_rated_movies_df['movieId'].tolist())]

    existing_user_movies = movies_with_genres_df[
        movies_with_genres_df['movieId'].isin(user_rated_movies_df['movieId'].tolist())]
    existing_user_genres = existing_user_movies.drop(columns=['movieId', 'title', 'genres', 'year'])
    existing_user_profile = np.matmul(existing_user_genres.transpose(), user_rated_movies_df['rating'])

    existing_recommendation_df = ((genres * existing_user_profile).sum(axis=1)) / (existing_user_profile.sum())
    # Recommendation System, sort the weighted average descending
    existing_recommendation_df = existing_recommendation_df.sort_values(ascending=False)

    existing_top_reco = movies_df.loc[movies_df['movieId'].isin(existing_recommendation_df.head(30).keys())]
    # Filter out the movies that the existing user has already rated
    existing_top_reco = existing_top_reco[~existing_top_reco['movieId'].isin(existing_user_movies['movieId'])]

    # convert into JSON objects
    result = existing_top_reco.to_json(orient="records")
    parsed = json.loads(result)
    json.dumps(parsed, indent=4)

    if _userId < 0:
        return {"success": False,
                "msg": "Not a valid user id"}, 400
    else:
        return parsed, 200


# register route
@app.route('/register', methods=['POST'])
def post_register():
    req_data = request.get_json()
    _email = req_data.get('email')
    _password = req_data.get('password')
    # TODO: insert into the database, after registration, assign a random userId,
    #  ask the user to rate, then generate with the ratings

    if _email == 'abcd':
        return {"success": False,
                "msg": "Already registered"}, 400
    else:
        return {"success": True,
                "msg": "valid email"}, 200


# login route
@app.route('/login', methods=['POST'])
def post_login():
    req_data = request.get_json()
    _email = req_data.get('email')
    _password = req_data.get('password')
    # TODO: compare the email and password with the users collection in the database

    if _email == 'abcd':
        return {"success": False,
                "msg": "Not a valid user id"}, 400
    else:
        return {"success": True,
                "msg": "valid email"}, 200


# GET all the movies from the database
@app.route('/movies', methods=['GET'])
def get_movies():
    # construct the dictionary of movies, key: movieId, value: movieInfo
    movies_data = {}
    # get data from the movies_collection
    movie_cursor = movies_collection.find({})

    for document in movie_cursor:
        movie_data = {}
        _movieId = document.get('movieId')
        movie_data['title'] = document.get('title')
        movie_data['genres'] = document.get('genres')
        movie_data['year'] = document.get('year')
        movies_data[_movieId] = movie_data

    response_body = json.dumps(movies_data)
    print(response_body)

    return response_body


# recommendation route
@app.route('/recommendation')
# generate recommendation for existing users' recommendation
def create_recommendation(givenId):
    print(givenId)
    user_rated_movies_df = ratings_df.loc[ratings_df['userId'].isin([givenId])]
    # existing_user_movies = genres[genres['movieId'].isin(user_rated_movies_df['movieId'].tolist())]

    existing_user_movies = movies_with_genres_df[
        movies_with_genres_df['movieId'].isin(user_rated_movies_df['movieId'].tolist())]
    existing_user_genres = existing_user_movies.drop(columns=['movieId', 'title', 'genres', 'year'])
    existing_user_profile = np.matmul(existing_user_genres.transpose(), user_rated_movies_df['rating'])

    existing_recommendation_df = ((genres * existing_user_profile).sum(axis=1)) / (existing_user_profile.sum())
    # Recommendation System, sort the weighted average descending
    existing_recommendation_df = existing_recommendation_df.sort_values(ascending=False)

    existing_top_reco = movies_df.loc[movies_df['movieId'].isin(existing_recommendation_df.head(50).keys())]
    # Filter out the movies that the existing user has already rated
    existing_top_reco = existing_top_reco[~existing_top_reco['movieId'].isin(existing_user_movies['movieId'])]
    existing_top_reco.to_csv('processed/top_user1.csv', encoding='utf-8', index=False)
    return
