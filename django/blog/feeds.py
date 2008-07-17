from django.contrib.syndication.feeds import Feed
from django.contrib.comments.models import FreeComment
from djblithe.blog.models import Entry

class LatestEntries(Feed):
    title_template = 'feeds/title.html'
    description_template = 'feeds/description.html'

    title = "Blithe's Beat Box - Djblithe.com"
    link = "/"
    description = "The musings of Blake Smith (blithe)"

    def items(self):
        return Entry.objects.order_by('-date')[:5]

class LatestComments(Feed):
    title_template = 'feeds/comment_title.html'
    description_template = 'feeds/comment_description.html'

    title = "Recent comments from Blithe's Beat Box - djblithe.com"
    link = "/"
    description = "Recent user comments from Blithe's Beat Box"

    def items(self):
        return FreeComment.objects.order_by('-submit_date')[:15]
