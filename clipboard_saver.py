#!/usr/bin/python
import sys
import pyperclip

if len(sys.argv) != 2:
    print('\nHow to use:')
    print('   clipboard_saver.py [outfile]\n')
    exit()

try:
    with open(sys.argv[1], 'a') as f:
        while True:
            clip = pyperclip.waitForNewPaste()
            print(clip)
            f.write(clip + '\n')
except KeyboardInterrupt:
    print('terminate')
