"""Converts a .bat file containing color constants to a Python constants file."""

import re
from pathlib import Path
import argparse
from datetime import datetime
import sys


def create_arg_parser():
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Convert batch color codes to Python constants or show ANSI color codes"
    )
    parser.add_argument(
        "--input", "-i", default="colors.bat", help="Input batch file with color codes (default: colors.bat)"
    )
    parser.add_argument("--output", "-o", default=None, help="Optional output Python file (default: print to stdout)")
    parser.add_argument(
        "--show-codes",
        "-s",
        action="store_true",
        help="Show ANSI 256-color codes in a 36x6 table instead of generating Python file",
    )
    return parser


def escape_for_fstring(value: str) -> str:
    """
    Escape braces so generated f-strings remain valid.
    """
    return value.replace("{", "{{").replace("}", "}}")


def save_python_module(py_file_path: str, python_code: str):
    """
    Save generated Python code to the given path.
    """
    Path(py_file_path).write_text(python_code, encoding="utf-8")


def bat_to_python_colors(bat_file_path: str, py_file_path: str = None) -> str:
    """
    Parse a .bat script containing 'set VAR=VALUE' color definitions
    and generate equivalent Python constants.
    """

    bat_text = Path(bat_file_path).read_text(encoding="utf-8")

    # Precompute safe path string and timestamp to avoid f-string backslash issues
    bat_path_resolved = str(Path(bat_file_path).resolve())
    # Escape backslashes explicitly (avoid \u parsing)
    safe_bat_path = bat_path_resolved.replace("\\", "\\\\")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header = '''"""
This file was generated from {path}
Date of generation: {ts}
"""
'''.format(path=safe_bat_path, ts=timestamp)

    python_lines = [
        header,
        "# Auto-generated from batch color definitions",
        'ESC = "\\033"',  # ESC substitute (common ANSI escape prefix in Python)
    ]

    pattern = re.compile(r"^\s*set\s+([A-Za-z0-9_]+)\s*=\s*(.*)$", re.IGNORECASE)

    for line in bat_text.splitlines():
        line = line.strip()
        if not line or line.lower().startswith("rem"):
            continue  # skip comments and empty lines
        match = pattern.match(line)
        if not match:
            continue

        var_name, value = match.groups()

        # Normalize variable name
        var_name = var_name.strip().upper().replace(" ", "_")

        # Prepare value safely
        value = value.strip()

        # Replace `%ESC%` with Python safe reference
        # value = value.replace("%ESC%", "ESC}")

        # Replace other `%VAR%` references
        for ref in re.findall(r"%([A-Za-z0-9_]+)%", value):
            value = value.replace(f"%{ref}%", f"{{{ref}}}")

        # Escape literal braces
        value = escape_for_fstring(value)

        # Define as f-string constant
        py_line = f'{var_name} = f"{value}"'
        # replace double f quotes
        py_line = py_line.replace("{{", "{")
        py_line = py_line.replace("}}", "}")
        python_lines.append(py_line)

    # Add __main__ block for inspection of constants
    python_lines.append('\n\nif __name__ == "__main__":')
    python_lines.append('    vars_dict = {k: f"{v}{k}{C_0}" for k, v in globals().items() if k.isupper()}')
    python_lines.append("    for _,v in vars_dict.items():")
    python_lines.append("        print(v + COL_DEFAULT)")

    python_code = "\n".join(python_lines)

    # Save only if output path was provided
    if py_file_path:
        save_python_module(py_file_path, python_code)

    return python_code


def show_color_codes():
    ESC = "\033"
    # TODO Show all colorcodes  in a 36 columns x 6 lines table in the output
    # as three number digit color_code ranging from 16 to 231 in the form
    # "{ESC}[38;5;{color_code}{str(color_code).zfill(3)}"
    ESC = "\033"
    columns = 36
    start, end = 16, 231

    for row in range(6):  # 6 rows
        line = ""
        for col in range(columns):  # 36 columns
            code = start + row * columns + col
            if code > end:
                break
            # Format as ANSI foreground color with zero-padded code
            line += f"{ESC}[38;5;{code}m{str(code).zfill(3)} {ESC}[0m "
        print(line)


def main():
    parser = create_arg_parser()
    args = parser.parse_args()

    if args.show_codes:
        show_color_codes()
        return

    try:
        python_constants = bat_to_python_colors(args.input, args.output)
        if not args.output:
            print(python_constants)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
