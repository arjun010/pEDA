$("#leftPanelToggleButton").click(function(ev){
	toggleLeftPanel();
});

$("#rightPanelToggleButton").click(function(ev){
	toggleRightPanel();
});


function toggleLeftPanel(){
	if(global.leftPanelStatus==1){ // left panel open
    	$("#leftPanel").removeClass('show');
    	$("#leftPanel").addClass('hide');
				
		$("#leftPanelToggleButton").removeClass('glyphicon-remove-circle');
		$("#leftPanelToggleButton").addClass('glyphicon-menu-hamburger');
		global.leftPanelStatus = 0;
	}else{ // left panel closed
		$("#leftPanel").removeClass('hide');
    	$("#leftPanel").addClass('show');
		
		$("#leftPanelToggleButton").removeClass('glyphicon-menu-hamburger');
		$("#leftPanelToggleButton").addClass('glyphicon-remove-circle');
		global.leftPanelStatus = 1;
	}
	resizeMainContainer();
}

function toggleRightPanel(){
	if(global.rightPanelStatus==1){ // right panel open
    	$("#assistantContainer").removeClass('show');
    	$("#assistantContainer").addClass('hide');
		
		$("#rightPanelToggleButton").removeClass('glyphicon-remove-circle');
		$("#rightPanelToggleButton").addClass('glyphicon-lamp');
		global.rightPanelStatus = 0;
	}else{ // right panel closed
		$("#assistantContainer").removeClass('hide');
    	$("#assistantContainer").addClass('show');
				
		$("#rightPanelToggleButton").removeClass('glyphicon-lamp');
		$("#rightPanelToggleButton").addClass('glyphicon-remove-circle');
		global.rightPanelStatus = 1;
	}	
	resizeMainContainer();
}

function resizeMainContainer(){
	$("#mainContainer").removeClass();
	if(global.rightPanelStatus==1 && global.leftPanelStatus==1){
		$("#mainContainer").addClass('col-md-6');
	}else if(global.rightPanelStatus==0 && global.leftPanelStatus==0){
		$("#mainContainer").addClass('col-md-12');
	}else{
		$("#mainContainer").addClass('col-md-9');
	}
}