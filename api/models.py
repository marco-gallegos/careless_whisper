from django.db import models

# Create your models here.
class Transcript(models.Model):
    id= models.AutoField(primary_key=True)
    rawtext= models.TextField()
    date=models.DateTimeField(auto_now_add=True)
    summary=models.TextField(null=True)
    actionables=models.TextField(null=True)