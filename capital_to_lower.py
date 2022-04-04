#!/usr/bin/python3
import os
import sys
import glob
import shutil
from getch import Getch

ignore_list = ['.part', '.rar']

if __name__ == "__main__":
    file_list = glob.glob("./*")
    getch = Getch()
    is_all = False
    num_files = 0
    for file in file_list:
        file_name = file.replace("./", "")

        # Ignore files which have extension in the list.
        _, ext = os.path.splitext(file_name)
        if ext in ignore_list:
            continue

        new_name = file_name.replace(file_name, file_name.lower())
        if (new_name == file_name):
            continue

        num_files += 1

        if is_all:
            os.rename(file_name, new_name)
            continue

        print("\nRename from [" + file_name + "]\n"
              + "         to [" + new_name + "]?  y:yes  n:no  !:yes all")
        while True:
            key = getch()
            if key == 'y':
                os.rename(file_name, new_name)
                break
            elif key == 'n':
                print("skip rename [" + file_name + "]")
                break
            elif key == '!':
                os.rename(file_name, new_name)
                is_all = True
                break

    print(str(num_files) + ' files are modified.')
