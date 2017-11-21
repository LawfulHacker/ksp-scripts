import curses
from curses import wrapper

def main(stdscr):
    # Clear screen
    stdscr.clear()

    begin_x = 20; begin_y = 7
    height = 5; width = 40
    win = curses.newwin(height, width, begin_y, begin_x)

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    win.addstr("Pretty text", curses.color_pair(1))
    win.refresh()
    win.getkey()

    # This raises ZeroDivisionError when i == 10.
    for i in range(1, 9):
        v = i
        stdscr.addstr(i, 0, '10 divided by {} is {}'.format(v, 10/v))

    stdscr.refresh()
    stdscr.getkey()




wrapper(main)

