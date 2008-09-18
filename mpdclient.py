#!/usr/bin/env python

import mpd
import cuesheet
import sys
import os

class MpdControl(object):
    
    def __init__(self):
        self.client = mpd.MPDClient()

    def client_connect(self, address, port):
        """Initialize the connection to the server."""
        try:
            self.client.connect(address, port)
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
        status = self.client.currentsong()
        if status.has_key("artist") and status.has_key("title"):
            print "%s - %s" % (status['artist'], status['title'])
        elif status.has_key("file"):
            print "%s" % (status['file'])
        else:
            print "Nothing playing"
        self.client_disconnect()
        
class CueControl(object):

    def __init__(self):
        self.cue = cuesheet.CueRead()
        self.music_directory = "/home/blake/.mpd/music"

    def convert_index_to_seconds(self, index):
        minutes = index[0] * 60
        seconds = index[1]
        miliseconds = index[2] / 100.0
        return minutes + seconds + miliseconds
        
def display_help():
    print "This is the standard help output that gets piped to stdout"

if __name__ == "__main__":
    try:
        control = MpdControl()
        control.client_connect("localhost", 6600)
    except:
        print "Unable to connect to mpd server!"
    if (len(sys.argv) == 1):
        control.song_info()
    else:
        if sys.argv[1] == 'play': control.client.play()
        elif sys.argv[1] == 'pause': control.client.pause()
        elif sys.argv[1] == 'toggle': control.toggle()
        else:
            display_help()
