from webBackend.models import Ptt_News
from bs4 import BeautifulSoup
import requests
import re

class PTTCrawler():
    def __init__(self, board):
        self.board = board

    def GetIndex(self):
        header = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
        r = requests.get(f'https://www.ptt.cc/bbs/{self.board}/index.html', cookies={'over18':'1'}, headers=header)
        # print(r.text)
        soup = BeautifulSoup(r.text, "html.parser")
        index = soup.find_all('a', class_='btn wide')[1]['href']
        page = int(re.findall(r"\d+", index)[0]) + 1
        print('page=', page)
        return page

    def Crawler(self, url):
        r = requests.get(url, cookies={'over18':'1'})
        soup = BeautifulSoup(r.text, "html.parser")
        nrecs = soup.find_all('div', class_='nrec')
        titles = soup.find_all('div', class_='title')
        authors = soup.find_all('div', class_='author')
        return nrecs, titles, authors

    def GossipingCrawler(self, c):
        print('start GossipingCrawler')
        res = '\n'
        page = self.GetIndex()
        for i in range(c, -1, -1):
            url = f'https://www.ptt.cc/bbs/{self.board}/index{page-i}.html'
            nrecs, titles, authors = self.Crawler(url)
            print(nrecs, titles, authors)
            for nrec, title, author in zip(nrecs, titles, authors):
                if title.find('a') != None and nrec.text.isdigit():
                    if int(nrec.text) >= 50:
                        res += self.InsertORUpdateData(nrec, title, author)
        return res

    def InsertORUpdateData(self, nrec, title, author):
        res = ''
        href = 'https://www.ptt.cc/' + title.find('a')['href']
        # print(href)
        if Ptt_News.objects.filter(URL=href).exists() == False:
            res = f"{title.find('a').get_text()}\n{href}\n\n"
            # 建立新資料
            Ptt_News.objects.create(URL=href,BOARD=self.board,AUTHOR=author.text,TITLE=title.find('a').get_text(),NRECS=int(nrec.text))
        else:
            # 更新推數
            Ptt_News.objects.filter(URL=href).update(NRECS=int(nrec.text))
        return res

    def DeleteData(self):
        all_data = Ptt_News.objects.order_by('id')
        if len(all_data) > 5000:
            for i in all_data[:2000]:
                Ptt_News.objects.filter(id=i.id).delete()

    def StockCrawler(self):
        res_lst = []
        url = 'https://www.ptt.cc/bbs/Stock/search?q=%E8%B2%B7%E8%B3%A3%E8%B6%85'
        nrecs, titles, authors = self.Crawler(url)
        for nrec, title, author in zip(nrecs, titles, authors):
            if title.find('a') != None and nrec.text.isdigit():
                t = title.find('a').get_text()
                if 'Re:' in t:
                    continue
                href = 'https://www.ptt.cc/' + title.find('a')['href']
                if Ptt_News.objects.filter(URL=href).exists() == False:
                    Ptt_News.objects.create(URL=href,BOARD=self.board,AUTHOR=author.text,TITLE=t,NRECS=int(nrec.text))
                else:
                    continue

                r = requests.get(href, cookies={'over18':'1'})
                soup = BeautifulSoup(r.text, "html.parser")
                img =  soup.find('a', {'href':re.compile(r'^https://i.imgur.com/')})
                
                if img:
                    img = img.text
                    # res_lst.append([t, img])
                    res_lst.append([f'{t}\n{href}', img])
        return res_lst

    def main(self, count): # count 代表要抓幾頁的資料
        if self.board == 'Gossiping':
            res = self.GossipingCrawler(count)
        elif self.board == 'Stock':
            res = self.StackCrawler()
        self.DeleteData() # 刪除太多的資料
        return res

# res = PTTCrawler('Gossiping').main(20)
# print(res)