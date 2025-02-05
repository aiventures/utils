"""Emoji Models
PyDantic Model for the emoji jsons from
# emoji list / with groups and subgroup ids
https://github.com/milesj/emojibase/blob/master/packages/data/en/data.raw.json
# group and metadata definition
https://github.com/milesj/emojibase/blob/master/packages/data/meta/groups.json
# Unicode Emoji Definitions
"https://unicode.org/Public/emoji/latest/"
_file = "emoji-sequences.txt"
"""

from typing import Optional, Dict, List, Annotated
from pydantic import BaseModel, Field, TypeAdapter


class EmojiRawType(BaseModel):
    """unicode emojis as refered by link above"""

    num: Optional[int] = None
    # class cant be used as name
    class_: Optional[str] = Field(None, alias="class")
    # export to dict using
    # instance = MyModel(class_="example")
    # print(instance.model_dump(by_alias=True))
    subclass: Optional[str] = None
    code: Optional[str] = None
    char: Optional[str] = None
    info: Optional[str] = None


class EmojiMetaType(EmojiRawType):
    """Emoji Metadata enriched with descriptions"""

    short_txt: Optional[str] = None
    description: Optional[str] = None


# derived models
EmojiMetaDictModel = Dict[str, EmojiMetaType]
EmojiMetaDictAdapter = TypeAdapter(EmojiMetaDictModel)
EmojiMetaDictType = Annotated[EmojiMetaDictModel, EmojiMetaDictAdapter]


class EmojiBaseMeta(BaseModel):
    """Emoji MetaModel"""

    label: str = None
    hexcode: str = None
    tags: Optional[List] = None
    emoji: str = None
    text: str = None
    type: int = None
    order: int = None
    group: int = None
    subgroup: int = None
    version: float = None
    tone: Optional[str] = None


class EmojiBaseMetaRaw(EmojiBaseMeta):
    """Metamodel with skins,"""

    skins: Optional[List[EmojiBaseMeta]] = None


class EmojiBaseGroups(BaseModel):
    """Model for the groups file"""

    groups: Dict[str, str]
    hierarchy: Dict[str, List[int]]
    subgroups: Dict[str, str]
