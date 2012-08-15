from django.shortcuts import render_to_response, redirect, HttpResponseRedirect, HttpResponse
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
    ''' Display a view for the index page. '''
    
    return render_to_response('index.html', locals(), 
                                      context_instance=RequestContext(request))

def processForm(request):
    
    if request.method == 'POST':
	
        form = renderForm(request.POST, request.FILES)        
        
        if form.is_valid():
	    
	    	if request.POST['xLogType'] == "loggly":
		    
			#Save the form detail in session.
		    
			request.session["logglyForm"] = request.POST
			
			if "afLoggly" in request.COOKIES \
			   and'key' in request.session \
			   and 'secret' in request.session \
			   and 'subdomain' in request.session:
			    
			    	return redirect('/search')
			else:
		    	
		    		return _logglyAuth(request)
	    	else:
	    	
            
            		return _render(request, request.POST['xLogType'] == "log")
    else:

        if "afConfig" in request.COOKIES: #Some saved config in history.
            
            form = renderForm(initial = _readCookie(request.COOKIES['afConfig']))
        else:
            form = renderForm(initial = {'regExType': '1'})
	    
    if "afLoggly" in request.COOKIES:
    	
    	afLogglySet = True
	afLogglySubdomain = _readLogglyCookie(request.COOKIES['afLoggly'], request.session)
	
    if "r" in request.GET and request.GET["r"] == '1':
	afLogglyRevoked = True    
	
    regExDescriptions = ""
    for e in Expressions.objects.order_by('id').all():
	regExDescriptions += str(e.id) + "[[;]]" + e.description + "[[[;]]]"
        
    return render_to_response('form.html', locals(), 
                              context_instance=RequestContext(request))

def contact(request):
    
    CAPTCHA_PUBLIC_KEY = settings.AF_RECAPTCHA_PUBLIC_KEY
    
    if request.method == 'POST':
        form = contactForm(request.POST)        
        
        if form.is_valid():
            
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
            
            mailSent = True

    else:
        form = contactForm()
    
    return render_to_response('contact.html', locals(), 
                              context_instance=RequestContext(request))

def _render(request, parsedData, loggly=False, logglyData=None):

    #Generate a session if one isn't already active.
    if hasattr(request, 'session') and hasattr(request.session, \
                                               'session_key') and \
       getattr(request.session, 'session_key') is None:
      
        request.session.create()
    
    #Generate a unique request ID hash from the session key.
    requestID = md5(request.session.session_key + 
            str(datetime.now())).hexdigest()       
    
    #Clean up old resource files (user config, user property and
    #rendered images) which are older than four hours.
    _cleanFiles()
    
    if loggly:
	POSTdata = request.session["logglyForm"]
    else:
	POSTdata = request.POST
    
    retVal = 0
    
    if parsedData:

	if loggly:
	    
	    if not logglyData:
		emptyData = True
		return render_to_response('render.html', locals(), 
				                          context_instance=RequestContext(request))			
	    
	    retVal = _parseToCsv(logglyData, requestID, POSTdata, True)  
	else:
	    retVal = _parseToCsv(request.FILES['dataFile'], requestID, POSTdata)  
          
	
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
        _writeDataFile(request.FILES['dataFile'], requestID)
    
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
	                   param)
	
	CAPTCHA_PUBLIC_KEY = settings.AF_RECAPTCHA_PUBLIC_KEY
		
	form = gallerySubmitForm(initial = {'image' : requestID})
	
	request.session['requestID'] = requestID
	
	#Construct a response.
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
    
    fileName = requestID + '.log'
    
    with open(os.path.join(settings.PROJECT_PATH, '../user_logs/') + fileName, 'wb+') as dest:

	if not loggly:	
	    for chunk in f.chunks():
	    	dest.write(chunk)
	else:
	    for line in f:
		dest.write(line)
	    
    if POSTdata['regExType'] == '1':
    	pat = re.compile(POSTdata['regEx'])
    else:
	pat = re.compile(Expressions.objects.all().get(id=POSTdata['regExChoices']).regex)
    
    with open(os.path.join(settings.PROJECT_PATH, '../user_logs_parsed/') + fileName, 'wb+') as dest:
        
        for line in open(os.path.join(settings.PROJECT_PATH, '../user_logs/') + fileName):
            match = pat.match(line)
	    
	    if not match:
		return 1
	    
	    match = match.groups()
	    
	    try:
            
            	string = match[0] + "," + match[1]   
	    
	    except IndexError:
		return 2
	    
	    try:
	    	if 'twoNodeMode' not in POSTdata: #We get the third group (column) as well.
		    string += "," + match[2]
		    
	    except IndexError:
		return 3
                
            string += "\n"
            
            dest.write(string)
	    
    return 0


