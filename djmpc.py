#!/usr/bin/env python

import mpd
import cuesheet
import gui
import sys
import os
import math
import curses
import time
import signal
from config import *

MAIN_LOOP_CYCLE_TIME = 2

class MpdControl(object):
    """Main object to control mpd through the mpd library. Methods here are what interact directly with the server."""
    
    def __init__(self):
        self.client = mpd.MPDClient()

    def client_init(self):
        """Things that should be loaded, started or run when the client first starts."""
        self.track_total_time = 0
        self.status_update()
        if not self.server_is_stopped():
            cue_control.cue_init()
            self.track_total_time = cuesheet.Index(self.current_song['time'])

    def status_update(self):
        """Current statuses that are updated each iteration of the main loop."""
        try:
            control.current_status = control.client.status()
            if not self.server_is_stopped():
                self.current_song = self.client.currentsong()
                self.track_current_time = cuesheet.Index(self.time_split(self.current_status['time']))
            return True
        except:
            return False

    def client_connect(self):
        """Initialize the connection to the server."""
        try:
            self.client.connect(mpd_address, mpd_port)
            return True
        except:
            return False

    def client_disconnect(self):
        """Disconnect function."""
        try:
            self.client.disconnect()
        except:
            return "Can't disconnect, are you sure you're connected?"

    def client_reconnect(self):
        while not self.status_update():
            try:
                control.client_disconnect()
                control.client_connect()
            except:
                control.client_connect()

    def toggle(self):
        """If the server is playing, pause it. If the server is paused, play it."""
        try:
            if self.client.status()['state'] == "play":
                self.client.pause()
            else:
                self.client.play()
        except:
            return "You aren't connected, you must connect first."

    def cue_list(self):
        """Pretty printout of the current cuesheet. Invoked from the command line using 'cuelist'."""
        self.client_init()
        if cue_control.cue_init():
            for i in cue_control.cue_parsed:
                print "[%s] %i: %s - %s at %s" % (i['length'], i['track'], i['performer'], i['title'], i['index'])
        else:
            print "No cuesheet found for the current song"

    def seek(self, seek_string):
        """First tries to see if the input was able to be converted to an int. If that fails, try to seek using a time formated string
        (eg. '23:34'). If that fails, see if the input from the command line is properly formed. If it was able to convert to an int, 
        seek to that position."""
        self.status_update()
        current_id = self.current_song['id']
        try:
            seek_string = int(seek_string)
        except:
            string_split = seek_string.rsplit(":")
            if len(string_split) == 2:
                string_split.append(0)
                int_split = []
                for i in string_split:
                    int_split.append(int(i))
                int_split = cuesheet.Index(int_split)
            elif len(string_split) > 2:
                print "Malformed seek time. Try 'minutes:seconds' or just 'seconds'"
        if isinstance(seek_string, int):
            self.client.seek(current_id, seek_string)
        else:
            self.client.seek(current_id, int_split.to_seconds())

    def cue_seek(self, track_string):
        """Seeks to a track number within a cue."""
        self.client_init()
        current_id = self.current_song['id']
        if cue_control.cue_init():
            try:
                track_int = int(track_string)
            except:
                print "Not a valid track number!"
            for i in cue_control.cue_parsed:
                if i['track'] == int(track_int):
                    self.client.seek(current_id, i['index'].to_seconds()) 
                    display_song_info()
                    break

    def time_split(self, in_time):
        """Takes a string input in the form "34:123", outputs the first number as an integer"""
        out_time = in_time.rsplit(":")[0]
        return out_time

    def random(self):
        """Enable or disable random."""
        try:
            if self.client.status()['random'] == "1":
                self.client.random(0)
            else:
                self.client.random(1)
            self.client_disconnect()
        except:
            return "You aren't connected, you must connect first."

    def repeat(self):
        """Enable or disable repeat."""
        try:
            if self.client.status()['repeat'] == "1":
                self.client.repeat(0)
            else:
                self.client.repeat(1)
            self.client_disconnect()
        except:
            return "You aren't connected, you must connect first."

    def setvol(self, vol):
        """Wrapper to set the volume on the server."""
        try:
            vol = int(vol)
            if vol < 0 or vol > 100:
                print "Outside a valid volume range!"
            else:
                self.client.setvol(vol)
        except: 
            print "Not a valid volume range!"

    def track_has_changed(self):
        """See if the playing track has ended and another has begun."""
        if self.track_has_started_or_stopped():
            return True
        elif not self.server_is_stopped():
            try:
                if control.client.currentsong()['file'] == control.current_song['file']:
                    return False
                else:
                    return True
            except:
                control.client_reconnect() #Server has died

    def track_has_started_or_stopped(self):
        """See if the user goes from the 'stop' state to the 'play' state, or visa-versa."""
        try:
            if control.current_status['state'] == control.client.status()['state']:
                return False
            else:
                return True
        except:
            control.client_reconnect() #Server has died.

    def server_is_stopped(self):
        """Polls the server to see if it's stopped. If it is, return True, otherwise return False."""
        if control.current_status['state'] == 'stop':
            return True
        else:
            return False

