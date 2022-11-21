from HNL.Tools.helpers import isValidRootFile, rootFileContent, getObjFromFile, makeDirIfNeeded
from ROOT import TFile, TH1F
import numpy as np
from HNL.EventSelection.eventCategorization import CATEGORIES
from HNL.Samples.sample import Sample

class Cutter():

    def __init__(self, name = None, chain = None, categories = None):
        self.name = name
        self.chain = chain
        self.categories = categories if categories != 'auto' else [c for c in CATEGORIES]
        self.list_of_cuts = {}
        self.order_of_cuts = {}
        if categories is not None:
            for cat in self.categories:
                self.list_of_cuts[cat] = {}
                self.order_of_cuts[cat] = []
        self.list_of_cuts[-1] = {}
        self.order_of_cuts[-1] = []

    def cut(self, passed, cut_name):

        for cat in self.categories:
            if cut_name not in self.list_of_cuts[cat].keys():
                self.list_of_cuts[cat][cut_name] = TH1F(cut_name, cut_name, 1, 0, 1)
                self.list_of_cuts[cat][cut_name].SetDirectory(0)
                self.order_of_cuts[cat].append(cut_name)
        if cut_name not in self.list_of_cuts[-1].keys():
            self.list_of_cuts[-1][cut_name] = TH1F(cut_name, cut_name, 1, 0, 1)
            self.list_of_cuts[-1][cut_name].SetDirectory(0)
            self.order_of_cuts[-1].append(cut_name)

        if passed:
            weight = self.chain.weight if self.chain.weight is not None else 1.
            if self.chain.category is not None: self.list_of_cuts[self.chain.category][cut_name].Fill(.5, weight)
            elif self.categories is not None:
                for cat in self.categories:
                    self.list_of_cuts[cat][cut_name].Fill(.5, weight)
            self.list_of_cuts[-1][cut_name].Fill(.5, weight)
            return True
        return False
    
    def printAllCuts(self, category = None):
        if category is not None:
            return self.order_of_cuts[category]
        else:
            return self.order_of_cuts[-1]

    def printAllEvents(self, category = None):
        if category is not None:
            return [(cut, self.list_of_cuts[category][cut]) for cut in self.order_of_cuts[category]]
        else:
            return [(cut, self.list_of_cuts[cut][-1]) for cut in self.order_of_cuts[-1]]

    def saveCutFlow(self, out_file, arg_string = None):

        original_path = out_file
        if arg_string is not None:
            split_path = out_file.split('/')
            index_to_use = split_path.index('testArea') + 1
            #
            # Have to hardcode because $HOME doesnt work on t2b condor
            #
            import os
            path_to_use = os.path.expandvars("/storage_mnt/storage/user/lwezenbe/Testing/Latest/"+'/'.join(split_path[index_to_use:-1])+'/'+arg_string+'/'+split_path[-1])
        else:
            path_to_use = original_path

        if isValidRootFile(path_to_use):
            f = TFile(path_to_use, 'update')
        else:
            f = TFile(path_to_use, 'recreate')
        
        f.mkdir('cutflow')
        f.cd('cutflow')

        if self.name:
            f.mkdir('cutflow/'+self.name)
            f.cd('cutflow/'+self.name)

        if self.categories is not None:
            for cat in self.categories:
                tmp_hist = TH1F('unweighted_cutflow_{}'.format(cat), 'unweighted_cutflow_{}'.format(cat), len(self.order_of_cuts[cat]), 0, len(self.order_of_cuts[cat]))
                for icut, cut in enumerate(self.order_of_cuts[cat]):
                    tmp_hist.GetXaxis().SetBinLabel(icut+1, cut)
                    tmp_hist.SetBinContent(icut+1, self.list_of_cuts[cat][cut].GetEntries())
                    tmp_hist.SetBinError(icut+1, np.sqrt(self.list_of_cuts[cat][cut].GetEntries()))
                tmp_hist.Write()
                tmp_hist = TH1F('weighted_cutflow_{}'.format(cat), 'weighted_cutflow_{}'.format(cat), len(self.order_of_cuts[cat]), 0, len(self.order_of_cuts[cat]))
                for icut, cut in enumerate(self.order_of_cuts[cat]):
                    tmp_hist.GetXaxis().SetBinLabel(icut+1, cut)
                    tmp_hist.SetBinContent(icut+1, self.list_of_cuts[cat][cut].GetSumOfWeights())
                    tmp_hist.SetBinError(icut+1, self.list_of_cuts[cat][cut].GetBinError(1))
                tmp_hist.Write()
        tmp_hist = TH1F('unweighted_cutflow_all', 'unweighted_cutflow_all', len(self.order_of_cuts[-1]), 0, len(self.order_of_cuts[-1]))
        for icut, cut in enumerate(self.order_of_cuts[-1]):
            tmp_hist.GetXaxis().SetBinLabel(icut+1, cut)
            tmp_hist.SetBinContent(icut+1, self.list_of_cuts[-1][cut].GetEntries())
            tmp_hist.SetBinError(icut+1, np.sqrt(self.list_of_cuts[-1][cut].GetEntries()))
        tmp_hist.Write()
        tmp_hist = TH1F('weighted_cutflow_all', 'weighted_cutflow_all', len(self.order_of_cuts[cat]), 0, len(self.order_of_cuts[-1]))
        for icut, cut in enumerate(self.order_of_cuts[-1]):
            tmp_hist.GetXaxis().SetBinLabel(icut+1, cut)
            tmp_hist.SetBinContent(icut+1, self.list_of_cuts[-1][cut].GetSumOfWeights())
            tmp_hist.SetBinError(icut+1, self.list_of_cuts[-1][cut].GetBinError(1))
        tmp_hist.Write()

        f.Close()
        # t = TTree('cutflowtree', 'cutflowtree')
        # branches = [cut+'/F' for cut in self.order_of_cuts]
        # new_vars = makeBranches(t, branches)

        # Now rerun with real testArea
        if arg_string is not None:
            self.saveCutFlow(original_path, None)

