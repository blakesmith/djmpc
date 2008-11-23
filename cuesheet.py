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
                    each_case[each_re[0]] = Index(index_list)
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
        sum_total_index = Index([0, 0, 0])
        i = 0
        for index in indices:
            if i == self.num_tracks() - 1: 
                break
            preadd_track_index = sum_total_index
            sum_total_index += indices[i+1] - preadd_track_index
            self.parsed[i]['length'] = sum_total_index - preadd_track_index
            i += 1

class Index(object):

    def __init__(self, value = None):
        self.value = value
        if self.value:
            if isinstance(self.value, str):
                try:
                    self.value = int(self.value)
                except:
                    raise Exception("String not a valid integer!")
            if isinstance(self.value, int):
                minutes = self.value / 60
                seconds = self.value - (minutes * 60)
                self.value = [minutes, seconds, 0]
            elif not (isinstance(self.value, list)) and (len(self.value) != 3):
                raise Exception("Index needs to be created with a list with length 3 as input: [minutes, seconds, frames], or a second integer.")


    def __sub__(self, other):
        sub_values = [self.value[0] - other[0], self.value[1] - other[1], self.value[2] - other[2]]
        if sub_values[2] < 0:
            sub_values[1] -= 1
            sub_values[2] += 75
        if sub_values[1] < 0:
            sub_values[0] -= 1
            sub_values[1] += 60
        return Index(sub_values)

    def __add__(self, other):
        added_values = [self.value[0] + other[0], self.value[1] + other[1], self.value[2] + other[2]]
        if added_values[2] >= 75:
            added_values[1] += 1
            added_values[2] -= 75
        if added_values[1] >= 60:
            added_values[0] += 1
            added_values[1] -= 60
        return Index(added_values)

    def __lt__(self, other):
        if (Index(self.value) - other).to_seconds("float") < 0:
            return True
        else:
            return False

    def __gt__(self, other):
        if (Index(self.value) - other).to_seconds("float") > 0:
            return True
        else:
            return False

    def __eq__(self, other):
        if (Index(self.value) - other).to_seconds("float") == 0:
            return True
        else:
            return False

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
            return "%s:%s" % (self.value[0], self.add_zeroes(self.value[1]))

    def to_seconds(self, type="int"):
        """Assumes a list or tuple as input of 3 ints. Returns the sum of all three in seconds."""
        minutes = self.value[0] * 60
        seconds = self.value[1]
        frames = self.value[2] / 75.0
        if type == "int":
            return int(minutes + seconds + frames)
        if type == "float":
            return minutes + seconds + frames

    def add_zeroes(self, in_seconds):
        """Take a second integer and add the zeroes to make it look normal."""
        if in_seconds < 10:
            return "0%i" % in_seconds
        else:
            return str(in_seconds)

    def percentage(self, other):
        first_upper = Index(self.value).to_seconds('float')
        second_upper = other.to_seconds('float')
        return (first_upper / second_upper) * 100

