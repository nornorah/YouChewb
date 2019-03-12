"""Models and database functions for Recipes and Movie Rec project."""

from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of recipe and movie rec website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)

    activity = db.relationship("Activity", backref="users")

    def __repr__(self):
        """Provide helpful representation when printed."""
        
        return f"<User user_id={self.user_id} email={self.email}>"


class Recipe(db.Model):
    """Recipe info"""

    __tablename__ = "recipes"

    recipe_id = db.Column(db.String(50), primary_key=True)
    recipe_url = db.Column(db.String(500), nullable=False)
    recipe_image = db.Column(db.String(500), nullable=False)
    recipe_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""
        
        return f"<Recipe recipe_id={self.recipe_id} recipe_name={self.recipe_name}>"


class Movie(db.Model):
    """Movie info"""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, primary_key=True)
    movie_url = db.Column(db.String(500), nullable=False)
    movie_image = db.Column(db.String(500), nullable=False)
    movie_name = db.Column(db.String(100), nullable=False)    


    def __repr__(self):
        """Provide helpful representation when printed."""
        
        return f"<Movie movie_id={self.movie_id} movie_name={self.movie_name}>"


class Activity(db.Model):
    """Activity log for a user"""

    __tablename__ = "activities"

    entry_id = (db.Column(db.Integer, autoincrement=True, primary_key=True))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)    
    recipe_id = db.Column(db.String(50), db.ForeignKey('recipes.recipe_id'), nullable=False) 
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), nullable=False) 
    date = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""
        
        return f"<Activity entry_id={self.entry_id} user_id={self.user_id} date={self.date}>"









##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hbproject'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print("Connected to DB.")
