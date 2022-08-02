def getLeptonEta(chain, index):
    if chain._lFlavor[index] == 0:
        return chain._lEtaSC[index]
    if chain._lFlavor[index] == 1:
        return abs(chain._lEta[index])

import os
from HNL.Tools.logger import getLogger
log = getLogger()

class LeptonIDSF(object):

    def __init__(self, sf_hist):
        self.ptMax  = sf_hist.GetYaxis().GetXmax()
        self.ptMin  = sf_hist.GetYaxis().GetXmin()

        self.etaMax = sf_hist.GetXaxis().GetXmax()
        self.etaMin = sf_hist.GetXaxis().GetXmin()

    def getSingleSF(self, pt, eta, syst = 'nominal'):
        if not eta <= self.etaMax:
            log.warning("Lepton eta out of bounds: %3.2f (need %3.2f <= eta <=% 3.2f)", eta, self.etaMin, self.etaMax)
            eta = self.etaMax
        if not eta > self.etaMin:
            log.warning("Lepton eta out of bounds: %3.2f (need %3.2f <= eta <=% 3.2f)", eta, self.etaMin, self.etaMax)
            eta = self.etaMin + 0.0001

        if pt > self.ptMax:    pt = self.ptMax - 1.
        elif pt <= self.ptMin: pt = self.ptMin + 1.

        if syst == 'nominal':
            return self.sf_hist.GetBinContent(self.sf_hist.FindBin(eta, pt))
        elif syst == 'statup':
            return self.sf_hist.GetBinContent(self.sf_hist.FindBin(eta, pt)) + self.stat_hist.GetBinContent(self.stat_hist.FindBin(eta, pt))
        elif syst == 'statdown':
            return self.sf_hist.GetBinContent(self.sf_hist.FindBin(eta, pt)) - self.stat_hist.GetBinContent(self.stat_hist.FindBin(eta, pt))
        elif syst == 'systup':
            return self.sf_hist.GetBinContent(self.sf_hist.FindBin(eta, pt)) + self.syst_hist.GetBinContent(self.syst_hist.FindBin(eta, pt))
        elif syst == 'systdown':
            return self.sf_hist.GetBinContent(self.sf_hist.FindBin(eta, pt)) - self.syst_hist.GetBinContent(self.syst_hist.FindBin(eta, pt))
        else:
            raise RuntimeError('Unknown syst {0} in lepton ID'.format(syst))

    def getTotalSF(self, chain, flavor, syst = 'nominal'):
        total_sf = 1.
        for l in chain.l_indices:
            if chain._lFlavor[l] == flavor: 
                eta = getLeptonEta(chain, l)
                from HNL.ObjectSelection.leptonSelector import getLeptonPt
                pt = getLeptonPt(chain, l)
                total_sf *= self.getSingleSF(pt, eta, syst)
                self.getSingleSF(pt, eta, syst), total_sf
        return total_sf

class ElectronIDSF(LeptonIDSF):

    working_point_dict = {
        'loose' : 'VLoose',
        'FO'    : 'VLoose',
        'tight' : 'Medium'
    }

    def __init__(self, era, year, working_point):
        if era == 'UL':
            #tmp prelegacy
            if '2016' in year: year = '2016'
            root_file_location = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Weights', 'data', 'IDSF', 'Electron', 'prelegacy', year, 'passingLeptonMva'+self.working_point_dict[working_point], 'egammaEffi.txt_EGM2D.root'))
        else:
            root_file_location = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Weights', 'data', 'IDSF', 'Electron', 'prelegacy', year, 'passingLeptonMva'+self.working_point_dict[working_point], 'egammaEffi.txt_EGM2D.root'))
        from HNL.Tools.helpers import getObjFromFile
        self.sf_hist = getObjFromFile(root_file_location, 'EGamma_SF2D')
        self.stat_hist = getObjFromFile(root_file_location, 'stat')
        self.syst_hist = getObjFromFile(root_file_location, 'sys')
        super(ElectronIDSF, self).__init__(self.sf_hist)

    def getTotalSF(self, chain, syst = 'nominal'):
        return super(ElectronIDSF, self).getTotalSF(chain, 0, syst)

class MuonIDSF(LeptonIDSF):

    working_point_dict = {
        'loose' : 'VLoose',
        'FO'    : 'Loose',
        'tight' : 'Medium040'
    }

    def __init__(self, era, year, working_point):
        if era == 'UL':
            #tmp prelegacy
            if '2016' in year: year = '2016'
            root_file_location = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Weights', 'data', 'IDSF', 'Muon', 'prelegacy', year, self.working_point_dict[working_point], 'muonTOPLeptonMVA{0}{1}.root'.format(self.working_point_dict[working_point], year)))
        else:
            root_file_location = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Weights', 'data', 'IDSF', 'Muon', 'prelegacy', year, self.working_point_dict[working_point], 'muonTOPLeptonMVA{0}{1}.root'.format(self.working_point_dict[working_point], year)))
        from HNL.Tools.helpers import getObjFromFile
        self.sf_hist = getObjFromFile(root_file_location, 'SF')
        self.stat_hist = getObjFromFile(root_file_location, 'SFTotStat')
        self.syst_hist = getObjFromFile(root_file_location, 'SFTotSys')
        super(MuonIDSF, self).__init__(self.sf_hist)

    def getTotalSF(self, chain, syst = 'nominal'):
        return super(MuonIDSF, self).getTotalSF(chain, 1, syst)