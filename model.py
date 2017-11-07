"""Models and database functions for my project."""

from flask_sqlalchemy import SQLAlchemy
from correlation import pearson

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of goal tracking website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(75), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    f_name = db.Column(db.String(30), nullable=False)
    l_name = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.Int, nullable=True)
    birth_date = db.Column(db.DateTime, nullable=True)
    gender = db.Column(db.String(1), nullable=True)
    # notifications = db.Column(db.Boolean, default=False)
    

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s name=%s>" % (self.user_id, 
                                                       self.email,
                                                       self.f_name)


class Goal(db.Model):
    """Goals entered by user on goal tracking website"""

    __tablename__ = "goals"

    goal_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    num_times = db.Column(db.Int, nullable=False)
    date_created = db.Column(db.DateTime, nullable=True)
    repeat = db.Column(db.Boolean, default=False)
    type_id = db.Column(db.Int, db.ForeignKey('types.type_id'), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Goal goal_id=%s name=%s type_id=%s repeat=%s>" % (self.goal_id,
                                                                   self.name,
                                                                   self.type_id,
                                                                   self.repeat)


class Track(db.Model):
    """Tracks/completions of user goals on goal tracking website."""

    __tablename__ = "tracks"

    track_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    goal_id = db.Column(db.Integer,
                        db.ForeignKey('goals.goal_id'),
                        nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    num_comp = db.Column(db.Integer, default=0, nullable=False)

    # Define relationship to user
    user = db.relationship("User",
                           backref=db.backref("ratings",
                                              order_by=rating_id))

    # Define relationship to movie
    movie = db.relationship("Movie",
                            backref=db.backref("ratings",
                                               order_by=rating_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Track track_id=%s goal_id=%s num_comp=%s>" % (
            self.track_id, self.goal_id, self.num_comp)


##############################################################################
# Helper functions

def connect_to_db(app, db_uri="postgresql:///ratings"):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def example_data():
    """create example data for the test database."""

    u1 = User(user_id=666,
              email='test@test.com',
              password='Password',
              age=50,
              zipcode='94117')

    u2 = User(user_id=420,
              email='me@email.com',
              password='Secret',
              age=42,
              zipcode='98346')

    m1 = Movie(movie_id=1,
               title='Killer Cupcakes',
               released_at='1995-01-01 00:00:00',
               imdb_url='http://www.imbd/killercupcakes.com')

    m2 = Movie(movie_id=2,
               title='Raspberry Rampage',
               released_at='1994-01-01 00:00:00',
               imdb_url='http://www.imbd/raspramp.com')

    r1 = Rating(rating_id=1, movie_id=1, user_id=666, score=4)
    r2 = Rating(rating_id=2, movie_id=2, user_id=666, score=1)
    r3 = Rating(rating_id=3, movie_id=1, user_id=420, score=5)
    r4 = Rating(rating_id=4, movie_id=2, user_id=420, score=3)

    db.session.add_all([u1, u2, m1, m2, r1, r2, r3, r4])
    db.session.commit()


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
