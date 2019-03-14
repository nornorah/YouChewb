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


"""//////////////////////////////////////////////////////////////////////////"""
#HELPER FUNCTIONS
"""//////////////////////////////////////////////////////////////////////////"""


def get_edamam_payload():
    """Helper function to get payload backbone for edamam API request"""

    dietary = request.args.get("dietary")
    health = request.args.getlist("health[]")

    integer = randint(0,50)

    payload = {'q': "", 'app_id': EDAMAM_ID, 'app_key': EDAMAM_KEY, 'health': 'alcohol-free',
                'calories': (randint(600,1000),'-',randint(2000,6000)),
                'from': integer, 'to': integer+99}

    print(payload)

    if dietary:
        payload.update({'diet': dietary})
    if health:
        payload.update({'health': health})   

    return payload


def request_edamam_api(payload):
    """Helper function to make edamam API request and retrieve data"""

    response = requests.get(EDAMAM_URL, params=payload)

    data = response.json()
    recipe_results = data['hits']
    recipes =  [ recipe['recipe'] for recipe in recipe_results ]
    
    return recipes


def get_movie_payload(genres=[], gte='', lte=''):
    """Helper function to build payload backbone with genre and year info for movies"""

    genre_dict = {'action': 28, 'adventure': 12, 'animation': 16, 
                'comedy': 35, 'crime': 80, 'documentary': 99,
                'drama': 18, 'family': 10751, 'fantasy': 14, 
                'history': 36, 'horror': 27, 'music': 10402,
                'mystery': 9648, 'romance': 10749, 'science fiction': 878,
                'thriller': 53, 'war': 10752, 'western': 37}
    
    genre = [ str(genre_dict[genre]) for genre in genres ]
    genre = ','.join(genre)

    payload = {'api_key': MOVIEDB_KEY}

    if genre:
        payload.update({'with_genres': genre})
    if gte:
        payload.update({'release_date.gte': gte})
    if lte:
        payload.update({'release_date.lte': lte})

    return payload


def request_movie_api(payload):
    """Helper function to make moviedb API request and retrieve data"""

    response = requests.get(MOVIEDB_URL + "discover/movie", params=payload)
    data = response.json()
    movie = choice(data['results'])

    return movie


def save_recipe_info(recipe):
    """Helper function to save the recipe selected to database"""

    recipe_id = recipe['uri'][-32:]
    recipe_entry = Recipe.query.filter_by(recipe_id=recipe_id).first()

    # add entry to recipes table if recipe does not already exist
    if not recipe_entry:
        new_recipe_entry = Recipe(recipe_image=recipe['image'], recipe_id=recipe_id,
                                recipe_name=recipe['label'], recipe_url=recipe['url'])
        db.session.add(new_recipe_entry)
        db.session.commit()

    session['recipe_id'] = recipe_id


def save_movie_info(movie):
    """Helper function to save the movie selected to database"""

    movie_id = movie['id']
    movie_entry = Movie.query.filter_by(movie_id=movie_id).first()

    # add entry to movies table if movie does not already exist
    if not movie_entry:
        new_movie_entry = Movie(movie_image=f"https://image.tmdb.org/t/p/w500/{movie['poster_path']}",
                                movie_id=movie_id, movie_name=movie['title'], 
                                movie_url=f"https://www.themoviedb.org/movie/{movie_id}")
        db.session.add(new_movie_entry)
        db.session.commit()

    session['movie_id'] = movie_id




"""//////////////////////////////////////////////////////////////////////////"""
#ROUTES
"""//////////////////////////////////////////////////////////////////////////"""


@app.route('/')
def index():
    """Homepage."""
    if session.get("user_id")==None:
        session['user_id'] = ''

    return render_template("index.html")


@app.route('/display_random_recipe_and_movie', methods=['GET'])
def display_random_recipe_and_movie():
    """Display random recipes from edamam API call"""
### FROM index.html

    payload = get_edamam_payload()
    recipes = request_edamam_api(payload)

    recipe = choice(recipes)
    save_recipe_info(recipe)

    payload = get_movie_payload()
    payload.update({'page': randint(1,50)})

    movie = request_movie_api(payload)
    save_movie_info(movie)

    return render_template("random_recipe_and_movie_results.html", recipe=recipe, movie=movie)


@app.route('/get_random_recipe')
def get_random_recipe():
    """Retrieve data which is the payload info from AJAX and return a recipe"""
### FROM random_recipe_and_movie_results.html


    payload = get_edamam_payload()
    recipes = request_edamam_api(payload)
    recipe = choice(recipes)

    save_recipe_info(recipe)

    return jsonify(recipe)


@app.route('/get_random_movie')
def get_random_movie():
    """Retrieve data which is the payload info from AJAX and return a movie"""
### FROM random_recipe_and_movie_results.html    

    genres = request.args.getlist("with_genres[]")
    gte = request.args.get("release_date.gte")
    lte = request.args.get("release_date.lte")

    payload = get_movie_payload(genres, gte, lte)

    response = requests.get(MOVIEDB_URL + "discover/movie", params=payload)
    data = response.json()
    page = data['total_pages']
    if int(page)>1000:
        page = 50
    payload.update({'page': randint(1, page)})
    movie = request_movie_api(payload)
    save_movie_info(movie)

    return jsonify(movie)


@app.route('/display_recipe_search_results')
def display_recipe_search_results():
    """Display recipe results from user input (ingredients/recipe name/filters)"""
### FROM random_recipes_search.html

    q = request.args.get("search")
    calories = request.args.get("calories")
    dietary = request.args.get("dietary")
    health = request.args.getlist("health")

    payload = get_edamam_payload()

    if q:
        payload.update({'q': q})
    if calories:
        payload.update({'calories': calories})
    if dietary:
        payload.update({'diet': dietary})
    if health:
        payload.update({'health': health})

    recipes = request_edamam_api(payload)

    return render_template("random_recipes_search.html", recipes=recipes)



