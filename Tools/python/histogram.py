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
            self.isTH3 = isinstance(self.hist, ROOT.TH3)
            self.var = None           #TODO: Is it possible to store the variable as well
            self.bins = None          #TODO: Read bins from axis and return  

            bins_x = np.array([self.hist.GetXaxis().GetBinLowEdge(b) for b in xrange(1, self.hist.GetXaxis().GetNbins()+1)]+[self.hist.GetXaxis().GetBinUpEdge(self.hist.GetXaxis().GetLast())])
            if not self.isTH2 and not self.isTH3:
                self.bins = bins_x
            elif self.isTH2:
                bins_y = np.array([self.hist.GetYaxis().GetBinLowEdge(b) for b in xrange(1, self.hist.GetYaxis().GetNbins()+1)]+[self.hist.GetYaxis().GetBinUpEdge(self.hist.GetYaxis().GetLast())])
                self.bins = (bins_x, bins_y)
            elif self.isTH3:
                bins_y = np.array([self.hist.GetYaxis().GetBinLowEdge(b) for b in xrange(1, self.hist.GetYaxis().GetNbins()+1)]+[self.hist.GetYaxis().GetBinUpEdge(self.hist.GetYaxis().GetLast())])
                bins_z = np.array([self.hist.GetZaxis().GetBinLowEdge(b) for b in xrange(1, self.hist.GetZaxis().GetNbins()+1)]+[self.hist.GetZaxis().GetBinUpEdge(self.hist.GetZaxis().GetLast())])
                self.bins = (bins_x, bins_y, bins_z)

        elif len(args) == 4:
            self.name = args[0]
            self.var = args[1]
            self.var_tex = args[2]
            self.bins = args[3]
            self.isTH2 = isinstance(self.bins, (tuple,)) and len(self.bins) == 2
            self.isTH3 = isinstance(self.bins, (tuple,)) and len(self.bins) == 3
            self.hist = None      

            if self.isTH2:
                self.hist = ROOT.TH2D(self.name, self.name, len(self.bins[0])-1, self.bins[0], len(self.bins[1])-1, self.bins[1])
            elif self.isTH3:
                self.hist = ROOT.TH3D(self.name, self.name, len(self.bins[0])-1, self.bins[0], len(self.bins[1])-1, self.bins[1], len(self.bins[2])-1, self.bins[2])
            else:
                self.hist = ROOT.TH1D(self.name, self.name, len(self.bins)-1, self.bins)
            self.hist.Sumw2()
            try:
                self.hist.SetXTitle(self.var_tex[0])
                self.hist.SetYTitle(self.var_tex[1])
            except:
                pass
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

    def fill3D(self, chain, weight, index = None):
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
            zval = min(max(self.hist.GetZaxis().GetBinCenter(1), var[2]), self.hist.GetZaxis().GetBinCenter(self.hist.GetZaxis().GetLast()))
        else:
            xval = var[0]
            yval = var[1]
            zval = var[2]

        self.hist.Fill(xval, yval, zval, weight)

    def slice3DalongZ(self):
        sliced_hist = {}
        for i_n, n in enumerate(self.bins[2]):
            if i_n == len(self.bins[2])-1: continue
            out_name = str(n)+'to'+str(self.bins[2][i_n + 1])
            sliced_hist[out_name] = ROOT.TH2D(self.name+'-2D', self.name+'-2D', len(self.bins[0])-1, self.bins[0], len(self.bins[1])-1, self.bins[1])
            sliced_hist[out_name].SetXTitle(self.var_tex[0])
            sliced_hist[out_name].SetYTitle(self.var_tex[1])
            for xb in xrange(1, sliced_hist[out_name].GetNbinsX()+1):
                for yb in xrange(1, sliced_hist[out_name].GetNbinsY()+1):
                    sliced_hist[out_name].SetBinContent(xb, yb, self.hist.GetBinContent(xb, yb, i_n+1))
                    sliced_hist[out_name].SetBinError(xb, yb, self.hist.GetBinError(xb, yb, i_n+1))
        return sliced_hist


    def fill(self, chain, weight, index = None):
        if self.var is None:
            print "\033[93m !Warning! \033[0m This histogram was loaded from a root file, the variable to fill is not known at the moment. Histogram will not be filled."
            return

        if self.isTH2:
            self.fill2D(chain, weight, index)
        elif self.isTH3:
            self.fill3D(chain, weight, index)
        else:
            self.fill1D(chain, weight, index)

    def getXTitle(self):
        return self.var_tex[0]
    
    def getYTitle(self):
        return self.var_tex[1]

    def getHist(self):
        return self.hist

    def write(self, path, subdirs=None, write_name = None, append = False, is_test=None):
        append_string = 'recreate'
        if append and isValidRootFile(path): append_string = 'update'

        if is_test is None:
            path_to_use = path
        else:
            split_path = path.split('/')
            index_to_use = split_path.index('testArea')+1
            #
            # Have to hardcode because $HOME doesnt work on t2b condor
            #
            # path_to_use = os.path.expandvars("$HOME/Testing/Latest/"+'/'.join(split_path[index_to_use:-1])+'/'+is_test+'/'+split_path[-1])
            path_to_use = os.path.expandvars("/storage_mnt/storage/user/lwezenbe/Testing/Latest/"+'/'.join(split_path[index_to_use:-1])+'/'+is_test+'/'+split_path[-1])

        makeDirIfNeeded(path_to_use)
        output_file = ROOT.TFile(path_to_use, append_string)
        name_to_use = write_name if write_name is not None else self.name
        if subdirs is None:
            pass
            # output_file.mkdir(name_to_use)
            # output_file.cd(name_to_use)
        else:
            nomo = ''
            for d in subdirs:
                nomo += d + '/'
                output_file.mkdir(nomo)
                output_file.cd(nomo)

        self.hist.Write(name_to_use)
        output_file.Close()

        if is_test is not None:
            self.write(path, write_name=write_name, subdirs=subdirs, append=append, is_test=None)

    def clone(self, out_name):
        hist_clone = self.hist.Clone(out_name)
        return Histogram(hist_clone)

    def divide(self, other_histogram):
        self.hist.Divide(other_histogram.getHist())

    def add(self, other_histogram):
        tmp_other_histogram = other_histogram.clone('other_hist_clone')
        self.hist.Add(tmp_other_histogram.getHist())

    def getYieldHistogram(self):
        tmp_hist = ROOT.TH1D('totalyield', 'total yield', 1, 0, 1)
        tmp_hist.SetBinContent(1, self.hist.GetSumOfWeights())
        tmp_hist.SetBinError(1, self.hist.GetMeanError())
        return Histogram(tmp_hist)

    def replaceZeroBins(self):
        nbinsx = self.hist.GetNbinsX() 
        nbinsy = self.hist.GetNbinsY() if self.isTH2 else 1
        nbinsz = self.hist.GetNbinsZ() if self.isTH3 else 1
        for bx in xrange(1, nbinsx+1):
            for by in xrange(1, nbinsy+1):
                for bz in xrange(1, nbinsz+1):
                    print self.hist.GetBinContent(bx, by, bz)
                    if self.hist.GetBinContent(bx, by, bz) <= 0.0: self.hist.SetBinContent(bx, by, bz, 1e-7)
        

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
            split_path = self.path.split('/')
            index_to_use = split_path.index('testArea')+1
            #
            # Have to hardcode because $HOME doesnt work on t2b condor
            #
            # path_to_use = os.path.expandvars("$HOME/Testing/Latest/"+'/'.join(split_path[index_to_use:]))
            path_to_use = os.path.expandvars("/storage_mnt/storage/user/lwezenbe/Testing/Latest/"+'/'.join(split_path[index_to_use:]))

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
