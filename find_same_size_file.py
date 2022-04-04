#!/usr/bin/python3

import glob
import subprocess
import os
import subprocess
import sys
from getch import Getch
from send2trash import send2trash

getch = Getch()

if len(sys.argv) == 1:
    print('\nHow to use:')
    print('  find_same_size_file.py [dir1] [dir2] ...\n')
    exit()

paths = sys.argv[1:]

for path in paths:
    if not os.path.exists(path):
        print(path + ' does not exist.')
        exit()

files = []
for path in paths:
    files += glob.glob(path + '/*')

sorted_files = sorted(files, key=os.path.getsize)

pre_file = ''
pre_size = ''

for cur_file in sorted_files:
    cur_size = os.path.getsize(cur_file)

    if cur_size == pre_size:
        print('-----------------------')
        print('[' + pre_file + ']')
        print('[' + cur_file + ']')
        print('    are same size files (' + str(cur_size/1000000) + 'MB)')
        print('  l:delete ' + pre_file)
        print('  ;:open   ' + pre_file)
        print('  .:delete ' + cur_file)
        print('  /:open   ' + cur_file)
        print('  q:quit')
        while True:
            key = getch()
            if(key == 'l'):
                file = pre_file
                print('delete ' + file)
                send2trash(file)
                break
            elif(key == '.'):
                file = cur_file
                print('delete ' + file)
                send2trash(file)
                break
            elif(key == ';'):
                file = pre_file
                print('play ' + file)
                subprocess.call(
                    ["open", "/Applications/VLC.app", file])
            elif(key == '/'):
                file = cur_file
                print('play ' + file)
                subprocess.call(
                    ["open", "/Applications/VLC.app", file])
            elif(key == '\''):
                print('skip')
                break
            elif(key == 'q'):
                exit()

    pre_file = cur_file
    pre_size = cur_size
