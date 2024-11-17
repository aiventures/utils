""" Testing The Code Artifact Class """

import os
import logging
import pytest
from pathlib import Path

from util import constants as C
from util.code_artifacts import ( CodeArtifacts,
                                  VsCodeArtifact,
                                  GitArtifact,
                                  VenvArtifact )
from model.model_code_artifacts import ( ArtifactMeta,
                                         CodeArtifactEnum as ARTIFACT )

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL,logging.INFO)))

def test_git_artifact(fixture_path_testdata):
    """ Basic Test of Code Artifact Constructor, get the git artifacts root folder """
    artifact_meta = ArtifactMeta()
    artifact_meta.p_root = fixture_path_testdata
    artifact_meta.max_path_depth = 5
    artifact_meta.artifact_type = ARTIFACT.GIT
    # artifact_meta.paths_only = True
    _artifact = GitArtifact(artifact_meta)
    artifact_type = _artifact.artifact_type
    artifacts = _artifact.artifacts
    _artifact.read_content()
    assert isinstance(artifacts,dict)
    assert len(artifacts) > 0
    assert len(_artifact._info_dict)>0

def test_venv_artifact(fixture_path_testdata):
    """ Basic Test of Code Artifact Constructor, get the git artifacts root folder """
    artifact_meta = ArtifactMeta()
    artifact_meta.p_root = fixture_path_testdata
    artifact_meta.max_path_depth = 6
    artifact_meta.artifact_type = ARTIFACT.VENV
    # artifact_meta.paths_only = True
    _artifact = VenvArtifact(artifact_meta)
    artifact_type = _artifact.artifact_type
    artifacts = _artifact.artifacts
    _artifact.read_content()
    assert isinstance(artifacts,dict)
    assert len(artifacts) > 0
    assert len(_artifact._info_dict)>0

def test_vscode_artifact(fixture_path_testdata):
    """ Basic Test of Code Artifact Constructor, get the git artifacts root folder """

    artifact_meta = ArtifactMeta()
    artifact_meta.p_root = fixture_path_testdata
    artifact_meta.max_path_depth = 5
    artifact_meta.artifact_type = ARTIFACT.VSCODE
    artifact_meta.show_progress = True
    _artifact = VsCodeArtifact(artifact_meta)
    _artifact_type = _artifact.artifact_type
    assert _artifact_type == ARTIFACT.VSCODE
    _artifact.read_content()
    assert len(_artifact._info_dict)>0    

def test_code_artifacts(fixture_path_testdata):
    """ Basic Test of Code Artifacts Constructor, that gets  """
    _artifact_list = []
    _git_meta = ArtifactMeta(p_root=fixture_path_testdata,max_path_depth=2,artifact_type=ARTIFACT.GIT)
    _venv_meta = ArtifactMeta(p_root=fixture_path_testdata,max_path_depth=5,artifact_type=ARTIFACT.VENV)
    _vscode_meta = ArtifactMeta(p_root=fixture_path_testdata,max_path_depth=2,artifact_type=ARTIFACT.VSCODE)
    _artifact_meta_list = [_git_meta,_venv_meta,_vscode_meta]
    _artifacts = CodeArtifacts(_artifact_meta_list)
    # load content
    _artifacts.read_content()
    # test the link
    _artifacts.link_vscode2git(True)
    pass
