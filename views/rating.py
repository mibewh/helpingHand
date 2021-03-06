from flask import Flask, render_template, g, redirect, request, session, flash, Blueprint
from sqlalchemy.sql import text
from . import db, app

ratings = Blueprint('rating', __name__, template_folder=app.template_folder+'/rating')

@ratings.route('/contracts/<contract_id>/rating', methods=('GET', 'POST'))
def rateWorker(contract_id):
	if request.method=="GET":
		sql=text('''SELECT worker_username, contract_status, rating FROM contract WHERE contract_id=:id;''')
		contract = db.engine.execute(sql, id=contract_id)
		contract=contract.fetchone()
		if(contract[1]=="finished" and contract[2]==None):
			return render_template('rating.jade', name=contract[0], id=contract_id)
		else:
			return redirect('/')
	if request.method=="POST":
		rating = request.form.get('rating')
		if rating == '0':
			rating = None
		sql=text('''UPDATE contract SET rating=:rating, review=:review WHERE contract_id=:id;''')
		result=db.engine.execute(sql, rating=rating, review=request.form.get("review"), id=contract_id)
		flash("Rating Submitted")
		return redirect('/')		

def getRating(worker_username, tag):
	if tag:
		sql=text('''SELECT AVG(rating) COUNT(rating)
			FROM contract c, service_request sr
			WHERE c.service_id=sr.service_id AND 
				worker_username=:worker_username AND 
				tag=:tag AND
				rating IS NOT NULL''')
		result = db.engine.execute(sql, worker_username=worker_username, tag=tag)
		return result[0], result[1];
	else:
		sql=text('''SELECT AVG(rating) COUNT(rating)
			FROM contract
			WHERE worker_username=:worker_username AND 
				rating IS NOT NULL''')
		result = db.engine.execute(sql, worker_username=worker_username)
		return result[0], result[1];