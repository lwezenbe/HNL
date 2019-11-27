from ROOT import TFile, TGraphErrors
from helpers import makeDirIfNeeded, getObjFromFile, isValidRootFile
import numpy as np
from HNL.Tools.histogram import Histogram

class ROC:
    def __init__(self, name, var, var_tex, path, bins=None, misid_path = None):
        self.name = name
        self.path = path
        self.var = var
        self.var_tex = var_tex
        self.bins = bins
        self.eff_numerator = None
        self.eff_denominator = None
        self.misid_numerator = None
        self.misid_denominator = None
 
        if self.bins is not None: 
            self.eff_numerator = Histogram(name + '_eff_numerator', self.var, self.var_tex, self.bins)
            self.misid_numerator = Histogram(name + '_misid_numerator', self.var, self.var_tex, self.bins)
            self.eff_denominator = Histogram(name + '_eff_denominator', self.var, self.var_tex, self.bins)
            self.misid_denominator = Histogram(name + '_misid_denominator', self.var, self.var_tex, self.bins)
            
        else:
            self.eff_numerator = Histogram(getObjFromFile(self.path, name+'/'+name + '_eff_numerator'))
            self.eff_denominator = Histogram(getObjFromFile(self.path, name+'/'+name + '_eff_denominator'))

            #Use different file for misid in case you split the jobs for signal and bkgr up
            tmp_path = misid_path if misid_path is not None else self.path
            self.misid_numerator = Histogram(getObjFromFile(tmp_path, name+'/'+name + '_misid_numerator'))
            self.misid_denominator = Histogram(getObjFromFile(tmp_path, name+'/'+name + '_misid_denominator'))
    
        print self.eff_numerator.getHist().GetSumOfWeights()
        print self.eff_denominator.getHist().GetSumOfWeights()
        print self.misid_numerator.getHist().GetSumOfWeights()
        print self.misid_denominator.getHist().GetSumOfWeights()
 
            

    def fillEfficiency(self, chain, index, passed, weight=1.):
        self.eff_denominator.fill(chain, weight, index)
        if passed: self.eff_numerator.fill(chain, weight, index)
    
    def fillMisid(self, chain, index, passed, weight=1.):
        self.misid_denominator.fill(chain, weight, index)
        if passed: self.misid_numerator.fill(chain, weight, index)
        
    def loadEfficiency(self, name, path):
        self.eff_numerator = getObjFromFile(path, name + '_eff_numerator')
        self.eff_denominator = getObjFromFile(path, name + '_eff_denominator')
    
    def loadMisid(self, name, path):
        self.misid_numerator = getObjFromFile(path, name + '_misid_numerator')
        self.misid_denominator = getObjFromFile(path, name + '_misid_denominator')

    def write(self, append = False):
        append_string = 'recreate'
        if append and isValidRootFile(self.path): append_string = 'update'

        makeDirIfNeeded(self.path)
        output_file = TFile(self.path, append_string)
        output_file.mkdir(self.name)
        output_file.cd(self.name)
       
        self.eff_numerator.getHist().Write()
        self.eff_denominator.getHist().Write()
        self.misid_numerator.getHist().Write()
        self.misid_denominator.getHist().Write()
        output_file.Close()

    def getEfficiency(self):
        eff = self.eff_numerator.getHist().Clone('efficiency')
        eff.Divide(self.eff_denominator.getHist()) #Wghat about errors?
#        eff.Scale(100.)
        
        return eff
    
    def getMisid(self):
        eff = self.misid_numerator.getHist().Clone('misid')
        eff.Divide(self.misid_denominator.getHist())
        return eff

    @staticmethod
    def bincontentToArray(h):
        arr = np.array([])
        for b in xrange(h.GetXaxis().GetNbins()):
            arr = np.append(arr, h.GetBinContent(b+1))
        return arr
        
    @staticmethod
    def binerrorToArray(h):
        arr = np.array([])
        for b in xrange(h.GetXaxis().GetNbins()):
            arr = np.append(arr, h.GetBinError(b+1))
        return arr

    def returnGraph(self):
        eff = self.getEfficiency()
        fr = self.getMisid()
        
        xval = self.bincontentToArray(eff).flatten('C')
        yval = self.bincontentToArray(fr).flatten('C')
        xerr = self.binerrorToArray(eff).flatten('C')
        yerr = self.binerrorToArray(fr).flatten('C')

        print xval
        graph = TGraphErrors(len(xval), xval, yval, xerr, yerr)
        return graph

if __name__ == '__main__':
    roc = ROC('x', ['x', 'y', 'z'])
