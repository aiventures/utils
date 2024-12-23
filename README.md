# utils

## Change Log 
* **2024/09/24** Work in Progress ...
* **2024/09/09** Copied over [tools code base](https://github.com/aiventures/tools)

## Elevator Pitch

Command Line Utils V2 as the tools project has become too bloated. To make a comofortable developer experience on the command line and not be required to memrize all command line commands this tool comes to the rescue.

## Features 

* Create a Pydantic CSV Model for several files 
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

## Installation, Dependencies, Test Drive

## Installation

In the project root, and in your VENV, install by: 

```
pip install -e .[dev]
```
* **Dependencies** [requirements.txt](https://github.com/aiventures/utils/blob/main/requirements/requirements.txt)

## Sample Configuration

A sample config showcasing the config structure is stored here

```<root>/test_data/test_config/config_env_template.json``` 

If you run
```python <root>/src/demo/demo_config.py```, this sample config (with some functional configs) will be copied to path ```[home]/.cli_client/``` directory (with home path being an os dependent path)

## Configuration Bootstrapping Order 

If you do not instanciate the configuration file for yourself by directly submitting config file location, it will be attempted to bootstrap the configuration file in the following order ```<path>\utils\src\util\config_env.py > _bootstrap_path ```):
1. `ENV` variable `CLI_CONFIG_DEMO` is set (any non `None` value): use demo configuration
2. `ConfigEnv` constructor is supplied with a `f_config` file path: use path from there
3. `ENV` variable `CLI_CONFIG_ENV` is set: Path stored in the `ENV`variable is used
4. Config file stored here: `[HOME]/.cli_client/cli_config.json`

Configuration should be OS independent, but only tested on Win Os.

## Commands 

**\<tbd>**

## Design & How It works

* on the root level of the project run pytest to see some feature 
* some modules also provide some functionality on `main`. So you can directly start it 
* To look for configuration hints check where the Constants in `utils/src/util/constants.py` are referenced 

## Implementation steps

* Define a "virtual twin" of your work environment mapping it into a config json (example ```/test_config/config_env_local.json``` )

## Todos / Ideas

* `20241216` create a function to count lfs stub sizes  
* `20241216` make worklog_txt and todo_txt work together 
* `20241216` Create the styles via command line (Simply Calling the constructor)
* `20241215` Create gliding overtime 
* `20241215` Create a directive / mapping for recording template
* `20241215` Create a time recording template and a parsing method 
* `20241215` Override an Office Time by Home Office 
* `20241215` Add an Over/UnderTime Indicator in calendar and markdown and Tree 
* `20241215` Add Duration separated by Office / Homeoffice to Stats  
* `20241215` Create Icon List with search capabilities based on keywords  
* `20241215` Calculate Total Durations per Month / and Delta to Working Times / directly in calendar model 
* `20241215` Use Rich Text to highlight text searches 
* `20241215` Create a Tree explorer view (including sizes)
* `20241215` Render Calendar as Tree
* `20241215` Create Pydantic Model to render the Calendar markdown list with different options such as  
             only certain types of days to be rendered 
* `20241003` Set Environment from Configuration / optionally save it as well as env file / create a bat file
* ~~`20241002` Parse Placeholder in [...] as links to config in command parser~~
* `20240929` Parsing links, add numbers and allow to launch links from CLI
* `20240929` Create the possibility to store/load the parsed data without processing 
* `20240929` Add a logic to update a value in a configuration in any case (for example when the config is not build up from scratch )
* `20240927` Create an Utility to create Markdown with Date Lines 
* `20240923` Additional attribute to indicate file path conversions (with no info implicitly leading to no conversion)
* ~~`20240923` Move Constants to enums~~
* `20240923` Generate envs to export Configuration as shell / batch setup scripts 
* ~~`20240923` Create Config validation features (Config.json > CHECK > Errors/Warnings > Automatical Clean Up)~~
* ~~`20240923` Create a Config schema (idea: create a yaml with comments and convwert it as json), so that configs can also be validated ~~
* `20240923` Enable `Yaml` 
* ~~`20240923` Create `Typer` SubCommands~~
* ~~`20240923` Link Executables to Configuration~~
* `20240923` Add [todo.txt](https://github.com/todotxt/todo.txt) logic 
* ~~dddd~~



