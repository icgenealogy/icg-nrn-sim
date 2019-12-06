# icg-nrn-sim
Tool to run voltage clamp protocols in the [NEURON Simulator](http://www.neuron.yale.edu/neuron/) against one or several .mod files.

## Usage

Download the .zip file of this repository and save it in your local ```/tmp/``` path. Unzip the file right there and rename the ```icg-nrn-sim-master``` directory to ```icg-nrn-sim```. 

Next, create a modfiles directory: ```mkdir -p /tmp/modfiles/``` 

To run a single .mod file which is in ``/tmp/modfiles/modfile.mod`` execute the following:
```bash
/tmp/icg-nrn-sim/runsingle.pl /tmp/modfiles/modfile.mod /tmp/icg-nrn-sim/kvconfig.in result
```

To run several .mod files which are in ``/tmp/modfiles``,  execute the following:
```bash
/tmp/icg-nrn-sim/runbatch.pl /tmp/modfiles /tmp/icg-nrn-sim/kvconfig.in result
```

## Notes

- The script copies several files to the directory it was called from, so this should be executed from a clean working directory.
- Currently, the mod file can not be inside the working directory you are calling the script from. It is enough to place it in another directory, e.g. `/tmp/modfiles`, or in a subdirectory of the working directory.
