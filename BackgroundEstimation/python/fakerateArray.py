from fakerate import FakeRate
class FakerateArray:

    def __init__(self, name, var, var_tex, path, bins=None):
        self.bin_collection = {'total': (lambda c : True)}
        self.name = name
        self.var = var
        self.var_tex = var_tex
        self.path = path
        self.bins = bins
        self.fakerates = {}
        self.fakerates['total'] = FakeRate(self.name, self.var, self.var_tex, self.path, self.bins, subdirs = ['total'])

    def addBin(self, bin_name, condition):
        self.bin_collection[bin_name] = condition
        self.fakerates[bin_name] = FakeRate(self.name, self.var, self.var_tex, self.path, self.bins, subdirs = [bin_name])

    def fillFakeRates(self, chain, weight, passed, index = None):
        for b in self.bin_collection:
            if self.bin_collection[b](chain): self.fakerates[b].fill(chain, weight, passed, index)

    def writeFakeRates(self, append = False, name=None, is_test=False):
        for i, b in enumerate(self.fakerates):
            if i == 0 and not append:
                self.fakerates[b].write(is_test=is_test)
            else:
                self.fakerates[b].write(append = True, is_test=is_test)

    def getFakeRate(self, bin_name):
        return self.fakerates[bin_name]


def createFakeRatesWithJetBins(name, var, var_tex, path, bins = None):
    fr_array = FakerateArray(name, var, var_tex, path, bins)
    fr_array.addBin('0jets', lambda c: c.njets == 0)
    fr_array.addBin('njets', lambda c: c.njets > 0)
    return fr_array

import os
def loadFakeRatesWithJetBins(name, var, var_tex, path_base, flavor, indata=False):
    fr_arrays = {}
    if flavor == 'tau':
        if indata:
            fr_arrays['TauFakesDY'] = createFakeRatesWithJetBins(name, var, var_tex, os.path.join(path_base, 'TauFakesDY', 'events.root'), bins = None)
            # fr_arrays['TauFakesTT'] = createFakeRatesWithJetBins(name, var, var_tex, os.path.join(path_base, 'TauFakesTT', 'events.root'), bins = None)
        else:
            fr_arrays['TauFakesDY'] = createFakeRatesWithJetBins(name, var, var_tex, os.path.join(path_base, 'TauFakesDY', 'DY', 'events.root'), bins = None)
            fr_arrays['TauFakesTT'] = createFakeRatesWithJetBins(name, var, var_tex, os.path.join(path_base, 'TauFakesTT', 'TT', 'events.root'), bins = None)
    elif flavor == 'e':
        fr_arrays['LightLeptonFakes'] = createFakeRatesWithJetBins(name, var, var_tex, os.path.join(path_base, 'LightLeptonFakes', 'QCDem', 'events.root'), bins = None)
    else:
        fr_arrays['LightLeptonFakes'] = createFakeRatesWithJetBins(name, var, var_tex, os.path.join(path_base, 'LightLeptonFakes', 'QCDmu', 'events.root'), bins = None)
    return fr_arrays

def readFakeRatesWithJetBins(fr_arrays, chain, flavor, region, split_in_njets):
    if flavor == 2:
        if region == 'TauFakesDY' or region == 'TauFakesTT':
            if split_in_njets:
                if chain.njets == 0:    return fr_arrays[region].getFakeRate('0jets').returnFakeWeight(chain, flavor)
                else:                   return fr_arrays[region].getFakeRate('njets').returnFakeWeight(chain, flavor)
            else:
                return fr_arrays[region].getFakeRate('total').returnFakeWeight(chain, flavor)
        elif region == 'Mix':
            if split_in_njets:
                if chain.njets == 0:    return fr_arrays['TauFakesDY'].getFakeRate('0jets').returnFakeWeight(chain, flavor)
                else:                   return fr_arrays['TauFakesTT'].getFakeRate('njets').returnFakeWeight(chain, flavor)
            else:
                raise RuntimeError("Invalid input for 'split_in_njets'")    
        else:
            raise RuntimeError("Invalid input for 'region'")
    else:
        if split_in_njets:
            if chain.njets == 0:    return fr_arrays['LightLeptonFakes'].getFakeRate('0jets').returnFakeWeight(chain, flavor)
            else:                   return fr_arrays['LightLeptonFakes'].getFakeRate('njets').returnFakeWeight(chain, flavor)
        else:
            return fr_arrays['LightLeptonFakes'].getFakeRate('total').returnFakeWeight(chain, flavor)

from HNL.EventSelection.eventSelectionTools import nBjets
def readFakeRatesWithBJetBins(fr_arrays, chain, flavor, region):
    if flavor == 2:
        if region == 'TauFakesDY' or region == 'TauFakesTT':
            raise RuntimeError("This region is not supported yet in readFakeRatesWithBJetBins")
        elif region == 'Mix':
            nbjets = nBjets(chain, 'loose', 'HNLLowPt')
            if nbjets == 0:    return fr_arrays['TauFakesDY'].getFakeRate('total').returnFakeWeight(chain, flavor)
            else:              
                return fr_arrays['TauFakesTT'].getFakeRate('total').returnFakeWeight(chain, flavor) 
        else:
            raise RuntimeError("Invalid input for 'region'")
    else:
        raise RuntimeError("This flavor is not supported yet in readFakeRatesWithBJetBins")




