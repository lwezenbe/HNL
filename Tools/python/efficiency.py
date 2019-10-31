import ROOT
import numpy as np
import HNL.Samples.sample
from HNL.Tools.helpers import makeDirIfNeeded, getObjFromFile, isValidRootFile

class efficiency(object):

    def __init__(self, name, path, bins=None, subdir = None):      
        self.name = name
        self.path = path
        self.bins = bins
        self.efficiency_num = None
        self.efficiency_denom = None
        self.isTH2 = False

        #If bins == None, load in histograms from the path
        bins_check = False
        try:
            if bins:    bins_check=True
        except:
            if bins.any():      bins_check=True
        
        if bins_check:
            if isinstance(bins[0], (list,)) or isinstance(bins[0], np.ndarray): 
                self.efficiency_num = ROOT.TH2D(name+'_num', name+'_num', len(bins[0])-1, bins[0], len(bins[1])-1, bins[1])
                self.efficiency_denom = ROOT.TH2D(name+'_denom', name+'_denom', len(bins[0])-1, bins[0], len(bins[1])-1, bins[1])
            elif isinstance(bins[0], int) or isinstance(bins[0], float) or isinstance(bins[0], np.int64) or isinstance(bins[0], np.float64):
                self.efficiency_num = ROOT.TH1D(name+'_num', name+'_num', len(bins)-1, bins)
                self.efficiency_denom = ROOT.TH1D(name+'_denom', name+'_denom', len(bins)-1, bins)
            self.efficiency_num.Sumw2()
            self.efficiency_denom.Sumw2()
        else:
            if subdir: name = subdir 
            else: name = ''
            self.efficiency_num = getObjFromFile(self.path, name+'/'+name+'_num')
            self.efficiency_denom = getObjFromFile(self.path, name+'/'+name+'_denom')

        if isinstance(self.efficiency_num, ROOT.TH2D):   self.isTH2 = True
        if self.isTH2 and not isinstance(self.efficiency_denom, ROOT.TH2D):  print "Warning: efficiency numerator and denominator have different dimensions"

    def fillNumerator1D(self, xval, weight):
        xval = min(max(self.efficiency_num.GetXaxis().GetBinCenter(1), xval), self.efficiency_num.GetXaxis().GetBinCenter(self.efficiency_num.GetXaxis().GetLast()))
        self.efficiency_num.Fill(xval, weight)
        
    def fillNumerator2D(self, xval, yval, weight):
        xval = min(max(self.efficiency_num.GetXaxis().GetBinCenter(1), xval), self.efficiency_num.GetXaxis().GetBinCenter(self.efficiency_num.GetXaxis().GetLast()))
        yval = min(max(self.efficiency_num.GetYaxis().GetBinCenter(1), yval), self.efficiency_num.GetYaxis().GetBinCenter(self.efficiency_num.GetYaxis().GetLast()))
        self.efficiency_num.Fill(xval, yval, weight)

    def fillNumerator(self, *val, **w):
        if len(w) == 1 and 'w' in w.keys():
            weight = w['w']
        else:
            weight = 1.

        if self.isTH2:
            if len(val) != 2:
                print "Warning. The number of values that can be entered into the histogram: 2"
                print "         The number of values you entered:", len(val)
                print "         Histogram not filled"
                return
            else:
                self.fillNumerator2D(val[0], val[1], weight)
        else:
            if len(val) != 1:
                print "Warning. The number of values that can be entered into the histogram: 1"
                print "         The number of values you entered:", len(val)
                print "         Histogram not filled"
                return
            else:
                self.fillNumerator1D(val[0], weight)

    def fillDenominator1D(self, xval, weight):
        xval = min(max(self.efficiency_denom.GetXaxis().GetBinCenter(1), xval), self.efficiency_denom.GetXaxis().GetBinCenter(self.efficiency_denom.GetXaxis().GetLast()))
        self.efficiency_denom.Fill(xval, weight)
        
    def fillDenominator2D(self, xval, yval, weight):
        xval = min(max(self.efficiency_denom.GetXaxis().GetBinCenter(1), xval), self.efficiency_denom.GetXaxis().GetBinCenter(self.efficiency_denom.GetXaxis().GetLast()))
        yval = min(max(self.efficiency_denom.GetYaxis().GetBinCenter(1), yval), self.efficiency_denom.GetYaxis().GetBinCenter(self.efficiency_denom.GetYaxis().GetLast()))
        self.efficiency_denom.Fill(xval, yval, weight)

    def fillDenominator(self, *val, **w):
        if len(w) == 1 and 'w' in w.keys():
            weight = w['w']
        else:
            weight = 1.

        if self.isTH2:
            if len(val) != 2:
                print "Warning. The number of values that can be entered into the histogram: 2"
                print "         The number of values you entered:", len(val)
                print "         Histogram not filled"
                return
            else:
                self.fillDenominator2D(val[0], val[1], weight)
        else:
            if len(val) != 1:
                print "Warning. The number of values that can be entered into the histogram: 1"
                print "         The number of values you entered:", len(val)
                print "         Histogram not filled"
                return
            else:
                self.fillDenominator1D(val[0], weight)

    def getNumerator(self):
        num = self.efficiency_num.Clone()
        return num

    def getDenominator(self):
        return self.efficiency_denom.Clone()

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
        self.efficiency_num.Write()
        self.efficiency_denom.Write()
        self.getEfficiency().Write()
        output_file.Close()

