from django.urls import path,re_path
from Blog.views import *
urlpatterns = [
    path('addbl/',addblog),
    re_path('^$',index),
    re_path('blogs/(\d+)',blogs),
    path('bloglist/',blogslist)
]
