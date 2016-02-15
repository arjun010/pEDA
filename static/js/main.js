/**
 * Created by arjun010 on 12/13/15.
 */
(function(){

    main = {};

    $body = $("body");
    $(document).on({
        ajaxStart: function() { $body.addClass("loading");    },
        ajaxStop: function() { $body.removeClass("loading"); }
    });


    main.init = function(){
        selectDataFile();        
    }

    $("#datasetpicker").change(function(ev){
        selectDataFile();        
    })

    function selectDataFile(){
        var dataFileName = $("#datasetpicker").val();
        // console.log(dataFileName)
        $.post( "/initializeData", { dataFileName: dataFileName })
            .done(function(response) {
                    console.log(response);
                    populateDataAttributeList(response['dataAttributes']);
            });
    }

    function populateDataAttributeList(dataAttributes){
        $('.dataattributesdropdown').find('option').remove().end();
        $(".dataattributesdropdown").append($("<option></option>").val('').html(''));
        for(var i in dataAttributes){
            var dataAttribute = dataAttributes[i];
            $(".dataattributesdropdown").append($("<option></option>").val(dataAttribute).html(dataAttribute));
        }
    }

    $(".dataattributesdropdown").change(function(ev){
        var attr1 = $("#x-axis-attribute").val();
        var attr2 = $("#y-axis-attribute").val();
        var attributes = [];
        var relatedAttributeObjects = [];    
        if(attr1!=''){
            attributes.push(attr1);
        }
        if(attr2!=''){
            attributes.push(attr2);            
        }
        updateRelatedAttributeObjects(attributes);
        
        $.post( "/getVisualizationObject", { "attributes": attributes })
            .done(function(response) {
                var visObject = response.visObject;
                var visDescription = response.visDescription;
                var visSelector = "#vis";
                // console.log(relatedAttributeObjects);
                populateRelatedAttributesDiv(global.relatedAttributeObjects);
                
                d3.selectAll(visSelector).selectAll('svg').remove();
                $("#visDescription").text(visDescription);
                drawVis(visObject,visSelector);
            });
    });

    $("#askQueryButton").click(function(ev){
        processUserQuery();
    });

    function processUserQuery(){
        var query = $("#queryBox").val();
        $.post( "/parseSentence", { sentence: query })
            .done(function( response ) {
                var visObject = response['visObject'];
                var botReply = response['response'];
                // $("#botresponsediv").text(botReply);                

                var visSelector = "#vis";
                var xAttr = visObject.visAttributes.xAttribute==undefined?'':visObject.visAttributes.xAttribute;
                var yAttr = visObject.visAttributes.yAttribute==undefined?'':visObject.visAttributes.yAttribute;

                var visDescription;
                if(xAttr!='' && yAttr!=''){
                    visDescription = xAttr + " vs " + yAttr;
                }else if(xAttr!=''){
                    visDescription = xAttr;
                }else if(yAttr!=''){
                    visDescription = yAttr;
                }
                $("#visDescription").text(visDescription);

                $("#x-axis-attribute").val(xAttr);
                $("#y-axis-attribute").val(yAttr);
                var attributes = [xAttr,yAttr];
                updateRelatedAttributeObjects(attributes);
                setTimeout(function(){
                    populateRelatedAttributesDiv(global.relatedAttributeObjects);
                },500)
                
                d3.selectAll(visSelector).selectAll('svg').remove();
                drawVis(visObject,visSelector);
            });
    }

    function updateRelatedAttributeObjects(attributeList){
        global.relatedAttributeObjects = [];
        for(var attrIndx in attributeList){
            var curAttribute = attributeList[attrIndx];
            $.post( "/getRelatedAttributes", { "attribute": curAttribute })
                .done(function(response) {
                    var relAttributeObjs = response.relatedAttributes;
                    for(var i in relAttributeObjs){
                        var attrObj = relAttributeObjs[i];
                        if(attrObj!={} && i<2){
                            if(global.relatedAttributeObjects.indexOf(attrObj)==-1 && attrObj.attribute!=curAttribute){ // if attr not in relatedAttributes
                                global.relatedAttributeObjects.push(attrObj);
                            }
                        }else{
                            break;
                        }
                    }                    
                });
        }
    }

    function drawVis(visObject,selector){
      var chartType = visObject['explicitType']=='' ? visObject['recommendedType'] : visObject['explicitType'];
      var width = 750, height = 600;
      if(chartType=='scatterplot'){
        var labels = {
            "xAttr":visObject.visAttributes.xAttribute,
            "yAttr":visObject.visAttributes.yAttribute
        };
        var data = visObject.data;
        visRenderer.drawScatterplot(data,labels,selector,width,height);
      }else if(chartType=='barchart'){
        var labels = {
            "xAttr":visObject.visAttributes.xAttribute,
            "yAttr":visObject.visAttributes.yAttribute
        };
        var data = visObject.data;
        visRenderer.drawVerticalBarChart(data,labels,selector,width,height);
      }else if(chartType=='histogram'){
        var labels = {
            "xAttr":visObject.visAttributes.xAttribute,
            "yAttr":visObject.visAttributes.yAttribute
        };
        var values = visObject.data;
        visRenderer.drawHistogram(values,labels,selector,width,height);
      }
    }

    function populateRelatedAttributesDiv(relatedAttributeObjects){
        $("#attributeSuggestionDiv").html('');
        if(relatedAttributeObjects.length==0){
            $("#attributeSuggestionDiv").html(global.defaultRelatedAttributesStatus);
        }else{
            for(var i in relatedAttributeObjects){
                var relAttributeObj = relatedAttributeObjects[i];
                $("#attributeSuggestionDiv").append("<p>"+relAttributeObj.attribute+"</p>")  
            }
        }
    }

})();