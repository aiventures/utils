# utils

## Change Log 
* **2024/09/24** Work in Progress ...
* **2024/09/09** Copied over [tools code base](https://github.com/aiventures/tools)

## Elevator Pitch

Command Line Utils V2 as the tools project has become too bloated. To make a comofortable developer experience on the command line and not be required to memrize all command line commands this tool comes to the rescue.

## Features 

* Automatically locate executables using `where` `under the hood
* Convert file paths using `cygpath` (comes with git)
* Searching in file content and paths (as an alternative to `find` and `grep)
* Parsing 
  * csv files
  * creating a markdown file from exported browser bookmarks/favorites
* Command Line Console enabling using [typer](https://pypi.org/project/typer/)
* Color Formatting using [rich](https://pypi.org/project/rich/), definition of app specific Color Themes and Styles 
* Formatted Log Output 
* Launching applications from the console
* Configuration Display options
* Data Parsing
  * Capabilities to parse to/from dict <-> json
  * Parsing tree like structrues

## Installation & Dependencies 

```
pip install -e .[dev]
```
* **Dependencies** [requirements.txt](https://github.com/aiventures/utils/blob/main/requirements/requirements.txt)

## Commands 

**\<tbd>**

## Design & How It works

* on the root level of the project run pytest to see some feature 
* some modules also provide some functionality on `main`. So you can directly start it 
* the unit test will generate a `/test_config/config_env_local.json` to illustrate what needs to be configured.
* To look for configuration hints check where the Constants in `utils/src/util/constants.py` are referenced 

## Implementation steps

* define a virtual twin of your work environment mapping it into a config json (example ```/test_config/config_env_local.json``` )

## Todos 

* `20240923` Move Constants to enums 
* `20240923` Generate envs to export Configuration as shell / batch setup scripts 
* `20240923` Create Config validation features (Config.json > CHECK > Errors/Warnings > Automatical Clean Up)
* `20240923` Create a Config schema (idea: create a yaml with comments and convwert it as json), so that configs can also be validated 
* `20240923` Enable `Yaml` 
* `20240923` Create `Typer` SubCommands
* `20240923` Link Executables to Configuration
* `20240923` Add [todo.txt](https://github.com/todotxt/todo.txt) logic 
* ~~dddd~~



