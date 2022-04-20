import ROOT
from HNL.TMVA.mvaVariables import getVariableNames, getVariableValue
from array import array
import numpy as np
import os

ctypes = {
    'F' : 'f',
    'I' : 'i'
}

#prelegacy choices
# MVA_of_choice = {
#     'high_e' : 'kBDT-boostType=Grad-ntrees=200-maxdepth=3-shrinkage=0.1',
#     'high_mu' : 'kBDT-boostType=Grad-ntrees=100-maxdepth=4-shrinkage=0.1',
#     'high_tau' : 'kBDT-boostType=Grad-ntrees=100-maxdepth=4-shrinkage=0.1',
#     'low_e' : 'kBDT-boostType=Grad-ntrees=200-maxdepth=2-shrinkage=0.3',
#     'low_mu' : 'kBDT-boostType=Grad-ntrees=200-maxdepth=4-shrinkage=0.1',
#     'low_tau' : 'kBDT-boostType=RealAdaBoost-ntrees=100-maxdepth=2-shrinkage=0.1',
#     # 'low_tau' : 'kBDT-boostType=Grad-ntrees=200-maxdepth=2-shrinkage=0.1',
#     # 'HNL-e-m200' : 'kBDT-boostType=Grad-ntrees=200-maxdepth=3-shrinkage=0.1',
# }

DEFAULT_PATH_TO_WEIGHTS = lambda era, region, signalname: os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'TMVA', 'data', 'FinalTrainings', era, region, signalname+'.xml')


class Reader:

    def __init__(self, chain, method_name, name_to_book, region, era, path_to_weights = None, cut_string = None):
        self.reader = ROOT.TMVA.Reader("Silent")
        self.chain = chain
        self.method_name = method_name
        self.region = region
        self.name_to_book = name_to_book
        self.path_to_weights = path_to_weights if path_to_weights is not None else DEFAULT_PATH_TO_WEIGHTS(era, region, name_to_book)
        if not os.path.isfile(self.path_to_weights):
            raise RuntimeError("Invalid path to weights: {0}".format(self.path_to_weights))
        self.variables = getVariableNames(name_to_book, cut_string)
        self.variable_array = self.initializeArrays()
        self.initializeVariables(name_to_book)
        self.bookMethod(era, name_to_book)

    def initializeArrays(self):
        arrays = {}
        for v in self.variables:
            arrays[v] = array('f', [0])
        return arrays

    def initializeVariables(self, name):
        for v in self.variables:
            self.reader.AddVariable(v, self.variable_array[v])

    def bookMethod(self, era, training_name): 
        self.reader.BookMVA(training_name, self.path_to_weights)

    def predict(self, trainingnames=False):
        for v in self.variables:
            if not trainingnames:
                self.variable_array[v][0] = getVariableValue(v)(self.chain)
            else:
                if not 'abs' in v:
                    self.variable_array[v][0] = getattr(self.chain, v)
                else:
                    var_name_stripped = v.split('(')[1].split(')')[0]
                    self.variable_array[v][0] = abs(getattr(self.chain, var_name_stripped))
                    

        return self.reader.EvaluateMVA(self.name_to_book)

    def predictAndWriteToChain(self, chain, trainingnames=False):
        setattr(chain, "".join(i for i in self.name_to_book if i not in "-"), self.predict(trainingnames=trainingnames))
        return 

from HNL.TMVA.mvaDefinitions import listAvailableMVAs
class ReaderArray:

    def __init__(self, chain, method_name, region, era, names_to_book = None, custom_mva_dict = None):
        self.names_to_book = listAvailableMVAs(region, custom_dict = custom_mva_dict) if names_to_book is None else names_to_book
        self.readers = {}
        for name in self.names_to_book:
            self.readers[name] = Reader(chain, method_name, name, region, era)

    def predictAndWriteAll(self, chain, trainingnames=False):
        for reader in self.readers:
            self.readers[reader].predictAndWriteToChain(chain, trainingnames)

#
# Testing code
#

