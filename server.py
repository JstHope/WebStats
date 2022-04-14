from aiohttp import web
import socketio
import asyncio

## Crée un serveur Async Socket IO 
sio = socketio.AsyncServer()
## Crée une nouvelle application web Aiohttp
app = web.Application()

# Attache notre application web a notre serveur
sio.attach(app)

# Pour retourner le index.html de manière envoyable pour le serveur
def index(request):
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')
def search(request):
    with open('search.html') as f:
        return web.Response(text=f.read(), content_type='text/html')

## On attache nos fichier html a notre serveur
app.router.add_get('/', index)
app.router.add_get('/search', search)



@sio.on("send link")
async def send_all_data(sid,cookie):
    link = list(filter(lambda x: 'SEARCH_LINK' in x, cookie.split('; ')))[0].split("=")[1]
    print(link)
    
    await sio.emit('return test',link,room=sid)
    print(f'Data send to [{sid}]')
    

if __name__ == '__main__':
    web.run_app(app) 