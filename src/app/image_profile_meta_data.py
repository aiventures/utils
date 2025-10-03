"""Creating a QR Code for Sony Picture Profiles
Creating QR Codes https://stackoverflow.com/questions/43295189/extending-a-image-and-adding-text-on-the-extended-area-using-python-pil
Required Libs: Pillow and qrcode
https://pypi.org/project/qrcode/
https://pypi.org/project/pillow/
Sony Picture Profiles
https://helpguide.sony.net/di/pp/v1/en/contents/TP0000909106.html
Sony RX 100 M7 Help Guide
https://helpguide.sony.net/dsc/1920/v1/en/contents/TP0001211745.html
Sony Picture Profile Recipes:
https://www.veresdenialex.com/home
How To Get Cinetone Simulation
https://www.youtube.com/watch?v=V_iRXE79GTw
Cinetone Whitepaper
https://pro.sony/s3/2020/03/24095333/S-Cinetone-whitepaper_v2.pdf
Cine Picture Profile Simulation
https://youtu.be/H6r-EZ8mDbg?si=JgsClu4LE6WLWKy9
Lab Color Space
https://de.wikipedia.org/wiki/Lab-Farbraum

"""

# Ideas ( Backlog )
# Profile Selector > Read A File with Numbers representing profiles to preselect profiles
# Picture Film Simulation Matcher: Based on some metadata do match image metadata with  profiles

import os
import logging
import shlex
import subprocess
import shutil
import sys
from pathlib import Path
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from collections import OrderedDict
import qrcode
import json
from typing import Dict, Tuple, Literal, List
from constants_local import IMAGE_PROFILE_TEMPLATES

BOM = "\ufeff"
p = "."
path = Path(p).absolute()

logger = logging.getLogger(__name__)


PROFILE_VARIABLE = [
    "Profile",
    "#",
    "Kelvin",
    "COLOR",
    "SATURATION_TONALITY",
    "RGB_RED",
    "RGB_YELLOW",
    "RGB_GREEN",
    "RGB_BLUE",
    "Black Level",
    "Gamma",
    "Black Gamma",
    "Black Gamma Value",
    "Knee Mode",
    "Knee %",
    "Knee Value",
    "Color Mode",
    "Saturation",
    "Color Phase",
    "Color Depth",
    "R",
    "G",
    "B",
    "C",
    "M",
    "Y",
    "Preset Group",
    "Preset Number",
    "Comment",
]
PROFILE_FIXED = [
    "Detail",
    "Mode",
    "V/H Balance",
    "B/W Balance",
    "Limit",
    "Crispening",
    "H-Light",
]

PROFILE_FIELDS = PROFILE_FIXED.copy()
PROFILE_FIELDS.extend(PROFILE_VARIABLE.copy())

PROFILE_FIELDS_INFO_ONLY = [
    "SATURATION_TONALITY",
    "RGB_RED",
    "RGB_YELLOW",
    "RGB_GREEN",
    "RGB_BLUE",
]

PROFILE_FIELDS_HIDE = ["#", "Preset Group", "Preset Number", "Profile"]

PROFILE_GROUPS = {
    "White Balance": ["Kelvin", "COLOR"],
    "Black Level": None,
    "Gamma": None,
    "Black Gamma": ["Black Gamma", "Black Gamma Value"],
    "Knee": ["Knee Mode", "Knee %", "Knee Value"],
    "Color Mode": None,
    "Saturation": None,
    "Color Phase": None,
    "Color Depth": None,
    "Colors RGBCMY": ["R", "G", "B", "C", "M", "Y"],
    # "Colors CMY": ["C", "M", "Y"],
}

# get all fields that are used in PROFILE GROUPS
PROFILE_GROUP_FIELDS = []
for profile_key, profile_value in PROFILE_GROUPS.items():
    if profile_value is None:
        PROFILE_GROUP_FIELDS.append(profile_key)
    else:
        PROFILE_GROUP_FIELDS.extend(profile_value)


