import ROOT
from HNL.Tools.helpers import makeDirIfNeeded, isValidRootFile

#
# Custom histogram class to set names and so on automatically and custom Fill functions
#

import numpy as np
class Histogram:
   
    #
    # Either make a histogram from scratch. In this case the args should be: name, var, var_tex and bins
    # bins only accepts np.arrays, otherwise weird things might happen
    # Or load in an existing histogram and make properties more accessible. I this case: args = hist
    #    
 
    def __init__(self, *args, **overflow):

        if len(args) == 1 and (isinstance(args[0], ROOT.TH1) or isinstance(args[0], ROOT.TH2)):
            self.hist = args[0]
            self.name = self.hist.GetName()
            self.var_tex = (self.hist.GetXaxis().GetTitle(), self.hist.GetYaxis().GetTitle())
            self.isTH2 = isinstance(self.hist, ROOT.TH2)
            self.var = None           #TODO: Is it possible to store the variable as well
            self.bins = None          #TODO: Read bins from axis and return  
        elif len(args) == 4:
            self.name = args[0]
            self.var = args[1]
            self.var_tex = args[2]
            self.bins = args[3]
            self.isTH2 = isinstance(self.bins, (tuple,))
            self.hist = None      

            if self.isTH2:
                self.hist = ROOT.TH2D(self.name, self.name, len(self.bins[0])-1, self.bins[0], len(self.bins[1])-1, self.bins[1])
                self.hist.Sumw2()
            else:
                self.hist = ROOT.TH1D(self.name, self.name, len(self.bins)-1, self.bins)
                self.hist.Sumw2()
            self.hist.SetXTitle(self.var_tex[0])
            self.hist.SetYTitle(self.var_tex[1])
        else:
            print "Incorrect input for Histogram"
            exit(0)
        
        try:
            self.overflow = overflow['overflow']
        except:
            self.overflow = True

    def fill1D(self, chain, weight, index = None):

        if self.var is None:
            print "\033[93m !Warning! \033[0m This histogram was loaded from a root file, the variable to fill is not known at the moment. Histogram will not be filled."
            return

        if index is not None:
            var = self.var(chain, index)
        else:
            var = self.var(chain)
        if self.overflow: xval = min(max(self.hist.GetXaxis().GetBinCenter(1), var), self.hist.GetXaxis().GetBinCenter(self.hist.GetXaxis().GetLast()))
        else: xval = var
        self.hist.Fill(xval, weight)

    def fill2D(self, chain, weight):
        if self.var is None:
            print "\033[93m !Warning! \033[0m This histogram was loaded from a root file, the variable to fill is not known at the moment. Histogram will not be filled."
            return

        if self.overflow:
            xval = min(max(self.hist.GetXaxis().GetBinCenter(1), self.var(chain)[0]), self.hist.GetXaxis().GetBinCenter(self.hist.GetXaxis().GetLast()))
            yval = min(max(self.hist.GetYaxis().GetBinCenter(1), self.var(chain)[1]), self.hist.GetYaxis().GetBinCenter(self.hist.GetYaxis().GetLast()))
        else:
            xval = self.var(chain)[0]
            yval = self.var(chain)[1]

        self.hist.Fill(xval, yval, weight)

    def fill(self, chain, weight, index = None):
        if self.var is None:
            print "\033[93m !Warning! \033[0m This histogram was loaded from a root file, the variable to fill is not known at the moment. Histogram will not be filled."
            return

        if self.isTH2:
            self.fill2D(chain, weight)
        else:
            self.fill1D(chain, weight, index)

    def getXTitle(self):
        return self.var_tex[0]
    
    def getYTitle(self):
        return self.var_tex[1]

    def getHist(self):
        return self.hist

    def write(self, path, append = False):
        append_string = 'recreate'
        if append and isValidRootFile(path): append_string = 'update'

        makeDirIfNeeded(path)
        output_file = ROOT.TFile(path, append_string)
        output_file.mkdir(self.name)
        output_file.cd(self.name)
        self.hist.Write()
        output_file.Close()

def returnSqrt(th1):
    sqrt = th1.Clone('sqrt')
    for xbin in xrange(1, th1.GetSize()-1):                     #GetSize returns nbins + 2 (for overflow and underflow bin)
        if th1.GetBinContent(xbin) <= 0:
            sqrt_x = 0
            sqrt.SetBinError(xbin, 0)
        else:
            sqrt_x = np.sqrt(th1.GetBinContent(xbin))
            sqrt.SetBinError(xbin, 0.5*th1.GetBinError(xbin)/sqrt_x)
        sqrt.SetBinContent(xbin, sqrt_x)
    return sqrt
