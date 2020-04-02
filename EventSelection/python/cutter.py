from HNL.Tools.helpers import isValidRootFile, rootFileContent, getObjFromFile
from ROOT import TFile, TH1F
from HNL.Tools.makeBranches import makeBranches

class Cutter():

    def __init__(self, name = None, chain = None):
        self.name = name
        self.chain = chain
        self.list_of_cuts = {'total' : TH1F('total', 'total', 1, 0, 1)}
        self.order_of_cuts = ['total']

    def cut(self, passed, cut_name):

        if cut_name not in self.list_of_cuts.keys():
            self.list_of_cuts[cut_name] = TH1F(cut_name, cut_name, 1, 0, 1)
            self.order_of_cuts.append(cut_name)
        if passed:
            if self.chain is not None:
                try:
                    weight = self.chain.weight
                except:
                    weight = 1.
            else:
                weight = 1.
            self.list_of_cuts[cut_name].Fill(.5, weight)
            return True
        return False
    
    def printAllCuts(self):
        return self.order_of_cuts

    def printAllEvents(self):
        return [(cut, self.list_of_cuts[cut]) for cut in order_of_cuts]

    def saveCutFlow(self, out_file):

        if isValidRootFile(out_file):
            f = TFile(out_file, 'update')
        else:
            f = TFile(out_file, 'recreate')
        
        f.mkdir('cutflow')
        f.cd('cutflow')

        if self.name:
            f.mkdir(self.name)
            f.cd(self.name)

        for cut in self.order_of_cuts:
            self.list_of_cuts[cut].Write()
        
        f.Close()
        # t = TTree('cutflowtree', 'cutflowtree')
        # branches = [cut+'/F' for cut in self.order_of_cuts]
        # new_vars = makeBranches(t, branches)

from HNL.Plotting.plot import makeList
def printCutFlow(in_file_paths, out_file_path, in_file_path_names):
    print in_file_path_names
    in_file_paths = makeList(in_file_paths)
    in_file_path_names = makeList(in_file_path_names)
    if len(in_file_paths) != len(in_file_path_names):
        print 'inconsistent file paths and names'
        exit(0)

    list_of_cut_values = {}
    for ifp, ifpn in zip(in_file_paths, in_file_path_names):
        in_file = TFile(ifp)
        key_names = [k[0] for k in rootFileContent(in_file, '/', starting_dir = 'cutflow')]
        in_file.Close()
        list_of_cut_values[ifpn] = {}
        for k in key_names:
            list_of_cut_values[ifpn][k] = getObjFromFile(ifp, 'cutflow/'+k).GetSumOfWeights()

    out_file = open(out_file_path, 'w')
    out_file.write(' \t \t ' + '\t'.join(in_file_path_names) + '\n')
    for k in key_names:
        out_file.write(k.split('/')[-1] +'\t \t ' + '\t'.join([str(list_of_cut_values[n][k]) for n in in_file_path_names]) + '\n')
    # out_file.write('NAME \t \t \t ' + '\t'.join([k.split('/')[-1] for k in key_names]) + '\n')
    # for n in in_file_path_names:
    #     out_file.write(n +'\t \t \t ' + '\t'.join([str(list_of_cut_values[n][k]) for k in key_names]) + '\n')
    out_file.close()

from HNL.Plotting.plot import Plot
def plotCutFlow(in_file_paths, out_file_path, in_file_path_names):
    in_file_paths = makeList(in_file_paths)
    in_file_path_names = makeList(in_file_path_names)
    if len(in_file_paths) != len(in_file_path_names):
        print 'inconsistent file paths and names'
        exit(0)

    list_of_cut_hist = []
    tex_names = []
    x_name = []
    #If one input file, plot keys on x
    if len(in_file_paths) == 1:
        in_file = TFile(ifp)
        key_names = [k[0] for k in rootFileContent(rf, 'cutflow')]
        in_file.Close()
        list_of_cut_hist.append(ROOT.TH1D('cutflow', 'cutflow', len(key_names), 0, len(key_names)))
        for i, k in enumerate(key_names):
            list_of_cut_hist[0].SetBinContent(i+1, getObjFromFile(ifp, 'cutflow/'+k).GetSumOfWeights())
        tex_names = in_file_path_names
        x_name = key_names
    #Plot samples on x
    else:
        in_file = TFile(ifp[0])
        key_names = [k[0] for k in rootFileContent(rf, 'cutflow')]
        in_file.Close()
        for j, k in enumerate(key_names):
            list_of_cut_hist.append(ROOT.TH1D('cutflow_'+k, 'cutflow_'+k, len(key_names), 0, len(key_names)))
            for i, (ifp, infp) in enumerate(zip(in_file_paths, in_file_path_names)):
                list_of_cut_hist[j].SetBinContent(i+1, getObjFromFile(ifp, 'cutflow/'+k).GetSumOfWeights())
        tex_names = in_file_path_names

    p = Plot(list_of_cut_hist, tex_names, x_name = x_name)
    p.drawBarChart(out_file_path, parallel_bins = len(in_file_paths) != 1)
        

