import os

from HNL.Tools.logger import getLogger
log = getLogger()

#
#Electron RECO (tracking) scale factor using JSON
# Similar file for muons does not exist, the recommendation by the POG is to not apply them for muons since they are
# close to 1
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/MuonUL2016#Tracking_efficiency
#

prelegacy_dict = {
    ('2016', 'ptBelow20'):  '2016EGM2D_BtoH_low_RecoSF_Legacy2016.root',
    ('2016', 'ptAbove20'):  '2016EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root',
    ('2017', 'ptBelow20'):  '2017egammaEffi.txt_EGM2D_runBCDEF_passingRECO_lowEt.root',
    ('2017', 'ptAbove20'):  '2017egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root',
    ('2018', 'ptBelow20'):  '2018egammaEffi.txt_EGM2D_updatedAll.root',
    ('2018', 'ptAbove20'):  '2018egammaEffi.txt_EGM2D_updatedAll.root',
}

class ElectronRecoSF:

    NAME_DICT = {
        'UL2016pre' : 'UL2016preVFP',
        'UL2016post' : 'UL2016postVFP',
        'UL2017' : 'UL2017',
        'UL2018' : 'UL2018'
    }

    def __init__(self, era, year):

        from HNL.Tools.helpers import getObjFromFile
        if era == 'UL':
            self.root_file_location = lambda pt_str : os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Weights', 'data', 'RecoSF', 'Electron', 'egammaEffi_{0}.txt_EGM2D_{1}.root'.format(pt_str,self.NAME_DICT[era+year])))
        else:
            self.root_file_location = lambda pt_str : os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Weights', 'data', 'RecoSF', 'Electron', prelegacy_dict[(year, pt_str)]))
        
        self.below20_hist = getObjFromFile(self.root_file_location('ptBelow20'), 'EGamma_SF2D')
        self.above20_hist = getObjFromFile(self.root_file_location('ptAbove20'), 'EGamma_SF2D')

        self.e_ptMax  = self.above20_hist.GetYaxis().GetXmax()
        self.e_ptMin  = self.below20_hist.GetYaxis().GetXmin()

        self.e_etaMax = self.below20_hist.GetXaxis().GetXmax()
        self.e_etaMin = self.below20_hist.GetXaxis().GetXmin()
    
    def getSingleRecoSF(self, chain, index):
        eta = chain._lEtaSC[index]
        pt = chain._lPt[index]

        if not eta <= self.e_etaMax: 
            log.warning("Supercluster eta out of bounds: %3.2f (need %3.2f <= eta <=% 3.2f)", eta, self.e_etaMin, self.e_etaMax)
            eta = self.e_etaMax
        if not eta > self.e_etaMin:
            log.warning("Supercluster eta out of bounds: %3.2f (need %3.2f <= eta <=% 3.2f)", eta, self.e_etaMin, self.e_etaMax)
            eta = self.e_etaMin + 0.0001

        if pt > self.e_ptMax:    pt = self.e_ptMax - 1. 
        elif pt <= self.e_ptMin: pt = self.e_ptMin + 1.

        if chain._lPt[index] < 20:
            return self.below20_hist.GetBinContent(self.below20_hist.FindBin(eta, pt))
        else:
            return self.above20_hist.GetBinContent(self.above20_hist.FindBin(eta, pt))

    def getTotalRecoSF(self, chain):
        from HNL.ObjectSelection.electronSelector import isGoodElectron

        sf = 1.
        for e in xrange(chain._nMu, chain._nLight):
            if isGoodElectron(chain, e, workingpoint='loose'):
        #        print e, self.getSingleRecoSF(chain, e)
                sf *= self.getSingleRecoSF(chain, e)
        
        return sf
