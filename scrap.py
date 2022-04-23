# Importer les librairies utilisées
from requests import get
from bs4 import BeautifulSoup
import time
from urllib.request import Request
from urllib.request import urlopen
from urllib import parse

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
def clean_link(all_links):
    raw_lib = []
    domains = []
    for link in all_links:
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

# Retourne tout les mots recherchés dans un texte 
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
    # Nettoyer les outputs pour enlever les erreurs
    clean_imported_lib = []
    for lib in imported_lib:
        if not set('[~!@#$%^&*()_+{}":;\']+$').intersection(lib) and lib != '':
            clean_imported_lib.append(lib + " js")

    return clean_imported_lib
    

def famous_lib_finder(r,all_links):
    rcontent = str(r.content)
    output = []
    # Trouver le serveur si donné dans les headers de la réponse
    try:
        output = [{"Server":r.headers['Server']}]
    except:
        output = [{"Server":"Inconnu"}]

    # Détecteur de Wordpress
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
        if all_links:
            while WordPress != True and count < len(all_links):
                if all_links[count].find("wp-content") != -1:
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

################## Chercher le logo sur Google images ##################

def search_image_google(query):
    search = parse.quote(query)
    url = f'https://www.google.com/search?q={search}+logo&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg'
    headers={'User-Agent':"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"}

    req = Request(url, headers=headers)
    resp = urlopen(req)  
    soup = BeautifulSoup(str(resp.read()),"html.parser")

    images = soup.find_all("img")
    return images[1]["src"]

################################################################################################
##################################### PARTIE GOOGLE SEARCH #####################################
################################################################################################

usr_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

def _req(term, results, lang, start, proxies):
    resp = get(
        url="https://www.google.com/search",
        headers=usr_agent,
        params=dict(
            q = term,
            num = results + 2, # Empêcher les requêtes multiples
            hl = lang,
            start = start,
        ),
        proxies=proxies,
    )
    resp.raise_for_status()
    return resp

def search(term_list, num_results=10, lang="fr", proxy=None, advanced=False):
    start_time = time.time()
    description = ''
    output = []
    for term in term_list:
        error = False
        escaped_term = term.replace(' ', '+')

        # Proxy
        proxies = None
        if proxy:
            if proxy[:5]=="https":
                proxies = {"https": proxy} 
            else:
                proxies = {"http": proxy}
        
        # Fetch
        start = 0
        # Envoyer request
        resp = _req(escaped_term, num_results-start, lang, start, proxies)

        # Parse
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Trouver la description Wikipédia
        try:
            result_desc = soup.find('div', attrs={'id': 'rhs'})
            description_box = result_desc.find('div', {'class': 'kno-rdesc'})
            ###image
            images = soup.find_all('img')
            for image in images:
                if str(image.get("id"))[0:5] == "dimg_" or str(image.get("id"))[0:7] == "wp_thbn":
                    print("",end="")

            description = description_box.find('span').text
            source = "Wikipedia"

        # Trouver le description du premier lien     
        except:
            try:
                result_desc = soup.find('div', attrs={'class': 'g'})
                description_box = result_desc.find('div', {'style': '-webkit-line-clamp:2'})
                if description_box:
                    description = description_box.find_all('span')[-1].text
                    
                # Trouver la source
                source = soup.find('div', attrs={'class': 'g'}).find('a', href=True)["href"]

            except:
                error = True
        if error == False and source.find("github.com") == -1 and source.find("https://developer.mozilla.org") == -1 and source.find("'https://medium.com"): # faux positif
            output.append({"name":term,"description":description,"image":search_image_google(term),"source":source})

    print("--- %s seconds ---" % (time.time() - start_time))
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
URL = "https://www.lcplanta.ch"

if URL[-1] == "/":
    URL = URL[:-1]


SSL = URL[:URL.find("://")]
DOMAIN = URL.split("/")[2].split(".")[-2]

r = get(URL)
print(r.status_code)
if r.status_code != 200:
    URL = URL.split("://")[0] + "://" +  URL.split("://")[1][4:]
    r = get(URL)


rcontent = str(r.content)
# Récupérer et parser le code source de la page
soup = BeautifulSoup(rcontent, "html5lib")

white_list = ["Google Analytics"]


all_SRC = Find_All_SRC(soup)
all_href = Find_All_HREF(soup)
all_links = all_href + all_SRC
domains,raw_lib = clean_link(all_links)

# imported_lib = find_imported_lib(all_links) # cassé

famous_lib = famous_lib_finder(r,all_links)

final_output = famous_lib + search(raw_lib)
