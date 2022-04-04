#!/usr/bin/python3
import argparse
import os
import re

parser = argparse.ArgumentParser()
parser.add_argument('--in_sbv', help='sbv input file')
parser.add_argument('--out_txt', help='txt output file')

args = parser.parse_args()
in_sbv = os.path.expanduser(args.in_sbv)
out_txt = os.path.expanduser(args.out_txt)

txt = ''
ptn = r'[0-9]+:[0-9]+:[0-9.]+,[0-9]+:[0-9]+:[0-9.]+'
with open(in_sbv, mode='r') as f:
    lines = f.readlines()
    for line in lines:
        if line == '\n':
            continue
        if re.match(ptn, line):
            continue
        txt += line.replace('\n', ' ')

with open(out_txt, mode='w') as f:
    f.write(txt)
