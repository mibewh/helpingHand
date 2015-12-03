from flask import Flask, render_template, g, redirect, request, session, flash, Blueprint
from sqlalchemy.sql import text
from . import db, app
from notify import pushNotification
from views import recommender
from schedule import formatSchedule

requestsBP = Blueprint('request', __name__, template_folder=app.template_folder+'/requests')

def selectWorkers(id):
	workers = request.form.getlist('workers')
	for user in workers:
		sql = text('''INSERT INTO worker_request (service_id, worker_username) VALUES (:id, :user);''')
		db.engine.execute(sql, id=id, user=user)
		pushNotification(user, 'You have been requested for a job', '/pending/'+str(id))

@requestsBP.route('/create', methods=('GET', 'POST'))
def createServiceRequest():
	if request.method == 'POST':
		sql = text('''INSERT INTO service_request(client_username, address, title, description, tag)
						VALUES(:user, :address, :title, :description, :tag);''')
		db.engine.execute(sql, user=session["user"], address=request.form.get('address'), title=request.form.get('title'),\
							description=request.form.get('description'), tag=request.form.get('tag'))
		sql2 = text('''SELECT service_id FROM service_request WHERE client_username=:user AND address=:address AND
						title=:title AND description=:description;''')
		result = db.engine.execute(sql2, user=session["user"], address=request.form.get('address'), title=request.form.get('title'),\
							description=request.form.get('description'))
		idnum = result.fetchone()
		days = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
		for day in days:
			times = request.form.getlist(day)
			for time in times:
				sql = text('''INSERT INTO service_schedule(service_id,day,hour) VALUES(:id,:day,:hour);''')
				db.engine.execute(sql, id=idnum[0], day=day, hour=time)
		flash('Service request created.')
		return redirect('/requests/'+str(idnum[0])+'/workers')
	if not session.get('user'):
		flash('Please login before creating requests.')
		return redirect('/')
	elif session['type'] == 'worker':
		flash('You must be a client to create service requests.')
		return redirect('/')
	else:
		sql = text('''SELECT tag FROM job_tag''')
		results = db.engine.execute(sql)
		tags = [res[0] for res in results]
		return render_template('createRequest.jade', tags=tags)

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
		sql = text('''SELECT service_id, client_username, title, description, address, contracted, tag
					  FROM service_request WHERE client_username=:username AND contracted=FALSE
					  ORDER BY time_submit DESC;''')
		results = db.engine.execute(sql, username=session.get('user'))
		results = results.fetchall()
		results = [r for r in results if r[5]==False]
		return render_template('viewRequests.jade', requests=results)
	else:
		return redirect('/')

def getRequest(service_id):
	sql=text('''SELECT client_username, title, description, address, tag FROM service_request WHERE service_id=:id;''')
	result=db.engine.execute(sql, id=service_id)
	return result.fetchone()

def getWorkers(service_id):
	sql=text('''SELECT worker_username, interested FROM worker_request WHERE service_id=:id;''')
	result=db.engine.execute(sql, id=service_id)
	return result.fetchall()

@requestsBP.route('/requests/<service_id>')
def viewRequest(service_id):
	result = getRequest(service_id)
	names = getWorkers(service_id)
	if result and result[0]==session.get('user'):
		days = formatSchedule('request', service_id)
		return render_template('request.jade', id=service_id, client_username=result[0], title=result[1], description=result[2], address=result[3], tag=result[4], worker_names=names, days=days)
	return redirect('/')

@requestsBP.route('/pending')
def viewPendings():
	if session.get('user') and session['type'] == 'worker':
		sql=text('''SELECT sr.service_id, client_username, title, description, address, interested, contracted, tag
								FROM service_request sr, worker_request wr, worker w
								WHERE sr.service_id=wr.service_id AND wr.worker_username=w.worker_username AND w.worker_username=:username AND contracted=FALSE
								ORDER BY time_submit DESC;''')
		results = db.engine.execute(sql, username=session.get('user'))
		results = results.fetchall()
		results = [r for r in results if r[6]==False]
		return render_template('viewPending.jade', requests=results)
	return redirect('/')