class CutterCollection():
    
    def __init__(self, names, chain = None, categories = None):
        self.names = names
        self.chain = chain
        self.cutters = {}
        for name in self.names:
            self.cutters[name] = Cutter(name, chain, categories)

    def cut(self, passed, cut_name, cutter_name = None):
        if cutter_name is not None:
            self.cutters[cutter_name].cut(passed, cut_name)
        else:
            for name in self.names:
                self.cutters[name].cut(passed, cut_name)

    def saveCutFlow(self, out_file, arg_string = None):
        for name in self.names:
            self.cutters[name].saveCutFlow(out_file, arg_string)

    def getCutter(self, name):
        return self.cutters[name]

from HNL.Plotting.plot import makeList
def printCutFlow(in_file_paths, out_file_path, subdir = None, ignore_weights = False, categories = ['all'], group_backgrounds = True):
    subdir = 'cutflow' if subdir is None else 'cutflow/'+subdir
    in_file_path_names = in_file_paths.keys()

    weight_string = 'weighted' if not ignore_weights else 'unweighted'
    tmp_hist = {}

    max_length = 0
    longest_sample = None
    longest_subfile = None
    for ifp in in_file_path_names:
        for sfp in in_file_paths[ifp]:
            tmp_length = getObjFromFile(sfp, subdir+'/'+weight_string+'_cutflow_all').GetNbinsX()
            if tmp_length > max_length:
                max_length = tmp_length
                longest_sample = ifp        
                longest_subfile = sfp

    reference_hist = getObjFromFile(longest_subfile, subdir+'/'+weight_string+'_cutflow_all')
    cut_names = []
    for b in xrange(1, max_length+1):
        cut_names.append(reference_hist.GetXaxis().GetBinLabel(b))
   
    def findLabelBin(hist, label):
        for b in xrange(1, hist.GetNbinsX()+1):
            if hist.GetXaxis().GetBinLabel(b) == label: return b
        return None

    list_of_cut_values = {}
    for ifp in in_file_path_names:
        is_bkgr = not 'HNL' in ifp
        if group_backgrounds and is_bkgr:
            ifp_to_use = 'background'
        else:
            ifp_to_use = ifp
        if ifp_to_use not in list_of_cut_values.keys(): list_of_cut_values[ifp_to_use] = []

        if not is_bkgr and not ignore_weights:
            flavor = Sample.getSignalFlavor(ifp.split('/')[-1])
            if 'tau' in flavor: flavor = 'tau'
            mass = Sample.getSignalMass(ifp.split('/')[-1])
            from HNL.Analysis.analysisTypes import signal_couplingsquared 

        def getBinContent(hist, b):
            val = hist.GetBinContent(b)
            #tmp solution
            if val == 0. and b in [12, 13]:
                return getBinContent(hist, b-1)
            return val

        for ic, c in enumerate(categories):
            for isfp, sfp in enumerate(in_file_paths[ifp]):
                tmp_hist = getObjFromFile(sfp, subdir+'/'+weight_string+'_cutflow_'+c)
                if not is_bkgr and not ignore_weights: tmp_hist.Scale(signal_couplingsquared[flavor][mass]/Sample.getSignalCouplingSquared(ifp.split('/')[-1]))
                for icut, cut in enumerate(cut_names):
                    if ic == 0 and isfp == 0:
                        list_of_cut_values[ifp_to_use].append(0.)
                    bin_to_use = findLabelBin(tmp_hist, cut)
                    if bin_to_use is not None:
                        list_of_cut_values[ifp_to_use][icut] += getBinContent(tmp_hist, bin_to_use) 
   
