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
		sql=text('''INSERT INTO table (:rating, :review) VALUES (rating, review);''')
		result=db.engine.execute(sql, rating=request.form.get("rating"), review=request.form.get("review"))
		flash("Rating Submitted")
		return redirect('/')		

