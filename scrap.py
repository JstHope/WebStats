# Importer les librairies utilisées
from requests import get
from bs4 import BeautifulSoup
from search_info_on_google import search
# Préfixer les liens sans HTTP(S)
# Faire une liste avec les attributs SRC des éléments script
def Find_All_SRC(soup):
    scriptSRCList = []
    for scriptSoups in soup.findAll("script"):
        try:
            if str(scriptSoups["src"])[0:2] == '//':
                scriptSRCList.append(SSL + ":" + scriptSoups["src"])
            elif str(scriptSoups["src"])[0] == '/':
                scriptSRCList.append(URL + scriptSoups["src"])     
            else:
                scriptSRCList.append(scriptSoups["src"])

        except:
            print("",end="")
    return scriptSRCList

# Faire une liste avec les attributs href des éléments script
def Find_All_HREF(soup):
    scriptHREFList = []
    for scriptSoups in soup.findAll("link"):
        try:
            if str(scriptSoups["href"])[0:2] == '//':
                scriptHREFList.append(SSL + ":" + scriptSoups["href"])
            elif str(scriptSoups["href"])[0] == '/':
                scriptHREFList.append(URL + scriptSoups["href"])     
            else:
                scriptHREFList.append(scriptSoups["href"])

        except:
            print("",end="")
    return scriptHREFList

# Trouver les min.js
def clean_link(all_link):
    raw_lib = []
    domains = []
    for link in all_link:
        version = ''
        # Lister les domaines utilisés
        try:
            if link[0] != '/':
                raw_output = link.split('/')[2].split(".")[-2]
                if raw_output not in domains and raw_output != DOMAIN:
                    domains.append(raw_output)
        except:
            print(f"{link} n'a pas de domains")

        # Chercher les noms d'extensions dans les fichiers JS
        if link.find(".js?ver=") != -1:
            lib = link.split("/")[link.count("/")]
            version = " version=" + lib.split(".js?ver=")[1]
            if lib.find(".min.js?ver=") != -1:
                raw_output = lib.split(".min.js?ver=")[0] + " js" + version
            else:
                raw_output = lib.split(".js?ver=")[0] + " js" + version
            if raw_output not in raw_lib:
                raw_lib.append(raw_output)

        elif (link.find(".js") != -1 or link.find(".css") != -1) and link.find(".json") == -1:
            lib = link.split("/")[link.count("/")]
            if link.split("/")[-2].split(".")[0].isdigit() == True:
                version = " version=" + link.split("/")[-2]
            raw_output = lib.split(".")[0] + " " + lib.split(".")[-1] + version
            if raw_output not in raw_lib:
                raw_lib.append(raw_output)
    return domains,raw_lib

#retourne tout les mots recherché dans un text 
def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # utiliser start += 1 pour trouver les matchs qui se superposent

# Trouver les librairies importées
def find_imported_lib(link_list):
    imported_lib = []
    for src in link_list:
        try:
            r = get(src)
            scriptLocateImport = list(find_all(str(r.content),"require("))
            for startimport in scriptLocateImport:
                k = False
                endimport = startimport
                while k == False:
                    if str(r.content)[endimport] == ")":
                        result = str(r.content)[startimport+9:endimport-1]
                        if result not in imported_lib:
                            imported_lib.append(result)
                            k = True
                    endimport +=1

        except:
            print("Script sans attribut SRC: ",src)
    # clean les output pour enlever les erreurs
    clean_imported_lib = []
    for lib in imported_lib:
        if not set('[~!@#$%^&*()_+{}":;\']+$').intersection(lib):
            clean_imported_lib.append(lib)
    return clean_imported_lib
    

def famous_lib_finder(r,all_link):
    rcontent = str(r.content)
    output = []
    # Trouver le serveur si donné dans les headers de la réponse
    try:
        output = [{"Server":r.headers['Server']}]
    except:
        output = [{"Server":"Inconnu"}]

    # Wordpress finder
    WordPress = ''
    i=''
    count = 0
    if rcontent.find('<meta name="generator" content=') != -1 and rcontent.find("WordPress") != -1:
        index = rcontent.find('<meta name="generator" content=')
        while i != '>':
            i = rcontent[index + count]
            WordPress += i
            count +=1
        version = WordPress.split('WordPress ')[1].split('"')[0]
        WordPress = True

    elif rcontent.find('<meta name=generator content=') != -1 and rcontent.find("WordPress") != -1:
        index = rcontent.find('<meta name=generator content=')
        while i != '>':
            i = rcontent[index + count]
            WordPress += i
            count +=1
        version = WordPress.split('WordPress ')[1].split('"')[0]
        WordPress = True
    else:
        count = 0
        if all_link:
            while WordPress != True and count < len(all_link):
                if all_link[count].find("wp-content") != -1:
                    WordPress = True
                count += 1
        version = ''

    if WordPress == True:
        print('WordPress ',version)
        output.append({"name":"WordPress",
                        "version":version,
                        "description":"WordPress est un système de gestion de contenu gratuit, libre et open-source. Ce logiciel écrit en PHP repose sur une base de données MySQL et est distribué par la fondation WordPress.org.",
                        "logo":"https://seeklogo.com/images/W/wordpress-logo-9F351E1870-seeklogo.com.png"
                        })

    # Google Analytics
    if rcontent.find("Google Analytics") != -1:
        print("Google Analytics: Find")
        output.append({"name":"WordPress",
                        "version":version,
                        "description":"WordPress est un système de gestion de contenu gratuit, libre et open-source. Ce logiciel écrit en PHP repose sur une base de données MySQL et est distribué par la fondation WordPress.org.",
                        "logo":"https://seeklogo.com/images/W/wordpress-logo-9F351E1870-seeklogo.com.png"
                        })

    return output

####################################################################################################################################
####################################################################################################################################
#MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN#
####################################################################################################################################
####################################################################################################################################
#MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN#
####################################################################################################################################
####################################################################################################################################
#MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN##MAIN#
####################################################################################################################################
####################################################################################################################################


        
# Définir la page à scraper
URL = "https://www.wikidot.com"
SSL = URL[:URL.find("://")]
DOMAIN = URL.split("/")[2].split(".")[-2]

if URL[-1] == "/":
    URL = URL[:-1]
# Raccourcir la requête en une variable
r = get(URL)
rcontent = str(r.content)
# Récupérer et parser le code source de la page
soup = BeautifulSoup(r.content, "html5lib")

black_list = ['https://developer.mozilla.org']
white_list = ["Google Analytics"]





all_SRC = Find_All_SRC(soup)
all_href = Find_All_HREF(soup)
all_link = all_href + all_SRC

domains,raw_lib = clean_link(all_link)
""" 
imported_lib = find_imported_lib(all_link)

 """
famous_lib = famous_lib_finder(r,all_link)

print(domains)
infos = search(domains)
