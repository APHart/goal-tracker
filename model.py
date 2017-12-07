"""Models and database functions for my project."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from psycopg2.extras import DateTimeRange
from datetime import datetime
from sqlalchemy_utils import DateRangeType
# from sqlalchemy.dialects.postgresql import DATERANGE
from sqlalchemy.dialects.postgresql import DATE
from sqlalchemy.dialects.postgresql import TIME

db = SQLAlchemy()


##############################################################################
#Constants

MAX_TEXT_LENGTH = 100

# Model definitions

class User(db.Model):
    """User on goal tracking website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(75), nullable=False)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    f_name = db.Column(db.String(30), nullable=True)
    l_name = db.Column(db.String(30), nullable=True)
    phone = db.Column(db.String(10), nullable=True)
    birth_date = db.Column(db.DATE, nullable=True)
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
                                                       self.username)

class Type(db.Model):
    """Goal types."""

    __tablename__ = "types"

    type_id = db.Column(db.String(1), primary_key=True)
    type_name = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Type type_id=%s type_name=%s>" % (self.type_id, 
                                                   self.type_name)


class Goal(db.Model):
    """Goals entered by user."""

    __tablename__ = "goals"

    goal_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.user_id'),
                        nullable=False)
    type_id = db.Column(db.String(1),
                        db.ForeignKey('types.type_id'),
                        nullable=False)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
    
    # Define relationship to type
    goal_type = db.relationship("Type",
                                backref=db.backref("goals",
                                order_by=type_id))

    #Define relationship to user
    user = db.relationship("User", backref=db.backref("goals", order_by=name))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Goal goal_id=%s name=%s type_id=%s user_id=%s>" % (self.goal_id,
                                                                   self.name,
                                                                   self.type_id,
                                                                   self.user_id)


class Track(db.Model):
    """Tracks/instances of user goals."""

    __tablename__ = "tracks"

    track_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    goal_id = db.Column(db.Integer,
                        db.ForeignKey('goals.goal_id'),
                        nullable=False)
    duration = db.Column(DateRangeType, nullable=False)
    repeat = db.Column(db.Boolean, default=False)
    num_times = db.Column(db.Integer, nullable=False)

    #DATES: may want to store as DATERANGE data type rather than separate 
    #start/end. May also need to have convo with Katie if dates stored to not
    #jsonify

    # Define relationship to user
    user = db.relationship("User",
                           secondary="goals",
                           backref=db.backref("tracks",
                                              order_by=goal_id))

    # Define relationship to goal
    goal = db.relationship("Goal",
                            backref=db.backref("tracks",
                                               order_by=goal_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Track track_id=%s goal_id=%s num_times=%s>" % (
            self.track_id, self.goal_id, self.num_times)


class Completion(db.Model):
  """Completion information for track of user goal."""

  __tablename__ = 'completions'

  comp_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  track_id = db.Column(db.Integer,
                       db.ForeignKey('tracks.track_id'),
                       nullable=False)
  comp_date = db.Column(db.DATE, nullable=False)
  comp_location = db.Column(db.String(50))
  comp_time = db.Column(db.TIME)
  comp_notes = db.Column(db.String(150))

  # Define relationship to track
  track = db.relationship("Track",
                          backref=db.backref("completions",
                                             order_by=comp_id))


class High_Five(db.Model):
    """High Fives given/received by user on goal tracking website"""

    __tablename__ = "high_fives"

    hfive_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    comp_id = db.Column(db.Integer,
                        db.ForeignKey('completions.comp_id'),
                        nullable=False)
    hfiver_id = db.Column(db.Integer,
                          db.ForeignKey('users.user_id'),
                          nullable=False)
    hfive_date = db.Column(db.DateTime, nullable=False)

    # Define relationship to track
    track = db.relationship("Completion",
                            backref=db.backref("high_fives"))
                            #come back to order_by

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<High Five hfive_id=%s comp_id=%s hfiver_id=%s>" % (
                                                                self.hfive_id,
                                                                self.comp_id,
                                                                self.hfiver_id)