@requestsBP.route('/pending/<service_id>')
def viewPending(service_id):
	sql=text('''SELECT client_username, title, description, address, interested, tag FROM service_request sr, worker_request wr WHERE sr.service_id=:id AND sr.service_id=wr.service_id;''')
	results=db.engine.execute(sql, id=service_id)
	result = results.fetchone()
	if result:
		days = formatSchedule('request', service_id)
		return render_template('pending.jade', id=service_id, client_username=result[0], title=result[1], description=result[2], address=result[3], interested=result[4], tag=result[5], days=days)
	return redirect('/')

@requestsBP.route('/pending/<service_id>/accept', methods=('GET', 'POST'))
def interestRequest(service_id):
	if request.method == 'GET': return redirect('/')
	if session.get('user') and session['type'] == 'worker':
		sql = text('''SELECT interested FROM worker_request WHERE service_id=:id AND worker_username=:user;''')
		results = db.engine.execute(sql, id=service_id, user=session['user'])
		interested = results.fetchone()[0]
		interested = not interested; #change interest
		sql = text('UPDATE worker_request SET interested=:interested WHERE service_id=:id AND worker_username=:user;')
		db.engine.execute(sql, interested=interested, id=service_id, user=session['user'])
		#Notify the user
		if interested:
			sql = text('''SELECT client_username FROM service_request WHERE service_id=:id''')
			results = db.engine.execute(sql, id=service_id)
			name = results.fetchone()[0]
			pushNotification(name, session.get('user')+' is interested in your job', '/requests/'+str(service_id))
		return redirect('/pending')
	else: return redirect('/')

@requestsBP.route('/requests/<service_id>/edit', methods=('GET', 'POST'))
def editRequest(service_id):
	if request.method=='POST':
		sql=text('''UPDATE service_request
					SET title=:title, description=:description, address=:address
					WHERE service_id=:id;''')
		db.engine.execute(sql,address=request.form.get('address'), title=request.form.get('title'),\
							description=request.form.get('description'), id=service_id)
		return redirect('/requests/'+service_id+'/workers')

	sql=text('''SELECT * FROM service_request WHERE service_id=:id AND client_username=:user;''')
	result = db.engine.execute(sql, id=service_id, user=session['user'])
	if result:
		user, title, description, address, tag = getRequest(service_id)
		sql2 = text('''SELECT worker_username FROM worker''')
		results = db.engine.execute(sql2)
		worker_names = [res[0] for res in results]
		return render_template('editRequest.jade', user=user, title=title, description=description, address=address, id=service_id, workers=worker_names)
	return redirect('/requests/'+service_id)

@requestsBP.route('/requests/<service_id>/workers', methods=('GET', 'POST'))
def workerList(service_id):
	if request.method=='POST':
		sql=text('''DELETE FROM worker_request WHERE service_id=:id;''')
		db.engine.execute(sql, id=service_id)
		selectWorkers(service_id)
		return redirect('/requests/'+service_id)

	workerlist = recommender.getFinalWorkerList(service_id)
	return render_template('workerList.jade', workers=workerlist, id=service_id)

@requestsBP.route('/requests/<service_id>/delete')
def deleteRequest(service_id):
	if session.get('user'):
		#Verify that the request to delete is that user's request
		sql = text('''SELECT * FROM service_request WHERE service_id=:id AND client_username=:user''')
		result = db.engine.execute(sql, id=service_id, user=session['user'])
		result = [r[0] for r in result]
		if result == []: return redirect('/')
		#Delete the entry
		sql = text('''DELETE FROM service_request WHERE service_id=:id''')
		db.engine.execute(sql, id=service_id)
		return redirect('/requests')
	else:
		return redirect('/')