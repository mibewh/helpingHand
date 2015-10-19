from flask import Flask, render_template, g, redirect, request, session, flash, Blueprint
from sqlalchemy.sql import text
from main import db

request = Blueprint('request', __name__)

@request.route('/create', methods=('GET', 'POST'))
def create_service_request():
	if request.method == 'POST':
		sql = text('''insert into service_request(client_id, address, title, decsription, schedule)values('{0}', '{1}', '{2}');'''\
		.format(session["user"], request.form.get('address'), request.form.get('title'), request.form.get('description'), request.form.get("time"))
		db.engine.execute(sql)
		return redirect('/')