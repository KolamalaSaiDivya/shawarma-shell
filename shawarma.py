import os
import shlex
import subprocess
import readline
import signal
import rlcompleter

HISTORY_FILE = "history.txt"
ALIAS_FILE = "aliases.txt"

aliases = {}


def handle_sigint(signum, frame):
    print("\nUse 'exit' to quit Shawarma.")


signal.signal(signal.SIGINT, handle_sigint)


def completer(text, state):

    commands = []

    paths = os.environ.get("PATH", "").split(os.pathsep)

    for path in paths:

        if os.path.exists(path):

            try:
                for cmd in os.listdir(path):
                    commands.append(cmd)

            except PermissionError:
                pass

    try:
        commands.extend(os.listdir("."))

    except PermissionError:
        pass

    commands.extend(aliases.keys())

    commands = sorted(set(commands))

    matches = [cmd for cmd in commands if cmd.startswith(text)]

    if state < len(matches):
        return matches[state]

    return None


readline.set_completer(completer)
readline.parse_and_bind("tab: complete")

# =========================
# LOAD HISTORY
# =========================

try:
    readline.read_history_file(HISTORY_FILE)

except FileNotFoundError:
    open(HISTORY_FILE, "w").close()

# =========================
# LOAD ALIASES
# =========================

try:

    with open(ALIAS_FILE, "r") as file:

        for line in file:

            if "=" in line:

                name, value = line.strip().split("=", 1)

                aliases[name] = value

except FileNotFoundError:

    open(ALIAS_FILE, "w").close()

# =========================
# MAIN SHELL LOOP
# =========================

while True:

    try:
        raw_input = input("shawarma> ")

    except KeyboardInterrupt:
        print("\nUse 'exit' to quit Shawarma.")
        continue

    except EOFError:
        print("\nGoodbye!")
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

        print("Goodbye!")
        break

    elif command == "pwd":

        print(os.getcwd())

    elif command == "cd":

        if len(args) == 0:

            print("Usage: cd <folder>")

        else:

            try:
                os.chdir(args[0])

            except FileNotFoundError:
                print("Directory not found")

    elif command == "clear":

        os.system("cls" if os.name == "nt" else "clear")

    elif command == "echo":

        print(" ".join(args))

    elif command == "alias":

        if len(args) == 0:

            for name, value in aliases.items():
                print(f"{name} = {value}")

        else:

            alias_input = " ".join(args)

            if "=" not in alias_input:

                print('Usage: alias name="command"')

            else:

                name, value = alias_input.split("=", 1)

                name = name.strip()
                value = value.strip('"')

                aliases[name] = value

                with open(ALIAS_FILE, "a") as file:
                    file.write(f"{name}={value}\n")

                print(f"Alias '{name}' added.")

    elif command == "help":

        print("Built-in commands:")
        print("  pwd")
        print("  cd <folder>")
        print("  clear")
        print("  echo <text>")
        print('  alias name="command"')
        print("  help")
        print("  exit")

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
                print("File or command not found")

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
                print("Command not found")

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
                print("Command not found")

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
                        f"Started background process PID: {process.pid}"
                    )

                else:

                    subprocess.run([command] + args)

            except FileNotFoundError:
                print("Command not found")

    # =========================
    # SAVE HISTORY
    # =========================

    readline.write_history_file(HISTORY_FILE)