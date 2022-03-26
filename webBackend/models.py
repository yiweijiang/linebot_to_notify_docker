from django.db import models

# Create your models here.

class Ptt_News(models.Model):
    TITLE = models.TextField()
    BOARD = models.TextField()
    URL = models.URLField()
    AUTHOR = models.TextField()
    NRECS = models.IntegerField()
    C_TIME = models.DateTimeField(auto_now_add=True)