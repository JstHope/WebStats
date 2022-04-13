from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit

app = Flask(__name__)
app.debug = True

socketio = SocketIO(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    return render_template('search.html')


@socketio.on('send link')
def input_link(link):
    emit('return test',"test")


if __name__ == '__main__':
    socketio.run(app)