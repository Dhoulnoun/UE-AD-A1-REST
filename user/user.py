from flask import Flask, render_template, request, jsonify, make_response, url_for
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3203
HOST = 'localhost'

with open('{}/databases/users.json'.format("."), "r") as jsf:
    users = json.load(jsf)["users"]

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.route("/user/site_map", methods=['GET'])
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    return make_response(jsonify(links), 200)

# root message
@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the User service!</h1>"


# get all users
@app.route("/users", methods=['GET'])
def get_users():
    res = make_response(jsonify(users), 200)
    return res


# get user by id
@app.route("/users/<userid>", methods=['GET'])
def get_user_byid(userid):
    for user in users:
        if str(user["id"]) == str(userid):
            res = make_response(jsonify(user), 200)
            return res
        return make_response(jsonify({"error": "User ID not found"}), 404)


# create user
@app.route("/users", methods=['POST'])
def create_user():
    user = request.get_json()
    for u in users:
        if u["id"] == user["id"]:
            return make_response(jsonify({"error": "User ID already exists"}), 400)
    users.append(user)
    res = make_response(jsonify(user), 201)
    return res


# update user
@app.route("/users/<userid>", methods=['PUT'])
def update_user(userid):
    newUser = request.get_json()
    for user in users:
        if str(user["id"]) == str(userid):
            user["name"] = newUser["name"]
            user["email"] = newUser["email"]
            users.append(newUser)
            res = make_response(jsonify(user), 200)
            return res


# get the bookings related to a user
@app.route("/bookedmovies/<userid>", methods=['GET'])
def get_booking_for_user(userid):
    for user in users:
        if str(user["id"]) == str(userid):
            res = requests.get(f'http://localhost:3201/bookings/{userid}')
            booking = res.json()
            dates = booking["dates"]
            movies = []
            for movie_id in dates:
                movie = requests.get(f'http://localhost:3200/movies/{movie_id["movies"][0]}')
                movies.append(movie.json())
            res = make_response(jsonify(movies), 200)
            return res
    return make_response(jsonify({"error": "bad input parameter"}), 400)


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
