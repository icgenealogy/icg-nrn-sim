'''
ICG PROTOCOLS - batch run through all mod files of a given directory
Written by William Podlaski and Christopher Currin, modified from original code (in Perl/NEURON) written by Rajnish Ranjan and William Podlaski.
Last modified 24.08.2016
'''

# NOTE: Verified and changed to run for all channel types.

from __future__ import print_function
import sys
import os
import glob
import argparse
import time
from os import listdir, remove, chdir, makedirs, close, getcwd
from os.path import isfile, isdir, join, dirname, splitext, abspath
import errno
import platform
from subprocess import call, Popen, PIPE
from shutil import copyfile, rmtree, move
from tempfile import mkstemp
from file_manip import cd, create_dir


def rename_suffix(file_read, file_write, suffix):
    """
    Redefine the suffix inside of mod file
     Each suffix must be unique
    :param file_read: the original mod filename
    :param file_write: the destination file name
    :param suffix: the new suffix name
    """
    # Create temp file
    fh, abs_path = mkstemp()
    with open(abs_path, 'w') as new_file:
        with open(file_read) as old_file:
            for line in old_file:
                if "SUFFIX" in line:
                    new_file.write('\tSUFFIX ' + suffix + '\n')
                elif "POINT_PROCESS" in line:
                    index = line.find("POINT_PROCESS")
                    index_name = line.find(" ", index + 1)
                    index_name_end = line.find(" ", index_name + 1)
                    # new_file.write('\tPOINT_PROCESS ' + suffix + '\n')
                    new_file.write(line[:index_name] + ' ' + suffix + line[index_name_end:])
                else:
                    new_file.write(line)
    close(fh)
    # Move to new file
    move(abs_path, file_write)


def remove_file(file):
    try:
        remove(file)
        print("file {} removed".format(file))
    except OSError as e:
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

def nrnivmodl(tries_left, mod_files, path=None, last_line_index=-1):
    output = None
    if tries_left == 0 or len(mod_files) == 0:
        return None
    if path is None:
        if (platform.system() == 'Linux' or platform.system() == 'Darwin'):
            path = ['nrnivmodl']
        elif platform.system() == 'Windows':
            path = ["c:\\nrn/mingw/bin/sh", "c:\\nrn/lib/mknrndll.sh", "/c\\nrn"]
            last_line_index = -2  # "Press Return key to exit" on Windows is last line
        else:
            print("unknown system")
            exit(1)
    try:
        process = Popen(path, stdin=PIPE, stdout=PIPE)
        output, err = process.communicate()
    except OSError as er:
        print("'{}' failed".format(path))
        alt_path = "/usr/local/nrn/bin/nrnivmodl"
        if path == alt_path:
            exit(1)
        else:
            print("trying {}".format(alt_path))
            return nrnivmodl(tries_left, mod_files, path=alt_path, last_line_index=last_line_index)
    if output is not None:
        lines = output.splitlines()
        last_line = lines[last_line_index]
        print(last_line)
        if last_line.find("failed") >= 0 or last_line.find("Error") >= 0 or last_line.find("error") >= 0:
            if last_line_index < -1:
                # Windows peculiarities...
                last_line = lines[last_line_index - 2]
                err_file_name = last_line[last_line.find('tmpmod'):]
            else:
                err_file_name = last_line[last_line.find("'") + 1:last_line.find(".")]
            err_file_tmp_number = err_file_name[len("tmpmod"):]
            remove_file(err_file_name + ".mod")
            mod_files[int(err_file_tmp_number)] = None
            return nrnivmodl(tries_left - 1, mod_files, path, last_line_index)
    return mod_files


def parse_args():
    parser = argparse.ArgumentParser(description="Run the ICG protocols")
    parser.add_argument('mod_type', type=str, metavar='<mod_type>', 
                        help='Options are kav, nav, cav, ih and kca')
    parser.add_argument('mod_loc', type=str, metavar='<mod_loc>',
                        help='Path to the location of the .mod file (or directory of *.mod files)')
    parser.add_argument('results_dir', type=str, metavar='<results_dir>',
                        help='Path to the location of output files')
    parser.add_argument("-v", "--variable_dt", type=int, choices=[0, 1], 
                        help="1 for variable time step, 0 for constant - default is 1 variable dt")
    parser.add_argument('--plotting', '-p',
                        action='store_true',
                        help="Plot output")
    parser.add_argument('--normalize', '-n',
                        action='store_true',
                        default=False,
                        help="Normalize output with respect to the maximum")
    return parser.parse_args()

