import requests
from bs4 import BeautifulSoup

# Remplacer par un input quand tout marchera
URL = "https://lcplanta.ch/"
r = requests.get(URL)

# Voir output
# soup = BeautifulSoup(r.content, "html5lib")
# print(soup.prettify())

soup = BeautifulSoup(r.content, "html5lib")

for linkSoups in soup.findAll("link"):
    linkSoups_Href = linkSoups["href"]
    print(linkSoups_Href)