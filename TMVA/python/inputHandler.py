# INPUT_BASE = lambda era, year : '/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/TMVA/'+era+year
INPUT_BASE = lambda era, year : os.path.expandvars(os.path.join('/pnfs/iihe/cms/store/user', '$USER', 'skimmedTuples/HNL/TMVA', era+year))
import os
import ROOT

signalregion_cuts = {
    'lowMassSR' : 'l1_pt<55&&M3l<80&&met<75&&minMossf<0',
    'lowMassSRloose' : 'l1_pt<55&&M3l<80&&met<75&&abs(MZossf-91.1876)>15&&minMossf>5',
    #'lowMassSRloose' : 'l1_pt<55&&M3l<80&&met<75&&abs(MZossf-91.1876)>15',
    'highMassSR' : 'l1_pt>55&&l2_pt>15&&l3_pt>10&&abs(MZossf-91.1876)>15&&abs(M3l-91.1876)>15&&(minMossf<0||minMossf>5)'
}

class InputHandler:
    NTREES = ['25', '50', '75', '100', '150', '200', '300', '400']
    MAXDEPTH = ['2', '3', '4']
    BOOSTTYPES = ['Grad']
    SHRINKAGE = [ '0.1', '0.3', '1.']

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

                if self.background_names is None:
                    background_paths = None
                else:
                    for bkgr in self.background_names:
                        if bkgr == 'nonprompt':
                            background_paths[bkgr].append(os.path.join(INPUT_BASE(era, y), 'baseline-'+self.selection, 'Background', 'Combined', 'nonprompt_bkgr.root'))
                        else:
                            background_paths[bkgr].append(os.path.join(INPUT_BASE(era, y), 'baseline-'+self.selection, 'Background', bkgr+'.root'))
                
                if 'UL' in self.era and era =='prelegacy': continue
                for signal in self.signal_names:
                    if self.background_names is None:
                        signal_paths[signal].append(os.path.join(INPUT_BASE(era, y), 'baseline-'+self.selection, 'Combined/SingleTree', signal+'.root'))
                    else:
                        signal_paths[signal].append(os.path.join(INPUT_BASE(era, y), 'baseline-'+self.selection, 'Signal', signal+'.root'))
                

        self.signal_paths = signal_paths
        self.background_paths = background_paths

        return signal_paths, background_paths

    def getTree(self, signal, name='trainingtree', signal_only = False, bkgr_only=False, specific_sample = None):

        in_tree = ROOT.TChain() 
        if not bkgr_only:
            for sub_signal in self.signal_paths[signal]:
                if specific_sample is not None and signal != specific_sample: continue
                in_tree.Add(sub_signal+'/prompt/'+name)
                in_tree.Add(sub_signal+'/nonprompt/'+name)
        if not signal_only:
            if self.background_names is None and bkgr_only: 
                raise RuntimeError("You are trying to make empty trees")
            else:
                for bn in self.background_names:
                    if specific_sample is not None and bn != specific_sample: continue
                    for bp in self.background_paths[bn]:
                        if bn == 'nonprompt':
                            in_tree.Add(bp+'/nonprompt/'+name)
                            #in_tree.Add(bp+'/sideband/'+name)
                        else:
                            in_tree.Add(bp+'/prompt/'+name)  
        return in_tree

    def getReportOnBackgrounds(self, name='trainingtree', channel = 'NoTau', cut_string=''):

        if self.background_names is None and bkgr_only: 
            raise RuntimeError("You are trying to read empty trees")
        else:
            import uproot
            for bn in self.background_names:
                all_weights = {'total' : 0., 'max' : 0., 'min' : 99999999999999999999999., 'avg' : 0}
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
                    
                    htemp = ROOT.TH1D('htemp', 'htemp', 300, -50., 50.)
                    all_weights['total'] = in_tree.Draw("event_weight>>htemp", cut_string)

                print '\t Checking', bn
                print '\t \t * Total contribution from this background: \t', all_weights['total'], 'with weight: \t', htemp.GetMean()
                if cut_string is None:
                    print '\t \t * Maximum weight from this background: \t', all_weights['max']
                    print '\t \t * Minimum weight from this background: \t', all_weights['min']
                print ''

    def getLoader(self, signal, input_variables, additional_cut_str = None, is_test = False):

        if 'had' in signal :
            name = 'SingleTau/trainingtree'
        else:
            name = 'NoTau/trainingtree'
        
        in_tree = self.getTree(signal, name=name)

        condition = additional_cut_str if additional_cut_str is not None else signalregion_cuts[self.region]

        condition = self.getAdditionalCutString(condition)
        nsignal = min(20000, in_tree.Draw("1", "is_signal"+condition))
        nbkgr = min(100000, in_tree.Draw("1", "!is_signal"+condition))

        if self.numbers_not_in_file:
            self.numbers = [int(nsignal*0.6), int(nbkgr*0.6), int(nsignal*0.4), int(nbkgr*0.4)]

        pruned_string = "".join(i for i in additional_cut_str if i not in "\/:*?<>|& ") if additional_cut_str is not None else 'full'
        loader = ROOT.TMVA.DataLoader(os.path.expandvars(os.path.join('TMVA' if args.isTest else '', 'data','testArea' if is_test else '', 'training', self.era+self.year, self.region+'-'+self.selection, pruned_string, signal, 'kBDT')))
        cuts = ROOT.TCut("is_signal"+condition)
        cutb = ROOT.TCut("!is_signal"+condition)
        loader.SetInputTrees(in_tree, cuts, cutb)
        #loader.SetWeightExpression("event_weight*fake_weight_{0}".format(self.region))
        loader.SetWeightExpression("abs(event_weight)")

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
    ih = InputHandler('UL', 'all', 'highMassSR', 'default')
    print(ih.numbers, ih.signal_names, ih.background_names)
