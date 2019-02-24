from django.shortcuts import render_to_response,render,HttpResponseRedirect
from Blog.models import *

def index(request):
    blogsright = BlogArticle.objects.all()[::-1][:7]
    blogsleft = BlogArticle.objects.all()[:7]
    myblogs = BlogArticle.objects.all()[::-1]
    return render(request,'blog/index.html',locals())

def addblog(request):
    blogsright = BlogArticle.objects.all()[::-1][:7]
    blogsleft = BlogArticle.objects.all()[:7]
    if request.method == 'POST' and request.POST:
        ab = BlogArticle()
        ab.title = request.POST.get('title')
        ab.author = request.POST.get('name')
        ab.body = request.POST.get('body')
        classify = request.POST.get('classify')
        ab.classify = Sort.objects.get(id=classify)
        ab.save()
    return render(request,'blog/addblog.html',locals())

def blogs(request,num):
    blogsright = BlogArticle.objects.all()[::-1][:7]
    blogsleft = BlogArticle.objects.all()[:7]
    num = int(num)
    myblog = BlogArticle.objects.filter(id = num).first()
    return render(request, 'blog/blog.html', locals())


def blogslist(request):
    blogsright = BlogArticle.objects.all()[::-1][:7]
    blogsleft = BlogArticle.objects.all()[:7]
    myblogs = BlogArticle.objects.all()[::-1]
    return render(request, 'blog/bloglist.html',  locals())