from django.shortcuts import render_to_response, redirect, HttpResponseRedirect
from django.template import RequestContext
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from recaptcha.client import captcha
from hashlib import md5
from datetime import datetime, timedelta
from subprocess import call
from time import time
from afterglow_cloud.app.form import renderForm, contactForm, logglySearchForm, gallerySubmitForm
from afterglow_cloud.app.models import Expressions, Images
from shutil import copyfile
from easy_thumbnails.files import get_thumbnailer
import os, re
import oauth2 as oauth
import urlparse
import base64
import urllib
import simplejson as json

def index(request):
    ''' 
    Display a view for the index page.
    
    Keyword arguments:
    request -- the request object.
     
    Return: 
    The index view.
    '''
    
    return render_to_response('index.html', locals(), 
                                      context_instance=RequestContext(request))

def processForm(request):
    '''
    Display the main process form for rendering an image. 
    This view also handles a process/render request and approriately diverts 
    the routine.
    
    Keyword arguments:
    request -- the request object.
    
    Return
    A view to display a form (pre-rendering request) or a processed
    request.
    '''
    
    if request.method == 'POST':
	
        form = renderForm(request.POST, request.FILES)        
        
        if form.is_valid():
	    
	    	# Save configuration property in session for "Last Used 
	    	# Configuration" option on the view.
	    	request.session['propertyConfig'] = request.POST['propertyConfig']
	    
	    	if request.POST['xLogType'] == "loggly":
		    
			# Save the complete rendering options in session for
		    	# later use.
			request.session["logglyForm"] = request.POST
			
			if "afLoggly" in request.COOKIES \
			   and'key' in request.session \
			   and 'secret' in request.session \
			   and 'subdomain' in request.session:
			    
			    	# If a user attempts to get data from Loggly and
			    	# has authentication credentials then direct
			    	# them straight to the search option.
			    	return redirect('/search')
			else:
		    	
		    		# No authentication data, try requesting a token
			    	# from Loggly.
		    		return _logglyAuth(request)
	    	else:
	    		
            		return _render(request, request.POST['xLogType'] == "log")
    else:

        if "afConfig" in request.COOKIES: #Some saved config in history.
            
            form = renderForm(initial = _readCookie(request.COOKIES['afConfig']))
        else:
            form = renderForm(initial = {'regExType': '1'})
	    
    if "afLoggly" in request.COOKIES:
    	
    	# User has previously authorized the application to use their Loggly
	# account. Read the cookie saved previously and populate the token
	# credentials in session.
	
    	afLogglySet = True
	afLogglySubdomain = _readLogglyCookie(request.COOKIES['afLoggly'], request.session)
	
    # Boolean flag to display a message when a user revokes access to Loggly.
    if "r" in request.GET and request.GET["r"] == '1':
	afLogglyRevoked = True    
	
    # Query for the descriptions of all the RegEx expressions saved in the
    # database, so that it can be populated on the view.
    regExDescriptions = ""
    for e in Expressions.objects.order_by('id').all():
	regExDescriptions += str(e.id) + "[[;]]" + e.description + "[[[;]]]"
	
    # Check if user has previously rendered an image in this session and obtain
    # their last used condiguration from their session if so - for the view.
    if "propertyConfig" in request.session:
	propertyConfigPopulate = True
	propertyConfig = request.session["propertyConfig"]        
        
    return render_to_response('form.html', locals(), 
                              context_instance=RequestContext(request))

def contact(request):
    '''
    Display and process the contact form.
    
    Keyword arguments:
    request -- the request object.
    
    Return:
    The contact form view (if pre-request) or a view with a success
    message.
    '''
    
    CAPTCHA_PUBLIC_KEY = settings.AF_RECAPTCHA_PUBLIC_KEY
    
    if request.method == 'POST':
        
        form = contactForm(request.POST)        
        
        if form.is_valid():
	    
	    # Check if the response CAPTCHA value is valid; else redirect back
	    # with an error.
            response = captcha.submit(  
                        request.POST.get('recaptcha_challenge_field'),  
                        request.POST.get('recaptcha_response_field'),  
                        settings.AF_RECAPTCHA_PRIVATE_KEY,  
                        request.META['REMOTE_ADDR'],)         
            
            if not response.is_valid:
		
                captchaWrong = True
                return render_to_response('contact.html', locals(), 
                              context_instance=RequestContext(request))
            
            subject = request.POST['userSubject']
            
            message = "Hello, you've received a message from AfterGlow Cloud.\n"
            
            message += "User: " + request.POST["userName"] + " (" \
                + request.POST["userEmail"] + ") says: \n\n"
            
            message += request.POST["userMessage"]
            
            from_email = settings.AF_FROM_EMAIL
	    
            try:
                send_mail("AfterGlow: " + subject, message, 
                          from_email, settings.AF_TO_EMAILS)
            except BadHeaderError:
                return HttpResponse('Invalid header found. Please try again.')
            
            # Boolean flag used to display a 'success' message on the view.
            mailSent = True

    else:
	
        form = contactForm()
    
    return render_to_response('contact.html', locals(), 
                              context_instance=RequestContext(request))

