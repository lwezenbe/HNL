INPUT_BASE = lambda era, year : '/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/TMVA/'+era+year
import os
import ROOT

class InputHandler:

    def __init__(self, era, year, region, selection):
        self.in_file = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'TMVA', 'data', 'InputLists', era+year+'-'+region+'.conf'))
        self.year = year
        self.era = era
        self.region = region
        self.selection = selection
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
        for signal in self.signal_names:
            signal_paths[signal] = []
        background_paths = {}
        for bkgr in self.background_names:
            background_paths[bkgr] = []
        from HNL.Sample.sampleManager import ERA_DICT
        for y in ERA_DICT[self.era]:
            if self.year == 'all': pass
            else:
                if self.year != y: continue

            for signal in self.signal_names:
                if self.background_names is None:
                    signal_paths[signal].append(os.path.join(INPUT_BASE(self.era, y), self.region+'-'+self.selection, 'Combined/SingleTree', signal+'.root'))
                else:
                    signal_paths[signal].append(os.path.join(INPUT_BASE(self.era, y), self.region+'-'+self.selection, 'Signal', signal+'.root'))
            
            if self.background_names is None:
                background_paths = None
            else:
                for bkgr in self.background_names:
                    if bkgr == 'nonprompt':
                        background_paths[bkgr].append(os.path.join(INPUT_BASE(self.era, y), self.region+'-'+self.selection, 'Background', 'Combined', 'all_bkgr.root'))
                    else:
                        background_paths[bkgr].append(os.path.join(INPUT_BASE(self.era, y), self.region+'-'+self.selection, 'Background', bkgr+'.root'))

        self.signal_paths = signal_paths
        self.background_paths = background_paths

        return signal_paths, background_paths

    def getTree(self, signal, name='trainingtree', signal_only = False, bkgr_only=False):
        in_tree = ROOT.TChain() 
        if not bkgr_only:
            for sub_signal in self.signal_paths[signal]:
                in_tree.Add(sub_signal+'/prompt/'+name)
                in_tree.Add(sub_signal+'/nonprompt/'+name)
        if not signal_only:
            if self.background_names is None and bkgr_only: 
                raise RuntimeError("You are trying to make empty trees")
            else:
                for bn in self.background_names:
                    for bp in self.background_paths[bn]:
                        if bn == 'nonprompt':
                            in_tree.Add(bp+'/nonprompt/'+name)
                        else:
                            in_tree.Add(bp+'/prompt/'+name)  
        return in_tree

    def getLoader(self, signal, input_variables):

        if signal.split('_')[-1] in ['e', 'mu']:
            name = 'NoTau/trainingtree'
        else:
            name = 'Total/trainingtree'
        in_tree = self.getTree(signal, name=name)
        nsignal = min(15000, in_tree.Draw("1", "is_signal"))
        nbkgr = min(100000, in_tree.Draw("1", "!is_signal"))

        if self.numbers_not_in_file:
            self.numbers = [int(nsignal*0.6), int(nbkgr*0.6), int(nsignal*0.4), int(nbkgr*0.4)]

        loader = ROOT.TMVA.DataLoader('data/training/'+self.era+self.year+'/'+self.region+'-'+self.selection+'/'+signal+'/kBDT')
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
    ih = InputHandler('all', 'baseline')
    print ih.numbers, ih.signal_names, ih.background_names