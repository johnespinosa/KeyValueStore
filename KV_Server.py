from flask import Flask, request, session, g, \
    render_template, render_template, request, redirect
from flask.helpers import make_response
from flask.wrappers import Request
from flask_sqlalchemy import SQLAlchemy
import flask.views
import hashlib
import sqlite3
from werkzeug.security import gen_salt
from Carbon.Aliases import false
import json
import os

app = Flask(__name__)
app.config.from_object(__name__)

app.secret_key = 'w\x9a\xfek\x89uG\xd4\xe3\xc7\x10\x89\x0ei\xc3[\x8a\xacp\xb4B\x93\xcd\x14'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
app.config['DATABASE'] = os.path.join(PROJECT_ROOT, 'hashtable.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE']
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(700), nullable=False)
    password = db.Column(db.String(700), nullable=False)
    salt = db.Column(db.String(30), nullable=False)

class DBHashTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(700), nullable=False)
    key = db.Column(db.String(700), nullable=False)
    value = db.Column(db.String(700), nullable=False)

'''
db.drop_all()
db.create_all()
'''

@app.route('/')
def landing_page():
    if 'username' in session:
        username = session['username']
        if(user_exists(username)):
            return render_template('hashtable.html')
    return render_template('login.html')
  
@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect('/')

@app.route('/login', methods = ['POST'])
def login():
    '''
    Handle the user logging in.
    @return the html associated with a successful or unsuccessful login
    '''
    if request.method == 'POST':
        username_input = request.form['username_input']
        password_input = request.form['password_input']
        if(login_successful(username_input, password_input)):
            session['username'] = username_input
    return redirect('/')
    
def login_successful(username_input, password_input):
    if(not user_exists(username_input)):
        return False
    
    user_info = get_user_info(username_input)
    hashed_password_input = produce_hashed_password(password_input, user_info['salt'])
    return user_info['password'] == hashed_password_input
    
@app.route('/sign_up')
def sign_up():
    '''
    Load the html associated with a user clicked the sign up href.
    @return html associated with sign up.
    '''
    return render_template("sign_up.html")

@app.route('/submit_sign_up', methods = ['POST'])
def submit_sign_up():
    '''
    Handle user submitting information in an attempt to sign up for Taunch.
    @return the html associated with a successful or unsuccessful sign up.
    '''
    username_input = request.form['username_input']
    password_input = request.form['password_input']
    
    # if the new username does not already exist and does not contain a "," character and is of reasonable length
    if(not user_exists(username_input) and not ("," in username_input) and len(username_input) > 0 and len(username_input) < 60):
        
        # salt and hash password
        salt = gen_salt(30)
        hashed_password = produce_hashed_password(password_input, salt)
            
        # create user
        newUser = User(user = username_input, password = hashed_password, salt = salt)
        db.session.add(newUser)
        db.session.commit()
        
        return redirect('/')
    else:
        return render_template('sign_up.html', sign_up_fail=True)

def produce_hashed_password(password, salt):
    hashed_password = password
    for i in range(200):
        hashed_password = hashlib.sha512(hashed_password + salt).hexdigest()
    return hashed_password

def user_exists(username):
    return not get_user_info(username) is None

def get_user_info(username):   
    user_info = User.query.filter_by(user = username).first()
    if(not user_info is None):
        result_user_info = {}
        result_user_info['user'] = user_info.user
        result_user_info['password'] = user_info.password
        result_user_info['salt'] = user_info.salt
        return result_user_info
    else:
        return None

@app.route('/get_value', methods = ['GET', 'POST'])   
def get_value():
    logged_in_user = session['username']
    key_input = request.form['key_input']
    if(key_exists(logged_in_user, key_input)):
        kv_pair = get_kv_pair(logged_in_user, key_input)
        return json.dumps({'key' : kv_pair['key'], 'value' : kv_pair['value']})
    else:
        return json.dumps({'key': key_input})
   
@app.route('/update_hashtable', methods = ['GET', 'POST'])
def update_hashtable():
    logged_in_user = session['username']
    key_input = request.form['key_input']
    value_input = request.form['value_input']
    
    if(key_exists(logged_in_user, key_input)):
        update_kv_pair(logged_in_user, key_input, value_input)
    else:
        insert_kv_pair(logged_in_user, key_input, value_input) 
    return json.dumps({'success':True})

def update_kv_pair(username, key, value):
    kv_pair = DBHashTable.query.filter_by(user = username, key = key).first()
    kv_pair.value = value
    db.session.commit()
    
def insert_kv_pair(username, key, value):
        newKVPair = DBHashTable(user = username, key = key, value = value)
        db.session.add(newKVPair)
        db.session.commit()
    
def key_exists(username, key):
    return not get_kv_pair(username, key) is None

def get_kv_pair(username, key):
    kv_pair = DBHashTable.query.filter_by(user = username, key = key).first()
    if (not kv_pair is None):
        result_kv_pair = {}
        result_kv_pair['user'] = kv_pair.user
        result_kv_pair['key'] = kv_pair.key
        result_kv_pair['value'] = kv_pair.value
        return result_kv_pair
    else:
        return None

def connect_db():
    return sqlite3.connect(app.config['DATABASE']) # LINE 17

@app.before_request
def before_request():
    g.db = connect_db() # LINE 22

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

