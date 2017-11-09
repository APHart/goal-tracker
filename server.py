"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, jsonify, render_template, redirect,
                   request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import (connect_to_db, db, User, Goal, Track, Completion, Type,
                   High_Five, Friendship, Sharing)


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

    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter(User.email == email).first()

    # print users[0]
    if user:
        flash('That email address is already registered, please log in.')
        return redirect("/login")
    else:
        new_user = User(email=email, password=password)
        #user_id = new_user.user_id
        db.session.add(new_user)
        db.session.commit()
        flash('''Successfully registered. Let's start tracking your goals!''')
        return redirect("/user/<new_user.user_id>")
        #return redirect("/<user_id>", user_id=user_id)


@app.route("/login", methods=["GET"])
def login():
    """User account login."""
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_process():
    """User account login process."""

    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter(User.email == email).first()
    if not user or user.password != password:
        flash('Incorrect email or password.')
        return redirect("/login")

    elif user and user.password == password:
        session['user_id'] = user.user_id
        flash('You have successfully logged in...woohoo!')
        url = "/user/" + str(user.user_id)
        return redirect(url)
    

@app.route("/logout", methods=["POST"])
def logout():
    """User account logout."""
    # session.pop removes user_id key/value from session, does not set value to none
    # session.pop('user_id', None)
    # print session['user_id']

    #delete user_id from session
    del session['user_id']
    flash('You have successfully logged out...bye!')

    return redirect("/")


@app.route("/user/<user_id>")
def user_dashboard(user_id):
    """Show user details."""

    user = User.query.filter(User.user_id == user_id).first()
    print user

    age = user.age
    zipcode = user.zipcode

    user_goals = user.ratings

    return render_template("user-dashboard.html",
                           user_id=user_id,
                           age=age,
                           zipcode=zipcode,
                           ratings=user_ratings)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')