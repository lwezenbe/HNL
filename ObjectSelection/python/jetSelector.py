from HNL.Tools.helpers import deltaR
#
#       Defines jet WP and b-tagging
#
def isCleanFromLightLeptons(chain, index):
    for l in xrange(chain._nLight):
        if chain._lFlavor == 1 and not isLooseMuon(chain, l):    continue
        if chain._lFlavor == 0 and not isLooseElectron(chain, l):    continue
        if deltaR(chain._lEta[l], chain._jetEta[index], chain._lPhi[l], chain._jetPhi[index]) < 0.4: return False
    return True

def isGoodJet(chain, index):
    if chain._jetPt[index] < 25:        return False
    if abs(chain._jetEta[index]) > 2.4: return False
    if not chain._jetIsTight[index]:    return False
    if not isCleanFromLightLeptons(chain, index):       return False
    return True

from bTagWP import getBTagWP, readBTagValue
def isBJet(chain, index, algo, wp):
    if readBTagValue(chain, index, algo) < getBTagWP(chain.year, wp, algo): return False
    return True
    

