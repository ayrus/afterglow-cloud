/* Globals */
var configCount = 0; //A counter for the number of configuration lines.
//Following are flags to enable/disable inputting a global setting (which can be
//	set only once).
var maxNodeSizeSet = false;
var sumSourceSet = false;
var sumEventSet = false;
var sumTargetSet = false;

var afLogglySet = false;

$(document).ready(function(){

	//Invoke the colour pickers.
    $('#id_textLabel').miniColors();
    $('#xColourHEX').miniColors();
	
    //Invoke the tool-tips.
    $(".tooltip").tipTip({maxWidth: "250px"});

    //Show the override box input (which is hidden otherwise) if the cookie
    //data from the view has the 'override-edge' box checked.
    if($("#id_overrideEdge").is(":checked")){
	    toggleShowOverrideInput();
    }
    
    $('input[name=xLogType]')[0].checked = true;
    $('input[name=regExType]')[0].checked = true;

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
    
    //Following are event handlers for different buttons in the configurations'
    //fieldsets.
    $('#xColourButton').click(function () {
        addColour();
    	hidePlaceholder();
        return false;
    });
    
    $('#xThresholdButton').click(function () {
		if(validateConfig('threshold')){ 
			//Request is processed only if the data is found to be valid.
        	addThreshold();
        	hidePlaceholder();
		}
        return false;
    });
    
    $('#xCustomButton').click(function () {
        addCustom();
        hidePlaceholder();
        return false;
    });    
    
    $('#xClusteringButton').click(function (){
        addClustering();
        hidePlaceholder();
        return false;
    });
    
    $('#xSizeButton').click(function (){
        addSize();
        hidePlaceholder();
        return false;
    });
    
    $('#xMaxNodeSizeButton').click(function (){
		
		if(validateConfig('maxNodeSize')){
        	addMaxNodeSize();
        	hidePlaceholder();
		}
		return false;
    });
    
    $('#xSumButton').click(function (){
        addSum();
        hidePlaceholder();
        return false;
    });
    
    if($("#id_twoNodeMode").is(":checked")){
    	$('#eventFanOutThres').hide();
    }
    
    //Change the type of configuration input, if the radio in the configurations
    //panel has any action.
    $('input[name=xConfigType]').change(function() {
    
        if($('input[name=xConfigType]:checked').val() == "manual"){
        
            $("#customConfig").hide();
            
            $("#manualConfig").fadeToggle(400);
        
        }else{
        
            $("#manualConfig").hide();
        
            $("#customConfig").fadeToggle(400);
        }
    
    });

    $('input[name=xLogType]').change(function() {

	var val = $('input[name=xLogType]:checked').val();
	
	if(val != "data" ){
		toggleRegExInputs(); 
		$('#regEx').show();
		if(val == "loggly"){
			$('#file').hide();
			if(!afLogglySet){
				$('#loggly').show();
			}else{
				$('#logglySetMsg').show();
			}
		}else{
			$('#file').show();
			$('#logglySetMsg').hide();
			$('#loggly').hide();
		}
	}else{
		$('#logglySetMsg').hide();
		$('#saveRegEx').hide();
		$('#regEx').hide();
		$('#file').show();
		$('#loggly').hide();
	}
    });
    
    $('input[name=regExType]').change(function() {
	toggleRegExInputs();    
    });
    
    $('#id_regExChoices').change(function() {
	showDescription($('#id_regExChoices').val());
    });
    
    $("#id_saveRegEx").click(function () { 
    	if($("#id_saveRegEx").is(":checked")){
		$('#saveRegExDetails').show();
	}else{
		$('#saveRegExDetails').hide();
	}
    });
    
    $("#id_twoNodeMode").click(function () { 
    	if($("#id_twoNodeMode").is(":checked")){
		$('#eventFanOutThres').hide();
	}else{
		$('#eventFanOutThres').show();
	}
    });
    
    //Set up a listener for the submit of the main form.    
    $('#renderMainForm').submit(function () {

	//Reset any previous validation messages.
	resetValidations();

	var dataFile = true;
	
	if($('input[name=xLogType]:checked').val() != "loggly"){
		dataFile = validateDataFile();
	}

	var edgeLength = validateEdgeLength();

	var advancedIntegers = validateAdvancedIntegers();
        
        //Read the configuration data (added by the user) from the hidden field
        //'alreadyAddedHidden' and populate form element to submit.
        populateProperty();    
    
    	//Check the validation booleans from every validators above and proceed
    	//ahead only if all are 'true'.
        return dataFile && edgeLength && advancedIntegers;
    });
    
});

