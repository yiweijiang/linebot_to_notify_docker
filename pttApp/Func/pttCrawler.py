import requests
from bs4 import BeautifulSoup

def PTTCrawler():
    res = ''
    url = 'https://www.ptt.cc/'
    web = requests.get('https://www.ptt.cc/bbs/Gossiping/index.html', cookies={'over18':'1'})
    soup = BeautifulSoup(web.text, "html.parser")
    titles = soup.find_all('div', class_='title')
    for i in titles:
        if i.find('a') != None:
            res += f"{i.find('a').get_text()}\n{url + i.find('a')['href']}\n\n"
    return res