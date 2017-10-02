'''
ICG PROTOCOLS - single compartment cell
Written by William Podlaski and Christopher Currin. Last modified 19.08.2016
'''

import numpy as np
from nrnutils import Mechanism, Section, alias


class ICGCell(object):
    def __init__(self, ion_type, current_type, L=20, diam=20, Ra=150, g_pas=0.00003334):
        self.ion_type = ion_type
        self.current_type = current_type
        leak = Mechanism('pas', e=-65, g=g_pas)
        self.soma = Section(L, diam, Ra=Ra, mechanisms=[leak])

    def insert_mechanism(self, mech):
        """
        Insert density mechanism into cell
        :param mech:
        """
        if isinstance(mech, basestring):
            mech = Mechanism(mech)
        mech.insert_into(self.soma)
        self.setRevVar()
        self.setConc()
    insert_distributed_channel = insert_mechanism

    def insert_synapse(self, suffix, **parameters):
        """

        :param suffix:
        :param parameters: passed as e=-70, g=0.0001
        :return:
        """
        self.soma.add_synapses(suffix.lower(), suffix, **parameters)
        return getattr(self.soma, suffix.lower())
    insert_single_channel = insert_synapse

    def setRevVar(self):
        self.eRev = {
            'kv': 'ek', 'nav': 'ena', 'cav': 'eca', 'kca': 'ek', 'ih': 'eh'
        }[self.ion_type]
        tmp_eRev = {
            'kv': -86.7, 'nav': 50.0, 'cav': 135.0, 'kca': -86.7, 'ih': -45.0
        }[self.ion_type]
        setattr(self.soma, self.eRev, tmp_eRev)

    def setConc(self):
        self.iConc = {
            'kv': 'ki', 'nav': 'nai', 'cav': 'cai', 'kca': 'ki', 'ih': None
        }[self.ion_type]
        self.oConc = {
            'kv': 'ko', 'nav': 'nao', 'cav': 'cao', 'kca': 'ko', 'ih': None
        }[self.ion_type]
        tmp_iConc = {
            'kv': 85.0, 'nav': 21.0, 'cav': 8.1929e-5, 'kca': 85.0, 'ih': None
        }[self.ion_type]
        tmp_oConc = {
            'kv': 3.3152396, 'nav': 136.3753955, 'cav': 2.0, 'kca': 3.3152396, 'ih': None
        }[self.ion_type]
        setattr(self.soma, self.iConc, tmp_iConc)
        setattr(self.soma, self.iConc, tmp_oConc)
