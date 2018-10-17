Run a single mod file to fetch the ICG protocols

Ref. https://github.com/icgenealogy/icg-nrn-sim/blob/master/pyICG/icg_batch_model_sim.py

Usage for running mod files inside a folder (will run multiple in series)

For help
./icg-nrn-sim/pyICG$ python icg_batch_model_sim.py -h

Run the ICG protocols

positional arguments:
  <mod_type>            Options are kav, nav, cav, ih and kca
  <mod_loc>             Path to the location of the .mod file (or directory of
                        *.mod files)
  <results_dir>         Path to the location of output files

optional arguments:
  -h, --help            show this help message and exit
  -v {0,1}, --variable_dt {0,1}
                        1 for variable time step, 0 for constant - default is
                        1 variable dt
  --plotting, -p        Plot output
  --normalize, -n       Normalize output with respect to the maximum

General usage

./icg-nrn-sim/pyICG$ python icg_batch_model_sim.py kv /home/chaitanya/icg-channels/icg-channels-K/123453_Kv1.mod/ temp

Would run the protocols under variable time step, and dumps the output to the temp folder from where python was prompted.

NOTE: The dumped output is interpolated to constant dt back again.


==========================================================================

Run protocols for entire folders in parallel.

This employes lazy parallel programming style - its not parallel at the NEURON side - we just all neuron multiple times is all.

Ref. https://github.com/icgenealogy/icg-nrn-sim/blob/master/pyICG/run_icg_parallel.py


Usage for running in parallel on multiple cores


./icg-nrn-sim/pyICG$ python run_icg_parallel.py /home/chaitanya/icg-channels/ K 4


implying it will go and implement where ever icg-channels/ as mentioned is - looks for icg-channels/icg-channels-K where K is the second input (others are Na KCa Ca IH) and the last input being number of cores to run it in parallel.


By default the results directory is the folder directory inside which an ICG_ORIG is created and the output is saved there.

NOTE: May have to comment on the switch_python2() line in this file to suit your needs.