def _render(request, parsedData, loggly=False, logglyData=None):
    '''
    Processes a request and attempts to render a graph. 
    
    Keyword arguments:
    request -- the request object.
    parsedData -- boolean, True if the incoming data is parsed data (log/Loggly)
    loggly -- boolean, True if the incoming data is from Loggly. 
    logglyData -- A string data returned from a Loggly search.
    
    Return:
    A rendered graph from the request if successful or an error message
    on the view.
    '''

    # Generate a session-key if one isn't already active.
    if hasattr(request, 'session') and hasattr(request.session, \
                                               'session_key') and \
       getattr(request.session, 'session_key') is None:
      
        request.session.create()
    
    # Generate a unique request ID hash from the session key for this particular
    # request.
    requestID = md5(request.session.session_key + 
            str(datetime.now())).hexdigest()       
    
    # Clean up old user resource files which are older than four hours.
    _cleanFiles()
    
    # If this rendering request's data has been fetched from Loggly, then
    # retrieve the rendering settings/configurations from the session (where it
    # has been previously saved).
    if loggly:
	POSTdata = request.session["logglyForm"]
    else:
	POSTdata = request.POST
    
    # Flag to check and alert of any errors encountered while attempting to 
    # render.
    retVal = 0
    
    
    if parsedData:

	if loggly:
	    
	    # If data from Loggly (after a search) is empty, alert the user.
	    if not logglyData:
		emptyData = True
		return render_to_response('render.html', locals(), 
				                          context_instance=RequestContext(request))			
	    
	    # Parse the data from Loggly's search into a CSV file.
	    retVal = _parseToCsv(logglyData, requestID, POSTdata, True)  
	    
	else:
	    
	    # Parse the log file into a CSV file with the expression given.
	    retVal = _parseToCsv(request.FILES['dataFile'], requestID, POSTdata)  
          
	
	# If the user submitted a custom regex expression and indicated to
	# save it; insert the data into the database and alert an administrator
	# through email.
	if not retVal and POSTdata['regExType'] == '1' and "saveRegEx" in POSTdata:
	    
	    expression = Expressions(name=POSTdata['saveRegExName'], \
	                             description=POSTdata['saveRegExDescription'], \
	                             regex=POSTdata['regEx'])
	    expression.save()
			
	    message = "Hello, a new expression has been submitted.\n"
	    
	    message += "Exp name: " + POSTdata["saveRegExName"] \
	        + "\n\nDescription: " + POSTdata["saveRegExDescription"] \
	        + "\n\nExpression: " + POSTdata["regEx"] \
	        + "\n\n"
	    
	    from_email = settings.AF_FROM_EMAIL
	    
	    try:
		send_mail("Expression submit @AfterGlow", message, 
	                  from_email, settings.AF_TO_EMAILS)
	    except BadHeaderError:
		return HttpResponse('Invalid header found. Please try again.')	    
	    
	
    else:
	# A CSV file has been uploaded, write it as-is to the server.
	
        _writeDataFile(request.FILES['dataFile'], requestID)
    
    # If retVal has been changed from 0 to any other value from its point of
    # declaration we have an error. Alert the user.
    if retVal:
	
	return render_to_response('render.html', locals(), 
		                          context_instance=RequestContext(request))	
	
    else:
    
	_writeConfigFile(POSTdata['propertyConfig'], requestID)
	
	#Build up parameters to be sent to the shell script.
	param = _buildParameters(POSTdata)
	
	if parsedData:
	    dataFile = "user_logs_parsed/" + requestID + ".log"
	else:
	    dataFile = "user_data/" + requestID + ".csv"
	    
	propertyFile = "user_config/" + requestID + ".property"
	outputFile = "afterglow_cloud/app/static/rendered/" + requestID + ".gif"
	afPath = "../afterglow/src/afterglow.pl"
	
	#Try rendering a graph, store the return code from the shell script.
	status = _renderGraph(dataFile, propertyFile, outputFile, afPath,
	                   POSTdata['renderingFilter'], param)
	
	CAPTCHA_PUBLIC_KEY = settings.AF_RECAPTCHA_PUBLIC_KEY
	
	# Form instance to save the rendered image to the gallery.	
	form = gallerySubmitForm(initial = {'image' : requestID})
	
	# Store the unique request-ID used in this render request (to be used
	# if the user opts in to submit the image to the gallery).
	request.session['requestID'] = requestID
	
	#Construct a rendered graph response.
	response = render_to_response('render.html', locals(), 
	                          context_instance=RequestContext(request))
	
	#Check if the user wanted to save/create a cookie to save their
	#settings for future use.
	if("saveConfigCookie" in POSTdata):
	  
	    expiry = datetime.now() + timedelta(days = 3)
	    
	    response.set_cookie(key = "afConfig", 
		                value = _buildCookie(POSTdata),
		                expires = expiry)
	
	return response    
    