cut_string_dict = {
    None : lambda c:True,
    'lowMassSR' : lambda c: c.M3l<80 and c.l1_pt < 55 and c.met < 75 and c.minMossf < 0,
}
def getNonPromptMVAhist(input_handler, channel, region, era):
    from HNL.Tools.histogram import Histogram
    from HNL.Tools.helpers import progress
    from HNL.Analysis.analysisTypes import var_mva
    from ROOT import TChain
    list_of_hist = {}
    for sample_name in input_handler.background_paths:
        if sample_name == 'nonprompt': continue
        sample_tree = TChain('nonprompt/'+channel+'/trainingtree')
        for sp in input_handler.background_paths[sample_name]:
            sample_tree.Add(sp)
        sample_tree.selection='default'
        print "Filling ", sample_name
        list_of_hist[sample_name] = {}
        for mva in input_handler.signal_names:
            print "     ->", mva
            list_of_hist[sample_name][mva] = Histogram(mva+'-nonprompt', var_mva[mva][0], var_mva[mva][2], var_mva[mva][1])
            reader = Reader(sample_tree, 'kBDT', mva, region, era)
            nentries = sample_tree.GetEntries()
            for entry in xrange(nentries):
                progress(entry, nentries)
                sample_tree.GetEntry(entry)
                if not cut_string_dict[cut_string](sample_tree): continue
                reader.predictAndWriteToChain(sample_tree, trainingnames=True)
                list_of_hist[sample_name][mva].fill(sample_tree, sample_tree.event_weight)

    return list_of_hist

def getAllMVAhist(input_handler, channel, region, era, signal_name = None, cut_string = None):
    from HNL.Tools.histogram import Histogram
    from HNL.Tools.helpers import progress
    from HNL.TMVA.mvaDefinitions import MVA_dict
    from ROOT import TChain
    list_of_hist = {}
    for sample_name in input_handler.background_paths:
        if sample_name == 'nonprompt':
            sample_tree = TChain('nonprompt/'+channel+'/trainingtree')
        else:
            sample_tree = TChain('prompt/'+channel+'/trainingtree')
        for sp in input_handler.background_paths[sample_name]:
            sample_tree.Add(sp)
        sample_tree.selection='default'
        print "Filling ", sample_name
        print "     loading", channel
        list_of_hist[sample_name] = {}
        readers = {}
        for mva in input_handler.signal_names:
            if signal_name is not None and mva != signal_name: continue
            if cut_string is None:
                path_to_use = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'TMVA', 'data', 'training', 
                                                era+'all', region+'-'+sample_tree.selection, 'full', mva, 'kBDT', 
                                                'weights', 'factory_'+MVA_dict[region][mva][0]+'.weights.xml')
            else:
                path_to_use = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'TMVA', 'data', 'training', 
                                era+'all', region+'-'+sample_tree.selection, "".join(i for i in cut_string if i not in "\/:*?<>|& "),
                                mva, 'kBDT', 'weights', 'factory_'+MVA_dict[region][mva][0]+'.weights.xml')
            readers[mva] = Reader(sample_tree, 'kBDT', mva, region, era, path_to_weights=path_to_use)
            list_of_hist[sample_name][mva] = Histogram(mva+'-'+sample_name, MVA_dict[region][mva][2], ('MVA score', 'Events'),  np.arange(-1., 1.1, 0.1))
        nentries = sample_tree.GetEntries()
        #nentries = 20
        for entry in xrange(nentries):
            progress(entry, nentries)
            sample_tree.GetEntry(entry)
            # if not cut_string_dict[cut_string](sample_tree): continue
            if not cut_string_dict[region](sample_tree): continue
            for reader in readers:
                readers[reader].predictAndWriteToChain(sample_tree, trainingnames=True)
                list_of_hist[sample_name][reader].fill(sample_tree, sample_tree.event_weight)

    return list_of_hist


if __name__ == '__main__':
    # in_file = ROOT.TFile('/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/2016/TMVA/Background/DYJetsToLL-M-50.root')
    in_file = ROOT.TFile('/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/2016/TMVA/Signal/HNL-e-m200.root')
    c = in_file.Get('trainingtree')
    reader = Reader(c, 'high_e', 'kBDT')

    for entry in xrange(100):
        c.GetEntry(entry)
        print entry, reader.predict()
    
