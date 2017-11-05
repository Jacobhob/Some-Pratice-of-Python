'''
Description: This is a web crawler for PE fund data in https://www.touzi.com/simu/
Time:10/29/2017
Author: Lu Yuqiao
'''

import bs4
import requests
import sys
import numpy as np
import pandas as pd
from pathlib import Path

def getURL(count):
    url = "https://www.touzi.com/simu/productlist-pn" + str(count) + ".html"
    return url

def setupSession():
	session = requests.Session()
	session.header = { 
                    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
            	    'Accept-Encoding': "gzip, deflate, br",
                    'Host': "www.touzi.com",
                    'Referer': "https://www.touzi.com/simu/productlist-pn1.html",
            	    'Connection': "keep-alive"
                    }
	return session

def standardize(s):
    temp = str(s)
    temp = temp.replace(' ','')
    temp = temp.replace('\n','')
    temp = temp.replace('\t','')
# Reset missing value to other notation here. 
    if temp in ["--",""]:
        temp = "N/A"
# Reset string type to float type here. 

    return temp

class PEFund:
    fundCount = 0

    def __init__(self, fund_id):
        PEFund.fundCount += 1

        self.fund_id = fund_id
        self.fund_short_name = ""
        self.strategy = ""
        self.fund_manager = ""
        self.company_short_name = ""
        self.inception_date = ""
        self.ret_1m = ""
        self.ret_1y_a = ""
        self.nav = ""
        self.ret_incep = ""

    def displayCount(self):
        print("***%d PE funds in total.***" % PEFund.fundCount)

    def fundStandardize(self):
        self.fund_short_name = standardize(self.fund_short_name)
        self.strategy = standardize(self.strategy)
        self.fund_manager = standardize(self.fund_manager)
        self.company_short_name = standardize(self.company_short_name)
        self.inception_date = standardize(self.inception_date)
        self.ret_1m = standardize(self.ret_1m)
        self.ret_1y_a = standardize(self.ret_1y_a)
        self.nav = standardize(self.nav)
        self.ret_incep = standardize(self.ret_incep)


if __name__ == "__main__":

    pageCount = 1908
    counter = 0

    # Set up requests session header, retrieve and decode data from server.
    urlList1 = [getURL(i) for i in range(1, 11)]
    urlList2 = [getURL(i) for i in range(11, 21)]
    urlList3 = [getURL(i) for i in range(1001, 1501)]
    urlList4 = [getURL(i) for i in range(1501, pageCount + 1)]
    urlListTotal = [urlList1, urlList2, urlList3, urlList4]

    session = setupSession()

    # Store funds information in fundList.
    fundList = []

    for urlList in urlListTotal:
        for url in urlList:
            counter += 1
            try:
                entryCount = 0

                response = session.get(url = url, timeout = 5)
                soup = bs4.BeautifulSoup(response.content, 'lxml', from_encoding='utf-8')

                table = soup.find_all('tr')
                for row in table:
                    entries = row.find_all('td')
                    #print(len(entries))
                    if len(entries) != 0:
                        entryCount += 1

                        fund = PEFund(int(entries[0].string))
                        fund.fund_short_name = str(entries[1].string)
                        fund.strategy = str(entries[2].string)
                        fund.fund_manager = str(entries[3].string)
                        fund.company_short_name = str(entries[4].string)
                        fund.inception_date = str(entries[5].string)
                        fund.ret_1m = str(entries[6].string)
                        fund.ret_1y_a = str(entries[7].string)
                        fund.nav = str(entries[8].string)
                        fund.ret_incep = str(entries[9].string)

                        fund.fundStandardize()
                        fundList.append(fund)

                print("Page " + str(counter) + " completed.")
                print("%d funds added!" % entryCount)
            
            except:
                print("Error: cannot fetch data with pagecount " + str(counter))

        try:
            fundList[len(fundList)-1].displayCount()
        except:
            print("Error: There is no fund information.")
            exit()

        # Reorganize fund information by DataFrame.
        dfInit = {
                'fund_id': [],
                'fund_short_name': [],
                'strategy': [],
                'fund_manager': [],
                'company_short_name': [],
                'inception_date': [],
                'ret_1m': [],
                'ret_1y_a': [],
                'nav': [],
                'ret_incep': [],
                }
        rawData = pd.DataFrame(dfInit, columns = ['fund_id', 'fund_short_name', 'strategy', 'fund_manager', 'company_short_name', 'inception_date', 'ret_1m', 'ret_1y_a', 'nav','ret_incep'])

        for fund in fundList:
            fundDescribe = {'fund_id': fund.fund_id,
                            'fund_short_name': fund.fund_short_name,
                            'strategy': fund.strategy,
                            'fund_manager': fund.fund_manager,
                            'company_short_name': fund.company_short_name,
                            'inception_date': fund.inception_date,
                            'ret_1m': fund.ret_1m,
                            'ret_1y_a': fund.ret_1y_a,
                            'nav': fund.nav,
                            'ret_incep': fund.ret_incep
                            }
            #print('fundDescribe',fundDescribe)
            rawData = rawData.append(fundDescribe, ignore_index = True)        

        newList =[]
        fundList = newList

        #print('rawdata',rawData)
        
        # Write fund information to csv.
        try:
            if len(sys.argv) == 1:
                fileName = "Touzi.csv" 
                path = Path("./"+fileName)

                if path.is_file():
                    rawData.to_csv(fileName, mode = 'a', header = False)

                else:
                    rawData.to_csv(fileName)

                print("Sucessfully write to file", fileName)

            else:
                fileName = argv[1]
                path = Path("./"+fileName)

                if path.is_file():
                    rawData.to_csv(fileName, mode = 'a', header = False)

                else:
                    rawData.to_csv(fileName)

                print("Sucessfully write to file", fileName)

        except:
            print("Error: Cannot write to file.")
            exit()

