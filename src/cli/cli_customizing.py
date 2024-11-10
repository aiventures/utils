""" Configuration and Env Client """

import logging
from typing_extensions import Annotated
import os
#import sys
#import json
import typer
from rich import print as rprint
from rich.console import Console
# from rich.markup import escape as esc
from rich.logging import RichHandler
import json
from rich import print_json
#from pathlib import Path
#from util.persistence import Persistence
from util import constants as C
from util.constants import DEFAULT_COLORS as CMAP
from util.emoji import show_rich_emoji_codes
# from util.config_env import ConfigEnv
from cli.bootstrap_config import config_env,console_maker
from cli.bootstrap_env import OS_BOOTSTRAP_VARS
from util_cli.cli_color_mapper import ColorMapper
# from util_cli import

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL,logging.INFO)))

app = typer.Typer(name="cli_config_client", add_completion=True, help="Command Line Client Customizing (Colors, Locations, Envionment Setup)")

@app.command("bootstrap")
def show_bootstrap_config():
    """Display Bootstrap OS ENV Parameters (cli.bootstrap_config)
    """
    rprint(f"[{CMAP['out_title']}]### ENV BOOTSTRAP CONFIGURATION (cli.bootstrap_env)")
    print_json(json.dumps(OS_BOOTSTRAP_VARS))

@app.command("show")
@app.command("s")
def show_config():
    """ Display configuration environment"""
    config_env.show()

@app.command("show-json")
@app.command("j")
def show_config_json():
    """ Display configuration environment as json together with the bootstrap configuration"""
    config_env.show_json()
    # show the env bootsrapping config
    show_bootstrap_config()

@app.command("ansi-colors")
def show_ansi_colors(with_names:bool=False):
    """Display ANSI Colors

    Args:
        with_names (bool, optional): Also render the rich color names. Defaults to False.
    """
    _console = console_maker.get_console()
    _ansi_table = ColorMapper.get_ansi_table(with_names)
    _console.print(_ansi_table)

@app.command("themes")
def show_themes_and_styles(theme:str=None):
    """Display available styles and themes

    Args:
        theme (str, optional): theme . Defaults to None (=drefault theme).
    """
    _console = console_maker.get_console(theme=theme)
    _theme = console_maker.theme
    _themes = console_maker.themes
    _styles = console_maker.style_names
    _console.print("[out_title]### Themes")
    _console.print(f"*   {_themes}")
    _console.print(f"[out_title]### Selected Theme [list_key]\[{_theme}]")
    for _style in _styles:
        _s_style=f"\[{_style}]"
        _console.print(f"[out_title]*   {_s_style:<19}[{_style}]THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG")

@app.command("theme-preview")
def show_theme_preview(theme:str=None):
    """Display styles using themes manager

    Args:
        theme (str, optional): Set theme. Defaults to None  (=drefault theme).
    """
    _console = console_maker.get_console(theme=theme)
    _console.print("[out_title]### Themes List")
    console_maker.list_themes()
    _console.print(f"[out_title]### Preview Theme \[{console_maker.theme}]")
    console_maker.preview_theme(console_maker.theme)

@app.command("color-map")
def show_color_map(num_cols:int=4,colors:str|None=None):
    """show color maps

    Args:
        cols (int, optional): number of columns. Defaults to 4.
        colors (str | None, optional): use comma separated string
        to filter resulting list  (for example filter use 'red,green')
        to display colors with green and red in their name
    """
    _colors = None
    if colors:
        _colors = colors.split(",")
    ColorMapper().show_colors(num_colums=num_cols,colors=_colors)

@app.command("emojis")
def show_emojis(emoji_filter:str|None=None,only_meta:bool=True):
    """Display Emojis

    Args:
        emoji_filter (str | None, optional): comma separated string of key search terms . Defaults to None.
        only_meta (bool, optional): Only Display emojis with meta data. Defaults to True.
    """
    _emoji_filter = None
    if emoji_filter:
        _emoji_filter = emoji_filter.split(",")
    show_rich_emoji_codes(_emoji_filter,only_meta)

# TODO Create Themes Using Theme Console Constructor

# https://typer.tiangolo.com/tutorial/commands/callback/
@app.callback()
def main():
    """ main method """
    pass

if __name__ == "__main__":
    log_level = os.environ.get(C.ConfigBootstrap.CLI_CONFIG_LOG_LEVEL.name,C.ConfigBootstrap.CLI_CONFIG_LOG_LEVEL.value)
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=log_level, datefmt="%Y-%m-%d %H:%M:%S",
                        handlers=[RichHandler(rich_tracebacks=True)])
    app()

