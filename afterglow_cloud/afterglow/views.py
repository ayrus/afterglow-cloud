from django.shortcuts import render_to_response, HttpResponseRedirect
from django.template import RequestContext
from afterglow.form import renderForm

def index(request):
    
    return render_to_response('index.html')

def processForm(request):
    
    if request.method == 'POST':
        form = renderForm(request.POST, request.FILES)        
        
        if form.is_valid():
            ##process
            return HttpResponseRedirect('/contact/thanks/')
    else:
        form = renderForm()
        
    return render_to_response('form.html', locals(), 
                              context_instance=RequestContext(request))