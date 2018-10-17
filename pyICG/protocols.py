'''
ICG PROTOCOLS - Protocol Classes
Written by William Podlaski and Christopher Currin. Last modified 19.08.2016

NOTE: the classes take in the neuron object 'h' as an argument. this is not necessary, will be changed.

Contains the following items:
 	1. function rename_suffix(file_path, suffix): redefines the suffix in the mod file found at <file_path> to new name in <suffix>
	2. parent class Protocol: defines the general methods for all ICG protocols
	3. child classes of Protocol: Activation, Inactivation, Deactivation, Ramp & ActionPotential
	4. protocol_dict: dictionary variable that returns the class. see other scripts for use
'''

import numpy as np
import os
from scipy import interpolate
import pickle
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt


def create_dir(path):
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise
    return path


def plotting_done():
    plt.show(block=True)


# activate interactive plotting
plt.ion()


class Protocol(object):
    def __init__(self, h, name='protocol', tstop=0, dt=0.25, nruns=1, var_dt=True):
        super(Protocol, self).__init__()
        self.h = h
        self.name = name
        self.tstop = self.h.tstop = tstop
        self.dt = dt
        self.h.dt = dt
        self.nruns = nruns
        self.totalsteps = int(round(self.tstop / self.dt)) + 1
        self.cvode = h.CVode()
        self.var_dt = var_dt
        if self.var_dt:
            print('Running with variable time step')
            self.cvode.active(1)
            self.cvode.atol(0.0001)
            self.cvode.re_init()
        else:
            self.cvode.active(0)
        
            
    def clampCell(self, cell, rs=0.001):
        self.testing_cell = cell
        self.vc = self.h.SEClamp(cell.soma(0.5))
        self.vc.rs = rs

    def getStepWaveform(self, t_list, v_list):
        # create voltage waveform
        v_tmp = np.array([v_list[0]])  # add extra data point in beginning
        for (t, v) in zip(t_list, v_list):
            v_tmp = np.append(v_tmp, v * np.ones(int(round(t / self.dt))) + 1)
            # double check that it has the right size
        if (v_tmp.size != self.totalsteps):
            raise Exception('Waveform size does not match with protocol tstop.')
        return v_tmp

    def record(self, cell):
        self.v_vec = self.h.Vector()  # Membrane potential vector
        self.i_vec = self.h.Vector()
        self.t_vec = self.h.Vector()  # Time stamp vector
        self.v_vec.record(cell.soma(0.5)._ref_v)
        if cell.ion_type in ['kv', 'nav', 'cav', 'kca']:
            curr_name = {'kv' : 'ik', 'nav':'ina', 'cav':'ica', 'kca':'ik'}[cell.ion_type]
        elif cell.ion_type == 'ih':
            curr_name = 'i_suff_0'
        exec('self.i_vec.record(cell.soma(0.5)._ref_'+curr_name+')')
        self.t_vec.record(self.h._ref_t)

    def initMat(self):
        print('nruns =',self.nruns,', tsteps =',self.totalsteps)
        #self.vMat = {} #np.zeros((self.nruns, self.totalsteps))
        self.iMat = {} #np.zeros((self.nruns, self.totalsteps))
        self.tMat = {} #np.zeros((self.nruns, self.totalsteps))

    def updateMat(self, idx, p=None):
        t_orig = np.array(self.t_vec.to_python())
        #v_orig = np.array(self.v_vec.to_python())
        i_orig = np.array(self.i_vec.to_python())
        #self.vMat[idx] = v_orig
        tt = np.arange(0., self.tstop, self.dt)
        self.iMat[idx] = np.interp(tt, t_orig, i_orig)
        self.tMat[idx] = tt #_orig

    def saveMat(self, fname, path):
        create_dir(path)
        with open(os.path.join(path, fname + '_' + self.name + '.t'), 'w') as t_mat_file:
            pickle.dump(self.tMat, t_mat_file)
        #with open(os.path.join(path, fname + '_' + self.name + '.v'), 'w') as v_mat_file:
        #    pickle.dump(self.vMat, v_mat_file)
        with open(os.path.join(path, fname + '_' + self.name + '.i'), 'w') as i_mat_file:
            pickle.dump(self.iMat, i_mat_file)

    def plot(self):
        plt.figure()
        plt.subplot(2, 1, 1)
        plt.hold(True)
        for i in range(0, self.nruns):
            plt.plot(self.tMat[i], self.vMat[i], color='black')
        plt.xlabel('time (ms)')
        plt.ylabel('mV')
        plt.subplot(2, 1, 2)
        plt.hold(True)
        for i in range(0, self.nruns):
            plt.plot(self.tMat[i], self.iMat[i], color='blue')
        plt.xlabel('time (ms)')
        plt.ylabel('nA')
        plt.show()

    def playWaveform(self, step):
        pass

    def run(self, cell):
        pass


