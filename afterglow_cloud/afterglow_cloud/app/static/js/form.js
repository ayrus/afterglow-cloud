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

function addCustom(){
    
    var elem = document.createElement("div");
    
    var elemID = configCount++;
    
    elem.id = "line" + elemID;
    
    elem.innerHTML = "Custom :: " + $("#xCustomCondition").attr("value");
    
    document.getElementById("alreadyAdded").appendChild(elem);
    
    elem = document.createElement("div");
    elem.id = "configLine" + elemID;
    
    elem.innerHTML = $("#xCustomCondition").attr("value");
    
    document.getElementById("alreadyAddedHidden").appendChild(elem);
    
}

function addClustering(){

    var elem = document.createElement("div");
    
    var elemID= configCount++;
    
    elem.id = "line" + elemID;
    
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
    
    elem.innerHTML = userHTML;
    
    document.getElementById("alreadyAdded").appendChild(elem);

    elem = document.createElement("div");
    
    elem.id = "configLine" + elemID;
    
    elem.innerHTML = configHTML;
    
    document.getElementById("alreadyAddedHidden").appendChild(elem);
    
}

function addSize(){
 
    if(!maxNodeSizeSet && $("#xSizeMaxSize").attr("value")){ //If the max node size hasn't been set yet.
    
        maxNodeSizeSet = true;
        
        var elem = document.createElement("div");
    
        var elemID = configCount++;
    
        elem.id = "line" + elemID;
        
        elem.innerHTML = "Max Node Size :: " + $("#xSizeMaxSize").attr("value");
        
        document.getElementById("alreadyAdded").appendChild(elem);
        
        elem = document.createElement("div");
        
        elem.id = "configLine" + elemID;
        
        elem.innerHTML = "maxnodesize=" + $("#xSizeMaxSize").attr("value");
        
        document.getElementById("alreadyAddedHidden").appendChild(elem);
        
        $("#xSizeMaxSize").prop('disabled', true);
    
    }
    
    var elem = document.createElement("div");
    
    var elemID = configCount++;
    
    elem.id = "line" + elemID;
    
    var configElem = document.createElement("div");
    
    configElem.id = "configLine" + elemID;
    
    var userHTML;
    
    
    if ($("input[name='xSizeRadio']:checked").val() == "exp"){
        
        userHTML = "Size :: " + $("#xSizeType").attr("value") + " | Expression - " +  $("#xSizeCondition").attr("value") + " | Sum - ";
        
        configElem.innerHTML = "size." + $("#xSizeType").attr("value").toLowerCase() + "=" + $("#xSizeCondition").attr("value");
    
    }else{
    
    }
    
    document.getElementById("alreadyAddedHidden").appendChild(configElem);
    
    
    
    
    elemID = configCount++;
    
    configElem = document.createElement("div");
    
    configElem.id = "configLine" + elemID;
    
    var configHTML = "sum." + $("#xSizeType").attr("value").toLowerCase() + "=";
    
    
    if($('#xSizeSum').is(':checked')){
        
        userHTML += "True";
        
        configHTML += "1";
    
    }else{
    
        userHTML += "False";    
    
        configHTML += "0";
    }
    
    
    elem.innerHTML = userHTML;

    configElem.innerHTML = configHTML;    
    
    document.getElementById("alreadyAdded").appendChild(elem);
    
    document.getElementById("alreadyAddedHidden").appendChild(configElem);

}

function populateProperty(){

    var value = "";
    
    for (var i = 0; i < configCount; i++){
        value += document.getElementById("configLine" + i).innerHTML + "\n"; 
    }
    
    document.getElementById("id_propertyConfig").value = value;

    //alert(value);
}