import re
import os

class CueRead(object):
    """Main class to use when working with the library -> import cuesheet, cue = cuesheet.Cuesheet"""
    def __init__(self):
        self.cue_re = {
            'performer': 'PERFORMER \"(.*)\"',
            'title': 'TITLE \"(.*)\"',
            'track': 'TRACK (\d{1,3}) AUDIO',
            'index': 'INDEX \d{1,3} (\d{1,3}):(\d{1,2}):(\d{1,2})'
            }

    def open(self, filename):
        try:
            os.path.exists(filename)
        except:
            print "File does not exist! Check file path?"
        try:
            self.sheet = open(filename).read()
        except:
            print "Cannot open file, are you sure it's readable?"

    def regcompile(self, reg, string):
        return re.compile(reg).findall(string)

    def num_tracks(self):
        return self.regcompile(self.cue_re['track'], self.sheet).__len__()

    def parse(self):
        parsed = []
        for i in range(self.num_tracks()):
            temp = {}
            temp['performer'] = self.regcompile(self.cue_re['performer'], self.sheet)[1:][i] # Performer
            temp['title'] = self.regcompile(self.cue_re['title'], self.sheet)[1:][i] # Title
            temp['track'] = self.regcompile(self.cue_re['track'], self.sheet)[i] # Track
            temp['index'] = self.regcompile(self.cue_re['index'], self.sheet)[i] # Index
            parsed.append(temp)
        return parsed

    def parse_pretty(self):
        for i in self.parse():
            print "%s: %s - %s" % (i['track'], i['performer'], i['title'])
