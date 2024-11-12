""" Testing The Code Artifact Class """

import os
import logging
import pytest
from pathlib import Path

from util import constants as C
from util.code_artifacts import ( CodeArtifact,
                                  CodeArtifacts,
                                  VsCodeArtifact,
                                  GitArtifact,
                                  VenvArtifact )
from model.model_code_artifacts import ( ArtifactMeta,
                                         CodeArtifactEnum as ARTIFACT )

logger = logging.getLogger(__name__)
# get log level from environment if given 
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL,logging.INFO)))

def test_code_artifact(fixture_path_testdata):
    """ Basic Test of Code Artifact Constructor, get the git artifacts root folder """
    artifact_meta = ArtifactMeta()
    artifact_meta.p_root = fixture_path_testdata
    artifact_meta.max_path_depth = 5
    artifact_meta.artifact_type = ARTIFACT.VSCODE
    git_artifact = CodeArtifact(artifact_meta)
    artifact_type = git_artifact.artifact_type
    artifacts = git_artifact.artifacts
    assert isinstance(artifacts,dict)

def test_code_artifacts(fixture_path_testdata):
    """ Basic Test of Code Artifacts Constructor, that gets  """    
    _artifact_list = []
    _git_meta = ArtifactMeta(p_root=fixture_path_testdata,max_path_depth=2,artifact_type=ARTIFACT.GIT)
    _venv_meta = ArtifactMeta(p_root=fixture_path_testdata,max_path_depth=5,artifact_type=ARTIFACT.VENV)
    _vscode_meta = ArtifactMeta(p_root=fixture_path_testdata,max_path_depth=2,artifact_type=ARTIFACT.VSCODE)    
    _artifact_meta_list = [_git_meta,_venv_meta,_vscode_meta]
    _artifacts = CodeArtifacts(_artifact_meta_list)
    pass
    