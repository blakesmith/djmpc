from django.shortcuts import render_to_response
from blog.models import *
from django.template import RequestContext


def entry_list(request):
    entry_list = Entry.objects.order_by("-date")
    return render_to_response("blog/home.html", locals())
    
def entry_details(request, entry_id):
    entry_details = Entry.objects.filter(id=entry_id)[:1]
    return render_to_response("blog/entry_details.html", locals())
    
def page_view(request, page_name):
    page_details = Page.objects.filter(short_title=page_name)
    return render_to_response("blog/page.html", locals())
