from flask import Flask, request, jsonify, Response
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
movies_collection = db.movies
# users_collection correspond to the users created on the web app, does not include the data from movieLens
users_collection = db.users

movies_with_genres_df = pd.read_csv('processed/movies_with_genres_df_processed.csv')

movies_df = pd.read_csv('processed/movies_processed.csv', header=0)
ratings_df = pd.read_csv('processed/ratings_processed.csv', header=0)
genres = pd.read_csv('processed/genres_for_movies_processed.csv', header=0)
movies = pd.read_csv('dataset/movies.csv', header=0)


# home page 
@app.route('/')
@cross_origin()
def dummy_function():  # put application's code here
    return 'Hello World?'


# profile page
@app.route('/profile', methods=['GET'])
def api_profile():  # put application's code here
    dummy = {
        'id': 680333
    }

    response_str = json.dumps(dummy, indent=4)
    dummy_response_body = json.loads(response_str)
    return dummy


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

    # generate the userId
    _userId = 13 * len(_email) + 49 * len(_password) + 713
    _dict = {"email": _email, "password": _password, "userId": _userId}
    # shallow copy the _dict, otherwise the objectId field would be assigned
    response_body = _dict.copy()
    users_collection.insert_one(_dict)

    if _email == 'sg6803@nyu.edu':
        return {"success": False,
                "msg": "Already registered"}, 400
    else:
        return response_body


# login route
@app.route('/login', methods=['POST'])
def post_login():
    req_data = request.get_json()
    _email = req_data.get("email")
    _password = req_data.get("password")

    users_cursor = users_collection.find({"email": _email})

    _current_userId = 0
    for document in users_cursor:
        _cur_userId = document.get("userId")
        _db_password = document.get("password")

        if _db_password != _password:
            return {"success": False,
                    "msg": "Wrong password"}, 401

        _current_userId = _cur_userId

    if _current_userId == 0:
        return {"success": False,
                "msg": "User not found"}, 400

    return {"email": _email, "userId": _current_userId}, 200


# GET all the movies from the database
@app.route('/movies', methods=['GET'])
def get_movies():
    # TODO: construct the dictionary of movies, key: movieId, value: movieInfo
    movies_data = {}
    complete_movies_data = {}
    movies_list = []
    # get data from the movies_collection
    movie_cursor = movies_collection.find({})

    for document in movie_cursor:
        movie_data = {}
        _movieId = document.get("movieId")

        movie_data["title"] = document.get("title")
        # movie_data['genres'] = document.get('genres')
        movie_data["year"] = document.get("year")

        del document["_id"]
        # del document["genres"]

        complete_movies_data[_movieId] = document
        movies_list.append(document)

    movies_data["movies"] = movies_list[0:700]

    js = json.dumps(movies_data)
    response = Response(js, status=200, mimetype='application/json')
    return response


# get a specific movie
@app.route('/movie', methods=['GET'])
def get_movie_by_id():
    _movieId = request.args['movieId']
    dummy = {
        "movieId": 5,
        "title": "Father of the Bride Part II",
        "genres": "['Comedy']",
        "year": 1995
    }
    return jsonify(dummy)


# post the rating and save the user data in the database to perform the get recommendation again
@app.route('/rating', methods=['POST'])
def post_movie_rating():
    req_data = request.get_json()
    _movieId = req_data.get('movieId')
    _rating = req_data.get('rating')
    # TODO: actually store the movieId & rating in the database,
    #  and GET recommendation when calling the get recommendation page
    user_input = [{'movieId': int(_movieId), 'rating': _rating},
                  {'movieId': 1, 'rating': 1},
                  {'movieId': 2, 'rating': 1}]
    # has to gather enough data to generate recommendation
    input_movies = pd.DataFrame(user_input)

    user_movies = movies_with_genres_df[movies_with_genres_df['movieId'].isin(input_movies['movieId'].tolist())]
    user_genres = user_movies.drop(columns=['movieId', 'title', 'genres', 'year'])
    transpose_genres = user_genres.transpose()

    user_profile = np.matmul(transpose_genres, input_movies['rating'])

    # Similarly, get the genres of every movie in the original dataframe
    cur_genres = movies_with_genres_df.set_index(movies_with_genres_df['movieId'])
    cur_genres = cur_genres.drop(columns=['movieId', 'title', 'genres', 'year'])

    recommendation_df = ((cur_genres * user_profile).sum(axis=1)) / (user_profile.sum())
    recommendation_df = recommendation_df.sort_values(ascending=False)
    new_user_top_reco = movies_df.loc[movies_df['movieId'].isin(recommendation_df.head(30).keys())]

    # convert into JSON objects
    result = new_user_top_reco.to_json(orient="records")
    parsed = json.loads(result)
    json.dumps(parsed, indent=4)

    if int(_movieId) < 0:
        return {"success": False,
                "msg": "Not a valid movie id"}, 400
    else:
        return parsed, 200