def _parseToCsv(f, requestID, POSTdata, loggly=False):
    '''
    Parses a data source into a CSV file using the regular expression given
    by the user.
    
    Keyword arguments:
    f -- data source.
    requestID -- uniquq request ID associated with this request.
    POSTdata -- rendering settings/options given by the user opon request.
    loggly -- boolean, True if the incoming data is from loggly.
    
    Return: 
    0 -- if the file was sucessfuly parsed.
    1 -- if no groups were made with the expression given.
    2 or 3 -- if there were missing match(es).
    '''
    
    fileName = requestID + '.log'
    
    with open(os.path.join(settings.PROJECT_PATH, '../user_logs/') + fileName, 'wb+') as dest:

	# If the data 'f' is from Loggly write it line by line or use the data
	# as a stream (uploaded log file from the user).
	if not loggly:	
	    
	    for chunk in f.chunks():
	    	dest.write(chunk)
	else:
	    
	    for line in f:
		dest.write(line)
		
    # If the user selected a 'predefined' expression, query and obtain the
    # expression from the database.
    if POSTdata['regExType'] == '1':
	
    	pat = re.compile(POSTdata['regEx'])
    else:
	
	pat = re.compile(Expressions.objects.all().get(id=POSTdata['regExChoices']).regex)
    
    # Parse the data using the regular expression compiled and write as a CSV 
    # file.
    with open(os.path.join(settings.PROJECT_PATH, '../user_logs_parsed/') + fileName, 'wb+') as dest:
        
        for line in open(os.path.join(settings.PROJECT_PATH, '../user_logs/') + fileName):
            match = pat.match(line)
	    
	    # Error - no match found.
	    if not match:
		return 1
	    
	    match = match.groups()
	    
	    try:
            
            	string = match[0] + "," + match[1]   
	    
	    except IndexError:
		# Grouping error.
		return 2
	    
	    try:
		
	    	if 'twoNodeMode' not in POSTdata: 
		    #We get the third group (column) as well.
		    string += "," + match[2]
		    
	    except IndexError:
		# Grouping / wrong number of columns - error.
		return 3
                
            string += "\n"
            
            dest.write(string)
	    
    return 0


def _cleanFiles():
    '''
    Clean up every user-data, user-configuration and rendered image files
    which are older than 4 hours from this point.
    
    Keyword arguments:
    None.
    
    Return:
    None.
    '''
    
    # List of relatives paths to be pruned for older files.
    paths = ["afterglow_cloud/app/static/rendered/", "user_data/", \
             "user_config/", "user_logs/", "user_logs_parsed/"]
    
    for path in paths:
    
        absPath = os.path.join(settings.PROJECT_PATH, '../' + path)
        files = os.listdir(absPath)
    
        for oldFile in files:
      
            oldFilePath = os.path.join(absPath, oldFile)
            info = os.stat(oldFilePath)            
            
            #If older than 4 hours -- delete.
            if(info.st_ctime < int(time() - 4*60*60)):
        
                os.unlink(oldFilePath)
            
