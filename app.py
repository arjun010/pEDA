import os,csv,json
from flask import Flask, render_template, jsonify,request, session, redirect, url_for, _app_ctx_stack

global dataAttributeMap
global visGenie

app = Flask(__name__)

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