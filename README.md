LLL - A Lightweight LLDB Frontend based on PyQt
---

## Motivation:
Debugging in commandline is neighter user friendly nor productive. Users may not memorize all commands and debugging practice usually needs to monitoring source code, variable content, disassembles, etc. in the same time. It is also convenient to allow user to do some simple code modification during debugging session. However, it won't be an IDE as it won't support fancy syntax hightlighting, auto completion, building, source code project, etc.

## Goals:
LLL is designed to be a lightweight LLDB GUI frontend based on Qt. It should support:
1) Convenient debugging and simple in-place source code modification
2) Windows to show call stack, watched variables, register values, memory data, etc.
3) Mixing the display of souce code and disassembled instructions in the same window
4) Remote debugging
5) Suppport debugging multi-threaded programs
6) Good looking UI

## Usage:
1) Modify lll.ini to set the path of clang and lldb.
2) lll.py [exe file] [args]...

## Requirements:
Qt 4.0
Python 2.7
Clang (for syntax hightlighting)
LLDB

## Current Status:
Very basic debugging support

## Tested on:
Linux Arch on x86-64

## Screenshot:
[Imgur](http://i.imgur.com/VnYSZ1s.png)
