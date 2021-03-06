# Importer les librairies utilisées
from requests import get
from bs4 import BeautifulSoup
from urllib.request import Request,urlopen
from urllib import parse
from sys import argv
import time
import pymongo
from requests.exceptions import ConnectionError,ReadTimeout,MissingSchema
import concurrent.futures
from urllib3.exceptions import ReadTimeoutError

# Préfixer les liens sans HTTP(S)
# Faire une liste avec les attributs SRC des éléments script
def Find_All_SRC(soup):
    scriptSRCList = []
    for scriptSoups in soup.findAll("script"):
        try:
            if str(scriptSoups["src"]).find("/") != -1:
                if str(scriptSoups["src"]).startswith("//"):
                    scriptSRCList.append(SSL + ":" + scriptSoups["src"])
                elif str(scriptSoups["src"]).startswith("/"):
                    scriptSRCList.append(URL + scriptSoups["src"])     
                else:
                    scriptSRCList.append(scriptSoups["src"])

        except KeyError:
            pass
    return scriptSRCList

# Faire une liste avec les attributs href des éléments script
def Find_All_HREF(soup):
    scriptHREFList = []
    for scriptSoups in soup.findAll("link"):
        try:
            if str(scriptSoups["href"]).find("/") != -1:
                if str(scriptSoups["href"]).startswith("//"):
                    scriptHREFList.append(SSL + ":" + scriptSoups["href"])
                elif str(scriptSoups["href"]).startswith("/"):
                    scriptHREFList.append(URL + scriptSoups["href"])     
                else:
                    scriptHREFList.append(scriptSoups["href"])

        except KeyError:
            pass
    return scriptHREFList

# Trouver les domains et les librairies utilisées en parsant des liens
def clean_link(all_link):
    raw_lib = []
    domains = []
    for link in all_link:
        raw_output = ''
        version = ''
        # Lister les domaines utilisés
        try:
            if link[0] != '/' and link != "https://www.google-analytics.com":
                raw_output = link.split('/')[2].split(".")[-2] + "." + link.split('/')[2].split(".")[-1]
                if raw_output not in domains and raw_output != DOMAIN and len(raw_output) > 1:
                    domains.append(raw_output)
        except IndexError:
            print(f"[{link}] n'a pas de domain.")


        # Chercher les noms de librairies dans les fichiers JS
        if link.find(".js?ver=") != -1:
            lib = link.split("/")[link.count("/")]
            version = " version=" + lib.split(".js?ver=")[1]
            if lib.find(".min.js?ver=") != -1:
                raw_output = lib.split(".min.js?ver=")[0] + " js" + version
            else:
                raw_output = lib.split(".js?ver=")[0] + " js" + version


        elif (link.find(".js") != -1 or link.find(".css") != -1) and link.find(".json") == -1:
            lib = link.split("/")[link.count("/")]
            if link.split("/")[-2].split(".")[0].isdigit():
                version = " version=" + link.split("/")[-2]
            raw_output = lib.split(".")[0] + " " + lib.split(".")[-1] + version

        if raw_output not in raw_lib and version != '': # les libs sans version sont presque toujours de faux résultats
            raw_lib.append(raw_output)
    return domains,raw_lib

# Retourne tout les mots recherchés dans un texte 
def find_all_word(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub)

#fait des requetes
def load_url(url, timeout):
    try:
        return get(url, timeout = timeout)
    except ConnectionError:
        print(f"requests.exceptions.ConnectionError: [{url}]")

def async_req(urls):
    result = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(load_url, url, 5): url for url in     urls}
        try:
            for future in concurrent.futures.as_completed(future_to_url):
                data = future.result()
                result.append(data)
        except (MissingSchema, ReadTimeout):
            print("la requete n'a pas aboutie")

    return result