function showDescription(id){
	var contents = $("#xRegExDescriptions").html().split("[[[;]]]");
	
	var desc;
	for(var i=0; i<contents.length; i++){
		desc = contents[i].split("[[;]]");
		if (id == desc[0]){
			$('#regDesc').html("<b>Expression Description</b>: " + desc[1].split('\n').join('<br/>'));
			$('#regDesc').show();
			break;
		}
	}	
}

function toggleRegExInputs(){
    	if ($('input[name=regExType]:checked').val() == 1){
		$('#id_regEx').show();
		$('#id_regExChoices').hide();
		$('#saveRegEx').show();
		$('#regDesc').hide();
	}else{
		$('#id_regExChoices').show();
		$('#id_regEx').hide();
		$('#saveRegEx').hide();
	}
}

/*	Toggle the textbox to input the edge-length. If the 'override-edge' checkbox
 *	is checked then show the box, hide otherwise.
 *	@Params: None.
 *	@Return: None.
 */
function toggleShowOverrideInput(){

     if($('#id_overrideEdge').attr('checked')){
        $('#id_overrideEdgeLength').show();
     }else{
        $('#id_overrideEdgeLength').hide();
     }
}

/*	Toggle the 'Settings' pane using JQuery's slide UI function.
 *	@Params: None.
 *	@Return: None.
 */
function toggleShowMainSettings(){
    $('#mainSettings').slideToggle(('slow'));   
}

/*	Toggle the 'Advanced Settings' pane using JQuery's slide UI function.
 *	@Params: None.
 *	@Return: None.
 */
function toggleShowAdvanced(){
    $('#advanced').slideToggle(('slow'));
}

/*	Toggle the 'Configuration' pane using JQuery's slide UI function.
 *	@Params: None.
 *	@Return: None.
 */
function toggleShowConfig(){
    $('#config').slideToggle(('slow'));
}

/*	Append a configuration line to the user UI.
 *	@Params: id - the count of this configuration (from the global counter).
 			html - the inner HTML content to append.
 *	@Return: None.
 */
function appendUserConfigDiv(id, html){

    var elem = document.createElement("div");
    
    elem.id = "line" + id;
    
    elem.className = "xConfigLine";
    
    html += "<div class=\"configFunctions\">";
    
    html += "  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <a href=\"#\" onclick=\"removeConfigLine(this.parentNode.parentNode.id)\" class=\"removeLink\" title=\"Remove line\">&nbsp;&nbsp;&nbsp;&nbsp;</a>";
    
    html += "  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <a href=\"#\" onclick=\"changeOrder(this.parentNode.parentNode.id, 'up')\" class=\"upLink\" title=\"Move Up\">&nbsp;&nbsp;&nbsp;&nbsp;</a>";
    
    html += "  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <a href=\"#\" onclick=\"changeOrder(this.parentNode.parentNode.id, 'down')\" class=\"downLink\" title=\"Move Down\">&nbsp;&nbsp;&nbsp;&nbsp;</a>";
    
    html += "</div>";
   
    elem.innerHTML = html;

    document.getElementById("alreadyAdded").appendChild(elem);
}