class Friendship(db.Model):
    """Friendships between users on goal tracking website"""

    __tablename__ = "friendships"

    fship_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    friend_A_id = db.Column(db.Integer,
                            db.ForeignKey('users.user_id'),
                            nullable=False)
    friend_B_id = db.Column(db.Integer,
                            db.ForeignKey('users.user_id'),
                            nullable=False)

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
    track_id = db.Column(db.Integer,
                         db.ForeignKey('tracks.track_id'),
                         nullable=False)
    sharer_id = db.Column(db.Integer,
                          db.ForeignKey('users.user_id'),
                          nullable=False)
    sharee_id = db.Column(db.Integer,
                          db.ForeignKey('users.user_id'),
                          nullable=False)

    # Define relationship to track
    track = db.relationship("Track", backref=db.backref("sharings"))

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

    u1 = User(
              email='moe@stooges.com',
              username='Moe',
              password='Password',
              f_name='Moe',
              l_name='Howard',
              phone='4151234321',
              birth_date='1982-01-01')

    u2 = User(
              email='larry@stooges.com',
              username='Larry',
              password='Pancakes',
              f_name='Larry',
              l_name='Fine',
              phone='4159876543',
              birth_date='1984-12-31')

    u3 = User(
              email='curly@stooges.com',
              username='Curly',
              password='Pickles',
              f_name='Jerome',
              l_name='Howward',
              phone='4159876543',
              birth_date='1986-12-31')

    typ1 = Type(type_id='P', type_name='Push')
    typ2 = Type(type_id='L', type_name='Limit')
    typ3 = Type(type_id='H', type_name='Head-2-heaD')

    g1 = Goal(user_id=1,
              type_id='P',
              name='Hit the Gym',
              date_created='2017-12-02 08:45:00')

    g2 = Goal(user_id=2,
              type_id='L',
              name='Eat pancakes',
              date_created='2017-12-02 08:45:00')

    t1 = Track(goal_id=1,
               duration='[2017-12-05,2017-12-11]',
               num_times=3)

    t2 = Track(goal_id=2,
               duration='[2017-12-05,2017-12-11]',
               num_times=2)

    c1 = Completion(track_id=1,
                    comp_date='2017-12-05',
                    comp_location='Dumbells Athletic Club',
                    comp_time='16:30',
                    comp_notes='Awesome')

    c2 = Completion(track_id=1,
                    comp_date='2017-12-6',
                    comp_location='My new gym',
                    comp_time='06:30',
                    comp_notes='Too early!')

    c3 = Completion(track_id=2,
                    comp_date='2017-12-05',
                    comp_location='Favorite Diner',
                    comp_time='16:30',
                    comp_notes='Awesome')

    c4 = Completion(track_id=2,
                    comp_date='2017-12-6',
                    comp_location='Not as good diner',
                    comp_time='06:30',
                    comp_notes='Too early!')

    c5 = Completion(track_id=2,
                    comp_date='2017-12-6',
                    comp_location='Favorite Diner',
                    comp_time='09:30',
                    comp_notes='Broke my limit!')

    hf1 = High_Five(comp_id=1,
                    hfiver_id=1,
                    hfive_date='2017-11-19 11:00')

    f1 = Friendship(friend_A_id=1,
                    friend_B_id=2)

    sh1 = Sharing(track_id=1,
                  sharer_id=1,
                  sharee_id=2)



    db.session.add_all([u1,u2,u3,typ1,typ2,typ3,g1,g2,t1,t2])
    db.session.commit()
    # import pdb; pdb.set_trace()

    db.session.add_all([c1,c2,c3,c4,c5])
    db.session.commit()

    db.session.add_all([hf1])
    db.session.commit()

    db.session.add_all([f1])
    db.session.commit()

    db.session.add_all([sh1])
    db.session.commit()


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    # app = Flask(__name__)
    connect_to_db(app)
    db.create_all()
    print "Connected to DB."
