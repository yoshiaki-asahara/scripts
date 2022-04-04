#!/usr/bin/python3
import os
import sys
import glob
import shutil
from getch import Getch

ignore_list = ['.part', '.rar']

if __name__ == "__main__":

    if len(sys.argv) == 2:
        before = sys.argv[1]
        after = ""
    elif len(sys.argv) == 3:
        before = sys.argv[1]
        after = sys.argv[2]
    else:
        print("Argument must be one.")
        exit()

    getch = Getch()

    file_list = glob.glob("./*")
    for file in file_list:
        file_name = file.replace("./", "")

        # Ignore files which have extension in the list.
        _, ext = os.path.splitext(file_name)
        if ext in ignore_list:
            continue

        new_name = file_name.replace(before, after)
        if (new_name == file_name):
            continue
        print("\nRename from [" + file_name + "]\n"
              + "         to [" + new_name + "]?  y:yes  n:no")

        while True:
            key = getch()
            if key == 'y':
                os.rename(file_name, new_name)
                break
            elif key == 'n':
                print("skip rename [" + file_name + "]")
                break
