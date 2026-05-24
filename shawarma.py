import os
import shlex
import subprocess
import readline
import signal
import rlcompleter
import difflib

from colorama import init, Fore, Style

from core.builtins import run_builtin

init(autoreset=True)

HISTORY_FILE = "history/history.txt"
ALIAS_FILE = "config/aliases.txt"
RC_FILE = ".shawarmarc"

aliases = {}


def handle_sigint(signum, frame):
    print(
        f"\n{Fore.RED}Use 'exit' to quit Shawarma.{Style.RESET_ALL}"
    )


signal.signal(signal.SIGINT, handle_sigint)


def get_all_commands():

    commands = []

    paths = os.environ.get("PATH", "").split(os.pathsep)

    for path in paths:

        if os.path.exists(path):

            try:
                commands.extend(os.listdir(path))

            except PermissionError:
                pass

    commands.extend(aliases.keys())

    return sorted(set(commands))


def suggest_command(command):

    commands = get_all_commands()

    matches = difflib.get_close_matches(
        command,
        commands,
        n=1,
        cutoff=0.6
    )

    if matches:

        print(
            f"{Fore.YELLOW}"
            f"Did you mean: {matches[0]} ?"
        )


def completer(text, state):

    commands = get_all_commands()

    try:
        commands.extend(os.listdir("."))

    except PermissionError:
        pass

    commands = sorted(set(commands))

    matches = [cmd for cmd in commands if cmd.startswith(text)]

    if state < len(matches):
        return matches[state]

    return None


def execute_rc_file():

    if not os.path.exists(RC_FILE):
        return

    try:

        with open(RC_FILE, "r") as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                if line.startswith("alias"):

                    alias_command = line[len("alias"):].strip()

                    if "=" in alias_command:

                        name, value = alias_command.split("=", 1)

                        name = name.strip()
                        value = value.strip('"')

                        aliases[name] = value

                elif line.startswith("echo"):

                    print(line[len("echo"):].strip())

    except Exception as e:

        print(
            f"{Fore.RED}Error loading .shawarmarc: {e}"
        )


readline.set_completer(completer)
readline.parse_and_bind("tab: complete")

# =========================
# LOAD HISTORY
# =========================

os.makedirs("history", exist_ok=True)

try:
    readline.read_history_file(HISTORY_FILE)

except FileNotFoundError:
    open(HISTORY_FILE, "w").close()

# =========================
# LOAD ALIASES
# =========================

os.makedirs("config", exist_ok=True)

try:

    with open(ALIAS_FILE, "r") as file:

        for line in file:

            if "=" in line:

                name, value = line.strip().split("=", 1)

                aliases[name] = value

except FileNotFoundError:

    open(ALIAS_FILE, "w").close()

# =========================
# LOAD RC FILE
# =========================

execute_rc_file()

# =========================
# MAIN SHELL LOOP
# =========================

while True:

    current_dir = os.getcwd()

    prompt = (
        f"{Fore.YELLOW}shawarma "
        f"{Fore.CYAN}{current_dir} "
        f"{Fore.GREEN}>{Style.RESET_ALL} "
    )

    try:
        raw_input = input(prompt)

    except KeyboardInterrupt:
        print(
            f"\n{Fore.RED}Use 'exit' to quit Shawarma."
        )
        continue

    except EOFError:
        print(
            f"\n{Fore.GREEN}Goodbye!"
        )
        break

    parts = shlex.split(raw_input)

    if len(parts) == 0:
        continue

    command = parts[0]
    args = parts[1:]

    # =========================
    # ALIAS EXPANSION
    # =========================

    if command in aliases:

        expanded = shlex.split(aliases[command])

        command = expanded[0]

        args = expanded[1:] + args

    # =========================
    # BUILT-IN COMMANDS
    # =========================

    if command == "exit":

        print(
            f"{Fore.GREEN}Goodbye!"
        )

        break

    elif run_builtin(command, args, aliases, ALIAS_FILE):

        pass

    # =========================
    # EXTERNAL COMMANDS
    # =========================

    else:

        # =========================
        # INPUT REDIRECTION
        # =========================

        if "<" in raw_input:

            command_part, file_part = raw_input.split("<")

            command_part = command_part.strip()
            file_name = file_part.strip()

            parsed_command = shlex.split(command_part)

            try:

                with open(file_name, "r") as file:

                    subprocess.run(
                        parsed_command,
                        stdin=file
                    )

            except FileNotFoundError:
                print(
                    f"{Fore.RED}File or command not found"
                )

                suggest_command(command)

        # =========================
        # OUTPUT REDIRECTION
        # =========================

        elif ">" in raw_input:

            append_mode = ">>" in raw_input

            if append_mode:
                command_part, file_part = raw_input.split(">>")

            else:
                command_part, file_part = raw_input.split(">")

            command_part = command_part.strip()
            file_name = file_part.strip()

            parsed_command = shlex.split(command_part)

            mode = "a" if append_mode else "w"

            try:

                with open(file_name, mode) as file:

                    subprocess.run(
                        parsed_command,
                        stdout=file
                    )

            except FileNotFoundError:
                print(
                    f"{Fore.RED}Command not found"
                )

                suggest_command(command)

        # =========================
        # MULTI-PIPE SUPPORT
        # =========================

        elif "|" in raw_input:

            try:

                pipe_commands = [
                    shlex.split(part.strip())
                    for part in raw_input.split("|")
                ]

                processes = []

                previous_process = None

                for i, cmd in enumerate(pipe_commands):

                    if i == 0:

                        process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.PIPE
                        )

                    elif i == len(pipe_commands) - 1:

                        process = subprocess.Popen(
                            cmd,
                            stdin=previous_process.stdout
                        )

                    else:

                        process = subprocess.Popen(
                            cmd,
                            stdin=previous_process.stdout,
                            stdout=subprocess.PIPE
                        )

                    if previous_process:
                        previous_process.stdout.close()

                    processes.append(process)

                    previous_process = process

                processes[-1].communicate()

            except FileNotFoundError:
                print(
                    f"{Fore.RED}Command not found"
                )

                suggest_command(command)

        # =========================
        # NORMAL + BACKGROUND EXECUTION
        # =========================

        else:

            background = False

            if raw_input.endswith("&"):

                background = True

                raw_input = raw_input[:-1].strip()

                parts = shlex.split(raw_input)

                command = parts[0]
                args = parts[1:]

            try:

                if background:

                    process = subprocess.Popen([command] + args)

                    print(
                        f"{Fore.GREEN}"
                        f"Started background process "
                        f"PID: {process.pid}"
                    )

                else:

                    subprocess.run([command] + args)

            except FileNotFoundError:

                print(
                    f"{Fore.RED}Command not found"
                )

                suggest_command(command)

    # =========================
    # SAVE HISTORY
    # =========================

    readline.write_history_file(HISTORY_FILE)