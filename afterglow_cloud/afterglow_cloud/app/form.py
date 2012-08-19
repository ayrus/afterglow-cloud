from django import forms
from afterglow_cloud.app.models import Expressions, Images
import re

class renderForm(forms.Form):
    '''
    Generate an instance of a form used to input the file and different
    configurations required for rendering a graph by AfterGlow Cloud. 
    '''
    
    #The CSV data file submitted by the user.
    dataFile = forms.FileField(required=False)
    
    #Flag: '-t' Configuration flag for "Two node mode".
    twoNodeMode = forms.BooleanField(required=False)
    
    #Flag: '-d' To print node count for each node.
    printNodeCount = forms.BooleanField(required=False)
    
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
    
    #Regular expression field (custom) for the RegEx used as the parser.
    regEx = forms.CharField(required=False)
    
    #Dropdown of RegEx types.
    regExTypes = (('1', 'Custom',), ('2', 'Predefined',))
    regExType = forms.ChoiceField(widget=forms.RadioSelect, choices=regExTypes)
    
    #A dropdown of predefined RegExs saved by different users imported from the
    #database.
    regExChoices = forms.ModelChoiceField(queryset = Expressions.objects.all(),\
                                          empty_label = None)
    
    #Boolean - Whether to save the regular expression to the database.
    saveRegEx = forms.BooleanField(required=False, initial=False)
    
    #Name of the regular expression to be saved.
    saveRegExName = forms.CharField(required=False)
    
    #Description of the regular expression.
    saveRegExDescription = forms.CharField(widget=forms.Textarea, required=False)
    
    #Subdomain field for Loggly.com's API access.
    logglySubdomain = forms.CharField(required=False)
    
    def clean_textLabel(self):
        '''
        Validate the textLabel input to see if it has a valid HEX colour
        format. Raise an error if not.
        '''
        
        textLabel = self.cleaned_data['textLabel']
        
        pat = re.compile('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$');
        if not pat.match(textLabel):
            raise forms.ValidationError("Not valid HEX colour format")
        
        return textLabel
    
    def clean_saveRegExName(self):
        '''
        Validate the saveRegExName field if the user chooses to save the custom
        expression they input. Validation constraint is: A string length of at
        least two characters. Raise an error if not.
        '''
        
        if self.cleaned_data['saveRegEx']:
            
            data = self.cleaned_data['saveRegExName']
            
            if len(data) <= 2:
                raise forms.ValidationError("Should be at least two characters")
            
    def clean_saveRegExDescription(self):
        '''
        Validate the saveRegDescription field if the user chooses to save the 
        custom expression they input. Validation constraint is: A string length
        of at least ten characters. Raise an error if not.        
        '''
        
        if self.cleaned_data['saveRegEx']:
            
            data = self.cleaned_data['saveRegExDescription']
            
            if len(data) <= 10:
                raise forms.ValidationError("Should be at least ten characters")
            
    

class contactForm(forms.Form):
    '''
    Generate an instance of contact form used at /contact.
    '''
    
    userName = forms.CharField(min_length = 2, max_length = 20)
    
    userEmail = forms.EmailField()
    
    subjects = [("feedback", "Feedback"), ("bug", "Report a bug"), 
                ("feature", "Suggest a new feature"), 
                ("general", "Everything else")]
    userSubject = forms.ChoiceField(subjects)
    
    userMessage = forms.CharField(widget=forms.Textarea)
    
class logglySearchForm(forms.Form):
    '''
    Generate an instance of the search form required to search and import logs
    from a Loggly.com account once authenticated.
    '''
    
    query = forms.CharField(min_length = 1)

    dateFrom = forms.CharField(initial = "NOW-24HOURS")
    
    dateUntil = forms.CharField(initial = "NOW")
    
    rows = forms.IntegerField(initial = 10)
    
    start = forms.IntegerField(initial = 0)
    
    
class gallerySubmitForm(forms.ModelForm):
    '''
    Generate an instance of a form used to submit a rendered image to the
    gallery. This form is linked to the class-model 'Images' in models.py.
    '''
    
    class Meta:
        
        model = Images
        
        #'image' field is hidden and is prepopulated by the view.
        widgets = {
                    'image': forms.HiddenInput(),
                }        