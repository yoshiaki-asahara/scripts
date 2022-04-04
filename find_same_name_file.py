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
    print('  find_same_name_file.py [dir1] [dir2] ...\n')
    exit()

paths = sys.argv[1:]

for path in paths:
    if not os.path.exists(path):
        print(path + ' does not exist.')
        exit()

files1 = []
for path in paths:
    files1 += glob.glob(path + '/*')

files2 = files1[:]
deleted_files = []

num_of_pairs = len(files1) ** 2
counter = 0

for file1 in files1:
    for file2 in files2:
        counter += 1
        print('\r' + '{:.1f}'.format(counter / num_of_pairs * 100) +
              '% processed...', end='')
        if file1 == file2:
            continue
        if os.path.basename(file1) != os.path.basename(file2):
            continue
        if os.path.basename(file1) in deleted_files:
            continue
        if os.path.basename(file2) in deleted_files:
            continue

        print('-----------------------')
        print('[size=' + str(os.path.getsize(file1)) + ' ' + file1 + ']')
        print('[size=' + str(os.path.getsize(file2)) + ' ' + file2 + ']')
        print('  l:delete ' + file1)
        print('  ;:open   ' + file1)
        print('  .:delete ' + file2)
        print('  /:open   ' + file2)
        print('  \':skip')
        print('  q:quit')
        while True:
            key = getch()
            if(key == 'l'):
                file = file1
                print('delete ' + file)
                send2trash(file)
                deleted_files.append(os.path.basename(file))
                break
            elif(key == '.'):
                file = file2
                print('delete ' + file)
                send2trash(file)
                deleted_files.append(os.path.basename(file))
                break
            elif(key == ';'):
                file = file1
                print('play ' + file)
                subprocess.call(["open", "/Applications/VLC.app", file])
            elif(key == '/'):
                file = file2
                print('play ' + file)
                subprocess.call(["open", "/Applications/VLC.app", file])
            elif(key == '\''):
                print('skip')
                break
            elif(key == 'q'):
                exit()
