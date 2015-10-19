from flask import Flask, render_template, g, redirect, request, session, flash
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.debug=True
app.secret_key = 'this is soooooo secret right?'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://iokqwvbpdqkbsb:kVe-Z6R1qqoAXF2uqtvvNW_kYY@ec2-54-204-15-48.compute-1.amazonaws.com:5432/d983rtid8h2rk'
db = SQLAlchemy(app)
db.engine.connect() 

from user import users
app.register_blueprint(users)

@app.route('/')
def index():
	return render_template('index.jade', testvar='hiya')

@app.route('/create', methods=('GET', 'POST'))
def create():
	return render_template('create.jade')