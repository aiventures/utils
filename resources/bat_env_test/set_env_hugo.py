"""reading the env var"""

import os

os.environ["HUGOTEST"] = "SET_FROM_PYTHON"
print("[SETTING FROM PYTHON] Variable HUGOTEST set to os.environ['HUGOTEST']")
