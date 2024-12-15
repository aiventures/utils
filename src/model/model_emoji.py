""" Emoji Models
    PyDantic Model for the emoji jsons from     
    # emoji list / with groups and subgroup ids
    https://github.com/milesj/emojibase/blob/master/packages/data/en/data.raw.json    
    # group and metadata definition
    https://github.com/milesj/emojibase/blob/master/packages/data/meta/groups.json
"""

from datetime import datetime as DateTime
from typing import Optional,Dict,Annotated,List,Literal
from enum import StrEnum
from pydantic import BaseModel,TypeAdapter,Field,RootModel

class EmojiMeta(BaseModel):
    """ Emoji MetaModel """
    label : str = None
    hexcode : str = None
    tags : Optional[List] = None
    emoji : str = None
    text : str = None
    type : int = None
    order : int = None
    group : int = None
    subgroup : int = None
    version : float = None
    tone : Optional[str] = None

class EmojiMetaRaw(EmojiMeta):
    """ Metamodel with skins,  """
    skins: Optional[List[EmojiMeta]] = None

class EmojiGroups(BaseModel):
    """ Model for the groups file """
    groups : Dict[str,str]
    hierarchy : Dict[str,List[int]]
    subgroups : Dict[str,str]

