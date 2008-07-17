import os, sys, Image, shutil
from config import *

class Gallery(object):
    def __init__(self, dir=image_path):
        if isinstance(dir, int):
            self.dir = image_path
            self.dir = self.id_to_dir(dir)
        else:
            self.dir = dir
        self.image_path = image_path
        self.image_link_path = image_link_path
        self.doc_path = doc_path
        self.thumbdir = thumbdir
        self.fulldir = fulldir
        self.thumb_size = thumb_size
        self.full_size = full_size

    def id_append(self, filelist):
        """Appends a unique ID number to a list of dicts"""
        id = 1
        for file in filelist:
            file["id"] = id
            id += 1
        return filelist

    def dir_list(self):
        """Retrieves the list of directories in the root picture directory. Applies unique folder IDs based on mtime, (newest modification being the newest ID). Returns a list of dicts for each folder, sorted alphabetically."""
        from operator import itemgetter
        dirlist = []
        for file in os.listdir(self.dir):
            combined = os.path.join(self.dir, file)
            if file.startswith("."):
                pass
            else:
                if os.path.isdir(combined):
                    mtime = os.stat(combined).st_mtime
                    dirlist.append({"folder": file, "mtime": mtime})
        dirlist = sorted(dirlist, key=itemgetter("mtime"))
        dirlist = self.id_append(dirlist)
        dirlist.sort()
        return dirlist

    def file_list(self):
        """Retrieves the list of files in a directory."""
        filelist = []
        combined = os.path.join(self.doc_path, self.dir)
        try:
            for file in os.listdir(combined):
                path = os.path.join(self.doc_path, self.dir, file)
                if file.startswith("."):
                    pass
                elif os.path.isdir(path):
                    pass
                else:
                    filelist.append({"file": file})
            return filelist
        except:
            print "Unable to retrieve list of files. Is the directory readable?"

    def pic_list(self):
        """Retrieves the list of pictures in a given directory inside a designated directory. Returns a dict."""
        piclist = []
        combined = os.path.join(self.image_path, self.dir)
        try:
            for file in os.listdir(combined):
                if file.startswith("."):
                    pass
                else:
                    if file.endswith(".JPG") or file.endswith(".jpg"):
                        mtime = os.stat(combined).st_mtime
                        piclist.append({"file": file, "mtime": mtime})
            piclist = self.id_append(piclist)
            return piclist
        except:
            print "Unable to retrieve picture directory! Did you type it in right?"

    def check_dir(self, size):
        """Checks to see if a thumbnail or sized directory exists. Returns False and makes it, otherwise returns True."""
        if size == "thumbs":
            combined = os.path.join(self.image_path, self.dir, self.thumbdir)
        elif size == "fulls":
            combined = os.path.join(self.image_path, self.dir, self.fulldir)
        if not os.path.exists(combined):
            os.mkdir(combined) 
        else:
            pass

    def check_sized(self, piclist, size):
        """Checks to see if the directory of images has been resized and has a thumbnail in the .thumbs/.fulls directory. Returns an array"""
        needs_resize = []
        if size == "thumbs":
            type = self.thumbdir
        elif size == "fulls":
            type = self.fulldir
        for pic in piclist:
            file = pic.get("file")
            combined = os.path.join(self.image_path, self.dir, type, file)
            if not os.path.exists(combined):
                needs_resize.append(pic)
            else:
                pass
        return needs_resize

    def copy_img(self, piclist, size):
        """Copies all the images from the designated directory into the made thumbnail/full directory for resizing."""
        if size == "thumbs":
            type = self.thumbdir
        elif size == "fulls":
            type = self.fulldir
        try:
            for pic in piclist:
                file = pic.get("file")
                src = os.path.join(self.image_path, self.dir, file)
                dst = os.path.join(self.image_path, self.dir, type, file)
                shutil.copy(src, dst)
        except:
            print "Pictures failed to copy to the .thumbs directory, maybe it doesn't exist?"

    def resize_img(self, piclist, size):
        """Resizes all images in a given list, located in a certain dir"""
        if size == "thumbs":
            type = self.thumb_size
            target_dir = self.thumbdir
        elif size == "fulls":
            type = self.full_size
            target_dir = self.fulldir
        try:
            for pic in piclist:
                file = pic.get("file")
                src = os.path.join(self.image_path, self.dir, target_dir, file)
                img = Image.open(src)
                img.thumbnail(type, Image.ANTIALIAS)
                img.save(src, img.format)
        except:
            print "Thumbnails failed to generate!"

    def get_caption(self, file):
        """Checks to see if a caption on a certain image exists in the same directory as the image. If it does, return the text in the file, if not, return false"""
        splitter = file.rsplit(".", 1)
        src = splitter[0] + ".txt"
        combined = os.path.join(self.image_path, self.dir, src)
        if os.path.isfile(combined):
            caption = open(combined, "r")
            return caption.read()
            caption.close()
        else:
            return False

    def id_to_dir(self, dirid):
        """Takes the ID of the folder, and converts it back to the filename. This is to facilitate pretty urls."""
        dirlist = self.dir_list()
        try:
            for path in dirlist:
                if dirid == path.get("id"):
                    return path["folder"]
        except:
                print "Failed to find the gallery. Did you modify the url?"

    def id_to_img(self, dir, picid):
        """Takes the ID of the image, and converts it back to the filename. This is to facilitate pretty urls."""
        combined = os.path.join(self.image_path, self.dir, dir)
        piclist = self.pic_list()
        try:
            for path in piclist:
                if picid == path.get("id"):
                    return path["file"]
        except:
                print "Failed to find the image. Did you modify the url?"

    def do_resize(self, dir, size):
        """Processess all the base functions to generate a thumbnail or fullview page"""
        self.check_dir(size)
        check_list = self.pic_list()
        needs_resize = self.check_sized(check_list, size)
        if needs_resize:
            self.copy_img(needs_resize, size)
            self.resize_img(needs_resize, size)
        else:
            pass
        return check_list
