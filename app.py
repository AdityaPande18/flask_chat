from time import localtime, strftime
import os
from flask import Flask, render_template, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from werkzeug import debug

from form_fields import *
from models import *

app = Flask(__name__)
app.secret_key = "Secret Key"

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login = LoginManager(app)
login.init_app(app)

socketio = SocketIO(app)
ROOMS = ["Public", "Coding", "Games", "News", "Fun"]

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route("/", methods=['GET', 'POST'])
def index():
    reg_form = RegistrationForm()
    if reg_form.validate_on_submit():
        username = reg_form.username.data
        password = reg_form.password.data

        hashed_password = pbkdf2_sha256.hash(password)
        
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        session.pop('_flashes', None)
        flash('Registered succesfully. Please login.', 'success')

        return redirect(url_for('login'))

    return render_template("index.html", form=reg_form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

    if login_form.validate_on_submit():
        user_object = User.query.filter_by(username=login_form.username.data).first()
        login_user(user_object)
        session.pop('_flashes', None)
        flash('You have logged in successfully', 'success')
        return redirect(url_for('chat'))

    return render_template("login.html", form=login_form)

@app.route("/logout", methods=['GET'])
def logout():
    logout_user()
    session.pop('_flashes', None)
    flash('You have logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route("/chat", methods=['GET', 'POST'])
def chat():
    if not current_user.is_authenticated:
        session.pop('_flashes', None)
        flash('Please login', 'danger')
        return redirect(url_for('login'))
    return render_template("chat.html", username=current_user.username, rooms=ROOMS)

@socketio.on('message')
def message(data):
    data['time_stamp'] = strftime('%I:%M%p', localtime())
    send(data, room=data['room'], broadcast=True)

@socketio.on('join')
def join(data):
    join_room(data['room'])
    send({'msg': data['username'] + " has joined the " + data['room'] + " room.",}, room=data['room'])


@socketio.on('leave')
def leave(data):
    leave_room(data['room'])
    send({'msg': data['username'] + " has left the " + data['room'] + " room.",}, room=data['room'])

if __name__ == "__main__":
    socketio.run(app, debug=True)