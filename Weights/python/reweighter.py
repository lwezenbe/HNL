from HNL.Weights.lumiweight import LumiWeight
from HNL.Weights.puReweighting import returnPUWeightReader
from HNL.Weights.bTagWeighter import getReweightingFunction as btagReweighter
from HNL.Weights.electronSF import ElectronRecoSFJSON
from HNL.ObjectSelection.tauSelector import getTauAlgoWP
from HNL.Weights.fakeRateWeights import returnFakeRateCollection
import numpy as np

var_weights = { 
        'lumiWeight':          (lambda c : c.lumiWeight,      np.arange(0., 2., .1),         ('lumi weight', 'Events')), 
        'puWeight':          (lambda c : c.puWeight,      np.arange(0.8, 1.21, .01),         ('PU weight', 'Events')), 
        'electronRecoWeight':          (lambda c : c.electronRecoWeight,      np.arange(0.8, 1.21, 0.01),         ('Electron reco weight', 'Events')), 
        'tauSFWeight':          (lambda c : c.tauSFWeight,      np.arange(0., 2., .1),         ('Tau SF weight', 'Events')), 
        'btagWeight':          (lambda c : c.btagWeight,      np.arange(0.5, 1.5, .01),         ('btag weight', 'Events')), 
} 

class Reweighter:
    
    WEIGHTS_TO_USE = var_weights.keys()

    def __init__(self, sample, sample_manager):
        self.sample = sample
        self.sample_manager = sample_manager

        #lumi weights
        self.lumiweighter = LumiWeight(sample, sample_manager)

        # pu weights
        if not sample.is_data:
            self.puReweighting      = returnPUWeightReader(sample.chain.era, sample.chain.year)

            if self.sample.chain.era != 'prelegacy': self.btagReweighting = btagReweighter('Deep', self.sample.chain.era, self.sample.chain.year, 'loose', self.sample.chain.selection)

            self.electronSF = ElectronRecoSFJSON(self.sample.chain.era, self.sample.chain.year)

            #
            # Tau SF
            #
            from HNL.Weights.tauSF import TauSF
            tau_algo, tau_wp = getTauAlgoWP(self.sample.chain)
            self.tauSF = TauSF(sample.chain.era, sample.chain.year, tau_algo, tau_wp[0], tau_wp[1], tau_wp[2])


        self.fakerate_collection = None

    def returnBranches(self):
        return ['{0}/F'.format(weight) for weight in self.WEIGHTS_TO_USE]

    def getPrefireWeight(self, syst = 'nominal'):
        if syst == 'nominal':
            return self.sample.chain._prefireWeight
        if syst == 'up':
            return self.sample.chain._prefireWeightUp
        if syst == 'down':
            return self.sample.chain._prefireWeightDown

    def getLumiWeight(self):
        return self.lumiweighter.getLumiWeight()

    def getPUWeight(self, syst = 'nominal'):
        if not self.sample.is_data:
            return self.puReweighting.readValue(self.sample.chain._nTrueInt, syst)
        else:
            return 1.

    def getFakeRateWeight(self, tau_method = None):
        try:
            return self.fakerate_collection.getFakeWeight()
        except:
            self.fakerate_collection = returnFakeRateCollection(self.sample.chain, tau_method = tau_method)
            return self.fakerate_collection.getFakeWeight()

    def getBTagWeight(self, syst = 'nominal'):
        if not self.sample.is_data and self.sample.chain.is_reco_level and self.sample.chain.era != 'prelegacy':
            return self.btagReweighting(self.sample.chain, syst)
        else:
            return 1.

    def getElectronRecoSF(self, syst = 'nominal'):
        if not self.sample.is_data and self.sample.chain.is_reco_level:
            return self.electronSF.getTotalRecoSF(self.sample.chain, syst)
        else:
            return 1.        

    def getTauSF(self, syst = 'nominal'):
        if not self.sample.is_data and self.sample.chain.is_reco_level:
            return self.tauSF.getTotalSF(self.sample.chain, syst)
        else:
            return 1.        

    def returnWeight(self, weight_name, syst = 'nominal'):
        if weight_name == 'lumiWeight':
            return self.getLumiWeight()
        if weight_name == 'puWeight':
            return self.getPUWeight(syst=syst)
        if weight_name == 'electronRecoWeight':
            return self.getElectronRecoSF(syst=syst)
        if weight_name == 'tauSFWeight':
            return self.getTauSF(syst=syst)
        if weight_name == 'btagWeight':
            return self.getBTagWeight(syst=syst)


    def getTotalWeight(self, sideband=False, tau_fake_method = None):
        tot_weight = 1.
        for weight in self.WEIGHTS_TO_USE:
            tot_weight *= self.returnWeight(weight)
        if sideband:
            tot_weight *= self.getFakeRateWeight(tau_method = tau_fake_method)
        #tot_weight *= self.getPrefireWeight()
        return tot_weight

    def fillTreeWithWeights(self, chain):
        for weight in self.WEIGHTS_TO_USE:
            chain.setTreeVariable(weight, self.returnWeight(weight))

if __name__ == '__main__':
    from HNL.Samples.sampleManager import SampleManager
    from HNL.ObjectSelection.objectSelection import getObjectSelection
    from HNL.Tools.logger import getLogger, closeLogger
    log = getLogger('INFO')

    # era = 'prelegacy'
    era = 'UL'

    sm = SampleManager(era, '2017', 'Reco', 'fulllist_{0}2017_mconly'.format(era))
    # sm = SampleManager(era, '2017', 'noskim', 'fulllist_{0}2017_mconly'.format(era))

    # s = sm.getSample('ZZTo4L')
    # s = sm.getSample('HNL-mu-m40')
    s = sm.getSample('ST-s-channel')

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

    chain.GetEntry(7)
    print 'b-tag weight', reweighter.getBTagWeight()
    # print 'electron weight', reweighter.getElectronRecoSF()
    # print 'tau weight', reweighter.getTauSF()

    print chain._nTrueInt

    closeLogger(log)
