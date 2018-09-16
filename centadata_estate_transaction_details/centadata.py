import bs4
import requests
import numpy as np 
import pandas as pd 
import sys
import traceback
from pathlib import Path
import re
import json

DEBUG = True
acode = ''
cblgcode = ''
cci_price = ''
header = []

# Function to set up request URL.
def getURL():
	url = "http://hk.centadata.com/transactionhistory.aspx?type=2&code=SBYYBPEVPG&ci=zh-hk"
	return url

def getPostURL():
	url = "http://hk.centadata.com/Ajax/AjaxServices.asmx/GenTransactionHistoryPinfo"
	return url

# Function to setup request header.
def setupSession():
	session = requests.Session()
	session.header = {
					'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
					'Accept-Encoding': "gzip, deflate, sdch",
					'Host': "hk.centadata.com",
					# 'Referer': "http://hk.centadata.com/ptest.aspx?type=2&code=SBYYBPEVPG&ref=CD2_Main",
					'Connection': "keep-alive"
					}
	return session

def setupPostSession():
	session = requests.Session()
	session.header = {
					'Connection': "keep-alive",
					'Host': "hk.centadata.com",
					'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
					'Origin': "http://hk.centadata.com",
					'X-Requested-With': "XMLHttpRequest"
					}
	return session

def htmlDecode(str):
	s = "";
	if (len(str) == 0):
		return ""
	s = str.replace('&amp;',"&")
	s = s.replace('&lt;',"<")
	s = s.replace('&gt;',">")
	s = s.replace('&nbsp;'," ")
	s = s.replace('&#39;',"\'")
	s = s.replace('&quot;',"\"")
	return s

def standardize(s):
    temp = str(s)
    temp = temp.replace(' ','')
    temp = temp.replace('\n','')
    temp = temp.replace('\t','')
    temp = temp.replace('\r','')
    temp = temp.replace('@','')
    temp = temp.replace('(實)','')
    temp = temp.replace('(建)','')

    if temp in ["--",""]:
        temp = "N/A"
    return temp

# class Trans:
# 	def __init__(self, no_of_trans):
# 		self.no_of_trans  = no_of_trans
# 		self.date      = ''
# 		self.price_tot = ''
# 		self.price_unit_act = ''
# 		self.price_unit_con = ''

class Estate:
	eCount = 0

	def __init__(self):
		Estate.eCount += 1
		self.id = Estate.eCount
		self.area_act   = ''
		self.area_con   = ''
		self.last_price = ''
		self.last_date  = ''
		self.est_name   = ''
		self.transDict  = {}

	def EstatStandardize(self):
		self.area_act   = standardize(self.area_act)
		self.area_con   = standardize(self.area_con)
		self.last_price = standardize(self.last_price)
		self.last_date  = standardize(self.last_date)
		self.est_name   = standardize(self.est_name)

	def toJSON(self):
		EstateDict = self.__dict__
		return json.dumps(EstateDict)

	def toObj(self, str):
		EstateDict = json.loads(str)
		self.id = int(EstateDict['id'])
		self.area_act   = EstateDict['area_act']
		self.area_con   = EstateDict['area_con']
		self.last_price = EstateDict['last_price']
		self.last_date  = EstateDict['last_date']
		self.est_name   = EstateDict['est_name']
		self.transDict  = EstateDict['transDict']
		"""Trans = {
				'date':,
				'price_tot':,
				'price_unit_act':,
				'price_unit_con':
				}"""

	def inLine(self):
		line = [self.id,
				self.area_act,
				self.area_con,
				self.last_price,
				self.last_date,
				self.est_name
				]
		for i in range(0, len(self.transDict), 1):
			line.append(self.transDict[str(i+1)]['date'])
			line.append(self.transDict[str(i+1)]['price_tot'])
			line.append(self.transDict[str(i+1)]['price_unit_act'])
			line.append(self.transDict[str(i+1)]['price_unit_con'])
		return line

	def printObj(self):
		print("-------------------------")
		print("Estate ID: " + str(self.id))
		print(self.est_name)
		print(self.area_act)
		print(self.area_con)
		print(self.last_price)
		print(self.last_date)
		print(self.transDict)
		print("-------------------------")

