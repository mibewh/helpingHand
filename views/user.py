from flask import Flask, render_template, g, redirect, request, session, flash, Blueprint
from sqlalchemy.sql import text
from . import db, app, bcrypt
from schedule import formatSchedule

users = Blueprint('users', __name__, template_folder=app.template_folder+'/users')

def login(username, password):
	#check if user, password combo is in the database
	#Client table
	sql=text('''SELECT password FROM client
				WHERE client_username=:username;''')
	result=db.engine.execute(sql, username=username, password=password)
	result = result.fetchone();
	if result != None and bcrypt.check_password_hash(result[0], password):
		session['user'] = username
		session['type'] = 'client'
		return True
	#Worker table
	sql=text('''SELECT password FROM worker
				WHERE worker_username=:username;''')
	result=db.engine.execute(sql, username=username, password=password)
	result = result.fetchone();
	if result != None and bcrypt.check_password_hash(result[0], password):
		session['user'] = username
		session['type'] = 'worker'
		return True

	return False

@users.route('/login', methods=('GET', 'POST'))
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

@users.route('/logout')
def logoutPage():
	if session['user']:
		session['user'] = None
		flash('Logged out successfuly')
	return redirect('/')

def verifyNew(username):
	sql=text('''SELECT * FROM client WHERE client_username=:username;''')
	result=db.engine.execute(sql, username=username)
	result=[r[0] for r in result]
	if result != []:
		return False
	sql=text('''SELECT * FROM worker WHERE worker_username=:username;''')
	result=db.engine.execute(sql, username=username)
	result=[r[0] for r in result]
	if result != []:
		return False

	return True

def register(username, password, email, phone, type):
	pw_hash = bcrypt.generate_password_hash(password)
	if type == 'client':
		sql=text('''INSERT INTO client(client_username, password, email, phone)VALUES(:username, :password, :email, :phone);''')
	else:
		sql=text('''INSERT INTO worker(worker_username, password, email, phone)VALUES(:username, :password, :email, :phone);''')
	db.engine.execute(sql, username=username, password=pw_hash, email=email, phone=phone)

@users.route('/register', methods=('GET', 'POST'))
def registerPage():
	if request.method=='POST':
		if not verifyNew(request.form.get('username')):
			flash('Username already taken')
			return render_template('register.jade')
		register(request.form.get('username'), request.form.get('password'), request.form.get('email'), request.form.get('phone'), request.form.get('typeuser'))
		login(request.form.get('username'), request.form.get('password'))
		return redirect('/schedule')

	return render_template('register.jade')

def getProfile(username):
	sql=text('''SELECT client_username, email, phone FROM client WHERE client_username=:username;''')
	result=db.engine.execute(sql, username=username)
	ret = result.fetchone()
	if ret:
		return (ret, 'Client')
	sql=text('''SELECT worker_username, email, phone FROM worker WHERE worker_username=:username;''')
	result=db.engine.execute(sql, username=username)
	return (result.fetchone(), 'Worker')


@users.route('/profile/<username>')
def profile(username):
	result, type = getProfile(username)
	if result:
		days = formatSchedule('worker', username)
		sql = text('''SELECT SUM(rating), COUNT(rating)
			FROM contract
			WHERE rating IS NOT NULL AND
				worker_username=:username''')
		result2 = db.engine.execute(sql, username=username)
		result2 = result2.fetchone()
		totalRating = result2[0]
		numRatings = result2[1]
		avgRating = None
		if numRatings != 0:
			avgRating = 1.0*totalRating/numRatings
		sql = text('''SELECT to_char(time_finish AT TIME ZONE 'CDT', 'MM/DD/YY'), rating, review, tag
			FROM contract c, service_request s
			WHERE worker_username=:username AND time_finish IS NOT NULL
			AND c.service_id=s.service_id
			ORDER BY time_finish DESC
			LIMIT 5;''')
		reviews = db.engine.execute(sql, username=username).fetchall()
		return render_template('profile.jade', username=result[0], email=result[1], phone=result[2], type=type, days=days, rating=avgRating, numRatings=totalRating, reviews=reviews)
	return redirect('/')

@users.route('/profile/<username>/edit', methods=('GET', 'POST'))
def editProfile(username):
	if request.method=='POST':
		sql=text('''UPDATE client
					SET email=:email, phone=:phone
					WHERE client_username=:username;''')
		db.engine.execute(sql, email=request.form.get('email'), phone=request.form.get('phone'), username=username)
		sql=text('''UPDATE worker
					SET email=:email, phone=:phone
					WHERE worker_username=:username;''')
		db.engine.execute(sql, email=request.form.get('email'), phone=request.form.get('phone'), username=username)
		return redirect('/profile/'+username)

	if session['user'] == username:
		user, type = getProfile(username)
		return render_template('editProfile.jade', username=user[0], email=user[1], phone=user[2])
	return redirect('/profile/'+username)

@users.route('/profile/<username>/delete')
def deleteProfile(username):
	if session['user'] == username:
		sql = text('''DELETE FROM worker_schedule WHERE worker_username=:username;''')
		db.engine.execute(sql, username=username)
		sql=text('''DELETE FROM client WHERE client_username=:username;''')
		db.engine.execute(sql, username=username)
		sql=text('''DELETE FROM worker WHERE worker_username=:username;''')
		db.engine.execute(sql, username=username)
		session['user'] = None
		flash('Account deleted.')
		return redirect('/')

	return redirect('/profile/'+username)