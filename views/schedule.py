from flask import Flask, render_template, g, redirect, request, session, flash, Blueprint
from sqlalchemy.sql import text
from notify import pushNotification
from . import db, app

scheduler = Blueprint('scheduler', __name__, template_folder=app.template_folder+'/scheduler')

@scheduler.route('/schedule', methods=('GET', 'POST'))
def setSchedule():
	if not session.get('user') or session['type'] != 'worker':
		return redirect('/')
	if request.method == 'GET':
		sql = text('''SELECT day, hour FROM worker_schedule WHERE worker_username=:user;''')
		times = db.engine.execute(sql, user=session.get('user')).fetchall()
		return render_template('scheduler/setSchedule.jade', times=times)
	days = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
	sql = text('''DELETE FROM worker_schedule WHERE worker_username=:user;''')
	db.engine.execute(sql, user=session.get('user'))
	for day in days:
		times = request.form.getlist(day)
		for time in times:
			sql = text('''INSERT INTO worker_schedule(worker_username,day,hour) VALUES(:user,:day,:hour);''')
			db.engine.execute(sql, user=session.get('user'), day=day, hour=time)

	return redirect('/profile/'+session.get('user'))

def formatSchedule(type, id):
	if type == 'worker':
		sql = text('''SELECT day, hour FROM worker_schedule
					  WHERE worker_username=:id
					  ORDER BY hour ASC''')
	else:
		sql = text('''SELECT day, hour FROM service_schedule
					  WHERE service_id=:id
					  ORDER BY hour ASC''')
	results = db.engine.execute(sql, id=id).fetchall()
	days = ['Monday: ', 'Tuesday: ', 'Wednesday: ', 'Thursday: ', 'Friday: ', 'Saturday: ', 'Sunday: ']
	for result in results:
		dayVal = getDayVal(result[0])
		time = result[1] % 12
		if time == 0: time = 12
		if result[1] / 12 == 0:
			mer = 'AM'
		else:
			mer = 'PM'
		days[dayVal] += str(time) + mer + ' '
	return days

def getDayVal(day):
	return {
		'mo': 0,
		'tu': 1,
		'we': 2,
		'th': 3,
		'fr': 4,
		'sa': 5,
		'su': 6,
	}[day]

@scheduler.route('/<service_id>/schedule', methods=('GET', 'POST'))
def setServiceSchedule(service_id):
	if not session.get('user') or session['type'] != 'client':
		return redirect('/')
	if request.method == 'GET':
		sql = text('''SELECT day, hour FROM service_schedule WHERE service_id=:id;''')
		times = db.engine.execute(sql, id=service_id).fetchall()
		return render_template('scheduler/setServiceSchedule.jade', times=times, id=service_id)
	days = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
	sql = text('''DELETE FROM service_schedule WHERE service_id=:id;''')
	db.engine.execute(sql, id=service_id)
	for day in days:
		times = request.form.getlist(day)
		for time in times:
			sql = text('''INSERT INTO service_schedule(service_id,day,hour) VALUES(:id,:day,:hour);''')
			db.engine.execute(sql, id=service_id, day=day, hour=time)
	if request.method == 'POST':
		sql = text('''DELETE FROM service_schedule WHERE service_id=:id;''')
		db.engine.execute(sql, id=service_id)
		for day in days:
			times = request.form.getlist(day)
			for time in times:
				sql = text('''INSERT INTO service_schedule(service_id,day,hour) VALUES(:id,:day,:hour);''')
				db.engine.execute(sql, id=service_id, day=day, hour=time)
		return redirect('/requests/'+service_id+'/workers')
	return redirect('/requests/'+str(service_id))