/*	Append a raw configuration line (which is hidden) to the page..
 *	@Params: id - the count of this configuration (from the global counter).
 			html - the inner HTML content to append.
 *	@Return: None.
 */
function appendHiddenConfigDiv(id, html){

    var elem = document.createElement("div");
    
    elem.id = "configLine" + id;
    
    elem.innerHTML = html;

    document.getElementById("alreadyAddedHidden").appendChild(elem);
}

/*	Remove a configuration line from the user's UI and the hidden field on the
	page.
 *	@Params: id - the HTML ID of the element on the user UI to be removed.
 *	@Return: None.
 */
function removeConfigLine(id){

	//Grab the unique numeric ID.
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

/*	Find and return the next sibling node to the existing node 'node'. The next
 *	sibling node has to be an element node.
 *	@Params: node - the present node to start the search from.
 *	@Return: The next sibling element node.
 */
function getNextSibling(node){

    var next = node.nextSibling;

    while (next != null && next.nodeType != 1){
    
        next = next.nextSibling;
    }
    
    return next;
}

/*	Find and return the previous sibling node to the existing node 'node'. The
 *	previous node has to be an element node.
 *	@Params: node - the present node to start the search from.
 *	@Return: The previous sibling element node.
 */
function getPreviousSibling(node){

    var previous = node.previousSibling;
    
    while (previous != null && previous.nodeType != 1){
    
        previous = previous.previousSibling;
    
    }
    
    return previous;

}

/*	Hide the placeholder message inside the added configurations pane if any
 *	configuration lines have been set.
 *	@Params: None.
 *	@Return: None.
 */
function hidePlaceholder(){
	
	if(configCount > 0){
		$("#configPlaceholder").hide();
		$("#configHeaders").show();
	}
	
}

/*	Change the ordering of a configuration element (both on the user ID and the
 * 	the hidden field) either 'up' or 'down'.
 *	@Params: id - the HTML ID of the element on the user UI to change the
 *	the ordering of.
 *		type - 'up' or 'down' specifying the order of change, upwards or down.
 *	@Return: The next sibling element node.
 */
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
        
		//Swap the elements IDs on the user UI.
        
        document.getElementById(closestUserID).id = userID;
            
        temp.id = closestUserID;
            
		//Swap the elements IDs on the hidden end.
        
        temp = document.getElementById(configID);
        
        document.getElementById(closestConfigID).id = configID;
        
        temp.id = closestConfigID;
        
        //Make the configurations lines on the page "appear" going "up" or "down".
        
        if(type == "down"){        
        
            document.getElementById("alreadyAdded").insertBefore(document.getElementById(userID), document.getElementById(closestUserID));
            
        }else{
        
            document.getElementById("alreadyAdded").insertBefore(document.getElementById(closestUserID), document.getElementById(userID));
        
        }
                
    }
}

/*	Add a colour configuration line.
 *	@Params: None.
 *	@Return: None.
 */
function addColour(){
    
    var elemID = configCount++;
    
    var html = "Colour :: " +  $("#xColourType").attr("value") + " | " + $("#xColourHEX").attr("value") + " | ";
    
    //Prepare and add the element to the user UI.
    if ($("input[name='xColourRadio']:checked").val() == "if"){
    
    	// not empty -- condition
        html += " IF | " + $("#xColourIfCondition").attr("value");
        
    }else if($("input[name='xColourRadio']:checked").val() == "custom"){
    
        html += " Custom | " + $("#xColourCustomCondition").attr("value");
        
    }
    
    
    html += "   <span class=\"colourBox\" style=\"background-color: " + $("#xColourHEX").attr("value") + ";\"> &nbsp;&nbsp;&nbsp;&nbsp; </span>"; 
    
    appendUserConfigDiv(elemID, html);

	//Prepare and add the element to the hidden config end.
    if($("#xColourType").attr("value") == "All"){
    
        html = "color=\"" + $("#xColourHEX").attr("value") + "\"";
        
    }else{
    
        html = "color." + $("#xColourType").attr("value").toLowerCase() + "=\"" + $("#xColourHEX").attr("value") + "\"";    
        
    }
    
    if ($("input[name='xColourRadio']:checked").val() == "if"){ 
    
    	// not empty -- condition
        html += " if (" + $("#xColourIfCondition").attr("value") + ")";
        
    }else if($("input[name='xColourRadio']:checked").val() == "custom"){
    
        html += " " + $("#xColourCustomCondition").attr("value");
        
    }
    
    appendHiddenConfigDiv(elemID, html);
}

