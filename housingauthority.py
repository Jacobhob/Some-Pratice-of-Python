import bs4
import requests
import sys
import numpy as np
import pandas as pd
from pathlib import Path
import traceback


TYPE = 2
DEBUG = True
id_type1 = list([2750,2730,11890,2762,2824,2814,2816,2815,15160,2817,15060,2734,2776,2818,8327,2720,11929,2794,2717,11993,2721,2716,10123,2777,2713,2715,2875,2867,2763,2754,2739,2714,2740,2731,2841,2735,2722,2852,15080,4267,2764,4264,2864,2853,2790,2842,2845,2843,3189,2706,3030,7005,15200,2825,2783,15101,2782,2779,4265,2732,2766,6762,2781,2826,2828,2821,12621,2829,2819,2741,2780,2865,2820,2755,2757,2827,11034,2866,2756,2742,2743,8553,2758,2802,2862,2733,2727,2807,2796,2707,2857,2751,2833,2858,8329,2719,2771,2760,2761,2788,15000,2834,2850,6763,2724,2813,3190,2798,2806,2772,2805,7067,2859,2723,2800,11103,2860,2737,12787,2767,2808,2809,11201,8224,2736,2810,2812,2770,12624,15180,2702,2791,2801,2792,2851,15280,2861,2856,3191,2738,2778,2747,2811,2748,15120,2793,2693,10063,3187,2729,2769,2697,2696,2695,2694,2752,7070,2698,2699,2700,2701,2822,2765,2795,2787,2847,2708,2703,2705,2704,2712,2711,15020,2759,2744,2745,2753,2823,2774,2775,2746,3188,2709,15100,2854,2785,2718,2728,2710,2725,12644,2838,7178,6764,2726,2789,15102,2855,2836,2837,2784,3122])
id_type2 = list([3050,3148,3109,3110,3077,3021,3035,3149,3119,3131,3022,3051,3176,3178,3180,3105,3120,3171,3114,3083,3084,3038,3113,3151,3025,3052,3036,3026,3150,3154,3135,3028,3133,3134,3106,3139,3140,3079,3121,3012,3147,3013,3014,3015,3016,3017,3018,3108,3057,3115,3011,10069,3141,3145,3181,3005,3107,3184,3138,3146,3143,3053,3193,3006,3007,3054,3068,3164,2998,3130,3103,3097,3073,3123,3074,3045,3125,3008,3065,3124,3064,3075,3192,3063,3067,3059,3060,3095,3009,3069,3072,3032,3033,3049,3034,3196,3029,3104,3043,3128,3066,3194,3195,3155,3156,10036,3159,3163,3085,3129,3117,3098,3102,3118,3086,11276,3076,3100,3010,3099,3167,3096,3087,2997,3058,3101,3116])
header_type1 = [
		"Name",
		"ID",
		"屋邨類別",
		"入伙年份",
		"樓宇類型",
		"樓宇座數",
		"樓宇名稱",
		"租住單位數目",
		"單位面積 (平方米)",
		"住戶數目",
		"認可人口",
		"屋邨管理諮詢委員會",
		"分區租約事務管理辦事處/屋邨辦事處",
		"屋邨物業管理",
		"停車場管理",
		"屋邨網站",
		"更多資料"
]
header_type2 = [
		"Name",
		"ID",
		"出售期數",
		"落成年份",
		"樓宇類型",
		"樓宇座數",
		"樓宇名稱",
		"單位數目",
		"單位建築面積 (平方米)",
		"單位實用面積 (平方米)",
		"首次推出售價 ($)",
		"業主立案法團",
		"區域物業管理辦事處 / 分區租約事務",
		"屋苑物業管理",
		"停車場管理",
		"屋苑網站",
		"更多資料"
		]
if TYPE == 1:
	header = header_type1
	id = id_type1
elif TYPE == 2:
	header = header_type2
	id = id_type2

# Function to set up request URL.
def getURL(type, id):
	url = "https://www.housingauthority.gov.hk/tc/global-elements/estate-locator/detail.html?propertyType=" + str(type) + "&id=" + str(id)
	return url

# Function to setup request header.
def setupSession():
	session = requests.Session()
	session.header = {
					'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
					'Accept-Encoding': "gzip, deflate",
					'Host': "www.housingauthority.gov.hk",
					'Connection': "keep-alive"
	}
	return session

# Function to standardize data type.
def standardize(s):
	temp = str(s)    # Set parameer to str type
	temp = temp.replace(' ','')     # Remove space
	temp = temp.replace('\r\n','')  # Remove newline
	temp = temp.replace('\n','')    # Remove newline
	temp = temp.replace('\t','')    # Remove tab

	# Reset missing value to other notation here.
	if temp in ["-","","暫時未能提供有關數字"]:
		temp = "N/A"    # Standardize missing value to "N/A"

	return temp


if __name__ == "__main__":

	counter = 0

	# Set up requests session header, retrieve and decode data from server.
	urlList = [getURL(TYPE, i) for i in id]

	session = setupSession()

	# Store estate information in estateList.
	estateList = pd.DataFrame(data = None, columns = header)

	# Web Crawling
	for url in urlList:
		counter += 1
		try:
			response = session.get(url = url, timeout = 10)
			soup = bs4.BeautifulSoup(response.content, 'lxml', from_encoding='utf-8')    # Decoding: UTF-8

			entryList = []
			# Find estate name
			name = soup.find('div', id = 'mainHeading', class_ = 'hd1')
			estate_name = standardize(name.string)
			print(repr(name.string)) if DEBUG else {}
			entryList.append(estate_name)
			entryList.append(id[counter-1])

			# Find table in html
			table = soup.find_all('tr')

			entry_counter = 0
			for entry in table:
				entry_counter += 1
				if entry_counter > 15:
					break

				i = 0
				strList = []
				for children in entry.children:
					i += 1
					content = children.strings if i == 4 else {}
					for txt in content:
						strList.append(standardize(txt))
				if (len(strList) == 0):
					strList.append("N/A")

				ety = strList[0]
				for s in range(2, len(strList)+1, 1):
					ety = ety + "," + str(strList[s-1])
				entryList.append(ety)

			entryList = pd.Series(entryList, index = header)
			print(entryList) if DEBUG else {}

		except Exception as e:
			print("Error: cannot fetch data with url: " + str(url))
			answer = input("End Crawler?[y/n] ")
			if answer == 'y':
				traceback.print_exc()
				print("Exiting...")
				exit()
			else:
				print("Continuing...")

		estateList = estateList.append(entryList, ignore_index = True)
	#print(estateList) if DEBUG else {}
	estateList.to_csv("HOS.csv", sep = ' ', header = True, index = False)

