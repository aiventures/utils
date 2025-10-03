#!/usr/bin/env python3
"""

This script converts a Windows .bat script file into a Python module file
with equivalent variable declarations.

Original BAT file: {bat_file_path}
Date of generation: {generation_date}

PROMPT

(...additional changes were done...)

Write a program in python that will read and convert code of an existing .bat script file for windows into a
python module file, that will declare the variable defined in the .bat file as variables as defined by the set command in a python file.

It should transform the bat file into python according to the follwing rules, as shown by the exemplary code

- in the docstring header, supply an additional comment, that lists the file path of the original BAT file and the date of generation
- for a set MY_VAR1=my_var1 command  in bat, transform it to MY_VAR1=r"my_var" in python
- for a set "MY_VAR2=my_var2 example" command  in bat, transform it to MY_VAR2=r"my_var2 example" in python (mind the double quote after the set
  command indicating everything behind = should be treated as variable value)
- in case the values defined in the bat can be interpreted as float or int, then transform them into float or int values instead
- in case there is a preceding comment in the bat, then also supply that comment in python module, example:
  IN BAT
  rem this my comment
  set MY_VAR3=hugo
  Transform to python snippet
  # this my comment
  MY_VAR3=r"hugo"
- Note that the variables can be depenedent from one another, so for example the bat can look like
  rem working path
  set "MY_P_WORK=C:\\xyz"
  rem path containing venvs
  set "MY_P_VENV=%MY_P_WORK%\VENV"
  rem path containing work venv
  set "MY_P_VENV_WORK=%MY_P_VENV%\WORK"
  Take care to collect all variable definitions before and resolve / replace them iteratively (so replace Vaiable name by its valiues from to bottom of file, for example MY_P_WORK is defined in previous lines and will be referenced below. So %MY_P_WORK% should be resolved to C:\30_Entwicklung )
- add a main method and argparse arguments to supply input file and output file with a default of myenv_set.bat and myenv_set.py for the case that these params won't be supplied at command line
- also add error messages in case avriables can't be resolved or there are circular references
- for the generate path in the comment fix "got unexpected unicode" for paths like C:\<...>\\utils\... (because there is a path with \\u)

"""

import argparse
import re
from datetime import datetime
from pathlib import Path
import sys


def parse_bat(bat_lines):
    variables = {}
    output_lines = []
    pending_comment = None

    # Matches: set VAR=value OR set "VAR=value"
    var_pattern = re.compile(r'^set\s+(?:"([^=]+)=(.*)"|([^=]+)=(.*))$', re.IGNORECASE)

    for line in bat_lines:
        line = line.strip()
        if not line:
            continue

        if line.lower().startswith("rem "):
            pending_comment = "# " + line[4:].strip()
            continue

        match = var_pattern.match(line)
        if match:
            if match.group(1):  # case: set "VAR=VALUE"
                var_name, var_value = match.group(1).strip(), match.group(2).strip()
            else:  # case: set VAR=VALUE
                var_name, var_value = match.group(3).strip(), match.group(4).strip()

            variables[var_name] = var_value

            if pending_comment:
                output_lines.append((pending_comment, var_name))
                pending_comment = None
            else:
                output_lines.append((None, var_name))

    return variables, output_lines


def resolve_variables(variables):
    """Resolve %VAR% placeholders recursively, detecting circular references."""
    resolved = {}
    stack = set()

    def substitute(value, path=None):
        if path is None:
            path = []

        inner_pattern = re.compile(r"%([^%]+)%")
        matches = inner_pattern.findall(value)

        for ref in matches:
            if ref in path:
                raise RuntimeError(f"Circular reference detected: {' -> '.join(path + [ref])}")
            if ref not in variables:
                raise RuntimeError(f"Unresolved reference: {ref} used but not defined")

            if ref not in resolved:
                stack.add(ref)
                sub_val = substitute(variables[ref], path + [ref])
                resolved[ref] = sub_val
                stack.discard(ref)

            value = value.replace(f"%{ref}%", str(resolved[ref]))

        return value

    for k, v in variables.items():
        if k not in resolved:
            resolved[k] = substitute(v, [k])

    return resolved


def convert_value(val):
    """Convert val to int, float, or raw string depending on content."""
    try:
        if "." in val:
            return float(val)
        else:
            return int(val)
    except ValueError:
        return f'r"{val}"'


def save_python_module(py_path, header, output_lines, resolved):
    """Save the generated Python module to the given path."""
    lines = [header, "\n"]

    for comment, var_name in output_lines:
        if comment:
            lines.append(comment + "\n")
        value = convert_value(resolved[var_name])
        lines.append(f"{var_name} = {value}\n")

    # Add __main__ test block so the generated module can print its variables
    lines.append('\n\nif __name__ == "__main__":\n')
    lines.append("    from pprint import pprint\n")
    lines.append("    vars_dict = {key: value for key, value in globals().items() if key.isupper()}\n")
    lines.append("    pprint(vars_dict)\n")

    Path(py_path).write_text("".join(lines), encoding="utf-8")


def bat_to_python(bat_path, py_path):
    abs_bat_path = str(Path(bat_path).resolve())

    # Escape backslashes explicitly to avoid accidental \u sequences
    safe_bat_path = abs_bat_path.replace("\\", "\\\\")

    bat_lines = Path(bat_path).read_text(encoding="utf-8").splitlines()
    variables, output_lines = parse_bat(bat_lines)

    try:
        resolved = resolve_variables(variables)
    except RuntimeError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

    header = f'''"""
This module was generated from {safe_bat_path}
Date of generation: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
'''

    save_python_module(py_path, header, output_lines, resolved)


def main():
    parser = argparse.ArgumentParser(description="Convert a Windows .bat environment script into a Python module.")
    parser.add_argument("--input", "-i", default="myenv.bat", help="Input .bat file path (default: myenv.bat)")
    parser.add_argument("--output", "-o", default="myenv.py", help="Output .py file path (default: myenv.py)")
    args = parser.parse_args()

    try:
        bat_to_python(args.input, args.output)
        print(f"✔ Converted {args.input} → {args.output}")
    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
