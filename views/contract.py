from flask import Flask, render_template, g, redirect, request, session, flash, Blueprint
from sqlalchemy.sql import text
from notify import pushNotification
from . import db, app
from notify import pushNotification

contractBP = Blueprint('contract', __name__, template_folder=app.template_folder+'/contracts')

@contractBP.route('/submitContract', methods=('GET', 'POST'))
def submitContract():
	if request.method=='POST':
		# move to after table insertion when debugging
		sql = text('''INSERT INTO contract
					  (worker_username, service_id, time, contract_status)
					  VALUES (:worker_username, :service_id, :time, 'pending');''')
		db.engine.execute(sql, \
			worker_username=request.form.get('worker_username'), \
			service_id=request.form.get('service_id'), \
			time=request.form.get('time'))
		sql = text('''UPDATE service_request SET contracted=TRUE WHERE service_id=:service_id''')
		db.engine.execute(sql, service_id=request.form.get('service_id'))

		sql = text('''SELECT contract_id, client_username
						FROM contract c, service_request sr
 						WHERE
							c.service_id=sr.service_id AND
							sr.service_id=:service_id AND
							worker_username=:worker_username;''')
		result = db.engine.execute(sql, \
			service_id=request.form.get('service_id'), \
			worker_username=request.form.get('worker_username'))
		result = result.fetchone()
		pushNotification(\
			name=request.form.get('worker_username'), \
			message='You\'ve received a contract from '+result[1], \
			link='/contracts/'+str(result[0]))

		flash('Contract created, awaiting worker acceptance')
		return redirect('/')
	else:
		return redirect('/')
	#return render_template('createContract.jade')

@contractBP.route('/createContract', methods=('GET', 'POST'))
def createContract():
	if request.method=='GET': return redirect('/')
	sql = text('''SELECT title, description, address
				  FROM service_request sr, worker_request wr
				  WHERE sr.service_id=wr.service_id AND sr.service_id=:id AND worker_username=:worker;''')
	print(request.form.get('service_id'), request.form.get('worker'))
	results = db.engine.execute(sql, id=request.form.get('service_id'), worker=request.form.get('worker'))
	res = results.fetchone()
	return render_template('createContract.jade', title=res[0], description=res[1], address=res[2], \
							service_id=request.form.get('service_id'), worker_username=request.form.get('worker'))

@contractBP.route('/contracts/<contract_id>')
def viewContract(contract_id):
	sql = text('''SELECT
					sr.title, 
					sr.description, 
					sr.client_username, 
					c.worker_username,
					c.time, 
					c.contract_status,
					c.service_id,
					sr.tag
				  FROM contract c, service_request sr
				  WHERE c.service_id=sr.service_id AND c.contract_id=:contract_id''')
	result = db.engine.execute(sql, contract_id=contract_id)
	result = result.fetchone()
	if result:
		return render_template('contract.jade', result=result, id=contract_id)
	return redirect('/')

@contractBP.route('/contracts')
def viewContracts():
	if session.get('user'):
		sql=text('''SELECT
						c.contract_id, 
						sr.title, 
						sr.description, 
						sr.client_username, 
						c.worker_username, 
						c.time,
						c.contract_status,
						sr.tag
					FROM contract c, service_request sr
					WHERE c.service_id=sr.service_id AND (sr.client_username=:username OR c.worker_username=:username)
					ORDER BY c.time_submit DESC;''')
		results = db.engine.execute(sql, username=session.get('user'))
		results = results.fetchall()
		pending = [res for res in results if res[6] == 'pending']
		accepted = [res for res in results if res[6] == 'accepted']
		finished = [res for res in results if res[6] == 'finished']
		return render_template('viewContracts.jade', pending=pending, accepted=accepted, finished=finished, type=session.get('type'))
	else:
		return redirect('/')

@contractBP.route('/contracts/<id>/accept')
def workerAcceptContract(id):
	if session.get('user') and session['type'] == 'worker':
		sql = text('''UPDATE contract SET contract_status='accepted' WHERE contract_id=:id;''')
		db.engine.execute(sql, id=id)

		sql = text('''SELECT client_username, worker_username
						FROM service_request sr, contract c
						WHERE sr.service_id=c.service_id AND
							contract_id=:id''')
		result = db.engine.execute(sql, id=id)
		result = result.fetchone()
		pushNotification( \
			name=result[0], \
			message=result[1]+' has accepted your contract', \
			link='/contracts/'+str(id))

		return redirect('/contracts')
	else:
		return redirect('/')
		
@contractBP.route('/contracts/<id>/deny')
def workerDenyContract(id):
	if session.get('user') and session['type'] == 'worker':
		sql = text('''SELECT service_id FROM contract WHERE contract_id=:id;''')
		result = db.engine.execute(sql, id=id)
		service_id = result.fetchone()[0]
		sql = text('''UPDATE service_request SET contracted=FALSE WHERE service_id=:service_id;''')
		db.engine.execute(sql, service_id=service_id)
		sql = text('''DELETE FROM contract WHERE contract_id=:id;''')
		db.engine.execute(sql, id=id)

		sql = text('''SELECT client_username, worker_username
						FROM service_request sr, contract c
						WHERE sr.service_id=c.service_id AND
							contract_id=:id''')
		result = db.engine.execute(sql, id=id)
		result = result.fetchone()
		pushNotification( \
			name=result[0], \
			message=result[1]+' has denied your contract', \
			link='/contracts/'+str(id))

		return redirect('/contracts')
	else:
		return redirect('/')

@contractBP.route('/contracts/<id>/cancel')
def clientCancelContract(id):
	if session.get('user') and session['type'] == 'client':
		sql = text('''SELECT client_username, worker_username, contract_status, contract.service_id FROM service_request sr, contract WHERE contract_id=:id AND contract.service_id=sr.service_id;''')
		result = db.engine.execute(sql, id=id).fetchone()
		client = result[0]
		worker = result[1]
		status = result[2]
		service_id = result[3]
		if client != session.get('user') or status != 'pending': return redirect('/')
		sql = text('''DELETE FROM contract WHERE contract_id=:id;''')
		db.engine.execute(sql, id=id)
		sql = text('''UPDATE service_request SET contracted=FALSE WHERE service_id=:id''')
		db.engine.execute(sql, id=service_id)
		flash('Pending contract deleted')
		pushNotification(worker, client+' cancelled a pending contract', '/contracts')
		return redirect('/')
	else:
		return redirect('/')

@contractBP.route('/contracts/<id>/complete')
def completeContract(id):
	if session.get('user') and session['type'] == 'client':
		#Check if this user is the owner of the request
		sql = text('''SELECT client_username, worker_username FROM contract, service_request
					  WHERE contract.service_id=service_request.service_id
					  AND contract_id=:id;''')
		result = db.engine.execute(sql, id=id)
		result = result.fetchone()
		contract_client = result[0]
		contract_worker = result[1]
		if contract_client == session.get('user'):
			#complete the contract
			sql = text('''UPDATE contract 
						  SET contract_status='finished',
						  time_finish=NOW()
						  WHERE contract_id=:id;''')
			db.engine.execute(sql, id=id)
			pushNotification(contract_worker, 'Contract with '+contract_client+' complete', '/contracts/'+str(id))
			return redirect('/contracts/'+id+'/rating')
		else:
			return redirect('/')
	else:
		return redirect('/')
