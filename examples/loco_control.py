#!/usr/bin/env python

import dccpi_mm as dccpi
import urwid

LOCO_ADDRESS = 9
COMMANDS_QUEUE = "dcc_command"
EMERGENCY_QUEUE = "dcc_emergency"
REDIS_ARGS =  {
    'host': 'localhost',
    'port': 6379,
    'db': 0
}





loco_control = dccpi.DCCKeyboardLocoControl(LOCO_ADDRESS, COMMANDS_QUEUE, EMERGENCY_QUEUE, **REDIS_ARGS)

def key_handler(key):
    if key in ('q', 'Q'):
        loco_control.exit()
        raise urwid.ExitMainLoop()

    command_move, command_functions = loco_control.key_handler(key)
    txt.set_text("Loco Speed = {speed} Functions: FL={loco_functions_FL} direction={direction}".format(
                                    speed=command_move['speed'],
                                    loco_functions_FL=command_functions['functions_state']['FL'],
                                    direction=command_move['direction']))

palette = [
    ('banner', '', '', '', '#ffa', '#60d'),
    ('streak', '', '', '', 'g50', '#60a'),
    ('inside', '', '', '', 'g38', '#808'),
    ('outside', '', '', '', 'g27', '#a06'),
    ('bg', '', '', '', 'g7', '#d06'),]

placeholder = urwid.SolidFill()

loop = urwid.MainLoop(placeholder, palette, unhandled_input=key_handler)
loop.screen.set_terminal_properties(colors=256)
loop.widget = urwid.AttrMap(placeholder, 'bg')
loop.widget.original_widget = urwid.Filler(urwid.Pile([]))

div = urwid.Divider()
outside = urwid.AttrMap(div, 'outside')
inside = urwid.AttrMap(div, 'inside')
txt = urwid.Text(u" Loco Control  ", align='left')


streak = urwid.AttrMap(txt, 'streak')
pile = loop.widget.base_widget # .base_widget skips the decorations
for item in [outside, inside, streak, inside, outside]:
    pile.contents.append((item, pile.options()))

loop.run()
