#
#       Sample class to load in samples
#

import ROOT
import glob
import os
from HNL.Tools.helpers import getObjFromFile, isValidRootFile

class Sample(object):
    
    #
    #   Added last variable due to t2b pnfs problems that took too long to get solved
    #

    def __init__(self, name, path, output, split_jobs, xsec, max_filesize = 1000):  
        self.name               = name
        self.path               = path
        self.is_data            = (xsec == 'data')
        self.xsec               = eval(xsec) if not self.is_data else None
        self.max_filesize       = max_filesize
        # self.split_jobs         = self.calcSplitJobs(split_jobs) if not is_test else 1
        self.split_jobs         = split_jobs
        self.hcount             = None
        self.chain              = None
        self.output             = output
        self.mass               = self.getMass()
        self.is_signal          = 'HNL' in name
        if self.path.endswith('.root'):
            self.list_of_files         = [self.path]
        else:
            self.list_of_files         = sorted(glob.glob(self.path + '/*/*/*.root'))

  
    #
    #   Return the file size of the file at the path location in MB
    #
    @staticmethod
    def fileSize(path):           
        file_info = os.stat(path)
        file_size = file_info.st_size
        file_size_MB = 0.000001*file_size
        return file_size_MB

    def shavedName(self):
        if 'ext' in self.name:
            tmp_sample_name = self.name.rsplit('-', 1)[0]
        else:
            tmp_sample_name = self.name
        return tmp_sample_name

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
                    print "No file loaded, check the input path of "+self.name+" again."
            split_jobs = int(round((tot_size/self.max_filesize)+0.5))
            if '*' in init_value:       
                split_jobs *= float(init_value.split('*')[-1])
        else:
            split_jobs = int(init_value)
        return max(1, int(split_jobs))

    def returnSplitJobs(self):
        if isinstance(self.split_jobs, str) and 'Calc' in self.split_jobs:
            self.split_jobs = self.calcSplitJobs(self.split_jobs)
        return self.split_jobs

    #
    #   Extract a histogram with given name stored alongside the tree
    #   from the input file
    #
    def getHist(self, name, sub_path = None): 
        if sub_path is None:             
            sub_path = self.path
        
        if sub_path.endswith('.root'):
            hcounter                    = getObjFromFile(sub_path, 'blackJackAndHookers/'+name)
            if hcounter is None:  hcounter = getObjFromFile(sub_path, name)     #Try without blackJackAndHookers
            return hcounter
        else:
            hcounter = None
            listOfFiles                 = glob.glob(sub_path + '/*/*/*.root')
            for f in listOfFiles:
                if hcounter is None:     
                    hcounter = self.getHist(name, f)
                else:                   
                    hcounter.Add(self.getHist(name, f))
            return hcounter
    
    #
    #   Initialize the chain for use
    #
    def initTree(self, needhcount=False):

        self.split_jobs         = self.returnSplitJobs()
        self.chain              = ROOT.TChain('blackJackAndHookers/blackJackAndHookersTree')
    
        assert len(self.list_of_files) > 0 and isValidRootFile(self.list_of_files[0])

        for f in self.list_of_files:
            if 'pnfs' in f:
                f = 'root://maite.iihe.ac.be/'+f
            self.chain.Add(f)
        
        if not self.is_data and needhcount:   
            hcounter = self.getHist('hCounter')
            self.hcount = hcounter.GetSumOfWeights()
 
        self.chain.is_data = self.is_data
        return self.chain

    #
    #   Returns the range of event numbers considered in the specified subjob
    #
    def getEventRange(self, subjob):
        limits = [entry*self.chain.GetEntries()/self.split_jobs for entry in range(self.split_jobs)] + [self.chain.GetEntries()]
        return xrange(limits[int(subjob)], limits[int(subjob)+1])

    def getMass(self):
        if 'HNL' in self.name:
            return float(self.name.rsplit('-m', 1)[-1])
        else:
            return None



