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

    def client_init(self):
        """Things that should be loaded, started or run when the server first starts."""
        self.track_total_time = 0
        self.status_update()
        if not self.server_is_stopped():
            cue_control.cue_init()
            self.track_total_time = cue_control.convert_seconds_to_index(control.current_song['time'])

    def status_update(self):
        """Current statuses that are updated each iteration of the main loop."""
        try:
            control.current_status = control.client.status()
            if not self.server_is_stopped():
                self.current_song = self.client.currentsong()
                self.track_current_time = cue_control.convert_seconds_to_index(self.time_split(self.current_status['time']))
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
            self.client.seek(current_id, cue_control.convert_index_to_seconds(int_split))

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
        gathered_song_info = {}
        if cue_control.cue_parsed:
            cue_information = cue_control.cue_update()
            gathered_song_info['1'] = "[CUE Track %s.] %s - %s" % (cue_information[0], cue_information[1], cue_information[2])
        gathered_song_info['2'] = song_info.title_values()
        gathered_song_info['3'] = "random: %s repeat: %s" % (song_info.random_status(), song_info.repeat_status())
        gathered_song_info['4'] = "state: %s volume: %s" % (control.current_status['state'], control.current_status['volume'])
        if not control.server_is_stopped():
            gathered_song_info['5'] = "%s%% - bitrate: %s" % (str(song_info.song_percentage()), song_info.bitrate_status())
            if control.track_total_time:
                gathered_song_info['6'] = "%i:%i / %i:%i" % (control.track_current_time[0], control.track_current_time[1], control.track_total_time[0], control.track_total_time[1])
        return gathered_song_info

    def repeat_status(self):
        if control.current_status['repeat'] == "1":
             return "on"
        else:
             return "off"

    def random_status(self):
        if control.current_status['random'] == "1":
            return "on"
        else:
            return "off"

    def bitrate_status(self):
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
                return True
            elif os.path.exists(remote):
                self.cue_lib.open(local)
                self.cue_parsed = self.cue_lib.parse()
                return True
            else:
                return False #No cue file exists
        else:
            return True #Cuesheet has already been loaded into self.cue_parsed

    def cue_update(self):
        """Function to be run every loop to see where the song is in the current cuesheet. Return the relevant information about the current location."""
        if not control.server_is_stopped():
            if self.cue_parsed:
                current_time = float(control.current_status['time'].rsplit(":")[0])
                for i in cue_control.cue_parsed:
                    if current_time < cue_control.convert_index_to_seconds(i['index']):
                        break
                    cue_info = (i['track'], i['performer'], i['title'])
                return cue_info
            else:
                return "No cue has been loaded yet!"

class CursesControl(object):

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
        control.track_total_time = cue_control.convert_seconds_to_index(control.current_song['time'])

    def window_draw(self):
        """Handles all drawing of the actual GUI."""
        main_win = curses.newwin(200, 200, 0, 0)
        for i, j in zip(range(len(song_info.gather_song_info())), song_info.gather_song_info().itervalues()):
            main_win.addstr(i+1, 5, j)
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
    control.client_init()
    for i in song_info.gather_song_info().itervalues():
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
    control.client_init()
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
