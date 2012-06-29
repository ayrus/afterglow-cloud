var configCount = 0;
var maxNodeSizeSet = false;
var sumSourceSet = false;
var sumEventSet = false;
var sumTargetSet = false;

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
    
    $('#xMaxNodeSizeButton').click(function (){
    
        addMaxNodeSize();
        
        return false;
    });
    
    $('#xSumButton').click(function (){
    
        addSum();
        
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
    
    html += "  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <a href=\"#\" onclick=\"removeConfigLine(this.parentNode.id)\">Remove</a>";
    
    html += "  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <a href=\"#\" onclick=\"changeOrder(this.parentNode.id, 'up')\">Up</a>";
    
    html += "  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <a href=\"#\" onclick=\"changeOrder(this.parentNode.id, 'down')\">Down</a><br/><br/>";
    
    //html += "  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <a href=\"#\" onclick=\"alert(this.parentNode.id)\";>XX</a>";
    
    elem.innerHTML = html;

    document.getElementById("alreadyAdded").appendChild(elem);
}

function appendHiddenConfigDiv(id, html){

    var elem = document.createElement("div");
    
    elem.id = "configLine" + id;
    
    elem.innerHTML = html;

    document.getElementById("alreadyAddedHidden").appendChild(elem);
}

function removeConfigLine(id){

    id = id.split("")[4];
    
    //Check if any global config is being removed and re-enable the form if so.

    var flag = $("#line" + id).find('#maxNodeSizeFlag').length;
    
    if (flag){
    
        maxNodeSizeSet = false;
        
        $("#xSizeMaxSize").prop('disabled', false);
        
        $("#xMaxNodeSizeButton").prop('disabled', false);
    
    }
    
    flag = $("#line" + id).find('#sumSourceFlag').length;
    
    if (flag){
    
        sumSourceSet = false;
        
        $("#xSumOptionSource").prop('disabled', false);
    
    }
    
    flag = $("#line" + id).find('#sumEventFlag').length;
    
    if (flag){
    
        sumEventSet = false;
        
        $("#xSumOptionEvent").prop('disabled', false);
    
    }
    
    flag = $("#line" + id).find('#sumTargetFlag').length;
    
    if (flag){
    
        sumTargetSet = false;
        
        $("#xSumOptionTarget").prop('disabled', false);
    
    }
    
    //Remove the user displayed config:
    
    var child = document.getElementById("line" + id);   
    
    var parent = child.parentNode;
    
    parent.removeChild(child);
    
    //Remove the raw config from the hidden field:
    
    child = document.getElementById("configLine" + id);
    
    parent = child.parentNode;
    
    parent.removeChild(child);
}

function getNextSibling(node){

    var next = node.nextSibling;

    while (next != null && next.nodeType != 1){
    
        next = next.nextSibling;
    }
    
    return next;
}

function getPreviousSibling(node){

    var previous = node.previousSibling;
    
    while (previous != null && previous.nodeType != 1){
    
        previous = previous.previousSibling;
    
    }
    
    return previous;

}

/* refactor */
function changeUp(id){

    id = parseInt(id.split("")[4]);
    
    for(var i=id-1; i>=0; i--){

        if ($("#line" + i).length > 0){
        
            var closestUserID = "line" + i;
            
            var closestConfigID = "configLine" + i;
            
            var userID = "line" + id;
            
            var configID = "configLine" + id;

            //Swap user UI end IDs.
           
            document.getElementById(userID).id = closestUserID;
            
            document.getElementById(closestUserID).id = userID;
            
            //Swap raw-config end IDs.
            
            document.getElementById(configID).id = closestConfigID;
            
            document.getElementById(closestConfigID).id = configID;
            
            document.getElementById("alreadyAdded").insertBefore(document.getElementById(closestUserID), document.getElementById(userID)); 
            
            break;
        
        }
    }

}

function changeOrder(id, type){

    var node = document.getElementById(id);
    
    id = parseInt(id.split("")[4]);
    
    if (type == "down"){
        var next = getNextSibling(node);
    }else{
        var next = getPreviousSibling(node);
    }
    
    var userID = "line" + id;
            
    var configID = "configLine" + id;
    
    if (next){
    
        var closestUserID = next.id;
        
        var closestConfigID = "configLine" + parseInt(next.id.split("")[4]);

        var temp = document.getElementById(userID);
        
        document.getElementById(closestUserID).id = userID;
            
        temp.id = closestUserID;
            
        //Swap raw-config end IDs.
        
        //alert(closestConfigID);
        
        temp = document.getElementById(configID);
        
        document.getElementById(closestConfigID).id = configID;
        
        temp.id = closestConfigID;
        
        document.getElementById("alreadyAdded").insertBefore(document.getElementById(userID), document.getElementById(closestUserID)); 
                
    }
    
/*    
    
    for(var i=id+1; i<=configCount; i++){
    
        //alert("x"+i);

        if ($("#line" + i).length > 0){
        
            var closestUserID = "line" + i;
            
            var closestConfigID = "configLine" + i;
            
            var userID = "line" + id;
            
            var configID = "configLine" + id;

            //Swap user UI end IDs.
            
            document.getElementById(closestUserID).id = userID;
            
            document.getElementById(userID).id = closestUserID;
            
            document.getElementById("alreadyAdded").insertBefore(document.getElementById(userID), document.getElementById(closestUserID)); 
            
            //Swap raw-config end IDs.
            
            document.getElementById(closestConfigID).id = configID;
            
            document.getElementById(configID).id = closestConfigID;
            
            break;
        
        }
    }
*/
}

function addColour(){
    
    var elemID = configCount++;
    
    var html = "Colour :: " +  $("#xColourType").attr("value") + " | " + $("#xColourHEX").attr("value") + " | ";
    
    if ($("input[name='xColourRadio']:checked").val() == "if"){ // not empty -- condition
        html += " IF | " + $("#xColourIfCondition").attr("value");
    }else if($("input[name='xColourRadio']:checked").val() == "custom"){
        html += " Custom | " + $("#xColourCustomCondition").attr("value");
    }
    
    
    html += "   <span class=\"colourBox\" style=\"background-color: " + $("#xColourHEX").attr("value") + ";\"> &nbsp;&nbsp;&nbsp;&nbsp; </span>"; 
    
    appendUserConfigDiv(elemID, html);

    if($("#xColourType").attr("value") == "All"){
        html = "color=\"" + $("#xColourHEX").attr("value") + "\"";
    }else{
        html = "color." + $("#xColourType").attr("value").toLowerCase() + "=\"" + $("#xColourHEX").attr("value") + "\"";    
    }
    
    if ($("input[name='xColourRadio']:checked").val() == "if"){ // not empty -- condition
        html += " if (" + $("#xColourIfCondition").attr("value") + ")";
    }else if($("input[name='xColourRadio']:checked").val() == "custom"){
        html += " " + $("#xColourCustomCondition").attr("value");
    }
    
    appendHiddenConfigDiv(elemID, html);
}

function addThreshold(){
    
    var elemID = configCount++;
    
    var html = "Threshold :: " + $("#xThresholdType").attr("value") + " | " + $("#xThresholdSize").attr("value");
    
    appendUserConfigDiv(elemID, html);
    
    if($("#xThresholdType").attr("value") == "All"){

        html = "threshold=" + $("#xThresholdSize").attr("value");
    
    }else{
    
        html = "threshold." + $("#xThresholdType").attr("value").toLowerCase() + "=" + $("#xThresholdSize").attr("value");
    }

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
    
    if($("#xClusteringType").attr("value") == "All"){
    
        configHTML = "cluster=";        
    
    }else{
    
        configHTML = "cluster." + $("#xClusteringType").attr("value").toLowerCase() + "=";    
    
    }
    
    
    
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
    
    var elemID = configCount++;
    
    var userHTML = "Size :: " + $("#xSizeType").attr("value");
    
    var configHTML;

    if($("#xSizeType").attr("value") == "All"){
    
        configHTML = "size=";
    
    }else{
    
        configHTML = "size." + $("#xSizeType").attr("value").toLowerCase() + "=";
    
    }
    
    
    if ($("input[name='xSizeRadio']:checked").val() == "exp"){
        
        userHTML += " | Expression - " +  $("#xSizeCondition").attr("value");
        
        configHTML +=  $("#xSizeCondition").attr("value");
    
    }else{

        if($("#xSizePreType").attr("value") == "num"){
        
            userHTML += " | Number of Occurences";
            
            configHTML += "$" + $("#xSizeType").attr("value").toLowerCase() + "Count{$" + $("#xSizeType").attr("value").toLowerCase() + "Name};";
        
        }else if($("#xSizePreType").attr("value") == "third"){
        
            userHTML += " | Third Data Column";
            
            configHTML += "$fields[2]"
        
        }else{
        
            userHTML += " | Fourth Data Column";
            
            configHTML += "$fields[3]"
        
        }
    
    }
    
    appendUserConfigDiv(elemID, userHTML);
    
    appendHiddenConfigDiv(elemID, configHTML);
    
}

function addMaxNodeSize(){

    if (!maxNodeSizeSet){
    
        var html = "Max Node Size :: " +  $("#xSizeMaxSize").attr("value");
        
        var elemID = configCount++;        
        
        appendUserConfigDiv(elemID, html);
        
        html = "maxnodesize=" + $("#xSizeMaxSize").attr("value");
        
        var elem = document.createElement("div");
        
        elem.id = "maxNodeSizeFlag";
        
        elem.style.display = "none";
        
        document.getElementById("line" + elemID).appendChild(elem);
        
        
        appendHiddenConfigDiv(elemID, html);
        
        maxNodeSizeSet = true;
        
        $("#xSizeMaxSize").prop('disabled', true);
        
        $("#xMaxNodeSizeButton").prop('disabled', true);
    
    }

}

function addSum(){

    var html;
    
    var elemID = configCount++;
    
    if($("#xSumType").attr("value") == "Source" && !sumSourceSet){
    
        html = "Sum Source :: True";
        
        appendUserConfigDiv(elemID, html);
        
        var elem = document.createElement("div");
        
        elem.id = "sumSourceFlag";
        
        elem.style.display = "none";
        
        document.getElementById("line" + elemID).appendChild(elem);
        
        html = "sum.source=1;"
        
        appendHiddenConfigDiv(elemID, html);
        
        $("#xSumOptionSource").prop('disabled', true);
        
        sumSourceSet = true;
    
    }else if($("#xSumType").attr("value") == "Event" && !sumEventSet){
    
        html = "Sum Event :: True";
        
        appendUserConfigDiv(elemID, html);
        
        var elem = document.createElement("div");
        
        elem.id = "sumEventFlag";
        
        elem.style.display = "none";
        
        document.getElementById("line" + elemID).appendChild(elem);
        
        html = "sum.event=1;"
        
        appendHiddenConfigDiv(elemID, html);
        
        $("#xSumOptionEvent").prop('disabled', true);
        
        sumEventSet = true;
    
    }else if(!sumTargetSet){
    
        html = "Sum Target :: True";
        
        appendUserConfigDiv(elemID, html);
        
        var elem = document.createElement("div");
        
        elem.id = "sumTargetFlag";
        
        elem.style.display = "none";
        
        document.getElementById("line" + elemID).appendChild(elem);
        
        html = "sum.target=1;"
        
        appendHiddenConfigDiv(elemID, html);
        
        $("#xSumOptionTarget").prop('disabled', true);
        
        sumTargetSet = true;
    
    }
    
}

function populateProperty(){

    var value = "";
    
    for (var i = 0; i <= configCount; i++){
    
        if ($("#configLine" + i).length > 0){ //if exists.
            value += document.getElementById("configLine" + i).innerHTML + "\n"; 
        }
    }
    
    document.getElementById("id_propertyConfig").value = value;

    //alert(value);
}