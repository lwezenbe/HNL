import ROOT
from HNL.TMVA.mvaVariables import getVariables, getVariableNames, input_variables
from array import array
import os

ctypes = {
    'F' : 'f',
    'I' : 'i'
}

class Reader:

    def __init__(self, chain, method_name, name_to_book, region):
        self.reader = ROOT.TMVA.Reader("Silent")
        self.chain = chain
        self.method_name = method_name
        self.region = region
        self.name_to_book = name_to_book
        self.variables = input_variables
        self.variable_array = self.initializeArrays()
        self.initializeVariables(name_to_book)
        self.bookMethod(name_to_book, str(chain.year))

    def initializeArrays(self):
        arrays = {}
        for v in self.variables:
            arrays[v] = array('f', [0])
        return arrays

    def initializeVariables(self, name):
        for v in getVariableNames(name):
            self.reader.AddVariable(v, self.variable_array[v])

    def bookMethod(self, training_name, year):
        path_to_weights = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'TMVA', 'data', 'training', 'all', self.region+'-'+self.chain.selection, training_name, self.method_name, 'weights', 'factory_'+self.method_name+'.weights.xml')
        self.reader.BookMVA(training_name, path_to_weights)

    def predict(self):
        for v in self.variables:
            self.variable_array[v][0] = self.variables[v]['var'](self.chain)

        return self.reader.EvaluateMVA(self.name_to_book)

if __name__ == '__main__':
    from HNL.Tools.helpers import getObjFromFile
    # in_file = ROOT.TFile('/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/2016/TMVA/Background/DYJetsToLL-M-50.root')
    in_file = ROOT.TFile('/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/2016/TMVA/Signal/HNL-e-m200.root')
    c = in_file.Get('trainingtree')
    # print c, c.GetEntries()
    reader = Reader(c, 'high_e', 'kBDT')
    # print c, c.GetEntries()

    for entry in xrange(100):
        c.GetEntry(entry)
        print entry, reader.predict()
    