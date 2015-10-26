from flask import Flask, render_template, g, redirect, request, session, flash, Blueprint
from sqlalchemy.sql import text
from main import db

requestsBP = Blueprint('request', __name__)

def selectWorkers(id):
	workers = request.form.getlist('workers')
	for user in workers:
		sql = text('''INSERT INTO worker_request (service_id, worker_username) VALUES (:id, :user);''')
		db.engine.execute(sql, id=id, user=user)

@requestsBP.route('/create', methods=('GET', 'POST'))
def create_service_request():
	if request.method == 'POST':
		sql = text('''INSERT INTO service_request(client_username, address, title, description, schedule)
						VALUES(:user, :address, :title, :description, :time);''')
		db.engine.execute(sql, user=session["user"], address=request.form.get('address'), title=request.form.get('title'),\
							description=request.form.get('description'), time=request.form.get("time"))
		sql2 = text('''SELECT service_id FROM service_request WHERE client_username=:user AND address=:address AND
						title=:title AND description=:description AND schedule=:time;''')
		result = db.engine.execute(sql2, user=session["user"], address=request.form.get('address'), title=request.form.get('title'),\
							description=request.form.get('description'), time=request.form.get("time"))
		idnum = result.fetchone()
		selectWorkers(idnum[0])
		flash('Service request created.')
		return redirect('/')
	if not session.get('user'):
		flash('Please login before creating requests.')
		return redirect('/')
	elif session['type'] == 'worker':
		flash('You must be a client to create service requests.')
		return redirect('/')
	else:
		sql = text('''SELECT worker_username FROM worker''')
		results = db.engine.execute(sql)
		worker_names = [res[0] for res in results]
		return render_template('create.jade', workers=worker_names)

@requestsBP.route('/search', methods=('GET', 'POST'))
def searchName():
	if request.method == 'POST':
		search = request.form.get('query')
		print(search)
		#sql = text('''select "sp_awesome_search_service_requests"('{0}')'''.format(search))
		sql = text('''SELECT *
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
		if session['type'] == 'worker':
			return redirect('/pending')
		sql = text('''SELECT * FROM service_request WHERE client_username=:username;''')
		results = db.engine.execute(sql, username=session.get('user'))
		results = results.fetchall()
		return render_template('viewRequests.jade', requests=results)
	else:
		return redirect('/')

def getRequest(id):
	sql=text('''SELECT client_username, title, description, schedule, address FROM service_request WHERE service_id=:id;''')
	result=db.engine.execute(sql, id=id)
	return result.fetchone()

def getWorkers(id):
	sql=text('''SELECT worker_username FROM worker_request WHERE service_id=:id;''')
	result=db.engine.execute(sql, id=id)
	return result.fetchall()

@requestsBP.route('/requests/<service_id>')
def viewRequest(service_id):
	result = getRequest(service_id)
	names = getWorkers(service_id)
	if(result):
		return render_template('request.jade', client_username=result[0], title=result[1], description=result[2], schedule=result[3], address=result[4], worker_names=names)
	return redirect('/')

@requestsBP.route('/pending')
def viewPending():
	if session.get('user') and session['type'] == 'worker':
		sql=text('''SELECT client_username, title, description, schedule, address
								FROM service_request sr, worker_request wr, worker w
								WHERE sr.service_id=wr.service_id AND wr.worker_username=w.worker_username AND w.worker_username=:username''')
		results = db.engine.execute(sql, username=session.get('user'))
		results = results.fetchall()
		return render_template('pending.jade', requests=results)
	return redirect('/')
