from centadata import Estate
import json
import sys
from pathlib import Path
import csv

json_path = Path("./Estate.json")
if json_path.is_file():	
	with open(json_path, 'r', encoding = 'utf-8') as f:
		estateDictList = json.loads(f.read())
else:
	print("Estate.json does not exist.")

estateList = []
for estate in estateDictList:
	newEstate = Estate()
	newEstate.toObj(estate)
	estateList.append(newEstate)
	newEstate.printObj()

csv_path = Path("./Centadata.csv")
if csv_path.is_file():	
	print("Centadata.csv exists.")
	answer = input("Rewrite?[y/n]")
	if (answer != 'y'):
		exit()

with open(csv_path, 'w') as f:
	w = csv.writer(f)
	w.writerow(['','','','','','',''])
	for estate in estateList:
		w.writerow(estate.inLine())

