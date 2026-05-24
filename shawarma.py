import os
import shlex
import subprocess

while True:
    raw_input = input("shawarma> ")

    parts = shlex.split(raw_input)

    if len(parts) == 0:
        continue

    command = parts[0]
    args = parts[1:]

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

    elif command == "help":
        print("Built-in commands:")
        print("  pwd")
        print("  cd <folder>")
        print("  clear")
        print("  echo <text>")
        print("  exit")

    else:

        if ">" in raw_input:

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
                    subprocess.run(parsed_command, stdout=file)

            except FileNotFoundError:
                print("Command not found")

        elif "|" in raw_input:

            pipe_parts = raw_input.split("|")

            left_command = shlex.split(pipe_parts[0].strip())
            right_command = shlex.split(pipe_parts[1].strip())

            try:
                left_process = subprocess.Popen(
                    left_command,
                    stdout=subprocess.PIPE
                )

                right_process = subprocess.Popen(
                    right_command,
                    stdin=left_process.stdout
                )

                left_process.stdout.close()

                right_process.communicate()

            except FileNotFoundError:
                print("Command not found")

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

                    print(f"Started background process PID: {process.pid}")

                else:

                    subprocess.run([command] + args)

            except FileNotFoundError:
                print("Command not found")