# Importer les librairies utilisées
import requests
from bs4 import BeautifulSoup

def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches

# Définir la page à scraper
URL = "https://lcplanta.ch/"
SSL = URL[:URL.find("://")]
# Raccourcir la requête en une variable
r = requests.get(URL)

# Récupérer et parser le code source de la page
soup = BeautifulSoup(r.content, "html5lib")


###
###     SRC
###

# Faire une liste avec les attributs SRC des éléments script
scriptSRCList = [URL]

for scriptSoups in soup.findAll("script"):
    try:
        if str(scriptSoups["src"])[0:2] == '//':
            scriptSRCList.append(SSL + ":",scriptSoups["src"])
        else:
            scriptSRCList.append(scriptSoups["src"])

    except:
        print("",end="")

# Aller chercher le contenu des SRC
for src in scriptSRCList:
    try:
        r = requests.get(src)
        scriptLocateImport = list(find_all(str(r.content),"require("))
        for startimport in scriptLocateImport:
            k = False
            endimport = startimport
            while k == False:
                if str(r.content)[endimport] == ")":
                    print(str(r.content)[startimport+9:endimport-1])
                    k = True
                endimport +=1

    except:
        print("Script sans attribut SRC")


# Récupérer les attributs href des éléments link sur la page
#for linkSoups in soup.findAll("link"):
#    linkSoups_HREF = linkSoups["href"]
#    print(linkSoups_HREF)

# Voir output
# soup = BeautifulSoup(r.content, "html5lib")
# print(soup.prettify())
