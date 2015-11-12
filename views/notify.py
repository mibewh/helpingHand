from flask import Flask, render_template, g, redirect, request, session, flash, Blueprint
from sqlalchemy.sql import text
from . import db, app

notifications = Blueprint('notifications', __name__, template_folder=app.template_folder+'/notifications')

def pushNotification(name, message, link):
	#Insert a notification for a given person, with a message and a link
	sql = text('''INSERT INTO notification
				  (name, message, link)
				  VALUES (:name, :message, :link);''')
	db.engine.execute(sql, name=name, message=message, link=link)

@notifications.route('/notifications')
def viewNotifications():
	if session.get('user'):
		#Get all new notifications
		sql = text('''SELECT message, link, time FROM notification
					  WHERE name=:user AND viewed=FALSE''')
		results = db.engine.execute(sql, user=session.get('user'))
		newNotifications = results.fetchall()
		#Get all old notifications
		sql = text('''SELECT name, message, link, time FROM notification
					  WHERE name=:user AND viewed=TRUE''')
		results = db.engine.execute(sql, user=session.get('user'))
		oldNotifications = results.fetchall()
		#Set new notifications as viewed now
		sql = text('''UPDATE notifications SET viewed=TRUE WHERE name=:user;''')
		db.engine.execute(sql, user=session.get('user'))

		return render_template('viewNotifications.jade', unviewed=newNotifications, viewed=oldNotifications)
	else:
		return redirect('/')