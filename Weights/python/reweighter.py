from HNL.Weights.lumiweight import LumiWeight
from HNL.Weights.puReweighting import getReweightingFunction
from HNL.Weights.fakeRateWeights import returnFakeRateCollection

class Reweighter:

    def __init__(self, sample, sample_manager):
        self.sample = sample
        self.sample_manager = sample_manager

        #lumi weights
        self.lumiweighter = LumiWeight(sample, sample_manager)

        # pu weights
        if not sample.is_data:
            self.puReweighting     = getReweightingFunction(sample.chain.era, sample.chain.year, 'central')
            self.puReweightingUp   = getReweightingFunction(sample.chain.era, sample.chain.year, 'up')
            self.puReweightingDown = getReweightingFunction(sample.chain.era, sample.chain.year, 'down')

        self.fakerate_collection = None

    def getLumiWeight(self):
        return self.lumiweighter.getLumiWeight()

    def getPUWeight(self):
        if not self.sample.is_data:
            return self.puReweighting(self.sample.chain._nTrueInt)
        else:
            return 1.

    def getFakeRateWeight(self):
        try:
            return self.fakerate_collection.getFakeWeight()
        except:
            self.fakerate_collection = returnFakeRateCollection(self.sample.chain)
            return self.fakerate_collection.getFakeWeight()


    def getTotalWeight(self, sideband=False):
        tot_weight = 1.
        tot_weight *= self.getLumiWeight()
        tot_weight *= self.getPUWeight()
        if sideband:
            tot_weight *= self.getFakeRateWeight()
        return tot_weight



if __name__ == '__main__':
    from HNL.Samples.sampleManager import SampleManager
    from HNL.Tools.logger import getLogger, closeLogger
    log = getLogger('INFO')

    sm = SampleManager('UL', '2017', 'Reco', 'fulllist_UL2017_mconly')

    s = sm.getSample('ZZTo4L')

    chain = s.initTree()
    chain.GetEntry(5)
    chain.year = '2017'
    chain.era = 'UL'
    reweighter = Reweighter(s, sm)


    print s.name
    print reweighter.getLumiWeight() 
    print reweighter.getPUWeight() 
    print reweighter.getTotalWeight() 

    print chain._nTrueInt

    closeLogger(log)