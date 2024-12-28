""" Model Representation for todo_txt 
    https://github.com/todotxt/todo.txt
    http://todotxt.org/

    Completion: "x" at the start of the line for completed tasks
    Priority: (A) to (Z) at the start of the line, optional
    Dates:
    - Creation date: YYYY-MM-DD format, optional
    - Completion date: YYYY-MM-DD format, only for completed tasks
    Description: The actual task text
    Projects: Denoted by "+project" anywhere in the description
    Contexts: Denoted by "@context" anywhere in the description    
    key:value : Key Value Pairs
    will transform lines of strings in todo format into json and vice versa
"""

from datetime import datetime as DateTime
from pydantic import BaseModel,Field
from typing import List, Optional, Union, Dict
from enum import Enum, StrEnum
from model.model_calendar import (CalendarDayType,DayTypeEnum)

# todo_list = ["x  2020-12-02 2020-12-01 Python with Deskbike @Computer +Python @Deskbike +Health",
#              "x  2020-12-02 2020-12-01 Python with Deskbike +Python +Health @Computer @Deskbike",
#              "x 2020-12-20 Visit Stuttgart +Friend @Offsite due:2020-12-12 other_attribute:34",
#              "(A) 2020-8-20 NO ATTRIBUTES due:2020-12-12",
#              "2020-11-20 Yet another task + @Offsite due:2020-12-12",
#              "(C) Visit Another +Friend @Offsite due:2020-12-12 hash:b06e78f00e8689ec52da48aaae4d6553",
#              "(C) Visit Another HASH +Friend @Offsite hash:45rerererer due:2020-12-12"
#              ]
#

class Todo(BaseModel):
    """ Model Representation for Todo TXT """
    original : Optional[str]=None
    hash : str
    complete : Optional[bool]=False
    priority : str = Field(pattern=r'[a-zA-Z]')|None
    date_created: Optional[DateTime] = None
    date_completed: Optional[DateTime] = None
    date_changed: Optional[DateTime] = None
    description : Optional[str] = None
    projects : Optional[List] = []
    contexts : Optional[List] = []
    attributes : Optional[Dict] = {}
