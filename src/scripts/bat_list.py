#!/usr/bin/env python3
"""

Batch file search, processing, and command generation script.

Features:
- Reads .bat files from given directories or paths.
- Extracts first REM comment for descriptions.
- Uses ANSI colors for formatted output.
- Case-insensitive search with ':' (AND) and ';' (OR) support.
- Highlights search matches.
- Displays "### PATH" header only once per directory.
- Dynamically aligns filenames to the longest in the list for neat output.
- Allows interactive command selection and parameter input.
- Writes command output to a file initialized with a default "Nothing To Do..." line.

Prompt:

write a python script:
- read all files from a list of paths or a single path.
- Select all b atch files for use in windows command line with the ".bat" suffix and put the results into a dict:
  the key an index number and a "path" attribute containing the absolute path, and an "index" attribute containing that number
- read each file by lines and if there is a line startin with rem command (upper or lowercase), copy out the string after that
  command and skip processing of reading lines. Add the found string to the previous dict to the corresponding entry
  for that file in the dict as "text" attribute. if no rem command is found add a description "no text found" instead.
- Add ANSI COLOR CODES so it is possible to use colored output using f strings like f"{C_T}text{C_0}".
  Color Codes the following, check the preceding comment on how to use them:
    rem set colors for certain use case
    rem reset all color formatting
    set C_0=%COL_RESET%
    rem title
    set C_T=%COL_BLUE_SKY%
    rem search keys
    set C_S=%COL_ORANGE%
    rem file keys
    set C_F=%COL_BLUE_SKY%
    rem highlighted output
    set C_H=%COL_YELLOW_PALE_229%
    rem python output
    set C_PY=%COL_GREEN%
    rem question / prompt
    set C_Q=%C_MAG%
    rem program
    set C_PROG=%COL_PINK%
    rem ERROR
    set C_E=%COL_RED%
    rem index number
    set C_I=%COL_GREEN_AQUA_85%
- provide a function that will print out the dictionary as a list:
  - absolute path as header line f"{C_T}### PATH {C_}{}"
  - below, each found line, provide a line, consisting: f"{C_I}[{index}] {C_F}{file_name}: {C_H}{text}"
- close with a final print of "{C_0}" to reset color formatting for the output
- provide the printing of the list in a separate function
- now also provide an input dialogue (Colored in color code C_Q) that allows for input of the index number
  to provide a command string. if there are params in the description as indicated by square brackets [...],
  make sure that the correct number of arguments is supplied. With the exception: if the string in the brackets
  will contain an "optional" or "default" then reduce the number of mandatory arguments by the number of arguments
  being either "optional" or "default". The generated line in the out put file will be a batch command: call
  "(absolute path of selected batch script)", followed by the list of supplied input arguments from the user input (if there are commands )
- Also allow the option to select no script at all by entering nothing
- store the entered input string as single line into a file that is referenced by a variable F_CMD_DEFAULT
- modularize into functions, provide argparse arguments to provide the path or a list of paths. Also provide a
  P_BAT_DEFAULT variable to define a default path to the bat files, in case nothing is passed. Also add another
  argparse parameter to store the command (if nothing provided use F_CMD_DEFAULT).provide a main method so it can run stand alone.
- now also add another function to the script to allow for search within the search script. Add an additional
  --query/-q argparse argument to allow to query the list. if executed render out the list as before, but filter
  by passed argument string. A query of term1:term2 indicates ALL of the terms need to be present in the "text",
  whereas as a term of term1;term2 indicates ALL terms need to be represent. If only a single term is supplied then
  apply the search as if it was searched for ANY terms search, but only with a single search term. Make the search case
  insensitive. If not query term is supplied, then treat this as default case, so that the complete list is shown.
  Also in the list, color highlight the found search terms in the text output using
  a new C_H color code (using a pink ANSI COlor) to highlight the occurences of the query terms.
- move the argparser construction into a separate function
- add docstrings to each function
- add type hints to all functions and variable declarations. Add new typing definitions such as Union
- Adjust the padding in the output list: so that the file name length in the result list matches the longest script name

"""

import os
import argparse
import re
import sys
from typing import List, Dict, Union, Optional

# Add parent directory of the current file to sys.path so as to avoid import errors
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config.myenv import MY_P_UTILS_BAT, MY_P_MYENV
from config.colors import C_0, C_T, C_F, C_H, C_Q, C_PROG, C_E, C_I, C_S, C_SH, C_PY

