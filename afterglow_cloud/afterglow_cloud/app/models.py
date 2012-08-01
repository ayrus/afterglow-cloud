from django.db import models

class Expressions(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=300)
    regex = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name  