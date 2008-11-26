class GuiObject(object):

    def __init__(self, curses, length, width, color_pair, y, x):
        self.curses = curses
        self.drawn = False
        self.window_width = width
        self.window_length = length
        self.y = y
        self.x = x
        self.color_pair = color_pair
        self.window = curses.newwin(self.window_length, self.window_width, self.y, self.x)

    def update(self):
        self.window.erase()
        self.window.box()
        self.draw()
        self.window.refresh()

    def destroy(self):
        self.window.erase()
        self.window.refresh()
        self.window = False


class ProgressBar(GuiObject):

    def draw(self):
        self.bar_length = self.window_width - 1
        bar_fill_percentage = (self.percentage / 100.0) * self.bar_length   
        for i in range(int(bar_fill_percentage)):
            self.window.addstr(1, i+1, " ", self.curses.color_pair(self.color_pair))

    def update(self, percentage=0):
        self.percentage = percentage
        self.window.erase()
        self.window.box()
        self.draw()
        self.window.refresh()

class BodyWin(GuiObject):

    def draw(self):
        start_position = 1
        while self.current_track > start_position*self.window_length:
            start_position += 1
        for track, i in zip(self.cue_parsed[(start_position-1)*self.window_length:start_position*self.window_length], range(self.window_length-2)):
            cue_string = "[%s] %s - %s" % (track['length'], track['performer'], track['title'])
            if track['track'] == self.current_track:
                self.window.addstr(i+1, 1, cue_string[:self.window_width-2], self.curses.color_pair(2))
            else:
                self.window.addstr(i+1, 1, cue_string[:self.window_width-2])

    def update(self, current_track, cue_parsed):
        self.current_track = current_track
        self.cue_parsed = cue_parsed
        self.window.erase()
        self.window.box()
        self.draw()
        self.window.refresh()