# === Default Configuration ===
P_BAT_DEFAULT: str = MY_P_UTILS_BAT
F_CMD_DEFAULT: str = os.path.join(MY_P_MYENV, "cmd_bat_list.env")


def initialize_output_file(output_file: str) -> None:
    """
    Initialize the output file with the default placeholder command.

    Args:
        output_file: The path of the file to initialize.

    Behavior:
        - Overwrites the output file with a single line:
          'echo %C_H%Nothing To Do...%C_0%'
        - Displays an info message if successful or an error if failed.
    """
    default_line = "echo %C_H%Nothing To Do...%C_0%"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(default_line + "\n")
        print(f"{C_PROG}Initialized command file with default message: {output_file}{C_0}")
    except Exception as e:
        print(f"{C_E}Error initializing output file {output_file}: {e}{C_0}")


def read_bat_files(paths: Union[str, List[str]]) -> Dict[int, Dict[str, str]]:
    """
    Read batch (*.bat) files from supplied directories or file paths.

    Args:
        paths: A single path or list of paths to scan for batch files.

    Returns:
        Dictionary mapping index numbers to metadata:
        {
            index: {
                "index": int,
                "path": absolute file path,
                "text": extracted description or "no text found"
            }
        }
    """
    if isinstance(paths, str):
        paths = [paths]
    bat_files: List[str] = []
    for path in paths:
        if os.path.isdir(path):
            for fname in os.listdir(path):
                if fname.lower().endswith(".bat"):
                    bat_files.append(os.path.join(os.path.abspath(path), fname))
        elif path.lower().endswith(".bat"):
            bat_files.append(os.path.abspath(path))
    result: Dict[int, Dict[str, str]] = {}
    for idx, f in enumerate(sorted(bat_files), start=1):
        result[idx] = {"index": idx, "path": f, "text": extract_rem_text(f)}
    return result


