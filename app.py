from flask import Flask, request, jsonify
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

        genres_str = document.get("genres")
        sliced_string = genres_str[1: len(genres_str) - 1]
        genres_list = sliced_string.split(", ")
        # print('after slicing', sliced_string)

        genres_dict = {"genres": genres_list}
        # movie_data['genres'] = genres_dict
        # movie_data.update(genres_dict)

        # movies_data[_movieId] = movie_data

        del document["_id"]
        del document["genres"]

        complete_movies_data[_movieId] = document
        movies_list.append(document)

    movies_data["movies"] = movies_list
    print(movies_data)
    print('type(movies_data) ', type(movies_data))

    response_str = json.dumps(movies_data, indent=4)
    response_body = json.loads(response_str)

    resp = jsonify(response_body)
    # resp = jsonify(movies_data)

    dummy = {
        "movieId": 5,
        "title": "Father of the Bride Part II",
        "genres": "['Comedy']",
        "year": 1995
    }

    dummy2 = {
        "movies": [
            dummy, dummy, dummy
        ]
    };

    print('type(resp) ', type(resp))
    resp.status_code = 200
    return jsonify(dummy2)

    # print('response_str', type(response_str))

    # print(movies_data)
    # print(type(response_body))
    #
    # response_str = json.dumps(movies_list, indent=4)
    # print(type(response_str))
    # response_body = json.loads(response_str)
    # print('response_body', type(response_body))
    # x

    # return movies_data


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
