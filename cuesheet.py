import re
import os

class CueRead(object):
    """Main class to use when reading a cuesheet."""
    def __init__(self):
        self.cue_re = {
            'track': 'TRACK (\d{1,3}) AUDIO',
            'performer': 'PERFORMER \"(.*)\"',
            'title': 'TITLE \"(.*)\"',
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
        return len(self.regcompile(self.cue_re['track'], self.sheet))

    def parse(self):
        parsed = []
        for i in range(self.num_tracks()):
            parsed.append({}) #First append our blank dicts.
        for each_re in self.cue_re.iteritems():
            reg = self.regcompile(each_re[1], self.sheet)
            if each_re[0] == 'title' or each_re[0] == 'performer': #Pop the first values, since these usually denote the overall title and performer
                reg.pop(0)
            for each_match, each_case in zip(reg, parsed):
                if each_re[0] == 'index':
                    index_list = []
                    for i in each_match:
                        index_list.append(int(i))
                    each_case[each_re[0]] = index_list
                else:
                    each_case[each_re[0]] = each_match
        return parsed
