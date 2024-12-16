"""reading the env var"""

import os

_hugotest = os.environ.get("HUGOTEST")
print(f"[READING FROM PYTHON] Variable HUGOTEST set to [{_hugotest}]")