/*	Add a threshold configuration line.
 *	@Params: None.
 *	@Return: None.
 */
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

/*	Add a custom configuration line.
 *	@Params: None.
 *	@Return: None.
 */
function addCustom(){
    
    var elemID = configCount++;
    
    var html = "Custom :: " + $("#xCustomCondition").attr("value");
    
    appendUserConfigDiv(elemID, html);
    
    html = $("#xCustomCondition").attr("value");
    
    appendHiddenConfigDiv(elemID, html);
    
}

/*	Add a clustering configuration line.
 *	@Params: None.
 *	@Return: None.
 */
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
	
	if($("#xClusteringIPType").val() == "a"){
		configHTML += 'regex_replace("(\\\\d\\+)\\\\.\\\\d\\+")."/8"';
	}else if($("#xClusteringIPType").val() == "b"){
		configHTML += 'regex_replace("(\\\\d\\+\\\\.\\\\d\\+)\\\\.\\\\d\\+")."/16"';
	}else{
		configHTML += 'regex_replace("(\\\\d\\+\\\\.\\\\d\\+\\\\.\\\\d\\+)\\\\.\\\\d\\+")."/24"';
	}
        
        
    }else if($("input[name='xClusteringRadio']:checked").val() == "exp"){
        
        userHTML += " | Condition | " + $("#xClusteringCondition").attr("value"); 
        
        configHTML += $("#xClusteringCondition").attr("value");
    
    }else{
    	
    	userHTML += " | Port | > " + $("#xClusteringPort").attr("value");
	
	configHTML += '\"> ' + $("#xClusteringPort").attr("value") + '\" if ($fields[2]>' + $("#xClusteringPort").attr("value") + ')';
    }
    
    appendUserConfigDiv(elemID, userHTML);

    appendHiddenConfigDiv(elemID, configHTML);
    
}

/*	Add a size configuration line.
 *	@Params: None.
 *	@Return: None.
 */
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

/*	Add a maxnodesize configuration line (a global setting).
 *	@Params: None.
 *	@Return: None.
 */
function addMaxNodeSize(){

	//Proceed only if not already set.
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
        
        //Update the flag and disable further input (until removed).
        maxNodeSizeSet = true;
        
        $("#xSizeMaxSize").prop('disabled', true);
        
        $("#xMaxNodeSizeButton").prop('disabled', true);
    
    }

}

/*	Add a sum configuration line (a global setting).
 *	@Params: None.
 *	@Return: None.
 */
