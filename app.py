import os,csv,json
from flask import Flask, render_template, jsonify,request, session, redirect, url_for, _app_ctx_stack
from dataProcessor import DataProcessor
from visGenie import VisGenie
from VisObject import VisObject

global dataAttributeMap
global visGenie

app = Flask(__name__)

@app.route('/getRelatedAttributes', methods=['POST'])
def getRelatesAttributes():
    global dataAttributeMap
    attribute = request.form['attribute']
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