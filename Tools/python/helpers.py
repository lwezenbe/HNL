import ROOT, os, time
from numpy import loadtxt
from math import pi, sqrt
import sys

#
# Check if valid ROOT file exists
#
def isValidRootFile(fname):
    if not os.path.exists(os.path.expandvars(fname)): return False
    if 'pnfs' in fname: fname = 'root://maite.iihe.ac.be'+ fname         #faster for pnfs files + avoids certain unstable problems I had with input/output errors
    f = ROOT.TFile.Open(fname)
    if not f: return False
    try:
        return not (f.IsZombie() or f.TestBit(ROOT.TFile.kRecovered) or f.GetListOfKeys().IsEmpty())
    finally:
        f.Close()

#
# Get object (e.g. hist) from file using key, and keep in memory after closing
#
def getObjFromFile(fname, hname):
    assert isValidRootFile(fname)

    if 'pnfs' in fname: fname = 'root://maite.iihe.ac.be'+ fname         #faster for pnfs file
    try:
        f = ROOT.TFile.Open(fname)
        f.cd()
        htmp = f.Get(hname)
        if not htmp: return None
        ROOT.gDirectory.cd('PyROOT:/')
        res = htmp.Clone()
        return res
    finally:
        f.Close()

def loadtxtCstyle(source):
    arr = loadtxt(source)
    arr = arr.flatten('C')
    arr = arr.astype('double')
    return arr

#
# Progress bar
#

def progress(i, n, prefix="", size=60):
    x = int(size*i/(n-1))
    sys.stdout.write("%s\x1b[6;30;42m%s\x1b[0m\x1b[0;30;41m%s\x1b[0m %i/%i %s\r" % (" "*0, " "*x, " "*(size-x), i, n, prefix))
    sys.stdout.flush()

def makeDirIfNeeded(path):
    try:
        os.makedirs(os.path.dirname(path))
    except OSError:
        pass

#
#Return array with values of a branch because I don't know a better solution
#

def showBranch(branch):
    arr = [x for x in branch]
    return arr

#
#Add timestamp to the end of a path
#
def makePathTimeStamped(path):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    basefolderOutput = path+'/'+timestamp
    makeDirIfNeeded(basefolderOutput)
    return basefolderOutput

#
#Sort one list based on another list
#
def sortByOtherList(to_sort, base):
    orderedList = [x for _, x in sorted(zip(base, to_sort))]
    return orderedList

#
#Get all low edges of hist because I dont trust the root function
#
def getLowEdges(hist):
    nbins = hist.GetXaxis().GetNbins()
    edges = []
    for b in xrange(nbins):
        edges.append(hist.GetXaxis().GetBinUpEdge(b))
    return edges

#
#Set all negative values to 0 in a hist
#

def cleanNegativeBins(hist):
    h = hist.Clone()
    for b in xrange(h.GetXaxis().GetNbins()):
        if h.GetBinContent(b+1) < 0:
            h.SetBinContent(b+1, 0)

    return h

#
#Write a message to a text file
#
def writeMessageToFile(name, destination, message):
    f = open(destination+'/'+name+'.txt', 'w')
    f.write(message)
    f.close()

#
#Timestamp a folder
#    
def timeStampFolder(folder, usefulInfo):
    timestamp = time.strftime("%Y%m%d_%H%M%S") 
    makeDirIfNeeded(folder + '/' +timestamp)
    if usefulInfo:
        writeMessageToFile('usefulInfo', folder+ '/' + timestamp, usefulInfo)    
    return folder + '/' +timestamp

#
#Check whether a string has the timestamp format from above
#Not entirely watertight but checks whether if you take the '_' out, all you are left with are digits
#

def isTimeStampFormat(input_string):
    str_arr = input_string.split('_')
    if len(str_arr) != 2:       return False
    if not str_arr[0].isdigit() or not str_arr[1].isdigit():    return False
    return True

#
#Create Four Vector
#
def getFourVec(pt, eta, phi, e):
    vec = ROOT.TLorentzVector()
    vec.SetPtEtaPhiE(pt, eta, phi, e)
    return vec

def getLeptonFourVecFromChain(chain, index):
    vec = getFourVec(chain._lPt[index], chain._lEta[index], chain._lPhi[index], chain._lE[index])
    return vec

