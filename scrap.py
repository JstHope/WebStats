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


###
###     SRC
###

# Faire une liste avec les attributs SRC des éléments script
scriptSRCList = []

for scriptSoups in soup.findAll("script"):
    try:
        scriptSRCList.append(scriptSoups["src"])
    except:
        print("",end="")

# Aller chercher le contenu des SRC
for SRC in scriptSRCList:
    try:
        r = requests.get(SRC)
        scriptLocateImport = str(r.content).find("import")

        if scriptLocateImport != -1:
            print(str(r.content)[scriptLocateImport:])
        else:
            print("Pas de librairie utilisée dans le script")
    except:
        print("Script sans attribut SRC")


# Récupérer les attributs href des éléments link sur la page
#for linkSoups in soup.findAll("link"):
#    linkSoups_HREF = linkSoups["href"]
#    print(linkSoups_HREF)

# Voir output
# soup = BeautifulSoup(r.content, "html5lib")
# print(soup.prettify())
