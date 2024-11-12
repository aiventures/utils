""" Reading Code Artifacts from environment or files such as git, venv,... """

import sys
import logging
from enum import Enum
import os
from copy import deepcopy
from typing import List,Optional,Union,Dict
from util import constants as C
from util.utils import Utils
from util.persistence import Persistence
from cli.bootstrap_config import config_env,console_maker
from model.model_code_artifacts import CodeArtifactEnum as ARTIFACT,ArtifactMeta

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL,logging.INFO)))

if __name__ == '__main__':
    loglevel = logging.INFO
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=loglevel, stream=sys.stdout, datefmt="%Y-%m-%d %H:%M:%S")

#ARTIFACT_GIT = "git"
#ARTIFACT_VENV = "venv"
#ARTIFACT_VSCODE = "vscode"
# default filter for most common artifact files
# os dependent paths definition
venv_regex = "scripts\\\\activate" if Utils.is_windows() else "scripts\/activate"
ARTIFACT_FILTER = { ARTIFACT.GIT:   {"include_paths":".git$"},
                   ARTIFACT.VSCODE:{"include_files":".code-workspace"},
                   ARTIFACT.VENV:  {"include_abspaths":venv_regex}}

# COPY TEMPLATE FOR INSTANCIATING 
ARTIFACT_INPUT_TEMPLATE={"p_root":None,"max_path_depth":3,"artifact_type":ARTIFACT.GIT,"show_progress":False}

class CodeArtifact():
    """ Reading Code Artifacts from environment or files such as git, venv,... """
    def __init__(self,artifact_meta:ArtifactMeta=ArtifactMeta()):
        """_summary_

        Args:
            artifact_meta (ArtifactMeta, optional): Constructor. Defaults to ArtifactMeta().
            Params Infos
            p_root (str|list): Entry Path (single or list) containing all entry paths. If initial,
            it will default to current directory
            max_path_depth (int, optional): max folder depth to search from root path. Defaults to None.
            artifact: filter to be applied to capture siognature of a certain code artifact
            show_progress (bool, optional): showing search indicator. Defaults to False.            
        """        

        p_root = artifact_meta.p_root
        max_path_depth = artifact_meta.max_path_depth
        artifact_type = artifact_meta.artifact_type
        artifact_filter = artifact_meta.artifact_filter
        show_progress = artifact_meta.show_progress

        # initalize / resolve paths
        if p_root is None:
            p_root = os.getcwd()
        self._p_root_list = p_root
        if isinstance(self._p_root_list,str):
            self._p_root_list = [p_root]
        self._max_path_depth = max_path_depth
        self._show_progress = show_progress
        _path_refs = []
        for _p_root in  self._p_root_list:
            # checkl if it is a path other wise try toresolve reference
            _ref = None
            if os.path.isdir(_p_root):
                _ref = _p_root
            else:
                _ref = config_env.get_ref(key=_p_root)
            if _ref is not None:
                _path_refs.append(_ref)        
        self._p_root_list = _path_refs
        # initialize filter
        self._artifact_type = artifact_type
        if artifact_type is not None:
            self._artifact_filter = deepcopy(ARTIFACT_FILTER[artifact_type])
        elif isinstance(artifact_filter,dict):
            self._artifact_filter = deepcopy(artifact_filter)
        else:
            logger.warning(f"[CodeArtifact] No Filter Dict or Artifact type {list(ARTIFACT_FILTER.keys())} was transferred")
            return 
        self._artifact_filter["as_dict"]=True
        self._artifact_filter["p_root_paths"]=_path_refs
        if self._max_path_depth is not None:
            self._artifact_filter["max_path_depth"] = self._max_path_depth
        self._artifact_filter["show_progress"] = self._show_progress   
        self._artifacts = {}
        self._read_artifacts()        
   
    def _read_artifacts(self)->dict:
        """ reads the artifact files according to filter """
        self._artifacts  = Persistence.find(**self._artifact_filter)
        return self._artifacts
    
    @property
    def artifacts(self):
        """ returns read artifacts """
        return self._artifacts
    
    @property
    def artifact_type(self):
        """ returns artifact type """
        return self._artifact_type
    
