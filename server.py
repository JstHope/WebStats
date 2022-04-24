from aiohttp import web
from requests import get
from os import remove
from json import load
from requests.exceptions import Timeout
import socketio,asyncio


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
app.router.add_static('/styles/',
                       path='static/styles',
                       name='styles')
app.router.add_static('/font/',
                       path='static/font',
                       name='font')
app.router.add_static('/resources/',
                       path='static/resources',
                       name='resources')
app.router.add_static('/js/',
                       path='static/js',
                       name='js')
#met une redirection sur / a notre fichier html 
app.router.add_get('/', index)



@sio.on("send link")
async def send_all_data(sid,link):
    r=''
    print(link)
    # Test le SSL

    if link[:link.find("://")] == 'https' or link[:link.find("://")] == 'http':
        if link[link.find("://"):][3:7] != "www.":
            link = link[:link.find("://")] + "://www." + link[link.find("://"):][3:]
        try:
            r = get(link, timeout=8)
        except Timeout:
                print('Timeout has been raised.')
                await sio.emit("timeout",room=sid)
        except:
            print("invalid link")
            await sio.emit("invalid link",room=sid)
    else:
        if link[0:4] != "www.":
            link ="www." + link
        try:
            r = get("https://" + link, timeout=8)
            link = "https://" + link
        except Timeout:
            print('Timeout has been raised.')
            await sio.emit("timeout",room=sid)
        except:
            try:
                r = get("http://" + link, timeout=8)
                link = "http://" + link
            except Timeout:
                print('Timeout has been raised.')
                await sio.emit("timeout",room=sid)

            except:
                print("invalid link")
                await sio.emit("invalid link",room=sid)

    if r != '':
        if link[-1] == "/":
            link = link[:-1]
        # on fait une promesse en lancant le subprocess 
        await asyncio.ensure_future(run_subprocess(link,sid))

        # ouvre le txt crée
        f = open(f'temp_subprocess_output/{sid}.txt','r',encoding="utf-8")
        
        # convertie le text en array de dictionnaire
        data = eval(f.read())
        # ferme le ficher
        f.close()
        
        remove(f'temp_subprocess_output/{sid}.txt')

        
        # envoie le resultat au client grace au socketid
        await sio.emit('receive data',data,room=sid)
        print(f'[Data sended to {sid}]\n\n')
    



#creation d'une fonction asynchrone
async def run_subprocess(link,sid):
    print('/Starting subprocess')
    # on fait une promesse en créant un subprocess qui va executer le script de scrap 
    proc = await asyncio.create_subprocess_exec('python', 'scrap.py',link,sid, stdout=asyncio.subprocess.PIPE)
    # on récupère l'output brut
    stdout, stderr = await proc.communicate()
    # la réponse est en bytes --> On convertit la réponse en string 
    output = stdout.strip()

    #print('/Subprocess output: ' + output)
    print(f'/Subprocess finished with return code {proc.returncode}')





# lancement du serveur
if __name__ == '__main__':
    web.run_app(app) 