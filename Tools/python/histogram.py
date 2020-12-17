import ROOT
from HNL.Tools.helpers import makeDirIfNeeded, isValidRootFile
import os

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

    def fill2D(self, chain, weight, index = None):
        if self.var is None:
            print "\033[93m !Warning! \033[0m This histogram was loaded from a root file, the variable to fill is not known at the moment. Histogram will not be filled."
            return

        if index is not None:
            var = self.var(chain, index)
        else:
            var = self.var(chain)

        if self.overflow:
            xval = min(max(self.hist.GetXaxis().GetBinCenter(1), var[0]), self.hist.GetXaxis().GetBinCenter(self.hist.GetXaxis().GetLast()))
            yval = min(max(self.hist.GetYaxis().GetBinCenter(1), var[1]), self.hist.GetYaxis().GetBinCenter(self.hist.GetYaxis().GetLast()))
        else:
            xval = var[0]
            yval = var[1]

        self.hist.Fill(xval, yval, weight)

    def fill(self, chain, weight, index = None):
        if self.var is None:
            print "\033[93m !Warning! \033[0m This histogram was loaded from a root file, the variable to fill is not known at the moment. Histogram will not be filled."
            return

        if self.isTH2:
            self.fill2D(chain, weight, index)
        else:
            self.fill1D(chain, weight, index)

    def getXTitle(self):
        return self.var_tex[0]
    
    def getYTitle(self):
        return self.var_tex[1]

    def getHist(self):
        return self.hist

    def write(self, path, subdirs=None, write_name = None, append = False, is_test=False):
        append_string = 'recreate'
        if append and isValidRootFile(path): append_string = 'update'

        if not is_test:
            path_to_use = path
        else:
            split_path = path.split('/')
            index_to_use = split_path.index('testArea')+1
            path_to_use = os.path.expandvars("$HOME/Testing/Latest/"+'/'.join(split_path[index_to_use:]))

        makeDirIfNeeded(path_to_use)
        output_file = ROOT.TFile(path_to_use, append_string)
        if subdirs is None:
            output_file.mkdir(self.name)
            output_file.cd(self.name)
        else:
            nomo = ''
            for d in subdirs:
                nomo += d + '/'
                output_file.mkdir(nomo)
                output_file.cd(nomo)

        if write_name is None:
            self.hist.Write(self.name)
        else:
            self.hist.Write()
        output_file.Close()

        if is_test:
            self.write(path, write_name=write_name, subdirs=subdirs, append=append, is_test=False)

    def clone(self, out_name):
        hist_clone = self.hist.Clone(out_name)
        return Histogram(hist_clone)

    def divide(self, other_histogram):
        self.hist.Divide(other_histogram.getHist())

    def add(self, other_histogram):
        self.hist.Add(other_histogram.getHist())

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

#Class for histograms with similar properties:
#   var, bins and dimensions

from HNL.Tools.helpers import getObjFromFile
class HistogramCollection(object):
    def __init__(self, collection_name, sub_names, var, var_tex, path, bins=None, subdirs=None):
        self.collection_name = collection_name
        self.sub_names = sub_names
        self.path = path
        self.var = var
        self.var_tex = var_tex
        self.bins = bins
        self.subdirs = subdirs
        self.histograms = {}

        #If bins == None, load in histograms from the path
        bins_check = False
        try:
            if bins:    bins_check = True
        except:
            if bins.any():      bins_check = True
       
        if bins_check:
            for n in self.sub_names:
                self.histograms[n] = Histogram(self.collection_name+'_'+n, self.var, self.var_tex, self.bins)
        else:
            if subdirs is not None:
                obj_name = ''
                for d in subdirs:
                    obj_name += d+'/'
            else:
                obj_name = self.collection_name + '/'
            for n in self.sub_names:
                self.histograms[n] = Histogram(getObjFromFile(self.path, obj_name+self.collection_name+'_'+n))
     
        self.isTH2 = self.histograms[self.sub_names[0]].isTH2
        for n in self.sub_names[1:]:
            if self.isTH2 and not self.histograms[n].isTH2:  raise RuntimeError("histograms in HistogramCollection object have different dimensions")

    def fill(self, sub_name, chain, weight, index = None):
        self.histograms[sub_name].fill(chain, weight, index)

    def getHistogram(self, sub_name):
        h = self.histograms[sub_name].getHist().Clone()
        return h

    def write(self, append = False, name=None, subdirs = None, is_test=False):
        append_string = 'recreate'
        if append and isValidRootFile(self.path): append_string = 'update'

        if not is_test:
            path_to_use = self.path
        else:
            path_to_use = "~/Testing/Latest/"+os.path.join(self.path.split('/')[self.path.index('testArea'):])

        makeDirIfNeeded(path_to_use)
        output_file = ROOT.TFile(path_to_use, append_string)
        if subdirs is None:
            output_file.mkdir(self.collection_name)
            output_file.cd(self.collection_name)
        else:
            nomo = ''
            for d in subdirs:
                nomo += d + '/'
                output_file.mkdir(nomo)
                output_file.cd(nomo)
        if name is not None:
            for n in self.sub_names:
                self.histograms[n].getHist().Write(name+'_'+n)
        else:
            for n in self.sub_names:
                self.histograms[n].getHist().Write()
        output_file.Close()

        if is_test:
            self.write(append=append, name=name, subdirs=subdirs, is_test=False)


