
```

  ______ _______ __   _  _____   _____  __   __  _____  _______
 |  ____ |______ | \  | |     | |_____]   \_/   |_____] |______
 |_____| |______ |  \_| |_____| |          |    |       |______
                                                               
                                                

```
#### Description

`B i o i n f o r m a t i c s` pipelines require creating directories, checking intermediate files, checking if those intermediate files have anything in them, checking return/error codes, gzipping, deleting temporary files, converting sam to bam, etc.  `genopype` is a Python package I've developed for creating these bash pipelines quickly, in Python (v2.7+ & 3.5+), and easily.  

#### About

`__author__ = "Josh L. Espinoza"`

`__cite__ = "TBD"`

`__contact__ = "jespinoz@jcvi.org, jol.espinoz@gmail.com"`

`__developmental__ = True`

`__license__ = "BSD-3"`

`__version__ = "2023.4.13"`

#### Installation

```
pip install genopype
conda install -c jolespin genopype
```

#### Usage

```python
# import genopype as gp
from genopype import * 

# Set up a directory dictionary	
directories = dict()
directories["output"] = create_directory("pipeline_testing")
directories["checkpoints"] = create_directory(os.path.join(directories["output"], "checkpoints"))
directories["logs"] = create_directory(os.path.join(directories["output"], "logs"))

# Create a commands.sh file to write to as you build the pipeline
with open(os.path.join(directories["output"], "commands.sh"), "w") as f_cmds:
	ep = ExecutablePipeline(name="Sith", description="The rule of two", f_cmds=f_cmds, checkpoint_directory=directories["checkpoints"], log_directory=directories["logs"], bypass_io_validation_if_checkpoints_exist=True)
	# Step 1
	output_filepaths = [os.path.join(directories["output"], "holocron.txt")]
	message = "Two there should be; no more, no less. One to embody the power, the other to crave it.\n"
	ep.add_step(id="Darth Bane",
	            cmd="echo '{}' > {}".format(message, output_filepaths[0]),
	            output_filepaths=output_filepaths,
	            description = "Begin the rule of two",
	            errors_ok=False,
	            validate_outputs=True,
	)
	# Step 2
	input_filepaths = [os.path.join(directories["output"], "holocron.txt")]
	output_filepaths = [os.path.join(directories["output"], "*.txt")]
	ep.add_step(id="Darth Plagueis",
	            cmd="(cat {} && echo 'jedi') > {} ".format(input_filepaths[0], os.path.join(directories["output"], "wisdom.txt")),
	            input_filepaths=input_filepaths,
	            output_filepaths=output_filepaths,
	            description = "Read the holocron",
	            errors_ok=False,
	            validate_inputs=True,
	            validate_outputs=True,
	)
	# Step 3
	input_filepaths = [os.path.join(directories["output"], "holocron.txt"), os.path.join(directories["output"], "wisdom.txt")]
	output_directory = create_directory(os.path.join(directories["output"], "temple"))
	output_filepaths = [os.path.join(output_directory, "data-crystal.txt"), output_directory]
	cmds = [
	"(",
	"mkdir -p {}".format(output_directory),
	"&&",
	"cat {} {} > {}".format(input_filepaths[0], input_filepaths[1], output_filepaths[0]),
	")",
	
	]
	ep.add_step(id="Darth Sidious",
	            cmd=cmds,
	            input_filepaths=input_filepaths,
	            output_filepaths=output_filepaths,
	            description = "Move the data",
	)
	ep.compile()
	ep.execute(restart_from_checkpoint=3)
	
	# Directory structure
	print("\n", format_header("Directory structure:","_"), "\n", get_directory_tree(directories["output"], ascii=True), sep="", file=sys.stdout)
        

```

#### Output

```
===========================
. .. ... Compiling ... .. .
===========================
Step: 1, Darth Bane | log_prefix = 1__Darth-Bane | Begin the rule of two
Step: 2, Darth Plagueis | log_prefix = 2__Darth-Plagueis | Read the holocron
Step: 3, Darth Sidious | log_prefix = 3__Darth-Sidious | Move the data
_________________________________________
. .. ... Sith || The rule of two ... .. .
_________________________________________

Restarting pipeline from checkpoint: 3

Executing pipeline:   0%|                                                                                                                                                                  | 0/3 [00:00<?, ?it/s]==============
. Darth Bane .
==============
Input: []
Output: ['pipeline_testing/holocron.txt']

Command:
echo 'Two there should be; no more, no less. One to embody the power, the other to crave it.
' > pipeline_testing/holocron.txt

Running. .. ... .....

Log files:
pipeline_testing/logs/1__Darth-Bane.*

Validating the following output files:
[=] File exists (88 bytes): pipeline_testing/holocron.txt

Duration: 00:00:00

==================
. Darth Plagueis .
==================
Input: ['pipeline_testing/holocron.txt']
Output: ['pipeline_testing/*.txt']

Command:
(cat pipeline_testing/holocron.txt && echo 'jedi') > pipeline_testing/wisdom.txt

Validating the following input files:
[=] File exists (88 bytes): pipeline_testing/holocron.txt

Running. .. ... .....

Log files:
pipeline_testing/logs/2__Darth-Plagueis.*

Validating the following output files:
[=] File exists (88 bytes): pipeline_testing/holocron.txt
[=] File exists (93 bytes): pipeline_testing/wisdom.txt

Duration: 00:00:00

=================
. Darth Sidious .
=================
Input: ['pipeline_testing/holocron.txt', 'pipeline_testing/wisdom.txt']
Output: ['pipeline_testing/temple/data-crystal.txt', 'pipeline_testing/temple']

Command:
( mkdir -p pipeline_testing/temple && cat pipeline_testing/holocron.txt pipeline_testing/wisdom.txt > pipeline_testing/temple/data-crystal.txt )

Validating the following input files:
[=] File exists (88 bytes): pipeline_testing/holocron.txt
[=] File exists (93 bytes): pipeline_testing/wisdom.txt

Running. .. ... .....

Log files:
pipeline_testing/logs/3__Darth-Sidious.*

Validating the following output files:
[=] File exists (181 bytes): pipeline_testing/temple/data-crystal.txt
[=] Directory exists (181 bytes): pipeline_testing/temple

Duration: 00:00:00

Executing pipeline: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 3/3 [00:00<00:00, 44.07it/s]

........................
Total duration: 00:00:00
........................

____________________
Directory structure:
____________________
pipeline_testing/
|__ checkpoints/
|   |__ 1__Darth-Bane
|   |__ 2__Darth-Plagueis
|   |__ 3__Darth-Sidious
|__ commands.sh
|__ holocron.txt
|__ logs/
|   |__ 1__Darth-Bane.e
|   |__ 1__Darth-Bane.o
|   |__ 1__Darth-Bane.returncode
|   |__ 2__Darth-Plagueis.e
|   |__ 2__Darth-Plagueis.o
|   |__ 2__Darth-Plagueis.returncode
|   |__ 3__Darth-Sidious.e
|   |__ 3__Darth-Sidious.o
|   |__ 3__Darth-Sidious.returncode
|__ temple/
|   |__ data-crystal.txt
|__ wisdom.txt
```