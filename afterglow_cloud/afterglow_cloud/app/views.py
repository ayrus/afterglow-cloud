from django.shortcuts import render_to_response, HttpResponseRedirect
from django.template import RequestContext
from afterglow_cloud.app.form import renderForm
from hashlib import md5
from datetime import datetime
from subprocess import call

def index(request):
    
    return render_to_response('index.html')

def processForm(request):
    
    if request.method == 'POST':
        form = renderForm(request.POST, request.FILES)        
        
        if form.is_valid():
            ##proces
            
            requestID = md5(request.session.session_key + 
                    str(datetime.now())).hexdigest()       
            
            #--prune older than <4 hours files (to be added).
            
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
            
            return render_to_response('render.html', locals(), 
                                      context_instance=RequestContext(request))
    else:
        form = renderForm()
        
    return render_to_response('form.html', locals(), 
                              context_instance=RequestContext(request))

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
        
    #param += "-x "

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

def _renderGraph(dataFile, propertyFile, outputFile, afPath, afArgs):
    
    return call("../afterglow.sh " + dataFile + " " + propertyFile + " " + 
                outputFile + " " + afPath + " " + afArgs, shell=True)