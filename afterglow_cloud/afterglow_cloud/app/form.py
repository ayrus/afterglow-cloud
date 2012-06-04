from django import forms
import re

class renderForm(forms.Form):
    ''' Generate an instance of a form used to input the data file and different
    configurations required for rendering a graph by AfterGlow Cloud. '''
    
    #The CSV data file submitted by the user.
    dataFile = forms.FileField()
    
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
    
    propertyConfig = forms.CharField(widget=forms.Textarea)
    
    def clean_textLabel(self):
        ''' Validate the textLabel input to see if it has a valid HEX colour
        format. Raise an error if not. '''
        
        textLabel = self.cleaned_data['textLabel']
        
        pat = re.compile('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$');
        if not pat.match(textLabel):
            raise forms.ValidationError("Not valid HEX colour format");
        
        return textLabel
    
    def clean_dataFile(self):
        ''' Validate the uploaded data file to see if its MIME type is
        "text/csv" (as only CSV files are supported). If not raise an error. '''
        
        dataFile = self.cleaned_data['dataFile']
        
        if dataFile.content_type not in ["text/csv"]:
            raise forms.ValidationError("Filetype has to be CSV.");
        
        return dataFile