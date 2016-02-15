__author__ = 'arjun010'
import csv,datetime
import numpy
from collections import Counter
from dateutil.parser import parse

class DataProcessor:

    def isfloat(self,x):
        try:
            a = float(x)
        except ValueError:
            return False
        else:
            return True

    def isint(self,x):
        try:
            a = float(x)
            b = int(a)
        except ValueError:
            return False
        else:
            return a == b

    def isDate(self,date_text):
        try:
            parse(date_text)
            return 1
        except ValueError:
            return -1

    def populateDataAtrributeMap(self):
        for dataObj in self.data:
            for attribute in self.dataAtrributeMap.keys():
                curAttributeDataType = ""
                curAttributeVal = dataObj[attribute]
                if self.isint(curAttributeVal)==True or self.isfloat(curAttributeVal)==True:
                    curAttributeVal = float(curAttributeVal)
                    curAttributeDataType = "numeric"
                elif self.isDate(curAttributeVal)==1:
                    curAttributeDataType = "datetime"
                else:
                    curAttributeDataType = "string"

                self.dataAtrributeMap[attribute]['dataType'].append(curAttributeDataType)
                self.dataAtrributeMap[attribute]['domain'].append(curAttributeVal)

        for attribute in self.dataAtrributeMap:

            finalAttributeType = Counter(self.dataAtrributeMap[attribute]['dataType']).most_common(1)[0][0]
            self.dataAtrributeMap[attribute]['domain'] = list(set(self.dataAtrributeMap[attribute]['domain']))
            
            if finalAttributeType=='numeric':
                # if len(self.dataAtrributeMap[attribute]['domain'])<=12:
                #     self.dataAtrributeMap[attribute]['isCategorical'] = "1"
                self.dataAtrributeMap[attribute]['isNumeric'] = "1"
            elif finalAttributeType=='string':
                self.dataAtrributeMap[attribute]['isCategorical'] = "1"
            elif finalAttributeType=='datetime':
                self.dataAtrributeMap[attribute]['isDatetime'] = "1"

            if len(self.dataAtrributeMap[attribute]['domain'])==self.dataRowCount and self.dataAtrributeMap[attribute]['isCategorical']=='1':
                self.dataAtrributeMap[attribute]['isLabel'] = "1"

            self.dataAtrributeMap[attribute].pop('dataType')


    def __init__(self, dataFile,dataFileFormat='csv'):
        self.dataFile = dataFile
        self.dataFileFormat = dataFileFormat
        self.dataAtrributeMap = {}
        self.data = []
        self.dataRowCount = 0

        dataFileObj = open(self.dataFile,'rb')
        reader = csv.reader(dataFileObj)
        dataAttributes = reader.next()

        for attribute in dataAttributes:
            self.dataAtrributeMap[attribute] = {
                'domain':[],
                'dataType':[],
                'isCategorical':"0",
                'isNumeric':"0",
                'isDatetime':"0",
                'isLabel':"0",
                'aliases':[],
                "relatedAttributes":[]
            }

        for line in reader:
            dataObj = {}
            for i in range(0,len(line)):
                dataObj[dataAttributes[i]] = line[i]
            self.data.append(dataObj)
            self.dataRowCount += 1

        print "dataRowCount = " + str(self.dataRowCount)
        self.populateDataAtrributeMap()
        self.updateRelatedAttributes()

    def updateRelatedAttributes(self):
        for attribute1 in self.dataAtrributeMap:
            for attribute2 in self.dataAtrributeMap:
                if attribute1!=attribute2:
                    if self.dataAtrributeMap[attribute1]['isNumeric']=='1' and self.dataAtrributeMap[attribute2]['isNumeric']=='1':
                        attribute1Data = []
                        attribute2Data = []
                        for dataObj in self.data:
                            attribute1Val = float(dataObj[attribute1])
                            attribute2Val = float(dataObj[attribute2])
                            attribute1Data.append(attribute1Val)
                            attribute2Data.append(attribute2Val)

                        corrCoef = numpy.corrcoef(attribute1Data,attribute2Data)[0][1]
                        if corrCoef>0.5 or corrCoef<-0.5:
                            self.dataAtrributeMap[attribute1]['relatedAttributes'].append({
                                    'attribute':attribute2,
                                    'score':corrCoef
                                })
            self.dataAtrributeMap[attribute1]['relatedAttributes'].sort(key = lambda x: abs(x['score']),reverse=True)

    def getDataCols(self):
        return self.dataAtrributeMap.keys()

    def getDataAttributeMap(self):
        return self.dataAtrributeMap

    def getData(self):
        return self.data

    def addAlias(self,attribute,alias):
        self.dataAtrributeMap[attribute]['aliases'].append(alias)

    def addRelatedAttribute(self,attribute,relatedAttributeObject):
        self.dataAtrributeMap[attribute]['relatedAttributes'].append(relatedAttributeObject)

    def setAttributeDataType(self,attribute,dataType):
        self.dataAtrributeMap[attribute][dataType] = "1"