class SkimSample(Sample):

    def __init__(self, name, path, output, split_jobs, xsec, max_filesize = 6000):  
        super(SkimSample, self).__init__(name, path, output, split_jobs, xsec, max_filesize)
        self.list_of_subjobclusters     = self.createSubjobClusters()
        self.split_jobs                 = len(self.list_of_subjobclusters)

    def createSubjobClusters(self):
        list_of_subjobclusters = []
        tot_size = 0.
        tmp_arr = []
        for f in self.list_of_files:
            file_size = self.fileSize(f)
            # if file_size > self.max_filesize:
            #     raise RuntimeError("There are singular files larger than 1GB, you run the risk of creating corrupt output.")
            if tot_size + file_size < self.max_filesize:
                tmp_arr.append(f)
                tot_size += file_size
            else:
                if len(tmp_arr) > 0: list_of_subjobclusters.append([x for x in tmp_arr])
                tmp_arr = [f]
                tot_size = file_size
            
        #Append last array to list of subjob cluster
        if len(tmp_arr) > 0:
            list_of_subjobclusters.append([x for x in tmp_arr])
        return list_of_subjobclusters

    def getSubHist(self, subjob, name):

        hcounter = None

        for f in self.list_of_subjobclusters[int(subjob)]:
            if hcounter is None:     
                hcounter = self.getHist(name, f)
            else:
                hcounter.Add(self.getHist(name, f))
        return hcounter
            

    def initTree(self, subjob):

        self.chain              = ROOT.TChain('blackJackAndHookers/blackJackAndHookersTree')
    
        assert len(self.list_of_files) > 0 and isValidRootFile(self.list_of_files[0])

        for f in self.list_of_subjobclusters[int(subjob)]:
            if 'pnfs' in f:
                f = 'root://maite.iihe.ac.be'+f
            self.chain.Add(f)
        
        # if not self.is_data and needhcount:   
        #     hcounter = self.getSubHist('hCounter')
        #     self.hcount = hcounter.GetSumOfWeights()
 
        self.chain.is_data = self.is_data
        return self.chain

    def getEventRange(self, subjob):
        return xrange(self.chain.GetEntries())

#
#       create list of samples from input file
#
def createSampleList(file_name, sample_manager = None, need_skim_sample = False, skim_selection = None, region = None):
    sample_infos = [line.split('%')[0].strip() for line in open(file_name)]                     # Strip % comments and \n charachters
    sample_infos = [line.split() for line in sample_infos if line]                              # Get lines into tuples
    for name, path, output, split_jobs, xsec in sample_infos:
        try:
            split_jobs
        except:
            continue

        if skim_selection is not None and region is not None:
            path = path.replace('$SKIMSELECTION$', skim_selection).replace('$REGION$', region)

        if sample_manager != None:
            split_jobs += '*' + str(sample_manager.sample_dict[name])
        if not need_skim_sample: 
            yield Sample(name, path, output, split_jobs, xsec)
        else:
            yield SkimSample(name, path, output, split_jobs, xsec)

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
        list_of_paths.extend([(s, sample[1]) for s in glob.glob(sample[0])])
    
    outfile = open(file_name.rsplit('.')[0]+'_sampleList.conf', 'w')
    names = [] #retain lists of names so you can make them unique
    for i, p in enumerate(list_of_paths):
        split_path = p[0].split('/')
        name = split_path[-2]
        xsec = p[1] if p[1] else 0.
        if name in names: 
            name += '-ext'+str(i)
        names.append(name)
        output = split_path[-2]
        outfile.write(name + ' ' + p[0] + ' ' + output + '       Calc    '+ xsec  +'  \n')
        
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

#
#       If during skimming there are extension files, they are on 
#       different lines with the same output but different names.
#       Usually getHist would get the correct hcounter per line.
#       However, if we want to save lumiweight in trees after skimming,
#       We need all events that are in all extension files.
#       This function lists all extension files
#
def getListOfPathsWithSameOutput(file_name, name):
    sample_infos = [line.split('%')[0].strip() for line in open(file_name)]                     # Strip % comments and \n charachters
    sample_infos = [line.split() for line in sample_infos if line]                              # Get lines into tuples

    if 'ext' in name:
        tmp_sample_name = name.rsplit('-', 1)[0]
    else:
        tmp_sample_name = name

    path_list = []
    for line in sample_infos:
        shaved_line_name = line[0] if not 'ext' in line[0] else line[0].rsplit('-', 1)[0]
        if tmp_sample_name != shaved_line_name: continue
        if line[0] == name: continue                            #Make sure the same file is not in the list
        path_list.append(line[1])
    return path_list   
 
if __name__ == "__main__":
    from HNL.Tools.logger import getLogger, closeLogger
    log = getLogger('INFO')

    in_file_path = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Samples', 'InputFiles', 'sampleList_UL2017_noskim.conf'))
    sample_list = createSampleList(in_file_path)
    sample = getSampleFromList(sample_list, 'DYJetsToLL-M-10to50')
    chain = sample.initTree(needhcount = True)
    log.info('Running test data')        
    # log.info('file size: ', '90.4 expected', str(sample.fileSize('/pnfs/iihe/cms/store/user/wverbeke/heavyNeutrino/DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/crab_MiniAOD2016v3-v2_singlelepton_MC_2016_v2/191227_182847/0000/singlelep_1.root')) +' observed')
    # log.info('hCounter: ', ' 2.05023673303e+12 expected', str(sample.hcount) + ' observed')
    # log.info('calcSplitJobs: ', '25 expected', str(sample.split_jobs) + ' observed')
    # log.info('event_range', len(sample.getEventRange(0)))
    log.info(getListOfSampleNames(in_file_path))
    log.info(getListOfPathsWithSameOutput(in_file_path, 'DYJetsToLL-M-10to50'))

    closeLogger(log)
