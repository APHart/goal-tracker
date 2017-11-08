"""Models and database functions for my project."""

from flask_sqlalchemy import SQLAlchemy
from correlation import pearson
from datetime import datetime
from datetime import date

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

    friends = db.relationship("User",
                              secondary="friendships",
                              primaryjoin=
                              "User.user_id==Friendship.friend_A_id",
                              secondaryjoin=
                              "User.user_id==Friendship.friend_B_id")

    sharers = (
        db.relationship("User",
                        secondary="sharings",
                        primaryjoin="User.user_id==Sharing.sharee_id",
                        secondaryjoin="User.user_id==Sharing.sharer_id"))

    sharees = (
        db.relationship("User",
                        secondary="sharings",
                        primaryjoin="User.user_id==Sharing.sharer_id",
                        secondaryjoin="User.user_id==Sharing.sharee_id"))
    

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
    date_created = db.Column(db.DateTime, nullable=True)
    repeat = db.Column(db.Boolean, default=False)
    type_id = db.Column(db.String(1),
                        db.ForeignKey('types.type_id'),
                        nullable=False)
    
    # Define relationship to type
    goal_type = db.relationship("Type",
                                backref=db.backref("goals",
                                order_by=type_id, goal_id))

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
    num_times = db.Column(db.Int, nullable=False)
    num_comp = db.Column(db.Integer, default=0, nullable=False)

    # Define relationship to user
    user = db.relationship("User",
                           backref=db.backref("tracks",
                                              order_by=goal_id))

    # Define relationship to goal
    goal = db.relationship("Goal",
                            backref=db.backref("tracks",
                                               order_by=goal_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Track track_id=%s goal_id=%s num_comp=%s>" % (
            self.track_id, self.goal_id, self.num_comp)


class Type(db.Model):
    """Goal types on goal tracking website"""

    __tablename__ = "types"

    type_id = db.Column(db.String(1), primary_key=True)
    type_name = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Type type_id=%s type_name=%s>" % (self.type_id, 
                                                   self.type_name)

class High_Five(db.Model):
    """High Fives given/received by user on goal tracking website"""

    __tablename__ = "high_fives"

    hfive_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.track_id'))
    hfiver_id = db.Column(db.Integer,
                          db.ForeignKey('user.user_id'),
                          nullable=False)
    hfive_date = db.Column(db.DateTime, nullable=False)

    # Define relationship to track
    track = db.relationship("Track",
                            backref=db.backref("high_fives",
                                               order_by=track_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<High Five hfive_id=%s track_id=%s hfiver_id=%s>" % (
                                                                self.hfive_id,
                                                                self.track_id,
                                                                self.hfiver_id)


class Friendship(db.Model):
    """Friendships between users on goal tracking website"""

    __tablename__ = "friendships"

    fship_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    friend_A_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    friend_B_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    # Define relationship to track
    user = db.relationship("User",
                            backref=db.backref("friends"))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Friendship fship_id=%s User=%s Friend=%s repeat=%s>" % (
                                                              self.fship_id,
                                                              self.friend_A_id,
                                                              self.friend_B_id)


class Sharing(db.Model):
    """Goal tracks shared between users on goal tracking website"""

    __tablename__ = "sharings"

    share_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.track_id'))
    sharer_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    sharee_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Sharing share_id=%s track_id=%s sharer_id=%s sharee_id=%s>" % (
                                                                self.share_id,
                                                                self.track_id,
                                                                self.sharer_id,
                                                                self.sharee_id)


##############################################################################
# Helper functions

def connect_to_db(app, db_uri="postgresql:///goal-tracker"):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def example_data():
    """create example data for the test database."""

    u1 = User(user_id=123,
              email='test@test.com',
              password='Password',
              f_name='Bob'
              l_name='Smith'
              phone=4151234321,
              birth_date='1982-01-01 00:00:00')

    u2 = User(user_id=321,
              email='user2@email.com',
              password='Secret',
              f_name='Sue',
              l_name='Doe',
              phone=5148900987,
              birth_date='1982-01-31 00:00:00')

    g1 = Goal(goal_id=1,
              name='Hit the Gym!'
              date_created=date.fromtimestamp(timestamp)
    repeat = db.Column(db.Boolean, default=False)
    type_id =

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
