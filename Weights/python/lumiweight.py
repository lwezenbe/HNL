from HNL.Samples.sample import getListOfPathsWithSameOutput 
LUMINOSITY_MAP = {
                    # 2016 : 35546.,
                    # 2016 : 35900.,
                    # 2016 : 35545.499064,
                    2016 : 35920.,
                    2017 : 41529.548819,
                    2018 : 59688.059536,
                    }

class LumiWeight:

    def __init__(self, sample, sample_manager):
        self.sample = sample
        self.skimmed = sample_manager.skim != 'noskim'

        if not self.skimmed and not self.sample.is_data: 
            self.lumi_cluster = sample_manager.makeLumiClusters()[sample.shavedName()]
            self.total_hcount = 0

            for cl_name in self.lumi_cluster:
                tmp_path = sample_manager.getPath(cl_name)
                self.total_hcount += self.sample.getHist('hCounter', tmp_path).GetSumOfWeights()
        elif self.skimmed:
            self.total_hcount = self.sample.getHist('hCounter')

    def getLumiWeight(self):
        if self.skimmed:
            try:
                return self.sample.chain.lumiweight
            except:
                self.lumi_weight = self.sample.chain._weight*(self.sample.xsec*LUMINOSITY_MAP[self.sample.chain.year])/self.total_hcount.GetSumOfWeights()
                return self.lumi_weight 
        elif self.sample.is_data:
            return 1.
        else:
            #the _weight is needed because otherwise the hcounter might be wrong for the denominator
            self.lumi_weight = self.sample.chain._weight*(self.sample.xsec*LUMINOSITY_MAP[self.sample.chain.year])/self.total_hcount
            return self.lumi_weight 

if __name__ == '__main__':
    from HNL.Samples.sample import createSampleList, getSampleFromList
    from HNL.Samples.sampleManager import SampleManager
    import os
    from HNL.Tools.logger import getLogger, closeLogger
    log = getLogger('INFO')

    sm = SampleManager(2016, 'noskim', 'fulllist_2016')

    # s = sm.getSample('ZZTo4L')
    s = sm.getSample('HNL-tau-m800')
    # s = sm.getSample('DYJetsToLL-M-50')

    chain = s.initTree()
    lw = LumiWeight(s, sm)
    chain.GetEntry(5)
    chain.year = 2016
    print s.name
    print lw.getLumiWeight() 
    print 'chain._weight: ', chain._weight, 'expected -41444.199'
    print 'xsec ', s.xsec, lw.sample.xsec, 'expected 18610'
    print 'luminosity ', LUMINOSITY_MAP[chain.year], 'expected 35546.'
    print 'hCount ', s.hcount, lw.total_hcount, 'more than 2.05023673303e+12'

    closeLogger(log)
