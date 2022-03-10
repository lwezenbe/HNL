LUMINOSITY_MAP = {
                    # 2016 : 35546.,
                    # 2016 : 35900.,
                    # 2016 : 35545.499064,
                    'prelegacy2016' : 35920.,
                    'prelegacy2017' : 41529.548819,
                    'prelegacy2018' : 59688.059536,
                    'UL2016pre' : 19520.,
                    'UL2016post' : 16810.,
                    'UL2017' : 41480.,
                    'UL2018' : 59830.,
                    }

class LumiWeight:

    def __init__(self, sample, sample_manager, recalculate = False):
        self.sample = sample
        self.skimmed = sample_manager.skim != 'noskim'
        self.recalculate = recalculate

#        if (not self.skimmed or recalculate) and not self.sample.is_data: 
#            self.lumi_cluster = sample_manager.makeLumiClusters()[sample.shavedName()]
#            self.total_hcount = 0
#
#            for cl_name in self.lumi_cluster:
#                tmp_path = sample_manager.getPath(cl_name) #Getting the hcount from original unskimmed paths because of temporary bug in the hcounters copied to skimmed files
#                self.total_hcount += self.sample.getHist('hCounter', tmp_path).GetSumOfWeights()
#        elif self.skimmed:
#            self.total_hcount = self.sample.getHist('hCounter').GetSumOfWeights()
        
        # Because of bug in weights, always use the hcount from original files
        if not self.sample.is_data:
            if recalculate:
                self.lumi_cluster = sample_manager.makeLumiClusters(noskimpath=True)[sample.shavedName()]
                self.total_hcount = 0

                for cl_name in self.lumi_cluster:
                    tmp_path = sample_manager.getPath(cl_name, noskimpath=True) #Getting the hcount from original unskimmed paths because of temporary bug in the hcounters copied to skimmed files
                    self.total_hcount += self.sample.getHist('hCounter', tmp_path).GetSumOfWeights()

            else:
                year = sample_manager.year
                era = sample_manager.era
                import os, json
                f = open(os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Weights', 'data', 'hcounters', era+year, 'hcounter.json')),)
                weights = json.load(f)
                self.total_hcount = weights[sample.name]
                f.close()

        #self.total_hcount = 1.

    def getLumiWeight(self):
        if self.sample.is_data:
            return 1.
        else:
            self.lumi_weight = self.sample.chain._weight*(self.sample.xsec*LUMINOSITY_MAP[self.sample.chain.era+self.sample.chain.year])/self.total_hcount
            return self.lumi_weight 


        #elif not self.skimmed or self.recalculate:
        #    #the _weight is needed because otherwise the hcounter might be wrong for the denominator
        #    self.lumi_weight = self.sample.chain._weight*(self.sample.xsec*LUMINOSITY_MAP[self.sample.chain.era+self.sample.chain.year])/self.total_hcount
        #    print self.sample.chain._weight, self.sample.xsec, LUMINOSITY_MAP[self.sample.chain.era+self.sample.chain.year], self.total_hcount
        #    return self.lumi_weight 
        #else:
        #    try:
        #        return self.sample.chain.lumiweight
        #    except:
        #        self.recalculate = True
        #        return self.getLumiWeight()


if __name__ == '__main__':
    from HNL.Samples.sampleManager import SampleManager
    from HNL.Tools.logger import getLogger, closeLogger
    log = getLogger('INFO')

    #sm = SampleManager('UL', '2017', 'Reco', 'fulllist_UL2017_mconly')
    sm = SampleManager('UL', '2016pre', 'Reco', 'fulllist_UL2016pre_mconly', skim_selection = 'default')

    s = sm.getSample('WZTo3LNu')
    # s = sm.getSample('HNL-tau-m800')
    # s = sm.getSample('DYJetsToLL-M-50')

    chain = s.initTree()
    lw = LumiWeight(s, sm, recalculate = True)
    lw.total_hcount
    chain.GetEntry(5)
    chain.year = '2016pre'
    chain.era = 'UL'
    print s.name
    print lw.getLumiWeight() 
    print 'chain._weight: ', chain._weight, 'expected -41444.199'
    print 'xsec ', s.xsec, lw.sample.xsec, 'expected 18610'
    print 'luminosity ', LUMINOSITY_MAP[chain.era+chain.year], 'expected 35546.'
    print 'hCount ', s.hcount, lw.total_hcount, 'more than 2.05023673303e+12'

    closeLogger(log)
