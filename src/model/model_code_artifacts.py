""" Pydantic model for the code_artifacts class """
from pydantic import BaseModel
from typing import List,Optional,Union,Dict
from enum import Enum

class CodeArtifactEnum(Enum):
    """ Enum for Code Artifacts """
    GIT = "git"
    VENV = "venv"
    VSCODE = "vscode"

class ArtifactMeta(BaseModel):
    """ Code artifact structure """
    # root folder
    p_root: Union[str|list]=None
    # search up to macx depth
    max_path_depth: Optional[int]=None
    # type of code artifact
    artifact_type: CodeArtifactEnum = CodeArtifactEnum.GIT
    # filtering search results
    artifact_filter: Optional[Dict]=None
    # show progress bar
    show_progress: Optional[bool]=False
    # find only paths not files
    paths_only: Optional[bool]=False

class VsCodeMeta(BaseModel):
    """ VsCodeFile Representation """
    # absolute path to a vscode file
    f_vscode : str
    # project folders stored in VSCode project file
    p_folders:List[str] = []

class GitMeta(BaseModel):
    """ Git Metadata Representation """
    # absolute path to the git controlled repository
    p_repo : str
    # repo path root name
    p_name : str
    # current branch (HEAD)
    branch_current : str=None
    # local branch list (config)
    branch_list_local : List[str]=None
    # remote url
    repo_url : str=None

class VenvMeta(BaseModel):
    """ Virtual Venv Metadata Representation """
    # absolute path to the VENV
    p_venv : str
    # venv root name 
    venv_name : str = None
    # python version
    python_version : str = None
    # original executable
    executable : str = None
    # list of installed modules
    package_list : List[str]=None

