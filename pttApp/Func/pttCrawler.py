import requests
from bs4 import BeautifulSoup
import re
from pttApp.models import Ptt_Info

def PTTCrawler():
    res = '\n'
    url = 'https://www.ptt.cc/'
    web = requests.get('https://www.ptt.cc/bbs/Gossiping/index.html', cookies={'over18':'1'})
    soup = BeautifulSoup(web.text, "html.parser")

    index = soup.find_all('a', class_='btn wide')[1]['href']
    page = int(re.findall(r"\d+", index)[0]) + 1

    for i in range(10, -1, -1):
        page_url = f'https://www.ptt.cc/bbs/Gossiping/index{page-i}.html'
        r = requests.get(page_url, cookies={'over18':'1'})
        soup = BeautifulSoup(r.text, "html.parser")

        nrecs = soup.find_all('div', class_='nrec')
        titles = soup.find_all('div', class_='title')
        for nrec, title in zip(nrecs, titles):
            if title.find('a') != None and nrec.text.isdigit():
                if int(nrec.text) >= 30:
                    href = url + title.find('a')['href']
                    if Ptt_Info.objects.filter(URL=href).exists() == False:
                        res += f"{title.find('a').get_text()}\n{href}\n\n"
                        # 建立新資料
                        Ptt_Info.objects.create(URL=href,TITLE=title.find('a').get_text(),NRECS=int(nrec.text))
                    else:
                        # 更新推數
                        Ptt_Info.objects.filter(URL=href).update(NRECS=int(nrec.text))
    # 刪除太多的資料
    all_data = Ptt_Info.objects.order_by('id')
    if len(all_data) > 1000:
        for i in all_data[:500]:
            Ptt_Info.objects.filter(id=i.id).delete()
    return res

# PTTCrawler()