def _cleanFiles():
    ''' Clean up every user-data, user-configuration and rendered image files
    which are older than 4 hours from this point. '''
    
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
    ''' Write the CSV data file present in the file-stream 'f' from the user,
    to a local file with 'requestID' as its name. '''
    
    fileName = requestID + '.csv'
    
    
    i = 0
    
    with open(os.path.join(settings.PROJECT_PATH, '../user_data/') + fileName, 'wb+') as dest:
        for chunk in f.chunks():
            dest.write(chunk)

def _writeConfigFile(data, requestID):
    ''' Write the configuration file present in the string 'data' fromt he user,
    to a local file with "requestID" as its name. '''
    
    fileName = requestID + '.property'
    
    with open(os.path.join(settings.PROJECT_PATH, '../user_config/') + fileName, 'wb') as dest:
        dest.write(data)

def _buildParameters(options):
    ''' Read the different flag values sent by the user request in 'options' and
    build parameters to be sent to AfterGlow. '''
    
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
    ''' Read the different flag values sent by the user request in 'options' and
    build a cookie string to be stored as a cookie with the user. '''

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
    ''' Read the cookie data from 'cookie' and populate the render form with
    their default values from the cookie. '''
    
    formData = {}
    
    cookie = cookie.split(";")

    for checkBox in cookie[:4]:
        
        checkBox = checkBox.split(":")
	
	print checkBox
        
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

def _renderGraph(dataFile, propertyFile, outputFile, afPath, afArgs):
    ''' Call the shell script invoking AfterGlow with the required parameters
    to render a graph. Return the exit status returned by the shell script. '''
    
    dataFile = os.path.join(settings.PROJECT_PATH, '../' + dataFile)
    
    propertyFile = os.path.join(settings.PROJECT_PATH, '../' + propertyFile)
    
    outputFile = os.path.join(settings.PROJECT_PATH, '../' + outputFile)
    
    afPath = os.path.join(settings.PROJECT_PATH, '../' + afPath)
    
    return call(os.path.join(settings.PROJECT_PATH, "../../afterglow.sh") + " " + dataFile + " " + propertyFile + " " + 
                outputFile + " " + afPath + " " + afArgs, shell=True)

def _logglyAuth(request):
    
    consumer = oauth.Consumer(key=settings.LOGGLY_OAUTH_CONSUMER_KEY, 
	secret=settings.LOGGLY_OAUTH_CONSUMER_SECRET)    

    request_token_url = "http://%s.loggly.com/api/oauth/request_token/" % (request.POST['logglySubdomain'])
    authorize_url = "http://%s.loggly.com/api/oauth/authorize/"	% (request.POST['logglySubdomain'])
    
    client = oauth.Client(consumer)
    
    method = oauth.SignatureMethod_PLAINTEXT()
    
    client.set_signature_method(method)    
    
    resp, content = client.request(request_token_url, method="POST", body=urllib.urlencode({'oauth_callback': settings.LOGGLY_OAUTH_CALLBACK}))
    request_token = dict(urlparse.parse_qsl(content))    
    
    request.session["logglyTokenSecret"] = request_token['oauth_token_secret']
    request.session["logglySubdomain"] = request.POST['logglySubdomain']
    
    return redirect("%s?oauth_token=%s" % (authorize_url, request_token['oauth_token']))

def receiveCallback(request):
    
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
	
	resp, content = client.request(access_token_url, "POST")
	access_token = dict(urlparse.parse_qsl(content))
	
	auth = True

	response = redirect('/search')   

	expiry = datetime.now() + timedelta(days = 100)
	
	response.set_cookie(key = "afLoggly", 
		                value = _buildLogglyCookie(access_token['oauth_token'], access_token['oauth_token_secret'], request.session["logglySubdomain"]),
		                expires = expiry)    
	request.session["subdomain"] = request.session["logglySubdomain"]
	request.session["key"] = access_token['oauth_token']
	request.session["secret"] = access_token['oauth_token_secret']
	
	return response
    
    else:
	
	auth = False
	
	return render_to_response('search.html', locals(), 
	                          context_instance=RequestContext(request))
    
