"""Goal Tracker"""

from jinja2 import StrictUndefined
from flask import (Flask, jsonify, render_template, redirect,
                   request, flash, session, url_for)
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

#helper functions regarding completion(s) for a given goal.
def completion_total(track_id):
    """Get total, if any, completions for given track."""

    # track_id = request.args.get("t_id")

    track = Track.query.get(track_id)
    completion_list = track.completions
    count = 0

    if completion_list:
        for completion in completion_list:
            count += 1

    return count

def completion_percentage(track_id):
    """Calculates the completion percentage/progress for given track."""

    total = completion_total(track_id)

    track = Track.query.get(track_id)

    if track.goal.type_id == "P":
        percentage = (float(total) / track.num_times) * 100

    elif track.goal.type_id == "L":
        if total <= track.num_times:
            percentage = 100
        else:
            percentage = 100 - ((float(total) / track.num_times) * 100)

    return percentage

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
        new_user = User(email=email, username=username, password=password)
        #user_id = new_user.user_id
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.user_id
        flash('''Successfully registered. Let's start tracking your goals!''')
        return redirect(url_for("user_dashboard", username=username))


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
        # return redirect("/user/<username>")
        return redirect(url_for("user_dashboard", username=user.username))
    

@app.route("/logout", methods=["POST"])
def logout():
    """User account logout."""

    del session['user_id']
    flash('You have successfully logged out...bye!')

    return redirect("/")

@app.route("/user/<username>")
def user_dashboard(username):
    """Show user dashboard info."""

    user_id = session['user_id']
    user = User.query.get(user_id)
    today = date.today()
    tracks = user.tracks
    current_tracks = []
    friends = user.friends

    for track in tracks:
        if track.duration.length.days == 6:
            length = "week"
        elif track.duration.length.days == 24:
            length = "month"

        if today in track.duration:
            track.percent_comp = completion_percentage(track.track_id)
            track.length = length
            current_tracks.append(track)
            # print track.duration.lower
            # print track.duration.upper
            # print track.duration.length.days
            # print type(track.duration.length.days)

    return render_template("user-dashboard.html",
                           user=user, current_tracks=current_tracks,
                           user_friends=friends)

@app.route("/friend-share-info", methods=['POST'])
def friend_share_info():
    """Get user friend info for friend share page url."""

    friend_name = request.form.get("friend_name")
    user_id = session['user_id']
    user = User.query.get(user_id)

    # return redirect(url_for("user_friend_goalshare_view", 
    #                         username=user.username,
    #                         friend_name=friend_name))

    results = {
        "username": user.username,
        "friend_name": friend_name
    }

    return jsonify(results)


@app.route("/user/<username>/GoalShare-<friend_name>")
def user_friend_goalshare_view(username,friend_name):
    """Show user & friend goals"""

    print "in share route"

    user_id = session['user_id']
    user = User.query.get(user_id)
    today = date.today()
    tracks = user.tracks
    current_tracks = []
    friend = User.query.filter(User.username == friend_name).first()
    friend_tracks = friend.tracks
    current_friend_tracks = []

    for track in tracks:
        if track.duration.length.days == 6:
            length = "week"
        elif track.duration.length.days == 24:
            length = "month"

        if today in track.duration:
            track.percent_comp = completion_percentage(track.track_id)
            track.length = length
            current_tracks.append(track)

    for track in friend_tracks:
        if track.duration.length.days == 6:
            length = "week"
        elif track.duration.length.days == 24:
            length = "month"

        if today in track.duration:
            track.percent_comp = completion_percentage(track.track_id)
            track.length = length
            current_friend_tracks.append(track)

    print current_tracks
    print current_friend_tracks

    return render_template("friend-goal-share.html",
                           user=user, current_tracks=current_tracks,
                           friend=friend, friend_tracks=current_friend_tracks)

@app.route("/get-goals.json", methods=['GET'])
def goal_list():
    """Get list of user goals for autocomplete data in 'new goal' input."""

    user_id = session['user_id']
    user = User.query.get(user_id)
    goal_list = [goal.name for goal in user.goals]

    return jsonify(goal_list)

