#
#Tau scale factor class using the tau POG tool
#

from TauPOG.TauIDSFs.TauIDSFTool import TauIDSFTool
from HNL.ObjectSelection.tauSelector import getCorrespondingLightLepDiscr

YEARLIB = {2016 : '2016Legacy',
            2017: '2017ReReco',
            2018: '2018ReReco'}

ISOLIB= {'deeptauVSjets' : 'DeepTau2017v2p1VSjet', 'MVA2017v2': 'MVAoldDM2017v2'}
ELIB= {'deeptauVSe' : 'DeepTau2017v2p1VSe', 'againstElectron': 'antiEleMVA6'}
MULIB= {'deeptauVSmu' : 'DeepTau2017v2p1VSmu', 'againstMuon': 'antiMu3'}

class TauSF:
    
    def __init__(self, chain, year, algorithm, wp_iso, wp_e, wp_mu):
        self.sftool_iso = TauIDSFTool(YEARLIB[year], ISOLIB[algorithm], wp_iso.title())
        self.sftool_e = TauIDSFTool(YEARLIB[year], ELIB[getCorrespondingLightLepDiscr(algorithm)[0]], wp_e.title())
        self.sftool_mu = TauIDSFTool(YEARLIB[year], MULIB[getCorrespondingLightLepDiscr(algorithm)[1]], wp_mu.title())

    def getSF(chain, index):
        if chain._tauGenStatus[index] == 1 or chain._tauGenStatus[index] == 3:
            return self.sftool_e.getSFvsEta(chain._lEta[index],chain._tauGenStatus[index])
        elif chain._tauGenStatus[index] == 2 or chain._tauGenStatus[index] == 4:
            return self.sftool_mu.getSFvsEta(chain._lEta[index],chain._tauGenStatus[index])
        elif chain._tauGenStatus[index] == 5:
            return self.sftool_iso.getSFvsPT(chain._lPt[index],chain._tauGenStatus[index])
        else:
            return 1.
