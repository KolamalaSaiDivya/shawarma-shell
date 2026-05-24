import os


def run_builtin(command, args, aliases, alias_file):

    if command == "pwd":

        print(os.getcwd())
        return True

    elif command == "cd":

        if len(args) == 0:
            print("Usage: cd <folder>")

        else:

            try:
                os.chdir(args[0])

            except FileNotFoundError:
                print("Directory not found")

        return True

    elif command == "clear":

        os.system("cls" if os.name == "nt" else "clear")
        return True

    elif command == "echo":

        print(" ".join(args))
        return True

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

                with open(alias_file, "a") as file:
                    file.write(f"{name}={value}\n")

                print(f"Alias '{name}' added.")

        return True

    elif command == "help":

        print("Built-in commands:")
        print("  pwd")
        print("  cd <folder>")
        print("  clear")
        print("  echo <text>")
        print('  alias name="command"')
        print("  help")
        print("  exit")

        return True

    return False