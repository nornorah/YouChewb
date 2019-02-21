"""Recipe and Movie Rec website"""
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

# Retrieve tokens and keys, set moviedb url
RAPIDAPI_TOKEN = os.environ.get('RAPIDAPI_TOKEN')
RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY')
MOVIEDB_KEY = os.environ.get('MOVIEDB_KEY')

EDAMAM_KEY = os.environ.get('EDAMAM_KEY')
EDAMAM_ID = os.environ.get('EDAMAM_ID')

MOVIEDB_URL = "https://api.themoviedb.org/3/"


@app.route('/')
def index():
    """Homepage."""

    return render_template("index.html")

@app.route('/search_recipe')
def search_recipe():
    """Give user the option to choose search by recipe name or by ingredients"""

    return render_template("search_recipe.html")

@app.route('/search_recipe_name')
def search_by_recipe():
    """Allow user to search for recipe by name and choose option for movie rec"""

    return render_template("search_recipe_name.html")

@app.route('/recipe_name_results')
def recipe_name_results():
    pass

@app.route('/search_recipe_ingr')
def search_by_ingredients():
    """Allow user to search for recipe by ingredients and choose option for movie rec"""
    
    return render_template("search_recipe_ingredients.html")


@app.route('/recipe_ingr_results')
def recipe_ingr_results():

    search = request.args.get("ingredients")
    dietary = request.args.get("dietary")
    health = request.args.getlist("health")

    health = ", ".join(health)

    payload = {'q': search, 'app_id': EDAMAM_ID, 'app_key': EDAMAM_KEY}

    if (dietary and health):
        payload['diet'] = dietary
        payload['health'] = health
    elif dietary:
        payload['diet'] = dietary
    elif health:
        payload['health'] = health


    response = requests.get("https://api.edamam.com/search", params=payload)

    data = response.json()
    recipe_results = data['hits']
    recipes =  [ recipe['recipe'] for recipe in recipe_results ]
    ingredients = [ recipe['ingredientLines'] for recipe in recipes ]

    return render_template("recipe_ingr_results.html", recipes=recipes)


@app.route('/movies')
def movie_results():
    """Output of movie recommendations from the movie title user queried"""

    movie_query = request.args.get('movie')
    payload = {'api_key': MOVIEDB_KEY,
                'query': movie_query}
    

    response = requests.get(MOVIEDB_URL + "search/movie", 
                            params=payload)
    
    data = response.json()
    results = data['results']
    movie_ids = [ movie['id'] for movie in results ]

    movie_data = []
    for movie_id in movie_ids:
        payload = {'api_key': MOVIEDB_KEY}
        movie_recc = requests.get(MOVIEDB_URL + f"movie/{movie_id}/recommendations", 
                                params=payload)
        data = movie_recc.json()
        movie_data.append(data['results'])

    return render_template("movie_recc_results.html", movie_data=movie_data[0])


@app.route('/save_recipe/<recipe_id>')
def save_recipe(recipe_id):
    """Save recipe to user's database of recipes"""

    if session['user_id']:


    return render_template("update_profile_form.html")

@app.route('/save_to_activity/<recipe_id>')
def save_to_activity(recipe_id):


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

    session["user_id"] = user.user_id #set session of user as their user_id in database

    flash("Logged in")
    return redirect("/")


@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    flash("Logged Out.")
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
    first_name = request.form.get("fname")
    last_name = request.form.get("lname")

    # Add the new user to the database
    user = User.query.filter_by(email=email).first()

    if not user:
        new_user = User(email=email, password=password, fname=first_name, 
                        lname=last_name)
        db.session.add(new_user)
        db.session.commit()
    else:
        flash("This email is already in use, please try logging in!")
        redirect("/login")

    flash(f"Thank you for registering, {first_name}")
    return redirect("/login")

@app.route('/update_profile', methods=['GET'])
def update_profile_form():
    """Show form for updating user profile."""
    print(session["user_id"])
    if not session["user_id"]:
        flash("Please log in")
        return redirect("/login")
    else:
        return render_template("update_profile_form.html")

@app.route('/update_profile', methods=['POST'])
def update_profile_process():
    """Process update profile form."""







if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
