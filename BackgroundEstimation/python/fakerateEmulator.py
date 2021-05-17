#
# Class for turning tu thong's fake rates into something that can be used with my own class
#
import numpy as np
tmp_bins = (np.array([20., 25., 35., 50., 70., 100.]), np.arange(0., 3.0, 0.5))

from HNL.BackgroundEstimation.fakerate import FakeRate
from HNL.Tools.helpers import getObjFromFile
from HNL.Tools.histogram import Histogram
class FakeRateEmulator(FakeRate):

    def __init__(self, name, var, var_tex, path):
        super(FakeRateEmulator, self).__init__(name, var, var_tex, path, bins=tmp_bins)
        self.efficiency_num = None
        self.efficiency_denom = None
        self.efficiency = getObjFromFile(self.path, self.name)
        efficiency_hist_obj = Histogram(self.efficiency)
        self.isTH2 = efficiency_hist_obj.isTH2

    def fill(self, chain, weight, passed, index = None):
        raise RuntimeError('Function "fill" disabled for Emulator')
 
    def getNumerator(self):
        raise RuntimeError('Function "getNumerator" disabled for Emulator')

    def getDenominator(self):
        raise RuntimeError('Function "getDenominator" disabled for Emulator')

    def clone(self, out_name='clone'):
        raise RuntimeError('Function "clone" disabled for Emulator')

    def add(self, other_efficiency):
        raise RuntimeError('Function "add" disabled for Emulator')
    
    def write(self, append = False, name = None, subdirs = None):
        raise RuntimeError('Function "write" disabled for Emulator')