@app.route("/add-goal.json", methods=['POST'])
def add_goal():
    """Add new user goal (if not present) and new goal track."""

    #get form values for goal record
    user_id = session['user_id']
    user = User.query.get(user_id)
    type_id = request.form.get("goal_type")
    name = request.form.get("new_goal_name")
    date_created = datetime.now()

    #if goal has not been used previously, create new goal in db
    goal_list = [goal.name for goal in user.goals]

    if name not in goal_list:
        new_goal = Goal(user_id=user_id,
                  type_id=type_id,
                  name=name,
                  date_created=date_created)

        db.session.add(new_goal)
        db.session.commit()

    #get form values and calculate end date for track record
    duration = (int(request.form.get("duration")) * 6)
    num_times = request.form.get("num_times")
    start_date = request.form.get("start_date")
    end_date = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=(duration))
    end_date = str(end_date.date())

    added_goal = Goal.query.filter(Goal.user_id == user_id , 
                                   Goal.name == name).first()


    new_track = Track(goal_id=added_goal.goal_id,
               duration='[' + start_date + ',' + end_date + ']',
               num_times=num_times)

    db.session.add(new_track)
    db.session.commit()

    today = date.today()
    if today in new_track.duration:
        add_button = True

        percent_comp = completion_percentage(new_track.track_id)

        if duration == 6:
            new_track.length = "week"
        elif duration == 24:
            new_track.length = "month"

    else:
        add_button = False

    results = {
        'id': new_track.track_id, 
        'name': added_goal.name, 
        'duration': str(new_track.duration), 
        'num_times': num_times,
        'type': added_goal.type_id,
        'length': new_track.length,
        'percent_comp': percent_comp,
        'add': add_button,
    }

    return jsonify(results)

@app.route("/get-completions.json", methods=['GET'])
def get_completion_data():
    """Get total completions, if any, & percent complete for given track."""

    track_id = request.args.get("t_id")
    count = completion_total(track_id)
    percent = completion_percentage(track_id)

    results = {'count': count,
              'percent': percent}

    return jsonify(results)

@app.route("/add-completion.json", methods=['POST'])
def add_completion():
    """Add new completion info for user goal track."""

    #get form values for goal record
    user_id = session['user_id']
    user = User.query.get(user_id)
    track_id = request.form.get("track-id")
    comp_date = request.form.get("comp-date")
    comp_location = request.form.get("comp-loc")
    comp_time = request.form.get("comp-time")
    comp_notes = request.form.get("comp-notes")

    if not comp_time:
        comp_time = "00:00:00"

    date_range = (Track.query.filter(Track.track_id == track_id).first()).duration
    comp_date = (datetime.strptime(comp_date, '%Y-%m-%d')).date()

    if comp_date in date_range:

        new_comp = Completion(track_id=track_id,
                              comp_date=comp_date,
                              comp_location=comp_location, 
                              comp_time=comp_time,
                              comp_notes=comp_notes)

        db.session.add(new_comp)
        db.session.commit()

        return "Success"

    else:

        return "Fail"

@app.route("/completion-chart.json")
def completion_chart_data():
    """Generates doughnut chart for percent complete for given goal track."""

    track = request.args.get("track_id")
    percent_comp = completion_percentage(track.track_id)

    data_dict = {
        "labels": ["percent complete"],
        "datasets": [
            {
                "data": [percent_comp],
                "backgroundColor": ["#36A2EB"],
                "hoverBackgroundColor": ["#36cfeb"]
            }]
    }

    return jsonify(data_dict)

@app.route("/add-friend.json", methods=['POST'])
def add_friend():
    """Add new user friend (if username present in db)."""

    #get form values for goal record
    user_id = session['user_id']
    user = User.query.get(user_id)
    friend_username = request.form.get("friend-username")
    
    #if friend_username registerd user in db, create new user friendship
    friend = User.query.filter(User.username == friend_username).first()
    existing_friend = Friendship.query.filter(Friendship.friend_A_id == user_id, 
                                              Friendship.friend_B_id == 
                                              friend.user_id).first()

    if friend and existing_friend is None:
        new_friendship1 = Friendship(friend_A_id=user_id,
                                     friend_B_id=friend.user_id,
                                     ) 
        new_friendship2 = Friendship(friend_A_id=friend.user_id,
                                     friend_B_id=user_id,
                                     )

        db.session.add_all([new_friendship1,new_friendship2])
        db.session.commit()
        add_button = True

    else:
        add_button = False

    results = {
        'id': friend.user_id, 
        'name': friend.username, 
        'add': add_button,
    }

    return jsonify(results)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')