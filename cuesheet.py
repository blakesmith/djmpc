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

    def num_tracks(self):
        return len(re.compile(self.cue_re['track']).findall(self.sheet))

    def parse(self):
        parsed = []
        for i in range(self.num_tracks()):
            parsed.append({}) #First append our blank dicts.
        for each_re in self.cue_re.iteritems(): #Loop through all our regexp tests
            reg = re.compile(each_re[1]).findall(self.sheet)
            if each_re[0] == 'title' or each_re[0] == 'performer': #Pop the first values, since these usually denote the overall title and performer
                reg.pop(0)
            for each_match, each_case in zip(reg, parsed): #Loop through all matches, and add each match to a corresponding dict.
                if each_re[0] == 'index':
                    index_list = []
                    for i in each_match:
                        index_list.append(int(i))
                    each_case[each_re[0]] = index_list
                elif each_re[0] == 'track':
                    each_case[each_re[0]] = int(each_match)
                else:
                    each_case[each_re[0]] = each_match
        #Done populating data from the regexp, now add extra calculated values.
        for track in parsed: #Populate the track dictionaries with their individual song length.
            track['length'] = self.calculate_song_length(track['index'])
        return parsed

    def calculate_song_length(self, index):
        return index
