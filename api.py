"""++++++++++++++++++++++++++API helper functions++++++++++++++++++++++++++++"""

def get_edamam_payload():
    """Helper function to get payload backbone for edamam API request"""

    dietary = request.args.get("dietary")
    health = request.args.getlist("health[]")

    integer = randint(0,50)

    payload = {'q': "", 'app_id': EDAMAM_ID, 'app_key': EDAMAM_KEY, 'health': 'alcohol-free',
                'calories': f'{randint(1000,1500)}-{randint(3000,6000)}','from': integer, 'to': integer+99}
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