class GuiObject(object):
    """Abstract GUI object class that all other GUI objects should inherit from."""

    def __init__(self, curses, length, width, color_pair, y, x):
        self.curses = curses
        self.drawn = False
        self.window_width = width
        self.window_length = length
        self.y = y
        self.x = x
        self.color_pair = color_pair
        self.window = curses.newwin(self.window_length, self.window_width, self.y, self.x)

    def update(self):
        """Function that should be called each iteration of the GUI loop to update the information contained in the object."""
        self.window.erase()
        self.window.box()
        self.draw()
        self.window.refresh()

    def draw(self):
        """Function that does the actual drawing of relevant data to the object."""
        pass

    def destroy(self):
        """Destroy the object entirely."""
        self.window.erase()
        self.window.refresh()
        self.window = False

class InfoWin(GuiObject):
    """Top information window that displays all current server status and track information."""

    def draw(self):
        try:
            for i, j in enumerate(self.song_info):
                self.window.addstr(i, 0, j[:self.window_width])
        except:
            pass

    def update(self, song_info):
        self.song_info = song_info
        self.window.erase()
        self.draw()
        self.window.refresh()

class ProgressBar(GuiObject):
    """A percentage progress bar, used to denote song position."""

    def draw(self):
        try:
            self.bar_length = self.window_width - 1
            bar_fill_percentage = (self.percentage / 100.0) * self.bar_length   
            for i in range(int(bar_fill_percentage)):
                self.window.addstr(1, i+1, " ", self.curses.color_pair(self.color_pair))
        except:
            pass

    def update(self, percentage=0):
        self.percentage = percentage
        self.window.erase()
        self.window.box()
        self.draw()
        self.window.refresh()

class BodyWin(GuiObject):
    """General body window that can be used to display any sort extra relevant text. Used to display current cuesheet position."""

    def draw(self):
        try:
            start_position = 1
            visible_window = self.window_length-2
            while self.current_track > start_position*visible_window:
                start_position += 1
            for track, i in zip(self.cue_parsed[(start_position-1)*visible_window:start_position*visible_window], range(visible_window)):
                cue_string = "[%s] %s - %s" % (track['length'], track['performer'], track['title'])
                if track['track'] == self.current_track:
                    self.window.addstr(i+1, 1, cue_string[:self.window_width-2], self.curses.color_pair(2))
                else:
                    self.window.addstr(i+1, 1, cue_string[:self.window_width-2])
        except:
            pass

    def update(self, current_track, cue_parsed):
        self.current_track = current_track
        self.cue_parsed = cue_parsed
        self.window.erase()
        self.window.box()
        self.draw()
        self.window.refresh()

class StatusBar(GuiObject):

    def draw(self):
        self.window.addstr("djmpc")

    def update(self):
        self.window.erase()
        self.draw()
        self.window.refresh()
