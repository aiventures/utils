"""Creating a QR Code for Sony Picture Profiles
Creating QR Codes https://stackoverflow.com/questions/43295189/extending-a-image-and-adding-text-on-the-extended-area-using-python-pil
Required Libs: Pillow and qrcode
https://pypi.org/project/qrcode/
https://pypi.org/project/pillow/
Sony Picture Profiles
https://helpguide.sony.net/di/pp/v1/en/contents/TP0000909106.html
Sony Picture Profile Recipes:
https://www.veresdenialex.com/home
"""

import os
import logging
import shutil
import sys
from pathlib import Path
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import qrcode
import json

p = "."
path = Path(p).absolute()

logger = logging.getLogger(__name__)


def _csv2dict(lines) -> list[dict]:
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

    qr_content_list = create_qr_meta_list(f_json)

    print("PATH:", str(p_root))
    for _idx, _qr_info in enumerate(qr_content_list):
        _file, _title, _bottom, _qr_content = _qr_info
        _f_qr = p_root.joinpath("out", _file)
        print(f"CREATE QR CODE: {str(_f_qr)}")
        create_qrcode(_f_qr, _qr_content, _title, _bottom)
