from aiohttp import web
import socketio,asyncio,json,os

## Crée un serveur Async Socket IO 
sio = socketio.AsyncServer()
## Crée une nouvelle application web Aiohttp
app = web.Application()

# Attache notre application web a notre serveur
sio.attach(app)

# Pour retourner le index.html
def index(request):
    return web.FileResponse(path='static/index.html', status=200)


#ajout d'un fichier statique
app.router.add_static('/css/',
                       path='static/css',
                       name='css')
app.router.add_static('/font/',
                       path='static/font',
                       name='font')
app.router.add_static('/resources/',
                       path='static/resources',
                       name='resources')

#met une redirection sur / a notre fichier html 
app.router.add_get('/', index)



@sio.on("send link")
async def send_all_data(sid,link):
    # prend le cookie contenant le lien
    print(link)

    # on fait une promesse en lancant le subprocess 
    await asyncio.ensure_future(run_subprocess(link,sid))

    # ouvre le json crée
    f = open(f'temp_subprocess_output/{sid}.json')
    
    # convertie le json en dictionnaire
    data = json.load(f)
    
    # ferme le ficher
    f.close()

    os.remove(f'temp_subprocess_output/{sid}.json')

    
    # envoie le resultat au client grace au socketid
    await sio.emit('receive data',data,room=sid)
    print(f'[Data sended to {sid}]\n\n')
    



#creation d'une fonction asynchrone
async def run_subprocess(link,sid):
    print('/Starting subprocess')
    # on fait une promesse en créant un subprocess qui va executer le script de scrap 
    proc = await asyncio.create_subprocess_exec('python', 'testasync.py',link,sid, stdout=asyncio.subprocess.PIPE)
    # on récupère l'output brut
    stdout, stderr = await proc.communicate()
    # la réponse est en bytes --> On convertit la réponse en string 
    output = stdout.strip().decode('utf-8')

    print('/Subprocess output: ' + output)
    print(f'/Subprocess finished with return code {proc.returncode}')





# lancement du serveur
if __name__ == '__main__':
    web.run_app(app) 