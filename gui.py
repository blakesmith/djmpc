class ProgressBar(object):

    def __init__(self, curses, song_info, width, y, x):
        self.curses = curses
        self.song_info = song_info
        self.drawn = False
        self.window_width = width
        self.window_length = 3
        self.bar_length = width - 1
        self.y = y
        self.x = x
        self.window = curses.newwin(self.window_length, self.window_width, self.y, self.x)

    def draw(self):
        bar_fill_percentage = (self.song_info.song_percentage() / 100.0) * self.bar_length   
        for i in range(int(bar_fill_percentage)):
            self.window.addstr(1, i+1, " ", self.curses.color_pair(1))

    def update(self):
        self.window.erase()
        self.window.box()
        self.draw()
        self.window.refresh()
