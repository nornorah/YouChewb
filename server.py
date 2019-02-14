"""Recipe website"""
from pprint import pformat
import os
import requests

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This raises an error instead.
app.jinja_env.undefined = StrictUndefined

# Retrieve tokens and keys, set movie url
RAPIDAPI_TOKEN = os.environ.get('RAPIDAPI_TOKEN')
RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY')
MOVIEDB_KEY = os.environ.get('MOVIEDB_KEY')
MOVIEDB_URL = "https://api.themoviedb.org/3/"


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/results')
def recipe_results():
    """Output of recipes user queried from putting in ingredients"""

    search = request.args.get('ingredients')
    payload = {'key': RAPIDAPI_KEY,
                'q': search,
                'sort': 'r'}
   
    headers = {"X-RapidAPI-Key": RAPIDAPI_TOKEN}

    response = requests.get("https://community-food2fork.p.rapidapi.com/search", 
                            params=payload, headers=headers)

    print(response)
    data = response.json()
    print(data)
    recipes = data['recipes']

    # ingredient_search = search.split(", ")
    # print(ingredient_search)

    # recipe_data = []
    # for recipe in recipes:
    #     rId = recipe['recipe_id']
    #     payload_get = {'key': "8b50ec6830e40ad83082a5b276c51a39",
    #                     'rId': rId}
    #     response = requests.get("https://community-food2fork.p.rapidapi.com/get", 
    #                         params=payload_get, headers=headers)
    #     data = response.json()
    #     ingredients = data['recipe']['ingredients']
    #     print(ingredients)


    # search = request.args.get('ingredients')
    # payload = {'i': search}
    # response = requests.get("http://www.recipepuppy.com/api/", params=payload)
    # data = response.json()
    # print(data)
    # recipes = data['results']


    return render_template("recipe_results.html", recipes=recipes)


@app.route('/movies')
def movie_results():
    """Output of movie recommendations user queried"""

    query_movie = request.args.get('movie')
    payload = {'api_key': MOVIEDB_KEY,
                'query': query_movie}
    

    response = requests.get(MOVIEDB_URL + "search/movie", 
                            params=payload)
    
    data = response.json()
    print(data)
    results = data['results']
    movie_ids = [ movie['id'] for movie in results ]
    print(movie_ids)

    movie_data = []
    for movie_id in movie_ids:
        payload = {'api_key': MOVIEDB_KEY}
        movie_recc = requests.get(MOVIEDB_URL + f"movie/{movie_id}/recommendations", params=payload)
        data = movie_recc.json()
        movie_data.append(data['results'])
        print(movie_data)

    return render_template("movie_recc_results.html", movie_data=movie_data[0])


@app.route('/login', methods=['GET'])
def login_form():
    """Show login form and register button """

    return render_template("login_form.html")


@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""

    # Get form variables
    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("Looks like you have not yet registered! Please register")
        return redirect("/register")

    if user.password != password:
        flash("Incorrect password")
        return redirect("/login")

    session["user_id"] = user.user_id

    flash("Logged in")
    return redirect("/")


@app.route('/register', methods=['GET'])
def register_form():
    """Show form for user signup."""

    return render_template("register_form.html")


@app.route('/register', methods=['POST'])
def register_process():
    """Process registration."""

    # Get form variables
    email = request.form.get("email")
    password = request.form.get("password")
    name = request.form.get("name")
    age = int(request.form.get("age"))
    zipcode = request.form.get("zipcode")

    # Add the new user to the database
    user = User.query.filter_by(email=email).first()

    if not user:
        new_user = User(email=email, password=password, name=name, 
                        age=age, zipcode=zipcode)
        db.session.add(new_user)
        db.session.commit()
    else:
        flash("This email is already in use, please try logging in!")
        redirect("/login")

    flash(f"Thank you for registering, {name}")
    return redirect("/login")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
