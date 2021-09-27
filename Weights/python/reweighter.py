from HNL.Weights.lumiweight import LumiWeight
from HNL.Weights.puReweighting import getReweightingFunction
from HNL.Weights.bTagWeighter import getReweightingFunction as btagReweighter
from HNL.Weights.electronSF import ElectronRecoSF
from HNL.ObjectSelection.tauSelector import getTauAlgoWP
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

            # if self.sample.chain.era != 'prelegacy': self.btagReweighting = btagReweighter('Deep', self.sample.chain.era, self.sample.chain.year, 'loose', self.sample.chain.selection)

            self.electronSF = ElectronRecoSF(self.sample.chain.era, self.sample.chain.year)

            from HNL.Weights.tauSF import TauSF
            tau_algo, tau_wp = getTauAlgoWP(self.sample.chain)
            self.tauSF = TauSF(sample.chain.era, sample.chain.year, tau_algo, tau_wp[0], tau_wp[1], tau_wp[2])

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

    def getBTagWeight(self):
        if not self.sample.is_data and self.sample.chain.is_reco_level:
            return self.btagReweighting(self.sample.chain)
        else:
            return 1.

    def getElectronRecoSF(self):
        if not self.sample.is_data and self.sample.chain.is_reco_level:
            return self.electronSF.getTotalRecoSF(self.sample.chain)
        else:
            return 1.        

    def getTauSF(self):
        if not self.sample.is_data and self.sample.chain.is_reco_level:
            return self.tauSF.getTotalSF(self.sample.chain)
        else:
            return 1.        

    def getTotalWeight(self, sideband=False):
        tot_weight = 1.
        tot_weight *= self.getLumiWeight()
        tot_weight *= self.getPUWeight()
        tot_weight *= self.getElectronRecoSF()
        tot_weight *= self.getTauSF()
        # if self.sample.chain.era != 'prelegacy': tot_weight *= self.getBTagWeight() #TODO: reskim of prelegacy samples because _jetSmeared not available
        if sideband:
            tot_weight *= self.getFakeRateWeight()
        return tot_weight



if __name__ == '__main__':
    from HNL.Samples.sampleManager import SampleManager
    from HNL.ObjectSelection.objectSelection import getObjectSelection
    from HNL.Tools.logger import getLogger, closeLogger
    log = getLogger('INFO')

    # era = 'prelegacy'
    era = 'UL'

    sm = SampleManager(era, '2017', 'Reco', 'fulllist_{0}2017_mconly'.format(era))
    # sm = SampleManager(era, '2017', 'noskim', 'fulllist_{0}2017_mconly'.format(era))

    s = sm.getSample('ZZTo4L')
    # s = sm.getSample('HNL-mu-m40')

    chain = s.initTree()
    chain.GetEntry(5)
    chain.year = '2017'
    chain.era = era
    chain.selection = 'default'
    chain.is_reco_level = True
    chain.obj_sel = getObjectSelection('default')
    reweighter = Reweighter(s, sm)

    chain.l_indices = xrange(chain._nL)

    print s.name
    print reweighter.getLumiWeight() 
    print reweighter.getPUWeight() 
    print reweighter.getTotalWeight() 

    # chain.GetEntry(7)
    # print 'b-tag weight', reweighter.getBTagWeight()
    # print 'electron weight', reweighter.getElectronRecoSF()
    # print 'tau weight', reweighter.getTauSF()

    print chain._nTrueInt

    closeLogger(log)