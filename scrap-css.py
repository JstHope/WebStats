from requests import get
from bs4 import BeautifulSoup
import tinycss2

# Temp pour travail sur un fichier à part
from scrap import Find_All_HREF

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
