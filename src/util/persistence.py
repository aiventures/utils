""" Helper class to read / write (single) file """
import sys
import os
from pathlib import Path
import logging
import re
from datetime import datetime as DateTime
from util import constants as C

import json

# when doing tests add this to reference python path
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# exclude yaml handling here to avoid import of required libs
# import yaml
# from yaml import CLoader
# from yaml.composer import Composer
# from yaml.constructor import Constructor

logger = logging.getLogger(__name__)

# byte order mark indicates non standard UTF-8
BOM = '\ufeff'

class Persistence():
    """ Helper class to read / write (single) file """

    NUM_COL_TITLE = "num" # csv column title for number
    ID_TITLE = "id" # column name of object header
    TEMPLATE_DEFAULT_VALUE = "undefined" # default value for template value
    LINE_KEY = "line" # dict key for lines attribute when reading yaml
    ALLOWED_FILE_TYPES = ["yaml","txt","json","plantuml","md"]

    def __init__(self,f_read:str=None,f_save:str=None,**kwargs) -> None:
        """ constructor """
        self._cwd = os.getcwd()
        if f_read:
            if os.path.isfile(f_read):
                self._f_read = os.path.abspath(f_read)
                logger.info(f"[Persistence] File read path: [{self._f_read}]")
            else:
                self._f_read = None
                logger.warning(f"[Persistence] File path {f_read} not found, check")
        self._f_save = None
        if f_save:
            logger.info(f"[Persistence] File save path: {f_save}")
            self._f_save = f_save
        # get more params form kwargs
        self._dec_sep = kwargs.get("dec_sep",",")
        self._csv_sep = kwargs.get("csv_sep",";")
        self._add_timestamp = kwargs.get("add_timestamp",False)

        logger.debug(f"[Persistence] Decimal Separator: {self._dec_sep}, CSV Separator: {self._csv_sep}")

    @property
    def f_read(self)->Path:
        """ returns the original file path as path object """
        return Path(self._f_read)

    @property
    def f_save(self)->str:
        """ returns the original save path """
        if self._f_save:
            self._get_save_file_name()
        else:
            return None

    @staticmethod
    def replace_file_suffix(f_name:str,new_suffix:str)->str:
        """ Replaces file suffix """
        p_file = Path(f_name)
        return str(p_file.with_suffix(new_suffix))

    @staticmethod
    def called_from_bash()->bool:
        """ returns whether script run from bash """
        return True if os.environ.get("TERM") else False

    @staticmethod
    def posix2winpath(f:str)->str:
        """ try to get winpath from (absolute) posix string """
        p_parts = f.split("/")
        p_parts = [p for p in p_parts if p]
        drive = p_parts[0]+":\\"
        p_parts = p_parts[1:]
        if not os.path.isdir(drive):
            logger(f"Could not find drive {drive} from Path {f}")
            return None
        p = os.path.join(drive,*p_parts)
        return p

    @staticmethod
    def find(_p_root_paths:list|str=None,
             include_abspaths:list|str=None,exclude_abspaths:list|str=None,
             include_files:list|str=None,exclude_files:list|str=None,
             include_paths:list|str=None,exclude_paths:list|str=None,
             paths:bool=True,files:bool=True,as_dict:bool=True,
             root_path_only:bool=False,
             match_all:bool=True)->list|dict:
        """ finds files and paths according to path names / a slightly slimmer version than the FileAnalyzer
            regex can be used (differewntly for filename only, path only or abs path)
            match all or anxy determines whethwer all or any crieteria need to match
        """
        def _is_match(file_info:str,reg_exprs:list|None):
            """ checks if a file object should be added. if an item is None, then it is considered as ok """
            if reg_exprs is None:
                return True

            if not isinstance(reg_exprs,list):
                logger.warning("[Persistence] Not a list of regexes")
                return False

            is_match = []
            for reg_expr in reg_exprs:
                _match = True if len(reg_expr.findall(file_info))>0 else False
                is_match.append(_match)

            if match_all:
                if len(is_match)>0 and all(is_match):
                    is_match = True
                else:
                    is_match = False
            else:
                is_match = any(is_match)
            return is_match

        def _passes(file_info:str,include_exprs:list|None,exclude_exprs:list|None):
            _matches_include = _is_match(file_info,include_exprs)
            # only continue if evaluated to true and there are some exclude critera
            if not isinstance(exclude_exprs,list):
                return _matches_include
            _matches_exclude = _is_match(file_info,exclude_exprs)
            if _matches_exclude is True:
                return False
            else:
                return _matches_include

        _p_root_paths = [_p_root_paths] if isinstance(_p_root_paths,str) else _p_root_paths
        _include_abspaths = [include_abspaths] if isinstance(include_abspaths,str) else include_abspaths
        _exclude_abspaths = [exclude_abspaths] if isinstance(exclude_abspaths,str) else exclude_abspaths
        _include_files = [include_files] if isinstance(include_files,str) else include_files
        _exclude_files = [exclude_files] if isinstance(exclude_files,str) else exclude_files
        _include_paths = [include_paths] if isinstance(include_paths,str) else include_paths
        _exclude_paths = [exclude_paths] if isinstance(exclude_paths,str) else exclude_paths
        _re_include_abspaths = [re.compile(_i) for _i in _include_abspaths] if isinstance(_include_abspaths,list) else None
        _re_exclude_abspaths = [re.compile(_e) for _e in _exclude_abspaths] if isinstance(_exclude_abspaths,list) else None
        _re_include_files = [re.compile(_i) for _i in _include_files] if isinstance(_include_files,list) else None
        _re_exclude_files = [re.compile(_e) for _e in _exclude_files] if isinstance(_exclude_files,list) else None
        _re_include_paths = [re.compile(_i) for _i in _include_paths] if isinstance(include_paths,list) else None
        _re_exclude_paths = [re.compile(_e) for _e in _exclude_paths] if isinstance(_exclude_paths,list) else None

        for _root_path in _p_root_paths:
            logger.debug(f"[Persistence] Checking files and paths for [{_root_path}]")
            if not os.path.isdir(_root_path):
                logger.warning(f"[Persistence] Path [{_root_path}] doesn't exist")
                continue
            _p_root = Path(_root_path).absolute

            _paths = []
            _files = []
            _path_dict = {}
            for _subpath,_,_files in os.walk(_p_root):
                _cur_path = Path(_subpath).absolute()
                if root_path_only and _cur_path != _p_root:
                    continue
                # check for path is there are criteria
                _passed = True
                _p = str(_cur_path)
                if _re_include_paths or _re_exclude_paths:
                    _passed = _passes(_p,_re_include_paths,_re_exclude_paths)
                if _passed is False:
                    continue
                _paths.append(_p)
                _path_dict[_p]=[]
                for _f in _files:
                    # check for file name matches
                    _passed = True
                    if _re_include_files or _re_exclude_files:
                        _passed = _passes(_f,_re_include_files,_re_exclude_files)
                    if _passed is False:
                        continue
                    # check for absolute paths
                    _f_abspath = _cur_path.joinpath(_f)
                    _f_abs = str(_f_abspath)
                    if _re_include_abspaths or _re_exclude_abspaths:
                        _passed = _passes(_f_abs,_re_include_abspaths,_re_exclude_abspaths)
                    if _passed is False:
                        continue
                    _path_dict[_p].append(_f_abs)
                    _files.append(_f_abs)

        # either return dict or list of files
        if as_dict:
            return _path_dict
        # depending on input return proper file objects
        else:
            if paths and files:
                return (_paths,_files)
            elif paths:
                return _paths
            elif files:
                return _files
            
    # todo: copy and renamee

    @staticmethod
    def absolute_winpath(f:str,posix:bool=False,uri:bool=False,as_path:bool=False)->bool:
        """ gets absolute path in a given representation also does an existence check """
        p = Path(f)
        p_valid = any([p.is_dir(),p.is_file()])
        if not p_valid:
            # try to interpret string as posix path
            p = Path(Persistence.posix2winpath(f))
            p_valid = any([p.is_dir(),p.is_file()])
            if not p_valid:
                logger.warning(f"[Persistence] {f} is not a valid file or path (path)")
                return
        p = p.absolute()
        if posix: # return as posix string (however it is not a valid path)
            p_parts=p.parts
            p_root="/"+p_parts[0][0]
            p_posix="/".join([p_root,*p_parts[1:]])
            return p_posix
        elif uri:
            return p.as_uri()
        else:
            if as_path:
                return p
            else:
                return str(p)

    @staticmethod
    def dict_stringify(d:dict,dateformat:str=C.DATEFORMAT_DD_MM_JJJJ_HH_MM_SS)->dict:
        """ converts a dict with objects to stringified dict (for json) """

        for k, v in d.copy().items():
            v_type = str(type(v).__name__)
            logger.debug(f"[Persistence] Key {k} type {v_type}")
            if isinstance(v, dict): # For DICT
                d[k]= Persistence.dict_stringify(v,dateformat)
            elif isinstance(v, list): # itemize LIST as dict
                d[k] = [Persistence.dict_stringify(i,dateformat) for i in v]
            elif isinstance(v, str): # Update Key-Value
                d.pop(k)
                d[k] = v
            elif isinstance(v,DateTime): # stringify date
                d.pop(k)
                d[k]=v.strftime(dateformat)
            else:
                d.pop(k)
                d[k] = v
        return d

    def read_file(self,encoding='utf-8',comment_marker=None,skip_blank_lines=False,strip_lines=True,with_line_nums:bool=False)->list|dict:
        """ read file and return content"""
        if self._f_read is None:
            logger.warning("[Persistence] No valid file in Object")
            return
        return Persistence.read_txt_file(self._f_read,encoding,comment_marker,skip_blank_lines,strip_lines,with_line_nums)

    @staticmethod
    def get_headerdict_template(keys:list,attribute_dict:dict):
        """ creates a headerdict template from keys and attributes """
        default = Persistence.TEMPLATE_DEFAULT_VALUE
        out_dict = {}
        for key in keys:
            dict_line = {}
            for attribute,value in attribute_dict.items():
                if not value:
                    value = default
                dict_line[attribute]=value
            out_dict[key]=dict_line
        return out_dict

    @staticmethod
    def create_headerdict_template(f:str,headers:list,template_body:dict)->str:
        """ creates a headerdict template and saves it """
        template=Persistence.get_headerdict_template(headers,template_body)
        p_file=Path(f)
        p_suffix = p_file.suffix
        if not p_file.is_absolute():
            p_file = Path(os.path.join(os.getcwd(),f))
        p_file = str(p_file)
        # if p_suffix.lower().endswith("yaml"):
        #     PersistenceHelper.save_yaml(p_file,template)
        if p_suffix.lower().endswith("json"):
            Persistence.save_json(p_file,template)
        elif p_suffix.lower().endswith("csv"):
            csv_data = Persistence.headerdict2list(template)
            Persistence.save_list(f,csv_data)
        else:
            logger.error("[Persistence] File template creation only allowed for type yaml,json,csv")
        logger.info(f"[Persistence] Created Template file {p_file}")
        return p_file

    @staticmethod
    def headerdict2list(d:dict,filter_list:list=None,header_name:str=ID_TITLE,column_list:list=None)->list:
        """ linearizes a dictionary containing header and attributes
            sample_key1:
                comment: comment 1
                property1: value1.1
                property2: value1.2
                status: open
            ...
            you may filter out entries using keywords for fields

            [{"status":"ignore"},...] would ignore any dictionaries with field status having ignore as value
            {"<header_name>":"sample"}: Any entries with header containing "sample" would be filtered
            header name attribute may be adjusted
            field list can be passed to extract only a subset / for a given order
        """
        def is_passed(header,value_dict):
            passed = True
            for f in filter_list:
                filter_field = list(f.keys())[0]
                filter_value = f[filter_field]
                value = None
                if filter_field == header_name:
                    value = header
                else:
                    value = value_dict.get(filter_field)
                if not value:
                    continue
                if filter_value in value:
                    logger.info(f"[Persistence] Item [{header}] will be filtered, Rule ({filter_field}:{filter_value}), value ({value})")
                    passed = False
                    break
            return passed

        num_col_title = Persistence.NUM_COL_TITLE
        out_list = []
        columns=[]
        column_counts=[]
        index = 1
        for header,value_dict in d.items():
            if filter_list:
                passed = is_passed(header,value_dict)
                if passed is False:
                    continue
            keys = list(value_dict.keys())
            # get some stats
            columns.append(keys)
            columns = list(set(keys))
            column_counts.append(len(keys))
            column_counts=list(set(column_counts))
            line_dict = {num_col_title:str(index).zfill(2),header_name:header}
            index += 1
            for k in keys:
                line_dict[k]=str(value_dict[k])
            out_list.append(line_dict)

        logger.debug(f"[Persistence] Created {len(out_list)} entries, columns {columns}")
        if len(column_counts) > 1:
            logger.debug("[Persistence] Different Columns present for each line, appending missing columns")
            out_list_new = []
            for line_dict in out_list:
                out_dict_new={num_col_title:line_dict[num_col_title],header_name:line_dict[header_name]}
                for column in sorted(columns):
                    v = line_dict.get(column)
                    if v is None:
                        logger.debug(f"[Persistence] Adding empty value for line with key {line_dict[header_name]}")
                        v = ""
                    out_dict_new[column]=v
                out_list_new.append(out_dict_new)
            out_list = out_list_new

        if column_list:
            # create column subset only / use to ensure column order
            out_list_new = []
            for line_dict in out_list:
                out_dict_new={header_name:line_dict[header_name]}
                for column in column_list:
                    v = line_dict.get(column)
                    if v is not None:
                        out_dict_new[column]=v
                out_list_new.append(out_dict_new)
            out_list = out_list_new

        return out_list

    def _csv2dict(self,lines)->dict:
        """ transform csv lines to dictionary """
        out_list = []
        if len(lines) <= 1:
            logger.warning("[Persistence] Too few lines in CSV")
            return {}
        keys = lines[0].split( self._csv_sep)
        num_keys = len(keys)
        logger.debug(f"[Persistence] CSV COLUMNS ({num_keys}): {keys}")
        for i,l in enumerate(lines[1:]):
            values = l.split( self._csv_sep)
            if len(values) != num_keys:
                logger.warning(f"[Persistence] Entry [{i}]: Wrong number of entries, expected {num_keys} {l}")
                continue
            out_list.append(dict(zip(keys,values)))
        logger.debug(f"[Persistence] Read {len(out_list)} lines from CSV")
        return out_list

    @staticmethod
    def dicts2csv(data_list:list,csv_sep:str=",",dec_separator:str=",",wrap_char:str=None,keys:list=None)->list:
        """ try to convert a list of dictionaries into csv format
            - separator is given and
            - value can be enclosed in wrap_char
            - keys to be transferred can also be controlled externally (to make sure a csv is
              exported in case not all lines contain the same keys)
        """
        if isinstance(wrap_char,str) and len(wrap_char) == 0:
            wrap_char = None

        out = []
        if not data_list:
            logger.warning("[Persistence] no data in list")
            return None
        key_row = data_list[0]
        if not isinstance(key_row,dict):
            logger.warning("[Persistence] List data is ot a dictionary, nothing will be returned")
            return None

        if keys is None:
            keys = list(key_row.keys())
        if wrap_char is not None:
            keys_out = [f"{wrap_char}{str(k)}{wrap_char}" for k in keys]
        else:
            keys_out = keys
        out.append(csv_sep.join(keys_out))
        # TODO Output In Order
        for data in data_list:
            data_row = []
            for k in keys:
                v = data.get(k,"None")

                # centralize conversion routine
                if v is None:
                    v = "None"
                elif isinstance(v,float):
                    v = str(v).replace(",","")
                    v = v.replace(".",dec_separator)
                else:
                    v = str(v)

                if csv_sep in v and wrap_char is None:
                    logger.warning(f"[Persistence] CSV Separator {v} found in {k}:{v}, will be replaced by _sep_")
                    v = v.replace(csv_sep,"_sep_")
                if wrap_char is not None:
                    v = f"{wrap_char}{str(v)}{wrap_char}"
                data_row.append(v)
            out.append(csv_sep.join(data_row))
        return out

    @staticmethod
    def read_txt_file(filepath,encoding='utf-8',comment_marker="# ",skip_blank_lines=True,strip_lines=True,with_line_nums:bool=False)->list:
        """ reads data as lines from file, optionally as dict with line numbers
        """
        if not isinstance(filepath,str):
            filepath = str(filepath)

        if with_line_nums:
            lines = {}
        else:
            lines = []
        bom_check = False
        try:
            with open(filepath,encoding=encoding,errors='backslashreplace') as fp:
                for n,line in enumerate(fp):
                    if not bom_check:
                        bom_check = True
                        if line[0] == BOM:
                            line = line[1:]
                            logger.warning("[Persistence] Line contains BOM Flag, file is special UTF-8 format with BOM")
                    if len(line.strip())==0 and skip_blank_lines:
                        continue
                    if comment_marker is not None and line.startswith(comment_marker):
                        continue
                    if strip_lines:
                        line = line.strip()
                    if with_line_nums:
                        lines[n] = line
                    else:
                        lines.append(line)
        except Exception as e:
            logger.error(f"[Persistence] Exception reading file {filepath}, [{e}]",exc_info=True)
        return lines

    @staticmethod
    def save_txt_file(filepath,data:str,encoding='utf-8')->None:
        """ saves string to file  """
        try:
            with open(filepath,encoding=encoding,mode="+wt") as fp:
                fp.write(data)
        except:
            logger.error(f"[Persistence] Exception writing file {filepath}",exc_info=True)
        return

    @staticmethod
    def read_json(filepath:str)->dict:
        """ Reads JSON file"""
        data = None

        if not os.path.isfile(filepath):
            logger.warning(f"[Persistence] File path {filepath} does not exist. Exiting...")
            return None
        try:
            with open(filepath,encoding='utf-8') as json_file:
                data = json.load(json_file)
        except:
            logger.error(f"[Persistence] Error opening {filepath} ****",exc_info=True)

        return data

    @staticmethod
    def save_json(filepath,data:dict)->None:
        """ Saves dictionary data as UTF8 json """
        # TODO ENCODE DATETIME
        # https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable

        with open(filepath, 'w', encoding='utf-8') as json_file:
            try:
                json.dump(data, json_file, indent=4,ensure_ascii=False)
            except:
                logger.error("[Persistence] Exception writing file {filepath}",exc_info=True)

            return None

    def read(self,line_key:str=None):
        """ read file, depending on file extension
            for yaml, lines in in filecan be read
        """
        if not self._f_read:
            logger.error("[Persistence] No file found")
            return
        out = None
        p = Path(self._f_read)
        suffix = p.suffix[1:].lower()
        if suffix in ["txt","plantuml","csv"]:
            out = Persistence.read_txt_file(self._f_read)
            if suffix == "csv":
                out = self._csv2dict(out)
        # elif suffix == "yaml":
        #     out = PersistenceHelper.read_yaml(self._f_read,line_key)
        elif suffix == "json":
            out = Persistence.read_json(self._f_read)
        else:
            logger.warning(f"[Persistence] File {self._f_read}, no supported suffix {suffix}, skip read")
            out = None

        logger.info(f"[Persistence] Reading {self._f_read}")

        return out

    def get_adjusted_filename(self,f,add_timestamp:bool=False)->str:
        """ gets adjusted and absolute filename """

        p_file = Path(f)
        dt = DateTime.now().strftime('%Y%m%d_%H%M%S')
        if add_timestamp:
            p_file_new = p_file.stem+"_"+dt+p_file.suffix
        else:
            p_file_new = p_file.name

        # get path
        if p_file.is_absolute():
            p_path = str(p_file.parent)
        else:
            p_path = os.getcwd()

        f_adjusted = os.path.join(p_path,p_file_new)
        return f_adjusted

    def _get_save_file_name(self,f_save:str=None)->str:
        """ creates an adjusted and absolute save filename """
        if f_save is None:
            f_save = self._f_save

        if not f_save:
            logger.warning("[Persistence] No file name for saving data was found")
            return None

        f_save = self.get_adjusted_filename(f_save,self._add_timestamp)
        return f_save

    @staticmethod
    def save_list(f_save:str,data:list)->str:
        """ save data in a list as string data, returns saved file name """
        if not f_save or not isinstance(data,list):
            logger.error(f"[Persistence] Can't Save file {f_save}")
            return
        try:
            data = "\n".join(data)
        except TypeError:
            logger.error(f"[Persistence] Data to save to {f_save} is not a list of strings")
        Persistence.save_txt_file(f_save,data)
        return f_save




    # make it static
    # def save(self,data,f_save:str=None)->str:
    #     """ save file, optionally with path, returns filename """
    #     f_save = self._get_save_file_name(f_save)

    #     if not f_save:
    #         return

    #     p = Path(f_save)
    #     suffix = p.suffix[1:].lower()

    #     if suffix in ["txt","plantuml","csv","md"]:
    #         if isinstance(data,list):
    #             try:
    #                 data = "\n".join(data)
    #             except TypeError:
    #                 # try to convert into a csv list
    #                 data = self._dicts2csv(data)
    #                 data = "\n".join(data)
    #                 if not data:
    #                     logger.error(f"Elements in list are not string / (plain) dicts, won't save {f_save}")
    #                     return
    #         if not isinstance(data,str):
    #             logger.warning(f"Data is not of type string, won't save {f_save}")
    #             return
    #         data = data+"\n"
    #         PersistenceHelper.save_txt_file(f_save,data)
    #     elif suffix in ["yaml","json"]:
    #         if isinstance(data,list):
    #             data = {"data":data}
    #             logger.warning(f"Data is a list, will save it as pseudo dict in {suffix} File")
    #         if not isinstance(data,dict):
    #             logger.warning("Data is not a dict, won't save {f_save}")
    #             return
    #         # convert objects in json
    #         data = PersistenceHelper.dict_stringify(data)
    #         # if suffix == "yaml":
    #         #     PersistenceHelper.save_yaml(f_save,data)
    #         if suffix == "json":
    #             PersistenceHelper.save_json(f_save,data)
    #     else:
    #         logger.warning(f"File {f_save}, no supported suffix {suffix} (allowed: {PersistenceHelper.ALLOWED_FILE_TYPES}), skip save")
    #         return
    #     logger.info(f"Saved [{suffix}] data: {f_save}")
    #     return f_save