def revokeAccess(request):
    
    response = HttpResponseRedirect('/process?r=1')
    
    if "afLoggly" in request.COOKIES:
	
	response.delete_cookie(key = "afLoggly")
	
    keys = ['key', 'secret,' 'subdomain']
    
    for key in keys:
	if key in request.session:
	    request.session.pop(key)

    return response

def logglySearch(request):
    
    if 'afLoggly' not in request.COOKIES \
       or 'key' not in request.session \
       or 'secret' not in request.session \
       or 'subdomain' not in request.session:
	
	    return redirect('/process')    
    
    auth = True
    
    if request.method == 'POST':
        form = logglySearchForm(request.POST)        
        
        if form.is_valid():
	    
	    	endpoint = "http://%s.loggly.com/api/search/"	% (request.session['subdomain'])
	    
		params = "?q=%s&from=%s&until=%s&rows=%s&start=%s" % (urllib.quote(request.POST['query']), urllib.quote(request.POST['dateFrom']), urllib.quote(request.POST['dateUntil']), urllib.quote(request.POST['rows']), urllib.quote(request.POST['start']))
		
		consumer = oauth.Consumer(key=settings.LOGGLY_OAUTH_CONSUMER_KEY, 
	secret=settings.LOGGLY_OAUTH_CONSUMER_SECRET)
		token = oauth.Token(request.session['key'], request.session['secret'])
		client = oauth.Client(consumer, token)
		response, content = client.request(endpoint + params)
	
		if response.status is 200:
			content = json.loads(content)

			fileData = ""			
			
			for entry in content["data"]:
				fileData += entry["text"] + "\n"
		    
			return _render(request, True, True, fileData)
			
		else:
		    
		    responseError = True
		    
		    responseErrorContent = content
		
	    
    else:
	form = logglySearchForm()	
	    
    return render_to_response('search.html', locals(), 
	                          context_instance=RequestContext(request))

def _buildLogglyCookie(key, secret, subdomain):
    
    contents = "%s:%s;%s:%s;%s:%s" % ("key", key, "secret", secret, "subdomain", subdomain)
    return base64.b64encode(contents)

def _readLogglyCookie(cookieData, SESSION):
    
    cookieData = base64.b64decode(cookieData)
    cookieData = cookieData.split(";")
    
    for data in cookieData:
	
	data = data.split(":")
	SESSION[data[0]] = data[1]
	
    return SESSION['subdomain']

def galleryProcess(request):
    
    if request.method == 'POST':
	
	    CAPTCHA_PUBLIC_KEY = settings.AF_RECAPTCHA_PUBLIC_KEY	
	
	    form = gallerySubmitForm(request.POST)        
	    
	    if form.is_valid():
		
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
		    
		staticPath = os.path.join(settings.PROJECT_PATH, "app/static/")
		
		renderedFile = staticPath + "rendered/" + request.session['requestID'] + ".gif"
		
		outputFile = staticPath + "gallery/" + request.session['requestID'] + ".gif"
		
		copyfile(renderedFile, outputFile)
		
		_generateThumbnail(staticPath, request.session['requestID'])
		
		form.save()
		
		return redirect('/gallery?s=1')
	    
	    else:
		
		requestID = request.POST['image']
		
		submitError = True
		
		return render_to_response('render.html', locals(), 
	                          context_instance=RequestContext(request))
    else:
	return redirect('/process')
    
def _generateThumbnail(staticPath, requestID):
    
    pic = open(staticPath + "gallery/" + requestID + ".gif")
    
    exportName = staticPath + "gallery_thumbs/" + requestID
    
    thumbnailer = get_thumbnailer(pic, relative_name = exportName)
    
    thumbnail = thumbnailer.generate_thumbnail({'size': (150, 150), 'crop' : 'smart'})
    
    thumbnail.image.save(staticPath + "gallery_thumbs/" + requestID + ".png")
    
def showGallery(request):
    
    if "s" in request.GET and request.GET["s"] == "1":
	fromSubmit = True
	
    if "o" in request.GET:
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
	
    imageSet = Images.objects.order_by('-id')[offset : offset + 15]
    
    moreImages = False
    if Images.objects.order_by('-id')[offset - 1 + 15:15].count():
	moreImages = True
	nextVal = offset + 15
    
    prevVal = offset - 15
	
	
    return render_to_response('gallery.html', locals(), 
	                              context_instance=RequestContext(request))
    