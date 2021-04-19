# -*- coding: utf-8 -*-
from __future__ import print_function, division
import os, sys, glob, time,subprocess, random
from collections import OrderedDict, Counter
# Pathlib
try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib
# Scandir
try:
    from os import scandir
except ImportError:
    from scandir import scandir
# Soothsayer utils
from soothsayer_utils import *


# Know Bugs:
# * Currently (2019.07.26), the "completed_message" parameter does not work.


# Check filename
def check_filename(filename, acceptable_characters={".","-","_"}):
    status_ok = True
    for character in str(filename).lower():
        conditions = [
        character.isalnum(),
        character in acceptable_characters,
        # character != " ",
        ]
        if not any(conditions):
            status_ok = False
            break
    return status_ok

# Format filename
def format_filename(name, replacement_character="_", acceptable_characters={".","-","_"}):
    listed_string = list(name)
    idx_nonalnum = list()
    for i, character in enumerate(listed_string):
        if not check_filename(character):
            idx_nonalnum.append(i)
    for i in idx_nonalnum:
        listed_string[i] = replacement_character
    return "".join(listed_string)

# Create directory
def create_directory(directory, sleep=(0.016180339887, 1.6180339887)):
    # Sleep was added so files aren't created at the same time
    if bool(sleep):
        sleep_duration = random.uniform(sleep[0], sleep[1])
        time.sleep(sleep_duration)
    assert is_path_like(directory, path_must_exist=False)
    # directory = os.path.realpath(directory)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

# Validating file existence
def validate_file_existence(paths, prologue="Validating the following files:", minimum_filesize=2, f_verbose=None):
    if is_file_like(f_verbose) or (f_verbose is None):
        print(prologue, file=f_verbose)

    paths_expanded = list()
    for path in paths:
        if "*" in path:
            paths_expanded += glob.glob(path)
        else:
            # path = os.path.realpath(path)
            paths_expanded.append(path)
    for path in paths_expanded:
        # Get the absolute path
        # path = os.path.realpath(path)
        # Get the path to the symlink target
        if os.path.islink(path):
            path = os.readlink(path)
        assert os.path.exists(path), "The following path does not exist: {}".format(path)
        # original_path = None
        # symlink = None
        if os.path.islink(path):
            path = os.readlink(path)
        if not os.path.isdir(path):
            size_bytes = os.path.getsize(path)

            assert size_bytes >= minimum_filesize, "The following file appears to be empty ({} bytes): {}".format(size_bytes, path)
            if is_file_like(f_verbose) or (f_verbose is None):
                size_mb = size_bytes >> 20
                if size_mb < 1:
                    print("[=] File exists ({} bytes):".format(size_bytes), path, file=f_verbose)

                else:
                    print("[=] File exists ({} MB):".format(size_mb), path, file=f_verbose)
        else:
            size_bytes = get_directory_size(path)
            assert size_bytes >= minimum_filesize, "The following directory appears to be empty ({} bytes): {}".format(size_bytes, path)
            if is_file_like(f_verbose) or (f_verbose is None):
                size_mb = size_bytes >> 20
                if size_mb < 1:
                    print("[=] Directory exists ({} bytes):".format(size_bytes), path, file=f_verbose)
                else:
                    print("[=] Directory exists ({} MB):".format(size_mb), path, file=f_verbose)

# Get directory tree structure
def get_directory_tree(root, ascii=False):
    if not ascii:
        return DisplayablePath.view(root)
    else:
        return DisplayablePath.get_ascii(root)

