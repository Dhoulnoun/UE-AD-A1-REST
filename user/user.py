from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'

with open('{}/databases/users.json'.format("."), "r") as jsf:
    users = json.load(jsf)["users"]


@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the User service!</h1>"


@app.route("/users", methods=['GET'])
def get_users():
    res = make_response(jsonify(users), 200)
    return res


@app.route("/users/<userid>", methods=['GET'])
def get_user_byid(userid):
    for user in users:
        if str(user["id"]) == str(userid):
            res = make_response(jsonify(user), 200)
            return res
        return make_response(jsonify({"error": "User ID not found"}), 404)


@app.route("/bookedmovies/<userid>", methods=['GET'])
def get_booking_for_user(userid):
    for user in users:
        if str(user["id"]) == str(userid):
            res = requests.get(f'http://172.16.121.127:3201/bookings/{userid}')
            booking = res.json()
            dates = booking["dates"]
            movies = []
            for movie_id in dates:
                movie = requests.get(f'http://172.16.121.127:3200/movies/{movie_id["movies"][0]}')
                movies.append(movie.json())
            res = make_response(jsonify(movies), 200)
            return res
    return make_response(jsonify({"error": "bad input parameter"}), 400)


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
