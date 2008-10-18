#!/usr/bin/env python

import sys
import re

def do_parse(in_file, out_file):
    try:
        track_file = open(in_file, "r").read()
    except:
        print "Unable to open specified file, check the path."
    track_file_split = re.compile("(.*) `(.*)'").findall(track_file)
    if not track_file_split:
        track_file_split = re.compile("(.*) '(.*)'").findall(track_file)
    if not track_file_split:
        track_file_split = re.compile("(.*) `(.*)`").findall(track_file)
    if not track_file_split:
        print "Unable to parse the text file, are you sure it's in the right format?"
    else:
        try:
            out_file = open(out_file, "w")
        except:
            print "Unable to open output file for writing."
        out_file.write('PERFORMER ""\nTITLE ""\nFILE "" MP3\n')
        out_file.write(' TRACK 01 AUDIO\n') 
        out_file.write('   PERFORMER "Essential Mix"\n') 
        out_file.write('   TITLE "Intro"\n') 
        out_file.write('   INDEX 01 00:00:00\n') 
        for i, j in zip(track_file_split, range(len(track_file_split))):
            j = j + 2
            if j < 10:
                track_string = "0"+str(j)
            else:
                track_string = str(j)
            out_file.write(' TRACK %s AUDIO\n' % track_string) 
            out_file.write('   PERFORMER "%s"\n' % i[0]) 
            out_file.write('   TITLE "%s"\n' % i[1]) 
            out_file.write('   INDEX 01 00:00:00\n') 
        out_file.close()
                    
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "You need to specify an input file, and an output file."
    elif len(sys.argv) == 3:
        do_parse(sys.argv[1], sys.argv[2])
    else:
        print "You entered too many parameters, you only need to specify an input file."
