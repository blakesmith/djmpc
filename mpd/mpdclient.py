#!/usr/bin/env python

import mpd
import cuesheet
import sys
import os
import math
import curses
import time
from config import *


class MpdControl(object):
    """Main object to control mpd through the mpd library. Methods here are what interact directly with the server."""
    
    def __init__(self):
        self.client = mpd.MPDClient()

    def status_update(self):
        control.current_status = control.client.status()
        if not control.server_is_stopped():
            control.current_song = control.client.currentsong()
            control.track_current_time = cue_control.convert_seconds_to_index(self.time_split(self.current_status['time']))

    def client_connect(self):
        """Initialize the connection to the server."""
        try:
            self.client.connect(mpd_address, mpd_port)
        except:
            return "Unable to connect to server, is the mpd backend running?"

    def client_disconnect(self):
        """Disconnect function."""
        try:
            self.client.disconnect()
        except:
            return "Can't disconnect, are you sure you're connected?"

    def toggle(self):
        """If the server is playing, pause it. If the server is paused, play it."""
        try:
            if self.client.status()['state'] == "play":
                self.client.pause()
            else:
                self.client.play()
        except:
            return "You aren't connected, you must connect first."

    def song_info(self):
        """Gathers all the current song info to be displayed as a dictionary. If a cuesheet exists, add that as well."""
        song_info = {}
        if self.current_status['repeat'] == "1":
            client_repeat = "on"
        else:
            client_repeat = "off"
        if self.current_status['random'] == "1":
            client_random = "on"
        else:
            client_random = "off"
        song_info['state'] = "state: %s volume: %s" % (self.current_status['state'], self.current_status['volume'])
        song_info['random'] = "random: %s repeat: %s" % (client_random, client_repeat)
        if self.server_is_stopped():
           song_info['song'] = "Nothing playing."
           song_info['percentage'] = ""
           return song_info
        song_info['percentage'] = "%s%% - bitrate: %s" % (str(self.song_percentage()), self.current_status['bitrate'])
        if self.cue_init():
            current_time = float(self.current_status['time'].rsplit(":")[0])
            for i in cue_control.cue_parsed:
                if current_time < cue_control.convert_index_to_seconds(i['index']):
                    break
                cue_info = "[CUE Track %s.] %s - %s" % (i['track'], i['performer'], i['title'])
            song_info['cue'] = cue_info
        if self.current_song.has_key("artist") and self.current_song.has_key("title"):
            song_info['song'] = "%s - %s" % (self.current_song['artist'], self.current_song['title'])
        elif self.current_song.has_key("name") and self.current_song.has_key("title"):
            song_info['song'] = "%s - %s" % (self.current_song['name'], self.current_song['title'])
        elif self.current_song.has_key("file"):
            song_info['song'] = "%s" % (self.current_song['file'])
        return song_info

    def cue_init(self):
        """Checks to see if a cuesheet has been loaded into memory already. If no, checks to see if the current track has a cuesheet visible in the filesystem. If so returns True. Otherwise returns false."""
        if cue_control.cue_parsed: #Is something loaded into memory?
            return True
        if cue_control.cue_load(self.current_song['file']): #Does a cuesheet exist for the currently playing file, if so, is it loaded?
            return True
        else:
            return False

    def cue_list(self):
        """Pretty printout of the current cuesheet. Invoked from the command line using 'cuelist'."""
        control.status_update()
        if self.cue_init():
            for i in cue_control.cue_lib.parse():
                print "%i: %s - %s at %i:%i:%i" % (i['track'], i['performer'], i['title'], i['index'][0], i['index'][1], i['index'][2])
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
            elif len(string_split) > 2:
                print "Malformed seek time. Try 'minutes:seconds' or just 'seconds'"
        if isinstance(seek_string, int):
            self.client.seek(current_id, seek_string)
        else:
            self.client.seek(current_id, CueControl().convert_index_to_seconds(int_split))

    def cue_seek(self, track_string):
        """Seeks to a track number within a cue."""
        self.status_update()
        current_id = self.current_song['id']
        if self.cue_init():
            try:
                track_int = int(track_string)
            except:
                print "Not a valid track number!"
            for i in cue_control.cue_parsed:
                if i['track'] == int(track_int):
                    self.client.seek(current_id, cue_control.convert_index_to_seconds(i['index'])) 
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

    def song_percentage(self):
        """Calculate and return the percentage of current track."""
        time_status = self.current_status['time']
        current_time = float(time_status.rsplit(":")[0])
        total_time = float(time_status.rsplit(":")[1])
        if total_time > 0:
            return int((current_time / total_time) * 100)
        else:
            return 0

    def track_has_changed(self):
        """See if the playing track has ended and another has begun."""
        if not self.server_is_stopped():
            if control.client.currentsong()['file'] == control.current_song['file']:
                return False
            else:
                return True

    def server_is_stopped(self):
        """Polls the server to see if it's stopped. If it is, return True, otherwise return False."""
        if control.current_status['state'] == 'stop':
            return True
        else:
            return False

