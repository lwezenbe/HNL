from HNL.Weights.lumiweight import LumiWeight
from HNL.Weights.puReweighting import getReweightingFunction

class Reweighter:

    def __init__(self, sample, sample_manager):
        self.sample = sample
        self.sample_manager = sample_manager

        #lumi weights
        self.lumiweighter = LumiWeight(sample, sample_manager)

        #pu weights
        if not sample.is_data:
            self.puReweighting     = getReweightingFunction(sample.chain.year, 'central')
            self.puReweightingUp   = getReweightingFunction(sample.chain.year, 'up')
            self.puReweightingDown = getReweightingFunction(sample.chain.year, 'down')

    def getLumiWeight(self):
        return self.lumiweighter.getLumiWeight()

    def getPUWeight(self):
        if not self.sample.is_data:
            return self.puReweighting(self.sample.chain._nTrueInt)
        else:
            return 1.

    def getTotalWeight(self):
        tot_weight = 1.
        # try:
        #     tot_weight *= self.sample.chain._weight
        # except:
        #     pass
        tot_weight *= self.getLumiWeight()
        tot_weight *= self.getPUWeight()

        return tot_weight



if __name__ == '__main__':
    from HNL.Samples.sample import createSampleList, getSampleFromList
    from HNL.Samples.sampleManager import SampleManager
    import os
    from HNL.Tools.logger import getLogger, closeLogger
    log = getLogger('INFO')

    sm = SampleManager(2016, 'noskim', 'test')

    s = sm.getSample('ZZTo4L')

    chain = s.initTree()
    chain.GetEntry(5)
    chain.year = 2016
    reweighter = Reweighter(s, sm)


    print s.name
    print reweighter.getLumiWeight() 
    print reweighter.getPUWeight() 
    print reweighter.getTotalWeight() 

    print chain._nTrueInt

    closeLogger(log)