from aiohttp import web
import socketio
import asyncio
import json

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
    # prend le cookie contenant le lien
    link = list(filter(lambda x: 'SEARCH_LINK' in x, cookie.split('; ')))[0].split("=")[1]
    print(link)

    # on fait une promesse en lancant le subprocess 
    await asyncio.ensure_future(run_subprocess(link,sid))

    # ouvre le json crée
    f = open(f'temp_subprocess_output/{sid}.json')
    
    # convertie le json en dictionnaire
    data = json.load(f)
    
    # ferme le ficher
    f.close()
    
    # envoie le resultat au client grace au socketid
    await sio.emit('return test',data,room=sid)
    print(f'Data send to [{sid}]')
    



#creation d'une fonction asynchrone
async def run_subprocess(link,sid):
    print('Starting subprocess')
    # on fait une promesse en créant un subprocess qui va executer le script de scrap 
    proc = await asyncio.create_subprocess_exec('python', 'testasync.py',link,sid, stdout=asyncio.subprocess.PIPE)
    # on récupère l'output brut
    stdout, stderr = await proc.communicate()
    # la réponse est en bytes --> On convertit la réponse en string 
    output = stdout.strip().decode('utf-8')

    print('Subprocess output: ' + output)
    print(f'Subprocess finished with return code {proc.returncode}')





# lancement du serveur
if __name__ == '__main__':
    web.run_app(app) 