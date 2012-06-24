var configCount = 0;
var maxNodeSizeSet = false;

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
    
    $('#configLabel').click(function () {
        toggleShowConfig();
    });
    
    $('#xColourButton').click(function () {
        addColour();
        
        return false;
    });
    
    $('#xThresholdButton').click(function () {
        addThreshold();
        
        return false;
    });
    
    $('#xCustomButton').click(function () {
    
        addCustom();
        
        return false;
    });    
    
    $('#xClusteringButton').click(function (){
    
        addClustering();
        
        return false;
    });
    
    $('#xSizeButton').click(function (){
    
        addSize();
        
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

function toggleShowConfig(){
    $('#config').slideToggle(('slow'));
}

function appendUserConfigDiv(id, html){

    var elem = document.createElement("div");
    
    elem.id = "line" + id;
    
    elem.innerHTML = html;

    document.getElementById("alreadyAdded").appendChild(elem);
}

function appendHiddenConfigDiv(id, html){

    var elem = document.createElement("div");
    
    elem.id = "configLine" + id;
    
    elem.innerHTML = html;

    document.getElementById("alreadyAddedHidden").appendChild(elem);
}

function addColour(){
    
    var elemID = configCount++;
    
    var html = "Colour :: " +  $("#xColourType").attr("value") + " | " + $("#xColourHEX").attr("value") + " | " + $("#xColourCondition").attr("value"); 
    
    appendUserConfigDiv(elemID, html);
    
    html = "color." + $("#xColourType").attr("value").toLowerCase() + "=\"" + $("#xColourHEX").attr("value") + "\"";    
    
    if ($("#xColourCondition").attr("value")){ // not empty -- condition
        html += " if (" + $("#xColourCondition").attr("value") + ");";
    }
    
    appendHiddenConfigDiv(elemID, html);
}

function addThreshold(){
    
    var elemID = configCount++;
    
    var html = "Threshold :: " + $("#xThresholdType").attr("value") + " | " + $("#xThresholdSize").attr("value");
    
    appendUserConfigDiv(elemID, html);
    
    html = "threshold." + $("#xThresholdType").attr("value").toLowerCase() + "=" + $("#xThresholdSize").attr("value");

    appendHiddenConfigDiv(elemID, html);
}

function addCustom(){
    
    var elemID = configCount++;
    
    var html = "Custom :: " + $("#xCustomCondition").attr("value");
    
    appendUserConfigDiv(elemID, html);
    
    html = $("#xCustomCondition").attr("value");
    
    appendHiddenConfigDiv(elemID, html);
    
}

function addClustering(){
    
    var elemID = configCount++;
    
    var userHTML = "";
    var configHTML = "";
    
    userHTML = "Cluster :: " + $("#xClusteringType").attr("value");
    
    configHTML = "cluster." + $("#xClusteringType").attr("value").toLowerCase() + "=";
    
    if ($("input[name='xClusteringRadio']:checked").val() == "ip"){
        
        userHTML += " | IP | " + $("#xClusteringIPType").attr("value");
        
        configHTML += 'regex_replace("(\\\\d\\+)\\\\.\\\\d\\+")."/8"';
        
    }else{
        
        userHTML += " | Condition | " + $("#xClusteringCondition").attr("value"); 
        
        configHTML += $("#xClusteringCondition").attr("value");
    
    }
    
    appendUserConfigDiv(elemID, userHTML);

    appendHiddenConfigDiv(elemID, configHTML);
    
}

function addSize(){
 
    if(!maxNodeSizeSet && $("#xSizeMaxSize").attr("value")){ //If the max node size hasn't been set yet.
    
        maxNodeSizeSet = true;
    
        var elemID = configCount++;
    
        var html = "Max Node Size :: " + $("#xSizeMaxSize").attr("value");
        
        appendUserConfigDiv(elemID, html);
        
        html = "maxnodesize=" + $("#xSizeMaxSize").attr("value");
        
        appendHiddenConfigDiv(elemID, html);
        
        $("#xSizeMaxSize").prop('disabled', true);
    
    }
    
    var elemID = configCount++;
    
    var userHTML;
    
    var configHTML;
    
    
    if ($("input[name='xSizeRadio']:checked").val() == "exp"){
        
        userHTML = "Size :: " + $("#xSizeType").attr("value") + " | Expression - " +  $("#xSizeCondition").attr("value");
        
        configHTML = "size." + $("#xSizeType").attr("value").toLowerCase() + "=" + $("#xSizeCondition").attr("value");
    
    }else{
    
    }
    
    appendUserConfigDiv(elemID, userHTML);
    
    appendHiddenConfigDiv(elemID, configHTML);
    
    
    
    elemID = configCount++;

    userHTML = "Sum :: " + $("#xSizeType").attr("value") + " | ";
    
    configHTML = "sum." + $("#xSizeType").attr("value").toLowerCase() + "=";
    
    
    if($('#xSizeSum').is(':checked')){
        
        userHTML += "True";
        
        configHTML += "1";
    
    }else{
    
        userHTML += "False";    
    
        configHTML += "0";
    }
    
    appendUserConfigDiv(elemID, userHTML);
    
    appendHiddenConfigDiv(elemID, configHTML);
    
}

function populateProperty(){

    var value = "";
    
    for (var i = 0; i < configCount; i++){
        value += document.getElementById("configLine" + i).innerHTML + "\n"; 
    }
    
    document.getElementById("id_propertyConfig").value = value;

    //alert(value);
}