function addSum(){

    var html;
    
    var elemID = configCount++;
    
    //Check for individual sum setting (determine which one has been set) and
    //proceed only if the one requested hasn't been already set.
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

/*	Read the raw configuration data from the hidden field and populate the
 * 	textbox form element supplied by the view to process and send the request.
 *	@Params: None.
 *	@Return: None.
 */
function populateProperty(){

    var value = "";
    
    //Check if the configuration tpye is manual or custom.
    if($('input[name=xConfigType]:checked').val() == "manual"){
    
        value = $("#xManualConfig").attr("value");
    
    }else{
    
        for (var i = 0; i <= configCount; i++){
        
            if ($("#configLine" + i).length > 0){ //if exists.
                value += document.getElementById("configLine" + i).innerHTML + "\n"; 
            }
        }
        
    }
    
    document.getElementById("id_propertyConfig").value = value;
}

/*	Change the CSS style property 'display' of the parent element of 'id' to
 *	'block' (show) itself.
 *	@Params: None.
 *	@Return: None.
 */
function showParent(id){

	$("#" + id).parent().attr('style','display: block !important');

}

/*	Change the CSS style property 'display' of the parent element of 'id' to
 *	'none' (hide) itself.
 *	@Params: None.
 *	@Return: None.
 */
function hideParent(id){

	$("#" + id).parent().attr('style','display: none !important');

}

/*	Remove every validation message (everything that is present) from the page.
 *	@Params: None.
 *	@Return: None.
 */
function resetValidations(){

	var ids = new Array("dataFileE", "overrideEdgeE", "maxLinesE", "skipLinesE", "omitThresholdE", "sourceFanOutE", "eventFanOutE");

	for (var i = 0; i < ids.length; i++){
		hideParent(ids[i]);
	}
}

/*	Validate the data-file form input on the page and return the validation
 * 	status.
 *	@Params: None.
 *	@Return: true if valid, false otherwise.
 */
function validateDataFile(){

	if(!$("#id_dataFile").attr("value")){

		$("#dataFileE").html("Please choose a file.");

		showParent("dataFileE");

		return false;

	}
    
    return true;

}

/*	Validate the edge-length form input on the page and return the validation
 * 	status.
 *	@Params: None.
 *	@Return: true if valid, false otherwise.
 */
function validateEdgeLength(){

	if($("#id_overrideEdge").is(":checked")){

		var condition = /^[0-9]+(\.[0-9]{1,2})?$/;

		if(!condition.test($("#id_overrideEdgeLength").attr("value"))){

			$("#overrideEdgeE").html("Please enter a positive decimal value. Maximum of two decimal places.");
	
			showParent("overrideEdgeE");

			$('#mainSettings').show();
			
			return false;
		}

	}
	
	return true;

}

/*	Validate all the integer form inputs on the page and return the validation
 * 	status.
 *	@Params: None.
 *	@Return: true if all valid, false otherwise.
 */
function validateAdvancedIntegers(){

	var flag = true;

	var posInteger = /^[0-9]+$/;

	var intFields = new Array("skipLines", "omitThreshold", "sourceFanOut", "eventFanOut");

	if(!posInteger.test($("#id_maxLines").attr("value"))){

		$("#maxLinesE").html("Please enter a valid decimal.");

		showParent("maxLinesE");

		flag = flag = false;

	}else if(parseInt($("#id_maxLines").attr("value")) < 1 || parseInt($("#id_maxLines").attr("value")) > 999999){
	
		$("#maxLinesE").html("Please enter a value between 1 - 999999");

		showParent("maxLinesE");

		//Boolean AND.
		flag = flag && false;

	}

	for (var i = 0; i < intFields.length; i++){

		if(!posInteger.test($("#id_" + intFields[i]).attr("value"))){

			$("#" + intFields[i] +"E").html("Please enter a valid decimal.");		

			showParent(intFields[i] + "E");
	
			flag = flag && false;

		}
	}
	
	if(!flag){
		$('#advanced').show();
	}
	
	return flag;
}

/*	Validate integer inputs on the configuration panel.
 *	@Params: what - specifies which input to test; valid values are "threshold"
 		and "maxNodeSize".
 *	@Return: true if valid, false otherwise.
 */
function validateConfig(what){

	var posInteger = /^[0-9]+$/;

	hideParent(what + "E");

	if(what == "maxNodeSize"){

		if(!posInteger.test($("#xSizeMaxSize").attr("value"))){

			$("#" + what +"E").html("Please enter a valid decimal.");		

			showParent(what + "E");

			return false;
		}

	}else{

		if(!posInteger.test($("#xThresholdSize").attr("value"))){

			$("#" + what +"E").html("Please enter a valid decimal.");		

			showParent(what + "E");

			return false;
		}	
	}

	return true;
}