class Activation(Protocol):
    def __init__(self, h, dt=0.025, var_dt=True):
        self.nruns = 16
        self.vsteps = np.linspace(-80.0, 70.0, self.nruns)
        super(Activation, self).__init__(h, name='act', tstop=700, dt=dt, nruns=self.nruns, var_dt=var_dt)

    def playWaveform(self, step):
        self.vWave = self.h.Vector(self.getStepWaveform([100.0, 500.0, 100.0], [-80.0, step, -80.0]))
        self.vc.dur1 = self.tstop
        self.vWave.play(self.vc._ref_amp1, self.dt)

    def run(self, cell):
        self.initMat()
        self.cvode.re_init()
        for i, v in enumerate(self.vsteps):
            self.playWaveform(v)
            self.record(cell)
            self.h.run()
            self.updateMat(i, p=self.__class__.__name__)


class Inactivation(Protocol):
    def __init__(self, h, dt=0.025, var_dt=True):
        self.nruns = 12
        self.vsteps = np.linspace(-100.0, 40.0, self.nruns)
        super(Inactivation, self).__init__(h, name='inact', tstop=1750, dt=dt, nruns=self.nruns, var_dt=var_dt)

    def playWaveform(self, step):
        self.vWave = self.h.Vector(self.getStepWaveform([100.0, 1500.0, 50.0, 100.0], [-80.0, step, 30.0, -80.0]))
        self.vc.dur1 = self.tstop
        self.vWave.play(self.vc._ref_amp1, self.dt)

    def run(self, cell):
        self.cvode.re_init()
        self.initMat()
        for i, v in enumerate(self.vsteps):
            self.playWaveform(v)
            self.record(cell)
            self.h.run()
            self.updateMat(i, p=self.__class__.__name__)


class Deactivation(Protocol):
    def __init__(self, h, dt=0.025, var_dt=True):
        self.nruns = 15
        self.vsteps = np.linspace(-100.0, 40.0, self.nruns)
        super(Deactivation, self).__init__(h, name='deact', tstop=700, dt=dt, nruns=self.nruns, var_dt=var_dt)

    def playWaveform(self, step):
        self.vWave = self.h.Vector(self.getStepWaveform([100.0, 300.0, 200.0, 100.0], [-80.0, 70, step, -80.0]))
        self.vc.dur1 = self.tstop
        self.vWave.play(self.vc._ref_amp1, self.dt)

    def run(self, cell):
        self.cvode.re_init()
        self.initMat()
        for i, v in enumerate(self.vsteps):
            self.playWaveform(v)
            self.record(cell)
            self.h.run()
            self.updateMat(i, p=self.__class__.__name__)


class Ramp(Protocol):
    def __init__(self, h, dt=0.025, var_dt=True):
        self.nruns = 1
        super(Ramp, self).__init__(h, name='ramp', tstop=2900, dt=dt, nruns=self.nruns, var_dt=var_dt)

    def getRampWaveform(self, t_list, v_hold, v_max):
        v_tmp = np.array([v_hold])  # add extra data point in beginning
        for i, t in enumerate(t_list):
            if (i % 2 == 0):  # flat line
                v_tmp = np.append(v_tmp, v_hold * np.ones(int(round(t / self.h.dt))))
            else:  # ramping
                v_tmp = np.append(v_tmp, np.linspace(v_hold, v_max, (t / 2 / self.h.dt)))
                v_tmp = np.append(v_tmp, np.linspace(v_max, v_hold, (t / 2 / self.h.dt)))
        # double check that it has the right size
        if (v_tmp.size != self.totalsteps):
            raise Exception('Waveform size does not match with protocol tstop.')
        return v_tmp

    def playWaveform(self, step):
        self.vWave = self.h.Vector(self.getRampWaveform([100.0, 800.0, 400.0, 400.0, 400.0, 200.0,
                                                         400.0, 100.0, 100.0], -80.0, 70.0))
        self.vc.dur1 = self.tstop
        self.vWave.play(self.vc._ref_amp1, self.dt)

    def run(self, cell):
        self.cvode.re_init()
        self.initMat()
        self.playWaveform(None)
        self.record(cell)
        self.h.run()
        self.updateMat(0)


class ActionPotential(Protocol):
    def __init__(self, h, dt=0.025, var_dt=True):
        self.nruns = 1
        super(ActionPotential, self).__init__(h, name='ap', tstop=1800, dt=dt, nruns=self.nruns, var_dt=var_dt)

    def getFileWaveform(self, fname):
        data = np.loadtxt(fname, dtype=float)
        f = interpolate.interp1d(data[:, 0], data[:, 1])
        t = np.linspace(0, self.tstop, self.totalsteps)
        v_tmp = f(t)
        # double check that it has the right size
        if (v_tmp.size != self.totalsteps):
            raise Exception('Waveform size does not match with protocol tstop.')
        return v_tmp

    def playWaveform(self, step):
        self.vWave = self.h.Vector(self.getFileWaveform(os.path.join(os.path.dirname(os.path.abspath(__file__)),'APwaveform_python.dat')))
        self.vc.dur1 = self.tstop
        self.vWave.play(self.vc._ref_amp1, self.dt)

    def run(self, cell):
        self.cvode.re_init()
        self.initMat()
        self.playWaveform(None)
        self.record(cell)
        self.h.run()
        self.updateMat(0)


protocol_dict = {'Activation': Activation, 'Inactivation': Inactivation, 'Deactivation': Deactivation,
                 'Ramp'      : Ramp, 'ActionPotential': ActionPotential}
