from HNL.Samples.sample import *
import os


ALLOWED_SKIMS = ['noskim', 'Reco', 'Gen']
BASE_PATH = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Samples', 'InputFiles')


class SampleManager:


    def __init__(self, year, skim, sample_names_file):
        if not skim in ALLOWED_SKIMS:
            raise RuntimeError("skim "+skim+" not allowed in the sample manager")
        self.year = year
        self.skim = skim
        self.path = os.path.join(BASE_PATH, '_'.join(['sampleList', str(self.year), skim+'.conf']))

        sample_names_file_full = os.path.join(BASE_PATH, 'Sublists', sample_names_file+'.conf')
        self.sample_names = self.getSampleNames(sample_names_file_full)
        self.sample_list = createSampleList(self.path)

    def getSampleNames(self, in_file_name):
        sample_infos = [line.split('%')[0].strip() for line in open(in_file_name)]                     # Strip % comments and \n charachters
        sample_infos = [line for line in sample_infos if line]                              
        return sample_infos

    def getSample(self, name):
        sample = getSampleFromList(self.sample_list, name)
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
            if sample[0] == name: return sample[1]
        return None        


if __name__ == '__main__':
    sample_manager = SampleManager(2018, 'noskim', BASE_PATH+'/Sublists/test.conf')

    s = sample_manager.getSample('ZZTo4L')
    print s.name, s.xsec
    s = sample_manager.getSample('TTJets-Dilep')
    print s.name, s.xsec
    s = sample_manager.getSample('ZZTo4L')
    print s.name, s.xsec
    print sample_manager.getSampleNames(BASE_PATH+'/Sublists/test.conf')
    print sample_manager.makeLumiClusters()