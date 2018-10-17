import os
import sys
import subprocess
from joblib import Parallel, delayed  

RUN_PARALLEL = True

def switch_python2():
    text = '''export PATH="/home/chaitanya/anaconda2/bin:$PATH" &
    export PATH="/home/chaitanya/neuron/nrn/py2/x86_64/bin:$PATH"  &
    export PYTHONPATH=$PYTHONPATH:$HOME/neuron/nrn/py2/lib/python2.7/site-packages'''
    os.system(text)
    return

def call_icg(mod_type, folder_path, results_prefix):
    switch_python2()   # Comment this if you have python and neuron in your default paths already.
    results_path = os.path.join(folder_path, results_prefix)
    path = 'python icg_batch_model_sim.py '
    path += mod_type + ' '
    path += folder_path + ' '
    path += results_path + ' '
    os.system(path)

if __name__ == '__main__':
    icg_channel_path = sys.argv[-3]   # Absolute Location of the icg-channels/ folder
    channel_type = sys.argv[-2]   # subfolder inside this channel that you wish to run ICG
    NUM_CORES = int(sys.argv[-1])  # Number of cores to use to parallelize 

    mod_type = {'KCa':'kca',
                'Na':'nav',
                'K':'kv',
                'IH':'ih',
                'Ca':'cav'}[channel_type]
    results_prefix = 'ICG_ORIG'
    for sub_channel in ['icg-channels-'+channel_type]:
        abs_path = os.path.abspath(icg_channel_path)
        all_channels = os.listdir(os.path.join(abs_path, sub_channel))
        rel_channels = []
        for channel_folder in all_channels:
            if channel_folder in ['.git', 'LICENSE', 'Readme.md']:
                pass
            else:
                fpath = os.path.join(abs_path, sub_channel, channel_folder)
                if RUN_PARALLEL:
                    rel_channels.append(fpath)
                else:
                    spath = 'icg_batch_model_sim.py'
                    rpath = os.path.join(spath, results_prefix)
                    path = ['python', spath, mod_type, fpath, rpath]
                    switch_python2()
                    subprocess.call(path)
    if RUN_PARALLEL:
        results = Parallel(n_jobs=NUM_CORES)(delayed(call_icg)(mod_type, ii, results_prefix)
                                             for ii in rel_channels)