class CmdRunner:
    """Cnd Runner: Runs OS Commands locally"""

    def __init__(self, cwd: str = None) -> None:
        """constructor"""
        self._output = None
        self._return_code = 0
        if not cwd:
            cwd = os.getcwd()
        if not os.path.isdir(cwd):
            logger.error(f"{cwd} is not a path, check input")
        self._cwd = os.path.abspath(cwd)

    def run_cmd(self, os_cmd: str, win_split: bool = False) -> int:
        """runs command line commandm
            since shlex will break windows os paths
            a custom routine can be activated using the win_split activation
            (has no effect on non Windows OS)

        Args:
            os_cmd (str): the command string to be parsewd
            win_split (bool, optional): use alwternative parsing routine for paths / files

        Raises:
            subprocess.CalledProcessError: When an error occurs

        Returns:
            int: return code (0 is ok)
        """

        logger.info(f"RUN COMMAND [{os_cmd}]")
        if not os_cmd:
            logger.warning("No command submitted, return")
            return

        # shlex Posix = False = quotes won't be removed
        oscmd_shlex = shlex.split(os_cmd, posix=False)
        # special case: output contains keywords (in this case its displaying a logfile)
        self._output = []
        self._return_code = 0
        logger.info(f"Execute Command [{oscmd_shlex}]")
        try:
            # encoding for german umlauts
            with subprocess.Popen(
                oscmd_shlex,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                errors="ignore",
                universal_newlines=True,
                encoding="utf8",
                cwd=self._cwd,
            ) as popen:
                for line in popen.stdout:
                    line = line.replace("\n", "")
                    self._output.append(line)
                    logger.info(line)

            # popen.stdout.close()
            if popen.stderr:
                logger.error(f"ERROR OCCURED: {popen.stderr}")

            self._return_code = popen.returncode
            if self._return_code:
                raise subprocess.CalledProcessError(self._return_code, os_cmd)
        except subprocess.CalledProcessError as e:
            self._return_code = 1
            logger.error(f"EXCEPTION OCCURED {e}, command {os_cmd}")
        return self._return_code

    def cmd(self, os_cmd: str, as_string=True, separator: str = "\n", win_split: bool = False) -> str | list:
        """shortcut to directly get results from a command routine
        Args:
            os_cmd (str):
            as_string (bool, optional): Return cd result as string. Defaults to True.
            separator (str, optional): Separator for concatenated result . Defaults to "\n".
            win_split (bool, optional): Alternative command splitting mode for Windows. Defaults to False.

        Returns:
            str|list: _cmd execution result
        """

        err_code = self.run_cmd(os_cmd, win_split)
        if err_code != 0:
            logger.error("[CmdRunner] There was an error running CmdRunner, check the logs")
            return None
        return self.get_output(as_string, separator)

    def get_output(self, as_string=True, separator: str = "\n"):
        """Returns output from last command
        Args:
            as_string (bool, optional): if True, output string list will be concatenated. Defaults to True.
        Returns:
            string/list: single output strings as list or concatenated string
        """
        out = self._output
        if as_string and isinstance(out, list):
            out = separator.join([l.strip() for l in out])
        return out


