#!/usr/bin/env python3

# pomo.py - Simple GUI pomodoro timer

import sys

import PySimpleGUI as sg
from kdeConnect import SMS
from Notification import Notification


GRAPH_SIZE = (300, 300)  # this one setting drives the other settings
CIRCLE_LINE_WIDTH, LINE_COLOR = 20, 'orange'
TEXT_FONT = 'Consolas'
THEME = 'Dark Gray 2'

# Computations based on your settings above
TEXT_HEIGHT = GRAPH_SIZE[0] // 4
TEXT_LOCATION = (GRAPH_SIZE[0] // 2, GRAPH_SIZE[1] // 2)
TEXT_COLOR = LINE_COLOR


def update_meter(graph_elem, percent_complete):
    """
    Update a circular progress meter
    :param graph_elem:              The Graph element being drawn in
    :type graph_elem:               sg.Graph
    :param percent_complete:        Percentage to show complete from 0 to 100
    :type percent_complete:         float | int
    """
    graph_elem.erase()
    arc_length = percent_complete / 100 * 360 + 0.9
    if arc_length >= 360:
        arc_length = 359.9
    graph_elem.draw_arc(
        (CIRCLE_LINE_WIDTH, GRAPH_SIZE[1] - CIRCLE_LINE_WIDTH),
        (GRAPH_SIZE[0] - CIRCLE_LINE_WIDTH, CIRCLE_LINE_WIDTH),
        arc_length,
        0,
        'arc',
        arc_color=LINE_COLOR,
        line_width=CIRCLE_LINE_WIDTH,
    )
    percent = percent_complete
    graph_elem.draw_text(f'{percent:.0f}%', TEXT_LOCATION, font=(TEXT_FONT, -TEXT_HEIGHT), color=TEXT_COLOR)


def main(timer=25, timeout=200):
    minutes = timer
    seconds = minutes * 60
    timeout_wait = (timer * 60) / (timeout / 1000)
    timeout_wait = round(timeout_wait)
    print(timeout_wait)

    sg.theme(THEME)

    layout = [
        [sg.Push(), sg.Text(str(timer), font=(TEXT_FONT), text_color=TEXT_COLOR, key='-TIME_LEFT-'), sg.Push()],
        [sg.Graph(GRAPH_SIZE, (0, 0), GRAPH_SIZE, key='-GRAPH-')],
        [sg.Push(), sg.Button('Go'), sg.Button('Exit'), sg.Push()],
    ]

    window = sg.Window('Circlular Meter', layout, location=(0, 0), finalize=True)
    graph_window = window['-GRAPH-']

    update_meter(graph_window, 0 / timeout_wait * 100)
    seconds_left = seconds - 0
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == 'Go':
            print('Started timer...')
            for progress in range(timeout_wait):
                try:
                    label = f'{seconds_left // 60}:{seconds_left % 60:02d}'
                    if progress % 5 == 0:
                        seconds_left -= 1
                        window['-TIME_LEFT-'].update(label)
                    update_meter(window['-GRAPH-'], progress / timeout_wait * 100)
                    window.read(timeout=timeout)
                except KeyboardInterrupt:
                    break
        if seconds_left <= 6:
            try:
                notify = Notification('Pomodoro', 'Time is up')
                notify.show()
            except:
                print('Could not send notification')
            try:
                sms_engine = SMS('d847bc89_cacd_4cb7_855b_9570dba7d6fa')
                sms_engine.send('Pomodoro: Time is up!', '6042265455')
            except:
                print('Could not send SMS')
        break
    window.close()


if __name__ == '__main__':
    if ('--help', '-help', '-h') in sys.argv:
        print('Usage: pomo [minutes]')
        print('Default 25 minutes')
        sys.exit(0)
    if len(sys.argv) > 1:
        timer = int(sys.argv[1])
        main(timer)
    else:
        main(25)
