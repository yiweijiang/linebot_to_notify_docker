import requests
from bs4 import BeautifulSoup

def PTTCrawler():
    res = '\n'
    url = 'https://www.ptt.cc/'
    web = requests.get('https://www.ptt.cc/bbs/Gossiping/index.html', cookies={'over18':'1'})
    soup = BeautifulSoup(web.text, "html.parser")
    nrecs = soup.find_all('div', class_='nrec')
    titles = soup.find_all('div', class_='title')
    for nrec, title in zip(nrecs, titles):
        if title.find('a') != None and nrec.text.isdigit():
            if int(nrec.text) >= 50:
                res += f"{title.find('a').get_text()}\n{url + title.find('a')['href']}\n\n"
    return res