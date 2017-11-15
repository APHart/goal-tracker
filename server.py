"""Goal Tracker"""

from jinja2 import StrictUndefined
from flask import (Flask, jsonify, render_template, redirect,
                   request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension
from model import (connect_to_db, db, User, Goal, Track, Completion, Type,
                   High_Five, Friendship, Sharing)
from datetime import (date, datetime, timedelta)
from sqlalchemy_utils import DateRangeType


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "SECRET"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route("/join", methods=["GET"])
def register_form():
    """Shows user registration/join form."""

    return render_template("register.html")


@app.route("/join", methods=["POST"])
def register_process():
    """Adds new user and redirects to user dashboard."""

    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter((User.email == email) |
                             (User.username == username)).first()

    if user:
        flash('That email address is already registered, please log in.')
        return redirect("/login")
    else:
        new_user = User(email=email, password=password)
        #user_id = new_user.user_id
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.user_id
        flash('''Successfully registered. Let's start tracking your goals!''')
        return redirect("/user/<username>")


@app.route("/login", methods=["GET"])
def login():
    """User account login."""
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_process():
    """User account login process."""

    loginname = request.form.get("loginname")
    password = request.form.get("password")

    user = User.query.filter((User.email == loginname) | 
                             (User.username == loginname)).first()

    if not user or user.password != password:
        flash('Incorrect username, email or password.')
        return redirect("/login")

    elif user and user.password == password:
        session['user_id'] = user.user_id
        flash('You have successfully logged in...woohoo!')
        # url = "/user/" + str(user.username)
        return redirect("/user/<username>")
    

@app.route("/logout", methods=["POST"])
def logout():
    """User account logout."""

    del session['user_id']
    flash('You have successfully logged out...bye!')

    return redirect("/")


@app.route("/user/<username>")
def user_dashboard(username):
    """Show user details."""

    user_id = session['user_id']
    user = User.query.get(user_id)
    tracks = user.tracks

    print tracks

    return render_template("user-dashboard.html",
                           user=user, tracks=tracks)

@app.route("/get-goals.json")
def goal_list():
    """Get list of user goals for autocomplete data in 'new goal' input."""

    user_id = session['user_id']
    user = User.query.get(user_id)
    goal_list = [goal.name for goal in user.goals]

    return jsonify(goal_list)

@app.route("/add-goal.json", methods=['POST'])
def add_goal():
    """Add new user goal (if not present) and new goal track."""

    # print request.form

    user_id = session['user_id']
    user = User.query.get(user_id)
    type_id = request.form.get("goal_type")
    name = request.form.get("new_goal_name")
    date_created = datetime.now()

    goal_list = [goal.name for goal in user.goals]

    if name not in goal_list:
        new_goal = Goal(user_id=user_id,
                  type_id=type_id,
                  name=name,
                  date_created=date_created)

        db.session.add(new_goal)
        db.session.commit()

    duration = int(request.form.get("duration")) * 7
    num_times = request.form.get("num_times")
    start_date = request.form.get("start_date")
    end_date = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=(duration))
    end_date = str(end_date.date())

    goals = user.goals
    print goal_id

    new_track = Track(goal_id=new_goal.goal_id,
               duration='[' + start_date + ',' + end_date + ')',
               num_times=num_times)

    db.session.add(new_track)
    db.session.commit()

    return "Success!"


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')