class PersistenceHelper:
    """util methods"""

    @staticmethod
    def csv2dict(lines) -> list[dict]:
        """transform csv lines to dictionary"""
        out_list = []
        if len(lines) <= 1:
            logger.warning("[Persistence] Too few lines in CSV")
            return {}
        keys = lines[0].split(";")
        # treat keys
        new_keys = []
        for key in keys:
            _key: str = key.strip()
            _key = _key.replace('"', "")
            new_keys.append(_key)
        keys = new_keys

        num_keys = len(keys)
        logger.debug(f"[Persistence] CSV COLUMNS ({num_keys}): {keys}")
        for i, l in enumerate(lines[1:]):
            values = l.split(";")
            if len(values) != num_keys:
                logger.warning(
                    f"[Persistence] Entry [{i}] ({l}): Wrong number of entries, expected {num_keys} {l}, got [{len(values)}]"
                )
                continue
            new_dict = dict(zip(keys, values))
            # print(f"Line [{i}] ({l[:30]}...) is ok ")
            out_list.append(new_dict)

        logger.debug(f"[Persistence] Read {len(out_list)} lines from CSV")
        return out_list

    @staticmethod
    def read_txt_file(
        filepath,
        encoding="utf-8",
        comment_marker="# ",
        skip_blank_lines=True,
        strip_lines=True,
        with_line_nums: bool = False,
    ) -> list:
        """reads data as lines from file, optionally as dict with line numbers"""
        if not isinstance(filepath, str):
            filepath = str(filepath)

        if with_line_nums:
            lines = {}
        else:
            lines = []
        bom_check = False
        try:
            with open(filepath, encoding=encoding, errors="backslashreplace") as fp:
                for n, line in enumerate(fp):
                    if not bom_check:
                        bom_check = True
                        if line[0] == BOM:
                            line = line[1:]
                            logger.warning(
                                "[Persistence] Line contains BOM Flag, file is special UTF-8 format with BOM"
                            )
                    if len(line.strip()) == 0 and skip_blank_lines:
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
            logger.error(f"[Persistence] Exception reading file {filepath}, [{e}]", exc_info=True)
        return lines

    @staticmethod
    def save_txt_file(filepath, data: str, encoding="utf-8") -> None:
        """saves string to file"""
        try:
            with open(filepath, encoding=encoding, mode="+wt") as fp:
                fp.write(data)
        except:
            logger.error(f"[Persistence] Exception writing file {filepath}", exc_info=True)
        return

    @staticmethod
    def read_json(filepath: str) -> dict:
        """Reads JSON file"""
        _filepath = str(filepath)
        data = None

        if _filepath is None:
            logger.warning(f"[Persistence] File path is None. Exiting...")
            return None

        if not os.path.isfile(_filepath):
            logger.warning(f"[Persistence] File path {_filepath} does not exist. Exiting...")
            return None
        try:
            with open(_filepath, encoding="utf-8") as json_file:
                data = json.load(json_file)
        except:
            logger.error(f"[Persistence] Error opening {_filepath} ****", exc_info=True)

        return data

    @staticmethod
    def save_json(filepath, data: dict) -> None:
        """Saves dictionary data as UTF8 json"""
        # TODO ENCODE DATETIME
        # https://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable

        with open(str(filepath), "w", encoding="utf-8") as json_file:
            try:
                json.dump(data, json_file, indent=4, ensure_ascii=False)
            except:
                logger.error(f"[Persistence] Exception writing file {str(filepath)}", exc_info=True)

            return None

    @staticmethod
    def modify_template(f_json_template: str):
        """create modificatoins of template"""
        _template_dict: Dict[str, dict] = PersistenceHelper.read_json(f_json_template)
        out = {}
        _delete_items = ["Preset", "PresetSave", "Vorbelegung"]
        for _profile, _profile_info in _template_dict.items():
            _info_copy = _profile_info.copy()
            # delete some old values
            for _del_item in _delete_items:
                try:
                    _info_copy.pop(_del_item)
                except (KeyError, ValueError):
                    continue
            # add new items
            # Number of Item
            _info_copy["Preset Group"] = ""  # Preset Group (contains 4 Presets)
            _info_copy["Preset Number"] = ""  # Preset Number (1...4)
            out[_profile] = _info_copy
        _f_template_out = Path(f_json_template).parent.joinpath("image_profiles2.json")
        PersistenceHelper.save_json(_f_template_out, out)

    @staticmethod
    def render_profile_groups(profile: dict) -> List[str]:
        """renders a profile in groups"""
        out = []
        # collect all profile infos bvelonging to one line
        for _profile_group, _profile_list in PROFILE_GROUPS.items():
            _profile_dicts = {}
            if _profile_list is None:
                out_s = f"    {_profile_group:<20}: {profile.get(_profile_group, 'N/A')}"
                out.append(out_s)
                continue
            for _profile in _profile_list:
                _profile_dicts[_profile] = profile.get(_profile, "N/A")
            _param_list = []
            for _key, _value in _profile_dicts.items():
                _param_list.append(f"{_key}:{_value}")
            out_s = f"    {_profile_group:<20}: {' | '.join(_param_list)}"
            out.append(out_s)
        return out

    @staticmethod
    def render_image_profiles(
        f_image_profiles,
        key: Literal["profile", "number", "group"] = "number",
        only_preset: bool = True,
        exclude_fixed: bool = True,
        ignore_info_fields: bool = True,
        as_profile_groups: bool = True,
        title_only: bool = False,
    ) -> List[str]:
        out = []
        template_dict = PersistenceHelper.read_image_profiles(f_image_profiles, key, only_preset, exclude_fixed)
        for _idx, (_profile_key, _info_dict) in enumerate(template_dict.items()):
            _profile = _info_dict["Profile"].replace("\n", " ")
            _preset = ""
            _number = str(_info_dict["#"]).zfill(2)
            _color_mode = _info_dict.get("Color Mode")
            if len(_info_dict["Preset Group"]) > 0:
                _preset = f"[{_info_dict['Preset Group']}/{_info_dict['Preset Number']}]"
            _profile_title = f"{_preset} {_profile} [{_color_mode}] (#{_number})"
            _title_spacer = "" if title_only else 20 * "#"
            _title = f"{str(_idx).zfill(2)}. {_title_spacer} {_profile_title}"
            out.append(_title)
            if title_only:
                continue
            # add fields from profiles if in group mode
            if as_profile_groups:
                _grouped_profiles = PersistenceHelper.render_profile_groups(_info_dict)
                out.extend(_grouped_profiles)

            # add the other fields
            for _key, _value in _info_dict.items():
                if ignore_info_fields and _key in PROFILE_FIELDS_INFO_ONLY:
                    continue
                if as_profile_groups and _key in PROFILE_GROUP_FIELDS:
                    continue
                if _key in PROFILE_FIELDS_HIDE:
                    continue
                if _key == "Comment" and len(_value) == 0:
                    continue
                if isinstance(_value, str):
                    _value = _value.replace("\n", "")
                out.append(f"    {_key:<20}: {_value}")
            out.append("\n")

        return out

    @staticmethod
    def read_image_profiles(
        f_image_profiles,
        key: Literal["profile", "number", "group"] = "number",
        only_preset: bool = True,
        exclude_fixed: bool = True,
        compact: bool = True,
    ) -> dict:
        """Reads image profiles"""
        out = {}
        _profile_dict = PersistenceHelper.read_json(f_image_profiles)
        for _profile, _profile_info in _profile_dict.items():
            _preset_group = _profile_info.get("Preset Group", "")
            _preset_number = _profile_info.get("Preset Number", "")
            _preset_key = f"{_preset_group}_{_preset_number}"
            _number = int(_profile_info.get("#"))
            _comment = _profile_info.get("Comment", "")
            if only_preset and _preset_group == "":
                continue
            _profile_out = {}
            for _key, _value in _profile_info.items():
                if exclude_fixed and _key in PROFILE_FIXED:
                    continue
                _profile_out[_key] = _value
            _key = _number
            if key == "group":
                _key = _preset_key
            elif key == "profile":
                _key = _profile
            out[_key] = _profile_out
            # print(list(_profile_info.keys()))
            # if only_preset and len(_pr)
        out = dict(sorted(out.items()))
        # print(json.dumps(out, indent=4))
        # print(list(out.keys()))
        return out


