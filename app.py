import os,csv,json
from flask import Flask, render_template, jsonify,request, session, redirect, url_for, _app_ctx_stack
from dataProcessor import DataProcessor
from visGenie import VisGenie
from VisObject import VisObject

import nltk
from nltk.corpus import stopwords
from nltk import word_tokenize,pos_tag, ngrams
from nltk.stem.porter import PorterStemmer
from nltk.corpus import wordnet as wn
from itertools import product
from nltk.tag import StanfordNERTagger
from nltk.util import ngrams
from nltk.corpus import wordnet_ic
import aiml
from fuzzywuzzy import fuzz

global dataAttributeMap
global visGenie

operationWordsMap = {
    'most':{
        'type':'sort',
        'order':'descending'
    },
    'least':{
        'type':'sort',
        'order':'ascending'
    }
}
operationWords = operationWordsMap.keys()
conjunctionWords = ["and", "because", "but", "for", "nor", "so", "until", "when","yet"]

porterStemmerObj = PorterStemmer()

app = Flask(__name__)

def isDataColumn(word,performFuzzyMatch = False):
    global dataAttributeMap
    possibleAttributes = []
    for attribute in dataAttributeMap:
        # if performFuzzyMatch==True:
        #     print word,word.lower(), attribute, attribute.lower(),'==', wordSimilarityScore(word.lower(),attribute.lower())

        if word.lower() in attribute.lower().split(' '):
            if attribute not in possibleAttributes and dataAttributeMap[attribute]['isLabel']=='0':
                possibleAttributes.append(attribute)
        # elif wordSimilarityScore(word.lower(),attribute.lower())>0.8 and performFuzzyMatch==True:
        #     if attribute not in possibleAttributes and dataAttributeMap[attribute]['isLabel']=='0':
        #         possibleAttributes.append(attribute)
        elif fuzz.token_set_ratio(word.lower(),attribute.lower())>=80 and performFuzzyMatch==True:
            if attribute not in possibleAttributes and dataAttributeMap[attribute]['isLabel']=='0':
                possibleAttributes.append(attribute)        
        elif fuzz.token_set_ratio(porterStemmerObj.stem(word.lower()),porterStemmerObj.stem(attribute.lower()))>=80 and performFuzzyMatch==True:
            if attribute not in possibleAttributes and dataAttributeMap[attribute]['isLabel']=='0':
                possibleAttributes.append(attribute)        
        else:
            for attributeAlias in dataAttributeMap[attribute]['aliases']:
                # print attributeAlias
                if word==attributeAlias:
                    if attribute not in possibleAttributes and dataAttributeMap[attribute]['isLabel']=='0':
                        possibleAttributes.append(attribute)
                # elif wordSimilarityScore(word.lower(),attributeAlias.lower())>0.8 and performFuzzyMatch==True:
                #     if attribute not in possibleAttributes and dataAttributeMap[attribute]['isLabel']=='0':
                #         possibleAttributes.append(attribute)
                elif fuzz.token_set_ratio(word.lower(),attributeAlias.lower())>=80 and performFuzzyMatch==True:
                    if attribute not in possibleAttributes and dataAttributeMap[attribute]['isLabel']=='0':
                        possibleAttributes.append(attribute)        
                elif fuzz.token_set_ratio(porterStemmerObj.stem(word.lower()),porterStemmerObj.stem(attributeAlias.lower()))>=80 and performFuzzyMatch==True:
                    if attribute not in possibleAttributes and dataAttributeMap[attribute]['isLabel']=='0':
                        possibleAttributes.append(attribute)

    if len(possibleAttributes)>0:
        return possibleAttributes
    else:
        return -1

