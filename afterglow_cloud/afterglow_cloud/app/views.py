from django.shortcuts import render_to_response, HttpResponseRedirect
from django.template import RequestContext
from afterglow_cloud.app.form import renderForm
from hashlib import md5
from datetime import datetime, timedelta
from subprocess import call
from time import time
import os

def index(request):
    
    return render_to_response('index.html')

def processForm(request):
    
    if request.method == 'POST':
        form = renderForm(request.POST, request.FILES)        
        
        if form.is_valid():
          
            ##proces
            if hasattr(request, 'session') and hasattr(request.session, \
                                                       'session_key') and \
               getattr(request.session, 'session_key') is None:
              
                request.session.create()
              
            requestID = md5(request.session.session_key + 
                    str(datetime.now())).hexdigest()       
            
            _cleanFiles()
            
            #--handle error here.
            _writeDataFile(request.FILES['dataFile'], requestID)
            
            _writeConfigFile(request.POST['propertyConfig'], requestID)
            
            param = _buildParameters(request.POST)
            
            dataFile = "user_data/" + requestID + ".csv"
            propertyFile = "user_config/" + requestID + ".property"
            outputFile = "afterglow_cloud/app/static/" + requestID + ".gif"
            afPath = "../afterglow/src/afterglow.pl"
            
            #--deal with errors
            status = _renderGraph(dataFile, propertyFile, outputFile, afPath, 
                               param)
            
            response = render_to_response('render.html', locals(), 
                                      context_instance=RequestContext(request))
            
            if("saveConfigCookie" in request.POST):
              
                expiry = datetime.now() + timedelta(days = 3)
                response.set_cookie(key = "afConfig", 
                                    value = _buildCookie(request.POST),
                                    expires = expiry)
            
            return response
    else:

        if "afConfig" in request.COOKIES: #Some saved config in history.
            
            form = renderForm(initial = _readCookie(request.COOKIES['afConfig']))
        else:
            form = renderForm()
        
    return render_to_response('form.html', locals(), 
                              context_instance=RequestContext(request))

def _cleanFiles():
  
  paths = ["afterglow_cloud/app/static/", "user_data/", "user_config/"]
  
  for path in paths:
  
    absPath = os.path.abspath(path)
    files = os.listdir(absPath)
    
    for oldFile in files:
      
        oldFilePath = os.path.join(absPath, oldFile)
        info = os.stat(oldFilePath)
      
        if(info.st_ctime < int(time() - 4*60*60)):
        
            os.unlink(oldFilePath)
  
def _writeDataFile(f, requestID):
    
    fileName = requestID + '.csv'
    
    with open('user_data/' + fileName, 'wb+') as dest: #------
        for chunk in f.chunks():
            dest.write(chunk)
            
    return 0

def _writeConfigFile(data, requestID):
    
    fileName = requestID + '.property'
    
    with open('user_config/' + fileName, 'wb') as dest: #------
        dest.write(data)
        
    return 0

def _buildParameters(options):
    
    param = ""
    
    if 'twoNodeMode' in options:
        param += "-t "
        
    if 'printNodeCount' in options:
        param += "-d "
        
    if 'omitLabelling' in options:
        param += "-a "
        
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

    cookieString = ""
    
    for checkBox in ["twoNodeMode", "printNodeCount", "omitLabelling", \
                     "splitNodes"]:
        
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
    
    formData = {}
    
    cookie = cookie.split(";")

    for checkBox in cookie[:5]:
        
        checkBox = checkBox.split(":")
        
        formData[checkBox[0]] = bool(int(checkBox[1]))
    
    cookie = dict(item.split(":") for item in cookie[5:-1])
        
    formData['overrideEdgeLength'] = float(cookie['overrideEdgeLength'])
    
    formData['textLabel'] = cookie['textLabel']
    
    for intData in ['splitMode', 'skipLines', 'maxLines', 'omitThreshold', \
                    'sourceFanOut', 'eventFanOut']:
    
        formData[intData] = int(cookie[intData])
    
    return formData

def _renderGraph(dataFile, propertyFile, outputFile, afPath, afArgs):
    
    return call("../afterglow.sh " + dataFile + " " + propertyFile + " " + 
                outputFile + " " + afPath + " " + afArgs, shell=True)