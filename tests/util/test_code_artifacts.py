""" Testing The Code Artifact Class """

import os
import logging
import pytest
from pathlib import Path

from util import constants as C
from util.code_artifacts import CodeArtifact


logger = logging.getLogger(__name__)
# get log level from environment if given 
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL,logging.INFO)))

def test_code_artifact(fixture_path_testdata):
    """ Basic Test of Code Artifact Constructor, get the git artifacts root folder """
    git_artifact = CodeArtifact(p_root=fixture_path_testdata,max_path_depth=2)
    artifact_type = git_artifact.artifact_type
    artifacts = git_artifact.artifacts
    pass
