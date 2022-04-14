# Importer les librairies utilisées
from re import T
from socket import create_server
import requests
from bs4 import BeautifulSoup

# Définir la page à scraper
URL = "https://lcplanta.ch/"

# Raccourcir la requête en une variable
r = requests.get(URL)

# Récupérer et parser le code source de la page
soup = BeautifulSoup(r.content, "html5lib")

scriptSRCList = []

for scriptSoups in soup.findAll("script"):
    try:
        scriptSRCList.append(scriptSoups['src'])
    except:
        print("",end='')

for links in scriptSRCList:
    try:
        r = requests.get(links)
        print(r.content)
    except:
        print('lien cancer')

# Récupérer les attributs href des éléments link sur la page
#for linkSoups in soup.findAll("link"):
#    linkSoups_HREF = linkSoups["href"]
#    print(linkSoups_HREF)

# Voir output
# soup = BeautifulSoup(r.content, "html5lib")
# print(soup.prettify())