def getPostParam(cblgcodeList, transaction):
	cblgcode = cblgcodeList.iloc[counter-1, 1]
	acode = transaction.find('input', class_ = "hdfcuntCode")
	cci_price = transaction.find('input', class_ = "hdfcciPrice")

	param = {
			'acode': acode.get('value'),
			'cblgcode': cblgcode,
			'cci_price': cci_price.get('value')
			}
	return param


if __name__ == "__main__":

	counter = 0

	path = Path("./EstateCode.csv")
	if path.is_file():
		cblgcodeList = pd.read_csv("./EstateCode.csv", sep = ',')
		print(cblgcodeList) if DEBUG else{}
	else:
		print("Download estate code first.")
		exit()

	# Set up requests session header, retrieve and decode data from server.
	urlList = [getURL()]

	session = setupSession()

	# Store estate information in estateList.
	estateList = []

	# Web Crawling
	for url in urlList:
		counter += 1
		newEstate = Estate()
		try:
			response = session.get(url = url, timeout = 10)
			soup = bs4.BeautifulSoup(response.content, 'lxml', from_encoding = 'utf-8')    # Decoding: UTF-8

			# table = soup.find('table', id = "unitTran-main-table")
			tables = soup.find_all('table', class_ = "unitTran-sub-table")

			for sub_table in tables:
				sys.stderr.write(str(len(tables))) if DEBUG else {}
				transactions = sub_table.find_all('tr', class_ = 'trHasTrans')
				
				for transaction in transactions:
					entries = transaction.find_all('td')
					newEstate.last_price = entries[2].string
					newEstate.last_date = entries[3].get_text()

					data = getPostParam(cblgcodeList, transaction)
					
					session_post = setupPostSession()
					response_post = session_post.post(getPostURL(), data = data, timeout = 10)
					soup_post = bs4.BeautifulSoup(htmlDecode(response_post.text), 'lxml')
					# print(soup_post)

					tables_post = soup_post.find_all('table')
					estate_info2 = tables_post[1].find_all('td')
					trans_info = tables_post[4].find_all('td')
					sys.stderr.write(str(estate_info2)) if DEBUG else {}
					sys.stderr.write(str(trans_info)) if DEBUG else {}

					newEstate.est_name = estate_info2[1].string
					newEstate.area_act = estate_info2[3].string
					newEstate.area_con = estate_info2[5].string

					trans_no = int(len(trans_info) / 5)
					trans_date, trans_price, unit_act, unit_con, trans_rate = [], [], [], [], []
					for i in range(0, trans_no, 1):
						trans_date.append(trans_info[5*i].string)
						trans_price.append(trans_info[5*i+1].string)
						unit_act.append(trans_info[5*i+2].string)
						unit_con.append(trans_info[5*i+3].string)
						trans_rate.append(trans_info[5*i+4].find('span').get_text())
					for i in range(0, trans_no, 1):
						newTrans = {
									'date': standardize(trans_date[i]),
									'price_tot': standardize(trans_price[i]),
									'price_unit_act': standardize(unit_act[i]),
									'price_unit_con': standardize(unit_con[i])
									}
						newEstate.transDict[str(i+1)] = newTrans
					newEstate.EstatStandardize()
					newEstate.printObj()
					
					# break

					estateList.append(newEstate.toJSON())
					newEstate = Estate()
				# break

		except Exception as e:
			print("Error: cannot fetch data with EstateID: " + str(Estate.eCount) + " url: " + str(url))
			answer = input("End Crawler?[y/n] ")
			if answer == 'y':
				traceback.print_exc()
				print("Exiting...")
				exit()
			else:
				print("Continuing...")

	json_file = "./Estate.json"
	path = Path(json_file)
	if path.is_file():
		print("Estate.json already exists!")
		answer = input("Rewrite?[y/n]")
		if (answer != 'y'):
			json_file = input("New file name: ")
		
	with open(json_file, 'w', encoding = 'utf-8') as f:
		f.write(json.dumps(estateList, indent = 4))

		

