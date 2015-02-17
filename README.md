LLL - A Lightweight LLDB Frontend based on PyQt
---

## Motivation & Goals:
This aim of this tool is to provide a productive and user-friendly interface for debugging. 

During a debugging session, usually users need to monitor a lot of info (source code, variables, disassembled instructions, etc.) at the same time, which makes command-driven interface less efficient. Besides, users need to memorize all commands variable content, disassembles, etc. in the same time. It is also convenient to allow user to do some simple code modification during debugging session. 


## Usage:
1. Create or edit **~/.config/c0deforfun/lll.conf** to setup the path of clang and lldb. Example:
```[common]
`clang_lib_path=/home/llvm/lib* # Clang lib for source code syntax highlighting`
*lldb_path=/home/llvm/lib/python2.7/site-packages* # Binding of lldb
*logging_level=INFO* # Logging level
```

2. *lll.sh [exe file] [args]...*

## Requirements:
Qt 4.0
Python 2.7
Clang (for syntax hightlighting)
LLDB

## Tested on:
Linux Arch on x86-64

## Screenshot:
![Alt text](/docs/screenshot.png?raw=true "Screenshot")
