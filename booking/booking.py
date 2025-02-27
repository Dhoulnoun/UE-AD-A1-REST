from flask import Flask, render_template, request, jsonify, make_response, url_for
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

with open('{}/databases/bookings.json'.format("."), "r") as jsf:
    bookings = json.load(jsf)["bookings"]


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.route("/bookings/site_map", methods=['GET'])
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
    return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"


# getAll, retourne toutes les infos de la bd via la methode get au format json
@app.route("/bookings", methods=['GET'])
def get_bookings():
    res = make_response(jsonify(bookings), 200)
    return res


# get the booking from a user id
@app.route("/bookings/<userid>", methods=['GET'])
def get_booking_for_user(userid):
    for booking in bookings:
        if str(booking["userid"]) == str(userid):
            res = make_response(jsonify(booking), 200)
            return res
        return make_response(jsonify({"error": "User ID not found"}), 404)


# add a booking for a user
@app.route("/bookings/<userid>", methods=['POST'])
def add_booking_byuser(userid):
    req = request.get_json()
    # parse through the bookings
    for booking in bookings:
        # if the user id is found
        if str(booking["userid"]) == str(userid):
            # request the showtime servicer for the movies on a specific date if he cannot find a movie on this date
            # then we cant pursue the reason I'm not checking if the movie existe on specific date is because I
            # haven't added a funtion that finds all dates for a movie since it's not in the yaml file
            res = requests.get(f'http://localhost:3202/showtimes/{req["date"]}',200)
            if res.status_code == 200:
                for dates in booking["dates"]:
                    # if the booking already exists
                    if str(dates) == str(req):
                        return make_response(jsonify({"error": "an existing item already exists"}), 409)
                    booking["dates"].append(req)
                    return make_response(jsonify(booking), 200)
            else:
                return make_response(jsonify({"error": "date not found"}), 404)
        # if the user id is not found
        else:
            res = make_response(jsonify({"error": "User ID not found"}), 404)
    # I'm so unsure about this return because of it's scope I can't tell if my res inside the loops will be able to
    # affect the one returned bellow.
    # didn't have time to test it thoughroughly
    # TODO: test it
    return res


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
