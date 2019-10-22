import ROOT, glob, os
from helpers import isValidRootFile, getObjFromFile

class Sample:

    def __init__(self, name, path, output, splitJobs, xsec, skipFaultyFiles = False):           #Added last variable due to t2b pnfs problems that took too long to get solved
        self.name               = name
        self.path               = path
        self.isData             = (xsec == 'data')
        self.xsec               = eval(xsec) if not self.isData else None
        self.splitJobs          = splitJobs
        self.hCount             = None
        self.Chain              = None
        self.output             = output
        self.singleFile         = self.path.endswith('.root')
        self.isSkimmed          = not 'pnfs' in self.path
     
    def getHist(self, name, subPath = None): 
        if subPath is None:             subPath = self.path
        if subPath.endswith('.root'):
            hCounter                    = getObjFromFile(subPath, 'blackJackAndHookers/'+name)
            return hCounter
        else:
            hCounter = None
            listOfFiles                 = glob.glob(self.path + '/*.root')
            print self.path + '/*.root'
            for f in listOfFiles:
                if hCounter is None:     hCounter = self.getHist(name, f)
                else:                   hCounter.Add(self.getHist(name, f))
            return hCounter
 
    def initTree(self, branches = None, needhCount=True):
        self.Chain              = ROOT.TChain('blackJackAndHookers/blackJackAndHookersTree')
        if self.singleFile:
            listOfFiles         = [self.path]
        else:
            listOfFiles         = sorted(glob.glob(self.path + '/*.root'))
        
        for f in listOfFiles:
            if 'pnfs' in f:
                f = 'root://maite.iihe.ac.be'+f
            self.Chain.Add(f)                                                   
        
        if branches is not None:        self.setSpecificBranches(branches)

        if not self.isData and needhCount:   
            hCounter = self.getHist('hCounter')
            self.hCount = hCounter.GetSumOfWeights()
        
        return self.Chain

    def getEventRange(self, subJob):
        limits = [entry*self.Chain.GetEntries()/self.splitJobs for entry in range(self.splitJobs)] + [self.Chain.GetEntries()]
        return xrange(limits[subJob], limits[subJob+1])

    def setSpecificBranches(self, branches):
        self.Chain.SetBranchStatus("*",0)
        for branch in branches:
            self.Chain.SetBranchStatus(branch, 1)


def createSampleList(fileName):
    sampleInfos = [line.split('%')[0].strip() for line in open(fileName)]                     # Strip % comments and \n charachters
    sampleInfos = [line.split() for line in sampleInfos if line]                              # Get lines into tuples
    for name, path, output, splitJobs, xsec in sampleInfos:
        try:
            if splitJobs == 'Calc':
                if path.endswith('.root'):
                    file_info = os.stat(path)
                    file_size = file_info.st_size
                    splitJobs = round((file_size/500000000.)+0.5)
                else:
                    splitJobs = round((len(glob.glob(path + '/*.root'))/5.)+0.5)
        except:
            continue
        yield Sample(name, path, output, int(splitJobs), xsec)

def getSampleFromList(sampleList, name):
  return next((s for s in sampleList if s.name==name), None)
     
