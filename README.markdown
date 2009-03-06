### djmpc - An ncurses mpd client with cuesheet support.


### SCREENSHOTS

![djmpc-ncurses] [djmpc-ncurses]
![djmpc-cmd] [djmpc-cmd]

### REQUIREMENTS

* Python 2.5 or greater
* ncurses
* A working version of mpd


### INSTALLATION

1. Untar the archive by running `tar xzvf djmpc-$versionnumber.tar.gz`.
2. Run `python setup.py install` to install the package into your python path.
3. A basic configuration file can be found in '/usr/share/djmpc/djmpc_config.py', Copy this file to ~/.djmpc. Edit the values in ~/.djmpc/djmpc_config.py to reflect your setup. 'music_directory' should point to the locally accessible mpd music library. If you're using djmpc with a server that's not located on the client computer, you can specify 'cue_diretory', which is where you can drop all cuesheets for tracks located on the server. Note that the client MUST have local access to the cuesheet files in some way in order to display cuesheet data.

### USAGE

djmpc has two basic modes: command line mode, and ncurses mode. 


- Command Line mode:

The command line mode has basic control over the server, most of which can also be found in another mpd client. The ones that will be most interesting are:

		% djmpc cuelist

This lists all the track and index information for the cuesheet on the currently playing track.

		% djmpc cueseek <int>

Seeks to a specific track within the cuesheet. EG - 'djmpc cueseek 24' would seek to the 24th index on the currently playing songs cuesheet.

- ncurses mode:

A display to output server data, as well as cuesheet/track information. To activate:
		
		% djmpc nc

At the moment the only thing you can do in this display is:

		't' - Toggle play/pause
		'q' - Quit the client

Other relevant commands can be seeing by typing:

		% djmpc help

### AUTHOR

djmpc is written by: 

Blake Smith <blakesmith0@gmail.com>

[djmpc-ncurses]: http://github.com/blakesmith/djmpc/raw/9218b31344d46aa9d0720732e8b77075953e2e1b/support/djmpc-ncurses.png "djmpc running in ncurses mode"
[djmpc-cmd]: http://github.com/blakesmith/djmpc/raw/9218b31344d46aa9d0720732e8b77075953e2e1b/support/djmpc-cmd.png "djmpc after executing 'djmpc cuelist'"
