from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField

class Sort(models.Model):
    sort = models.CharField(max_length=64)

class BlogArticle(models.Model):
    title = models.CharField(max_length=128)
    author = models.CharField(max_length=32)
    body = RichTextUploadingField()
    classify = models.ForeignKey(Sort,on_delete=True)
    time = models.DateTimeField(auto_now=True)

# Create your models here.