# Trouver les librairies importées
def find_imported_lib(link_list):
    imported_lib = []
    r_lists = async_req(link_list)

    for r in r_lists:
        try:
            scriptLocateImport = list(find_all_word(str(r.content),"require("))
            for startimport in scriptLocateImport:
                k = False
                endimport = startimport
                while k == False:
                    if str(r.content)[endimport] == ")":
                        result = str(r.content)[startimport+9:endimport-1]
                        if result not in imported_lib:
                            if result.startswith("./") == False:
                                imported_lib.append(result)

                            k = True
                    endimport +=1

        except AttributeError:
            print("[INFO] Script sans attribut SRC")
    # clean les outputs pour enlever les erreurs
    clean_imported_lib = []
    for lib in imported_lib:
        if not set('[~!@#$%^&*()_+{}":;,\']+$').intersection(lib) and lib != '':
            clean_imported_lib.append(lib + " js")

    return clean_imported_lib
    
# Trouve des libraires spécifiques
def famous_lib_finder(r,all_link):
    rcontent = str(r.content)
    output = []
    wp_plugins = []

    # Trouver le serveur si donné dans les headers de la réponse
    try:
        output = [{"Server":r.headers['Server']}]
    except KeyError:
        output = [{"Server":"Inconnu"}]

    # Détection Wordpress
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

    if WordPress:
        print('WordPress ',version)
        output.append({"name":"WordPress",
                        "version":version,
                        "description":"WordPress est un système de gestion de contenu gratuit, libre et open-source. Ce logiciel écrit en PHP repose sur une base de données MySQL et est distribué par la fondation WordPress.org.",
                        "logo":"https://seeklogo.com/images/W/wordpress-logo-9F351E1870-seeklogo.com.png"
                        })
        for link in all_link:
            if link.find("wp-content/plugins/") != -1:
                plugin = link.split("wp-content/plugins/")[1]
                if plugin.find("/"):
                    plugin = plugin.split("/")[0] + " Wordpress"
                if plugin not in wp_plugins:
                    wp_plugins.append(plugin)


    # Google Analytics
    if rcontent.find("Google Analytics") != -1 or "https://www.google-analytics.com" in all_link:

        print("Google Analytics: Find")
        output.append({"name":"Google Analytics",
                        "description":"Google Analytics est un service gratuit d'analyse d'audience d'un site Web ou d'applications utilisé par plus de 10 millions de sites, soit plus de 80 % du marché mondial.",
                        "logo":"https://logowik.com/content/uploads/images/google-analytics-2020.jpg"
                        })
    # recaptcha api
    if "https://www.google.com/recaptcha/api.js" in all_link:
        output.append({"name":"reCAPTCHA",
                        "description":"reCAPTCHA est un système de détection automatisée d'utilisateurs appartenant à Google et mettant à profit les capacités de reconnaissance de ces derniers, mobilisées par les tests CAPTCHA, pour améliorer par la même occasion le processus de reconnaissance des formes par les robots.",
                        "logo":"https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/RecaptchaLogo.svg/1200px-RecaptchaLogo.svg.png"
                        }) 

    return output,wp_plugins

################## Cherche le logo sur google image ##################
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

def _req(term, results, lang, start):
    resp = get(
        url="https://www.google.com/search",
        headers=usr_agent,
        params=dict(
            q = term,
            num = results + 2, # Prevents multiple requests
            hl = lang,
            start = start,
        )
    )
    if resp.status_code == 429:
        print("Google a bloqué la requète")
        return None
    else:
        print("Requête OK")

    try:
        resp.raise_for_status()
    except ReadTimeoutError:
        return None

    return resp

