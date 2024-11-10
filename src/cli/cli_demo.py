""" sample cli config """
import logging
import typer
import time
import sys
import os
from typing import List
from rich import print
from rich.prompt import Prompt
from rich.progress import BarColumn,DownloadColumn
from rich.progress import track
from util import constants as C
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing_extensions import Annotated,Optional
from util.const_local import LOG_LEVEL
from util.persistence import Persistence

# This is just a typer playground, topics of interest in the typer documentation
# Password https://typer.tiangolo.com/tutorial/options/password/
# force only one option / but not the other  True or False
# boolean options https://typer.tiangolo.com/tutorial/parameter-types/bool/
# declaring short names: https://typer.tiangolo.com/tutorial/parameter-types/bool/#short-names
# Help Options: https://typer.tiangolo.com/tutorial/options/help/
# ENVIRONMENT vars: https://typer.tiangolo.com/tutorial/arguments/envvar/
# Callback Options / Validations
# https://typer.tiangolo.com/tutorial/options/callback-and-context/#validate-cli-parameters
# Additional Command Line Options / Short Versions
# Password and repeat https://typer.tiangolo.com/tutorial/options/password/
# Alternative Names / Short Names
# https://typer.tiangolo.com/tutorial/parameter-types/bool/?h=short#alternative-names
# Parameter Types: Boolean CLI Options,UUID,DateTime,Enum - Choices,Path,File,Custom Types
# https://typer.tiangolo.com/tutorial/parameter-types/


logger = logging.getLogger(__name__)
# get log level from environment if given
logger.setLevel(int(os.environ.get(C.CLI_LOG_LEVEL,logging.INFO)))

app = typer.Typer(name="cli_demo_client", add_completion=False, help="Demo Parser (show casing typer)")

sample_int = 10
sample_str = "HUGO"

# you may define the params separately
_annot_test = Annotated[str, typer.Option(help="HELP TEXT param2_annot")]
# Annotation Optional


@app.command("params1")
def demo_params1(param1:int,
          param2_annot: _annot_test,
          param3_opt:str="OPTIONALPARAM3",
          param4_opt_annot: Annotated[str, typer.Option()] = "OPTIONALPARAM4",
          param5_opt_annot: Annotated[Optional[str], typer.Argument(help="params5 opt help text")]=None
):
    """ Test Driving several options

    Args:
        param1 (int): DOCTYPE for param1
        param2_annot (Annotated[str, typer.Option, optional): DOCTYPE for param2_annot
        param3_opt (str, optional): DOCTYPE for param3_opt
        param4_opt_annot (Annotated[str, typer.Option, optional): DOCTYPE for param4_opt_annot

    """
    print(f"Hello params1:  param1 {param1}, param2_annot {param2_annot}, param3_opt {param3_opt}, param4_opt_annot {param4_opt_annot}, param5_opt_annot {param5_opt_annot}")

@app.command("demo1")
def demo_demo1(param_str:str,param_out:str="Test"):
    """demo1 method summary

    Args:
        param_str (str): xyz_description
        test (str, optional): test_description. Defaults to "Test".
    """
    print(f"Hello Share Parser CLI {param_str} param_opt {param_out}")
    return None
    pass

@app.command("demo2")
def demo_demo2(param_str:str,param_opt:str="Test"):
    """demo1 method summary

    Args:
        xyz (str): xyz_description
        test (str, optional): test_description. Defaults to "Test".
    """
    print(f"Hello Share Parser CLI {param_str} param_opt [{param_opt}]")


@app.command("demo_args1")
def demo_args1(req_param1:str, req_param2: Annotated[str, typer.Option("--req1")]):
    """ testing arguments req_param1 as positional arg and req_param2 as required
    """
    # https://typer.tiangolo.com/tutorial/options/name/
    # since rich is used we need to mask the brackets
    print(f"req_param1 \[{req_param1}] req_param2 \[{req_param2}]")

@app.command("prompt")
def demo_prompt():
    """ demo_prompt
    """
    # https://typer.tiangolo.com/tutorial/prompt/#prompt-with-rich
    name = Prompt.ask("[bright_red] Enter your name :sunglasses:")
    print(f"Hey there {name}!")
    name2 = typer.confirm("Enter someething", abort=True)
    print(f"OUTPUT {name2}")

@app.command("prompt2")
def demo_prompt2(
    force: Annotated[
        bool, typer.Option(prompt="Are you sure you want to do this?")
    ],
):
    """ testing promp """
    # this is an option to ask for values in case not given at the command line
    if force:
        print(f"FORCE was chosen")
    else:
        print("Operation cancelled")

