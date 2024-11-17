""" Reading Code Artifacts from environment or files such as git, venv,... """

import sys
import logging
import re
from enum import Enum
from abc import ABC,abstractmethod
import os
from copy import deepcopy
from typing import List,Optional,Union,Dict
from util import constants as C
from util.utils import Utils
from util.persistence import Persistence
from cli.bootstrap_config import config_env,console
from model.model_code_artifacts import ( CodeArtifactEnum as ARTIFACT,
                                         ArtifactMeta, VenvMeta, VsCodeMeta, GitMeta )
from pathlib import Path
# from typer import progressbar as t_progressbar
from rich.progress import Progress,TaskID
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
venv_regex = "Lib\\\\site-packages$" if Utils.is_windows() else "Lib\/site-packages$"
ARTIFACT_FILTER = { ARTIFACT.GIT:   {"include_paths":".git$","paths_only":True},
                   ARTIFACT.VSCODE:{"include_files":".code-workspace"},
                   ARTIFACT.VENV:  {"include_paths":venv_regex,"paths_only":True} }

# COPY TEMPLATE FOR INSTANCIATING
ARTIFACT_INPUT_TEMPLATE={"p_root":None,"max_path_depth":3,"artifact_type":ARTIFACT.GIT,"show_progress":False}

REGEX_BRANCH = re.compile('\"(.+)\"',re.IGNORECASE)

class CodeArtifact(ABC):
    """ Reading Code Artifacts from environment or files such as git, venv,... """
    def __init__(self,artifact_meta:ArtifactMeta=ArtifactMeta()):
        """_summary_

        Args:
            artifact_meta (ArtifactMeta, optional): Constructor. Defaults to ArtifactMeta().
            Params Infos
            p_root (str|list): Entry Path (single or list) containing all entry paths. If initial,
            it will default to current directory
            max_path_depth (int, optional): max folder depth to search from root path. Defaults to None.
            artifact: filter to be applied to capture signature of a certain code artifact
            show_progress (bool, optional): showing search indicator. Defaults to False.
        """

        p_root = artifact_meta.p_root
        max_path_depth = artifact_meta.max_path_depth
        artifact_type = artifact_meta.artifact_type
        artifact_filter = artifact_meta.artifact_filter
        show_progress = artifact_meta.show_progress
        paths_only = artifact_meta.paths_only

        # initalize / resolve paths
        if p_root is None:
            p_root = os.getcwd()
        self._p_root_list = p_root
        if isinstance(self._p_root_list,str):
            self._p_root_list = [p_root]
        self._max_path_depth = max_path_depth
        self._show_progress = show_progress
        self._paths_only = paths_only
        _path_refs = []
        for _p_root in  self._p_root_list:
            # checkl if it is a path other wise try to resolve reference
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
        # value in filter takes over priotity over supplied value
        _flt = self._artifact_filter
        if _flt.get("max_path_depth") is None and self._max_path_depth is not None:
            _flt["max_path_depth"] = self._max_path_depth
        self._artifact_filter["show_progress"] = _flt.get("show_progress",self._show_progress)
        self._artifact_filter["paths_only"] = _flt.get("paths_only",self._paths_only)
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

    @abstractmethod
    def read_content(self)->None:
        """ abstract method to read content from subclasses """
        pass

