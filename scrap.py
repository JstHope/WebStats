# Importer les librairies utilisées
from requests import get
from bs4 import BeautifulSoup
from urllib.request import Request,urlopen
from urllib import parse
from sys import argv
from time import sleep
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
                if raw_output not in domains and raw_output != DOMAIN and len(raw_output) > 1:
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


        elif (link.find(".js") != -1 or link.find(".css") != -1) and link.find(".json") == -1:
            lib = link.split("/")[link.count("/")]
            if link.split("/")[-2].split(".")[0].isdigit() == True:
                version = " version=" + link.split("/")[-2]
            raw_output = lib.split(".")[0] + " " + lib.split(".")[-1] + version

        if raw_output not in raw_lib:
            raw_lib.append(raw_output)
            
    return domains,raw_lib

#retourne tout les mots recherché dans un text 
def find_all_word(a_str, sub):
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
            scriptLocateImport = list(find_all_word(str(r.content),"require("))
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
        if not set('[~!@#$%^&*()_+{}":;,\']+$').intersection(lib) and lib != '':
            clean_imported_lib.append(lib + " js")

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
        output.append({"name":"Google Analytics",
                        "description":f"Google Analytics est un service gratuit d'analyse d'audience d'un site Web ou d'applications utilisé par plus de 10 millions de sites, soit plus de 80 % du marché mondial.",
                        "logo":"https://logowik.com/content/uploads/images/google-analytics-2020.jpg"
                        })

    return output

################## cherche le logo sur google image ##################
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
    while True:
        resp = get(
            url="https://www.google.com/search",
            headers=usr_agent,
            params=dict(
                q = term,
                num = results + 2, # Prevents multiple requests
                hl = lang,
                start = start,
            ),
            proxies=proxies,
        )
        if resp.status_code == 429:
            print("spam pas stp")
            sleep(2)
        else:
            print("requet pass :D")
            break

    try:
        resp.raise_for_status()
    except:
        print("trop de requetes a google")
    return resp

def search(term_list, num_results=10, lang="fr", proxy=None):
    description = ''
    output = []
    for term in term_list:
        version = ''
        if term.find(" version=") != -1:
            term,version = term.split(" version=")


        error = False
        escaped_term = term.replace(' ', '+')

        # Proxy
        proxies = ''
        if proxy:
            if proxy[:5]=="https":
                proxies = {"https": proxy} 
            else:
                proxies = {"http": proxy}
        
        # Fetch
        start = 0
        # Send request
        resp = _req(escaped_term, num_results-start, lang, start, proxies)

        # Parse
        soup = BeautifulSoup(resp.text, 'html.parser')

        #find wikipedia desc
        try:
            result_desc = soup.find('div', attrs={'id': 'rhs'})
            description_box = result_desc.find('div', {'class': 'kno-rdesc'})
            ###image
            images = soup.find_all('img')
            for image in images:
                if str(image.get("id"))[0:5] == "dimg_" or str(image.get("id"))[0:7] == "wp_thbn":
                    print("",end="")

            description = description_box.find_all('span')[-3].text
            source = "Wikipedia"

        # Find description du premier lien     
        except:
            try:
                result_desc = soup.find('div', attrs={'class': 'g'})
                description_box = result_desc.find('div', {'style': '-webkit-line-clamp:2'})
                if description_box:
                    description = description_box.find_all('span')[-1].text
                    
                #trouve la source
                source = soup.find('div', attrs={'class': 'g'}).find('a', href=True)["href"]

            except:
                error = True
            site = True
            for black_site in BLACK_LIST:
                if source.find(black_site) != -1:
                    site = False
                    break

            if error == False and site == True:
                output.append({"name":term,"version":version,"description":description,"logo":search_image_google(term),"source":source})

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

BLACK_LIST = ["medium.com","github.com","developer.mozilla.org","checkwebsitetools.com","stackoverflow.com","codegrepper"]


sid = argv[2]
URL = argv[1]
# Définir la page à scraper
#URL = "https://www.wikidot.com"

if URL[-1] == "/":
    URL = URL[:-1]


SSL = URL[:URL.find("://")]
DOMAIN = URL.split("/")[2].split(".")[-2]

r = get(URL)
print(r.status_code)
if r.status_code != 200:
    URL = URL.split("://")[0] + "://" +  URL.split("://")[1][4:]
    r = get(URL)


# Récupérer et parser le code source de la page
soup = BeautifulSoup(r.content, "html5lib")

all_SRC = Find_All_SRC(soup)
all_href = Find_All_HREF(soup)
all_link = all_href + all_SRC
domains,raw_lib = clean_link(all_link)

#imported_lib = find_imported_lib(all_link)

famous_lib = famous_lib_finder(r,all_link)

final_output = famous_lib + search(domains) + search(raw_lib)

final_output[0]["url"] = URL
###
fichier = open(f"temp_subprocess_output/{sid}.txt", "a", encoding="utf-8")
fichier.write(str(final_output))
fichier.close()