def _writeDataFile(f, requestID):
    '''
    Write the CSV data file present in the file-stream 'f' from the user,
    to a local file with 'requestID' as its name.
    
    Keyword arguments:
    f -- CSV data file uploaded by the user.
    requestID -- the unique requestID associated with this rendering request.
    
    Return:
    None.
    '''
    
    fileName = requestID + '.csv'

    with open(os.path.join(settings.PROJECT_PATH, '../user_data/') + fileName, 'wb+') as dest:
	
        for chunk in f.chunks():
            dest.write(chunk)

def _writeConfigFile(data, requestID):
    '''
    Write the configuration file present in the string 'data' fromt he user,
    to a local file with "requestID" as its name.
    
    Keyword arguments:
    data -- configuration file uploaded by the user..
    requestID -- the unique requestID associated with this rendering request.
    
    Return:
    None.    
    '''
    
    fileName = requestID + '.property'
    
    with open(os.path.join(settings.PROJECT_PATH, '../user_config/') + fileName, 'wb') as dest:
        dest.write(data)

def _buildParameters(options):
    '''
    Read the different flag values sent by the user request in 'options' and
    build parameters to be sent to AfterGlow.
    
    Keyword arguments:
    options -- POST data submitted by the user while submitting a request.
    
    Return:
    A parameterized string built from the user's choices to be sent to the
    shell script for rendering.
    '''
    
    # Append '-a' by default to disable text on the footer.
    param = "-a "
    
    if 'twoNodeMode' in options:
        param += "-t "
        
    if 'printNodeCount' in options:
        param += "-d "
        
    if 'splitNodes' in options:
        param += "-s "
        
    if options['splitMode'] is not 0:
        param += "-p " + options['splitMode'] + " "
        
    if 'overrideEdge' in options:
        param += "-e " + options['overrideEdgeLength'] + " "
        
    param += "-x \"" + options['textLabel'] + "\" "
    
    if options['skipLines'] is not 0:
        param += "-b " + options['skipLines'] + " " 
    
    if options['maxLines'] is not 999999:
        param += "-l " + options['maxLines'] + " "
    
    if options['omitThreshold'] is not 0:
        param += "-o " + options['omitThreshold'] + " "
    
    if options['sourceFanOut'] is not 0:
        param += "-f " + options['sourceFanOut'] + " "
    
    if options['eventFanOut'] is not 0:
        param += "-g " + options['eventFanOut'] + " "       
        
    return param  
  
def _buildCookie(options):
    '''
    Read the different flag values sent by the user request in 'options' and
    build a cookie string to be stored as a cookie with the user.
    
    Keyword arguments:
    options -- POST data submitted by the user while submitting a request.
    
    Return:
    String containing the cookie content.
    '''

    cookieString = ""
    
    for checkBox in ["twoNodeMode", "printNodeCount", "splitNodes"]:
        
        if checkBox in options:            
            cookieString += checkBox + ":1;"
        else:
            cookieString += checkBox + ":0;"
            
    if "overrideEdge" in options:
        cookieString += "overrideEdge:1;" + "overrideEdgeLength:" + \
                     options['overrideEdgeLength'] + ";"
    else:
        cookieString += "overrideEdge:0;overrideEdgeLength:0;"
        
    for choice in ["splitMode", "textLabel", "skipLines", "maxLines", \
                   "omitThreshold", "sourceFanOut", "eventFanOut"]:
        
        cookieString += choice + ":" + options[choice] + ";"
        
    return cookieString
        
def _readCookie(cookie):
    '''
    Read the cookie data from 'cookie' and populate the render form with
    their default values from the cookie.
    
    Keyword arguments:
    cookie -- content of the cookie from the user.
    
    Return:
    A dictionary of default values used for instantiating a render form request
    (populated with the values from the user's cookie).
    '''
    
    formData = {}
    
    cookie = cookie.split(";")

    for checkBox in cookie[:4]:
        
        checkBox = checkBox.split(":")
        
        #Explicit cast to booleans required for the form's checkboxes.
        formData[checkBox[0]] = bool(int(checkBox[1]))
    
    cookie = dict(item.split(":") for item in cookie[4:-1])
        
    formData['overrideEdgeLength'] = float(cookie['overrideEdgeLength'])
    
    formData['textLabel'] = cookie['textLabel']
    
    for intData in ['splitMode', 'skipLines', 'maxLines', 'omitThreshold', \
                    'sourceFanOut', 'eventFanOut']:
    
        formData[intData] = int(cookie[intData])
	
    formData['regExType'] = '1'
    
    return formData

