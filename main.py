from flask import Flask, render_template, g, redirect, request, session
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text


app = Flask(__name__)
app.jinja_env.add_extension(	'pyjade.ext.jinja.PyJadeExtension')
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

@app.route('/login', methods=('GET', 'POST'))
def loginPage():
	if request.method == 'POST':
		#Check the login
		if request.form.get('username')=='admin' and request.form.get('password')=='admin':
			session['user'] = 'admin'
			return render_template('index.jade')
		else:
			return render_template('index.jade')
	else:
		return render_template('login.jade')

@app.route('/logout')
def logoutPage():
	if session['user']:
		session['user'] = None
	return redirect('/')

@app.route('/register', methods=('GET', 'POST'))
def register():
	if request.method=='POST':
		sql=text('''select * from client where client_username='{0}';'''\
			.format(request.form.get('username')))
		result=db.engine.execute(sql)
		result=[r[0] for r in result]
		if  result != []:
			print('Already exists')
			return redirect('/')
		sql=text('''insert into client(client_username, password, email)values('{0}', '{1}', '{2}');'''\
		.format(request.form.get('username'), request.form.get('password'), request.form.get('email')))
		db.engine.execute(sql)
		return redirect('/')
	return render_template('register.jade')

@app.route('/user/<username>')
def profile(username): pass

# @app.route('/profile/<username>')
# def profile(username):
# 	#Check if logged in
