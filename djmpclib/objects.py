from cuesheet import Index

MAIN_LOOP_CYCLE_TIME = 2

class Track(object):

    def __init__(self, current_song):
        """Track object should be initialized with the value from MPDClient().currentsong() passed to it for analysis."""
        self.cuesheet = False
        self.current_song = current_song
        self.title = self._get_title()
        self.artist = self._get_artist()
        self.total_time = self._get_total_time()
        self.update_current_time()
        if "id" in current_song: self.id = current_song['id']

    def _get_artist(self):
        """Depending on what ID3 or cuesheet information is available, print the relevant artist name."""
        if self.has_cuesheet():
            return self.cuesheet.performer
        if "artist" in self.current_song:
            return self.current_song['artist']
        elif "name" in self.current_song:
            return self.current_song['name']
        elif "file" in self.current_song:
            return self.current_song['file']
        else:
            return "Nothing is playing."

    def _get_title(self):
        """Depending on what ID3 or cuesheet information is available, print the relevant track name."""
        if self.has_cuesheet():
            return self.cuesheet.title
        if "title" in self.current_song:
            return self.current_song['title']
        else:
            return ""

    def _get_total_time(self):
        """Return the total track time."""
        if "time" in self.current_song:
            return Index(self.current_song['time'])
        else:
            return Index(0)

    def update_current_time(self, time_value="0:0"):
        """Takes a string input in the form "34:123", outputs the first number as an integer"""
        try:
            self.current_time = Index(time_value.rsplit(":")[0])
        except:
            self.current_time = Index(time_value)

    def get_track_titles(self):
        """Display the relevant artist and track names."""
        if self.title:
            return "%s - %s" % (self.artist, self.title)
        else:
            return "%s" % self.artist

    def has_cuesheet(self):
        """Does the current track have a cuesheet?"""
        if self.cuesheet:
            return True
        else:
            return False

class EventFactory(object):

    def __init__(self):
        self.active_event_timers = []

    def new(self, callback, seconds=3):
        """Function to add a new timed event (callback) EG - 'event_factory.new(lambda: control.toggle())'. Defaults to a 3 second timer."""
        self.active_event_timers.append(EventTimer(callback, seconds))

    def update_all(self):
        """Updates all active event timers. Executes the callback function if time is up."""
        if not self.active_event_timers:
            return False
        else:
            for timer in self.active_event_timers:
                timer.update()
                if timer.timeleft <= 0:
                    timer.callback()
                    self.active_event_timers.remove(timer)

class EventTimer(object):

    def __init__(self, callback_function=None, seconds=3):
        self.timeleft = seconds * (10 / MAIN_LOOP_CYCLE_TIME)
        self.callback_function = callback_function

    def update(self):
        self.timeleft -= MAIN_LOOP_CYCLE_TIME

    def callback(self):
        if self.callback_function:
            self.callback_function()

