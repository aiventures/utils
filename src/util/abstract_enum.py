"""Enum Definition with some additional helper methods on Enum"""

from enum import Enum
from typing import Any
import logging
from cli.bootstrap_env import CLI_LOG_LEVEL


logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(CLI_LOG_LEVEL)

class AbstractEnum(Enum):
    """Abstract Enum To Provide some helper methods"""

    @classmethod
    def get_values(cls) -> list:
        """returns maintained filter values"""
        return [c.value for c in cls]

    @classmethod
    def get_names(cls) -> list:
        """returns maintained filter values"""
        return [c.name for c in cls]

    @classmethod
    def as_dict(cls) -> dict:
        """returns the enum as dict"""
        return {c.name: c.value for c in cls}

    @classmethod
    def get_enum(
        cls, key: str, search_name: bool = True, search_value: bool = False, exact: bool = True
    ) -> list | Enum:
        """returns the enum(s) from a key

        Args:
            key (str): search string or key ()
            search_names (bool, optional): Search in name Defaults to True.
            search_values (bool, optional): Search in values Defaults to False.
            exact (bool, optional): Search Mode exact or as containing key mode. Defaults to True.
        """
        out = []
        for c in cls:
            _found = None
            if search_name:
                if exact:
                    if c.name == key:
                        _found = c
                else:
                    if key in c.name:
                        _found = c
            if search_value and not _found:
                if exact:
                    if c.value == key:
                        _found = c
                else:
                    if isinstance(c.value, str) and key in c.value:
                        _found = c

            if _found:
                out.append(_found)

        if exact:
            if len(out) == 1:
                return out[0]
            elif len(out) > 1:
                logger.info(
                    f"[AbstractEnum] Found more entries for key [{key}] in Enum [{cls.__name__}] when doing an exact search"
                )
                return out
        else:
            return out