if __name__ == "__main__":
    loglevel = logging.DEBUG
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=loglevel, stream=sys.stdout, datefmt="%Y-%m-%d %H:%M:%S")

    # @staticmethod
    # def read_yaml(filepath:str,line_key:str=None)->dict:
    #     """ Reads YAML file (optionally with line numbers)"""
    #     # https://stackoverflow.com/questions/13319067

    #     def compose_node(parent, index):
    #         # the line number where the previous token has ended (plus empty lines)
    #         line = loader.line
    #         node = Composer.compose_node(loader, parent, index)
    #         node.__line__ = line + 1
    #         return node

    #     def construct_mapping(node, deep=False):
    #         mapping = Constructor.construct_mapping(loader, node, deep=deep)
    #         mapping[line_key] = str(node.__line__)
    #         return mapping

    #     if not os.path.isfile(filepath):
    #         logger.warning(f"File path {filepath} does not exist. Exiting...")
    #         return None
    #     loader = yaml.Loader(open(filepath,encoding='utf-8').read())
    #     if line_key:
    #         loader.compose_node = compose_node
    #         loader.construct_mapping = construct_mapping
    #     data = loader.get_single_data()
    #     return data

    # @staticmethod
    # def read_yaml_old(filepath:str,)->dict:
    #     """ Reads YAML file """

    #     if not os.path.isfile(filepath):
    #         logger.warning(f"File path {filepath} does not exist. Exiting...")
    #         return None
    #     data = None
    #     try:
    #         with open(filepath, encoding='utf-8',mode='r') as stream:
    #             data = yaml.load(stream,Loader=CLoader)
    #     except:
    #         logger.error(f"Error opening {filepath} ****",exc_info=True)
    #     return data

    # @staticmethod
    # def save_yaml(filepath,data:dict)->None:
    #     """ Saves dictionary data as UTF8 yaml"""
    #     # encode date time and other objects in dict see

    #     with open(filepath, 'w', encoding='utf-8') as yaml_file:
    #         try:
    #             yaml.dump(data,yaml_file,default_flow_style=False,sort_keys=False)
    #         except:
    #             logger.error(f"Exception writing file {filepath}",exc_info=True)
    #         return None