class SongInfo(object):
    """Object to control all functions associated with song information."""

    def gather_song_info(self):
        """Gathers all the current song info to be displayed as a dictionary. If a cuesheet exists, add that as well."""
        gathered_song_info = []
        if cue_control.cue_parsed:
            self.cue_information = cue_control.cue_update()
            gathered_song_info.append("[CUE Track %s.] %s - %s" % (self.cue_information[0], self.cue_information[1], self.cue_information[2]))
            gathered_song_info.append("%s / %s" % (self.cue_information[4], self.cue_information[3]))
        gathered_song_info.append(song_info.title_values())
        gathered_song_info.append("random: %s repeat: %s" % (song_info.random_status(), song_info.repeat_status()))
        gathered_song_info.append("state: %s volume: %s" % (control.current_status['state'], control.current_status['volume']))
        if not control.server_is_stopped():
            gathered_song_info.append("bitrate: %s" % song_info.bitrate_status())
            if control.track_total_time:
                gathered_song_info.append("%s / %s [%s%%]" % (control.track_current_time, control.track_total_time, str(song_info.song_percentage())))
        return gathered_song_info

    def repeat_status(self):
        """Is repeat enabled?"""
        if control.current_status['repeat'] == "1":
             return "on"
        else:
             return "off"

    def random_status(self):
        """Is random enabled?"""
        if control.current_status['random'] == "1":
            return "on"
        else:
            return "off"

    def bitrate_status(self):
        """Poll for current bitrate."""
        if not control.server_is_stopped():
            return control.current_status['bitrate']
        else:
            return 0

    def title_values(self):
        """Depending on what ID3 information is available, print the relevant artist name and title."""
        if control.server_is_stopped():
            return "Nothing is playing."
        if control.current_song.has_key("artist") and control.current_song.has_key("title"):
            return "%s - %s" % (control.current_song['artist'], control.current_song['title'])
        elif control.current_song.has_key("name") and control.current_song.has_key("title"):
            return "%s - %s" % (control.current_song['name'], control.current_song['title'])
        elif control.current_song.has_key("file"):
            return "%s" % (control.current_song['file'])

    def song_percentage(self):
        """Calculate and return the percentage of current track."""
        if not control.server_is_stopped():
            time_status = control.current_status['time']
            current_time = float(time_status.rsplit(":")[0])
            total_time = float(time_status.rsplit(":")[1])
            if total_time > 0:
                return int((current_time / total_time) * 100)
            else:
                return 0
        else:
            return 0

class CueControl(object):
    """Object to control the functions associated with cuesheet reading."""

    def __init__(self):
        self.cue_lib = cuesheet.CueRead()
        self.cue_parsed = False
        self.music_directory = music_directory
        self.cue_directory = cue_directory

    def cue_init(self):
        """Checks to see if a cuesheet has been loaded into memory already. If no, checks to see if the current track has a cuesheet visible in the filesystem. If so returns True. Otherwise returns false."""
        if not control.server_is_stopped():
            if self.cue_parsed: #Is something loaded into memory?
                return True
            if self.cue_load(control.current_song['file']): #Does a cuesheet exist for the currently playing file, if so, is it loaded?
                return True
            else:
                return False

    def cue_load(self, path):
        """Handles the actual file handling of opening and storing the contents of the cuesheet in memory."""
        if not self.cue_parsed: # Has a cuesheet been loaded into memory?
            path = os.path.splitext(path)[0] + ".cue"
            local = os.path.join(self.music_directory, path)
            remote = os.path.join(self.cue_directory, path)
            if os.path.exists(local):
                self.cue_lib.open(local)
                self.cue_parsed = self.cue_lib.parse()
                self.append_last_length()
                return True
            elif os.path.exists(remote):
                self.cue_lib.open(local)
                self.cue_parsed = self.cue_lib.parse()
                self.append_last_length()
                return True
            else:
                return False #No cue file exists
        else:
            return True #Cuesheet has already been loaded into self.cue_parsed

    def cue_update(self):
        """Function to be run every loop to see where the song is in the current cuesheet. Return the relevant information about the current location."""
        if not control.server_is_stopped():
            if self.cue_parsed:
                for i in cue_control.cue_parsed:
                    current_index = i['index']
                    if control.track_current_time < current_index:
                        break
                    self.current_track_time = control.track_current_time - current_index
                    cue_info = (i['track'], i['performer'], i['title'], i['length'], self.current_track_time)
                return cue_info
            else:
                return "No cue has been loaded yet!"

    def append_last_length(self):
        """Since cuesheet.py can't provide the length of the last track, deduce it from the length of the song, and append it to the parsed cuesheet."""
        num_tracks = self.cue_lib.num_tracks()
        track_time = int(control.current_song['time'])
        last_index = self.cue_parsed[num_tracks - 1]['index'].to_seconds()
        self.cue_parsed[num_tracks - 1]['length'] = cuesheet.Index(track_time - last_index)

