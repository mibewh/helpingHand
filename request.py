from flask import Flask, render_template, g, redirect, request, session, flash, Blueprint
from sqlalchemy.sql import text
from main import db

requestsBP = Blueprint('request', __name__)

@requestsBP.route('/create', methods=('GET', 'POST'))
def create_service_request():
	if request.method == 'POST':
		sql = text('''insert into service_request(client_username, address, title, description, schedule)
						values('{0}', '{1}', '{2}', '{3}', '{4}');'''\
		.format(session["user"], request.form.get('address'), request.form.get('title'), request.form.get('description'), request.form.get("time")))
		db.engine.execute(sql)
		return redirect('/')
	if session['user']:
		return render_template('create.jade')
	else:
		return redirect('/')

@requestsBP.route('/search', methods=('GET', 'POST'))
def searchName():
	if request.method == 'POST':
		search = request.form.get('query')
		print(search)
		#sql = text('''select "sp_awesome_search_service_requests"('{0}')'''.format(search))
		sql = text('''SELECT sr.title, sr.description, sr.client_username, sr.schedule, sr.address
						FROM service_request sr
						WHERE
							sr.title LIKE '%'||'{0}'||'%' OR
							sr.description LIKE '%'||'{0}'||'%' OR
							sr.address LIKE '%'||'{0}'||'%';'''.format(search))
		results = db.engine.execute(sql)
		results = results.fetchall()
		return render_template('searchRequests.jade', results=results)
	return render_template('searchRequests.jade')