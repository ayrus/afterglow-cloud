$(document).ready(function(){

    $('#id_textLabel').miniColors();
    
    $('#xColourHEX').miniColors();

    $("#id_overrideEdge").click(function () { 
        toggleShowOverrideInput();
    });
    
    $("#settingsLabel").click(function () { 
        toggleShowMainSettings();
    });
    
    $('#advancedLabel').click(function () {
        toggleShowAdvanced();
    });
    
});

function toggleShowOverrideInput(){

     if($('#id_overrideEdge').attr('checked')){
        $('#id_overrideEdgeLength').show();
     }else{
        $('#id_overrideEdgeLength').hide();
     }
}

function toggleShowMainSettings(){
    $('#mainSettings').slideToggle(('slow'));   
}

function toggleShowAdvanced(){
    $('#advanced').slideToggle(('slow'));
}

function addColour(){
    
}