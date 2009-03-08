# djmpc (ncurses mpd client)
# (c) Blake Smith
# Project homepage: http://github.com/blakesmith/djmpc/tree/master

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import curses

class GuiObject(object):
    """Abstract GUI object class that all other GUI objects should inherit from."""

    def set_parameters(self, songinfo, length, width, color_pair, y, x):
        self.song_info = songinfo
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
            for i, j in enumerate(self.song_lines):
                self.window.addstr(i, 0, j[:self.window_width])
        except:
            pass

    def update(self):
        self.song_lines = self.song_info.gather_song_info()
        self.window.erase()
        self.draw()
        self.window.refresh()

class ProgressBar(GuiObject):
    """A percentage progress bar, used to denote song position."""

    def __init__(self, type):
        if type == 's': #Normal progress bar
            self.percentage_updater = lambda: self.song_info.current_track.current_time.percentage(self.song_info.current_track.total_time)
        if type == 'c': #Cuesheet progress bar
            self.percentage_updater = lambda: self.song_info.cue_information[4].percentage(self.song_info.cue_information[3])

    def draw(self):
        try:
            self.bar_length = self.window_width - 1
            bar_fill_percentage = (self.percentage / 100.0) * self.bar_length   
            for i in range(int(bar_fill_percentage)):
                self.window.addstr(1, i+1, " ", curses.color_pair(self.color_pair))
        except:
            pass

    def update(self):
        self.percentage = self.percentage_updater()
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
                    self.window.addstr(i+1, 1, cue_string[:self.window_width-2], curses.color_pair(2))
                else:
                    self.window.addstr(i+1, 1, cue_string[:self.window_width-2])
        except:
            pass

    def update(self):
        self.current_track = self.song_info.cue_information[0]
        self.cue_parsed = self.song_info.current_track.cuesheet.get_cuesheet()
        self.window.erase()
        self.window.box()
        self.draw()
        self.window.refresh()

class StatusBar(GuiObject):

    def __init__(self):
        self.default_message = "djmpc"
        self.message = self.default_message

    def draw(self):
        self.window.addstr(self.message)

    def update(self):
        self.window.erase()
        self.draw()
        self.window.refresh()

    def write(self, message, type=None):
        if type == None:
            prefix = ""
        elif type == 'c':
            prefix = "Command: "
        elif type == 'm':
            prefix = "Message: "
        elif type == 'e':
            prefix = "Error: "
        self.message = prefix + message

    def write_default(self):
        self.message = self.default_message