def _renderGraph(dataFile, propertyFile, outputFile, afPath, rFilter, afArgs):
    '''
    Call the shell script invoking AfterGlow with the required parameters
    to render a graph. Return the exit status returned by the shell script.
    
    Keyword arguments:
    dataFile -- Path to CSV data file.
    propertyFile -- Path to the configuration file.
    outputFile -- Path to render the image to (with filename and extension).
    afPath -- Path to the afterglow shell script.
    rFilter -- Rendering filter to use with GraphViz (neato/dot/sfdp).
    afArgs -- Arguments to be sent to the shell script.
    
    Return:
    Exit code from the afterglow shell script.    
    '''
    
    dataFile = os.path.join(settings.PROJECT_PATH, '../' + dataFile)
    
    propertyFile = os.path.join(settings.PROJECT_PATH, '../' + propertyFile)
    
    outputFile = os.path.join(settings.PROJECT_PATH, '../' + outputFile)
    
    afPath = os.path.join(settings.PROJECT_PATH, '../' + afPath)
    
    filters = {'1' : 'neato', '2' : 'dot', '3' : 'sfdp'}
    
    return call(os.path.join(settings.PROJECT_PATH, "../../afterglow.sh") + " " + dataFile + " " + propertyFile + " " + 
                outputFile + " " + afPath + " " + filters[rFilter] + " " + afArgs, shell=True)

def _logglyAuth(request):
    '''
    Perform an authorization request to Loggly.com for accessing a user's 
    account.
    
    Keyword arguments:
    request -- the request object.
    
    Return:
    Redirect the user to Loggly.com's for giving access to AfterGlow.
    '''
    
    # Construct a consumer object.
    consumer = oauth.Consumer(key=settings.LOGGLY_OAUTH_CONSUMER_KEY, 
	secret=settings.LOGGLY_OAUTH_CONSUMER_SECRET)    

    request_token_url = "http://%s.loggly.com/api/oauth/request_token/" % (request.POST['logglySubdomain'])
    authorize_url = "http://%s.loggly.com/api/oauth/authorize/"	% (request.POST['logglySubdomain'])
    
    client = oauth.Client(consumer)
    
    # Change the signature method to PLAINTEXT.
    method = oauth.SignatureMethod_PLAINTEXT()
    client.set_signature_method(method)    
    
    # Request a token.
    resp, content = client.request(request_token_url, method="POST", body=urllib.urlencode({'oauth_callback': settings.LOGGLY_OAUTH_CALLBACK}))
    request_token = dict(urlparse.parse_qsl(content))    
    
    # Store the subdomain and token secret in the session.
    request.session["logglyTokenSecret"] = request_token['oauth_token_secret']
    request.session["logglySubdomain"] = request.POST['logglySubdomain']
    
    # Redirect the user to Loggly's webpage for granting/denying access.
    return redirect("%s?oauth_token=%s" % (authorize_url, request_token['oauth_token']))

def receiveCallback(request):
    '''
    Recieve and process a callback from Loggly. If the user grants access, a 
    cookie is set with the token details and the user is taken to the search
    interface. If not, an error is shown.
    
    Keyword arguments:
    request -- the request object.
    
    Return:
    A redirect to the search interface if access was granted else redirect 
    to an error page.
    '''
    
    # Process if the user has granted access to their account else throw
    # an error.
    if "oauth_callback_confirmed" in request.GET and \
       request.GET['oauth_callback_confirmed'] == 'true' and \
       "oauth_token" in request.GET and "oauth_verifier" in request.GET:
	
	consumer = oauth.Consumer(key=settings.LOGGLY_OAUTH_CONSUMER_KEY, 
		secret=settings.LOGGLY_OAUTH_CONSUMER_SECRET)	
	
	access_token_url = "http://%s.loggly.com/api/oauth/access_token/" % (request.session["logglySubdomain"])
    
	token = oauth.Token(request.GET['oauth_token'],
	    request.session['logglyTokenSecret'])
	
	token.set_verifier(request.GET['oauth_verifier'])
	client = oauth.Client(consumer, token)
	
	# Obtain an access token with its credentials.
	resp, content = client.request(access_token_url, "POST")
	access_token = dict(urlparse.parse_qsl(content))
	
	auth = True

	response = redirect('/search')   

	expiry = datetime.now() + timedelta(days = 100)
	
	# Set a cookie for 100 days with Loggly's authentication data so that
	# the user does not have to grant access again in the timeframe.
	response.set_cookie(key = "afLoggly", 
		                value = _buildLogglyCookie(access_token['oauth_token'], access_token['oauth_token_secret'], request.session["logglySubdomain"]),
		                expires = expiry)    
	
	request.session["subdomain"] = request.session["logglySubdomain"]
	request.session["key"] = access_token['oauth_token']
	request.session["secret"] = access_token['oauth_token_secret']
	
	# Redirect the user to the search page.
	return response
    
    else:
	
	# User didn't grant access.
	auth = False
	
	return render_to_response('search.html', locals(), 
	                          context_instance=RequestContext(request))
    
