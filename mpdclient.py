#!/usr/bin/env python

import mpd
import cuesheet
import sys
import os
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
        current_song = self.client.currentsong()
        client_status = self.client.status()
        if self.cue_init():
            current_time = float(client_status['time'].rsplit(":")[0])
            for i in self.cue_control.cue_parsed:
                if current_time <= self.cue_control.convert_index_to_seconds(i['index']):
                    break
                cue_info = "%s - %s" % (i['performer'], i['title'])
            return cue_info
        if current_song.has_key("artist") and current_song.has_key("title"):
            return "%s - %s" % (current_song['artist'], current_song['title'])
        elif current_song.has_key("name") and current_song.has_key("title"):
            return "%s - %s" % (current_song['name'], current_song['title'])
        elif current_song.has_key("file"):
            return "%s" % (current_song['file'])
        else:
            return "Nothing playing"
        self.client_disconnect()
    
    def cue_init(self):
        current_song = self.client.currentsong()
        if not self.cue_control: #Cuesheet object not loaded
            self.cue_control = CueControl()
            if self.cue_control.cue_load(current_song['file']): #Does a cuesheet exist for the currently playing file?
                return True
            else:
                return False

    def cue_list(self):
        if self.cue_init():
            for i in self.cue_control.cue_lib.parse():
                print "%i: %s - %s at %i:%i:%i" % (i['track'], i['performer'], i['title'], i['index'][0], i['index'][1], i['index'][2])
        else:
            print "No cuesheet found for the current song"

class CueControl(object):

    def __init__(self):
        self.cue_lib = cuesheet.CueRead()
        self.cue_parsed = False
        self.music_directory = "/home/blake/.mpd/music/"
        self.cue_directory = "/home/blake/cues/"

    def convert_index_to_seconds(self, index):
        minutes = index[0] * 60
        seconds = index[1]
        miliseconds = index[2] / 100.0
        return minutes + seconds + miliseconds

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
            return False #Cuesheet has already been loaded into self.cue_parsed
        
def display_help():
    print "This is the standard help output that gets piped to stdout"

if __name__ == "__main__":
    try:
        control = MpdControl()
        control.client_connect()
    except:
        print "Unable to connect to mpd server!"
    if (len(sys.argv) == 1):
        print control.song_info()
    else:
        if sys.argv[1] == 'play': control.client.play()
        elif sys.argv[1] == 'pause': control.client.pause()
        elif sys.argv[1] == 'toggle': control.toggle()
        elif sys.argv[1] == 'cuelist': control.cue_list()
        else:
            display_help()