#    for ifp in in_file_path_names:
#        is_bkgr = not 'HNL' in ifp
#        if group_backgrounds and is_bkgr:
#            ifp_to_use = 'background'
#        else:
#            ifp_to_use = ifp
#        for ic, c in enumerate(categories):
#            if ifp_to_use not in tmp_hist.keys() and ic == 0:
#                tmp_hist[ifp_to_use] = getObjFromFile(in_file_paths[ifp], subdir+'/'+weight_string+'_cutflow_'+c)
#            else:
#                tmp_hist[ifp_to_use].Add(getObjFromFile(in_file_paths[ifp], subdir+'/'+weight_string+'_cutflow_'+c))
#
#
#    list_of_cut_values = {}
#    for ifp in tmp_hist.keys():
#        list_of_cut_values[ifp] = []
#        for b in xrange(1, len(cut_names)+1):
#            list_of_cut_values[ifp].append(tmp_hist[ifp].GetBinContent(b))

    from HNL.Tools.helpers import makeDirIfNeeded
    makeDirIfNeeded(out_file_path+'/cutflowtable.txt')
    out_file = open(out_file_path+'/cutflowtable.txt', 'w')
    
    signal_path_names = sorted([x for x in list_of_cut_values.keys() if 'HNL' in x], key = lambda x: Sample.getSignalMass(x))
    background_path_names = [x for x in list_of_cut_values.keys() if not 'HNL' in x]
    total_path_names = background_path_names + signal_path_names
    
    out_file.write('\\begin{tabular}{l|'+'|'.join(['c' for x in total_path_names])+'} \n')
    out_file.write('\\hline \n')
    out_file.write('Selection & ' + ' & '.join(total_path_names) + '\\\\ \\hline \n')
    for ik, k in enumerate(cut_names):
        out_file.write(k +' & ' +  '&'.join(['%s \t'%float('%.1f' % list_of_cut_values[n][ik]) for n in total_path_names]) + '\\\\ \n')
    
    out_file.write('\\end{tabular}')
    # out_file.write('NAME \t \t \t ' + '\t'.join([k.split('/')[-1] for k in key_names]) + '\n')
    # for n in in_file_path_names:
    #     out_file.write(n +'\t \t \t ' + '\t'.join([str(list_of_cut_values[n][k]) for k in key_names]) + '\n')
    out_file.close()

def printSelections(in_file_path, out_file_path):
    in_file = TFile(in_file_path)
    key_names = [k[0] for k in rootFileContent(in_file, '/', starting_dir = 'cutflow')]
    makeDirIfNeeded(out_file_path)
    out_file = open(out_file_path, 'w')
    for k in key_names:
        if 'Total' in k: continue
        out_file.write(k.split('/')[-1] + '\n')
    return

from HNL.Plotting.plot import Plot
import ROOT
def plotCutFlow(in_file_paths, out_file_path, ignore_weights=False, output_name = None, subdir = None, categories = ['all']):
    list_of_cut_hist = []
    subdir = 'cutflow' if subdir is None else 'cutflow/'+subdir
    weight_string = 'weighted' if not ignore_weights else 'unweighted'
    in_file_path_names = in_file_paths.keys()

    for i_ifp, ifp in enumerate(in_file_path_names):
        for ic, c in enumerate(categories):
            if ic == 0:
                list_of_cut_hist.append(getObjFromFile(in_file_paths[ifp], subdir+'/'+weight_string+'_cutflow_'+c))
            else:
                list_of_cut_hist[i_ifp].Add(getObjFromFile(in_file_paths[ifp], subdir+'/'+weight_string+'_cutflow_'+c))

    p = Plot(list_of_cut_hist, in_file_path_names, name = 'cutflow' if output_name is None else output_name, y_log = True)
    p.drawBarChart(out_file_path, index_colors=True, parallel_bins=True)
        

