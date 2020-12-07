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

#
# Selector for light leptons
#
from HNL.ObjectSelection.electronSelector import isGoodElectron
from HNL.ObjectSelection.muonSelector import isGoodMuon
from HNL.ObjectSelection.tauSelector import isGoodTau

def isGoodLightLepton(chain, index, workingpoint = None):
    if chain._lFlavor[index] == 0:
        return isGoodElectron(chain, index, workingpoint=workingpoint)
    elif chain._lFlavor[index] == 1:
        return isGoodMuon(chain, index, workingpoint=workingpoint)
    else:
        return False

#
# Selector for all leptons
#
def isGoodLepton(chain, index, workingpoint = None):
    if chain._lFlavor[index] == 0 or chain._lFlavor == 1:
        return isGoodLightLepton(chain, index, workingpoint=workingpoint)
    elif chain._lFlavor[index] == 2:
        return isGoodTau(chain, index, workingpoint=workingpoint)
    else:
        return False

from HNL.ObjectSelection.tauSelector import isJetFakingTau
from HNL.ObjectSelection.electronSelector import isFakeElectron
from HNL.ObjectSelection.muonSelector import isFakeMuon
def isFakeLepton(chain, index):
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