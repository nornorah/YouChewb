"""Recipe and Movie Rec website"""
from pprint import pformat
import os
import requests
from random import randint, choice
from jinja2 import StrictUndefined
from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Recipe, Movie, Activity
from ast import literal_eval
from datetime import datetime, timedelta
from passlib.hash import sha256_crypt



app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This raises an error instead.
app.jinja_env.undefined = StrictUndefined

# Retrieve tokens and keys, set moviedb and edamam urls for API call

EDAMAM_KEY = os.environ.get('EDAMAM_KEY')
EDAMAM_ID = os.environ.get('EDAMAM_ID')

MOVIEDB_KEY = os.environ.get('MOVIEDB_KEY')

YOUTUBE_KEY = os.environ.get('YOUTUBE_KEY')

EDAMAM_URL = "https://api.edamam.com/search"
MOVIEDB_URL = "https://api.themoviedb.org/3/"



def get_edamam_payload():
    """Helper function to get payload backbone for edamam API request"""

    dietary = request.args.getlist("dietary")
    health = request.args.getlist("health")

    payload = {'q': "", 'app_id': EDAMAM_ID, 'app_key': EDAMAM_KEY, 'to': '100'}

    if (dietary and health):
        payload.update({'diet': dietary, 'health': health})
    elif dietary:
        payload.update(diet=dietary)
    elif health:
        payload.update(health=health)

    return payload


def request_edamam_api(payload):
    """Helper function to make edamam API request and retrieve data"""

    response = requests.get(EDAMAM_URL, params=payload)

    data = response.json()
    recipe_results = data['hits']
    recipes =  [ recipe['recipe'] for recipe in recipe_results ]
    
    return recipes


def save_recipe_info(recipe_info):
    """Helper function to save the recipe selected to database"""

    (recipe_url, recipe_image, recipe_name, recipe_id) = recipe_info
    session['recipe_id'] = recipe_id

    # access session to retrieve user_id when user is logged in
    user_id = session.get("user_id")

    recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()

    # add entry to recipes table if user is logged in and recipe does not exist
    if not recipe:
        if user_id: 
            new_recipe_entry = Recipe(recipe_image=recipe_image, recipe_id=recipe_id,
                                    recipe_name=recipe_name, recipe_url=recipe_url)
            db.session.add(new_recipe_entry)
            db.session.commit()

        # reroute the user to login if not logged in
        else:
            flash("Please log in to add this recipe!")
            return redirect("/login")


def save_movie_info(movie_info):
    """Helper function to save the movie selected to database"""

    (movie_url, movie_image, movie_name, movie_id) = movie_info
    session['movie_id'] = movie_id

    # access session to retrieve user_id when user is logged in
    user_id = session.get("user_id")

    movie = Movie.query.filter_by(movie_id=movie_id).first()

    # add entry to movies table if movie does not exist
    if not movie:
        new_recipe_entry = Movie(movie_image=movie_image, movie_id=movie_id,
                                    movie_name=movie_name, movie_url=movie_url)
        db.session.add(new_recipe_entry)
        db.session.commit()


@app.route('/')
def index():
    """Homepage."""

    return render_template("index.html")


@app.route('/get_random_recipe')
def get_random_recipe():
    """Show form to get a random recipe recommendation"""

    return render_template("get_random_recipe.html")


@app.route('/display_random_recipe', methods=['GET'])
def display_random_recipe():
    """Display random recipes from edamam API call; 'GET' shows one random recipe"""

    payload = get_edamam_payload()
    payload.update({'nutrients%5BCA%5D': '0%2B',
                    'health': 'alcohol-free',
                    'calories': f'{randint(300,1000)}-{randint(2000,6000)}'})

    recipes = request_edamam_api(payload)

    if not session.get("activities"):
        recipe = choice(recipes)
        return render_template("random_recipe_results.html", recipe=recipe)
        # return jsonify(recipe)
    else:
        del session["activities"]
        return render_template("random_recipes.html", recipes=recipes)


@app.route('/get_random_movie')
def get_random_movie():
    """Get and show random movie from moviedb API call"""
    
    genre_dict = {'action': 28, 'adventure': 12, 'animation': 16, 
                'comedy': 35, 'crime': 80, 'documentary': 99,
                'drama': 18, 'family': 10751, 'fantasy': 14, 
                'history': 36, 'horror': 27, 'music': 10402,
                'mystery': 9648, 'romance': 10749, 'science fiction': 878,
                'thriller': 53, 'war': 10752, 'western': 37}

    genres = request.args.getlist("genre")
    year = request.args.get("year")
    recipe_info = request.args.get("recipe")
    
    if recipe_info:
        recipe_info = literal_eval(recipe_info)
        save_recipe_info(recipe_info)

    genre = [ genre_dict[genre] for genre in genres ]

    payload = {'api_key': MOVIEDB_KEY, 'page': randint(1,50)}

    if (genre and year):
        payload.update({'release_date.gte': year, 'with_genres': genre})
    elif genre:
        payload.update({'with_genres': genre})
    elif year:
        payload.update({'release_date.gte': year})

    response = requests.get(MOVIEDB_URL + "discover/movie", params=payload)

    data = response.json()
    movie = choice(data['results'])

    return render_template("random_movie_results.html", movie=movie)


