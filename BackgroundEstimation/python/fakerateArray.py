from fakerate import FakeRate

#
# Class from reading out from different fake rates of single flavor
# Made with tau FR from DY and TT in mind
#
class SingleFlavorFakeRateCollection:
    def __init__(self, paths, obj_names, call_names, method = 'fractional', **kwargs):
        if len(paths) != len(obj_names) or len(paths) != len(call_names):
            raise RuntimeError('Length of path, obj_names and call_names in SingleFlavorFakeRateCollection should be the same')

        self.fakerates = {}
        for cn, on, path in zip(call_names, obj_names, paths):
            if '/' in on:
                subdirs, on_end = on.split('/')
                subdirs = subdirs.split('/')
            else:
                subdirs = None
                on_end = on
            self.fakerates[cn] = FakeRate(on_end, lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), path, None, subdirs = subdirs)

        self.method = method
        self.frac_weights = kwargs.get('frac_weights')
        self.frac_names = kwargs.get('frac_names')
        self.ossf_map = kwargs.get('ossf_map')

    def getFractionalFakeFactor(self, chain, index, manual_var_entry = None):
        fake_factor = 0.
        for n in self.frac_names:
            fake_factor += self.frac_weights[n]*self.fakerates[n].returnFakeFactor(chain, index, manual_var_entry)
        return fake_factor

    def getOSSFFakeFactor(self, chain, index, manual_var_entry = None):
        from HNL.EventSelection.eventSelectionTools import containsOSSF
        contains_ossf = containsOSSF(chain)
        return self.fakerates[self.ossf_map[contains_ossf]].returnFakeFactor(chain, index, manual_var_entry)

    
    def returnFakeFactor(self, chain, l_index = None, manual_var_entry = None):
        if self.method == 'fractional':
            if self.frac_weights is None or self.frac_names is None:
                raise RuntimeError('Invalid input: weights or names is None')
            return self.getFractionalFakeFactor(chain, l_index, manual_var_entry)
        elif self.method == 'OSSFsplitMix':
            return self.getOSSFFakeFactor(chain, l_index, manual_var_entry)
        else:
            raise RuntimeError('No other methods supported yet')

class FakeRateCollection:

    def __init__(self, chain, fakerates_flavordict):
        self.chain = chain
        self.fakerates = fakerates_flavordict

    def returnFakeFactor(self, l_index, manual_var_entry = None):
        if self.fakerates[self.chain.l_flavor[l_index]] is not None:
            return self.fakerates[self.chain.l_flavor[l_index]].returnFakeFactor(self.chain, l_index = l_index, manual_var_entry =  manual_var_entry)
        else:
            return 'skip'

    def getFakeWeight(self):
        weight = -1.
        nleptons = 0
        for i in xrange(len(self.chain.l_indices)):
            if not self.chain.l_istight[i]:
                if self.chain.selection in ['Luka', 'default'] and self.chain.l_flavor[i] in [0, 1]:
                    man_var = [min(44.9, self.chain.l_pt[i]), abs(self.chain.l_eta[i])]
                else:
                    man_var = None
             
                ff = self.returnFakeFactor(l_index = i, manual_var_entry = man_var)
                if ff == 'skip': continue

                weight *= -1*ff
                nleptons += 1

        if nleptons == 0:
            return 1.
        else:
            return weight

class ConditionalFakeRate:
    def __init__(self, name, var, var_tex, path, bins=None):
        self.bin_collection = {'total': (lambda c : True)}
        self.name = name
        self.var = var
        self.var_tex = var_tex
        self.path = path
        self.bins = bins
        self.fakerates = {}
        #If bins is None, FakeRate loads in fake rate
        self.fakerates['total'] = FakeRate(self.name, self.var, self.var_tex, self.path, self.bins, subdirs = ['total'])

    def addBin(self, bin_name, condition):
        self.bin_collection[bin_name] = condition
        self.fakerates[bin_name] = FakeRate(self.name, self.var, self.var_tex, self.path, self.bins, subdirs = [bin_name])

    def fillFakeRates(self, chain, weight, passed, index = None):
        for b in self.bin_collection:
            if self.bin_collection[b](chain): self.fakerates[b].fill(chain, weight, passed, index)

    def writeFakeRates(self, append = False, is_test=None):
        for i, b in enumerate(self.fakerates):
            if i == 0 and not append:
                self.fakerates[b].write(is_test=is_test)
            else:
                self.fakerates[b].write(append = True, is_test=is_test)

    def getFakeRate(self, bin_name):
        return self.fakerates[bin_name]

    def returnFakeFactor(self, chain, l_index = None, manual_var_entry = None):
        condition_of_choice = None
        for condition in self.bin_collection.keys():
            if condition == 'total': continue
            if not self.bin_collection[condition](chain): continue
            if condition_of_choice is not None:
                raise RuntimeError("conditions in conditional fake rate are not exclusive. You will need to design a special function for them to be read out by the ConditionalFakeRate returnFakeFactor function.")           
            condition_of_choice = condition

        return self.fakerates[condition].returnFakeFactor(chain, l_index, manual_var_entry)

def createFakeRatesWithJetBins(name, var, var_tex, path, bins = None):
    fr_array = ConditionalFakeRate(name, var, var_tex, path, bins)
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
