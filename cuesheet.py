import re
import os
import math

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
        self.parsed = []
        for i in range(self.num_tracks()):
            self.parsed.append({}) #First append our blank dicts.
        for each_re in self.cue_re.iteritems(): #Loop through all our regexp tests
            reg = re.compile(each_re[1]).findall(self.sheet)
            if each_re[0] == 'title' or each_re[0] == 'performer': #Pop the first values, since these usually denote the overall title and performer
                reg.pop(0)
            for each_match, each_case in zip(reg, self.parsed): #Loop through all matches, and add each match to a corresponding dict.
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
        indices = []
        for track in self.parsed:
            indices.append(track['index'])
        self.calculate_song_length(indices) #Populate the track dictionaries with their individual song length.
        return self.parsed

    def calculate_song_length(self, indices):
        """Input a list of indecis, Populate the parsed data with track lengths."""
        sum_track_seconds = 0
        i = 0
        for index in indices:
            if i == self.num_tracks() - 1: 
                break
            preadd_track_seconds = sum_track_seconds
            sum_track_seconds += self.convert_index_to_seconds(indices[i+1]) - preadd_track_seconds
            self.parsed[i]['length'] = self.convert_seconds_to_index(sum_track_seconds - preadd_track_seconds)
            i += 1

    def convert_index_to_seconds(self, index):
        """Assumes a list or tuple as input of 3 ints. Returns the sum of all three in seconds."""
        minutes = index[0] * 60
        seconds = index[1]
        miliseconds = math.ceil(index[2] / 100.0)
        return int(minutes + seconds + miliseconds)

    def convert_seconds_to_index(self, in_seconds):
        """Takes total seconds and converts it to an index with type list."""
        in_seconds = int(in_seconds)
        minutes = in_seconds / 60
        seconds = in_seconds - (minutes * 60)
        return [minutes, seconds, 0]

class Index(object):

    def __init__(self, value = None):
        self.value = value
        if self.value:
            if not isinstance(self.value, list):
                raise Exception("Index needs to be created with a list with length 3 as input: [minutes, seconds, frames]")
            if len(self.value) != 3:
                raise Exception("Index needs to be length 3: [minutes, seconds, frames]")

    def __sub__(self, other):
        sub_value = self.value
        for i in range(3)[1:]:
            if (sub_value[i] - other[i]) < 0:
                sub_value[i] += 60
                sub_value[i-1] -= 1
        return self([sub_value[0] - other[0], sub_value[1] - other[1], sub_value[2] - other[2]])

    def __add__(self, other):
        sub_value = self.value
        for i in range(3)[1:]:
            if i == 2: 
                test_amount = 75
            else: 
                test_amount = 60
            if (sub_value[i] + other[i]) > test_amount:
                sub_value[i] -= test_amount
                sub_value[i-1] += 1
        return self([sub_value[0] + other[0], sub_value[1] + other[1], sub_value[2] + other[2]])

    def __getitem__(self, index):
        return self.value[index]
    
    def __repr__(self):
        if not self.value:
            return "[]" 
        else:
            return "[%s, %s, %s]" % (self.value[0], self.value[1], self.value[2])

    def __str__(self):
        if not self.value:
            return "00:00:00" 
        else:
            return "%s:%s:%s" % (self.value[0], self.add_zeroes(self.value[1]), self.add_zeroes(self.value[2]))

    def to_seconds(self):
        """Assumes a list or tuple as input of 3 ints. Returns the sum of all three in seconds."""
        minutes = self.value[0] * 60
        seconds = self.value[1]
        miliseconds = math.ceil(self.value[2] / 100.0)
        return int(minutes + seconds + miliseconds)

    def add_zeroes(self, in_seconds):
        """Take a second integer and add the zeroes to make it look normal."""
        if in_seconds < 10:
            return "0%i" % in_seconds
        else:
            return str(in_seconds)
