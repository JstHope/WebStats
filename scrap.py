# Importer les librairies utilisées
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
        print("Pas d'attribut SRC")

print(scriptSRCList)

# Récupérer les attributs href des éléments link sur la page
#for linkSoups in soup.findAll("link"):
#    linkSoups_HREF = linkSoups["href"]
#    print(linkSoups_HREF)

# Voir output
# soup = BeautifulSoup(r.content, "html5lib")
# print(soup.prettify())