@app.route('/get_recipe_ingr')
def get_recipe_ingr():
    """Allow user to search for recipe by ingredients and choose option for movie rec"""
    
    return render_template("get_recipe_ingr.html")


@app.route('/display_ingr_results')
def display_ingr_results():
    """Display recipe results from user input (ingredients)"""

    search = request.args.get("ingredients")

    payload = get_edamam_payload()
    payload.update(q=search)

    recipes = request_edamam_api(payload)

    return render_template("recipe_ingr_results.html", recipes=recipes)


@app.route('/get_movie_rec')
def get_movie_rec():
    """Save recipe info and show form for user to provide a movie to get movie rec"""

    recipe_info = request.args.get("recipe")
    
    if recipe_info:
        recipe_info = literal_eval(recipe_info)
        save_recipe_info(recipe_info)    

    return render_template("get_movie_rec.html")


@app.route('/display_movie_rec')
def movie_results():
    """Output of movie recommendations from the movie title user queried"""
    
    movie_title = request.args.get("movie")
    payload = {'api_key': MOVIEDB_KEY,
                'query': movie_title}

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

    return render_template("movie_rec_results.html", movie_data=movie_data[0][:15])


@app.route('/display_activity')
def display_activity():
    """Display user's choice of recipe and movie and save to database"""

    movie_info = literal_eval(request.args.get("movie"))
    save_movie_info(movie_info)

    recipe_id = session.get("recipe_id")
    movie_id = session.get("movie_id")

    recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()
    movie = Movie.query.filter_by(movie_id=movie_id).first()

    payload = {'part': 'snippet',
    'maxResults': 5,
    'q': movie.movie_name,
    'type': 'video',
    'videoDuration':'long',
    'videoType': 'movie',
    'key': YOUTUBE_KEY}

    response = requests.get("https://www.googleapis.com/youtube/v3/search", params=payload)
    data = response.json()
    video_id = data['items'][0]['id']['videoId']

    return render_template("display_activity.html", recipe=recipe, 
                            movie=movie, video=video_id)


@app.route('/save_activity')
def save_activity():
    """Save recipe and movie user chose to the database and user's profile"""

    user_id = session.get("user_id")

    if user_id:
        recipe_id = session.get("recipe_id")
        movie_id = session.get("movie_id")

        date_today = (datetime.today()-timedelta(hours=8)).strftime("%Y-%m-%d")

        activity = Activity.query.filter_by(user_id=user_id, movie_id=movie_id, 
                                            recipe_id=recipe_id).first()

        if not activity:
            new_entry = Activity(user_id=user_id, movie_id=movie_id,
                                recipe_id=recipe_id, date=date_today)
            db.session.add(new_entry)
            db.session.commit()
        
        session["activities"] = "activity"

        return redirect("/display_random_recipe")    

    else:
        flash("Please log in to save this activity!")
        return redirect("/login")


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Show login form and register button and then process login"""
    
    if request.method=='GET':
        user = session.get("user_id")
        if not user:
            return render_template("login_form.html")
        else:
            flash("Already logged in. Please make a selection")
            return redirect("/")
    else:
            # Get form variables
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Looks like you have not yet registered! Please register")
            return redirect("/register")

        if not sha256_crypt.verify(password, user.password):
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


@app.route('/register', methods=['GET', 'POST'])
def register_form():
    """Show form for user signup. Then process registration."""

    if request.method == 'GET':
        return render_template("register_form.html")
    else:
        # Get form variables
        email = request.form.get("email")
        password = request.form.get("password")
        first_name = request.form.get("fname")
        last_name = request.form.get("lname")

        password = sha256_crypt.encrypt(password)

        # Add the new user to the database
        user = User.query.filter_by(email=email).first()

        if not user:
            new_user = User(email=email, password=password, fname=first_name, 
                            lname=last_name)
            db.session.add(new_user)
            db.session.commit()
            flash(f"Thank you for registering, {first_name}")
            return redirect("/login")

        else:
            flash("This email is already in use, please try logging in!")
            redirect("/login")



@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile_form():
    """Show form for updating user profile. Then update the user profile."""

    # if request.method == 'GET':
    #     if not session.get("user_id"):
    #         flash("Please log in")
    #         return redirect("/login")
    #     else:
    #         return render_template("update_profile_form.html")
    # else:


@app.route('/display_activity_log')
def display_activity_log():
    """Show recipe and movie for the date user selects"""
    user_id = session.get("user_id")
    date = request.args.get("date")

    #group by
    if user_id:
        activity = Activity.query.filter_by(user_id=user_id, date=date).all()







if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
