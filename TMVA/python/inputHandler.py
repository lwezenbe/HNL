# INPUT_BASE = lambda era, year : '/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/TMVA/'+era+year
INPUT_BASE = lambda era, year : os.path.expandvars(os.path.join('/pnfs/iihe/cms/store/user', '$USER', 'skimmedTuples/HNL/TMVA', era+year))
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
        from HNL.Samples.sampleManager import ERA_DICT
        for era in self.era.split('-'):
            for y in ERA_DICT[era]:
                if self.year == 'all': pass
                else:
                    if self.year != y: continue

                if not '-' in self.era or era == 'UL':
                    for signal in self.signal_names:
                        if self.background_names is None:
                            signal_paths[signal].append(os.path.join(INPUT_BASE(era, y), self.region+'-'+self.selection, 'Combined/SingleTree', signal+'.root'))
                        else:
                            signal_paths[signal].append(os.path.join(INPUT_BASE(era, y), self.region+'-'+self.selection, 'Signal', signal+'.root'))
                
                if '-' in self.era and era == 'UL': continue
                # if '-' in self.era and era == 'prelegacy' and y != '2018': continue

                if self.background_names is None:
                    background_paths = None
                else:
                    for bkgr in self.background_names:
                        if bkgr == 'nonprompt':
                            background_paths[bkgr].append(os.path.join(INPUT_BASE(era, y), self.region+'-'+self.selection, 'Background', 'Combined', 'nonprompt_bkgr.root'))
                        else:
                            background_paths[bkgr].append(os.path.join(INPUT_BASE(era, y), self.region+'-'+self.selection, 'Background', bkgr+'.root'))

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

    def getReportOnBackgrounds(self, name='trainingtree', channel = 'NoTau', cut_string=''):

        if self.background_names is None and bkgr_only: 
            raise RuntimeError("You are trying to read empty trees")
        else:
            import uproot
            for bn in self.background_names:
                all_weights = {'total' : 0., 'max' : 0., 'min' : 99999999999999999999999.}
                if cut_string is None:
                    #For some reason uproot.concatenate does not work so we have to use this shitty way
                    for bp in self.background_paths[bn]:
                        in_tree_file = uproot.open(bp)
                        if bn == 'nonprompt':
                            in_tree = in_tree_file['nonprompt'][channel][name].arrays(["event_weight"])
                        else:
                            in_tree = in_tree_file['prompt'][channel][name].arrays(["event_weight"])

                        all_weights['total'] += len(in_tree['event_weight'])
                        all_weights['max'] = max(all_weights['max'], max(in_tree['event_weight']))
                        all_weights['min'] = min(all_weights['min'], min(in_tree['event_weight']))   
                else:             
                    in_tree = ROOT.TChain() 
                    for bp in self.background_paths[bn]:
                        if bn == 'nonprompt':
                            in_tree.Add(bp+'/nonprompt/'+channel+'/'+name)
                        else:
                            in_tree.Add(bp+'/prompt/'+channel+'/'+name)
                    
                    all_weights['total'] = in_tree.Draw("1", cut_string)

                print '\t Checking', bn
                print '\t \t * Total contribution from this background: \t', all_weights['total']
                if cut_string is None:
                    print '\t \t * Maximum weight from this background: \t', all_weights['max']
                    print '\t \t * Minimum weight from this background: \t', all_weights['min']
                print ''

    def getLoader(self, signal, input_variables, additional_cut_str = None):

        if 'had' in signal :
            name = 'SingleTau/trainingtree'
        else:
            name = 'NoTau/trainingtree'
        
        in_tree = self.getTree(signal, name=name)

        additional_cut_str = self.getAdditionalCutString(additional_cut_str)
        nsignal = min(15000, in_tree.Draw("1", "is_signal"+additional_cut_str))
        nbkgr = min(100000, in_tree.Draw("1", "!is_signal"+additional_cut_str))

        if self.numbers_not_in_file:
            self.numbers = [int(nsignal*0.6), int(nbkgr*0.6), int(nsignal*0.4), int(nbkgr*0.4)]

        if additional_cut_str != '':
            pruned_string = "".join(i for i in additional_cut_str if i not in "\/:*?<>|& ")
            loader = ROOT.TMVA.DataLoader('data/training/'+self.era+self.year+'/'+self.region+'-'+self.selection+'/'+pruned_string+'/'+signal+'/kBDT')
        else:
            loader = ROOT.TMVA.DataLoader('data/training/'+self.era+self.year+'/'+self.region+'-'+self.selection+'/'+signal+'/kBDT')
        cuts = ROOT.TCut("is_signal"+additional_cut_str)
        cutb = ROOT.TCut("!is_signal"+additional_cut_str)
        loader.SetInputTrees(in_tree, cuts, cutb)
        loader.SetWeightExpression("event_weight")

        #Set input variables
        for var in input_variables:
            v, t = var.split('/') 
            loader.AddVariable(v, t)

        return loader

    def getAdditionalCutString(self, cut_string):
        if cut_string is not None:
            additional_cut_str = '&& ' + cut_string
        else:
            additional_cut_str = ''
        return additional_cut_str

if __name__ == '__main__':
    ih = InputHandler('all', 'baseline')
    print(ih.numbers, ih.signal_names, ih.background_names)