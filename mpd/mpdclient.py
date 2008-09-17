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
        except:
            return "You aren't connected, you must connect first."

    def song_info(self):
        status = self.client.currentsong()
        if status.has_key("artist") and status.has_key("title"):
            print "%s - %s" % (status['artist'], status['title'])
        else:
            print "%s" % (status['file'])
        
def display_help():
    print "This is the standard help output that gets piped to stdout"

if __name__ == "__main__":
    if (len(sys.argv) == 1):
        control = MpdControl()
        control.client_connect("localhost", 6600)
        control.song_info()
    else:
        display_help()

