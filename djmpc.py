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
            if control.current_status['state'] == 'play' or control.current_status['state'] == 'pause':
                return False
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
            gathered_song_info.append("%s / %s [%s%%]" % (self.cue_information[4], self.cue_information[3], int(self.cue_information[4].percentage(self.cue_information[3]))))
        gathered_song_info.append(song_info.title_values())
        gathered_song_info.append("random: %s repeat: %s" % (song_info.random_status(), song_info.repeat_status()))
        gathered_song_info.append("state: %s volume: %s" % (control.current_status['state'], control.current_status['volume']))
        if not control.server_is_stopped():
            gathered_song_info.append("bitrate: %s" % song_info.bitrate_status())
            if control.track_total_time:
                gathered_song_info.append("%s / %s [%s%%]" % (control.track_current_time, control.track_total_time, int(control.track_current_time.percentage(control.track_total_time))))
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
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_WHITE)
        self.active_gui_objects = []
        self.progress_bar = False
        self.cue_progress_bar = False
        self.body_win = False
        self.info_win = False
        self.activate_gui_objects()

    def status_check(self):
        """Things that need to be checked or updated each iteration of the GUI loop."""
        if control.track_has_changed():
            self.track_check()
        control.status_update()

    def activate_gui_objects(self):
        """Initializes all relevant GUI objects"""
        objects = []
        song_info.gather_song_info()
        self.info_win = gui.InfoWin(curses, length=7, width=self.window_width, color_pair=1, y=0, x=0)  
        objects.append(self.info_win)
        if cue_control.cue_parsed:
            self.cue_progress_bar = gui.ProgressBar(curses, length=3, width=self.window_width, color_pair=1, y=10, x=0)
            self.cue_progress_bar.update(0)
            self.progress_bar = gui.ProgressBar(curses, length=3, width=self.window_width, color_pair=3, y=7, x=0)
            self.progress_bar.update(control.track_current_time.percentage(control.track_total_time))
            self.body_win = gui.BodyWin(curses, length=self.window_length+1, width=self.window_width, color_pair=1, y=13, x=0)
            self.body_win.update(song_info.cue_information[0], cue_control.cue_parsed)
            objects.append(self.progress_bar), objects.append(self.cue_progress_bar), objects.append(self.body_win)
        elif not cue_control.cue_parsed and not control.server_is_stopped():
            self.progress_bar = gui.ProgressBar(curses, length=3, width=self.window_width, color_pair=3, y=5, x=0)
            self.progress_bar.update(control.track_current_time.percentage(control.track_total_time))
            objects.append(self.progress_bar)
        self.active_gui_objects = objects
        return objects

    def destroy_gui_objects(self):
        """Destroys all relevant GUI objects."""
        for i in self.active_gui_objects:
            i.destroy()
            i = False

    def update_gui_objects(self):
        """Updates all active GUI objects."""
        for i in self.active_gui_objects:
            if i == self.info_win:
                self.info_win.update(song_info.gather_song_info())
            elif i == self.progress_bar:
                self.progress_bar.update(control.track_current_time.percentage(control.track_total_time))
            elif i == self.cue_progress_bar:
                self.cue_progress_bar.update(song_info.cue_information[4].percentage(song_info.cue_information[3]))
            elif i == self.body_win:
                self.body_win.update(song_info.cue_information[0], cue_control.cue_parsed)
            else:
                i.update()

    def track_check(self):
        """Things that need to be checked or updated if the track is switched."""
        control.status_update()
        cue_control.cue_parsed = False #unload current cuesheet
        cue_control.cue_init() #Recheck for a new cuesheet
        control.track_total_time = cuesheet.Index(control.current_song['time'])
        self.destroy_gui_objects()
        self.active_gui_objects = self.activate_gui_objects()

    def user_input(self, char):
        """Handles all user input, and it's associated action. Returns the associated action for the input."""
        if char == ord('q'):
            return "quit"	
        if char == ord('t'):
            control.toggle()     
            return "update"
        if char == curses.KEY_RESIZE:
            return "resize"

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
        user_input = curses_control.user_input(stdscr.getch())
        curses_control.update_gui_objects()
        if user_input == "quit":
            break
        elif user_input == "resize":
            curses.resize_term(*stdscr.getmaxyx())
            curses_control.destroy_gui_objects()
            curses_control = CursesControl()
            curses_control.activate_gui_objects()
            curses_control.update_gui_objects()

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
