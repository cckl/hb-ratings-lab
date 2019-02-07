"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/users/<user_id>')
def show_user(user_id):

    user = User.query.get(user_id)

    return render_template("user_details.html", user=user)


@app.route('/register')
def register_form():
    """Register page."""
    return render_template("register_form.html")


@app.route('/register', methods=['POST'])
def register_process():
    """Process user registration page."""

    email = request.form.get('email')
    password = request.form.get('password')

    db.session.add(User(email=email, password=password))
    db.session.commit()

    return redirect("/")


@app.route('/login')
def login_form():
    """Login page."""

    return render_template("login_form.html")


@app.route('/login', methods=['POST'])
def login_process():
    """Process login page."""

    email = request.form.get('email')
    password = request.form.get('password')    

    # checks for existing user
    try:
        user_data = db.session.query(User.user_id, User.email, User.password).filter(User.email == email).one()
    except:
        flash('Please create an account.')
        return redirect('/register')
    
    # unpack user data
    user_id = user_data[0]
    user_email = user_data[1]
    user_password = user_data[2]

    # check if input password matches user password in database
    if password == user_password:
        session['login'] = user_id
        flash('Successfully logged in.')
        return redirect("/")
    else:
        flash('Sorry, incorrect password!')
        return redirect('/login')

    return render_template("login_form.html")


@app.route('/logout')
def logout_process():
    """Logout user."""

    session['login'] = None

    flash('Successfully logged out')
    return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.run(port=5000, host='0.0.0.0')
