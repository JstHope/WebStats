import socketio

# On cree notre serveur
sio = socketio.Server()

static_files = {
    '/': 'index.html',
    'search': 'search.html',
}