def revokeAccess(request):
    '''
    Revokes access to the application from Loggly for a user's account. All
    token credentials in the cookie and session are purged.
    
    Keyword arguments:
    request -- the request object.
    
    Return:
    A redirect back to the rendering request form.   
    '''
    
    response = HttpResponseRedirect('/process?r=1')
    
    # Remove the set cookie.    
    if "afLoggly" in request.COOKIES:
	
	response.delete_cookie(key = "afLoggly")
	
    # Purge any authentication data in session.
    keys = ['key', 'secret,' 'subdomain']
    
    for key in keys:
	if key in request.session:
	    request.session.pop(key)

    return response

def logglySearch(request):
    '''
    Show a search interface for the user. If the user submits this form, 
    perform a search on a user's Loggly account for data. If data is retrieved
    sucessfuly, parse it to a CSV file and attempt to render a graph. If data 
    isn't retrieved sucessfuly, notify the user of the error.
    
    Keyword arguments:
    request -- the request object.
    
    Return:
    A rendered image if the transfer and parsing was sucessful, redirect if
    there was any error.
    '''
    
    # Check if the user has appropriate credentials (has granted access to
    # Loggly) to access their data. Otherwise redirect them to the render
    # request form (so that they can grant access).
    if 'afLoggly' not in request.COOKIES \
       or 'key' not in request.session \
       or 'secret' not in request.session \
       or 'subdomain' not in request.session:
	
	    return redirect('/process')    
	
    
    auth = True
    
    if request.method == 'POST':
	
        form = logglySearchForm(request.POST)        
        
        if form.is_valid():
	    
	    	endpoint = "http://%s.loggly.com/api/search/" % (request.session['subdomain'])
	
		# Parameters to be sent to the search endpoint on the API.    
		params = "?q=%s&from=%s&until=%s&rows=%s&start=%s" % (urllib.quote(request.POST['query']), urllib.quote(request.POST['dateFrom']), urllib.quote(request.POST['dateUntil']), urllib.quote(request.POST['rows']), urllib.quote(request.POST['start']))
		
		consumer = oauth.Consumer(key=settings.LOGGLY_OAUTH_CONSUMER_KEY, 
	secret=settings.LOGGLY_OAUTH_CONSUMER_SECRET)
		
		token = oauth.Token(request.session['key'], request.session['secret'])
		client = oauth.Client(consumer, token)
		
		# Perform a search.
		response, content = client.request(endpoint + params)
	
		# Check if the response was valid.
		if response.status is 200:
		    
			content = json.loads(content)

			fileData = ""			
			
			for entry in content["data"]:
				fileData += entry["text"] + "\n"
		    
		    	# Parse the data into a CSV file and attempt the
			# render a graph with the parsed data.
			return _render(request, True, True, fileData)
			
		else:
		    
		    # Notify the user of the error from Loggly.
		    responseError = True
		    
		    responseErrorContent = content
		
    else:
	
	form = logglySearchForm()	
	    
    return render_to_response('search.html', locals(), 
	                          context_instance=RequestContext(request))

def _buildLogglyCookie(key, secret, subdomain):
    '''
    Build the contents of the cookie used to store token credentials for a
    a user's account on Loggly. Cookie content is encoded using base64.
    
    Keyword arguments:
    key -- token key.
    secret -- token secret.
    subdomain -- subdomain at which user has granted access.
    
    Return:
    String content of the cookie.
    '''
    
    contents = "%s:%s;%s:%s;%s:%s" % ("key", key, "secret", secret, "subdomain", subdomain)
    return base64.b64encode(contents)

