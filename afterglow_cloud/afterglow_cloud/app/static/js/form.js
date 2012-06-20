var configCount = 0;

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
    
    $('#xColourButton').click(function () {
        addColour();
        
        return false;
    });
    
    $('#xThresholdButton').click(function () {
        addThreshold();
        
        return false;
    });
    
    $('#renderMainForm').submit(function () {
        
        populateProperty();    
    
        //return false;
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
    
    var elem = document.createElement("div");
    
    var elemID = configCount++;
    
    elem.id = "line" + elemID;
    
    elem.innerHTML = "Colour :: " +  $("#xColourType").attr("value") + " | " + $("#xColourHEX").attr("value") + " | " + $("#xColourCondition").attr("value"); 
    
    document.getElementById("alreadyAdded").appendChild(elem);
    
    elem = document.createElement("div");
    elem.id = "configLine" + elemID;
    
    var conf = "color." + $("#xColourType").attr("value").toLowerCase() + "=\"" + $("#xColourHEX").attr("value") + "\"";    
    
    if ($("#xColourCondition").attr("value")){ // not empty -- condition
        conf += " if (" + $("#xColourCondition").attr("value") + ");";
    }
    
    elem.innerHTML = conf;
    
    document.getElementById("alreadyAddedHidden").appendChild(elem);
}

function addThreshold(){
    
    var elem = document.createElement("div");
    
    var elemID = configCount++;
    
    elem.id = "line" + elemID;
    
    elem.innerHTML = "Threshold :: " + $("#xThresholdType").attr("value") + " | " + $("#xThresholdSize").attr("value");
    
    document.getElementById("alreadyAdded").appendChild(elem);
    
    elem = document.createElement("div");
    elem.id = "configLine" + elemID;
    
    elem.innerHTML = "threshold." + $("#xThresholdType").attr("value").toLowerCase() + "=" + $("#xThresholdSize").attr("value");

    document.getElementById("alreadyAddedHidden").appendChild(elem);
}

function populateProperty(){

    var value = "";
    
    for (var i = 0; i < configCount; i++){
        value += document.getElementById("configLine" + i).innerHTML + "\n"; 
    }
    
    document.getElementById("id_propertyConfig").value = value;

    //alert(value);
}