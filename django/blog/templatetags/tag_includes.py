from django.template import Library
from blog.models import Page

register = Library()

def get_away_message():
    status = []
    file = open('/var/www/away2web-status', 'r')
    for line in file:
        strip = line.rstrip('\n')
        status.append(strip)
    file.close()
    context = {"away_message": status[1]}
    return context

def get_twitter_status():
    import feedparser
    import datetime
    url = "http://twitter.com/statuses/user_timeline/13113562.rss"
    twit = feedparser.parse(url)
    update = twit['entries'][0]['updated_parsed']
    update_time = datetime.datetime(update[0], update[1], update[2], update[3], update[4], update[5])
    return {"twitter_status": twit['entries'][0]['title'], "twitter_date": update_time}

def get_sidebar():
    page_cat = [
            {"name": "Main"}, 
            {"name": "Computers"},
            {"name": "Music"},
            {"name": "Contact"},
            ]
    page_list = Page.objects.all().order_by("order")
    return {"page_cat": page_cat, "page_list": page_list}

register.inclusion_tag('blog/chat.html')(get_away_message)
register.inclusion_tag('blog/twitter.html')(get_twitter_status)
register.inclusion_tag('blog/sidebar.html')(get_sidebar)
