from flask import Flask, render_template


app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.debug=True

@app.route('/')
def index():
	return render_template('index.jade', testvar='hiya')
	
@app.route('/create')
def create():
	return render_template('create.jade')

@app.route('/login')
def logins():
	return render_template('login.jade')

@app.route('/register')
def login():
	return render_template('register.jade')

# @app.route('/profile/<username>')
# def profile(username):
# 	#Check if logged in
