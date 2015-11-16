from flask import Flask, render_template, g, redirect, request, session, flash, Blueprint
from sqlalchemy.sql import text
from notify import pushNotification
from . import db, app

scheduler = Blueprint('scheduler', __name__, template_folder=app.template_folder+'/scheduler')

def calculateScheduleCompatibility(workerScheduleArray, requestScheduleArray):#assume {Monday:3pm, Monday:4pm, Monday:5pm......etc
	numbers = {} #return values. just counts how many times in common for each day {Monday: 4, Tuesday:2 .......etc
	requestTimeSlots = len(requestScheduleArray)
	for requestTime in workerScheduleArray:
		for workerTime in requestScheduleArray:
			if(requestTime[0] ==  workerTime[0] and requestTime[1] ==  workerTime[1]):
				if requestTime[0] in numbers:
					numbers[requestTime[0]] += 1
				else:
					numbers[requestTime[0]] = 1

	return numbers, requestTimeSlots

def calculateScheduleNumber(numbers, requestTimeSlots):
	#do math here and get a number we can use to tell how relatable they are or relatable in comparison to other workers
	workerTimeSlots = 0;
	for value in numbers:
		workerTimeSlots ++ value
	return workerTimeSlots/requestTimeSlots

def getSchedules(worker_username, service_id):
	workerScheduleArray = []
	requestScheduleArray = []
	sql = text('''SELECT day, hour FROM schedule WHERE
				  worker_username=:worker;''')
	schedule = db.engine.execute(sql, worker=worker_username)
	schedule = schedule.fetchall()
	for tuple in schedule:
		workerScheduleArray.append([tuple[0], tuple[1]])
	sql = text('''SELECT day, hour FROM request_schedule WHERE
				  service_id=:request;''')
	schedule = db.engine.execute(sql, request=service_id)
	schedule = schedule.fetchall()
	for tuple in schedule:
		requestScheduleArray.append([tuple[0], tuple[1]])

	return workerScheduleArray, requestScheduleArray

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