from cuesheet import Index

class Track(object):

    def __init__(self, current_song):
        self.current_song = current_song
        self.title = self._get_title()
        self.artist = self._get_artist()
        self.total_time = self._get_total_time()
        self.update_current_time()
        self.cue_parsed = False

    def _get_artist(self):
        """Depending on what ID3 information is available, print the relevant artist name."""
        if self.current_song.has_key("artist"):
            return self.current_song['artist']
        elif self.current_song.has_key("name"):
            return self.current_song['name']
        elif self.current_song.has_key("file"):
            return self.current_song['file']
        else:
            return ""

    def _get_title(self):
        if self.current_song.has_key("title"):
            return self.current_song['title']
        else:
            return ""

    def _get_total_time(self):
        return Index(self.current_song['time'])

    def update_current_time(self, time_value="0:0"):
        """Takes a string input in the form "34:123", outputs the first number as an integer"""
        self.current_time = Index(time_value.rsplit(":")[0])

    def get_track_titles(self):
        if self.title:
            return "%s - %s" % (self.artist, self.title)
        else:
            return "%s" % self.artist
