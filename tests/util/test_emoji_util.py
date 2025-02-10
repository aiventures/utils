"""Unit Tests for the Constants Class"""

import logging
import os
import json
from copy import deepcopy
from enum import Enum
from unittest.mock import MagicMock

import pytest

import util.constants as C
from util.emoji_util import EmojiIndicator, EmojiUtil
from cli.bootstrap_env import CLI_LOG_LEVEL

from model.model_emoji import EmojiMetaDictType
from model.model_filter import SimpleStrFilterModel

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)


def test_emojiutil_metadata():
    """testing the emoji metadata classes"""

    # parse emoji metadata as model and back to json
    metadata: EmojiMetaDictType = EmojiUtil.get_emoji_metadata(skip_multi_char=False)
    class_filter = None
    subclass_filter = None
    key_filter = None
    # filter out some symbols containing colors
    description_filter = "BLUE,RED,Black"
    description_filter = SimpleStrFilterModel(str_filter=description_filter)

    metadata_filtered = EmojiUtil.filter_emoji_metadata(
        metadata, class_filter, subclass_filter, description_filter, key_filter
    )
    assert isinstance(metadata_filtered, dict)
    # converting it into bytes and into string / set alias to true to export class_ attribute as class
    _dict = EmojiUtil.to_dict(metadata_filtered)
    _json_s = EmojiUtil.to_json(metadata_filtered)
    assert isinstance(json.loads(_json_s), dict)
    assert isinstance(_dict, dict)

    # creating hierarchy
    metadata_hierarchy = EmojiUtil.emoji_hierarchy(metadata_filtered, result_type="unicode_first_char")
    assert isinstance(metadata_hierarchy, dict)

    for _, _info in metadata_filtered.items():
        # check conversion
        assert isinstance(EmojiUtil.unicode2emoji(_info.code, only_first_code=True), str)


def test_emoji_indicator():
    """testing the indicator"""
    emoji_list = EmojiIndicator.render_list(num_values=10, rendering="spectral", emoji_type="circle")
    # # get an indicator using emoji list
    emoji_indicator = EmojiIndicator(min_value=0, max_value=100, emojis=emoji_list)
    out = []
    for n in range(0, 101, 5):
        out.append(f"([{str(n).zfill(2)}] {emoji_indicator.render(n, add_percentage=False)}),")
    assert isinstance(out, list) and len(out) > 0


def test_emoji_unicode():
    """test rendering of emojis based on unicode"""
    _emoji = EmojiUtil.unicode2emoji("U+1F9D9 U+200D U+2640 U+FE0F")
    _emoji2 = EmojiUtil.unicode2emoji("U+1F9D9 U+200D U+2640 U+FE0F", only_first_code=True)
    assert isinstance(_emoji, str)
    assert isinstance(_emoji2, str)
    assert _emoji != _emoji2