@app.route('/display_movie_rec_by_search')
def movie_results():
    """Output of movie recommendations from the movie title user queried"""
### FROM random_movies_search.html    


    movie_title = request.args.get("search")
    payload = {'api_key': MOVIEDB_KEY}

    payload.update({'query': movie_title})

    response = requests.get(MOVIEDB_URL + "search/movie", 
                            params=payload)
    data = response.json()
    results = data['results']
    movie_ids = [ movie['id'] for movie in results ]

    movies = []

    for movie_id in movie_ids:
        payload = {'api_key': MOVIEDB_KEY}
        movie_recc = requests.get(MOVIEDB_URL + f"movie/{movie_id}/recommendations", 
                                params=payload)
        data = movie_recc.json()
        movies.append(data['results'])
    print(movies)

    return render_template("random_movies_search.html", movies=movies[0])


@app.route('/display_movie_rec_by_filters')
def movie_results_by_filter():
    """Display movie recommendations with filters user selected"""
### FROM random_movies_search.html

    genres = request.args.getlist("genre")
    gte = request.args.get("gte")
    lte = request.args.get("lte")

    payload = get_movie_payload(genres, gte, lte)
    response = requests.get(MOVIEDB_URL + "discover/movie", params=payload)
    data = response.json()

    page = data['total_pages']
    if int(page)>1000:
        page = 50

    payload.update({'page': randint(1, page)})
    response = requests.get(MOVIEDB_URL + "discover/movie", params=payload)
    data = response.json()
    movies = data['results']

    print(movies)

    return render_template("random_movies_search.html", movies=movies)



@app.route('/get_youtube_video')
def get_youtube_video():
    """Retrieve movie title from AJAX and make Youtube API call"""
### FROM random_recipe_and_movie_results.html

    q = request.args.get("q")

    payload = {'part': 'snippet',
    'maxResults': 5,
    'q': q,
    'type': 'video',
    'videoDuration':'long',
    'videoType': 'movie',
    'key': YOUTUBE_KEY}

    response = requests.get("https://www.googleapis.com/youtube/v3/search", params=payload)
    data = response.json()
    video_id = data['items'][0]['id']['videoId']

    return jsonify(video_id)


@app.route('/save_activity')
def save_activity():
    """Save recipe and movie user chose to the database and user's profile"""
### FROM random_recipe_and_movie_results.html


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

    return ('', 204)



@app.route('/save_movie_activity')
def save_movie_activity():
    """Save movie info into movies table"""
### FROM random_movies_search.html

    movie_info = literal_eval(request.args.get("movie"))
    (movie_url, movie_image, movie_name, movie_id) = movie_info

    movie_entry = Movie.query.filter_by(movie_id=movie_id).first()

    # add entry to movies table if movie does not already exist
    if not movie_entry:
        new_movie_entry = Movie(movie_image=movie_image, movie_id=movie_id,
                                movie_name=movie_name, movie_url=movie_url)

        db.session.add(new_movie_entry)
        db.session.commit()

    return ('', 204)



@app.route('/display_random_recipes')
def display_random_recipes():
    """Display random recipes for user to browse through"""
### FROM index.html

    payload = get_edamam_payload()
    recipes = request_edamam_api(payload)

    return render_template("random_recipes_search.html", recipes=recipes)


@app.route('/save_recipe')
def save_recipe():
    """Save recipe info to database and later to activities"""
### FROM random_recipes_search.html    

    recipe_info = literal_eval(request.args.get("recipe"))
    (recipe_url, recipe_image, recipe_name, recipe_id) = recipe_info

    recipe_entry = Recipe.query.filter_by(recipe_id=recipe_id).first()

    # add entry to recipes table if recipe does not already exist
    if not recipe_entry:
        new_recipe_entry = Recipe(recipe_image=recipe_image, recipe_id=recipe_id,
                                recipe_name=recipe_name, recipe_url=recipe_url)
        db.session.add(new_recipe_entry)
        db.session.commit()

    session['recipe_id'] = recipe_id

    # payload = get_movie_payload()
    # payload.update({'page': randint(1,50)})

    # response = requests.get(MOVIEDB_URL + "discover/movie", params=payload)
    # data = response.json()
    # movies = data['results']

    return redirect('/display_movie_rec_by_filters')

"""++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"""


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Show login form and register button and then process login"""
    
    if request.method=='GET':
        user = session.get("user_id")
        if not user:
            return render_template("login_form.html")
        else:
            flash("Already logged in. Please make a selection")
    else:
        # Get form variables
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user:
            if sha256_crypt.verify(password, user.password):
                session["user_id"] = user.user_id #set session of user as their user_id in database
                flash("Logged in", 'alert-success')
                return redirect("/")
            else:
                flash("Incorrect password", 'alert-danger')
                return redirect("/")
        else:
            flash("Looks like you have not yet registered! Please register", 'alert-info')
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


@app.route('/display_activity_log')
def display_activity_log():
    """Show recipe and movie for the date user selects"""

    user_id = session.get("user_id")
    activities = Activity.query.filter_by(user_id=user_id).all()
    dates = [ activity.date for activity in activities ]
    recipes = [ Recipe.query.filter_by(recipe_id=activity.recipe_id).first() for activity in activities ]
    movies = [ Movie.query.filter_by(movie_id=activity.movie_id).first() for activity in activities ]
    
    activity_info = zip(dates, recipes, movies)
    return render_template("activity_log.html", activity_info=activity_info)


@app.route('/display_activity_')
def display_activity():
    """ """



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    app.debug = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