class Utils:
    """Other helper methods"""

    @staticmethod
    def hex2rgb(chex: str) -> Tuple[int]:
        """convert hex to rgb"""
        # https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python
        _chex = chex.lstrip("#")
        return tuple(int(_chex[i : i + 2], 16) for i in (0, 2, 4))


class ProfileTransformer:
    """Transforming Image Profules into QR Codes"""

    @staticmethod
    def create_qr_meta_list(f_json: str) -> list:
        """creates a list containing the qr codw meta data from a json file"""
        # drop some of the attributes as they are constant
        _ignore_fields = [
            "Detail",
            "Mode",
            "V/H Balance",
            "B/W Balance",
            "Limit",
            "Crispening",
            "H-Light",
            "Vorbelegung",
            "Profile",
        ]

        _f_json = str(f_json)

        # create a list to be used for output
        with open(_f_json, "r", encoding="utf-8") as file:
            _dict = json.load(file)

        # create the qr code texts
        qr_content_list = []
        for _profile, _info in _dict.items():
            _info_copy: dict = _info.copy()
            _num = f"({_info['#'].zfill(2)})"
            _title = f"{_num} {_info['Profile']}"
            _bottom = f"{_info['Kelvin']} {_info['COLOR']}"
            _file_name = f"{str(_info['#']).zfill(2)}_{_profile.replace(' ', '_')}.png"
            _preset = _info["Preset"]
            if len(_preset) > 0:
                _title = f"P{_preset} {_title}"
                _file_name = f"P{_preset}_{_file_name}"
            _info_copy["filename"] = _file_name
            print(_file_name)
            _s_out = [f"### PROFILE [{_profile}]"]

            for _key, _value in _info_copy.items():
                if len(_value) == 0:
                    continue
                if _key in _ignore_fields:
                    continue
                _line = f"{_key:<20}: {_value}"
                print(_line)
                _s_out.append(_line)
            _s_out = "\n".join(_s_out)
            qr_content_list.append((_file_name, _title, _bottom, _s_out))
        return qr_content_list

    @staticmethod
    def create_qrcode(
        f_qr: str | Path,
        qr_text: str,
        top_txt: str | None = None,
        bottom_text: str | None = None,
    ):
        """creating a QR Cwode with top and bottom description"""
        # define the paths
        _f_qr = Path(f_qr).absolute()
        _p_qr = _f_qr.parent
        _f_qr_tmp = _p_qr.joinpath("qr_tmp.png")

        # draw and save the qr code
        _qr = qrcode.QRCode(version=15, box_size=6, border=1)
        _qr.add_data(qr_text)
        _img = _qr.make_image(fill_color="black", back_color="white")

        try:
            _img.save(str(_f_qr_tmp))
        except OSError:
            return

        # add qr code to image
        _qr_img = Image.open(_f_qr_tmp)
        _qr_size = _qr_img.size[0]

        # draw an image with qr code and description
        _edge = 30
        _left = _edge
        _img_size = _qr_size + 2 * _edge
        _font_size = 30
        _background = Image.new("RGBA", (_img_size, _img_size + 4 * _font_size), (255, 255, 255, 255))
        _draw = ImageDraw.Draw(_background)

        # add text to image
        _font = ImageFont.load_default(_font_size)
        # font = ImageFont.truetype('arial.ttf',40)
        _font = ImageFont.truetype("cour.ttf", 40)
        if top_txt:
            _draw.text(
                xy=(_left, _edge),
                text=top_txt,
                fill=(0, 0, 0),
                font=_font,
                stroke_width=1,
            )
        if bottom_text:
            _draw.text(
                xy=(_left, 4 * _edge + _qr_size),
                text=bottom_text,
                fill=(0, 0, 0),
                font=_font,
                stroke_width=1,
            )

        _background.paste(_qr_img, (_left, 3 * _edge))
        _background.save(str(_f_qr))
        print(f"Saved QR Code to {_f_qr}")
        os.remove(_f_qr_tmp)


