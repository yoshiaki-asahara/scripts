#!/usr/bin/python3
import csv
import glob
import os
import pathlib
import platform
import psutil
import random
import shutil
import subprocess
import sys
from getch import Getch
from send2trash import send2trash
from transitions import Machine


class EmptyListException(Exception):
    pass


class HistoryManager(object):
    FIELD_NAMES = ['file', 'is_played', 'num_finished']
    CSV_NAME = './.history.csv'

    def __init__(self, favorite_mode):
        self._history_data = {}
        # If history file doesn't exist, create it.
        if not os.path.isfile(self.CSV_NAME):
            with open(self.CSV_NAME, 'w') as f:
                csv_file = csv.DictWriter(f, fieldnames=self.FIELD_NAMES)
                csv_file.writeheader()
        # Read history file and make history list.
        with open(self.CSV_NAME, 'r') as f:
            rows = csv.DictReader(f)
            for row in rows:
                # key : file
                # item: [num_played, num_finished]
                self._history_data[row[self.FIELD_NAMES[0]]] = [
                    int(row[self.FIELD_NAMES[1]]),
                    int(row[self.FIELD_NAMES[2]])]

        self._favorite_mode = favorite_mode

    def played(self, file):
        if not self._favorite_mode:
            self._history_data[file][0] = 1

    def finished(self, file, log_finished=True):
        if file in self._history_data.keys() and log_finished:
            self._history_data[file][0] = 0
            if self._favorite_mode:
                self._history_data[file][1] -= 1
            else:
                self._history_data[file][1] += 1
        new_file_exists = False
        files_in_current = glob.glob("./*")
        for file in files_in_current:
            if file not in self._initial_files:
                new_file_exists = True
                break
        all_played = True
        if not new_file_exists:
            for value in self._history_data.values():
                if value[0] == 0:
                    all_played = False
            if all_played:
                for key in self._history_data.keys():
                    self._history_data[key][0] = 0
        with open(self.CSV_NAME, 'w') as f:
            csv_file = csv.DictWriter(f, fieldnames=self.FIELD_NAMES)
            csv_file.writeheader()
            for key in self._history_data.keys():
                csv_file.writerow(
                    {self.FIELD_NAMES[0]: key,
                     self.FIELD_NAMES[1]: self._history_data[key][0],
                     self.FIELD_NAMES[2]: self._history_data[key][1]})
            print(self.CSV_NAME + ' closed')

    def play_list(self, files_in_current):
        self._initial_files = files_in_current
        # Add new files to history.
        for file in files_in_current:
            if file not in self._history_data.keys():
                self._history_data[file] = [0, 0]
        # Delete files from history which are not in current.
        deleted_files = []
        for file in self._history_data.keys():
            if file not in files_in_current:
                deleted_files.append(file)
        for file in deleted_files:
            self._history_data.pop(file)
        play_list = []
        for file in self._history_data.keys():
            if self._favorite_mode:
                if self._history_data[file][1] > 0:
                    play_list.append(file)
            elif self._history_data[file][0] == 0:
                play_list.append(file)
        random.shuffle(play_list)
        return play_list


