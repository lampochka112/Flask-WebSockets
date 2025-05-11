from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Храним данные: {sid: {'nickname': str, 'room': str}}
users = {}
messages = []

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print(f"Клиент подключился: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in users:
        nickname = users[request.sid]['nickname']
        emit('user_left', {'nickname': nickname}, broadcast=True)
        del users[request.sid]

@socketio.on('set_nickname')
def handle_set_nickname(data):
    users[request.sid] = {
        'nickname': data['nickname'],
        'room': 'general'
    }
    emit('user_joined', {'nickname': data['nickname']}, broadcast=True)
    # Отправляем историю сообщений новому пользователю
    for msg in messages:
        emit('new_message', msg, room=request.sid)

@socketio.on('send_message')
def handle_message(data):
    time = datetime.now().strftime('%H:%M')
    message_data = {
        'nickname': users[request.sid]['nickname'],
        'message': data['message'],
        'time': time
    }
    messages.append(message_data)
    emit('new_message', message_data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)