from flask import Flask, render_template, g, redirect, request, session, flash, Blueprint
from sqlalchemy.sql import text
from operator import itemgetter
from . import db, app
import math, random, sys

#TODO: implement tiered system?
TIERED = False
MIN_RANDOMNESS = 0.7
NUM_RATING_MODIFIER = 0.5
SCHEDULE_PROPORTION = 0.7
TIER_THRESHOLDS = [5, 15, 40, 100, 250, sys.maxint]

# tiered scores
RANDOMNESS = 0.1

# should return the final list of workers to be displayed to the client
def getFinalWorkerList(service_id):
	workerList = getFullWorkerList(service_id)
	finalList = []

	if not TIERED:
		workerScores = []
		for worker in workerList:
			worker_username = worker[0]
			workerScores.append((worker, getWorkerScoreForService(worker_username, service_id)))
		# allWorkers contains tuples of workers and their scores

		workerScores = sorted(workerScores, key=itemgetter(1), reverse=True)
		for idx, val in enumerate(workerList):
			finalList.append(workerScores[idx][0][0])
			#workerList[idx] = workerScores[idx][0]
	else:
		tieredLists = []
		for thresh in TIER_THRESHOLDS:
			tieredLists.append([])
		for worker in workerList:
			for tier, thresh in enumerate(TIER_THRESHOLDS):
				numRatings = worker[2]
				if numRatings <= thresh:
					tieredLists[tier].append(worker)
					break
		for tier, tieredList in enumerate(tieredLists):
			print "" + str(tier) + str(tieredList)

		# sort tier lists
		for tier, tieredList in enumerate(tieredLists):
			workerAndScores = []
			for worker in tieredList:
				worker_username = worker[0]
				#score = 
				workerScores.append((worker, getScheduleScore(worker_username, service_id)))
			workerScores = sorted(workerScores, key=itemgetter(1), reverse=True)
			tieredList[tier] = workerScores


	#list of worker_usernames
	return finalList

# gets the compatibility score between the specified user and service
def getWorkerScoreForService(worker_username, service_id):
	tag = getServiceTag(service_id)
	ratingScore = getRatingScore(worker_username, tag)
	scheduleScore = getScheduleScore(worker_username, service_id)
	# TODO: complete
	return (1 - SCHEDULE_PROPORTION)*ratingScore + SCHEDULE_PROPORTION*scheduleScore

# NEEDS TESTING
# returns a score from 0 to 1 based on a little randomness and average rating
def getRatingScore(worker_username, tag):
	# randomness interval should vary with 1/sqrt(num_rating)
	numRatings, avgRating = getRatingInfo(worker_username, tag)

	if numRatings == 0: # if no ratings, completely random
		randomness = 2.5
		avgRating = 2.5 
	else:
		randomness = MIN_RANDOMNESS + NUM_RATING_MODIFIER/math.sqrt(numRatings)

	score = (avgRating + random.uniform(-1, 1)*randomness)/5
	if score > 1:
		score = 1
	elif score < 0:
		score = 0
	# TODO: Complete
	return score

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
	sql = text('''SELECT COUNT(rating), SUM(rating)
		FROM contract c, service_request sr
		WHERE c.service_id=sr.service_id AND
			worker_username = :worker_username AND
			tag=:tag AND
			rating IS NOT NULL''')
	ratingInfo = db.engine.execute(sql, worker_username=worker_username, tag=tag)
	ratingInfo = ratingInfo.fetchone()
	num_ratings = ratingInfo[0]
	total_rating = ratingInfo[1]

	if num_ratings == 0:
		mean_rating = 0
	else:
		mean_rating = 1.0*total_rating/num_ratings

	return num_ratings, mean_rating


# worker_username, avg_rating
def getFullWorkerList(service_id):
	sql = text('SELECT worker_username FROM worker')
	workerList = db.engine.execute(sql)
	workerList = workerList.fetchall()

	tag = getServiceTag(service_id)

	for idx, val in enumerate(workerList):
		worker_username = val[0]
		numRatings, avgRating = getRatingInfo(worker_username, tag)
		workerList[idx] = (worker_username, avgRating, numRatings)

	return workerList

def getServiceTag(service_id):
	sql = text('SELECT tag FROM service_request WHERE service_id=:service_id;')
	tag = db.engine.execute(sql, service_id=service_id)
	tag = tag.fetchone()
	tag = tag[0]
	return tag