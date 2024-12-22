"""Testing The Code Artifact Class"""

import logging
import os
from pathlib import Path

import pytest

# from model.model_worklog import WorkLogT
from util.worklog_txt import WorkLogTxt
from enum import Enum, StrEnum,EnumMeta

# from model.model_code_artifacts import CodeArtifactEnum as ARTIFACT
from util import constants as C
# from util.code_artifacts import CodeArtifacts, CodeMetaDict, GitArtifact, VenvArtifact, VsCodeArtifact
# from util.persistence import Persistence

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))

def test_add_shortcodes():
    """adding shortcodes """
    year = 2024
    add_shortcodes = {"SHORTCODE":"SHORTCODE_VALUE"}
    _enum = WorkLogTxt.add_shortcodes(add_shortcodes)
    assert isinstance(_enum,EnumMeta)