class GitArtifact(CodeArtifact):
    """  Git Code Artifact Parsing """
    def __init__(self, artifact_meta:ArtifactMeta=ArtifactMeta()) -> None:
        super().__init__(artifact_meta)
        self._artifact_type = ARTIFACT.GIT
        self._info_dict = {}

    @staticmethod
    def read_meta(p_git:str)->GitMeta:
        """ reading the git metadata from a root path """

        if not p_git.endswith(".git"):
            p_git = os.path.join(p_git,".git")

        if not os.path.isdir(p_git):
            logger.warning(f"[GitArtifact] Path [{p_git}] is not a valid git path")
            return

        path_git =  Path(p_git)
        path_repo = path_git.parent

        _config = Utils.read_ini_config(str(path_git.joinpath("config")))
        _head = Persistence.read_txt_file(str(path_git.joinpath("HEAD")))

        if _config is None or _head is None:
            logger.warning(f"[GitArtifact] Couldn't find config or HEAD in [{p_git}]")
            return

        # current branch
        _branch = _head[0].split("/")[-1]
        # parse the git config file
        _local_branches = []
        _url_repo = None
        for _config_key,config_meta in _config.items():
            if "branch" in _config_key:
                # parse the branch key branch "<branch_name>"
                _branch = REGEX_BRANCH.search(_config_key)
                if _branch:
                    _branch = _branch.group().replace('"','')
                    _local_branches.append(_branch)
            elif "origin"  in _config_key:
                _url_repo = config_meta.get("url")

        git_meta = GitMeta(p_repo=str(path_repo),
                           p_name=path_repo.name,
                           branch_current=_branch,
                           branch_list_local=_local_branches,
                           repo_url=_url_repo)
        return git_meta

    def read_content(self) -> None:
        """ reading content: configuration and current branch """
        num_artifacts = len(self._artifacts)

        def _read_git_metadata(task_id:TaskID,progress:Progress)->None:
            """ reads the content od git files """
            for _f_artifact in list(self._artifacts.keys()):
                _git_meta = GitArtifact.read_meta(_f_artifact)
                self._info_dict[_f_artifact]=_git_meta
                progress.update(task_id,advance=1)

        with Progress(disable=(not self._show_progress),console=console) as progress:
            task = progress.add_task("[out_path]Parsing Git Files", total=num_artifacts)
            _read_git_metadata(task,progress)
    
    def get_repo_refs(self) -> Dict[str,GitMeta]:
        """ returns the git repo references (read_content needs to be called prior to use this method) """
        out = {}
        for _git_meta in list(self._info_dict.values()):
            out[_git_meta.p_repo] = _git_meta
        return out
            
class VenvArtifact(CodeArtifact):
    """  Virtual Environment Code Artifact Parsing """
    def __init__(self, artifact_meta:ArtifactMeta=ArtifactMeta()) -> None:
        super().__init__(artifact_meta)
        self._artifact_type = ARTIFACT.VENV
        self._info_dict = {}

    @staticmethod
    def parse_venv_cfg(f_cfg:str)->dict:
        """ parse the pyvenv.cfg file """
        if not os.path.isfile(f_cfg):
            return {}

        _lines = Persistence.read_txt_file(f_cfg)
        _config_list = []
        for _line in _lines:
            # split into key value pairs
            _config = _line.split("=")
            _config = [c.strip() for c in _config]
            if len(_config) == 2:
                _config_list.append(_config)
        return dict(_config_list)

    @staticmethod
    def read_meta(p_venv:str)->None|VenvMeta:
        """ reading the git metadata from a root path """

        if not p_venv.endswith("site-packages"):
            logger.warning(f"[VenvArtifact] Path [{p_venv}] is not a site-package")
            return

        # get paths and packages of the VENV
        _path_site_packages = Path(p_venv)
        _path_venv = _path_site_packages.parent.parent
        _venv_name = _path_venv.name
        # assert there is a Scripts Folder
        if not (_path_venv.joinpath("Scripts")).is_dir():
            logger.warning(f"[VenvArtifact] Path [{p_venv}] doesn't contain a /Scripts subfolder")
            return

        _package_list = [Path(_p).name for _p in os.listdir(_path_site_packages) if os.path.isdir(os.path.join(_path_site_packages,_p))]
        # parse the config folder
        _f_cfg = _path_venv.joinpath("pyvenv.cfg")
        _venv_cfg = VenvArtifact.parse_venv_cfg(_f_cfg)
        _python_version = _venv_cfg.get("version")
        _executable = _venv_cfg.get("executable")

        _venv_meta = VenvMeta(p_venv=str(_path_venv),
                              venv_name=_venv_name,
                              package_list=_package_list,
                              python_version=_python_version,
                              executable=_executable)
        return _venv_meta

    def read_content(self) -> None:
        """ reads the venv content  """

        def _read_venvs(task_id:TaskID,progress:Progress)->None:
            """ reads the content of venv paths """
            for _p_venv in list(self._artifacts.keys()):
                _venv_meta = VenvArtifact.read_meta(_p_venv)
                self._info_dict[_p_venv] = _venv_meta
                progress.update(task_id,advance=1)

        with Progress(disable=(not self._show_progress),console=console) as progress:
            task = progress.add_task("[out_path]Parsing VS Code Files", total=len(self.artifacts))
            _read_venvs(task,progress)

