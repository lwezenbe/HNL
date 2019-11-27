#
#       Sample class to load in samples
#

import ROOT
import glob
import os
from HNL.Tools.helpers import getObjFromFile

class Sample:
    
    #
    #   Added last variable due to t2b pnfs problems that took too long to get solved
    #

    def __init__(self, name, path, output, split_jobs, xsec, max_filesize = 500):           
        self.name               = name
        self.path               = path
        self.is_data            = (xsec == 'data')
        self.xsec               = eval(xsec) if not self.is_data else None
        self.max_filesize       = max_filesize
        self.split_jobs         = self.calcSplitJobs(split_jobs)
        self.hcount             = None
        self.chain              = None
        self.output             = output
  
    #
    #   Return the file size of the file at the path location in MB
    #
    @staticmethod
    def fileSize(path):           
        file_info = os.stat(path)
        file_size = file_info.st_size
        file_size_MB = 0.000001*file_size
        return file_size_MB
    
    #
    #   Function to calculate the number of subjobs
    #   If the option to calculate was given in inputfile,
    #   it splits up jobs corresponding to filesize smaller than
    #   or equal to self.max_filesize
    #
    def calcSplitJobs(self, init_value):
        split_jobs = 1
        if 'Calc' in init_value:
            tot_size = 0
            if self.path.endswith('.root'):
                tot_size = self.fileSize(self.path)
            else:
                for f in glob.glob(self.path + '/*/*/*.root'):
                    tot_size += self.fileSize(f)
                if tot_size == 0: 
                    print "No file loaded, check the input path again."
            split_jobs = int(round((tot_size/self.max_filesize)+0.5))
            if '*' in init_value:       
                split_jobs *= float(init_value.split('*')[-1])
        else:
            split_jobs = int(init_value)
        return split_jobs

    #
    #   Extract a histogram with given name stored alongside the tree
    #   from the input file
    #
    def getHist(self, name, sub_path = None): 
        if sub_path is None:             
            sub_path = self.path
        
        if sub_path.endswith('.root'):
            hcounter                    = getObjFromFile(sub_path, 'blackJackAndHookers/'+name)
            return hcounter
        else:
            hcounter = None
            listOfFiles                 = glob.glob(self.path + '/*/*/*.root')
            for f in listOfFiles:
                if hcounter is None:     
                    hcounter = self.getHist(name, f)
                else:                   
                    hcounter.Add(self.getHist(name, f))
            return hcounter
    
    #
    #   Initialize the chain for use
    #
    def initTree(self, needhcount=True):
        
        self.chain              = ROOT.TChain('blackJackAndHookers/blackJackAndHookersTree')
        
        if self.path.endswith('.root'):
            list_of_files         = [self.path]
        else:
            list_of_files         = sorted(glob.glob(self.path + '/*/*/*.root'))
       
        for f in list_of_files:
            if 'pnfs' in f:
                f = 'root://maite.iihe.ac.be'+f
            self.chain.Add(f)                                                   
        
        if not self.is_data and needhcount:   
            hcounter = self.getHist('hCounter')
            self.hcount = hcounter.GetSumOfWeights()
        
        return self.chain

    #
    #   Returns the range of event numbers considered in the specified subjob
    #
    def getEventRange(self, subjob):
        limits = [entry*self.chain.GetEntries()/self.split_jobs for entry in range(self.split_jobs)] + [self.chain.GetEntries()]
        return xrange(limits[int(subjob)], limits[int(subjob)+1])

#
#       create list of samples from input file
#
def createSampleList(file_name):
    sample_infos = [line.split('%')[0].strip() for line in open(file_name)]                     # Strip % comments and \n charachters
    sample_infos = [line.split() for line in sample_infos if line]                              # Get lines into tuples
    for name, path, output, split_jobs, xsec in sample_infos:
        try:
            split_jobs
        except:
            continue
        yield Sample(name, path, output, split_jobs, xsec)

#
#       Load in a specific sample from the list
#
def getSampleFromList(sample_list, name):
    return next((s for s in sample_list if s.name==name), None)

#
#       In case only a short list is given, i.e.
#         *DYJets*
#        *TTJets*
#       A proper list will be constructed
#       Meant for skimmer where a whole group should be skimmed
#
def createSampleFileFromShortlist(file_name):
    sample_infos = [line.split('%')[0].strip() for line in open(file_name)]                     # Strip % comments and \n charachters
    sample_infos = [line.split() for line in sample_infos if line]                              # Get lines into tuples
    
    list_of_paths = []
    for sample in sample_infos:
        list_of_paths += glob.glob(sample[0])
    
    print "\033[93m !Warning! \033[0m Be aware that right know your samples do not have a cross section because you are in skimming mode. \n If you need a cross section, use the createSampleList function."
    outfile = open(file_name.rsplit('.')[0]+'_sampleList.conf', 'w')
    for p in list_of_paths:
        split_path = p.split('/')
        name = split_path[-1]
        output = split_path[-2]
        outfile.write(name + ' ' + p + ' ' + output + '       Calc    0.  \n')
    outfile.close()
    return 

#
#       Return a list of all names of the samples in the input file
#    
def getListOfSampleNames(file_name):
    sample_infos = [line.split('%')[0].strip() for line in open(file_name)]                     # Strip % comments and \n charachters
    sample_infos = [line.split() for line in sample_infos if line]                              # Get lines into tuples
    name_list = []
    for line in sample_infos:
        name_list.append(line[0])

    return name_list

if __name__ == "__main__":
    createSampleFileFromShortlist('input.conf') 
    LISTW = createSampleList('input_sampleList.conf')
    for l in LISTW:
        print l.name, l.output, l.split_jobs
