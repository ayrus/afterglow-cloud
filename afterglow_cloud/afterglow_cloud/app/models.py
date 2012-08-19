from django.db import models

class Expressions(models.Model):
    '''
    Model instance to store regular expressions used by the parser.
    '''
    
    name = models.CharField(max_length=50)
    
    description = models.CharField(max_length=300)
    
    regex = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name
    
class Images(models.Model):
    '''
    Model instace to images in the gallery. 
    '''
    
    name = models.CharField(max_length=25)
    
    description = models.TextField(max_length=300)
    
    author = models.CharField(blank=True, max_length=50)
    
    image = models.CharField(max_length = 40)
    
    def __unicode__(self):
        return self.name