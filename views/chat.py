from flask import Flask, render_template, g, redirect, request, session, flash, Blueprint
from sqlalchemy.sql import text
from notify import pushNotification
from . import db, app, socketio
from notify import pushNotification
from flask.ext.socketio import emit, join_room, leave_room

chatBP = Blueprint('chat', __name__, template_folder=app.template_folder+'/chat', static_folder=app.static_folder)
rooms = {};

##
#Helper methods
##
def addMessage(message, room):
	sql = text('''INSERT INTO message(room, msg, username, time)
					VALUES(:room, :msg, :user, NOW());''')
	db.engine.execute(sql, room=room, msg=message, user=session.get('user'))

def isOtherOffline(room):
	return len(rooms[room]) <= 1

def isOtherNotified(room):
	#Chatrooms should only ever have 2 users in them.
	#Therefore, only need to check if other user is notified, which is relatively trivial.
	sql = text('''SELECT name
				  FROM notification
				  WHERE viewed=FALSE AND link=:link
				  AND name!=:curUser;''')
	name = db.engine.execute(sql, link='/chat/'+room, curUser=session.get('user')).fetchone()
	return (name is not None)

def getOther(room):
	id = room[:room.find(";")]
	worker = room[1+room.find(";"):]
	if session.get('user') != worker:
		return worker
	else:
		sql = text('''SELECT client_username FROM service_request
					  WHERE service_id=:id;''')
		client = db.engine.execute(sql, id=id).fetchone()[0]
		return client
##
#Urls
##
@chatBP.route('/chat/<room>')
def chat(room):
	id = room[:room.find(";")]
	worker = room[1+room.find(";"):]
	sql = text('''SELECT client_username FROM service_request
					WHERE service_id=:id;''')
	results = db.engine.execute(sql, id=id);
	client = results.fetchone()[0]
	if not session.get('user') or not (session.get('user')==client or session.get('user')==worker):
		return redirect('/')

	session['room'] = room
	#Fetch the previous chat messages, and add to the log
	sql = text('''SELECT msg FROM message
					WHERE room=:room
					ORDER BY time;''')
	msgs = db.engine.execute(sql, room=room).fetchall()
	chat = ''
	for msg in msgs:
		chat += msg[0] + '\n'
	#Determine if the other person is already in the chatroom, and display if they are
	if room in rooms:
		for user in rooms[room]:
			if user != session.get('user'):
				chat += '\n<'+user+' is chatting>'
	other = getOther(room)

	return render_template('chat.jade', room=room, chat=chat, otherUser=other)
##
#Events
##
@socketio.on('joined', namespace='/chat')
def join(message):
	room = session.get('room')
	join_room(room)
	if not room in rooms:
		rooms[room] = set()
	rooms[room].add(session.get('user'))

	msg = '<' + session.get('user') +' joined the chat>'
	emit('message', {'msg': msg}, room=room)

@socketio.on('text', namespace='/chat')
def getMsg(message):
	room = session.get('room')
	msg = session.get('user') + ': ' + message['msg']
	addMessage(msg, room)
	emit('message', {'msg': msg}, room=room)
	#If other user is not online and message not recently sent (?), do stuff
	if isOtherOffline(room) and not isOtherNotified(room):
		pushNotification(getOther(room), session.get('user')+' messaged you', '/chat/'+room)

@socketio.on('disconnect', namespace='/chat')
def dc():
	room = session.get('room')
	leave_room(room)
	rooms[room].remove(session.get('user'))
	if len(rooms[room] == 0):
		del(rooms[room])

	msg = '<' + session.get('user') +' left the chat>'
	emit('message', {'msg': msg}, room=room)

@socketio.on('typing', namespace='/chat')
def isTyping(message):
	room = session.get('room')
	emit('userTyping', {'user': session.get('user')}, room=room)

@socketio.on('doneTyping', namespace='/chat')
def doneTyping(message):
	room = session.get('room')
	emit('userDoneTyping', {'user': session.get('user')}, room=room)