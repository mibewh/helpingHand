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

<<<<<<< HEAD
def getRequest(id):
	sql=text('''SELECT client_username, title, description, schedule, address FROM service_request WHERE service_id=:id;''')
	result=db.engine.execute(sql, id=id)
	return result

def getWorkers():
	sql=text('''SELECT worker_username FROM worker;''')
	result=db.engine.execute(sql)
	return result

@requestsBP.route('/requests/<service_id>')#check info here
def request(service_id):
	request = getRequest(service_id)
	names = getWorkers()
	if(request):
		return render_template('requests.jade', client_username=result[0], title=result[1], description=result[2], schedule=result[3], address=result[4], worker_names=names)
		#check info above
	return redirect('/')

#select worker into tables with service request
=======
@requestsBP.route('/requests')
def viewRequests():
	if session.get('user'):
		sql = '''SELECT * FROM service_request WHERE '''
		return render_template('requests.jade')
	else:
		redirect('/')
>>>>>>> 29700025420b62a33cd33c84234b406341ff7f27
