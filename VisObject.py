__author__ = 'arjun010'
class VisObject:
    def __init__(self,vizType = '',explicitVizType ='',filters=[],data = [],visAttributes = {},operataions = []):
        self.recommendedType = ''
        self.explicitType = ''
        self.filters = []
        self.data = []
        self.visAttributes = {}
        #self.visAttributes.clear()
        self.operations = []

    def addOperation(self,operation):
        self.operations.append(operation)

    def setRecommendedVisType(self,visType):
        self.recommendedType = visType

    def setExplicitVisType(self,visType):
        self.explicitType = visType

    def setData(self,data):
        self.data = data

    def setFilters(self,filters):
        self.filters = filters

    def addVisAttribute(self,attribute,value):
        self.visAttributes.update({attribute: value})

    def getFormattedVisObject(self):
        return {
            'recommendedType':self.recommendedType,
            'explicitType':self.explicitType,
            'data':self.data,
            'filters':self.filters,
            'visAttributes':self.visAttributes,
            'operations':self.operations
        }