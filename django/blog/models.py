from django.db import models
from comment_utils.moderation import CommentModerator, moderator

class Tag(models.Model):
    name = models.CharField(max_length=15)
    description = models.CharField(max_length=40)

    def __str__(self):
        return self.name

    class Admin:
        pass

class Entry(models.Model):
    title = models.CharField(max_length=50)
    summary = models.TextField()
    author = models.CharField(max_length=30)
    date = models.DateTimeField(auto_now_add=True)
    edit = models.BooleanField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    url = models.CharField(blank=True, max_length=100)
    enable_comments = models.BooleanField()
    public = models.BooleanField(null=True)
    content = models.TextField()

    def get_absolute_url(self):
        return "http://djblithe.com/entry/%i" % self.id
    
    def __str__(self):
        return self.title

    class Admin:
        pass

    class EntryModerator(CommentModerator):
        akismet = True
        enable_field = 'enable_comments'
        auto_moderate_field = 'date'

#moderator.register(Entry, EntryModerator)

class Page(models.Model):
    title = models.CharField(max_length=50)
    short_title = models.CharField(max_length=15)
    summary = models.TextField()
    author = models.CharField(max_length=30)
    date = models.DateTimeField(auto_now_add=True)
    edit = models.BooleanField(null=True, blank=True)
    category = models.CharField(max_length=15)
    url = models.CharField(blank=True, max_length=100)
    enable_comments = models.BooleanField()
    public = models.BooleanField(null=True)
    content = models.TextField()
    order = models.IntegerField()

    def __str__(self):
        return self.title

    class Admin:
        pass

    def get_absolute_url(self):
        return "/page/%s" % self.short_title.lower()
