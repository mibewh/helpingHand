from flask import Flask, render_template, g, redirect, request, session, flash, Blueprint
from sqlalchemy.sql import text
from . import db, app

contractBP = Blueprint('contract', __name__, template_folder=app.template_folder+'/contracts')

@contractBP.route('/contracts/<contract_id>')
def viewContract(contract_id):
	sql = text('''SELECT client_username, worker_username, address, start_time, payment
								FROM contract
								WHERE contract_id=:contract_id''')
	result = db.engine.execute(sql, contract_id=contract_id)
	result = result.fetchone()
	if result:
		return render_template('contract.jade', title='Title', client_username=result[0], worker_username=result[1], address=result[2], start_time=result[3], money=result[4])
	return redirect('/')

@contractBP.route('/contracts')
def viewRequests():
	if session.get('user'):
		sql = text('''SELECT * FROM contract 
					WHERE client_username=:username
					OR worker_username=:username;''')
		results = db.engine.execute(sql, username=session.get('user'))
		results = results.fetchall()
		return render_template('viewContracts.jade', results=results)
	else:
		return redirect('/')