from django import forms
from afterglow_cloud.app.models import Expressions
import re

class renderForm(forms.Form):
    ''' Generate an instance of a form used to input the data file and different
    configurations required for rendering a graph by AfterGlow Cloud. '''
    
    #The CSV data file submitted by the user.
    dataFile = forms.FileField(required=False)
    
    #Flag: '-t' Configuration flag for "Two node mode".
    twoNodeMode = forms.BooleanField(required=False)
    
    #Flag: '-d' To print node count for each node.
    printNodeCount = forms.BooleanField(required=False)
    
    #Flag: '-a' Turn off any labelling.
    omitLabelling = forms.BooleanField(required=False)
    
    #Flag: '-s' Split subject and object nodes.
    splitNodes = forms.BooleanField(required=False)
    
    #Flag: '-p' Split predicate node options.
    splitModeChoices = [(0, "Only one predicate node"), 
                        (1, "One predicate node per unique subject node"), 
                        (2, "One predicate node per unique target node"),
                        (3, "One predicate node per unique source/target node")]
    splitMode = forms.ChoiceField(splitModeChoices)
    
    #Flag: 'e' Render with 'overrideEdgeLength' length.
    overrideEdge = forms.BooleanField(required=False)
    overrideEdgeLength = forms.DecimalField(min_value = 0, decimal_places = 2, 
                                            initial=0)
    
    #Flag: '-x' Colour for the text labels used in the graph. Feild is validated
    #by the method clean_textLabel() below.
    textLabel = forms.CharField(min_length = 7, max_length = 7, 
                                initial="#000000")
    
    #Flag: '-b' Number of lines to skip reading. 
    skipLines = forms.IntegerField(min_value = 0, initial=0)

    #Flag: '-l' Maximum number of lines to read.
    maxLines = forms.IntegerField(min_value = 1, max_value = 999999, 
                                  initial=999999)
    
    #Flag: '-o' Minimum count for a node to be displayed.
    omitThreshold = forms.IntegerField(initial=0)
    
    #Flag: '-f' Source fan out threshold - Filter nodes on the number of edges
    #originating from source nodes.
    sourceFanOut = forms.IntegerField(initial=0)
    
    #Flag: '-f' Event fan out threshold - Filter nodes on the number of edges
    #originating from event nodes (trivially true only for three node graphs). 
    eventFanOut = forms.IntegerField(initial=0)
    
    #The contents of the property file; eventually written out.
    propertyConfig = forms.CharField(widget=forms.HiddenInput, required=False)
    
    #Boolean - Whether to save the settings as a configuration cookie.
    saveConfigCookie = forms.BooleanField(required=False, initial=True)
    
    #---------------------------------------------------------------
    regEx = forms.CharField(required=False)
    
    regExTypes = (('1', 'Custom',), ('2', 'Predefined',))
    
    regExType = forms.ChoiceField(widget=forms.RadioSelect, choices=regExTypes)
        
    regExChoices = forms.ModelChoiceField(queryset = Expressions.objects.all(),\
                                          empty_label = None)
    
    saveRegEx = forms.BooleanField(required=False, initial=False)
    
    saveRegExName = forms.CharField(required=False)
    
    saveRegExDescription = forms.CharField(widget=forms.Textarea, required=False)
    
    logglySubdomain = forms.CharField(required=False)
    
    def clean_textLabel(self):
        ''' Validate the textLabel input to see if it has a valid HEX colour
        format. Raise an error if not. '''
        
        textLabel = self.cleaned_data['textLabel']
        
        pat = re.compile('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$');
        if not pat.match(textLabel):
            raise forms.ValidationError("Not valid HEX colour format")
        
        return textLabel
    
    def clean_saveRegExName(self):
        
        if self.cleaned_data['saveRegEx']:
            
            data = self.cleaned_data['saveRegExName']
            
            if len(data) <= 2:
                raise forms.ValidationError("Should be at least two characters")
            
    def clean_saveRegExDescription(self):
        
        if self.cleaned_data['saveRegEx']:
            
            data = self.cleaned_data['saveRegExDescription']
            
            if len(data) <= 10:
                raise forms.ValidationError("Should be at least ten characters")
            
    

class contactForm(forms.Form):
    '''  '''
    
    #The CSV data file submitted by the user.
    userName = forms.CharField(min_length = 2, max_length = 20)
    
    userEmail = forms.EmailField()
    
    subjects = [("feedback", "Feedback"), ("bug", "Report a bug"), 
                ("feature", "Suggest a new feature"), 
                ("general", "Everything else")]
    userSubject = forms.ChoiceField(subjects)
    
    userMessage = forms.CharField(widget=forms.Textarea)
    
class logglySearchForm(forms.Form):
    
    query = forms.CharField(min_length = 1)

    dateFrom = forms.CharField(initial = "NOW-24HOURS")
    
    dateUntil = forms.CharField(initial = "NOW")
    
    rows = forms.IntegerField(initial = 10)
    
    start = forms.IntegerField(initial = 0)
    
    