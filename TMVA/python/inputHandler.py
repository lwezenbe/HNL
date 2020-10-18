INPUT_BASE = '/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/2016/TMVA'
import os
import ROOT

class InputHandler:

    def __init__(self, in_file):
        self.in_file = in_file
        self.numbers = None
        self.signal_names = None
        self.background_names = None
        self.numbers_not_in_file = False
        self.readInFile()

        self.background_paths = None
        self.signal_paths = None
        self.getPathNames()
        
    def readInFile(self):
        infos = [line.split('#')[0].strip() for line in open(self.in_file)]                     # Strip % comments and \n charachters
        infos = [line for line in infos if line != '']                                 # Get lines into tuples

        # First split off the backgrounds
        bkgr_index = infos.index('//Background')
        bkgr_list = infos[bkgr_index+1:]
        infos = infos[:bkgr_index]

        if len(bkgr_list) == 0:
            bkgr_list = None

        # Split off signal and numbers list
        signal_list = infos[1:]
        numbers_list = infos[0]

        if numbers_list != 'Default': 
            numbers = [int(n) for n in numbers_list.split(' ')]
        else:
            numbers = None
            self.numbers_not_in_file = True

        self.numbers = numbers
        self.signal_names = signal_list
        self.background_names = bkgr_list

        return numbers, signal_list, bkgr_list


    def getPathNames(self):
        signal_paths = {}
        background_paths = []
        for signal in self.signal_names:
            if self.background_names is None:
                signal_paths[signal] = os.path.join(INPUT_BASE, 'Combined/SingleTree', signal+'.root')
            else:
                signal_paths[signal] = os.path.join(INPUT_BASE, 'Signal', signal+'.root')
        
        if self.background_names is None:
            background_paths = None
        else:
            for bkgr in self.background_names:
                background_paths.append(os.path.join(INPUT_BASE, 'Background', bkgr+'.root'))

        self.signal_paths = signal_paths
        self.background_paths = background_paths

        return signal_paths, background_paths

    def getTree(self, signal):
        in_tree = ROOT.TChain('trainingtree') 
        in_tree.Add(self.signal_paths[signal])
        if self.background_names is not None:
            for b in self.background_paths:
                in_tree.Add(b)
        return in_tree

    def getLoader(self, signal, input_variables, year):

        in_tree = self.getTree(signal)
        nsignal = min(15000, in_tree.Draw("1", "is_signal"))
        nbkgr = min(15000, in_tree.Draw("1", "!is_signal"))

        if self.numbers_not_in_file:
            self.numbers = [int(nsignal*0.9), int(nbkgr*0.9), int(nsignal*0.1), int(nbkgr*0.1)]

        loader = ROOT.TMVA.DataLoader('data/training/'+str(year)+'/'+signal+'/kBDT')
        cuts = ROOT.TCut("is_signal")
        cutb = ROOT.TCut("!is_signal")
        loader.SetInputTrees(in_tree, cuts, cutb)
        loader.SetWeightExpression("event_weight")

        #Set input variables
        for var in input_variables:
            v, t = var.split('/') 
            loader.AddVariable(v, t)

        return loader

if __name__ == '__main__':
    ih = InputHandler(os.path.expandvars('$CMSSW_BASE/src/HNL/TMVA/data/InputLists/2016.conf'))
    print ih.numbers, ih.signal_names, ih.background_names