from bs4 import BeautifulSoup
from requests import get

usr_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

def _req(term, results, lang, start, proxies):
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
    resp.raise_for_status()
    return resp

def search(term, num_results=10, lang="fr", proxy=None, advanced=False):
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

        description = description_box.find('span').text
        source = "wikipedia"

    # Find description du premier lien     
    except:
        try:
            result_desc = soup.find('div', attrs={'class': 'g'})
            description_box = result_desc.find('div', {'style': '-webkit-line-clamp:2'})
            if description_box:
                description = description_box.find('span').text
            #trouve la source
            source = soup.find('div', attrs={'class': 'g'}).find('a', href=True)["href"]

        except:
            return False

    output = {"description":description,"image":"","source":source}
    return(output)



print(search("bs4"))