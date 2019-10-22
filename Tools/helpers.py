import ROOT, socket, os, shutil, subprocess, time
from math import pi, sqrt
from operator import mul
from numpy import loadtxt
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

def progress(i, N, prefix="", size=60):
    x = int(size*i/(N-1))
    sys.stdout.write("%s\x1b[6;30;42m%s\x1b[0m\x1b[0;30;41m%s\x1b[0m %i/%i %s\r" % (" "*0, " "*x, " "*(size-x), i, N, prefix))
    sys.stdout.flush()

def makeDirIfNeeded(path):
    try:
        os.makedirs(path)
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
    orderedList = [x for _,x in sorted(zip(base,to_sort))]
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

def CleanNegativeBins(hist):
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