def _readLogglyCookie(cookieData, SESSION):
    '''
    Read contents of user's cookie having Loggly access-token credentials.
    Populate the contents to session for later retrieval.
    
    Keyword arguments:
    cookieData -- contents of the cookie.
    SESSION -- the session object of the user.
    
    Return:
    String subdomain which user had granted access.
    '''
    
    cookieData = base64.b64decode(cookieData)
    cookieData = cookieData.split(";")
    
    for data in cookieData:
	
	data = data.split(":")
	SESSION[data[0]] = data[1]
	
    return SESSION['subdomain']

def galleryProcess(request):
    '''
    Process a request to save a rendered image to the gallery.
    
    Keyword arguments:
    request -- the request object.
    
    Return:
    Redirect user to the gallery is the submission was sucessful or display an
    approriate error message.
    '''
    
    if request.method == 'POST':
	
	    CAPTCHA_PUBLIC_KEY = settings.AF_RECAPTCHA_PUBLIC_KEY	
	
	    form = gallerySubmitForm(request.POST)        
	    
	    if form.is_valid():
		
		# Check if CAPTCHA response was valid.
		response = captcha.submit(  
			               request.POST.get('recaptcha_challenge_field'),  
			               request.POST.get('recaptcha_response_field'),  
			               settings.AF_RECAPTCHA_PRIVATE_KEY,  
			               request.META['REMOTE_ADDR'],)         			   
			   
		if not response.is_valid:
		    
			captchaWrong = True
			submitError = True
			requestID = request.POST['image']
			
			return render_to_response('render.html', locals(), 
					     context_instance=RequestContext(request))	
		 
		# Copy the temporary rendered image into the gallery - so that
		# it doesn't get pruned (_cleanFiles).
		staticPath = os.path.join(settings.PROJECT_PATH, "app/static/")
		
		renderedFile = staticPath + "rendered/" + request.session['requestID'] + ".gif"
		
		outputFile = staticPath + "gallery/" + request.session['requestID'] + ".gif"
		
		copyfile(renderedFile, outputFile)
		
		# Generate and save a thumbnail of this image.
		_generateThumbnail(staticPath, request.session['requestID'])
		
		# Insert the image details into the gallery database.
		form.save()
		
		return redirect('/gallery?s=1')
	    
	    else:
		
		# Validation error.		
		
		requestID = request.POST['image']
		
		submitError = True
		
		return render_to_response('render.html', locals(), 
	                          context_instance=RequestContext(request))
    else:
	return redirect('/process')
    
def _generateThumbnail(staticPath, requestID):
    '''
    Generate and save a thumbnail of the image created by request 'requestID'.
    
    Keyword arguments:
    staticPath -- absolute path to the /static directory.
    requestID -- the requestID associated with the image (those thumbnail has
    		to be created).
                
    Return:
    None.
    '''
    
    pic = open(staticPath + "gallery/" + requestID + ".gif")
    
    exportName = staticPath + "gallery_thumbs/" + requestID
    
    thumbnailer = get_thumbnailer(pic, relative_name = exportName)
    
    thumbnail = thumbnailer.generate_thumbnail({'size': (150, 150), 'crop' : 'smart'})
    
    thumbnail.image.save(staticPath + "gallery_thumbs/" + requestID + ".png")
    
def showGallery(request):
    '''
    Show an image gallery with all the rendered graphs users have submitted.
    
    Keyword arguments:
    request -- the request object.
    
    Return:
    View to display the gallery.
    '''
    
    if "s" in request.GET and request.GET["s"] == "1":
	# User is coming from a sucessful submission redirect.
	fromSubmit = True
	
    if "o" in request.GET:
	# User is trying to access another page.	
	
    	try:
		offset = int(request.GET['o'])
		
		if offset % 15 != 0:
		    raise Exception
	except:
	    	error = True
		return render_to_response('gallery.html', locals(), 
			                          context_instance=RequestContext(request))		
    else:
	
	offset = 0
	
    # Query and retrieve a range of 15 images from 'offset'.
    imageSet = Images.objects.order_by('-id')[offset : offset + 15]
    
    moreImages = False
    
    # Check if there are more images available (beyond this page).
    if Images.objects.order_by('-id')[offset - 1 + 15:15].count():
	
	moreImages = True
	nextVal = offset + 15
    
    prevVal = offset - 15
	
    return render_to_response('gallery.html', locals(), 
	                              context_instance=RequestContext(request))