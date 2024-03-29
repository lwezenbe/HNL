#
# Is good lepton on generator level
#
from HNL.ObjectSelection.electronSelector import isGoodGenElectron
from HNL.ObjectSelection.muonSelector import isGoodGenMuon
from HNL.ObjectSelection.tauSelector import isGoodGenTau

def isGoodGenLepton(chain, index):
    if chain._gen_lFlavor[index] == 0:       return isGoodGenElectron(chain, index)
    if chain._gen_lFlavor[index] == 1:       return isGoodGenMuon(chain, index)
    if chain._gen_lFlavor[index] == 2:       return isGoodGenTau(chain, index)
    else:
        return False


def getLeptonPt(chain, index, syst=None):
    if chain._lFlavor[index] == 0:
        from HNL.ObjectSelection.electronSelector import getElectronPt
        return getElectronPt(chain, index, syst)
    elif chain._lFlavor[index] == 1:
        from HNL.ObjectSelection.muonSelector import getMuonPt
        return getMuonPt(chain, index, syst)
    else:
        return chain._lPt[index]

def getLeptonE(chain, index, syst=None):
    if chain._lFlavor[index] == 0:
        from HNL.ObjectSelection.electronSelector import getElectronE
        return getElectronE(chain, index, syst)
    elif chain._lFlavor[index] == 1:
        from HNL.ObjectSelection.muonSelector import getMuonE
        return getMuonE(chain, index, syst)
    else:
        return chain._lE[index]
#
# Selector for light leptons
#
from HNL.ObjectSelection.electronSelector import isGoodElectron
from HNL.ObjectSelection.muonSelector import isGoodMuon
from HNL.ObjectSelection.tauSelector import isGoodTau

def isGoodLightLepton(chain, index, workingpoint = None, syst=None):
    if chain._lFlavor[index] == 0:
        return isGoodElectron(chain, index, workingpoint=workingpoint, syst=syst)
    elif chain._lFlavor[index] == 1:
        return isGoodMuon(chain, index, workingpoint=workingpoint, syst=syst)
    else:
        return False

#
# Selector for all leptons
#
def isGoodLepton(chain, index, workingpoint = None, syst=None):
    if chain._lFlavor[index] == 0 or chain._lFlavor[index] == 1:
        return isGoodLightLepton(chain, index, workingpoint=workingpoint, syst=syst)
    elif chain._lFlavor[index] == 2:
        return isGoodTau(chain, index, workingpoint=workingpoint)
    else:
        return False


#
# general functions for lepton ID comparison
#
def isGoodLightLeptonGeneral(chain, index, workingpoint = None, algo = None, syst = None):
    if chain._lFlavor[index] == 0:
        return isGoodElectron(chain, index, workingpoint=workingpoint, algo=algo, syst=syst)
    elif chain._lFlavor[index] == 1:
        return isGoodMuon(chain, index, workingpoint=workingpoint, algo=algo, syst=syst)
    else:
        return False

def isGoodLeptonGeneral(chain, index, workingpoint = None, algo = None, syst = None):
    if chain._lFlavor[index] == 0:
        return isGoodElectron(chain, index, workingpoint=workingpoint, algo=algo, syst=syst)
    elif chain._lFlavor[index] == 1:
        return isGoodMuon(chain, index, workingpoint=workingpoint, algo=algo, syst=syst)
    elif chain._lFlavor[index] == 2:
        return isGoodTau(chain, index, workingpoint=workingpoint, algo=algo)
    else:
        return False


def isFakeLepton(chain, index):
    from HNL.ObjectSelection.tauSelector import isJetFakingTau
    from HNL.ObjectSelection.electronSelector import isFakeElectron
    from HNL.ObjectSelection.muonSelector import isFakeMuon

    if chain._lFlavor[index] == 0: return isFakeElectron(chain, index)
    if chain._lFlavor[index] == 1: return isFakeMuon(chain, index)
    if chain._lFlavor[index] == 2: return isJetFakingTau(chain, index)
    return False

#
# Cone correction
#
from HNL.ObjectSelection.tauSelector import tauConeCorrection
from HNL.ObjectSelection.electronSelector import electronConeCorrection
from HNL.ObjectSelection.muonSelector import muonConeCorrection
def coneCorrection(chain, index, algo = None):
    if chain._lFlavor[index] == 0: return electronConeCorrection(chain, index, algo)
    if chain._lFlavor[index] == 1: return muonConeCorrection(chain, index, algo)
    if chain._lFlavor[index] == 2: return tauConeCorrection(chain, index, algo)


FLAVOR_DICT = {
    'e'     :   0,
    'mu'    :   1,
    'tau'   :   2
}

def isBaseLepton(chain, index, syst = None):
    from HNL.ObjectSelection.tauSelector import isBaseTau
    from HNL.ObjectSelection.electronSelector import isBaseElectron
    from HNL.ObjectSelection.muonSelector import isBaseMuon

    if chain._lFlavor[index] == 0: return isBaseElectron(chain, index, syst)
    if chain._lFlavor[index] == 1: return isBaseMuon(chain, index, syst)
    if chain._lFlavor[index] == 2: return isBaseTau(chain, index)    
