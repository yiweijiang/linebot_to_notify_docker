from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from bs4 import BeautifulSoup
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class StockStrategy():
	def __init__(self):
		self.TradingVolumeDict = {}
		# self.driver = webdriver.Remote(
		# 	command_executor='http://chrome:4444/wd/hub',
		# 	desired_capabilities=DesiredCapabilities.CHROME,
		# )

		options = webdriver.ChromeOptions()
		options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
		chromePATH = os.environ.get("CHROMEDRIVER_PATH", '')
		self.driver = webdriver.Chrome(chromePATH, options=options)

	def Crawler(self, url):
		res = []
		try:
			self.driver.get(url)
			element = WebDriverWait(self.driver, 10).until(
				EC.presence_of_element_located((By.ID, "tblStockList"))
			)
			soup = BeautifulSoup(self.driver.page_source, "html.parser")
			for row in soup.find('table', {'id':'tblStockList'}).find_all('tr',{'id':re.compile('^row')}):
				data = [td.text for td in row.find_all('td')]
				res.append(data)
		except:
			return []
		return res

	def Strategy(self, strategy):
		msg = ''
		url = ''
		if strategy == 'MACD':
			url = 'https://goodinfo.tw/tw/StockList.asp?RPT_TIME=&MARKET_CAT=%E6%99%BA%E6%85%A7%E9%81%B8%E8%82%A1&INDUSTRY_CAT=%E6%97%A5OSC+%E2%86%97%40%40%E6%97%A5MACD%E8%B5%B0%E5%8B%A2%40%40OSC+%E2%86%97'
		elif strategy == 'KDCross':
			url = 'https://goodinfo.tw/tw/StockList.asp?RPT_TIME=&MARKET_CAT=%E6%99%BA%E6%85%A7%E9%81%B8%E8%82%A1&INDUSTRY_CAT=%E6%97%A5KD+20~50%E9%BB%83%E9%87%91%E4%BA%A4%E5%8F%89%40%40%E6%97%A5KD%E7%9B%B8%E4%BA%92%E4%BA%A4%E5%8F%89%40%40KD+20~50%E9%BB%83%E9%87%91%E4%BA%A4%E5%8F%89'
		res = self.Crawler(url)
		# r = []
		for i in res:
			if i[0] in self.TradingVolumeDict:
				# r.append(i[:3] + [self.TradingVolumeDict[i[0]]])
				msg += f'{i[1]}({i[0]}) {self.TradingVolumeDict[i[0]]}\n'
		# print(msg)
		return msg

	def TradingVolume(self):
		url = 'https://goodinfo.tw/tw/StockList.asp?RPT_TIME=&MARKET_CAT=%E6%99%BA%E6%85%A7%E9%81%B8%E8%82%A1&INDUSTRY_CAT=%E6%88%90%E4%BA%A4%E5%83%B9%E5%9C%A8%E4%B8%89%E5%B9%B4%E7%B7%9A%E4%B9%8B%E4%B8%8A%40%40%E6%88%90%E4%BA%A4%E5%83%B9%E5%9C%A8%E5%9D%87%E5%83%B9%E7%B7%9A%E4%B9%8B%E4%B8%8A%40%40%E4%B8%89%E5%B9%B4%E7%B7%9A'
		res = self.Crawler(url)
		for i in res:
			price = float(i[2])
			volume = int(i[5].replace(',', ''))
			if (volume < 1200) or (price > 250) or (i[0][:2] == '28') or (i[0][0] == '0') or ('KY' in i[1]) or ('DR' in i[1]):
				continue
			else:
				self.TradingVolumeDict[i[0]] = price

		# print(self.TradingVolumeDict)

# s = StockStrategy()
# s.TradingVolume()
# s.Strategy('MACD')
# # s.Strategy('KDCross')
# s.driver.close()