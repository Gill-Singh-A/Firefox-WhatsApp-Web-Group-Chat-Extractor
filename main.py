#! /usr/bin/env python3

import os, subprocess, pickle
from pathlib import Path
from datetime import date
from optparse import OptionParser
from colorama import Fore, Back, Style
from time import strftime, localtime

status_color = {
    '+': Fore.GREEN,
    '-': Fore.RED,
    '*': Fore.YELLOW,
    ':': Fore.CYAN,
    ' ': Fore.WHITE
}

folder_name = ".mozilla"
default_path = Path.home() / folder_name
end_strings = ["pport", "susp", "termi", "/vt", "@g.us"]

def display(status, data, start='', end='\n'):
    print(f"{start}{status_color[status]}[{status}] {Fore.BLUE}[{date.today()} {strftime('%H:%M:%S', localtime())}] {status_color[status]}{Style.BRIGHT}{data}{Fore.RESET}{Style.RESET_ALL}", end=end)

def get_arguments(*args):
    parser = OptionParser()
    for arg in args:
        parser.add_option(arg[0], arg[1], dest=arg[2], help=arg[3])
    return parser.parse_args()[0]

def extractChats(file_path):
    chats = []
    strings_output = subprocess.check_output(["strings", file_path]).decode().split('\n')
    for index in range(len(strings_output)):
        if strings_output[index].strip() == "desc":
            group_name_offset = 1
            try:
                while True:
                    if "creation" in strings_output[index-group_name_offset]:
                        group_name = strings_output[index-group_name_offset-1].strip()[1:]
                        break
                    group_name_offset += 1
            except:
                group_name = None
            message_content = ""
            message_offset = 1
            sender_offset = 1
            try:
                while True:
                    if "owner" in strings_output[index-sender_offset]:
                        sender = strings_output[index-sender_offset+1].strip()[1:].split('@')[0]
                        break
                    sender_offset += 1
            except:
                sender = None
            try:
                end = False
                while True:
                    for end_string in end_strings:
                        if strings_output[index+message_offset].strip().startswith(end_string) or strings_output[index+message_offset].strip().endswith(end_string):
                            end = True
                            break
                    if end:
                        break
                    message_content += f"{strings_output[index+message_offset]}\n"
                    message_offset += 1
            except Exception as error:
                pass
            if message_content.strip() != '':
                chats.append([group_name, sender, message_content])
    return chats

if __name__ == "__main__":
    arguments = get_arguments(('-p', "--path", "path", f"Path to Firefox Cache Folder (Default={default_path})"),
                              ('-w', "--write", "write", "Write to CSV File (Default=Current Date and Time)"))
    if not arguments.path:
        arguments.path = default_path
    if not os.path.isdir(arguments.path):
        display('-', f"No Directory as {Back.YELLOW}{arguments.path}{Back.RESET}")
        exit(0)
    if not arguments.write:
        arguments.write = f"{date.today()} {strftime('%H_%M_%S', localtime())}.txt"
    paths = []
    for path, folders, files in os.walk(arguments.path):
        if "whatsapp" in path:
                paths.extend([f"{path}/{file}" for file in files if "sqlite" in file])
    paths = []
    for path, folders, files in os.walk(arguments.path):
        if "whatsapp" in path:
                paths.extend([f"{path}/{file}" for file in files if "sqlite" in file])
    chats = []
    for path in paths:
        chats.extend([chat for chat in extractChats(path) if chat not in chats])
    display('+', f"Total Chats => {Back.MAGENTA}{len(chats)}{Back.RESET}")
    print('\n'.join([f"* {Fore.CYAN}{group}{Fore.RESET} => {Fore.GREEN}{sender}{Fore.RESET}" for group, sender, message in chats]))
    with open(arguments.write, 'wb') as file:
        pickle.dump(chats, file)