def main():
    args = parse_args()
    # TODO: standardise Erev
    normalize = args.normalize        # normalize all traces between 0 and 1
    plotting = args.plotting        # plot traces
    mod_name = args.mod_type
    input_directory = args.mod_loc
    result_directory = args.results_dir
    var_dt = args.variable_dt
    if var_dt == 0:
        var_dt = False
    elif var_dt == 1:
        var_dt = True
    else:
        var_dt = True
    
    try:
        current_type = {'kv': 'outward', 'nav': 'inward',
                        'cav': 'outward', 'kca': 'outward',
                        'ih': 'outward'}[mod_name]
    except KeyError:
        print('Incorrect argument mod_type')
        
    # 2. PREPARE DIR - clean up, then add all mod files and compile
    if os.path.isdir(input_directory):
        input_path = input_directory
        mod_files = glob.glob(os.path.join(input_path, '*.mod'))  # should use glob instead
    elif os.path.isfile(input_directory):
        input_path = os.path.dirname(os.path.abspath(input_directory))
        mod_files = [input_directory]
    print('Processing %d mod files,' %(len(mod_files)))        
    orig_directory = getcwd()
    with cd(input_path):
        unique_id = str(int(time.time()*1000))
        folder_temp = "compiled_files_" + unique_id
        compiled_dir = create_dir(folder_temp)
        print(mod_files)
        custom_files = {}
        # python hack - copy all mod files to the directory and compile
        # NOTE: each file is given a new name (tmpmodX.mod) and suffix (suff_X), where X is the index in list mod_files
        for (m_idx, mpath) in enumerate(mod_files):
            m = os.path.basename(mpath)
            print("{} is tmpmod{}".format(m, m_idx))
            dest_file = 'tmpmod' + str(m_idx) + '.mod'
            new_suffix = 'suff_' + str(m_idx)
            rename_suffix(m, join(compiled_dir, dest_file), new_suffix)
            if isfile(abspath(join(orig_directory,'../','custom_code','customcode_'+splitext(m)[0]+'.hoc'))):
                custom_files[m_idx] = abspath(join(orig_directory,'../','custom_code','customcode_'+splitext(m)[0]+'.hoc'))
        with cd(compiled_dir):
            # compile the mod files
            mod_files = nrnivmodl(len(mod_files), mod_files)
            # remove mode files which caused an issue
            mod_files = [m for m in mod_files]
            # this must be done AFTER compiling of mechanisms is complete
            # import within the same directory as compiled mod files to have them loaded automatically into NEURON
            from neuron import h, gui
        print(custom_files)

        # SET UP NEURON ENVIRONMENT
        h.celsius = 37.0
        h.finitialize(-80.0)
        # because nrnutils has neuron import statement, these should be placed after this file's neuron import
        from vClampCell import ICGCell
        from protocols import protocol_dict, plotting_done, \
            Activation, Inactivation, Deactivation, Ramp, ActionPotential

        # 3. LOOP THROUGH AND RUN ALL MOD FILES
        for (m_idx, m) in enumerate(mod_files):
            print('*'*50+'\n'+'Running protocols for modfile: ', m)
            if m is None:
                continue
            fname = m.replace('.mod', '')
            new_suffix = 'suff_' + str(m_idx)
            print('suffix =', new_suffix)
            # create the cell and insert the ion channel conductance
            cell = ICGCell(mod_name, current_type)

            # some files require custom_code: if extra hoc file exists, then run it
            with cd(orig_directory):
                open('../customcode.hoc', 'w').close()  # empty the file
                if m_idx in custom_files.keys():
                    print('This mod requires additional files. Loading...')
                    copyfile(custom_files[m_idx],'../customcode.hoc')
                    h('load("../customcode.hoc")')

            cell.insert_distributed_channel(new_suffix)

            # loop through protocols
            protocol_list = protocol_dict.keys()
            for p in protocol_list:
                print('Running protocol: ', p)
                # create protocol and run
                protocol = protocol_dict[p](h, dt=0.025, var_dt=var_dt)  # should generate an instance of the correct protocol
                protocol.clampCell(cell)  # create SEClamp attached to soma
                protocol.run(cell)  # run the protocol
                with cd(orig_directory):
                    ff = fname.rsplit('/', 1)[-1]
                    protocol.saveMat(ff, result_directory)  # save voltage, current and time

                # optional plotting
                if plotting:  # plot each run from the matrices
                    protocol.plot()
        rmtree(folder_temp, ignore_errors=True)
    plotting_done()

if __name__ == '__main__':
    main()
