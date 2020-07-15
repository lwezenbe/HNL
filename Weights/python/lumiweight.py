from HNL.Samples.sample import getListOfPathsWithSameOutput 
LUMINOSITY_MAP = {
                    # 2016 : 35546.,
                    2016 : 35900.,
                    2017 : 41529.548819,
                    2018 : 59688.059536,
                    }

class LumiWeight:

    def __init__(self, sample, sample_manager, skimmed = False):
        self.sample = sample
        self.skimmed = skimmed

        if not self.skimmed and not self.sample.is_data: 
            self.lumi_cluster = sample_manager.makeLumiClusters()[sample.shavedName()]
            self.total_hcount = 0

            for cl_name in self.lumi_cluster:
                tmp_path = sample_manager.getPath(cl_name)
                self.total_hcount += self.sample.getHist('hCounter', tmp_path).GetSumOfWeights()

    def getLumiWeight(self):
        if self.skimmed:
            return self.sample.chain.lumiweight
        elif self.sample.is_data:
            return 1.
        else:
            try:
                return self.sample.chain.lumiweight
            except:
                self.lumi_weight = self.sample.chain._weight*(self.sample.xsec*LUMINOSITY_MAP[self.sample.chain.year])/self.total_hcount
                self.sample.chain.lumiweight = self.lumi_weight
                return self.lumi_weight 

if __name__ == '__main__':
    from HNL.Samples.sample import createSampleList, getSampleFromList
    from HNL.Samples.sampleManager import *
    import os

    sample_manager = SampleManager(2016, 'noskim', 'test')

    # sample = sample_manager.getSample('DYJetsToLL-M-10to50')
    sample = sample_manager.getSample('ZZTo4L')

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