# cherche des informations sur les technologies utilisées
def search(term_list, num_results=10, lang="fr"):
    output = []
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["Webstats"]
    mycol = mydb["lib"]
    for term in term_list:
        if DOMAIN not in term:
            version = ''
            description = ''
            source = ''

            if term.find(" version=") != -1:
                term,version = term.split(" version=")

            ########### MONGO ######### cherche si la technologie est deja dans la base de donné
            if mycol.find_one({"name":term}) != None:
                mongolib = mycol.find_one({"name":term})
                print(term + " DB")
                output.append({"name":mongolib["name"],"version":version,"description":mongolib["description"],"logo":mongolib["logo"],"source":mongolib["source"]})

            
            else:
                error = False
                escaped_term = term.replace(' ', '+')
                
                start = 0
                # Send request
                resp = _req(escaped_term, num_results-start, lang, start)
                
                if resp != None:
                        
                    # Parse
                    soup = BeautifulSoup(resp.text, 'html.parser')

                    #find wikipedia desc
                    try:
                        result_desc = soup.find('div', attrs={'id': 'rhs'})
                        description_box = result_desc.find('div', {'class': 'kno-rdesc'})
                        ###image
                        print(term)
                        description = description_box.find_all('span')[-3].text
                        source = "Wikipedia"

                    # Find description du premier lien     
                    except AttributeError:
                        try:
                            result_desc = soup.find('div', attrs={'class': 'g'})
                            description_box = result_desc.find('div', {'style': '-webkit-line-clamp:2'})
                            if description_box:
                                description = description_box.find_all('span')[-1].text
                                
                            #trouve la source
                            source = soup.find('div', attrs={'class': 'g'}).find('a', href=True)["href"]

                        except (IndexError,AttributeError):
                            error = True
                        site = True
                        for black_site in BLACK_LIST:
                            if source.find(black_site) != -1:
                                site = False
                                break
                        if source.find("www.npmjs.com") != -1:
                            r = get(source)
                            soup = BeautifulSoup(r.content,"html5lib")
                            p = soup.find("p", {"class": "_9ba9a726 f4 tl flex-auto fw6 black-80 ma0 pr2 pb1"})
                            print(p.text)
                            if int(p.text.replace(",","")) < 500000:
                                site = False
                            else:
                                site = True
                                


                        if error == False and site:
                            output.append({"name":term,"version":version,"description":description,"logo":search_image_google(term),"source":source})
                            #add to mango
                            mycol.insert_one({"name":term,"description":description,"logo":search_image_google(term),"source":source})

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
if __name__ == "__main__":
    BLACK_LIST = ["github.com","w3schools.com","medium.com","developer.mozilla.org","checkwebsitetools.com","stackoverflow.com","codegrepper"]

    sid = argv[2]
    URL = argv[1]


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

    start_time = time.time()

    all_SRC = Find_All_SRC(soup)
    print("SRC --- %s seconds ---" % (time.time() - start_time))

    all_href = Find_All_HREF(soup)
    print("HREF--- %s seconds ---" % (time.time() - start_time))
    print("%10",flush=True)

    all_link = all_href + all_SRC
    print(all_link,flush=True)
    domains,raw_lib = clean_link(all_link)
    print("CL--- %s seconds ---" % (time.time() - start_time))
    print("%20",flush=True)


    imported_lib = find_imported_lib(all_link)
    print("FIL --- %s seconds ---" % (time.time() - start_time))
    print("%30",flush=True)


    famous_lib,wp_plugins = famous_lib_finder(r,all_link)
    _map = str(len(famous_lib)-1)
    final_output = famous_lib
    print("FLF--- %s seconds ---" % (time.time() - start_time))
    print("%40",flush=True)

    domains_output = search(domains)
    _map += " " + str(len(domains_output))
    final_output += domains_output
    print("Search domains--- %s seconds ---" % (time.time() - start_time))
    print("%60",flush=True)


    imported_lib_output = search(imported_lib)
    _map += " " + str(len(imported_lib_output))
    final_output += imported_lib_output
    print("Search importedlib--- %s seconds ---" % (time.time() - start_time))
    print("%80",flush=True)

    raw_lib_output = search(raw_lib)
    _map += " " + str(len(raw_lib_output))
    final_output += raw_lib_output
    print("Search raw--- %s seconds ---" % (time.time() - start_time))
    print("%90",flush=True)

    
    wp_plugins_output = search(wp_plugins)
    _map += " " + str(len(wp_plugins_output))
    final_output += wp_plugins_output
    print("Search wp_plugins--- %s seconds ---" % (time.time() - start_time))

    final_output[0]["map"] = _map

    print("%100",flush=True)
    print("done")
    fichier = open(f"temp_subprocess_output/{sid}.txt", "a", encoding="utf-8")
    fichier.write(str(final_output))
    fichier.close()