class CueControl(object):
    """Object to control the functions associated with cuesheet reading."""

    def __init__(self):
        self.cue_lib = cuesheet.CueRead()
        self.cue_parsed = False
        self.music_directory = music_directory
        self.cue_directory = cue_directory

    def convert_index_to_seconds(self, index):
        """Assumes a list or tuple as input of 3 ints. Returns the sum of all three in seconds."""
        minutes = index[0] * 60
        seconds = index[1]
        miliseconds = math.ceil(index[2] / 100.0)
        return int(minutes + seconds + miliseconds)

    def convert_seconds_to_index(self, in_seconds):
        """Takes total seconds and converts it to an index with type list."""
        index = []
        in_seconds = int(in_seconds)
        minutes = in_seconds / 60
        seconds = int(((in_seconds / 60.0) - minutes) * 60)
        index.append(minutes)
        index.append(seconds)
        index.append(0)
        return index

    def cue_load(self, path):
        """Handles the actual file handling of opening and storing the contents of the cuesheet in memory."""
        if not self.cue_parsed: # Has a cuesheet been loaded into memory?
            if path.endswith("mp3"):
                path = "%s%s" % (path.rstrip("mp3"), "cue")
                local = os.path.join(self.music_directory, path)
                remote = os.path.join(self.cue_directory, path)
            if os.path.exists(local):
                self.cue_lib.open(local)
                self.cue_parsed = self.cue_lib.parse()
                return True
            elif os.path.exists(remote):
                self.cue_lib.open(local)
                self.cue_parsed = self.cue_lib.parse()
                return True
            else:
                return False #No cue file exists
        else:
            return True #Cuesheet has already been loaded into self.cue_parsed

class CursesControl(object):

    def status_check(self):
        """Things that need to be checked or updated each iteration of the GUI loop."""
        if control.track_has_changed():
            self.track_check()
        control.status_update()
    
    def track_check(self):
        """Things that need to be checked or updated if the track is switched."""
        control.status_update()
        cue_control.cue_parsed = False #unload cuesheet
        control.track_total_time = cue_control.convert_seconds_to_index(control.current_song['time'])

    def window_draw(self):
        """Handles all drawing of the actual GUI."""
        main_win = curses.newwin(200, 200, 0, 0)
        if control.song_info().has_key('cue'):
            main_win.addstr(1, 5, control.song_info()['cue'])
        main_win.addstr(2, 5, control.song_info()['song'])
        main_win.addstr(3, 5, control.song_info()['random'])
        main_win.addstr(4, 5, control.song_info()['state'])
        main_win.addstr(5, 5, control.song_info()['percentage'])
        main_win.addstr(6, 5, "%i:%i / %i:%i" % (control.track_current_time[0], control.track_current_time[1], control.track_total_time[0], control.track_total_time[1]))
        main_win.refresh()

    def user_input(self, char):
        """Handles all user input, and it's associated action. Returns the associated action for the input."""
        if char == ord('q'):
            return "quit"
        if char == ord('t'):
            control.toggle()     
            return "update"

def display_song_info():
    """Pretty output of song_info()."""
    control.status_update()
    for i in control.song_info().itervalues():
        print i

def display_help():
    """Invoked when user has malformed input or sends '--help'."""
    print "This is the standard help output that gets piped to stdout"

def curses_gui(stdscr):
    """Master function for all curses control."""
    curses_control = CursesControl()
    stdscr.refresh()
    curses.curs_set(0)
    curses.halfdelay(1)
    control.status_update()
    control.track_total_time = cue_control.convert_seconds_to_index(control.current_song['time'])
    while True:
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
        control.client_connect()
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
