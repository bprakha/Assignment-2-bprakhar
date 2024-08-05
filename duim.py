#!/usr/bin/env python3

import subprocess, sys
import os
import argparse

'''
OPS445 Assignment 2 - Winter 2022
Program: duim.py 
Author: "bprakhar"
The python code in this file (duim.py) is original work written by
"Prakhar Bhola". No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: This program is a Python implementation of the du command with additional features.

Date: 
'''

def parse_command_args():
    "Set up argparse here. Call this function inside main."
    parser = argparse.ArgumentParser(description="DU Improved -- See Disk Usage Report with bar charts", epilog="Copyright 2022")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    parser.add_argument("-H", "--human-readable", action="store_true", help="Display sizes in human-readable format.")
    parser.add_argument("target", nargs=1, help="Specify the target directory.")
    args = parser.parse_args()
    return args

def percent_to_graph(percent, total_chars):
    "returns a string: eg. '##  'or 50 if total_chars == 4"
    filled_length = int(round(percent * total_chars / 100))
    graph = '#' * filled_length + ' ' * (total_chars - filled_length)
    return graph

def call_du_sub(location):
    "takes the target directory as an argument and returns a list of strings"
    "returned by the command `du -d 1 location`"
    du_output = subprocess.check_output(['du', '-d', '1', location]).decode('utf-8').splitlines()
    return du_output

def create_dir_dict(alist):
    "gets a list from call_du_sub, returns a dictionary which should have full"
    "directory name as key, and the number of bytes in the directory as the value."
    dir_dict = {}
    for line in alist:
        size, directory = line.split('\t')
        dir_dict[directory] = int(size)
    return dir_dict


if __name__ == "__main__":
    args = parse_command_args()
    du_output = call_du_sub(args.target[0])
    dir_dict = create_dir_dict(du_output)
    for directory, size in dir_dict.items():
        percent = size / sum(dir_dict.values())
        graph = percent_to_graph(percent, args.length)
        print(f"{directory}: {graph} ({size} bytes)")