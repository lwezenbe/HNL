import ROOT
from HNL.TMVA.mvaVariables import getVariableNames, getVariableValue
from array import array
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

MVA_of_choice_None = {
    # 'highmass-e' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3',
    'highestmass-e' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3',
    # 'highmass-mu' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=3-shrinkage=0.3',
    'highestmass-mu' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3',
    # 'highmass-tau' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3',
    'highestmass-tau' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3',
    # 'mediummass-e' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3',
    # 'mediummass-mu' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3',
    # 'mediummass-tau' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3',
    'mediummass85100-e' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3',
    'mediummass85100-mu' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3',
    # 'mediummass-tau' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3',
    'mediummass150200-e' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3',
    'mediummass150200-mu' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3',
    # 'mediummass-tau' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3',
    'mediummass250400-e' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3',
    'mediummass250400-mu' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3',
    # 'mediummass-tau' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3',
    # 'lowmass-e' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.1',
    # 'lowmass-mu' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=3-shrinkage=0.1',
    # 'lowmass-tau' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3',
    # 'lowestmass-e' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.3',
    # 'lowestmass-mu' : 'kBDT-boostType=AdaBoost-ntrees=200-maxdepth=3-shrinkage=1',
    # 'lowestmass-tau' : 'kBDT-boostType=Grad-ntrees=200-maxdepth=4-shrinkage=0.1',
}

MVA_of_choice_M3l80 = {
    'lowmass-e' : 'kBDT-boostType=Grad-ntrees=200-maxdepth=4-shrinkage=0.1',
    'lowmass-mu' : 'kBDT-boostType=Grad-ntrees=200-maxdepth=2-shrinkage=0.1',
    'lowmass-tau' : 'kBDT-boostType=Grad-ntrees=100-maxdepth=3-shrinkage=0.1',
    'lowestmass-e' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=3-shrinkage=0.1',
    'lowestmass-mu' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.1',
    # 'lowestmass-taulep' : 'kBDT-boostType=Grad-ntrees=200-maxdepth=3-shrinkage=0.1', 
    'lowestmass-taulep' : 'kBDT-boostType=AdaBoost-ntrees=100-maxdepth=2-shrinkage=0.1', 
    'lowestmass-tauhad' : 'kBDT-boostType=Grad-ntrees=200-maxdepth=4-shrinkage=0.1', 
}
MVA_of_choice_l1pt55 = {
    'lowmass-e' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=3-shrinkage=0.1',
    'lowmass-mu' : 'kBDT-boostType=Grad-ntrees=200-maxdepth=2-shrinkage=0.1',
    'lowmass-tau' : 'kBDT-boostType=Grad-ntrees=100-maxdepth=3-shrinkage=0.1',
    'lowestmass-e' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=3-shrinkage=0.1',
    'lowestmass-mu' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=4-shrinkage=0.1',
    'lowestmass-tau' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=3-shrinkage=0.1', 
}
MVA_of_choice_M3l80l1pt50 = {
    # 'lowmass-e' : 'kBDT-boostType=Grad-ntrees=200-maxdepth=2-shrinkage=0.1',
    'lowmass-e' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=3-shrinkage=0.1',
    'lowmass-mu' : 'kBDT-boostType=Grad-ntrees=100-maxdepth=4-shrinkage=0.1',
    # 'lowmass-tau' : 'kBDT-boostType=Grad-ntrees=300-maxdepth=2-shrinkage=0.3',
    'lowestmass-e' : 'kBDT-boostType=Grad-ntrees=200-maxdepth=2-shrinkage=0.1',
    'lowestmass-mu' : 'kBDT-boostType=AdaBoost-ntrees=200-maxdepth=3-shrinkage=1',
    # 'lowestmass-tau' : 'kBDT-boostType=AdaBoost-ntrees=300-maxdepth=3-shrinkage=1', 
}

MVA_of_choice = {
    None : MVA_of_choice_None,
    "M3l<80" : MVA_of_choice_M3l80,
    "l1_pt<55" : MVA_of_choice_l1pt55,
    "M3l<80&&l1_pt<55" : MVA_of_choice_M3l80l1pt50,
    "M3l<80&&l1_pt<55&&met<75" : MVA_of_choice_M3l80l1pt50,
    "met<75" : MVA_of_choice_M3l80l1pt50,
    "dRmaxMossf<0" : MVA_of_choice_M3l80l1pt50,

}

