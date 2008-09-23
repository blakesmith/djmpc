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
    
    def __init__(self):
        self.client = mpd.MPDClient()
        self.cue_control = False

    def client_connect(self):
        """Initialize the connection to the server."""
        try:
            self.client.connect(mpd_address, mpd_port)
        except:
            return "Unable to connect to server, is the mpd backend running?"

    def client_disconnect(self):
        try:
            self.client.disconnect()
        except:
            return "Can't disconnect, are you sure you're connected?"

    def toggle(self):
        try:
            if self.client.status()['state'] == "play":
                self.client.pause()
            else:
                self.client.play()
            self.client_disconnect()
        except:
            return "You aren't connected, you must connect first."

    def song_info(self):
        song_info = {}
        current_song = self.client.currentsong()
        client_status = self.client.status()
        if client_status['repeat'] == "1":
            client_repeat = "on"
        else:
            client_repeat = "off"
        if client_status['random'] == "1":
            client_random = "on"
        else:
            client_random = "off"
        song_info['state'] = "state: %s bitrate: %s volume: %s" % (client_status['state'], client_status['bitrate'], client_status['volume'])
        song_info['random'] = "random: %s repeat: %s" % (client_random, client_repeat)
        if self.cue_init():
            current_time = float(client_status['time'].rsplit(":")[0])
            for i in self.cue_control.cue_parsed:
                if current_time < self.cue_control.convert_index_to_seconds(i['index']):
                    break
                cue_info = "[CUE Track %s.] %s - %s" % (i['track'], i['performer'], i['title'])
            song_info['cue'] = cue_info
        if current_song.has_key("artist") and current_song.has_key("title"):
            song_info['song'] = "%s - %s" % (current_song['artist'], current_song['title'])
        elif current_song.has_key("name") and current_song.has_key("title"):
            song_info['song'] = "%s - %s" % (current_song['name'], current_song['title'])
        elif current_song.has_key("file"):
            song_info['song'] = "%s" % (current_song['file'])
        else:
            print "Nothing playing"
        return song_info

        self.client_disconnect()
    
    def cue_init(self):
        current_song = self.client.currentsong()
        if not self.cue_control: #Cuesheet object not loaded
            self.cue_control = CueControl()
            if self.cue_control.cue_load(current_song['file']): #Does a cuesheet exist for the currently playing file, if so, is it loaded?
                return True
            else:
                return False
        else:
            return False

    def cue_list(self):
        if self.cue_init():
            for i in self.cue_control.cue_lib.parse():
                print "%i: %s - %s at %i:%i:%i" % (i['track'], i['performer'], i['title'], i['index'][0], i['index'][1], i['index'][2])
        else:
            print "No cuesheet found for the current song"

    def seek(self, seek_string):
        current_id = self.client.currentsong()['id']
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
        current_id = self.client.currentsong()['id']
        if self.cue_init():
            try:
                track_int = int(track_string)
            except:
                print "Not a valid track number!"
            for i in self.cue_control.cue_parsed:
                if i['track'] == int(track_int):
                    self.client.seek(current_id, self.cue_control.convert_index_to_seconds(i['index'])) #Add one so we actually hit the track we seek to.
                    display_song_info()
                    break

    def random(self):
        try:
            if self.client.status()['random'] == "1":
                self.client.random(0)
            else:
                self.client.random(1)
            self.client_disconnect()
        except:
            return "You aren't connected, you must connect first."

    def repeat(self):
        try:
            if self.client.status()['repeat'] == "1":
                self.client.repeat(0)
            else:
                self.client.repeat(1)
            self.client_disconnect()
        except:
            return "You aren't connected, you must connect first."
        

class CueControl(object):

    def __init__(self):
        self.cue_lib = cuesheet.CueRead()
        self.cue_parsed = False
        self.music_directory = "/home/blake/.mpd/music/"
        self.cue_directory = "/home/blake/cues/"

    def convert_index_to_seconds(self, index):
        minutes = index[0] * 60
        seconds = index[1]
        miliseconds = math.ceil(index[2] / 100.0)
        return int(minutes + seconds + miliseconds)

    def cue_load(self, path):
        if not self.cue_parsed: # Has a cuesheet been loaded into memory?
            path = "%s%s" % (path.rstrip(".mp3"), ".cue")
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
        
def display_song_info():
    for i in control.song_info().itervalues():
        print i

def display_help():
    print "This is the standard help output that gets piped to stdout"

def curses_gui(stdscr):
    stdscr.refresh()
    while True:
        main_win = curses.newwin(200, 200, 0, 0)
        if control.song_info().has_key('cue'):
            main_win.addstr(1, 5, control.song_info()['cue'])
        main_win.addstr(2, 5, control.song_info()['song'])
        main_win.addstr(3, 5, control.song_info()['random'])
        main_win.addstr(4, 5, control.song_info()['state'])
       # if char == 'q':
       #     break
        main_win.refresh()
        time.sleep(.5)




if __name__ == "__main__":
    try:
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
        elif sys.argv[1] == 'seek': control.seek(sys.argv[2])
        elif sys.argv[1] == 'cueseek': control.cue_seek(sys.argv[2])
        else:
            display_help()
