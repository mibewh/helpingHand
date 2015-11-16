from flask import Flask, render_template, g, redirect, request, session, flash, Blueprint
from sqlalchemy.sql import text
from notify import pushNotification
from . import db, app

def calculateScheduleCompatibility(workerScheduleArray, requestScheduleArray):#assume {Monday:3pm, Monday:4pm, Monday:5pm......etc
	numbers = {} #return values. just counts how many times in common for each day {Monday: 4, Tuesday:2 .......etc
	for requestTime in workerScheduleArray:
		for workerTime in requestScheduleArray
			if(requestTime[0] ==  workerTime[0] and requestTime[1] ==  workerTime[1]):
				if requestTime[0] in numbers:
					numbers[requestTime[0]] += 1
				else:
					numbers[requestTime[0]] = 1

	return numbers

def calculateScheduleNumber(arrayFromAboveFunction):
	#do math here and get a number we can use to tell how relatable they are or relatable in comparison to other workers

def getSchedules(worker_username, service_id):
	workerScheduleArray = []
	requestScheduleArray = []
	sql = text('''SELECT day, time FROM schedule WHERE
				  worker_username=:worker;''')
	schedule = db.engine.execute(sql, worker=worker_username)
	schedule = schedule.fetchall()
	for tuple in schedule:
		workerScheduleArray.append([tuple[0], tuple[1]])
	sql = text('''SELECT day, time FROM request_schedule WHERE
				  service_id=:request;''')
	schedule = db.engine.execute(sql, request=:service_id)
	schedule = schedule.fetchall()
	for tuple in schedule:
		requestScheduleArray.append([tuple[0], tuple[1]])

	return workerScheduleArray, requestScheduleArray