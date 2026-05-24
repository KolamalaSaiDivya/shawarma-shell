# Shawarma Shell 🌯

Shawarma is a modern custom shell built from scratch in Python to deeply understand how shells, processes, pipes, streams, and operating systems work internally.

This project started as a simple command loop and evolved into a fully interactive shell with process orchestration, redirection, pipes, history, aliases, configuration files, tab completion, and intelligent command suggestions.

---

# Features

## Core Shell Features
- Interactive shell loop
- Custom prompt system
- Built-in commands
- External command execution
- Argument parsing

## Process & OS Features
- Subprocess management
- Background process execution (`&`)
- Signal handling (`CTRL+C`)
- Multi-process orchestration

## Stream & IO Features
- Output redirection (`>`, `>>`)
- Input redirection (`<`)
- Single and multi-pipe support (`|`)

## Shell UX Features
- Persistent command history
- Tab completion
- Alias system
- Startup configuration with `.shawarmarc`
- Colored shell prompt
- Intelligent typo suggestions

## Architecture
- Modular shell architecture
- Separate built-in command module
- Persistent config/history management

---

# Example Commands

```bash
echo hello
pwd
cd folder
dir | findstr py
echo test > file.txt
sort < file.txt
python app.py &
alias gs="git status"