$(document).ready(function(){
    $('#contactForm').submit(function () {
    
	//Reset any previous validation messages.
	resetValidations();
    
	var user = validate("userName");
	var email = validate("userEmail");
	var message = validate("userMessage")
    
    	//Check the validation booleans from every validators above and proceed
    	//ahead only if all are 'true'.
        return user && email && message;
    });
});

function resetValidations(){

	var ids = new Array("userNameE", "userEmailE", "userMessageE");

	for (var i = 0; i < ids.length; i++){
		hideParent(ids[i]);
	}
}

function showParent(id){

	$("#" + id).parent().attr('style','display: block !important');

}

function hideParent(id){

	$("#" + id).parent().attr('style','display: none !important');

}

function validate(what){

    if(!$("#id_" + what).attr("value")){	
    
	    $("#" + what + "E").html("This field is required.");
	    showParent(what + "E");
	    return false;
	    
	}
    
    return true;
}