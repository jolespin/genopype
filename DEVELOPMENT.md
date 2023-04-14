**Development:**

* 2023.4.13 - Added `executable` argument for subprocess.Popen calls. https://github.com/jolespin/veba/issues/23. Added `whitelist_empty_files` argument to `validate_file_existence` to allow certain files to be empty.  Added support for `restart_from_checkpoint = -1` to use penultimate step. Added filter(bool) commands before joining strings.
* 2022.09.23 - Removed "restart_from_checkpoint == 'preprocessing'" because that isn't very useful plus these need to be integers anyways.  I also added support for negative values to do the last step (-1), the penultimate step (-2), etc.
* 2021.08.18 - `cmd = " ".join(cmd)` -> `cmd = " ".join(list(map(str,cmd)))` on line 342

**Pending:**

* Show log files before finished running
* Don't make compile dependent on labels and make it dependent on steps so you can have multiple labels that are the same
* Make file size object that defaults to bytes but can have .as_kilobyte(), .as_gigabyte(), or .as_megabyte(). 
* Create a directories object
* Add stop_at_checkpoint
* How to stop pipeline if a certain criteria is met?

**Maybe:**

* Need to set up a method for having steps as 2.1, 2.2, 3.1, 3.2 but when they are executed, they are executed as 2.1, 3.1, and then 2.2, 3.2.

* ^^^ Make some kind of lambda rule?