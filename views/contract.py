from flask import Flask, render_template, g, redirect, request, session, flash, Blueprint
from sqlalchemy.sql import text
from . import db, app

contractBP = Blueprint('contract', __name__, template_folder=app.template_folder+'/contracts')

@contractBP.route('/submitContract', methods=('GET', 'POST'))
def submitContract():
	if request.method=='POST':
		sql = text('''INSERT INTO contract
					  (client_username, worker_username, service_id, time)
					  VALUES (:client_username, :worker_username, :service_id, :time)''')
		sql2 = text('''SELECT client_username FROM service_request WHERE service_id=:service_id''')
		result = db.engine.execute(sql2, request.form.get('service_id'))
		result = result.fetchone()
		db.engine.execute(sql, client_username=result, worker_username=request.form.get('worker_username'), service_id=request.form.get('service_id'), time=request.form.get('time'))
		flash('Contract created')
		return redirect('/')
	else:
		return redirect('/')
	#return render_template('createContract.jade')

@contractBP.route('/createContract', methods=('GET', 'POST'))
def createContract():
	if request.method=='GET': return redirect('/')
	sql = text('''SELECT title, description, address, schedule
				  FROM service_request sr, worker_request wr
				  WHERE sr.service_id=wr.service_id AND sr.service_id=:id AND worker_username=:worker;''')
	print(request.form.get('service_id'), request.form.get('worker'))
	results = db.engine.execute(sql, id=request.form.get('service_id'), worker=request.form.get('worker'))
	res = results.fetchone()
	return render_template('createContract.jade', title=res[0], description=res[1], address=res[2], time=res[3], \
							service_id=request.form.get('service_id'), worker_username=request.form.get('worker_username'))

@contractBP.route('/contracts/<contract_id>')
def viewContract(contract_id):
	sql = text('''SELECT * FROM contract WHERE contract_id=:contract_id''')
	result = db.engine.execute(sql, contract_id=contract_id)
	result = result.fetchone()
	if result:
		return render_template('contract.jade',results=result)
	return redirect('/')

@contractBP.route('/contracts')
def viewContracts():
	if session.get('user'):
		sql=text('''SELECT * FROM contract c, service_request sr WHERE c.service_id=sr.service_id AND (client_username=:username OR worker_username=:username) AND contract_status='accepted';''')
		results = db.engine.execute(sql, username=session.get('user'))
		results = results.fetchall()
		return render_template('viewContracts.jade', results=results)
	else:
		return redirect('/')

@contractBP.route('/pendingContracts')
def viewPendingContracts():
	user = session.get('user')
	if user:
		sql=text('''SELECT * FROM contract c, service_request sr WHERE c.service_id=sr.service_id AND (client_username=:username OR worker_username=:username) AND contract_status='pending';''')
		results = db.enginge.execute(sql, username=user)
		results = results.fetchall()
		return render_template('viewPendingContracts.jade', results=results)
	else:
		return redirect('/')

@contractBP.route('/pendingContracts/<contract_id>')
def viewPendingContract(contract_id):
	sql = text('''SELECT * FROM contract WHERE contract_id=:contract_id''')
	result = db.engine.execute(sql, contract_id=contract_id)
	result = result.fetchone()
	if result:
		return render_template('pendingContract.jade',results=results)
	return redirect('/')