class VsCodeArtifact(CodeArtifact):
    """  VS Code Project Code Artifact Parsing """
    def __init__(self, artifact_meta:ArtifactMeta=ArtifactMeta()) -> None:
        super().__init__(artifact_meta)
        self._artifact_type = ARTIFACT.VSCODE
        self._info_dict = {}

    @staticmethod
    def parse_vscode_folders(f_vscode:str)->list:
        """ parse the folders section in vs code configuration """
        _vs_config = Persistence.read_json(f_vscode)
        _folder_list = _vs_config.get("folders",[])
        _project_folders = []
        for _folder in _folder_list:
            _rel_path = _folder.get("path")
            if _rel_path is None:
                continue
            p_vscode = str(Path(f_vscode).absolute().parent)
            _p_abspath = Persistence.get_abspath_from_relpath(p_vscode,_rel_path)
            _project_folders.append(_p_abspath)
        return _project_folders

    def read_content(self)->None:
        """ reads the content  """

        def _read_vscode_files(task_id:TaskID,progress:Progress)->None:
            """ reads the content od vscode files """
            # flatten all vscode file refs into a list
            _vs_code_files=[]
            for _vs_code_file_list in self.artifacts.values():
                _vs_code_files.extend(_vs_code_file_list)
            for _f_artifact in _vs_code_files:
                _vscode_meta = VsCodeMeta(f_vscode=_f_artifact)
                _vscode_meta.p_folders = VsCodeArtifact.parse_vscode_folders(_f_artifact)
                self._info_dict[_f_artifact] = _vscode_meta
                progress.update(task_id,advance=1)

        with Progress(disable=(not self._show_progress),console=console) as progress:
            task = progress.add_task("[out_path]Parsing VS Code Files", total=len(self.artifacts))
            _read_vscode_files(task,progress)
    
    def get_path_refs(self)->Dict[str,Dict[str,VsCodeMeta]]:
        """ returns the paths with reference to the VScode File and the metadata 
            method read_content needs to be called prior to call this method
        """
        out = {}
        for _f_vs_code,_vs_code_meta in self._info_dict.items():
            # _out_folder = out.get()
            _p_folders = _vs_code_meta.p_folders
            for _p_folder in _p_folders:
                _p_info = out.get(_p_folder,{})
                _p_info[_f_vs_code]=_vs_code_meta
                out[_p_folder] = _p_info
        return out


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

    def read_content(self)->None:
        """ reads the content of all loaded classes """
        for _artifact_cls in list(self._artifacts.values()):
            _artifact_cls.read_content()

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
    
    def link_vscode2git(self,git2vscode:bool=False)->None:
        """ links VSCODE Projects To GIT Objects based on name equality of refered path and name of git repo 
            if git2vscode is True git_refs will be linked to existing vs code projects
        """
        out = {}
        _vscode = self.vscode_artifact
        _git = self.git_artifact
        if _vscode is None and _git is None:
            return {}
        _vscode_path_refs = _vscode.get_path_refs()
        _vscode_paths = list(_vscode_path_refs.keys())
        _git_refs = _git.get_repo_refs()
        _git_ref_paths = list(_git_refs.keys())
        if git2vscode is False:
            _source_paths = _vscode_paths
            _target_paths = _git_ref_paths
        else:
            _source_paths = _git_ref_paths
            _target_paths = _vscode_paths            

        _match_paths = [_p for _p in _source_paths if _p in _target_paths]
        for match_path in _match_paths:            
            out_info = {}
            if git2vscode is False:
                out_info["match"] = "vscode2git"
            else:
                out_info["match"] = "git2vscode"
            out_info[ARTIFACT["VSCODE"]]=_vscode_path_refs[match_path]
            out_info[ARTIFACT["GIT"]]=_git_refs[match_path]
            out[match_path]=out_info

        return out




