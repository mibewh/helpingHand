from flask import Flask, render_template, g, redirect, request, session, flash, Blueprint
from sqlalchemy.sql import text
from main import db

requestsBP = Blueprint('request', __name__)

@requestsBP.route('/create', methods=('GET', 'POST'))
def create_service_request():
	if request.method == 'POST':
		sql = text('''INSERT INTO service_request(client_username, address, title, description, schedule)
						VALUES(:user, :address, :title, :description, :time);''')
		db.engine.execute(sql, user=session["user"], address=request.form.get('address'), title=request.form.get('title'),\
							description=request.form.get('description'), time=request.form.get("time"))
		flash('Service request created.')
		return redirect('/')
	if not session.get('user'):
		flash('Please login before creating requests.')
		return redirect('/')
	elif session['type'] == 'worker':
		flash('You must be a client to create service requests.')
		return redirect('/')
	else:
		return render_template('create.jade')

@requestsBP.route('/search', methods=('GET', 'POST'))
def searchName():
	if request.method == 'POST':
		search = request.form.get('query')
		print(search)
		#sql = text('''select "sp_awesome_search_service_requests"('{0}')'''.format(search))
		sql = text('''SELECT sr.title, sr.description, sr.client_username, sr.schedule, sr.address
						FROM service_request sr
						WHERE
							UPPER(sr.title) LIKE UPPER('%'||:search||'%') OR
							UPPER(sr.description) LIKE UPPER('%'||:search||'%') OR
							UPPER(sr.address) LIKE UPPER('%'||:search||'%');''')
		results = db.engine.execute(sql, search=search)
		results = results.fetchall()
		return render_template('searchRequests.jade', results=results)
	return render_template('searchRequests.jade')

@requestsBP.route('/requests')
def viewRequests():
	if session.get('user'):
		sql = text('''SELECT * FROM service_request WHERE client_username=:username;''')
		results = db.engine.execute(sql, username=session.get('user'))
		results = results.fetchall()
		return render_template('requests.jade', requests=results)
	else:
		return redirect('/')