# Directory size
def get_directory_size(path_directory='.'):
    """
    Adapted from @Chris:
    https://stackoverflow.com/questions/1392413/calculating-a-directorys-size-using-python
    """
    path_directory = format_path(path_directory)

    total_size = 0
    seen = {}
    for dirpath, dirnames, filenames in os.walk(path_directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                stat = os.stat(fp)
            except OSError:
                continue

            try:
                seen[stat.st_ino]
            except KeyError:
                seen[stat.st_ino] = True
            else:
                continue

            total_size += stat.st_size

    return total_size

# ===============
# Shell utilities
# ===============
# # View directory structures
class DisplayablePath(object):
    """
    Display the tree structure of a directory.

    Implementation adapted from the following sources:
        * Credits to @abstrus
        https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python
    """
    display_filename_prefix_middle = '|__'
    display_filename_prefix_last = '|__'
    display_parent_prefix_middle = '    '
    display_parent_prefix_last = '|   '

    def __init__(self, path, parent_path, is_last):
        self.path = pathlib.Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None):
        root = pathlib.Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(list(path
                               for path in root.iterdir()
                               if criteria(path)),
                          key=lambda s: str(s).lower())
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                for item in cls.make_tree(path, parent=displayable_root, is_last=is_last, criteria=criteria):
                    yield item
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    def displayable(self):
        if self.parent is None:
            return self.displayname

        _filename_prefix = (self.display_filename_prefix_last
                            if self.is_last
                            else self.display_filename_prefix_middle)

        parts = ['{!s} {!s}'.format(_filename_prefix,
                                    self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self.display_parent_prefix_middle
                         if parent.is_last
                         else self.display_parent_prefix_last)
            parent = parent.parent

        return ''.join(reversed(parts))

    # Additions by Josh L. Espinoza for Soothsayer
    @classmethod
    def get_ascii(cls, root):
        ascii_output = list()
        paths = cls.make_tree(root)
        for path in paths:
            ascii_output.append(path.displayable())
        return "\n".join(ascii_output)
    @classmethod
    def view(cls, root, file=sys.stdout):
        print(cls.get_ascii(root), file=file)



# Bash commands
class Command(object):
    """
    Run bash commands and stuff.

    Recommended usage:
    ------------------
    with open("test_commands.sh", "w") as f_cmds:
        cmd = Command("echo ':)' > testing_output.txt", name="TEST", f_cmds=f_cmds)
        cmd.run(epilogue="footer", prologue="header", checkpoint="testing_output.txt.checkpoint")

    or

    f_cmds = open("test_commands.sh", "w")
    cmd = Command("echo ':)'' > testing_output.txt", name="TEST", f_cmds=f_cmds)
    cmd.run(epilogue="footer", prologue="header", checkpoint="testing_output.txt.checkpoint")
    f_cmds.close()

    Just in case you need a quick one-liner [not recommended but works]:
    -------------------------------------------------------------------
    cmd = Command("echo ':)'' > testing_output.txt", name="TEST", f_cmds="test_commands.sh")
    cmd.run(epilogue="footer", prologue="header", checkpoint="testing_output.txt.checkpoint").close()

    or

    cmd = Command("echo ':)'' > testing_output.txt", name="TEST", f_cmds="test_commands.sh")
    cmd.run(epilogue="footer", prologue="header", checkpoint="testing_output.txt.checkpoint")
    cmd.close()

    Future:
    -------
    * Create an object called ExecutablePipeline that wraps Command objects together
    * Something like this:
        ep = ExecutablePipeline(name="RNA-seq mapping", description="Quality trim, remove contaminants, and map reads to reference")
        # This method
        ep.create_step(name="kneaddata", pos=1, checkpoint="path/to/checkpoint", write_stdout="path/to/stdout", write_stderr="path/to/stderr", write_returncode="path/to/returncode")
        ep["kneaddata"].set_inputs(*?)
        ep["kneaddata"].set_outputs(*?)
        # or this method
        ep.create_step(name="kneaddata", pos=1, checkpoint="path/to/checkpoint", write_stdout="path/to/stdout", write_stderr="path/to/stderr", write_returncode="path/to/returncode", inputs=*?, outputs=*?)
        ep.execute(?*)

    Here is an example for constructing pipelines:
    -------------------------------------------------------------------
    # =========
    # Utility
    # =========
    def process_command(cmd, f_cmds, logfile_name, description, directories, io_filepaths):
        start_time = time.time()
        # Info
        program = logfile_name.split("_")[-1]
        print(description, file=sys.stdout)
        print("Input: ", io_filepaths[0], "\n", "Output: ", io_filepaths[1], sep="", file=sys.stdout)
        print("Command: ", " ".join(cmd), file=sys.stdout)
        executable = Command(cmd, name=logfile_name, description=description, f_cmds=f_cmds)
        executable.run(
            prologue=format_header(program, "_"),
            dry="infer",
            errors_ok=False,
            error_message="Check the following files: {}".format(os.path.join(directories["log"], "{}.*".format(logfile_name))),
            checkpoint=os.path.join(directories["checkpoints"], "{}".format(logfile_name)),
            write_stdout=os.path.join(directories["log"], "{}.o".format(logfile_name)),
            write_stderr=os.path.join(directories["log"], "{}.e".format(logfile_name)),
            write_returncode=os.path.join(directories["log"], "{}.returncode".format(logfile_name)),
            f_verbose=sys.stdout,
        )
        print("Duration: {}".format(executable.duration_), file=sys.stdout)
        return executable
    # =========
    # Kneaddata
    # =========
    program = "kneaddata"

    # Add to directories
    output_directory = directories[("intermediate", program)] = create_directory(os.path.join(directories["intermediate"], "{}_output".format(program)))

    # Info
    step = "1"
    logfile_name = "{}_{}".format(step, program)
    description = "{}. {} | Removing human associated reads and quality trimming".format(step, program)

    # i/o
    input_filepath = [opts.r1, opts.r2]
    output_filename = ["kneaddata_repaired_1.fastq.gz", "kneaddata_repaired_2.fastq.gz"]
    output_filepath = list(map(lambda filename: os.path.join(output_directory, filename), output_filename))
    io_filepaths = [input_filepath,  output_filepath]

    # Parameters
    params = {
        "reads_r1":input_filepath[0],
        "reads_r2":input_filepath[1],
        "output_directory":output_directory,
        "opts":opts,
        "directories":directories,
    }
    cmd = get_kneaddata_cmd(**params)
    process = process_command(cmd, f_cmds=f_cmds, logfile_name=logfile_name, description=description, directories=directories, io_filepaths=io_filepaths)
    sys.stdout.flush()

    """
    def __init__(self, cmd, name=None, description=None, f_cmds=sys.stdout ):

        if isinstance(cmd, str):
            cmd = [cmd]
        cmd = " ".join(cmd)
        self.cmd = cmd
        if not is_file_like(f_cmds):
            if is_path_like(f_cmds, path_must_exist=False):
                f_cmds = open(f_cmds, "w")
        self.f_cmds = f_cmds
        self.name = name
        self.description = description

    def __repr__(self):
        class_name = str(self.__class__)[17:-2]
        return '{}(name={}, description={}, cmd="{}")'.format(class_name, self.name, self.description, self.cmd)
    def close(self):
        self.f_cmds.close()
        return self
    def _write_output(self, data, filepath):
        if filepath is not None:
            if not is_file_like(filepath):
                filepath = format_path(filepath)
                f_out = open(filepath, "w")
            else:
                f_out = filepath
            print(data, file=f_out)
            f_out.flush()
            if self.f_cmds not in {sys.stdout, sys.stderr}:
                os.fsync(self.f_cmds.fileno())
            if f_out not in {sys.stdout, sys.stderr}:
                f_out.close()

    # Run command
    def run(
        self,
        prologue=None,
        epilogue=None,
        errors_ok=False,
        dry="infer",
        checkpoint=None,
        write_stdout=None,
        write_stderr=None,
        write_returncode=None,
        close_file=False,
        checkpoint_message_notexists="Running. .. ... .....",
        checkpoint_message_exists="Loading. .. ... .....",
        error_message=None,
        completed_message=None,
        f_verbose=None,
        n_linebreaks=1,
        acceptable_returncodes=[0],
        popen_kws=dict(),
        ):
        """
        Should future versions should have separate prologue and epilogue for f_cmds and f_verbose?
        """
        # Verbose
        if f_verbose is None:
            f_verbose = sys.stdout
        # Return codes
        if isinstance(acceptable_returncodes, int):
            acceptable_returncodes = [acceptable_returncodes]
        assert all(map(lambda returncode:isinstance(returncode, int), acceptable_returncodes)), "Please use integer return codes"
        # ----------
        # Checkpoint
        # ----------
        if checkpoint is not None:
            checkpoint = format_path(checkpoint)
        if dry == "infer":
            dry = False
            if checkpoint is not None:
                if os.path.exists(checkpoint):
                    dry = True
                    if checkpoint_message_exists is not None:
                        print(checkpoint_message_exists, file=f_verbose)
                        f_verbose.flush()
                else:
                    if checkpoint_message_notexists is not None:
                        print(checkpoint_message_notexists, file=f_verbose)
                        f_verbose.flush()


        # ----
        # Info
        # ----
        if self.f_cmds is not None:
            # Prologue
            if prologue is not None:
                self.prologue_ = prologue
                print("#", prologue, file=self.f_cmds)
            # Command
            print(self.cmd, file=self.f_cmds)
            # Epilogue
            if epilogue is not None:
                self.epilogue_ = epilogue
                print("#", epilogue, file=self.f_cmds)
            # Padding
            assert n_linebreaks >= 0, "`n_linebreaks` must be an integer >= 0"
            print("\n"*(n_linebreaks-1), file=self.f_cmds)
            self.f_cmds.flush()
            if self.f_cmds not in {sys.stdout, sys.stderr}:
                os.fsync(self.f_cmds.fileno())
        # Run
        if not dry:
            start_time = time.time()
            f_stdout = subprocess.PIPE
            if write_stdout is not None:
                write_stdout = format_path(write_stdout)
                f_stdout = open(write_stdout, "wb")
            f_stderr = subprocess.PIPE
            if write_stderr is not None:
                write_stderr = format_path(write_stderr)
                f_stderr = open(write_stderr, "wb")
            # Execute the process
            self.process_ = subprocess.Popen(self.cmd, shell=True, stdout=f_stdout, stderr=f_stderr, **popen_kws) #! Future: Use file objects instead here so it can be written in real time
            # Wait until process is complete and return stdout/stderr
            self.stdout_, self.stderr_ = self.process_.communicate() # Use this .communicate instead of .wait to avoid zombie process that hangs due to defunct. Removed timeout b/c it's not available in Python 2

            # Set stdout and stderr to the contents of the file object created...or just the path then do a get_stdout() function

            if hasattr(f_stdout, "close"):
                f_stdout.close()
            if hasattr(f_stderr, "close"):
                f_stderr.close()

            # Return code
            self.returncode_ = self.process_.returncode
            self.duration_ = format_duration(start_time)

            # # stdout
            # if isinstance(self.stdout_, bytes):
            #     self.stdout_ = self.stdout_.decode("utf-8")
            # self._write_output(data=self.stdout_, filepath=write_stdout)
            # # stderr
            # if isinstance(self.stderr_, bytes):
            #     self.stderr_ = self.stderr_.decode("utf-8")
            # self._write_output(data=self.stderr_, filepath=write_stderr)

            # Return code
            self._write_output(data=self.returncode_, filepath=write_returncode)



            # Check
            if not errors_ok:
                if self.returncode_ not in acceptable_returncodes:
                    if error_message is not None:
                        print(error_message, file=f_verbose)
                    sys.exit(self.returncode_)
            if self.returncode_ in acceptable_returncodes:
                if completed_message is not None:
                    print(completed_message, file=f_verbose)

            # Create checkpoint
            if checkpoint is not None:
                if self.returncode_ in acceptable_returncodes:
                    duration = format_duration(start_time)
                    with open(checkpoint, "w") as f_checkpoint:
                        print(get_timestamp(), duration, file=f_checkpoint)
        # Close file object
        if self.f_cmds not in {None, sys.stdout, sys.stderr}:
            if close_file:
                self.close()
        return self


# Executable
class ExecutablePipeline(object):
    def __init__(self,
                 name=None,
                 description=None,
                 checkpoint_directory=None,
                 log_directory=None,
                 checkpoint_message_notexists="Running. .. ... .....",
                 checkpoint_message_exists="Loading. .. ... .....",
                 f_cmds=None,
                 f_verbose=None,
                 bypass_io_validation_if_checkpoints_exist=False,
                 **metadata
                ):
        self.name = name
        self.description = description
        self.metadata = metadata
        self.executables = dict()
        self.f_cmds = f_cmds
        self.f_verbose = f_verbose
        self.checkpoint_message_notexists = checkpoint_message_notexists
        self.checkpoint_message_exists = checkpoint_message_exists
        # Log directory
        self.log_directory = log_directory
        if log_directory is not None:
            assert is_path_like(log_directory, path_must_exist=False), "`{}` is not path-like".format(log_directory)
            log_directory = format_path(log_directory)
            self.log_directory = create_directory(log_directory)
        # Checkpoint directory
        self.checkpoint_directory = checkpoint_directory
        if checkpoint_directory is not None:
            assert is_path_like(checkpoint_directory, path_must_exist=False), "`{}` is not path-like".format(checkpoint_directory)
            checkpoint_directory = format_path(checkpoint_directory)
            self.checkpoint_directory = create_directory(checkpoint_directory)
        self.bypass_io_validation_if_checkpoints_exist = bypass_io_validation_if_checkpoints_exist

        # Compiled
        self.compiled = False

    # Add step in pipeline
    def add_step(self,
                # Required
                id,
                cmd,
                step="infer",
                log_prefix="infer",
                # Descriptions
                description=None,
                # I/O
                input_filepaths=None,
                output_filepaths=None,
                # Utility
                dry="infer",
                errors_ok=False,
                validate_inputs=True,
                validate_outputs=True,
                acceptable_returncodes=[0],
                ):
        # Step
        if step == "infer":
            step = len(self.executables) + 1
        assert isinstance(step, int), "Please specify an integer step."

        # if bypass_io_validation_if_checkpoint_exists:
        #    HOW TO DETEREMINE WHAT THE CHECKPOINT FILE IS AT THIS STAGE
        #     if os.path.exists(checkpoint):
        #
        attrs = dict()
        attrs["step"] = step

        # Command
        attrs["executable"] = Command(cmd,
                          name=id,
                          description=description,
                          f_cmds=self.f_cmds,
        )
        attrs["description"] = description
        attrs["log_prefix"] = log_prefix

        #I/O
        if isinstance(input_filepaths, str):
            input_filepaths = [input_filepaths]
        if input_filepaths is None:
            input_filepaths = list()
        attrs["input_filepaths"] = input_filepaths
        if isinstance(output_filepaths, str):
            output_filepaths = [output_filepaths]
        if output_filepaths is None:
            output_filepaths = list()
        attrs["output_filepaths"] = output_filepaths

        # Checkpoints
        attrs["checkpoint"] = None
        attrs["write_stdout"] = None
        attrs["write_stderr"] = None
        attrs["write_returncode"] = None
        attrs["error_message"] = None
        attrs["completed_message"] = None
        attrs["acceptable_returncodes"] = acceptable_returncodes


        # Checkpoint
        attrs["dry"] = dry

        # Validation
        attrs["errors_ok"] = errors_ok
        attrs["validate_inputs"] = validate_inputs
        attrs["validate_outputs"] = validate_outputs

        self.executables[id] = attrs
        return self

    # Set attribute
    def set_attribute(self, id, attribute, value):
        assert id in self.executables, "`{}` not in `executables`".format(id)
        self.executables[id][attribute] = value
        return self

    # Set the order of operations
    def set_order_of_executables(self, ordering):
        for id, step in ordering.items():
            self.executables[id]
        return self

    # Compile everything and get ready for execution
    def compile(self):
        # if func_steps is None:
        #     func_steps = lambda step:step
        # Check duplicate steps
        steps = list()
        for id, attrs in self.executables.items():
            steps.append(attrs["step"])
        assert all(map(lambda x: x == 1, Counter(steps).values()))

        # Check missing steps
        assert set(steps) == set(range(min(steps), max(steps)+1)), "Please check for missing steps."

        # Check boolean attrs
        for id, attrs in self.executables.items():
            for attribute in ["errors_ok", "validate_inputs", "validate_outputs"]:
                assert isinstance(attrs[attribute], bool), "`{}` must be a boolean type".format(attribute)

        # Compiled steps
        self.compiled_steps_ = OrderedDict()
        print(format_header(". .. ... Compiling ... .. .", "="), file=self.f_verbose)

        for id, attrs in sorted(self.executables.items(), key=lambda x:x[1]["step"]):
            # Logfile name
            if attrs["log_prefix"] in {"infer", None}:
                attrs["log_prefix"] = "__".join([str(attrs["step"]).strip(), format_filename(id, replacement_character="-").strip()])
            assert check_filename(attrs["log_prefix"]), "Please format the filename `{}` so it only inlcudes alphanumeric characters, '.', '_', and '-'.".format(attrs["log_prefix"])
            # assert all(x)
            # Checkpoint
            if self.checkpoint_directory is not None:
                 attrs["checkpoint"] = os.path.join(self.checkpoint_directory,  attrs["log_prefix"] )
            # Log files
            if self.log_directory is not None:
                attrs["write_stdout"] = os.path.join(self.log_directory,  "{}.o".format(attrs["log_prefix"] ))
                attrs["write_stderr"] = os.path.join(self.log_directory, "{}.e".format(attrs["log_prefix"] ))
                attrs["write_returncode"] = os.path.join(self.log_directory,  "{}.returncode".format(attrs["log_prefix"] ))
                attrs["error_message"] = "Check log files to diagnose error:\ncat {}.*".format(os.path.join(self.log_directory,  attrs["log_prefix"] ))
                attrs["completed_message"] = "\nLog files:\n{}.*".format(os.path.join(self.log_directory,  attrs["log_prefix"] )) # Use glob here


           # Add step order
            self.compiled_steps_[attrs["step"]] = id
            # Update attributes
            self.executables[id].update(attrs)

            print("Step: {}, {} | log_prefix = {} | {}".format(attrs["step"], id, attrs["log_prefix"], attrs["description"]), file=self.f_verbose)



        # Compiled
        self.compiled = True
        return self

    # Execute pipeline
    def execute(self, steps=None, description="Executing pipeline", restart_from_checkpoint=None):
        start_time = time.time()
        assert self.compiled, "Please compile before continuing."
        if steps is None:
            steps = list(self.compiled_steps_.keys())
        if self.name is not None:
            if self.description is None:
                print(format_header(". .. ... {} ... .. .".format(self.name), "_"), file=self.f_verbose)
            else:
                print(format_header(". .. ... {} || {} ... .. .".format(self.name, self.description), "_"), file=self.f_verbose)
            print("", file=self.f_verbose)
        if restart_from_checkpoint is not None:
            restart_from_checkpoint = int(restart_from_checkpoint)
            assert restart_from_checkpoint in steps, "Cannot restart from checkpoint `{}` because it does not exist".format(restart_from_checkpoint)
            if self.checkpoint_directory is not None:
                if restart_from_checkpoint == "preprocessing":
                    restart_from_checkpoint = 1

                target_checkpoint = restart_from_checkpoint
                print("Restarting pipeline from checkpoint:", target_checkpoint, file=self.f_verbose)
                for file in scandir(self.checkpoint_directory):
                    if "_" in file.name:
                        query_checkpoint = int(file.name.split("_")[0].split(".")[0])
                        if query_checkpoint >= target_checkpoint:
                            print("...[-] {}".format(file.path), file=self.f_verbose)
                            os.remove(file.path)
                            # Intermediate files
                            for intermediate_filepath in self.executables[self.compiled_steps_[query_checkpoint]]["output_filepaths"]:
                                if os.path.exists(os.path.realpath(intermediate_filepath)):
                                    try:
                                        os.remove(intermediate_filepath)
                                        print("...[-] {}".format(intermediate_filepath), file=self.f_verbose)
                                    except OSError: # Changed from PermissionError 2020.01.15
                                        pass
                        else:
                            print("...[=] {}".format(file.path), file=self.f_verbose)
                print("", file=self.f_verbose)

        for step, id in pv(self.compiled_steps_.items(), description=description):
            if step in steps:
                attrs = self.executables[id]
                executable = attrs["executable"]
                # Headers
                print(format_header(". {} .".format(id), "="),  sep="", file=self.f_verbose)
                print("Input: ", attrs["input_filepaths"], "\n", "Output: ", attrs["output_filepaths"], "\n", sep="", file=self.f_verbose)
                print("Command:", file=self.f_verbose)
                print(attrs["executable"].cmd, "\n", file=self.f_verbose)

                # ===============
                # Execute command
                # ===============
                # Bypass io validation
                if self.bypass_io_validation_if_checkpoints_exist:
                    if os.path.exists(attrs["checkpoint"]):
                        # if_file_isnt_empty?
                        attrs["validate_inputs"] = False
                        attrs["validate_outputs"] = False
                        print("! Bypassing I/O validation: {}\n".format(attrs["checkpoint"]), file=self.f_verbose)

                # Check inputs
                if attrs["validate_inputs"]:
                    input_filepaths = attrs["input_filepaths"]
                    if bool(input_filepaths):
                        assert is_nonstring_iterable(input_filepaths), "`input_filepaths` must be a non-string iterable"
                        # paths_expanded = list()
                        # for path in input_filepaths:
                        #     if "*" in path:
                        #         paths_expanded += glob.glob(path)
                        #     else:
                        #         # path = os.path.realpath(path)
                        #         paths_expanded.append(path)
                        # self.executables[id]["input_filepaths"] = paths_expanded
                        validate_file_existence(input_filepaths, prologue="Validating the following input files:", f_verbose=self.f_verbose)
                        print("", file=self.f_verbose)


                # Execute
                executable.run(
                    prologue=id,
                    dry=attrs["dry"],
                    errors_ok=attrs["errors_ok"],
                    error_message=attrs["error_message"],
                    completed_message=attrs["completed_message"],
                    checkpoint=attrs["checkpoint"],
                    checkpoint_message_notexists=self.checkpoint_message_notexists,
                    checkpoint_message_exists=self.checkpoint_message_exists,
                    write_stdout=attrs["write_stdout"],
                    write_stderr=attrs["write_stderr"],
                    write_returncode=attrs["write_returncode"],
                    acceptable_returncodes=attrs["acceptable_returncodes"],
                    f_verbose=self.f_verbose,
                )
                # Check outputs
                if attrs["validate_outputs"]:
                    output_filepaths = attrs["output_filepaths"]
                    if bool(output_filepaths):
                        assert is_nonstring_iterable(output_filepaths),  "`output_filepaths` must be a non-string iterable"
                        validate_file_existence(output_filepaths, prologue="\nValidating the following output files:", f_verbose=self.f_verbose)
                        # print("", file=self.f_verbose)

                print("\nDuration: {}\n".format(format_duration(start_time)), file=self.f_verbose)

        self.duration_ = format_duration(start_time)
        print("\n", format_header("Total duration: {}".format(self.duration_), "."), sep="", file=self.f_verbose)
        return self

#     # Save object
#     def to_file(self, path, compression="infer", protocol=pickle.HIGHEST_PROTOCOL, *args):
#         # Cannot serialize file objects while open so we need make placeholders
#         f_cmds = self.f_cmds
#         f_verbose = self.f_verbose
#         self.f_verbose = None
#         self.f_cmds = None
# #         for id in self.executables.keys():
# #             self.executables[id]["executable"].f_verbose = None
# #             self.executables[id]["executable"].f_cmds = None

#         # Write object
#         write_object(self, path=path, compression=compression, protocol=protocol, *args)
#         # Set file objects
#         self.f_verbose = f_verbose
#         self.f_cmds = f_cmds
#         return self

    # Load object
    @classmethod
    def from_file(cls, path, compression="infer", f_verbose=None, f_cmds=None):
        cls = read_object(path=path, compression=compression)
        cls.f_verbose = f_verbose
        cls.f_cmds = f_cmds
        return cls

    def __getitem__(self, id):
        assert id in self.executables, "`{}` not in `executables`".format(id)
        return self.executables[id]


def main():
    directories = dict()
    directories["output"] = create_directory("pipeline_testing")
    directories["checkpoints"] = create_directory(os.path.join(directories["output"], "checkpoints"))
    directories["logs"] = create_directory(os.path.join(directories["output"], "logs"))


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
if __name__ == "__main__":
    main()
