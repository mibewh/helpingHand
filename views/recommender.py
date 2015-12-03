from flask import Flask, render_template, g, redirect, request, session, flash, Blueprint
from sqlalchemy.sql import text
from . import db, app

#TODO: implement tiered system?

# should return the final list of workers to be displayed to the client
def getFinalWorkerList(service_id):

	sql = text('SELECT worker_username FROM worker')
	workerScores = db.engine.execute(sql)
	workerScores = allWorkers.fetchall()
	for idx, val in enumerate(allWorkers):
		allWorkers[idx] = (val[0], getWorkerScoreForService(val[0], service_id))
	# allWorkers contains tuples of workers and their scores

	# TODO: sort and return
	return allWorkers

# gets the compatibility score between the specified user and service
def getWorkerScoreForService(worker_username, service_id):
	sql = text('SELECT tag FROM service_request WHERE service_id=:service_id;')
	tag = db.engine.execute(sql, service_id=service_id)
	tag = tag.fetchone()
	tag = tag[0]

	ratingScore = getRatingScore(worker_username, tag)
	scheduleScore = getScheduleScore(worker_username, service_id)
	# TODO: complete
	return 0

# NEEDS TESTING
# returns a score from 0 to 1 based on a little randomness and average rating
def getRatingScore(worker_username, tag):
	# randomness interval should vary with 1/sqrt(num_rating)
	numRatings, avgRating = getRatingInfo(worker_username, tag)
	# TODO: Complete
	return 0

# NEEDS TESTING
# returns a score from 0 to 1 based on how compatible the schedules are
def getScheduleScore(worker_username, service_id):
	# tuples in the form (<day>, <timeslot>), e.g:('mo', 9)
	workerScheduleTuples, requestScheduleTuples = getSchedules(worker_username, service_id)
	totalServiceSlots = 0
	commonSlots = 0
	for serviceTuple in requestScheduleTuples:
		for workerTuple in workerScheduleTuples:
			totalServiceSlots += 1
			if serviceTuple == workerTuple:
				commonSlots += 1
	if totalServiceSlots == 0:
		return 0
	return commonSlots/totalServiceSlots

# reads the schedule from the database into a data structure
def getSchedules(worker_username, service_id):
	workerScheduleArray = []
	requestScheduleArray = []
	sql = text('''SELECT day, hour FROM worker_schedule WHERE
				  worker_username=:worker;''')
	schedule = db.engine.execute(sql, worker=worker_username)
	schedule = schedule.fetchall()
	for tuple in schedule:
		workerScheduleArray.append([tuple[0], tuple[1]])
	sql = text('''SELECT day, hour FROM service_schedule WHERE
				  service_id=:request;''')
	schedule = db.engine.execute(sql, request=service_id)
	schedule = schedule.fetchall()
	for tuple in schedule:
		requestScheduleArray.append([tuple[0], tuple[1]])
		print(requestScheduleArray[-1])

	return workerScheduleArray, requestScheduleArray

# returns the number of ratings and the average ratings of the specified worker under
# the specified tag
def getRatingInfo(worker_username, tag):
	sql = text('''SELECT COUNT(rating), AVG(rating)
		FROM contract c, service_request sr
		WHERE c.service_id=sr.service_id AND
			worker_username = :worker_username AND
			tag = :tag AND
			rating IS NOT NULL''')
	ratingInfo = db.engine.execute(sql, worker_username=worker_username, tag=tag)
	ratingInfo = ratingInfo.fetchone()
	num_ratings = ratingInfo[0]
	mean_rating = ratingInfo[1]
	return num_ratings, mean_rating