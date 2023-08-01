from HNL.Tools.helpers import isValidRootFile, rootFileContent, getObjFromFile, makeDirIfNeeded
from ROOT import TFile, TH2D
import numpy as np
from HNL.EventSelection.eventCategorization import CATEGORIES
from HNL.Samples.sample import Sample

class Cutter():

    def __init__(self, name = None, chain = None, categories = None, searchregions = None):
        self.name = name
        self.chain = chain
        self.categories = categories if categories != 'auto' else [c for c in CATEGORIES]
        self.searchregions = searchregions
        self.list_of_cuts = {}
        self.list_of_entries = {}
        self.order_of_cuts = []

    def addCut(self, cut_name):
        if cut_name not in self.list_of_cuts.keys():
            self.list_of_cuts[cut_name] = TH2D(cut_name, cut_name, len(self.categories), 0.5, len(self.categories)+0.5, len(self.searchregions), 0.5, len(self.searchregions)+0.5)
            self.list_of_entries[cut_name] = TH2D(cut_name+'_raw', cut_name+'_raw', len(self.categories), 0.5, len(self.categories)+0.5, len(self.searchregions), 0.5, len(self.searchregions)+0.5)
            self.list_of_cuts[cut_name].SetDirectory(0)
            self.list_of_entries[cut_name].SetDirectory(0)
            self.order_of_cuts.append(cut_name)

    def cut(self, passed, cut_name, weight = None):
        if weight is None:
            weight = self.chain.lumiweight if self.chain.lumiweight is not None else 1.
   
        self.addCut(cut_name)
        if passed:
            if self.chain.category is None:
                range_of_cat = [c for c in self.categories]
            else:
                range_of_cat = [self.chain.category]

            if self.chain.searchregion is None:
                range_of_sr = [s for s in self.searchregions]
            else:
                range_of_sr = [self.chain.searchregion]

            for c in range_of_cat:
                for s in range_of_sr:
                    self.list_of_cuts[cut_name].Fill(c, s, weight)
                    self.list_of_entries[cut_name].Fill(c, s, 1.)

            return True
    
        return False

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

        for cut in self.order_of_cuts:
            self.list_of_cuts[cut].Write()
        
        f.cd()
        f.mkdir('cutflow_raw')
        f.cd('cutflow_raw')

        if self.name:
            f.mkdir('cutflow_raw/'+self.name)
            f.cd('cutflow_raw/'+self.name)

        for cut in self.order_of_cuts:
            self.list_of_entries[cut].Write()
        
        f.Close()
        # t = TTree('cutflowtree', 'cutflowtree')
        # branches = [cut+'/F' for cut in self.order_of_cuts]
        # new_vars = makeBranches(t, branches)

        # Now rerun with real testArea
        if arg_string is not None:
            self.saveCutFlow(original_path, None)

       
class CutterCollection():

    def __init__(self, names, chain = None, categories = None, searchregions = None, function = None):
        self.names = names
        self.chain = chain
        self.function = function
        self.cutters = {}
        for name in self.names:
            self.cutters[name] = Cutter(name, chain, categories, searchregions)

    def cut(self, passed, cut_name, cutter_name = None):
        if cutter_name is None and self.function is not None:
            cutter_name = self.getCutterName()

        if cutter_name is not None:
            self.cutters[cutter_name].cut(passed, cut_name)
        else:
            for name in self.names:
                self.cutters[name].cut(passed, cut_name)
        return passed

    def saveCutFlow(self, out_file, arg_string = None):
        for name in self.names:
            self.cutters[name].saveCutFlow(out_file, arg_string)

    def getCutter(self, name):
        return self.cutters[name]

    def getCutterName(self):
        if self.function is None:
            return None
        elif self.function == 'sideband':
            if self.chain.is_sideband is None:
                return None
            elif self.chain.is_sideband:
                return 'sideband'
            else:
                return 'nominal'
        return None


