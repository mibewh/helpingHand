from flask import Flask, render_template, g, redirect, request, session, flash
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask.ext.bcrypt import Bcrypt

app = Flask(__name__, template_folder='../templates')
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.debug=True
app.secret_key = 'this is soooooo secret right?'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://iokqwvbpdqkbsb:kVe-Z6R1qqoAXF2uqtvvNW_kYY@ec2-54-204-15-48.compute-1.amazonaws.com:5432/d983rtid8h2rk'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
db.engine.connect()

bcrypt = Bcrypt(app)

from user import users
from request import requestsBP
from contract import contractBP
from rating import ratings
from notify import notifications
from schedule import scheduler
app.register_blueprint(users)
app.register_blueprint(requestsBP)
app.register_blueprint(contractBP)
app.register_blueprint(ratings)
app.register_blueprint(notifications)
app.register_blueprint(scheduler)

@app.route('/')
def index():
	return render_template('index.jade', testvar='hiya')

@app.route('/create', methods=('GET', 'POST'))
def create():
	return render_template('create.jade')

@app.before_request
def before_request():
	if session.get('user'):
		sql = text('''SELECT COUNT(notification_id) FROM notification
					  WHERE name=:user AND viewed=FALSE;''')
		results = db.engine.execute(sql, user=session.get('user'))
		results = results.fetchone()
		session['notifications'] = results[0]