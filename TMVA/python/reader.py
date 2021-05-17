import ROOT
from HNL.TMVA.mvaVariables import getVariableNames, getVariableValue
from array import array
import os

ctypes = {
    'F' : 'f',
    'I' : 'i'
}

MVA_of_choice = {
    'high_e' : 'kBDT-boostType=Grad-ntrees=200-maxdepth=3-shrinkage=0.1',
    'high_mu' : 'kBDT-boostType=Grad-ntrees=100-maxdepth=4-shrinkage=0.1',
    'high_tau' : 'kBDT-boostType=Grad-ntrees=100-maxdepth=4-shrinkage=0.1',
    'low_e' : 'kBDT-boostType=Grad-ntrees=200-maxdepth=2-shrinkage=0.3',
    'low_mu' : 'kBDT-boostType=Grad-ntrees=200-maxdepth=4-shrinkage=0.1',
    'low_tau' : 'kBDT-boostType=RealAdaBoost-ntrees=100-maxdepth=2-shrinkage=0.1',
    # 'low_tau' : 'kBDT-boostType=Grad-ntrees=200-maxdepth=2-shrinkage=0.1',
    # 'HNL-e-m200' : 'kBDT-boostType=Grad-ntrees=200-maxdepth=3-shrinkage=0.1',
}

class Reader:

    def __init__(self, chain, method_name, name_to_book, region, model_name = None):
        self.reader = ROOT.TMVA.Reader("Silent")
        self.chain = chain
        self.method_name = method_name
        self.model_name = model_name if model_name is not None else MVA_of_choice[name_to_book]
        self.region = region
        self.name_to_book = name_to_book
        self.variables = getVariableNames(name_to_book)
        self.variable_array = self.initializeArrays()
        self.initializeVariables(name_to_book)
        self.bookMethod(name_to_book)

    def initializeArrays(self):
        arrays = {}
        for v in self.variables:
            arrays[v] = array('f', [0])
        return arrays

    def initializeVariables(self, name):
        for v in getVariableNames(name):
            self.reader.AddVariable(v, self.variable_array[v])

    def bookMethod(self, training_name):
        path_to_weights = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'TMVA', 'data', 'training', 
                                        'all', self.region+'-'+self.chain.selection, training_name, self.method_name, 
                                        'weights', 'factory_'+self.model_name+'.weights.xml')
        self.reader.BookMVA(training_name, path_to_weights)

    def predict(self, trainingnames=False):
        for v in self.variables:
            if not trainingnames:
                self.variable_array[v][0] = getVariableValue(v)(self.chain)
            else:
                self.variable_array[v][0] = getattr(self.chain, v)

        return self.reader.EvaluateMVA(self.name_to_book)

def listAvailableMVAs():
    return MVA_of_choice.keys()

if __name__ == '__main__':
    # in_file = ROOT.TFile('/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/2016/TMVA/Background/DYJetsToLL-M-50.root')
    in_file = ROOT.TFile('/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/2016/TMVA/Signal/HNL-e-m200.root')
    c = in_file.Get('trainingtree')
    reader = Reader(c, 'high_e', 'kBDT')

    for entry in xrange(100):
        c.GetEntry(entry)
        print entry, reader.predict()
    