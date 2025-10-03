"""handling the rendering of a prompt.
COLORS CODES TO BE USED in bat file to be generated

"""

import subprocess
import os
import sys

# Add parent directory of the current file to sys.path so as to avoid import errors
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.myenv import MY_F_MYENV_PROMPT
from config.colors import C_B, C_P, C_V, C_SC, C_0, C_1

PROMPT_SYMBOL = "λ"


def get_git_branch(path="."):
    """gets the git branch for a git controlled path"""
    try:
        result = subprocess.run(
            ["git", "-C", path, "rev-parse", "--abbrev-ref", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True,
        )
        branch = result.stdout.strip()
        return branch if branch != "HEAD" else ""  # "HEAD" means detached state
    except subprocess.CalledProcessError:
        return None


def get_current_venv():
    """Tries to get the Virtual ENV NAME"""
    # Method 1: VIRTUAL_ENV env variable (most reliable if activated)
    venv = os.environ.get("VIRTUAL_ENV")
    if venv:
        return os.path.basename(venv)
    # Method 2: Compare sys.prefix to sys.base_prefix (works for venv/virtualenv)
    if hasattr(sys, "base_prefix") and sys.prefix != sys.base_prefix:
        return os.path.basename(sys.prefix)
    # Method 3: Older Python - real_prefix
    if hasattr(sys, "real_prefix"):
        return os.path.basename(sys.prefix)
    # Not in a venv
    return None


def create_prompt(path=".", reset: bool = False) -> str:
    """creates the prompt string"""
    if reset:
        return f"{C_P}$P{C_SC}$G"
    input_color = f"{C_0}"
    prompt = ""
    branch = get_git_branch(path)
    venv = get_current_venv()
    if venv:
        prompt += f"{C_V}[{venv}] "
        input_color = f"{C_1}"
    if branch:
        prompt += f"{C_B}({branch}) "

    prompt += f"{C_P}$P {C_SC}{PROMPT_SYMBOL}{input_color} "
    return prompt


def save_prompt(filepath: str, prompt: str):
    """saves the prompt string to a file"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(prompt)


def main():
    """Main entry point"""
    # Generate prompt
    prompt = f'SET "PROMPT={create_prompt()}"'
    # print("Generated prompt:", prompt)
    # Save to configured file
    save_prompt(MY_F_MYENV_PROMPT, prompt)
    # print(f"Prompt saved to {MY_F_MYENV_PROMPT}")


if __name__ == "__main__":
    main()
