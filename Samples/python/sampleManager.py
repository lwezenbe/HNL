from HNL.Samples.sample import Sample, getListOfSampleNames, createSampleList, getSampleFromList, SkimSample
import os

#
# To get load in samples, this manager is used
# There are 9 general list, containing all the available samples and cross sections  for all three years for three different types of skims (no skim, reco skim, gen skim)
# To select samples to use in a certain piece of code, you can make a list with the sample names in a "sublist"
# No need to include the extensions in the sublists, it will handle that
#

ALLOWED_SKIMS = ['noskim', 'Reco', 'RecoGeneral', 'auto']
BASE_PATH = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Samples', 'InputFiles')
LAMBDA_PATH = lambda era, year, skim : os.path.join(BASE_PATH, '_'.join(['sampleList', era + year, skim+'.conf']))
SAMPLE_GROUPS = {
    # 'non-prompt': ['DY', 'WJets', 'WW', 'ST', 'TT'],
    'TT-T+X': ['ttX', 'TTG', 'TG', 'TTTT', 'ST', 'TT'],
    'triboson': ['triboson'],
    'WZ': ['WZ'],
    # 'diboson': ('ZZ', 'WW', 'WZ'),
    'ZZ-H': ['ZZ', 'Higgs'],
    'XG': ['DY', 'ZG', 'WG'],
    'other':['WJets', 'WW', 'QCD']
}
# SAMPLE_GROUPS = {
#     'non-prompt': ['DY', 'WJets', 'WW', 'ST', 'TT'],
#     'TT-T+X': ['ttX', 'TTG', 'TG', 'TTTT'],
#     'triboson': ['triboson'],
#     'WZ': ['WZ'],
#     # 'diboson': ('ZZ', 'WW', 'WZ'),
#     'ZZ-H': ['ZZ', 'Higgs'],
#     'XG': ['ZG', 'WG'],
#     'other':['QCD']
# }


ERA_DICT = {
    'prelegacy': ['2016', '2017', '2018'],
    'UL': ['2016pre', '2016post', '2017', '2018']
}

allowed_reco_general_skimselections = ['default', 'AN2017014']
allowed_reco_general_regions = ['lowMassSR', 'highMassSR']

low_mass_range_lightlep = [10, 20, 30, 40, 50, 60, 70, 75]
low_mass_range_tau = [20, 30, 40, 50, 60, 70, 75]
high_mass_range_lightlep = [85, 100, 125, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1500]
high_mass_range_tau = [85, 100, 125, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000]

