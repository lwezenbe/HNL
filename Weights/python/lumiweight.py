LUMINOSITY_MAP = {
                    # 2016 : 35546.,
                    # 2016 : 35900.,
                    # 2016 : 35545.499064,
                    'prelegacy2016' : 35920.,
                    'prelegacy2017' : 41529.548819,
                    'prelegacy2018' : 59688.059536,
                    'UL2016pre' : 19500.,
                    'UL2016post' : 16800.,
                    'UL2017' : 41480.,
                    'UL2018' : 59830.,
                    }

class LumiWeight:

    def __init__(self, sample, sample_manager, recalculate = False):
        self.sample = sample
        self.skimmed = sample_manager.skim != 'noskim'
        self.recalculate = recalculate

        if (not self.skimmed or recalculate) and not self.sample.is_data: 
            self.lumi_cluster = sample_manager.makeLumiClusters()[sample.shavedName()]
            self.total_hcount = 0

            for cl_name in self.lumi_cluster:
                tmp_path = sample_manager.getPath(cl_name)
                self.total_hcount += self.sample.getHist('hCounter', tmp_path).GetSumOfWeights()
        elif self.skimmed:
            self.total_hcount = self.sample.getHist('hCounter')

    def getLumiWeight(self):
        if self.sample.is_data:
            return 1.
        elif not self.skimmed or self.recalculate:
            #the _weight is needed because otherwise the hcounter might be wrong for the denominator
            self.lumi_weight = self.sample.chain._weight*(self.sample.xsec*LUMINOSITY_MAP[self.sample.chain.era+self.sample.chain.year])/self.total_hcount
            return self.lumi_weight 
        else:
            try:
                return self.sample.chain.lumiweight
            except:
                self.lumi_weight = self.sample.chain._weight*(self.sample.xsec*LUMINOSITY_MAP[self.sample.chain.era+self.sample.chain.year])/self.total_hcount.GetSumOfWeights()
                return self.lumi_weight 


if __name__ == '__main__':
    from HNL.Samples.sampleManager import SampleManager
    from HNL.Tools.logger import getLogger, closeLogger
    log = getLogger('INFO')

    sm = SampleManager(2016, 'noskim', 'fulllist_2016')

    # s = sm.getSample('ZZTo4L')
    s = sm.getSample('HNL-tau-m800')
    # s = sm.getSample('DYJetsToLL-M-50')

    chain = s.initTree()
    lw = LumiWeight(s, sm)
    chain.GetEntry(5)
    chain.year = '2016'
    chain.era = 'prelegacy'
    print s.name
    print lw.getLumiWeight() 
    print 'chain._weight: ', chain._weight, 'expected -41444.199'
    print 'xsec ', s.xsec, lw.sample.xsec, 'expected 18610'
    print 'luminosity ', LUMINOSITY_MAP[chain.year], 'expected 35546.'
    print 'hCount ', s.hcount, lw.total_hcount, 'more than 2.05023673303e+12'

    closeLogger(log)
