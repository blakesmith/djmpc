# Create your views here.
from django.shortcuts import render_to_response
from functions import *


def get_dir_list(request):
    gal = Gallery()
    dir_list = gal.dir_list()
    return render_to_response("gallery/root.html", locals())

def get_thumbs(request, id):
    gal = Gallery(int(id))
    piclist = []
    check_list = gal.do_resize(gal.dir, "thumbs")
    for pic in check_list:
        hardlink = pic.get("file")
        url = os.path.join(gal.image_link_path, gal.dir, gal.thumbdir, hardlink)
        piclist.append({"url": url, "id": pic.get("id")})
    return render_to_response("gallery/thumb_list.html", locals())

def get_fulls(request, id, file):
    gal = Gallery(int(id))
    piclist = []
    file = gal.id_to_img(gal.dir, int(file))
    check_list = gal.do_resize(gal.dir, "fulls")
    caption = gal.get_caption(file)
    url = os.path.join(gal.image_link_path, gal.dir, gal.fulldir, file)
    original = os.path.join(gal.image_link_path, gal.dir, file)
    dir_image = os.path.join(gal.image_path, gal.dir, file)
    if os.path.isfile(dir_image):
        image_exists = True
    return render_to_response("gallery/full.html", locals())