class SampleManager:


    def __init__(self, era, year, skim, sample_names_file, need_skim_samples=False, skim_selection=None, region=None):
        if not year in ERA_DICT[era]:
            raise RuntimeError('year {0} not allowed for era {1}'.format(year, era))
        if not skim in ALLOWED_SKIMS:
            raise RuntimeError("skim "+skim+" not allowed in the sample manager")

        self.skim_selection = skim_selection
        self.region = region
        self.era = era
        self.year = year

        if skim_selection is None:
            self.skim = 'noskim'
        elif skim == 'auto':
            self.skim = self.findInFileToUse()
        else:
            self.skim = skim
        
        print "Using {0} skim".format(self.skim)
        self.path = LAMBDA_PATH(self.era, self.year, self.skim)

        self.sample_names_file_full = os.path.join(BASE_PATH, 'Sublists', sample_names_file+'.conf')
        self.sample_dict = self.getSampleDict(self.sample_names_file_full)
        self.sample_names = self.sample_dict.keys()
        self.need_skim_samples = need_skim_samples
        self.sample_list = self.createSampleList()
        self.sample_groups = SAMPLE_GROUPS

        self.sample_outputs = self.getOutputs()

        self.lumi_clusters = {}

    def getTestPath(self, in_file_name):
        sample_infos = [line.split('%')[0].strip() for line in open(in_file_name)]                     # Strip % comments and \n charachters
        sample_infos = [line.split() for line in sample_infos if line] 

        sample = sample_infos[0]
        return os.path.isdir(sample[1].rsplit('/', 1)[0].replace('$SKIMSELECTION$', self.skim_selection).replace('$REGION$', self.region))

    def findInFileToUse(self):
        if self.getTestPath(LAMBDA_PATH(self.era, self.year, 'RecoGeneral')):
            return 'RecoGeneral'
        elif self.getTestPath(LAMBDA_PATH(self.era, self.year, 'Reco')):
            return 'Reco'
        else:
            return 'noskim'


    def getSampleDict(self, in_file_name):
        sample_infos = [line.split('%')[0].strip() for line in open(in_file_name)]                     # Strip % comments and \n charachters
        sample_infos = [line.split() for line in sample_infos if line] 
        sample_info_dict = {}
        for info in sample_infos:
            if info[0] in getListOfSampleNames(self.path):
                sample_info_dict[info[0]] = info[1]
        # Add extension files if this is noskim
        # For the Gen and Reco skims, the skimmer already included those to be added in the final sample
        if self.skim == 'noskim':
            for info in sample_info_dict.keys():
                ext_files = [x for x in getListOfSampleNames(self.path) if info+'-ext' in x]
                for ext_file in ext_files:
                    sample_info_dict[ext_file] = sample_info_dict[info]
        return sample_info_dict

    def getSample(self, name):
        sample = getSampleFromList(self.sample_list, name)
        self.sample_list = self.createSampleList()
        return sample

    def makeLumiClusters(self):
        self.lumi_clusters = {}
        for n in self.sample_names:
            if 'ext' in n:
                tmp_sample_name = n.rsplit('-', 1)[0]
            else:
                tmp_sample_name = n
            
            if not tmp_sample_name in self.lumi_clusters.keys():
                self.lumi_clusters[tmp_sample_name] = [tmp_sample_name]
            else:
                self.lumi_clusters[tmp_sample_name].append(n)
        return self.lumi_clusters   

    def getPath(self, name):
        sample_infos = [line.split('%')[0].strip() for line in open(self.path)]                     # Strip % comments and \n charachters
        sample_infos = [line.split() for line in sample_infos if line]                              # Get lines into tuples
        for sample in sample_infos:
            if sample[0] == name:
                path = sample[1]
                if self.skim_selection is not None:
                    path = path.replace('$SKIMSELECTION$', self.skim_selection)
                if self.region is not None:
                    path = path.replace("$REGION$", self.region)
                return path
        return None      

    def getOutputs(self):  
        sample_infos = [line.split('%')[0].strip() for line in open(self.path)]                     # Strip % comments and \n charachters
        sample_infos = [line.split() for line in sample_infos if line] 
        sample_infos = [info[2] for info in sample_infos if info[0] in self.sample_names]
        output_set = {info for info in sample_infos}
        return output_set

    #
    #       create list of samples from input file
    #
    def createSampleList(self):
        sample_infos = [line.split('%')[0].strip() for line in open(self.path)]                     # Strip % comments and \n charachters
        sample_infos = [line.split() for line in sample_infos if line]                              # Get lines into tuples
        for name, path, output, split_jobs, xsec in sample_infos:
            if name not in self.sample_names: continue
            try:
                split_jobs
            except:
                continue

            if self.skim_selection is not None:
                path = path.replace('$SKIMSELECTION$', self.skim_selection)
            if self.region is not None:
                path = path.replace("$REGION$", self.region)

            if name in self.sample_names:
                split_jobs += '*' + str(self.sample_dict[name])

            if not self.need_skim_samples: 
                yield Sample(name, path, output, split_jobs, xsec)
            else:
                yield SkimSample(name, path, output, split_jobs, xsec)

if __name__ == '__main__':
    sample_manager = SampleManager(2016, 'noskim', 'test')

    s = sample_manager.getSample('ZZTo4L')
    print s.name, s.xsec
    s = sample_manager.getSample('TTJets-Dilep')
    print s.name, s.xsec
    s = sample_manager.getSample('ZZTo4L')
    print s.name, s.xsec
    print sample_manager.getSampleDict(BASE_PATH+'/Sublists/test.conf')
    print sample_manager.makeLumiClusters()