class CutflowReader:
    
    def __init__(self, name, in_path, subdir = None):
        self.name = name

        self.list_of_cut_hist = {}
        self.list_of_entry_hist = {}
        self.cut_names = []

        in_file = TFile(in_path, 'read')
        subdir = 'cutflow' if subdir is None else 'cutflow/'+subdir
        key_names = [k[0] for k in rootFileContent(in_file, starting_dir = subdir)]
        in_file.Close() 

        for k in key_names:
            cut_name = k.split('/')[-1]
            self.list_of_cut_hist[cut_name] = getObjFromFile(in_path, k)
            self.list_of_entry_hist[cut_name] = getObjFromFile(in_path, k.replace('cutflow', 'cutflow_raw')+'_raw')
            self.cut_names.append(cut_name)

    @staticmethod
    def shouldMergeSingleList(lst):
        if len(lst) < 0:
            res = True
        res = all([ele == lst[0] for ele in lst])
        return not res

    @staticmethod
    def shouldMergeMatrix(matrix, axis):
        full_list = []
        if axis == 0:
            for i in xrange(len(matrix)):
                full_list.append(CutflowReader.shouldMergeSingleList(matrix[i]))
        else:
            for i in xrange(len(matrix[0])):
                full_list.append(CutflowReader.shouldMergeSingleList([x[i] for x in matrix]))

        return any(full_list)
            
        

    @staticmethod
    def mergeMatrix(matrix):
        merge_x = CutflowReader.shouldMergeMatrix(matrix, 0)
        merge_y = CutflowReader.shouldMergeMatrix(matrix, 1)
   
        if merge_x:
            if merge_y:
                return sum([sum(x) for x in matrix])
            else:
                return sum(matrix[0])

        else:
            if merge_y:
                return sum([x[0] for x in matrix])
            else:
                return matrix[0][0]

    def getNumber(self, hists, cut_name, categories = None, searchregions = None):
        if categories is None:
            categories = range(1, hists[cut_name].GetNbinsX()+1)
        if searchregions is None:
            searchregions = range(1, hists[cut_name].GetNbinsY()+1)

        from HNL.Plotting.plot import makeList
        categories = makeList(categories)
        searchregions = makeList(searchregions)

        list_of_yields = []
        for icat, cat in enumerate(categories):
            list_of_yields.append([])
            for sr in searchregions:
                list_of_yields[icat].append(hists[cut_name].GetBinContent(hists[cut_name].GetXaxis().FindBin(cat), hists[cut_name].GetYaxis().FindBin(sr)))

        return self.mergeMatrix(list_of_yields)

#    def getYield(self, cut_name, categories = None, searchregions = None):
#        if categories is None:
#            categories = range(1, self.list_of_cut_hist[cut_name].GetNbinsX()+1)
#        if searchregions is None:
#            searchregions = range(1, self.list_of_cut_hist[cut_name].GetNbinsY()+1)
#
#        from HNL.Plotting.plot import makeList
#        categories = makeList(categories)
#        searchregions = makeList(searchregions)
#
#        list_of_yields = []
#        for icat, cat in enumerate(categories):
#            list_of_yields.append([])
#            for sr in searchregions:
#                list_of_yields[icat].append(self.list_of_cut_hist[cut_name].GetBinContent(self.list_of_cut_hist[cut_name].GetXaxis().FindBin(cat), self.list_of_cut_hist[cut_name].GetYaxis().FindBin(sr)))
#
#        return self.mergeMatrix(list_of_yields)        

    def getYield(self, cut_name, categories = None, searchregions = None):
        return self.getNumber(self.list_of_cut_hist, cut_name, categories, searchregions)

    def getEntries(self, cut_name, categories = None, searchregions = None):
        return self.getNumber(self.list_of_entry_hist, cut_name, categories, searchregions)
        
    def returnCutFlow(self, categories = None, searchregions = None):
        out_lists = {'cuts' : [], 'values' : [], 'entries' : []}
        for cut_name in self.cut_names:
            out_lists['cuts'].append(cut_name)
            out_lists['values'].append(self.getYield(cut_name, categories, searchregions))
            out_lists['entries'].append(self.getEntries(cut_name, categories, searchregions))
        return out_lists
    
if __name__ == '__main__':
    in_path = '../../Analysis/data/runAnalysis/HNL/MVA-default-lowMassSRloose-reco/UL-2018/signal/HNL-mu-m30-Vsq1em4-prompt/variables.root'
    #in_path = '../../Analysis/data/runAnalysis/HNL/MVA-default-lowMassSRloose-reco/UL-2018/signal/HNL-mu-m30-Vsq2em6-displaced/variables.root'
    #in_path = '../../Analysis/data/runAnalysis/HNL-CutFlow/MVA-default-lowMassSRloose-reco/UL-2018/signal/HNL-mu-m30-Vsq2em6-displaced/variables.root'
    #in_path = '../../Analysis/data/runAnalysis/HNL-CutFlow/MVA-default-lowMassSRloose-reco/UL-2018/signal/HNL-mu-m30-Vsq1em4-prompt/variables.root'
    #in_path = '../../Analysis/data/testArea/runAnalysis/HNL/MVA-default-lowMassSRloose-reco/UL-2018/signal/HNL-mu-m30-Vsq1em4-prompt/tmp_HNL-mu-m30-Vsq1em4-prompt/HNL-mu-m30-Vsq1em4-prompt_variables_subJob0.root'
    #in_path = '../../Analysis/data/runAnalysis/HNL/MVA-default-lowMassSRlooseBeforeMZcut-reco/UL-2018/signal/HNL-mu-m30-Vsq1em4-prompt/variables.root'
    cfr = CutflowReader('HNL-e-m40-Vsq1em4-prompt', in_path, 'nominalnominal')
    print cfr.returnCutFlow(categories = [26, 33, 34, 35, 36, 37, 38])
#    for i in range(1, 17):
#        print cfr.returnCutFlow(searchregions = i)
