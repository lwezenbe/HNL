from HNL.Tools.helpers import deltaR
from HNL.ObjectSelection.leptonSelector import isGoodLepton

#
#       Defines jet WP and b-tagging
#
def isCleanFromLeptons(chain, index, wp):
    for l in xrange(chain._nL):
    # for l in xrange(chain._nLight):
        if not isGoodLepton(chain, l, wp): continue
        if deltaR(chain._lEta[l], chain._jetEta[index], chain._lPhi[l], chain._jetPhi[index]) < 0.4: return False
    return True

def isGoodJetAN2017014(chain, index, cleaned = 'loose'):
    if chain._jetPt[index] < 25:        return False
    if abs(chain._jetEta[index]) > 2.4: return False
    if chain.year != 2018:
        if not chain._jetIsLoose[index]:    return False
    else:
        if not chain._jetIsTight[index]:    return False
    if cleaned is not None and not isCleanFromLeptons(chain, index, cleaned):       return False
    return True

def isGoodJetHNL(chain, index, cleaned = 'loose'):
    if chain._jetPt[index] < 25:        return False
    if abs(chain._jetEta[index]) > 2.4: return False
    if not chain._jetIsTight[index]:    return False
    if cleaned is not None and not isCleanFromLeptons(chain, index, cleaned):       return False
    return True

def isGoodJetHNLLowPt(chain, index, cleaned = 'loose'):
    if chain._jetPt[index] < 25:        return False
    if abs(chain._jetEta[index]) > 2.4: return False
    if not chain._jetIsTight[index]:    return False
    if cleaned is not None and not isCleanFromLeptons(chain, index, cleaned):       return False
    return True

def isGoodJetTTT(chain, index, cleaned = 'loose'):
    if chain._jetSmearedPt[index] < 30:        return False
    # if chain._jetPt[index] < 30:        return False
    if abs(chain._jetEta[index]) > 2.4: return False
    if not chain._jetIsTight[index]:    return False
    if cleaned is not None and not isCleanFromLeptons(chain, index, cleaned):       return False
    return True

def isGoodJetLuka(chain, index, cleaned = 'loose'):
    if chain._jetPt[index] < 25:        return False
    if abs(chain._jetEta[index]) > 5.: return False
    if not chain._jetIsTight[index]:    return False
    if cleaned is not None and not isCleanFromLeptons(chain, index, cleaned):       return False
    return True

from HNL.ObjectSelection.objectSelection import objectSelectionCollection
def checkJetAlgorithm(chain, algo):
    if algo is None:
        try:
            chain.obj_sel
        except:
            #Initiate default object selection
            chain.obj_sel = objectSelectionCollection()
        return chain.obj_sel['jet_algo']
    else:
        return algo

def isGoodJet(chain, index, cleaned = None, selection = None):
    selection = checkJetAlgorithm(chain, selection)

    if selection == 'HNL':
        return isGoodJetHNL(chain, index, cleaned = cleaned)
    elif selection == 'HNLLowPt':
        return isGoodJetHNLLowPt(chain, index, cleaned = cleaned)
    elif selection == 'AN2017014':
        return isGoodJetAN2017014(chain, index, cleaned = cleaned)
    elif selection == 'TTT':
        return isGoodJetTTT(chain, index, cleaned = cleaned)
    elif selection == 'Luka':
        return isGoodJetLuka(chain, index, cleaned = cleaned)
    else:
        return True


#
# B tagging
#
from HNL.ObjectSelection.bTagWP import getBTagWP, readBTagValue
def isLooseBJetHNL(chain, index):
    if not isGoodJet(chain, index, cleaned='FO', selection='HNL'): return False
    if readBTagValue(chain, index, 'Deep') < getBTagWP(chain.year, 'loose', 'Deep'): return False
    return True

def isTightBJetHNL(chain, index):
    if not isGoodJet(chain, index, cleaned='FO', selection='HNL'): return False
    if readBTagValue(chain, index, 'Deep') < getBTagWP(chain.year, 'tight', 'Deep'): return False
    return True

def isLooseBJetHNLLowPt(chain, index):
    if not isGoodJet(chain, index, cleaned='FO', selection='HNLLowPt'): return False
    if readBTagValue(chain, index, 'Deep') < getBTagWP(chain.year, 'loose', 'Deep'): return False
    return True

def isTightBJetHNLLowPt(chain, index):
    if not isGoodJet(chain, index, cleaned='FO', selection='HNLowPt'): return False
    if readBTagValue(chain, index, 'Deep') < getBTagWP(chain.year, 'tight', 'Deep'): return False
    return True

def isLooseBJetAN2017014(chain, index):
    if not isGoodJet(chain, index, cleaned=None, selection='AN2017014'): return False
    if readBTagValue(chain, index, 'AN2017014') < getBTagWP(chain.year, 'loose', 'AN2017014'): return False
    return True

def isTightBJetAN2017014(chain, index):
    if not isGoodJet(chain, index, cleaned=None, selection='AN2017014'): return False
    if readBTagValue(chain, index, 'AN2017014') < getBTagWP(chain.year, 'tight', 'AN2017014'): return False
    return True

def isLooseBJetTTT(chain, index):
    if not isGoodJet(chain, index, cleaned='loose', selection='TTT'): return False
    if readBTagValue(chain, index, 'Deep') < getBTagWP(chain.year, 'loose', 'Deep'): return False
    return True

def isTightBJetTTT(chain, index):
    if not isGoodJet(chain, index, cleaned='loose', selection='TTT'): return False
    if readBTagValue(chain, index, 'Deep') < getBTagWP(chain.year, 'tight', 'Deep'): return False
    return True

def isLooseBJetLuka(chain, index):
    if not isGoodJet(chain, index, cleaned='loose', selection='Luka'): return False
    if readBTagValue(chain, index, 'Deep') < getBTagWP(chain.year, 'loose', 'Deep'): return False
    return True

def isTightBJetLuka(chain, index):
    if not isGoodJet(chain, index, cleaned='loose', selection='Luka'): return False
    if readBTagValue(chain, index, 'Deep') < getBTagWP(chain.year, 'tight', 'Deep'): return False
    return True

def isLooseBJet(chain, index, selection):
    if selection == 'HNL':
        return isLooseBJetHNL(chain, index)
    elif selection == 'HNLLowPt':
        return isLooseBJetHNLLowPt(chain, index)
    elif selection == 'AN2017014':
        return isLooseBJetAN2017014(chain, index)
    elif selection == 'TTT':
        return isLooseBJetTTT(chain, index)
    elif selection == 'Luka':
        return isLooseBJetLuka(chain, index)
    else:
        raise RuntimeError("Unknown selection for jets")

def isTightBJet(chain, index, selection):
    if selection == 'HNL':
        return isTightBJetHNL(chain, index)
    elif selection == 'HNLLowPt':
        return isTightBJetHNLLowPt(chain, index)
    elif selection == 'AN2017014':
        return isTightBJetAN2017014(chain, index)
    elif selection == 'TTT':
        return isTightBJetTTT(chain, index)
    elif selection == 'Luka':
        return isTightBJetLuka(chain, index)
    else:
        raise RuntimeError("Unknown selection for jets")

def isGoodBJet(chain, index, wp, selection = None):
    selection = checkJetAlgorithm(chain, selection)
    if wp == 'loose':
        return isLooseBJet(chain, index, selection)
    elif wp == 'tight':
        return isTightBJet(chain, index, selection)
    else:
        raise RuntimeError("Unknown working point for jets")