class GitArtifact(CodeArtifact):
    """  Git Code Artifact Parsing """
    def __init__(self, artifact_meta:ArtifactMeta=ArtifactMeta()) -> None:
        super().__init__(artifact_meta)
        self._artifact_type = ARTIFACT.GIT

class VenvArtifact(CodeArtifact):
    """  Virtual Environment Code Artifact Parsing """
    def __init__(self, artifact_meta:ArtifactMeta=ArtifactMeta()) -> None:
        super().__init__(artifact_meta)
        self._artifact_type = ARTIFACT.VENV

class VsCodeArtifact(CodeArtifact):
    """  VS Code Project Code Artifact Parsing """
    def __init__(self, artifact_meta:ArtifactMeta=ArtifactMeta()) -> None:
        super().__init__(artifact_meta)    
        self._artifact_type = ARTIFACT.VSCODE

ARTIFACT_CLASS = { ARTIFACT.GIT:   GitArtifact,
                   ARTIFACT.VSCODE:VsCodeArtifact,
                   ARTIFACT.VENV:  VenvArtifact }

class CodeArtifacts():
    """ handling all Code Artifacts Types in one class """

    def __init__(self,artifacts_meta:List[ArtifactMeta]) -> None:
        """Constructor to handle any of the Code Artifact Types

        Args:
            artifact_metas (List[Dict[ARTIFACT,ArtifactMeta]]): 
        """
        self._artifacts = {}

        # instanciate classes 
        for _artifact_meta in artifacts_meta:
            _type = _artifact_meta.artifact_type
            try:
                self._artifacts[_type] = ARTIFACT_CLASS[_type](_artifact_meta)
            except AttributeError:
                logger.warning(f"[CodeArtifacts] unknown type [{_type}]")
        pass
    
    @property
    def vscode_artifact(self)->VsCodeArtifact:
        """ returns VS Code artifact """
        return self._artifacts.get(ARTIFACT.VSCODE,None)

    @property
    def git_artifact(self)->GitArtifact:
        """ returns VS Code artifact """
        return self._artifacts.get(ARTIFACT.GIT,None)

    @property
    def venv_artifact(self)->VenvArtifact:
        """ returns VS Code artifact """
        return self._artifacts.get(ARTIFACT.VENV,None)        
    

    
    
        
        





        # param for the din filter depending on the Code Artifact Type
        # HEAD / config
        #for _p_root in self._p_root_list:
        # include_abspaths
    #     _kwargs = {
    #     }
    # def find(_p_root_paths:list|str=None,
    #          include_abspaths:list|str=None,exclude_abspaths:list|str=None,
    #          include_files:list|str=None,exclude_files:list|str=None,
    #          include_paths:list|str=None,exclude_paths:list|str=None,
    #          paths:bool=False,files:bool=True,as_dict:bool=False,
    #          root_path_only:bool=False,
    #          match_all:bool=False,ignore_case:bool=True,
    #          show_progress:bool=True,
    #          max_path_depth:int=None)->list|dict:

        # _params = {"path_dict":_path_dict,
        #             "paths_out":_paths_out,
        #             "files_out":_files_out,
        #             "p_root":_root_path,
        #             "root_path_only":root_path_only,
        #             "re_include_paths":_re_include_paths,
        #             "re_exclude_paths":_re_exclude_paths,
        #             "re_include_files":_re_include_files,
        #             "re_exclude_files":_re_exclude_files,
        #             "re_include_abspaths":_re_include_abspaths,
        #             "re_exclude_abspaths":_re_exclude_abspaths,
        #             "match_all":match_all,
        #             "show_progress":show_progress,
        #             "max_path_depth":max_path_depth}





        # self._p_root_work_list = p_work
        # if isinstance(self._p_root_work_list,str):
        #     self._p_root_work_list = [p_work]


        # self._p_venv = config_env.get_ref(key=p_venv,fallback_default=os.getcwd())
        # self._p_work = config_env.get_ref(key=p_work,fallback_default=os.getcwd())

# class VirtualEnvironment():
#     """ Abstaction of the virutal environment """
#     def __init__(self) -> None:
#         """ Constructor """
#         return

# class Git():
#     """ Abstraction of Git """
#     def __init__(self,p_git:list|str) -> None:
#         """ Constructor """
#         _p_list = []
#         if isinstance(p_git,str):
#             _p_list = [p_git]
#         else:
#             _p_list = p_git
#         return

# classs