class Reader:

    def __init__(self, chain, method_name, name_to_book, region, era, model_name = None, cut_string = None):
        self.reader = ROOT.TMVA.Reader("Silent")
        self.chain = chain
        self.method_name = method_name
        self.model_name = model_name if model_name is not None else MVA_of_choice[cut_string][name_to_book]
        self.region = region
        self.cut_string = cut_string
        self.name_to_book = name_to_book
        self.variables = getVariableNames(name_to_book)
        self.variable_array = self.initializeArrays()
        self.initializeVariables(name_to_book)
        self.bookMethod(era, name_to_book)

    def initializeArrays(self):
        arrays = {}
        for v in self.variables:
            arrays[v] = array('f', [0])
        return arrays

    def initializeVariables(self, name):
        for v in getVariableNames(name):
            self.reader.AddVariable(v, self.variable_array[v])

    def bookMethod(self, era, training_name):
        if self.cut_string is None:
            path_to_weights = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'TMVA', 'data', 'training', 
                                        era+'all', self.region+'-'+self.chain.selection, training_name, self.method_name, 
                                        'weights', 'factory_'+self.model_name+'.weights.xml')
        else:
            path_to_weights = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'TMVA', 'data', 'training', 
                            era+'all', self.region+'-'+self.chain.selection, "".join(i for i in self.cut_string if i not in "\/:*?<>|& "),
                            training_name, self.method_name, 'weights', 'factory_'+self.model_name+'.weights.xml')  
        self.reader.BookMVA(training_name, path_to_weights)

    def predict(self, trainingnames=False):
        for v in self.variables:
            if not trainingnames:
                self.variable_array[v][0] = getVariableValue(v)(self.chain)
            else:
                self.variable_array[v][0] = getattr(self.chain, v)

        return self.reader.EvaluateMVA(self.name_to_book)

    def predictAndWriteToChain(self, chain, trainingnames=False):
        setattr(chain, "".join(i for i in self.name_to_book if i not in "-"), self.predict(trainingnames=trainingnames))
        return 

def listAvailableMVAs(cut_string = None):
    return MVA_of_choice[cut_string].keys()


cut_string_dict = {
    None : lambda c:True,
    "M3l<80" : lambda c: c.M3l<80,
    'full' : lambda c: c.M3l<80 and c.l1_pt < 55 and c.met < 75 and c.dRmaxMossf < 0,
    'fullwithOSSF' : lambda c: c.M3l<80 and c.l1_pt < 55 and c.met < 75,
    'fullnomet' : lambda c: c.M3l<80 and c.l1_pt < 55 and c.dRmaxMossf < 0,
    'M3lnoOSSF' : lambda c: c.M3l<80 and c.dRmaxMossf < 0,
    'noOSSF' : lambda c: c.dRmaxMossf < 0,
    'l1ptnoOSSF' : lambda c: c.l1_pt < 55 and c.dRmaxMossf < 0,
    'l1pt' : lambda c: c.l1_pt < 55,
}

def getNonPromptMVAhist(input_handler, channel, region, era, cut_string = None):
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
            reader = Reader(sample_tree, 'kBDT', mva, region, era, cut_string = cut_string)
            nentries = sample_tree.GetEntries()
            for entry in xrange(nentries):
                progress(entry, nentries)
                sample_tree.GetEntry(entry)
                if not cut_string_dict[cut_string](sample_tree): continue
                reader.predictAndWriteToChain(sample_tree, trainingnames=True)
                list_of_hist[sample_name][mva].fill(sample_tree, sample_tree.event_weight)

    return list_of_hist

def getAllMVAhist(input_handler, channel, region, era, cut_string = None):
    from HNL.Tools.histogram import Histogram
    from HNL.Tools.helpers import progress
    from HNL.Analysis.analysisTypes import var_mva
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
        list_of_hist[sample_name] = {}
        for mva in input_handler.signal_names:
            print "     ->", mva
            list_of_hist[sample_name][mva] = Histogram(mva+'-'+sample_name, var_mva[mva][0], var_mva[mva][2], var_mva[mva][1])
            reader = Reader(sample_tree, 'kBDT', mva, region, era, cut_string = cut_string)
            nentries = sample_tree.GetEntries()
            # nentries = 20
            for entry in xrange(nentries):
                progress(entry, nentries)
                sample_tree.GetEntry(entry)
                # if not cut_string_dict[cut_string](sample_tree): continue
                if not cut_string_dict['full'](sample_tree): continue
                reader.predictAndWriteToChain(sample_tree, trainingnames=True)
                list_of_hist[sample_name][mva].fill(sample_tree, sample_tree.event_weight)

    return list_of_hist


if __name__ == '__main__':
    # in_file = ROOT.TFile('/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/2016/TMVA/Background/DYJetsToLL-M-50.root')
    in_file = ROOT.TFile('/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/2016/TMVA/Signal/HNL-e-m200.root')
    c = in_file.Get('trainingtree')
    reader = Reader(c, 'high_e', 'kBDT')

    for entry in xrange(100):
        c.GetEntry(entry)
        print entry, reader.predict()
    