@app.command("progress")
def demo_progress():
    """ demo progress bar """
    # https://typer.tiangolo.com/tutorial/progressbar/
    total = 0
    # for value in track(["a","b","c"], description="Processing..."):
    for value in track(range(100), description="Processing..."):
        time.sleep(0.05)
        total += 1
    print(f"Processed {total} things.")

@app.command("progress2")
def demo_progress2():
    """ demo progress bar 2 """
    # https://typer.tiangolo.com/tutorial/progressbar/
    users = ["Camila", "Rick", "Morty"]

    def iterate_user_ids():
        # Let's imagine this is a web API, not a range()
        for i in range(100):
            yield i

    print("### Progress from list")
    with typer.progressbar(users) as progress:
        for user in progress:
            typer.echo(user)

    print("### Progress from length")
    total = 0
    with typer.progressbar(iterate_user_ids(), length=100,show_percent=True,fill_char="🐽") as progress:
        for value in progress:
            # Fake processing time
            time.sleep(0.05)
            total += 1
    print(f"Processed {total} user IDs.")

@app.command("progress_sample")
def demo_progress_sample():
    """progress from test data sample
    """
    p = os.path.join(C.PATH_ROOT,"test_data")
    # display the file search
    _file_objects = Persistence.find(p,show_progress=True)


@app.command("progress_nested")
def demo_progress_nested():
    """ demo progress for nested progress bars"""
    # https://github.com/Textualize/rich/discussions/950#discussioncomment-300794
    # https://typer.tiangolo.com/tutorial/progressbar/#progress-bar_1
    # COlor Table https://rich.readthedocs.io/en/latest/appendix/colors.html

    class MyProgress(Progress):
        def get_renderables(self):
            for task in self.tasks:
                if task.fields.get("progress_type") == "mygreenbar":
                    # self.columns = ("[green]Rich is awesome!", BarColumn(bar_width=20,style="bar.back"))                    
                    self.columns = ("[green1]Rich is awesome!", BarColumn(bar_width=20,style="green1"))
                if task.fields.get("progress_type") == "mybluebar":
                    self.columns = (
                        "[blue]Another bar with a different layout",
                        BarColumn(bar_width=10),
                        #"•",
                        # DownloadColumn(),
                    )
                yield self.make_tasks_table([task])

    with MyProgress() as progress:
        num_outer = 5
        num_inner = 10
        taskone = progress.add_task("taskone", progress_type="mygreenbar",total=num_outer)
        # tasktwo = progress.add_task("tasktwo", progress_type="mybluebar",total=num_inner)
        for outer in range(num_outer):
            progress.update(taskone,advance=1)
            tasktwo = progress.add_task("tasktwo", progress_type="mybluebar",total=num_inner)
            for _ in range(num_inner):
                progress.update(tasktwo,advance=1)
                time.sleep(0.1)
            time.sleep(0.1)

@app.command("spinner")
def demo_spinner():
    """ demo spinner """
    # https://typer.tiangolo.com/tutorial/progressbar/#progress-bar_1
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Processing...", total=None)
        progress.add_task(description="Preparing...", total=None)
        time.sleep(5)
    print("Done!")

@app.command("launcher")
def demo_launcher():
    """ demo launcher """
    # https://typer.tiangolo.com/tutorial/launch/
    print("Opening Notepad")
    typer.launch("notepad")
    print("opening a link")
    typer.launch("https://typer.tiangolo.com")

@app.command("open_file")
def demo_open_file():
    """ demo launcher """
    # https://typer.tiangolo.com/tutorial/launch/
    print("locating an executable")
    _cmd = "Notepad++"
    app_dir = typer.get_app_dir(_cmd)
    print(f"APP [{_cmd}], Path [{app_dir}]")
    typer.launch(_cmd,locate=True)
    _file = os.path.abspath(__file__)
    print(f"OPENING EXPLORER USING FILENAME [{_file}]")
    typer.launch(_file, locate=True)
    typer.launch(_file, locate=False)
    _file = os.path.join(C.PATH_ROOT,"test_data","test_path","testfile_for_table.txt")
    print(f"OPENING FILE [{_file}]")
    typer.launch(_file, locate=False)
    print(f"OPENING FILE LOCATION [{_file}]")
    typer.launch(_file, locate=True)

@app.command("demo_list")
def demo_list(params: Optional[List[str]]=typer.Option(None)):
    """ Lists as input (needs to be comma separated list of args eg args1,args2) """
    print(f"HELLO {params}")

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s %(module)s:[%(name)s.%(funcName)s(%(lineno)d)]: %(message)s',
                        level=LOG_LEVEL, stream=sys.stdout, datefmt="%Y-%m-%d %H:%M:%S")
    app()
