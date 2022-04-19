# Importer les librairies utilisées
import requests,googlesearch
from bs4 import BeautifulSoup

# trouver wp: <meta name=generator content="WordPress 4.9.8"> <meta name="generator" content="WordPress 4.9.8">

# Définir la page à scraper
URL = "https://www.faceit.com/fr/home"
SSL = URL[:URL.find("://")]
DOMAIN = URL.split("/")[2].split(".")[-2]
# Raccourcir la requête en une variable
r = requests.get(URL)
rcontent = str(r.content)
# Récupérer et parser le code source de la page
soup = BeautifulSoup(r.content, "html5lib")

black_list = ['https://developer.mozilla.org']
white_list = ["Google Analytics"]

scriptSRCList = []

# Faire une liste avec les attributs SRC des éléments script
for scriptSoups in soup.findAll("script"):
    try:
        if str(scriptSoups["src"])[0:2] == '//':
            scriptSRCList.append(SSL + ":",scriptSoups["src"])
        else:
            scriptSRCList.append(scriptSoups["src"])

    except:
        print("",end="")

# Faire une liste avec les attributs href des éléments script
for scriptSoups in soup.findAll("link"):
    try:
        if str(scriptSoups["href"])[0:2] == '//':
            scriptSRCList.append(SSL + ":",scriptSoups["href"])
        else:
            scriptSRCList.append(scriptSoups["href"])
    except:
        print("",end="")

raw_lib = []
domains = []
print(scriptSRCList)
# Trouve les min.js
for link in scriptSRCList:
    version = ''
    # liste les domains utilisé
    try:
        if link[0] != '/':
            output = link.split('/')[2].split(".")[-2]
            if output not in domains and output != DOMAIN:
                domains.append(output)
    except:
        print(f"{link} n'a pas de domains")

    # cherche les noms d'extension dans les fichier js
    if link.find(".js?ver=") != -1:
        lib = link.split("/")[link.count("/")]
        version = " version=" + lib.split(".js?ver=")[1]
        if lib.find(".min.js?ver=") != -1:
            output = lib.split(".min.js?ver=")[0] + " js" + version
        else:
            output = lib.split(".js?ver=")[0] + " js" + version
        if output not in raw_lib:
            raw_lib.append(output)

        
    elif (link.find(".js") != -1 or link.find(".css") != -1) and link.find(".json") == -1:
        lib = link.split("/")[link.count("/")]
        if link.split("/")[-2].split(".")[0].isdigit() == True:
            version = " version=" + link.split("/")[-2]
        output = lib.split(".")[0] + " " + lib.split(".")[-1] + version
        if output not in raw_lib:
            raw_lib.append(output)

print(domains)
print(raw_lib)


""" 
# trouve les lib importé
def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches

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
"""

# Wordpress finder
WordPress = ''
i=''
count = 0
if rcontent.find('<meta name="generator" content=') != -1:
    index = rcontent.find('<meta name="generator" content=')
    while i != '>':
        i = rcontent[index + count]
        WordPress += i
        count +=1
    WordPress = WordPress.split('WordPress ')[1].split('"')[0]

elif rcontent.find('<meta name=generator content=') != -1:
    index = rcontent.find('<meta name=generator content=')
    while i != '>':
        i = rcontent[index + count]
        WordPress += i
        count +=1
    WordPress = WordPress.split('WordPress ')[1].split('"')[0]
else:
    count = 0
    if scriptSRCList:
        while WordPress != True and count < len(scriptSRCList):
            if scriptSRCList[count].find("wp-content") != -1:
                WordPress = True
            count += 1
print("WordPress: ",WordPress)

# Google Analytics
if rcontent.find("Google Analytics") != -1:
    print("Google Analytics: Find")





## chercher les infos a afficher + chercher si pas faux résultats
# on commence par les domains: 

#si ya pas de wikipedia
for domain in domains:
    search = list(googlesearch.search(domain,lang="fr"))
    site = str(requests.get(search[0]).content)
    debut = site.find('<meta name="description" content=')
    count = 34
    result = ''
    k = ''
    while k != '>':
        k = site[debut + count]
        count +=1
        result += k
    result = result[:-2]
    print("source: ",search[0])
    print(result,"\n")












# go tout chercher sur ca https://www.npmjs.com/package/... ou equivalent voire si dl< nbr