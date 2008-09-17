import curses, sys, traceback

class gb:
    boxrows = int(sys.argv[1])
    boxcols = boxrows
    scrn = None
    row = None
    col = None

def draw(chr):
    if gb.row == gb.boxrows-1:
        gb.scrn.addch(gb.row,gb.col,chr,curses.color_pair(1))
    else:
        gb.scrn.addch(gb.row,gb.col,chr)
    gb.scrn.refresh()
    gb.row += 1
    if gb.row == gb.boxrows:
        gb.row = 0
        gb.col += 1
        if gb.col == gb.boxcols: gb.col = 0

def restorescreen():
    curses.nocbreak()
    curses.echo()
    curses.endwin()

def main():
    gb.scrn = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    curses.init_pair(1,curses.COLOR_RED,curses.COLOR_WHITE)
    gb.scrn.clear()
    gb.row = 0
    gb.col = 0
    gb.scrn.refresh()
    while True:
        c = gb.scrn.getch()
        c = chr(c)
        if c == 'q': break
        draw(c)
    restorescreen()

if __name__ =='__main__':
    try:
        main()
    except:
        restorescreen()
        traceback.print_exc()