if __name__ == "__main__":
    loglevel = logging.INFO
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s",
        level=loglevel,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    p_root = Path(__file__).parent.resolve()
    f_json_template = p_root.joinpath("image_profiles_templates.json")
    f_json = p_root.joinpath("image_profiles.json")
    shutil.copy2(str(f_json_template), str(f_json))
    # create a template copy with altered fields
    f_profiles = IMAGE_PROFILE_TEMPLATES
    p_profiles = Path(IMAGE_PROFILE_TEMPLATES).parent
    if False:
        PersistenceHelper.modify_template(f_profiles)

    if False:
        qr_content_list = ProfileTransformer.create_qr_meta_list(f_json)
        print("PATH:", str(p_root))
        for _idx, _qr_info in enumerate(qr_content_list):
            _file, _title, _bottom, _qr_content = _qr_info
            _f_qr = p_root.joinpath("out", _file)
            print(f"CREATE QR CODE: {str(_f_qr)}")
            ProfileTransformer.create_qrcode(_f_qr, _qr_content, _title, _bottom)

    if True:
        title_list = PersistenceHelper.render_image_profiles(f_profiles, key="profile", title_only=True)
        print("\n".join(title_list))
        # PersistenceHelper.save_txt_file(p_profiles.joinpath("filmsimulation_list.txt"), "\n".join(title_list))
        # profile_list = PersistenceHelper.render_image_profiles(f_profiles, key="profile")
        # PersistenceHelper.save_txt_file(p_profiles.joinpath("filmsimulation_details.txt"), "\n".join(profile_list))
        # print("\n".join(profile_list))
