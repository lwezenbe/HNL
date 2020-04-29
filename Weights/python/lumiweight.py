from HNL.Samples.sample import getListOfPathsWithSameOutput 
LUMINOSITY_MAP = {
                    2016 : 35546.,
                    2017 : 41529.548819,
                    2018 : 59688.059536,
                    }

class LumiWeight:

    def __init__(self, sample, sample_manager):
        self.sample = sample
        self.lumi_weight = 1.  

        self.lumi_cluster = sample_manager.makeLumiClusters()[sample.shavedName()]
        self.total_hcount = 0

        for cl_name in self.lumi_cluster:
            tmp_path = sample_manager.getPath(cl_name)
            self.total_hcount += self.sample.getHist('hCounter', tmp_path).GetSumOfWeights()

        # for path_name in getListOfPathsWithSameOutput(input_file, self.sample.name):
        #     self.total_hcount += self.sample.getHist('hCounter', path_name).GetSumOfWeights()

    def getLumiWeight(self):
        self.lumi_weight = self.sample.chain._weight*(self.sample.xsec*LUMINOSITY_MAP[self.sample.chain.year])/self.total_hcount
        return self.lumi_weight 

if __name__ == '__main__':
    from HNL.Samples.sample import createSampleList, getSampleFromList
    from HNL.Samples.sampleManager import *
    import os

    sample_manager = SampleManager(2016, 'noskim', 'test')

    sample = sample_manager.getSample('DYJetsToLL-M-10to50')

    chain = sample.initTree()
    lw = LumiWeight(sample, sample_manager)
    chain.GetEntry(5)
    chain.year = 2016
    print sample.name
    print lw.getLumiWeight() 
    print 'chain._weight: ', chain._weight, 'expected -41444.199'
    print 'xsec ', sample.xsec, lw.sample.xsec, 'expected 18610'
    print 'luminosity ', LUMINOSITY_MAP[chain.year], 'expected 35546.'
    print 'hCount ', sample.hcount, lw.total_hcount, 'more than 2.05023673303e+12'
