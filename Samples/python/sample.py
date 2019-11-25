import ROOT, glob, os
from helpers import isValidRootFile, getObjFromFile

class sample:

    def __init__(self, name, path, output, splitJobs, xsec, max_filesize = 500):           #Added last variable due to t2b pnfs problems that took too long to get solved
        self.name               = name
        self.path               = path
        self.isData             = (xsec == 'data')
        self.xsec               = eval(xsec) if not self.isData else None
        self.max_filesize       = max_filesize
        self.splitJobs          = self.calcSplitJobs(splitJobs)
        self.hCount             = None
        self.Chain              = None
        self.output             = output
        self.singleFile         = self.path.endswith('.root')
        self.isSkimmed          = not 'pnfs' in self.path
   
    @staticmethod
    def fileSize(path):              #return filesize in MB
        file_info = os.stat(path)
        file_size = file_info.st_size
        file_size_MB = 0.000001*file_size
        return file_size_MB
 
    def calcSplitJobs(self, init_value):
        splitJobs = 1
        if 'Calc' in init_value:
            tot_size = 0
            if self.path.endswith('.root'):
                tot_size = self.fileSize(self.path)
            else:
                for f in glob.glob(self.path + '/*/*/*.root'):
                    tot_size += self.fileSize(f)
                if tot_size == 0:       print "No file loaded, check the input path again."
            splitJobs = int(round((tot_size/self.max_filesize)+0.5))
            if '*' in init_value:       splitJobs *= float(init_value.split('*')[-1])
        else:
            splitJobs = int(init_value)
        return splitJobs

    def getHist(self, name, subPath = None): 
        if subPath is None:             subPath = self.path
        if subPath.endswith('.root'):
            hCounter                    = getObjFromFile(subPath, 'blackJackAndHookers/'+name)
            return hCounter
        else:
            hCounter = None
            listOfFiles                 = glob.glob(self.path + '/*/*/*.root')
            for f in listOfFiles:
                if hCounter is None:     hCounter = self.getHist(name, f)
                else:                   hCounter.Add(self.getHist(name, f))
            return hCounter
 
    def initTree(self, needhCount=True):
        
        self.Chain              = ROOT.TChain('blackJackAndHookers/blackJackAndHookersTree')
        
        if self.singleFile:
            listOfFiles         = [self.path]
        else:
            listOfFiles         = sorted(glob.glob(self.path + '/*/*/*.root'))
       
        for f in listOfFiles:
            if 'pnfs' in f:
                f = 'root://maite.iihe.ac.be'+f
            self.Chain.Add(f)                                                   
        
        if not self.isData and needhCount:   
            hCounter = self.getHist('hCounter')
            self.hCount = hCounter.GetSumOfWeights()
        
        return self.Chain

    def getEventRange(self, subJob):
        limits = [entry*self.Chain.GetEntries()/self.splitJobs for entry in range(self.splitJobs)] + [self.Chain.GetEntries()]
        return xrange(limits[int(subJob)], limits[int(subJob)+1])

def createSampleList(fileName):
    sampleInfos = [line.split('%')[0].strip() for line in open(fileName)]                     # Strip % comments and \n charachters
    sampleInfos = [line.split() for line in sampleInfos if line]                              # Get lines into tuples
    for name, path, output, splitJobs, xsec in sampleInfos:
        try:
            splitJobs
        except:
            continue
        yield sample(name, path, output, splitJobs, xsec)

def getSampleFromList(sampleList, name):
  return next((s for s in sampleList if s.name==name), None)


def createSampleFileFromShortlist(fileName):
    sampleInfos = [line.split('%')[0].strip() for line in open(fileName)]                     # Strip % comments and \n charachters
    sampleInfos = [line.split() for line in sampleInfos if line]                              # Get lines into tuples
    
    list_of_paths = []
    for sample in sampleInfos:
        list_of_paths += glob.glob(sample[0])
    
    print "\033[93m !Warning! \033[0m Be aware that right know your samples do not have a cross section because you are in skimming mode. \n If you need a cross section, use the createSampleList function."
    outfile = open(fileName.rsplit('.')[0]+'_sampleList.conf', 'w')
    for p in list_of_paths:
        split_path = p.split('/')
        name = split_path[-1]
        output = split_path[-2]
        outfile.write(name + ' ' + p + ' ' + output + '       Calc    0.  \n')
    outfile.close()
    return 
    
def getListOfSampleNames(fileName):
    sampleInfos = [line.split('%')[0].strip() for line in open(fileName)]                     # Strip % comments and \n charachters
    sampleInfos = [line.split() for line in sampleInfos if line]                              # Get lines into tuples
    name_list = []
    for name, path, output, splitJobs, xsec in sampleInfos:
        name_list.append(name)

    return name_list
if __name__ == "__main__":
    createSampleFileFromShortlist('input.conf') 
    listw = createSampleList('input_sampleList.conf')
    for l in listw:
        print l.name, l.output, l.splitJobs
