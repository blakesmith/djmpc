import re
import os

class Cuesheet(object):
    """Main class to use when working with the library -> import cuesheet, cue = cuesheet.Cuesheet"""
    def __init__(self):
        self.cue_re = {
            'performer': 'PERFORMER \"(.*)\"',
            'title': 'TITLE \"(.*)\"',
            'track': 'TRACK (\d{1,2}) AUDIO',
            'index': 'INDEX \d{1,2} (\d{1,2}):(\d{1,2}):(\d{1,2})'
            }

    def open(self, filename):
        try:
            os.path.exists(filename)
        except:
            print "File does not exist! Check file path?"
        try:
            return open(filename).read()
        except:
            print "Cannot open file, are you sure it's readable?"

    def regcompile(self, reg, string):
        return re.compile(reg).findall(string)

    def parse(self, filename):
        self.sheet = self.open(filename)
        return self.regcompile(self.cue_re['performer'], self.sheet)
