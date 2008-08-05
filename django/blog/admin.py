from djblithe.blog.models import *
from django.contrib import admin

class EntryAdmin(admin.ModelAdmin):
    pass

class PageAdmin(admin.ModelAdmin):
    pass

admin.site.register(Entry, EntryAdmin)
admin.site.register(Page, PageAdmin)
