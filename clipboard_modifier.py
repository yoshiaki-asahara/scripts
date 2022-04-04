#!/usr/bin/python
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import pyperclip

_REPLACE = [
    ['-\n', ''],
    ['\n', ' '],
    ['%', ' percent'],
    ['/', ' and ']
]

while True:
    clip = pyperclip.waitForNewPaste()
    for r in _REPLACE:
        clip = clip.replace(r[0], r[1])
    print(clip)
    pyperclip.copy(clip)
