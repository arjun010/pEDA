import json, os,csv
with open('aliases.json') as data_file:    
    aliasMap = json.load(data_file)


dataDir = '../data/'

print aliasMap.keys()
for fileName in os.listdir(dataDir):
	if fileName not in aliasMap:
		aliasMap[fileName] = {}

		reader = csv.reader(open(dataDir+fileName,'rb'))
		attributes = reader.next()
		for attribute in attributes:
			aliasMap[fileName][attribute] = []


print aliasMap.keys()
with open('aliases.json', 'w') as outfile:
    json.dump(aliasMap, outfile,indent=1)