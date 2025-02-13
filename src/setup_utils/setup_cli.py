"""creates a demo config file with real paths"""

import sys
import os
import logging
from rich.prompt import Confirm
from rich import print as rprint
from util import constants as C
from util.emoji_util import EmojiUtil
from setup_utils.demo_config import create_config_home
from cli.bootstrap_env import setup

from cli.bootstrap_env import (
    CLI_LOG_LEVEL,
    FILE_CONFIGFILE_HOME,
    OS_BOOTSTRAP_VARS,
    PATH_RESOURCES,
    PATH_HOME_RESOURCES,
)


logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)


def main():
    """all in one runner for setting up cli util"""

    rprint("\n[gold3]### Environment variables[/]")
    rprint(OS_BOOTSTRAP_VARS)
    rprint("\n[gold3]### Create CLI Artefacts[/]")
    _download_emoji_meta = Confirm.ask(
        f":inbox_tray: [red](1)[medium_purple1] Download Emoji Metadata fom unicode to [gold1]\[{PATH_RESOURCES}][/]?"
    )
    _create_emoji_json = Confirm.ask(
        f":outbox_tray: [red](2)[medium_purple1] Create emoji.json metadata ton [gold1]\[{PATH_RESOURCES}][/]?"
    )
    _copy_resources = Confirm.ask(
        f":squid: [red](3)[medium_purple1] Copy Resources and Test Aritfacts to [gold1]\[{PATH_HOME_RESOURCES}][/]?"
    )
    _create_sample_config = Confirm.ask(
        f":pencil: [red](4)[medium_purple1] Create sample config file  [gold1]\[{FILE_CONFIGFILE_HOME}][/]?"
    )

    rprint("\n[gold3]### Executing Actions[/]")
    if _download_emoji_meta:
        EmojiUtil.download_emoji_sequences()
    if _create_emoji_json:
        EmojiUtil.parse_emoji_sequences_to_dict()
    if _copy_resources:
        setup()
    if _create_sample_config:
        create_config_home(overwrite_if_exist=True)


if __name__ == "__main__":
    loglevel = os.environ.get(C.ConfigBootstrap.CLI_CONFIG_LOG_LEVEL.name, C.ConfigBootstrap.CLI_CONFIG_LOG_LEVEL.value)
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=loglevel,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    main()
