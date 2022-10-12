from flask import Flask, render_template, request, jsonify, make_response, url_for
import json
import sys
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3200
HOST = 'localhost'

with open('{}/databases/movies.json'.format("."), "r") as jsf:
    movies = json.load(jsf)["movies"]


# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>", 200)


@app.route("/template", methods=['GET'])
def template():
    return make_response(render_template('index.html', body_text='This is my HTML template for Movie service'), 200)


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.route("/movies/site_map", methods=['GET'])
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    return make_response(jsonify(links), 200)


# getAll, retourne toutes les infos de la bd via la methode get au format json
@app.route("/json", methods=['GET'])
def get_json():
    res = make_response(jsonify(movies), 200)
    return res


# getMovieById: retrieves a movie with it's id returns a json object
@app.route("/movies/<movieid>", methods=['GET'])
def get_movie_byid(movieid):
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            res = make_response(jsonify(movie), 200)
            return res
        return make_response(jsonify({"error": "Movie ID not found"}), 404)


# getMoviByTitle: retrieves one or many movies with the same name
@app.route("/moviesbytitle", methods=['GET'])
def get_movie_bytitle():
    json = []
    if request.args:
        req = request.args
        for movie in movies:
            if str(movie["title"]) == str(req["title"]):
                json.append(movie)
    if not json:
        res = make_response(jsonify({"error": "movie title not found"}), 404)
    else:
        res = make_response((jsonify(json)), 200)
    return res


# returns all movies created by a director
@app.route("/moviesbydirector", methods=['GET'])
def get_movie_bydriector():
    json = []
    if request.args:
        req = request.args
        for movie in movies:
            if str(movie["director"]) == str(req["director"]):
                json.append(movie)
                print(json, file=sys.stderr)
    if not json:
        res = make_response(jsonify({"error": "movie title not found"}), 404)
    else:
        print(json, file=sys.stderr)
        res = make_response((jsonify(json)), 200)
    return res


"""createMovie"""


@app.route("/movies/<movieid>", methods=['POST'])
def create_movie(movieid):
    req = request.get_json()

    for movie in movies:
        if str(movie["id"]) == str(movieid):
            return make_response(jsonify({"error": "movie ID already exists"}), 409)

    movies.append(req)
    res = make_response(jsonify({"message": "movie added"}), 200)
    return res


"""updateMovieRating: update the rating of a movie recovered thx to its id"""


@app.route("/movies/<movieid>/<rate>", methods=['PUT'])
def update_movie_rating(movieid, rate):
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movie["rating"] = float(rate)
            res = make_response(jsonify(movie), 200)
            return res
    res = make_response(jsonify({"error": "movie ID not found"}), 201)
    return res


"""deleteMovie: deletes a movie, removes the move from the db"""


@app.route("/movies/<movieid>", methods=['DELETE'])
def del_movie(movieid):
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movies.remove(movie)
            return make_response(jsonify(movie), 200)

    res = make_response(jsonify({"error": "movie ID not found"}), 400)
    return res


if __name__ == "__main__":
    # p = sys.argv[1]
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT, debug=True)
