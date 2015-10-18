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

@app.route('/')
def index():
	return render_template('index.jade', testvar='hiya')

@app.route('/create', methods=('GET', 'POST'))
def create():
	return render_template('create.jade')

def login(username, password):
	#check if user, password combo is in the database
	#Client table
	sql=text('''select * from client
				where client_username='{0}' AND password='{1}';'''\
				.format(username, password))
	result=db.engine.execute(sql)
	result=[r[0] for r in result]
	if result != []:
		session['user'] = username
		session['type'] = 'client'
		return True
	#Worker table
	sql=text('''select * from worker
				where worker_username='{0}' AND password='{1}';'''\
				.format(username, password))
	result=db.engine.execute(sql)
	result=[r[0] for r in result]
	if result != []:
		session['user'] = username
		session['type'] = 'worker'
		return True

	return False

@app.route('/login', methods=('GET', 'POST'))
def loginPage():
	if request.method == 'POST':
		#Check the login
		if not login(request.form.get('username'), request.form.get('password')):
			#Flash stuff and print error
			flash('Invalid Login')
			return render_template('login.jade')		
		return redirect('/profile/'+session['user'])

	else:
		return render_template('login.jade')

@app.route('/logout')
def logoutPage():
	if session['user']:
		session['user'] = None
		flash('Logged out successfuly')
	return redirect('/')

@app.route('/register', methods=('GET', 'POST'))
def register():
	if request.method=='POST':
		sql=text('''select * from client where client_username='{0}';'''\
			.format(request.form.get('username')))
		result=db.engine.execute(sql)
		result=[r[0] for r in result]
		if  result != []:
			flash('Username already taken')
			return render_template('register.jade')
		sql=text('''insert into client(client_username, password, email)values('{0}', '{1}', '{2}');'''\
		.format(request.form.get('username'), request.form.get('password'), request.form.get('email')))
		db.engine.execute(sql)
		login(request.form.get('username'), request.form.get('password'))
		return redirect('/profile/'+request.form.get('username'))

	return render_template('register.jade')

@app.route('/profile/<username>')
def profile(username):
	if session['user'] == username:
		return render_template('profile.jade', username=username)
	return redirect('/')