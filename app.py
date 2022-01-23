from datetime import date, datetime, time
from time import strptime
from turtle import position
from flask import Flask, redirect, request, session
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session     
import requests
import json

app = Flask(__name__)
YOUR_GEOLOCATION_KEY = '03e73814098e46909e701d6073b1d27c'
# URL to send the request to
request_url = 'https://ipgeolocation.abstractapi.com/v1/?api_key=' + YOUR_GEOLOCATION_KEY
response = requests.get(request_url)
result = json.loads(response.content)

#app.config['SECRET_KEY'] = 'super secret key'
app.secret_key = 'IH session id1234'
app.config['SESSION_TYPE'] = 'filesystem'

ENV = "dev"
#client_secrects_file = os.path.join(pathlib.Path)

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///login.db"
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://inzftzpcqmrmaw:1b283ef78ddfa53275c338335b3f3e074c85abf55bd44b98d3b9411c88297f42@ec2-34-236-136-215.compute-1.amazonaws.com:5432/dbommchfej1gh9"

#GOOGLE_CLIENT_ID = "218660666241-ba7co81a25o9hd6epjh8jnk866car88l.apps.googleusercontent.com"
# flow = Flow.from_client_secrets_file(client_secrets_file=)
db = SQLAlchemy(app)
Session(app)

class Login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100))
    password = db.Column(db.String(25))
    type = db.Column(db.String(10))

    def __repr__(self):
        return 'User '+str(self.id)

class Emergency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lattitude = db.Column(db.Integer())
    longitude = db.Column(db.Integer())
    type = db.Column(db.String(20))

    def __repr__(self):
        return 'User '+str(self.id)


@app.route('/')
def home():
    usernow = session.get('userid')
    return render_template('home.html', usernow = usernow, responce = response)

@app.route('/logout')
def logout():
    session['userid'] = None
    return redirect('/')

@app.route('/ers')
def ers():
    if session.get('userid') == None:
        return redirect('/login')
    else:
        user = session.get('userid')
        type1 = session.get('type')
        emergencies = Emergency.query.filter_by(type = type1)
        return render_template('ers.html', emergencies=emergencies, user1 = user)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['uname']
        password = request.form['pass']
        users = Login.query.filter_by(user=email, password=password)
        if users != None and users.count() > 0:
            if str(email) == str(users[0].user) and str(password) == str(users[0].password):
                    session['userid'] = users[0].user
                    session['type'] = users[0].type
                    return redirect('/ers')
            else:
                return render_template('login.html', alert = "True")
        else:
             return render_template('login.html', alert = "True")   
    else:
        return render_template('login.html')

@app.route('/emergency/police')
def emergency():
        emergency = Emergency(lattitude=result['latitude'], longitude=result['longitude'], type = "Police")
        db.session.add(emergency)
        db.session.commit()
        return redirect('/')



@app.route('/emergency/fire')
def emergency2():
        emergency = Emergency(lattitude=result['latitude'], longitude=result['longitude'], type = "Fire")
        db.session.add(emergency)
        db.session.commit()
        return redirect('/')


@app.route('/emergency/medical')
def emergency3():
        emergency = Emergency(lattitude=result['latitude'], longitude=result['longitude'], type = "Medical")
        db.session.add(emergency)
        db.session.commit()
        return redirect('/')

@app.errorhandler(404)
def err(e):
    return render_template('err.html')

if __name__ == "__main__":
    app.run(debug=True)