#
# Delta phi and R function
#
def deltaPhi(phi1, phi2):
    dphi = phi2-phi1
    if dphi > pi:   dphi -= 2.0*pi
    if dphi <= -pi: dphi += 2.0*pi
    return abs(dphi)

def deltaR(eta1, eta2, phi1, phi2):
    return sqrt(deltaPhi(phi1, phi2)**2 + (eta1-eta2)**2)

#
# Get all subdirectories
#
def getSubDir(path):
    list_of_subdir = next(os.walk(path))[1]
    return [path + '/' + f for f in list_of_subdir]

#
# Read the content of a root file
#
def rootFileContent(d, basepath="/", getNested=False, starting_dir=None):
    #"Generator function to recurse into a ROOT file/dir and yield (path, obj) pairs"
    if starting_dir is not None: d = d.Get(starting_dir)
    for key in d.GetListOfKeys():
        kname = key.GetName()
        if key.IsFolder() and getNested:
    #    if key.IsFolder():
            # TODO: -> "yield from" in Py3
            for i in rootFileContent(d.Get(kname), basepath+kname+"/", getNested):
                yield i
        else:
            if starting_dir is not None:
                yield basepath+starting_dir+'/'+kname, d.Get(kname)
            else:
                yield basepath+kname, d.Get(kname)

#
# Get Maximum or Minimum value including the error on the bin. I could not find any
# existing root function for it
#

def getMaxWithErr(hist):
    max_val = 0
    if isinstance(hist, ROOT.TH1):
        for bx in xrange(1, hist.GetNbinsX()+1):
            new_val = hist.GetBinContent(bx) + hist.GetBinErrorUp(bx)
            if new_val > max_val:       max_val = new_val

    elif isinstance(hist, ROOT.TH2):
        for bx in xrange(1, hist.GetNbinsX()+1):
            for by in xrange(1, hist.GetNbinsY()):
                new_val = hist.GetBinContent(bx, by) + hist.GetBinErrorUp(bx, by)
                if new_val > max_val:       max_val = new_val
              
#    elif isinstance(hist, ROOT.TGraph):
#        for bx in xrange(1, hist.GetNbinsX()):
#            for by in xrange(1, hist.GetNbinsY()):
#                new_val = hist.GetBinContent(bx, by) + hist.GetBinErrorUp(bx, by)
#                if new_val > max_val:       max_val = new_val
    
    else:
        print "Wrong type in getMaxWithErr. Returning 0."
        return 0.

    return max_val  
            
def getMinWithErr(hist, zero_not_allowed=False):
    min_val = 99999999.
    if isinstance(hist, ROOT.TH1):
        for bx in xrange(1, hist.GetNbinsX()+1):
            if zero_not_allowed and not hist.GetBinContent(bx) > 0.: continue
            new_val = hist.GetBinContent(bx) - hist.GetBinErrorLow(bx)
            if zero_not_allowed and new_val <= 0.: new_val = hist.GetBinContent(bx)
            if new_val < min_val:       min_val = new_val

    elif isinstance(hist, ROOT.TH2):
        for bx in xrange(1, hist.GetNbinsX()+1):
            for by in xrange(1, hist.GetNbinsY()):
                if zero_not_allowed and not hist.GetBinContent(bx, by) > 0: continue
                new_val = hist.GetBinContent(bx, by) - hist.GetBinErrorLow(bx, by)
                if zero_not_allowed and new_val <= 0.: new_val = hist.GetBinContent(bx, by)
                if new_val < min_val:       min_val = new_val
              
    else:
        print "Wrong type in getMaxWithErr. Returning 0."
        return 0.01
    return min_val  


def getMassRange(list_of_names):
    all_masses = [float(name.rsplit('-m', 1)[-1]) for name in list_of_names if 'HNL' in name]
    m_range = []
    if len(all_masses) == 1:
        m_range = [all_masses[0]/2, all_masses[0]*1.5]
    else:
        for i, mass in enumerate(all_masses):
            if i != len(all_masses)-1: distance_to_next = all_masses[i+1] - mass
            if i == 0: m_range.append(mass - 0.5*distance_to_next)
            m_range.append(mass+0.5*distance_to_next)  #For last run, distance_to_next should still be the same
    return m_range
