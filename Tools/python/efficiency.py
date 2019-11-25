import ROOT
import numpy as np
import HNL.Samples.sample
from HNL.Tools.helpers import makeDirIfNeeded, getObjFromFile, isValidRootFile
from HNL.Tools.histogram import Histogram

class Efficiency(object):

    def __init__(self, name, var, var_tex, path, bins=None, subdir = None):      
        self.name = name
        self.path = path
        self.var = var
        self.var_tex = var_tex
        self.bins = bins
        self.efficiency_num = None
        self.efficiency_denom = None

        #If bins == None, load in histograms from the path
        bins_check = False
        try:
            if bins:    bins_check=True
        except:
            if bins.any():      bins_check=True
       
        if bins_check:
            self.efficiency_num = Histogram(name+'_num', self.var, var_tex, bins)
            self.efficiency_denom = Histogram(name+'_denom', self.var, var_tex, bins)
        else:
            if subdir: name = subdir 
            else: name = ''
            self.efficiency_num = getObjFromFile(self.path, name+'/'+name+'_num')
            self.efficiency_denom = getObjFromFile(self.path, name+'/'+name+'_denom')
        
        self.isTH2 = self.efficiency_num.isTH2
        if self.isTH2 and not self.efficiency_denom.isTH2:  print "Warning: efficiency numerator and denominator have different dimensions"

    def fill(self, chain, weight, passed, index = None):
        self.efficiency_denom.fill(chain, weight, index)
        if passed:      self.efficiency_num.fill(chain, weight, index)
 
    def getNumerator(self):
        num = self.efficiency_num.getHist().Clone()
        return num

    def getDenominator(self):
        return self.efficiency_denom.getHist().Clone()

    def getEfficiency(self, inPercent = False):
        eff = self.getNumerator().Clone(self.name+'_efficiency')
        eff.Divide(self.getDenominator())
        if inPercent: eff.Scale(100.)
        return eff

    def write(self, append = False):
        append_string = 'recreate'
        if append and isValidRootFile(self.path): append_string = 'update'

        makeDirIfNeeded(self.path)
        output_file = ROOT.TFile(self.path, append_string)
        output_file.mkdir(self.name)
        output_file.cd(self.name)
        self.efficiency_num.getHist().Write()
        self.efficiency_denom.getHist().Write()
        self.getEfficiency().Write()
        output_file.Close()

