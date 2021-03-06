#!/usr/bin/env python3

import sys
import select
import tty
import termios
import time
import curses
from datetime import datetime


def seconds_to_string(sec):
    """Convert time in seconds to h:m:s string."""
    mins = sec // 60
    sec = sec % 60
    hours = mins // 60
    mins = mins % 60
    time_str = "{:02d}:{:02d}:{:02d}".format(int(hours), int(mins), int(sec))
    return time_str


def time_convert(stdscr, sec):
    """Convert time in seconds to hh:mm:ss format and print it
    overwritting previous line(s).
    """
    time_str =  "############\n"
    time_str += "# {} #\n".format(seconds_to_string(sec))
    time_str +=  "############\n"
    # time_str +=  "\n (q)uit, (s)ave and quit, (p)ause\n"
    stdscr.addstr(0, 0, time_str)
    stdscr.refresh()


def is_data():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


# Initial state
paused = False
start_time = time.time()
elapsed_time = 0
total_time = 0
periods = []

# Curses initialization
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()


old_settings = termios.tcgetattr(sys.stdin)
try:
    tty.setcbreak(sys.stdin.fileno())

    while True:

        time.sleep(0.2)

        # If not paused, calculate elapsed time
        if not paused:
            current_time = time.time()
            elapsed_time = current_time - start_time
            # Add all the time from previous periods
            previous_time = 0
            for p in periods:
                previous_time += p
            total_time = previous_time+elapsed_time
            time_convert(stdscr, total_time)

        # Get user input
        if is_data():
            # Read key
            c = sys.stdin.read(1)
            if c == 's':  # Save and Quit
                # Write total time to current date file and exit
                # program
                today_str = datetime.today().strftime('%Y-%m-%d')
                # Open a file with access mode 'a'
                with open("times/{}.txt".format(today_str), "a") as file_object:
                    # Append 'hello' at the end of file
                    file_object.write(seconds_to_string(total_time)+'\n')
                break
            if c == 'q':  # Quit
                # Exit program
                break
            if c == 'p':  # Pause
                # Pause stopwatch
                paused = not paused
                if paused:
                    # Running -> Paused: record period time
                    periods.append(elapsed_time)
                else:
                    # Paused -> Running: new start time for the new
                    # period
                    start_time = time.time()
finally:
    # Close termios
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    # Close curses
    curses.echo()
    curses.nocbreak()
    curses.endwin()

