from flask import Flask, render_template, g, redirect, request, session, flash, Blueprint
from sqlalchemy.sql import text
from main import db

users = Blueprint('users', __name__)

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
	sql=text('''select * from client where client_username='{0}';'''\
			.format(request.form.get('username')))
	result=db.engine.execute(sql)
	result=[r[0] for r in result]
	if result != []:
		return False
	sql=text('''select * from worker where worker_username='{0}';'''\
			.format(request.form.get('username')))
	result=db.engine.execute(sql)
	result=[r[0] for r in result]
	if result != []:
		return False

	return True

def register(username, password, email, phone, type):
	if type == 'client':
		sql=text('''insert into client(client_username, password, email, phone)values('{0}', '{1}', '{2}', '{3}');'''\
		.format(username, password, email, phone))
	else:
		sql=text('''insert into worker(worker_username, password, email, phone)values('{0}', '{1}', '{2}', '{3}');'''\
		.format(username, password, email, phone))
	db.engine.execute(sql)

@users.route('/register', methods=('GET', 'POST'))
def registerPage():
	if request.method=='POST':
		if not verifyNew(request.form.get('username')):
			flash('Username already taken')
			return render_template('register.jade')
		register(request.form.get('username'), request.form.get('password'), request.form.get('email'), request.form.get('phone'), request.form.get('typeuser'))
		login(request.form.get('username'), request.form.get('password'))
		return redirect('/profile/'+request.form.get('username'))

	return render_template('register.jade')

def getProfile(username):
	sql=text('''select client_username, email, phone from client where client_username='{0}';'''\
			.format(username))
	result=db.engine.execute(sql)
	ret = result.fetchone()
	if ret:
		return (ret, 'Client')
	sql=text('''select worker_username, email, phone from worker where worker_username='{0}';'''\
			.format(username))
	result=db.engine.execute(sql)
	return (result.fetchone(), 'Worker')


@users.route('/profile/<username>')
def profile(username):
	result, type = getProfile(username)
	if result:
		return render_template('profile.jade', username=result[0], email=result[1], phone=result[2], type=type)
	return redirect('/')

@users.route('/profile/<username>/edit', methods=('GET', 'POST'))
def editProfile(username):
	if request.method=='POST':
		sql=text('''UPDATE client
					SET email='{0}', phone='{1}'
					WHERE client_username='{2}';'''
					.format(request.form.get('email'), request.form.get('phone'), username))
		db.engine.execute(sql)
		sql=text('''UPDATE worker
					SET email='{0}', phone='{1}'
					WHERE worker_username='{2}';'''
					.format(request.form.get('email'), request.form.get('phone'), username))
		db.engine.execute(sql)
		return redirect('/profile/'+username)

	if session['user'] == username:
		user, type = getProfile(username)
		return render_template('editProfile.jade', username=user[0], email=user[1], phone=user[2])
	return redirect('/profile/'+username)

@users.route('/profile/<username>/delete')
def deleteProfile(username):
	if session['user'] == username:
		sql=text('''DELETE from client where client_username='{0}';'''.format(username))
		db.engine.execute(sql)
		sql=text('''DELETE from worker where worker_username='{0}';'''.format(username))
		db.engine.execute(sql)
		session['user'] = None
		return redirect('/')

	return redirect('/profile/'+username)