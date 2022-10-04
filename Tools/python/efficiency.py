import ROOT
import os
from HNL.Tools.helpers import makeDirIfNeeded, getObjFromFile, isValidRootFile
from HNL.Tools.histogram import Histogram

class Efficiency(object):

    def __init__(self, name, var, var_tex, path=None, bins=None, subdirs=None, efficiency_num = None, efficiency_denom = None):      
        self.name = name
        self.path = path
        self.var = var
        self.var_tex = var_tex
        self.bins = bins
        self.subdirs = subdirs
        self.efficiency_num = efficiency_num
        self.efficiency_denom = efficiency_denom
        self.efficiency = None

        #If bins == None, load in histograms from the path
        bins_check = False
        try:
            if bins:    bins_check = True
        except:
            if bins.any():      bins_check = True
     
        if bins_check:
            self.efficiency_num = Histogram(name+'_num', self.var, var_tex, bins)
            self.efficiency_denom = Histogram(name+'_denom', self.var, var_tex, bins)
        else:
            obj_name = ''
            if subdirs is not None:
                for d in subdirs:
                    obj_name += d+'/'
            if (self.efficiency_num is None or self.efficiency_denom is None) and self.path is not None:
                self.efficiency_num = Histogram(getObjFromFile(self.path, obj_name+self.name+'_num'))
                self.efficiency_denom = Histogram(getObjFromFile(self.path, obj_name+self.name+'_denom'))
            else:
                self.efficiency_num = Histogram(self.efficiency_num)
                self.efficiency_denom = Histogram(self.efficiency_denom)
     
        self.isTH2 = self.efficiency_num.isTH2
        self.isTH3 = self.efficiency_num.isTH3
        if self.isTH2 and not self.efficiency_denom.isTH2:  print "Warning: efficiency numerator and denominator have different dimensions"
        if self.isTH3 and not self.efficiency_denom.isTH3:  print "Warning: efficiency numerator and denominator have different dimensions"

    def isVarCorrectSize(self):
        if self.isTH2: return (isinstance(self.var, (list,)) and len(self.var) == 2)
        elif self.isTH3: return (isinstance(self.var, (list,)) and len(self.var) == 3)
        else: return (not isinstance(self.var, (list,)))

    def fill(self, chain, weight, passed, index = None):
        self.efficiency_denom.fill(chain, weight, index)
        if passed:      self.efficiency_num.fill(chain, weight, index)
 
    def getNumerator(self):
        num = self.efficiency_num.getHist().Clone()
        return num

    def getDenominator(self):
        return self.efficiency_denom.getHist().Clone()

    def getEfficiency(self, inPercent = False, hist_object=False):
        if self.efficiency is None:
            eff = self.getNumerator().Clone('tmp_'+self.name)
            eff.Divide(eff, self.getDenominator(), 1., 1., "B")
            if inPercent: eff.Scale(100.)
            if hist_object:
                self.efficiency = Histogram(eff.Clone(self.name+'_efficiency'))
            else:
                self.efficiency = eff.Clone(self.name+'_efficiency')

        #
        # Check if physics makes sense
        #
        if not hist_object:
            for b in range(1, self.efficiency.GetNcells()+1):
                if self.efficiency.GetBinContent(b) < 0.:
                    print "efficiency has negative value {0} in bin number {1}. Setting to 0.".format(self.efficiency.GetBinContent(b), b)
                    self.efficiency.SetBinContent(b, 0.)
                if self.efficiency.GetBinContent(b) > 1.:
                    print "efficiency has value larger than one: {0} in bin number {1}. This is probably due to negative weights in denominator that dont pass to the numerator but you should check this. Setting to 1.".format(self.efficiency.GetBinContent(b), b)
                    self.efficiency.SetBinContent(b, 1.)
        else:
            print "There is a chance you will get unphysical values, we could not check it at this time"

        return self.efficiency

    def evaluateEfficiency(self, chain, index = None, manual_var_entry = None):
        if self.var is None and manual_var_entry is None:
            raise RuntimeError('Member "var" in efficiency is None. Either set it or provide the input var manually')

        if index is not None:
            var = self.var(chain, index) if manual_var_entry is None else manual_var_entry
        else:
            var = self.var(chain) if manual_var_entry is None else manual_var_entry

        #Take into account overflow
        if self.isTH2:
            var[0] = min(max(self.getEfficiency().GetXaxis().GetBinCenter(1), var[0]), self.getEfficiency().GetXaxis().GetBinCenter(self.getEfficiency().GetXaxis().GetLast()))
            var[1] = min(max(self.getEfficiency().GetYaxis().GetBinCenter(1), var[1]), self.getEfficiency().GetYaxis().GetBinCenter(self.getEfficiency().GetYaxis().GetLast()))  
        elif self.isTH3:
            var[0] = min(max(self.getEfficiency().GetXaxis().GetBinCenter(1), var[0]), self.getEfficiency().GetXaxis().GetBinCenter(self.getEfficiency().GetXaxis().GetLast()))
            var[1] = min(max(self.getEfficiency().GetYaxis().GetBinCenter(1), var[1]), self.getEfficiency().GetYaxis().GetBinCenter(self.getEfficiency().GetYaxis().GetLast()))  
            var[2] = min(max(self.getEfficiency().GetZaxis().GetBinCenter(1), var[2]), self.getEfficiency().GetZaxis().GetBinCenter(self.getEfficiency().GetZaxis().GetLast()))  
        else:
            var = min(max(self.getEfficiency().GetXaxis().GetBinCenter(1), var), self.getEfficiency().GetXaxis().GetBinCenter(self.getEfficiency().GetXaxis().GetLast()))
 
        if self.isTH2:
            bin_to_read = self.getEfficiency().FindBin(var[0], var[1])
        elif self.isTH3:
            bin_to_read = self.getEfficiency().FindBin(var[0], var[1], var[2])
        else:
            bin_to_read = self.getEfficiency().FindBin(var)

        return self.getEfficiency().GetBinContent(bin_to_read)
    
    def getGraph(self):
        eff = self.getEfficiency()
        graph = ROOT.TGraphAsymmErrors(eff)
        y_values = [y for y in graph.GetY()] 
        for i in xrange(eff.GetNbinsX()):
            err_up = graph.GetErrorYhigh(i)
            val_y = y_values[i]
            if val_y + err_up > 1.:
                graph.SetPointEYhigh(i, 1.-val_y)
       
        graph.SetTitle(eff.GetName()+ ';' + eff.GetXaxis().GetTitle()+';'+eff.GetYaxis().GetTitle()) 
        return graph

    def clone(self, out_name='clone'):
        new_num = self.efficiency_num.clone(out_name)
        new_denom = self.efficiency_denom.clone(out_name)
        new_eff = Efficiency(self.name, self.var, self.var_tex, self.path, self.bins, self.subdirs)
        new_eff.efficiency_num = new_num
        new_eff.efficiency_denom = new_denom
        return new_eff

    #
    # Efficiency objects just use num and denom, so we can just add those of different objects together
    # and getEfficiency should still be correct
    #
    def add(self, other_efficiency):
        self.efficiency_num.add(other_efficiency.efficiency_num)
        self.efficiency_denom.add(other_efficiency.efficiency_denom)
        return

    #
    # Efficiency objects just use num and denom, so we can just add those of different objects together
    # and getEfficiency should still be correct
    #
    def addNumeratorOnly(self, other_efficiency):
        self.efficiency_num.add(other_efficiency.efficiency_num)
        return
    

    def write(self, append = False, name=None, is_test=None):
        append_string = 'recreate'
        if self.path is None: raise RuntimeError('No path defined for storage of efficiency')
        if append and isValidRootFile(self.path): append_string = 'update'


        if is_test is None:
            path_to_use = self.path
        else:
            split_path = self.path.split('/')
            index_to_use = split_path.index('testArea')+1
            #
            # Have to hardcode because $HOME doesnt work on t2b condor
            #
            # path_to_use = os.path.expandvars("$HOME/Testing/Latest/"+'/'.join(split_path[index_to_use:-1])+'/'+is_test+'/'+split_path[-1])
            path_to_use = os.path.expandvars("/storage_mnt/storage/user/lwezenbe/Testing/Latest/"+'/'.join(split_path[index_to_use:-1])+'/'+is_test+'/'+split_path[-1])

        makeDirIfNeeded(path_to_use)
        output_file = ROOT.TFile(path_to_use, append_string)
        if self.subdirs is None:
            pass
            # output_file.mkdir(self.name)
            # output_file.cd(self.name)
        else:
            nomo = ''
            for d in self.subdirs:
                nomo += d + '/'
                output_file.mkdir(nomo)
                output_file.cd(nomo)
        if name is not None:
            self.efficiency_num.getHist().Write(name+'_num')
            self.efficiency_denom.getHist().Write(name+'_denom')
            # self.getEfficiency().Write(name+'_efficiency')
        else:
            self.efficiency_num.getHist().Write(self.name+'_num')
            self.efficiency_denom.getHist().Write(self.name+'_denom')
            # self.getEfficiency().Write()
        output_file.Close()

        if is_test is not None:
            self.write(append=append, name=name, is_test=None)
