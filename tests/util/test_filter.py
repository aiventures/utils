"""Unit Tests for the Constants Class"""

import logging
import os
from util import constants as C

logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL, logging.INFO)))