class CursesControl(object):

    def __init__(self):
        self.window_width = curses.COLS
        self.window_length = curses.LINES - 14
        curses.curs_set(0)
        curses.halfdelay(MAIN_LOOP_CYCLE_TIME)
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        signal.signal(signal.SIGWINCH, signal_handler)
        self.info_win = curses.newwin(8, 200, 0, 0)
        self.progress_bar = gui.ProgressBar(curses, song_info, self.window_width, 1, 7, 0)
        self.progress_bar.update()
        self.body_win = curses.newwin(curses.LINES - 12, self.window_width, 12, 0)
        self.body_win.box()

    def status_check(self):
        """Things that need to be checked or updated each iteration of the GUI loop."""
        if control.track_has_changed():
            self.track_check()
        control.status_update()
    
    def track_check(self):
        """Things that need to be checked or updated if the track is switched."""
        control.status_update()
        cue_control.cue_parsed = False #unload current cuesheet
        cue_control.cue_init() #Recheck for a new cuesheet
        control.track_total_time = cuesheet.Index(control.current_song['time'])

    def window_draw(self):
        """Handles all drawing of the actual GUI."""
        self.info_win.erase()
        for i, j in zip(range(len(song_info.gather_song_info())), song_info.gather_song_info()):
            self.info_win.addstr(i, 0, j)
        self.body_win.erase()
        self.body_win.box()
        self.draw_cue_list()
        self.info_win.refresh()
        self.progress_bar.update()
        self.body_win.refresh()

    def user_input(self, char):
        """Handles all user input, and it's associated action. Returns the associated action for the input."""
        if char == ord('q'):
            return "quit"
        if char == ord('t'):
            control.toggle()     
            return "update"

    def draw_cue_list(self):
        if cue_control.cue_parsed:
            start_position = 1
            while song_info.cue_information[0] > start_position*self.window_length:
                start_position += 1
            for track, i in zip(cue_control.cue_parsed[(start_position-1)*self.window_length:start_position*self.window_length], range(self.window_length)):
                cue_string = "[%s] %s - %s" % (track['length'], track['performer'], track['title'])
                if track['track'] == song_info.cue_information[0]:
                    self.body_win.addstr(i+1, 1, cue_string[:self.window_width-2], curses.color_pair(2))
                else:
                    self.body_win.addstr(i+1, 1, cue_string[:self.window_width-2])
        elif control.server_is_stopped():
            self.body_win.addstr(self.window_length / 2, 1, "Nothing is playing.")
        else:
            self.body_win.addstr(self.window_length / 2, 1, "No cuesheet for the current track.")

def signal_handler(n, frame):
    curses_control = CursesControl()

def display_song_info():
    """Pretty output of gather_song_info()."""
    control.client_init()
    for i in song_info.gather_song_info():
        print i

def display_help():
    """Invoked when user has malformed input or sends '--help'."""
    print "This is the standard help output that gets piped to stdout"

def curses_gui(stdscr):
    """Master function for all curses control."""
    control.client_init()
    curses_control = CursesControl()
    while True:
        stdscr.refresh()
        curses_control.status_check()
        curses_control.window_draw()
        user_input = curses_control.user_input(stdscr.getch())
        if user_input == "quit":
            break
        elif user_input == "update":
            curses_control.window_draw()

if __name__ == "__main__":
    try:
        cue_control = CueControl()
        control = MpdControl()
        song_info = SongInfo()
        while not control.client_connect():
            time.sleep(1)
    except:
        print "Unable to connect to mpd server!"
    if (len(sys.argv) == 1):
        display_song_info()
    else:
        if sys.argv[1] == 'play': control.client.play()
        elif sys.argv[1] == 'pause': control.client.pause()
        elif sys.argv[1] == 'toggle': control.toggle()
        elif sys.argv[1] == 'nc': curses.wrapper(curses_gui)
        elif sys.argv[1] == 'cuelist': control.cue_list()
        elif sys.argv[1] == 'update': control.client.update()
        elif sys.argv[1] == 'random': control.random()
        elif sys.argv[1] == 'repeat': control.repeat()
        elif sys.argv[1] == 'volume': control.setvol(sys.argv[2])
        elif sys.argv[1] == 'seek': control.seek(sys.argv[2])
        elif sys.argv[1] == 'cueseek': control.cue_seek(sys.argv[2])
        else:
            display_help()
