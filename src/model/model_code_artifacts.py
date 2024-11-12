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
    p_root: Union[str|list]=None
    max_path_depth: Optional[int]=None
    artifact_type: CodeArtifactEnum = CodeArtifactEnum.GIT
    artifact_filter: Optional[Dict]=None
    show_progress: Optional[bool]=False