def extract_rem_text(filepath: str) -> str:
    """
    Extract the first 'REM' comment (case-insensitive) from a batch file.

    Args:
        filepath: Absolute path of the .bat file.

    Returns:
        The string following the first REM command, or
        "no text found" if absent or the file cannot be read.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                if line.strip().lower().startswith("rem "):
                    return line.strip()[4:].strip()
    except Exception as e:
        print(f"{C_E}Error reading {filepath}: {e}{C_0}")
    return "no text found"


def highlight_text(text: str, terms: List[str], font_color: str = C_0) -> str:
    """
    Highlight all search term occurrences in text using ANSI color codes.

    Args:
        text: Input text to highlight.
        terms: List of search terms (case-insensitive).
        font_color: original font color

    Returns:
        Modified text with occurrences wrapped with C_H color codes.
    """
    for term in terms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        text = pattern.sub(lambda m: f"{C_SH}{m.group(0)}{font_color}", text)
    return f"{font_color}{text}"


def filter_dict(files_dict: Dict[int, Dict[str, str]], query: Optional[str]) -> Dict[int, Dict[str, str]]:
    """
    Filter a list of batch files by search terms.

    Args:
        files_dict: Dictionary containing batch file metadata.
        query: Search criteria (case-insensitive):
               ':' = all terms required, ';' = any match, or single term = any match.

    Returns:
        Filtered dictionary matching the query.
    """
    if not query:
        return files_dict

    def contains_all(text: str, terms: List[str]) -> bool:
        return all(t.lower() in text.lower() for t in terms)

    def contains_any(text: str, terms: List[str]) -> bool:
        return any(t.lower() in text.lower() for t in terms)

    if ":" in query:
        terms = [t.strip() for t in query.split(":") if t.strip()]
        return {k: v for k, v in files_dict.items() if contains_all(v["text"], terms)}
    elif ";" in query:
        terms = [t.strip() for t in query.split(";") if t.strip()]
        return {k: v for k, v in files_dict.items() if contains_any(v["text"], terms)}
    else:
        term = query.strip()
        return {k: v for k, v in files_dict.items() if term.lower() in v["text"].lower()}


def print_bat_dict(files_dict: Dict[int, Dict[str, str]], query: Optional[str] = None) -> None:
    """
    Print aligned, color-coded batch file list grouped by directory.

    Args:
        files_dict: Dictionary of batch files with path and description.
        query: Terms for highlighting (optional).

    Behavior:
        - Each directory is shown with a single "### PATH" header.
        - Each filename is padded to match the longest file name for alignment.
        - Search terms are highlighted in color when present.
    """
    if not files_dict:
        print(f"{C_E}No batch files found.{C_0}")
        return

    highlight_terms: List[str] = []
    if query:
        sep = ":" if ":" in query else (";" if ";" in query else None)
        highlight_terms = [t.strip() for t in query.split(sep)] if sep else [query.strip()]

    # Determine longest filename for alignment
    longest_name: int = max(len(os.path.basename(entry["path"])) for entry in files_dict.values())

    current_dir: Optional[str] = None
    text_color = C_H
    for entry in files_dict.values():
        dir_name = os.path.dirname(entry["path"])
        if dir_name != current_dir:
            current_dir = dir_name
            print(f"{C_T}### PATH {C_0}{dir_name}")

        fname = os.path.basename(entry["path"])
        padded_name = fname.ljust(longest_name)

        text_out = highlight_text(entry["text"], highlight_terms, text_color) if highlight_terms else entry["text"]
        print(f"{C_I}[{str(entry['index']).zfill(3)}] {C_F}{padded_name}: {text_color}{text_out}")
    print(C_0)


def input_command_interactive(files_dict: Dict[int, Dict[str, str]], output_file: str = F_CMD_DEFAULT) -> None:
    """
    Prompt the user for a script selection and optional arguments.

    Args:
        files_dict: Dictionary of available scripts and metadata.
        output_file: Path to write the constructed command line.

    Behavior:
        - Displays available file indices and waits for user input.
        - If no input is given, existing file content remains unchanged.
        - Validates required and optional parameters from REM description.
        - Saves generated Windows "call" command line to output file.
    """
    choice: str = input(f"{C_Q}Enter index number (or Enter to skip): {C_0}").strip()
    if not choice:
        print(f"{C_PROG}No selection made. Default message remains in {output_file}{C_0}")
        return

    if not choice.isdigit() or int(choice) not in files_dict:
        print(f"{C_E}Invalid index selection.{C_0}")
        return

    selected = files_dict[int(choice)]
    text = selected["text"]
    params = re.findall(r"\[(.*?)\]", text)
    mandatory = [p for p in params if "optional" not in p.lower() and "default" not in p.lower()]
    args: List[str] = []

    # Ask user for each detected parameter
    for p in params:
        if "optional" in p.lower() or "default" in p.lower():
            val = input(f"{C_Q}Optional/default param {p} (Enter to skip): {C_0}").strip()
            if val:
                args.append(val)
        else:
            val = input(f"{C_Q}Required param {p}: {C_0}").strip()
            args.append(val)

    if len(args) < len(mandatory):
        print(f"{C_E}Missing mandatory parameters.{C_0}")
        return

    cmd_line = f'call "{selected["path"]}" {" ".join(args)}'.strip()
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(cmd_line + "\n")
    print(f"{C_PROG}Command saved to {output_file}:{C_0} {cmd_line}")


def get_argparser() -> argparse.ArgumentParser:
    """
    Build and configure the argument parser for CLI execution.

    Returns:
        argparse.ArgumentParser: Configured parser with supported options.
    """
    parser = argparse.ArgumentParser(description="Case-insensitive batch file search and executor.")
    parser.add_argument(
        "-p",
        "--paths",
        nargs="*",
        default=[P_BAT_DEFAULT],
        help="Path(s) to batch files or directories (default=P_BAT_DEFAULT).",
    )
    parser.add_argument(
        "-c", "--command", default=F_CMD_DEFAULT, help="Path to save generated command (default=F_CMD_DEFAULT)."
    )
    parser.add_argument(
        "-q", "--query", default=None, help="Search query (':'=AND, ';'=OR, single=ANY). Case-insensitive."
    )
    return parser


def main() -> None:
    """
    Main program entry point.

    Workflow:
        1. Initialize output file with default message.
        2. Parse CLI arguments.
        3. Scan directories for batch files.
        4. Print formatted list with optional term highlighting.
        5. Prompt user interaction to generate command line.
    """
    parser = get_argparser()
    args = parser.parse_args()

    initialize_output_file(args.command)
    files_dict = read_bat_files(args.paths)
    filtered = filter_dict(files_dict, args.query)
    print_bat_dict(filtered, args.query)
    input_command_interactive(filtered, args.command)


if __name__ == "__main__":
    main()
