__author__ = 'arjun010'
from VisObject import VisObject
import math, itertools


def sortByKey(data,attribute,order='a'):
    shouldReverse = False
    if order=='d':
        shouldReverse = True

    data.sort(key=lambda x: x[attribute], reverse=shouldReverse)

class VisGenie:
    def __init__(self, dataAttributeMap,data):
        self.dataAttributeMap = dataAttributeMap
        self.data = data

    def getVisObjectList(self,attributeList,operation):
        possibleVisObjects = []
        for i in range(1,3):
            combinations = itertools.combinations(attributeList,i)
            for combination in combinations:
                print list(combination)

    def getVisObject(self,attributeList,filters=[],explicitVisType = '',operation = {}):
        visObjectList = []

        if len(attributeList)==1: # distribution of single attribute
            attribute = attributeList[0]
            if self.dataAttributeMap[attribute]['isNumeric']=="1":
                curVisObject = VisObject()
                curVisObject.setRecommendedVisType('histogram')

                curVisObject.addVisAttribute('xAttribute',attribute)

                dataList = self.getValuesList(attribute)
                curVisObject.setData(dataList)
                visObjectList.append(curVisObject.getFormattedVisObject())

            else:
                curVisObject = VisObject()
                curVisObject.setRecommendedVisType('barchart')

                curVisObject.addVisAttribute('xAttribute',attribute)
                curVisObject.addVisAttribute('yAttribute','COUNT')

                dataList = self.getCountList(attribute)
                self.applyDataTransform(dataList,operation)
                curVisObject.setData(dataList)
                visObjectList.append(curVisObject.getFormattedVisObject())

        elif len(attributeList)==2: # simple X-Y axes charts
            xAttr = ''
            yAttr = ''
            if self.dataAttributeMap[attributeList[0]]['isCategorical']=='1' and self.dataAttributeMap[attributeList[1]]['isNumeric']=='1':
                xAttr = attributeList[0]
                yAttr = attributeList[1]

                curVisObject = VisObject()
                
                curVisObject.addVisAttribute('xAttribute',xAttr)
                curVisObject.addVisAttribute('yAttribute','SUM('+yAttr+')')

                dataList = self.getSumList(xAttr,yAttr)
                self.applyDataTransform(dataList,operation)
                curVisObject.setData(dataList)

                curVisObject.setRecommendedVisType('barchart')
                visObjectList.append(curVisObject.getFormattedVisObject())

            elif self.dataAttributeMap[attributeList[1]]['isCategorical']=='1' and self.dataAttributeMap[attributeList[0]]['isNumeric']=='1':
                xAttr = attributeList[1]
                yAttr = attributeList[0]

                curVisObject = VisObject()
                curVisObject.addVisAttribute('xAttribute',xAttr)
                curVisObject.addVisAttribute('yAttribute','SUM('+yAttr+')')

                dataList = self.getSumList(xAttr,yAttr)
                self.applyDataTransform(dataList,operation)
                curVisObject.setData(dataList)

                curVisObject.setRecommendedVisType('barchart')
                visObjectList.append(curVisObject.getFormattedVisObject())

            elif self.dataAttributeMap[attributeList[0]]['isNumeric']=='1' and self.dataAttributeMap[attributeList[1]]['isNumeric']=='1':
                xAttr = attributeList[0]
                yAttr = attributeList[1]

                curVisObject = VisObject()
                curVisObject.addVisAttribute('xAttribute',xAttr)
                curVisObject.addVisAttribute('yAttribute',yAttr)

                dataList = self.getXYValueList(xAttr,yAttr)
                curVisObject.setData(dataList)

                curVisObject.setRecommendedVisType('scatterplot')                
                visObjectList.append(curVisObject.getFormattedVisObject())

        elif len(attributeList)==3: # X-Y axes charts with coloring variable
            xAttr = ''
            yAttr = ''
            coloringAttr = ''
            for attribute in attributeList:
                if self.dataAttributeMap[attribute]['isNumeric']=="1":
                    if xAttr=='':
                        xAttr = attribute
                    elif yAttr=='':
                        yAttr = attribute
                elif self.dataAttributeMap[attribute]['isCategorical']=="1":
                    if coloringAttr=='':
                        coloringAttr = attribute

            if coloringAttr!='' and xAttr!='' and yAttr!='':
                curVisObject = VisObject()
                curVisObject.addVisAttribute('xAttribute',xAttr)
                curVisObject.addVisAttribute('yAttribute',yAttr)
                curVisObject.addVisAttribute('colorAttribute',coloringAttr)

                dataList = self.getXYValueList(xAttr,yAttr,coloringAttr)
                curVisObject.setData(dataList)

                curVisObject.setRecommendedVisType('scatterplot')
                visObjectList.append(curVisObject.getFormattedVisObject())

        return visObjectList

    def applyDataTransform(self,data,operation):
        if operation!={}:
            if operation['type']=='sort':
                order = operation['order'][0]
                sortByKey(data,'value',order)
            elif operation['type']=='average':
                attribute = operation['dataAttribute']
                for dataObj in data:
                    value = data['label']
                    curValue = data['value']
                    data['value'] = curValue/getOccuranceCount(value,attribute)

    def getValuesList(self,attribute):
        dataList = []
        for dataItem in self.data:
            if math.isnan(float(dataItem[attribute])):
                attributeValue = float(0)
            else:
                attributeValue = float(dataItem[attribute])
            dataList.append(attributeValue)

        return dataList

    
    def getOccuranceCount(self,value,attribute):
        count = 0
        for dataItem in self.data:
            attributeValue = dataItem[attribute]
            if attributeValue == value:
                count+=1
        return count

    def getCountList(self,attribute,category=''):
        attributeCountMap = {}
        attributeCountList = []
        for dataItem in self.data:
            attributeValue = dataItem[attribute]
            if attributeCountMap.get(attributeValue)==None:
                attributeCountMap[attributeValue] = 1
            else:
                attributeCountMap[attributeValue] += 1

        for attribute in attributeCountMap:
            attributeCountList.append({'label':attribute,'value':attributeCountMap[attribute],'category':category})
        return attributeCountList

    def getSumList(self,keyAttribute,valueAttribute,category=''):
        attributeSumMap = {}
        attributeSumList = []
        for dataItem in self.data:
            keyAttributeValue = dataItem[keyAttribute]
            valueAttributeVal = float(dataItem[valueAttribute])
            if attributeSumMap.get(keyAttributeValue)==None:
                attributeSumMap[keyAttributeValue] = valueAttributeVal
            else:
                attributeSumMap[keyAttributeValue] += valueAttributeVal

        for attribute in attributeSumMap:
            attributeSumList.append({'label':attribute,'value':attributeSumMap[attribute],'category':category})

        return attributeSumList

    def getXYValueList(self,xAttr,yAttr,categoryAttr=''):
        transformedData = []
        labelAttribute = ''
        for attribute in self.dataAttributeMap:
            if self.dataAttributeMap[attribute]['isLabel']=="1":
                labelAttribute = attribute
        for dataItem in self.data:
            xAttrValue = float(dataItem[xAttr])
            yAttrValue = float(dataItem[yAttr])
            if labelAttribute=='':
                labelValue = ''
            else:
                labelValue = dataItem[labelAttribute]

            if categoryAttr!='':
                categoryAttrVal = dataItem[categoryAttr]
            else:
                categoryAttrVal = ''

            transformedData.append({'xVal':xAttrValue,'yVal':yAttrValue,'label':labelValue,'category':categoryAttrVal})

        return transformedData