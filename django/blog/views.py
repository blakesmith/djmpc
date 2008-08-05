from django.shortcuts import render_to_response
from blog.models import *
from django.template import RequestContext
import math


def entry_list(request, start=0):
    """
     Variables to use with pagination in the templates:
           
           has_next: Boolean to indicate whether a 'Next page' link should be included in navigation of the page.
           has_prev: Boolean to indicate whether a 'Previous page' link should be included in navigation of the page.
           num_pages: Count how many pages we should be producing. Integer.
           page_list: Iterable dict of pages. page_num provides the page number, and href provides the clickable number variable, current_page provides a boolean that indicates whether the loaded page is the one looped in the list.
           next_num: Goes in the link for 'Next page'
           prev_num: Goes in the link for 'Previous page'
    """
    entries_per_page = 10
    page_list = []
    num_entries = Entry.objects.count() #retrieve all entries
    if not start: #User hits the front page.
        if num_entries > entries_per_page: #Check to see if all entries don't fit on the page.
            entry_list = Entry.objects.order_by("-date")[:entries_per_page] 
        else:
            entry_list = Entry.objects.order_by("-date")
        start = 0
        end = entries_per_page
    else:
        start = int(start)
        begin = start * entries_per_page
        end = begin + entries_per_page
        entry_list = Entry.objects.order_by("-date")[begin:end]
    num_pages = int(math.ceil(num_entries / float(entries_per_page)))
    for i in range(num_pages):
        if start == i:
            current_page = 1
        else:
            current_page = 0
        page_list.append({"page_num": i + 1, "href": i, "current_page": current_page})
    next_num = start + 1
    prev_num = start - 1
    if num_entries > end:
        has_next = 1
    else:
        has_next = 0
    if start == 0:
        has_prev = 0
    else:
        has_prev = 1
    next_num = start + 1
    prev_num = start - 1
    return render_to_response("blog/home.html", locals())
    
def entry_details(request, entry_id):
    entry_details = Entry.objects.filter(id=entry_id)[:1]
    return render_to_response("blog/entry_details.html", locals())
    
def page_view(request, page_name):
    page_details = Page.objects.filter(short_title=page_name.capitalize())
    return render_to_response("blog/page.html", locals())
