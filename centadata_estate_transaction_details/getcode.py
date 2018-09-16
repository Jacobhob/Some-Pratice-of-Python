import bs4
import requests
import numpy as np 
import pandas as pd 
import sys
import traceback
import re

DEBUG = True
header = ['Estate', 'Code']

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


if __name__ == "__main__":

	counter = 0

	# Set up requests session header, retrieve and decode data from server.
	urlList = [getURL()]

	session = setupSession()

	# Store estate information in estateList.
	estateList = pd.DataFrame(data = None, columns = header)

	# Web Crawling
	for url in urlList:
		counter += 1
		try:
			response = session.get(url = url, timeout = 10)
			soup = bs4.BeautifulSoup(response.content, 'lxml', from_encoding='utf-8')    # Decoding: UTF-8

			table = soup.find('div', class_ = "build-select-content select-content")
			codes = table.find_all('a')

		except Exception as e:
			print("Error: cannot fetch data with url: " + str(url))
			answer = input("End Crawler?[y/n] ")
			if answer == 'y':
				traceback.print_exc()
				print("Exiting...")
				exit()
			else:
				print("Continuing...")

		for code in codes:
			href = code.get('href')
			estate_code = href[30:40]
			estate = code.get_text()

			entry = pd.Series(index = header)
			entry['Estate'] = estate
			entry['Code'] = estate_code
			# print(entry)
			estateList = estateList.append(entry, ignore_index = True)

		print(estateList) if DEBUG else {}
		estateList.to_csv("EstateCode.csv", index = False)
