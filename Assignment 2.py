#!/usr/bin/env python3

import argparse
import os
import sys

def parse_command_args() -> object:
    """Set up argparse here. Call this function inside main."""
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts",
                                     epilog="Copyright 2023")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    parser.add_argument("-H", "--human-readable", action='store_true', help="Prints sizes in human readable format")
    parser.add_argument("program", type=str, nargs='?', help="if a program is specified, show memory use of all associated processes. Show only total use if not.")
    args = parser.parse_args()
    return args

def percent_to_graph(percent: float, length: int = 20) -> str:
    """Turns a percent 0.0 - 1.0 into a bar graph."""
    filled_length = int(length * percent) 
    bar = '#' * filled_length + ' ' * (length - filled_length)
    return bar

# Example usage:
#print(percent_to_graph(0.5))  # Output: '##########          '


def get_sys_mem() -> int:
    """Return total system memory (used or available) in kB."""
    with open('/proc/meminfo', 'r') as file:
        for line in file:
            if line.startswith('MemTotal:'):
                return int(line.split()[1])
    return 0

def get_avail_mem() -> int:
    """Return total memory that is currently available in kB."""
    with open('/proc/meminfo', 'r') as file:
        for line in file:
            if line.startswith('MemAvailable:'):
                return int(line.split()[1])
    return 0

def pids_of_prog(app_name: str) -> list:
    """Given an app name, return all PIDs associated with the app."""
    pids = []
    with os.popen(f'pidof {app_name}') as proc:
        output = proc.read().strip()
        if output:
            pids = output.split()
    return pids

def rss_mem_of_pid(proc_id: str) -> int:
    """Given a process ID, return the Resident memory used."""
    rss_total = 0
    try:
        with open(f'/proc/{proc_id}/smaps', 'r') as file:
            for line in file:
                if line.startswith('Rss:'):
                    rss_total += int(line.split()[1])
    except FileNotFoundError:
        pass
    return rss_total

def bytes_to_human_r(kibibytes: int, decimal_places: int = 2) -> str:
    """Turn 1,024 into 1 MiB, for example."""
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']  # iB indicates 1024
    suf_count = 0
    result = kibibytes
    while result > 1024 and suf_count < len(suffixes):
        result /= 1024
        suf_count += 1
    str_result = f'{result:.{decimal_places}f} '
    str_result += suffixes[suf_count]
    return str_result

if __name__ == "__main__":
    args = parse_command_args()

    if not args.program:  # If no program name is specified.
        total_memory = get_sys_mem()
        available_memory = get_avail_mem()
        used_memory = total_memory - available_memory
        percent_used = used_memory / total_memory

        if args.human_readable:
            total_memory_str = bytes_to_human_r(total_memory)
            used_memory_str = bytes_to_human_r(used_memory)
        else:
            total_memory_str = f"{total_memory} kB"
            used_memory_str = f"{used_memory} kB"

        print(f"Debug: total_memory = {total_memory}, available_memory = {available_memory}, used_memory = {used_memory}, percent_used = {percent_used}")

        graph = percent_to_graph(percent_used, args.length)
        print(f"Memory         [{graph} | {percent_used*100:.0f}%] {used_memory_str}/{total_memory_str}")

    else:
        pids = pids_of_prog(args.program)

        if not pids:  # If no PIDs are found for the given program.
            print(f"No PIDs found for program '{args.program}'")
        else:
            for pid in pids:
                rss_memory = rss_mem_of_pid(pid)
                if args.human_readable:
                    rss_memory_str = bytes_to_human_r(rss_memory)
                else:
                    rss_memory_str = f"{rss_memory} kB"

                percent_used = rss_memory / get_sys_mem()
                graph = percent_to_graph(percent_used, args.length)
                print(f"{pid:<15} [{graph} | {percent_used*100:.0f}%] {rss_memory_str}/{get_sys_mem()} kB")