@app.route('/parseSentence', methods=['POST'])
def parseSentence():
    global visGenie

    sentence = request.form['sentence']
    stopwordsList = stopwords.words('english')
    # print stopwordsList
    for stopword in stopwordsList:
        if isDataColumn(stopword)!=-1 or (stopword.lower() in operationWords) or (stopword.lower() in conjunctionWords):
            stopwordsList.remove(stopword)

    tokenized_sentence = word_tokenize(sentence)    

    # print tokenized_sentence

    for word in tokenized_sentence:
        if word.lower() in stopwordsList:
            tokenized_sentence.remove(word)

    # print tokenized_sentence    

    dataAttributes = []
    operation = {}

    for word in tokenized_sentence:
        # print word
        # word = porterStemmerObj.stem(word)
        # print word
        dataCols = isDataColumn(word,True)
        if word.lower() in operationWords:
            operation = operationWordsMap[word]
        if dataCols!=-1:
            for dataCol in dataCols:
                if dataCol not in dataAttributes:
                    dataAttributes.append(dataCol)

    # pos_list = nltk.pos_tag(tokenized_sentence)
    # print pos_list
    print dataAttributes
    print operation

    visObject = visGenie.getVisObject(dataAttributes,operation=operation)
    
    if len(visObject)>0:
        visObject = visObject[0]
    else:
        visObject = VisObject().getFormattedVisObject()

    botResponse = ''
    if len(visObject['data'])==0:
        botResponse = "Sorry I can't draw a chart for that yet."
        print tokenized_sentence
    else:
        if visObject['explicitType']=='':
            chartType = visObject['recommendedType']
        else:
            chartType = visObject['explicitType']

        attributeStringList = []
        for attribute in visObject['visAttributes']:
            attributeStringList.append(visObject['visAttributes'][attribute])

        attributeString = ' and '.join(attributeStringList)

        botResponse = "Here's a " + chartType + " showing " + attributeString

    return jsonify({
        'response':botResponse,
        'visObject':visObject
    })

@app.route('/getRelatedAttributes', methods=['POST'])
def getRelatesAttributes():
    global dataAttributeMap
    attribute = request.form['attribute']
    if dataAttributeMap.get(attribute)==None:
        return jsonify({
            'relatedAttributes':[]
        })
    else:
        return jsonify({
            'relatedAttributes':dataAttributeMap[attribute]['relatedAttributes']
        })

@app.route('/getVisualizationObject', methods=['POST'])
def getVisualizationObjectForAttributes():
    global visGenie
    dataAttributes = request.form.getlist('attributes[]')
    print dataAttributes
    visObject = visGenie.getVisObject(dataAttributes)[0]
    if len(visObject['visAttributes'])==1:
        visDescription = visObject['visAttributes']['xAttribute']
    elif len(visObject['visAttributes'])==2:
        visDescription = visObject['visAttributes']['xAttribute'] + " vs " + visObject['visAttributes']['yAttribute']
    return jsonify({
            'visObject':visObject,
            'visDescription':visDescription
        })


@app.route('/initializeData', methods=['POST'])
def initializeData():
    global dataAttributeMap
    global visGenie

    dataFile = 'static/data/'+request.form['dataFileName']

    dataProcessorObj = DataProcessor(dataFile)
    dataAttributeMap = dataProcessorObj.getDataAttributeMap()
    
    aliasFile = 'static/knowledgebase/aliases.json'
    with open(aliasFile, "r") as jsonFile:
        aliasKnowledgeMap = json.load(jsonFile)

    for dataFileLabel in aliasKnowledgeMap:
        if dataFileLabel==request.form['dataFileName']:
            for attribute in aliasKnowledgeMap[dataFileLabel]:
                for alias in aliasKnowledgeMap[dataFileLabel][attribute]:
                    dataProcessorObj.addAlias(attribute,alias)

    if request.form['dataFileName']=='cars_2004.csv':
        dataProcessorObj.setAttributeDataType('Name','isLabel')
    elif request.form['dataFileName']=='nutrition.csv':
        dataProcessorObj.setAttributeDataType('NDB_No','isLabel')

    visGenie = VisGenie(dataAttributeMap,dataProcessorObj.getData())

    return jsonify({'status':'data initialization was successful!','dataAttributes':dataAttributeMap.keys()})

@app.route('/')
def indexMain():
    return render_template('index.html')

if __name__ == "__main__":
    global dataAttributeMap
    app.run(debug=True,threaded=True,port=5000)