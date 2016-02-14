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
        // selectDataFile();
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
        $('#dataattributesdropdown').find('option').remove().end();
        for(var i in dataAttributes){
            var dataAttribute = dataAttributes[i];
            $("#dataattributesdropdown").append($("<option></option>").val(dataAttribute).html(dataAttribute));
        }        
    }

})();