class MoviePlayerMachine(object):
    states = ['INIT', 'WAIT', 'PLAYED']

    def __init__(self, name, mv_path, ignore_list, favorite_mode):
        self._name = name
        self._machine = Machine(
            model=self, states=MoviePlayerMachine.states, initial='INIT', auto_transitions=False)
        self._machine.add_transition(
            trigger='start', source='INIT', dest='WAIT', before='make_list', after='next_file')
        self._machine.add_transition(
            trigger='skip', source='WAIT', dest='WAIT', after='next_file')
        self._machine.add_transition(
            trigger='play', source='WAIT', dest='PLAYED', after='play_movie')
        self._machine.add_transition(
            trigger='play', source='PLAYED', dest='PLAYED', after='play_movie')
        self._machine.add_transition(
            trigger='delete', source='PLAYED', dest='WAIT', before='delete_movie', after='next_file')
        self._machine.add_transition(
            trigger='move', source='PLAYED', dest='WAIT', before='move_movie', after='next_file')
        self._machine.add_transition(
            trigger='nothing', source='PLAYED', dest='WAIT', after='next_file')
        self._mv_path = mv_path

        self._history_manager = HistoryManager(favorite_mode)
        self._file = ''

        self._ignore_list = ignore_list

    # Pick up next file name from play list.
    def next_file(self):
        # raise exception if file list becomes empty.
        if(len(self._play_list) == 0):
            print('play list is empty.')
            self._file = ''
            self._history_manager.finished(self._file, log_finished=False)
            raise EmptyListException
        # Choose file from play list.
        self._file = self._play_list.pop()

        # Print all files in play list.
        print('')
        for file_after_next in self._play_list:
            print(file_after_next.replace('./', ''))
        print('--------------------------------------\n')
        print('('+str(self._num_files-len(self._play_list)) +
              '/'+str(self._num_files)+')')
        print(self._file.replace('./', ''))

    def make_list(self):
        # Make list of files that are in current.
        files_in_current = glob.glob("./*")
        for file in files_in_current[:]:
            _, ext = os.path.splitext(file)
            if ext in self._ignore_list:
                files_in_current.remove(file)
                continue
        self._play_list = self._history_manager.play_list(files_in_current)
        self._num_files = len(self._play_list)

    def play_movie(self):
        subprocess.run(["vlc", self._file],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        self._history_manager.played(self._file)

    def delete_movie(self):
        # Move file to Trashbox.
        send2trash(self._file)

    def move_movie(self):
        # Force to move file to destination.
        cwd = os.getcwd() + "/"
        dst = pathlib.Path(self._mv_path)
        print('move to ' + str(dst.resolve()))
        try:
            shutil.move(os.path.join(cwd, self._file),
                        dst.resolve())
        except:
            print(
                '\n[WARNING] The same name file already exists in the target path. Do nothing.')

    def quit(self):
        self._history_manager.finished(self._file, log_finished=False)

    def finish(self):
        self._history_manager.finished(self._file, log_finished=True)


if __name__ == '__main__':
    favorite_mode = False
    if len(sys.argv) == 1:
        print("no path input. Favorite mode.")
        mv_path = "./"
        favorite_mode = True
    elif len(sys.argv) == 2:
        mv_path = sys.argv[1]
        if not os.path.exists(mv_path):
            print(mv_path+' does not exist')
            exit()
    else:
        print('usage: python3 movie_player.py (path to move dir)')

    ignore_list = ['.part', '.rar']
    machine = MoviePlayerMachine(
        'movie_player_machine', mv_path, ignore_list, favorite_mode)
    getch = Getch()

    try:
        machine.start()
        while True:
            if machine.state == 'WAIT':
                if favorite_mode:
                    print('[favorite mode] q:quit  /:play  \':skip')
                else:
                    print('q:quit  /:play  \':skip')
                while True:
                    key = getch()
                    if(key == '\''):
                        machine.skip()
                        break
                    elif(key == '/'):
                        machine.play()
                        break
                    elif(key == 'q'):
                        machine.quit()
                        exit()
            if machine.state == 'PLAYED':
                if favorite_mode:
                    print(
                        '[favorite mode] q:quit  /:next  m:move  k:delete  p:replay  f:unfavorite')
                else:
                    print('q:quit  /:next  m:move  k:delete  p:replay  f:favorite')
                while True:
                    key = getch()
                    if(key == '/'):
                        machine.nothing()
                        break
                    elif(key == 'p'):
                        machine.play()
                        break
                    elif(key == 'k'):
                        machine.delete()
                        break
                    elif(key == 'm'):
                        machine.move()
                        break
                    elif(key == 'q'):
                        machine.quit()
                        exit()
                    elif(key == 'f'):
                        machine.finish()
                        exit()
    except EmptyListException:
        pass
    else:
        import traceback
        traceback.print_exc()
    finally:
        print('finish')
