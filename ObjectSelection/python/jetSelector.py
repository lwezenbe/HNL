from HNL.Tools.helpers import deltaR
from HNL.ObjectSelection.leptonSelector import isGoodLepton

#
#       Defines jet WP and b-tagging
#
def getJetPt(chain, index):
    syst = chain.obj_sel['systematic']
    if chain.era != 'prelegacy':
        if syst == 'JECUp':
            return chain._jetSmearedPt_JECUp[index]
        elif syst == 'JECDown':
            return chain._jetSmearedPt_JECDown[index]
        elif syst == 'JERUp':
            return chain._jetSmearedPt_JERUp[index]
        elif syst == 'JERDown':
            return chain._jetSmearedPt_JERDown[index]
        else:
            return chain._jetSmearedPt[index]
    else:
        return chain._jetPt[index]  #smearedpt temporarily not available in prelegacy skims

def isCleanFromLeptons(chain, index, wp):
    if wp is None: return True
    for l in xrange(chain._nL):
    # for l in xrange(chain._nLight):
        if not isGoodLepton(chain, l, wp): continue
        if deltaR(chain._lEta[l], chain._jetEta[index], chain._lPhi[l], chain._jetPhi[index]) < 0.4: return False
        if chain._lFlavor[l] == 2:
            if not isGoodLepton(chain, l, 'tight'): continue
            if deltaR(chain._lEta[l], chain._jetEta[index], chain._lPhi[l], chain._jetPhi[index]) < 0.5: return False
            
    return True

def isGoodJetAN2017014(chain, index, cleaned = 'loose'):
    if getJetPt(chain, index) < 25:        return False
    if abs(chain._jetEta[index]) > 2.4: return False
    if chain.year != '2018':
        if not chain._jetIsLoose[index]:    return False
    else:
        if not chain._jetIsTight[index]:    return False
    if cleaned is not None and not isCleanFromLeptons(chain, index, cleaned):       return False
    return True

def isGoodJetHNL(chain, index, cleaned = 'loose'):
    if getJetPt(chain, index) < 25:        return False
    if abs(chain._jetEta[index]) > 2.4: return False
    if not chain._jetIsTight[index]:    return False
    if cleaned is not None and not isCleanFromLeptons(chain, index, cleaned):       return False
    return True

def isGoodJetHNLLowPt(chain, index, cleaned = 'loose'):
    if getJetPt(chain, index) < 25:        return False
    if abs(chain._jetEta[index]) > 2.4: return False
    if not chain._jetIsTight[index]:    return False
    if cleaned is not None and not isCleanFromLeptons(chain, index, cleaned):       return False
    return True

def isGoodJetTTT(chain, index, cleaned = 'loose'):
    if getJetPt(chain, index) < 30:        return False
    if abs(chain._jetEta[index]) > 2.4: return False
    if not chain._jetIsTight[index]:    return False
    if cleaned is not None and not isCleanFromLeptons(chain, index, cleaned):       return False
    return True

def isGoodJetLuka(chain, index, cleaned = 'loose'):
    if getJetPt(chain, index) < 25:                                                    return False
    if abs(chain._jetEta[index]) > 5.:                                              return False
    if not chain._jetIsTight[index]:                                                return False
    if 2.7 < abs(chain._jetEta[index]) < 3 and getJetPt(chain, index) < 60:            return False
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

def isGoodJet(chain, index, cleaned = 'loose', selection = None):
    selection = checkJetAlgorithm(chain, selection)

    if selection == 'HNL':
        return isGoodJetHNL(chain, index, cleaned = cleaned)
    elif selection == 'HNLLowPt':
        return isGoodJetHNLLowPt(chain, index, cleaned = cleaned)
    elif selection == 'AN2017014':
        return isGoodJetAN2017014(chain, index, cleaned = cleaned)
    elif selection == 'TTT':
        return isGoodJetTTT(chain, index, cleaned = cleaned)
    elif selection == 'tZq':
        return isGoodJetLuka(chain, index, cleaned = cleaned)
    else:
        return True


#
# B tagging
#
from HNL.ObjectSelection.bTagWP import getBTagWP, readBTagValue

def isBaseBJetHNL(chain, index):
    if not isGoodJet(chain, index, cleaned='FO', selection='HNL'): return False
    return True

def isLooseBJetHNL(chain, index):
    if not isBaseBJetHNL(chain, index): return False
    if readBTagValue(chain, index, 'Deep') < getBTagWP(chain.era, chain.year, 'loose', 'Deep'): return False
    return True

def isTightBJetHNL(chain, index):
    if not isBaseBJetHNL(chain, index): return False
    if readBTagValue(chain, index, 'Deep') < getBTagWP(chain.era, chain.year, 'tight', 'Deep'): return False
    return True

def isBaseBJetHNLLowPt(chain, index):
    if not isGoodJet(chain, index, cleaned='FO', selection='HNLLowPt'): return False
    return True

def isLooseBJetHNLLowPt(chain, index):
    if not isBaseBJetHNLLowPt(chain, index): return False
    if readBTagValue(chain, index, 'Deep') < getBTagWP(chain.era, chain.year, 'loose', 'Deep'): return False
    return True

def isTightBJetHNLLowPt(chain, index):
    if not isBaseBJetHNLLowPt(chain, index): return False
    if readBTagValue(chain, index, 'Deep') < getBTagWP(chain.era, chain.year, 'tight', 'Deep'): return False
    return True

def isBaseBJetAN2017014(chain, index):
    if not isGoodJet(chain, index, cleaned=None, selection='AN2017014'): return False
    return True

def isLooseBJetAN2017014(chain, index):
    if not isBaseBJetAN2017014(chain, index): return False
    if readBTagValue(chain, index, 'AN2017014') < getBTagWP(chain.era, chain.year, 'loose', 'AN2017014'): return False
    return True

def isTightBJetAN2017014(chain, index):
    if not isBaseBJetAN2017014(chain, index): return False
    if readBTagValue(chain, index, 'AN2017014') < getBTagWP(chain.era, chain.year, 'tight', 'AN2017014'): return False
    return True

def isBaseBJetTTT(chain, index):
    if not isGoodJet(chain, index, cleaned='loose', selection='TTT'): return False
    return True

def isLooseBJetTTT(chain, index):
    if not isBaseBJetTTT(chain, index): return False
    if readBTagValue(chain, index, 'Deep') < getBTagWP(chain.era, chain.year, 'loose', 'Deep'): return False
    return True

def isMediumBJetTTT(chain, index):
    if not isBaseBJetTTT(chain, index): return False
    if readBTagValue(chain, index, 'Deep') < getBTagWP(chain.era, chain.year, 'medium', 'Deep'): return False
    return True

def isTightBJetTTT(chain, index):
    if not isBaseBJetTTT(chain, index): return False
    if readBTagValue(chain, index, 'Deep') < getBTagWP(chain.era, chain.year, 'tight', 'Deep'): return False
    return True

def isBaseBJetLuka(chain, index):
    if not isGoodJet(chain, index, cleaned='loose', selection='tZq'): return False
    if abs(chain._jetEta[index]) > 2.5: return False
    return True

def isLooseBJetLuka(chain, index):
    if not isBaseBJetLuka(chain, index): return False
    if readBTagValue(chain, index, 'Deep') < getBTagWP(chain.era, chain.year, 'loose', 'Deep'): return False
    return True

def isMediumBJetLuka(chain, index):
    if not isBaseBJetLuka(chain, index): return False
    if readBTagValue(chain, index, 'Deep') < getBTagWP(chain.era, chain.year, 'medium', 'Deep'): return False
    return True

def isTightBJetLuka(chain, index):
    if not isBaseBJetLuka(chain, index): return False
    if readBTagValue(chain, index, 'Deep') < getBTagWP(chain.era, chain.year, 'tight', 'Deep'): return False
    return True

def isBaseBJet(chain, index, selection):
    if selection == 'HNL':
        return isBaseBJetHNL(chain, index)
    elif selection == 'HNLLowPt':
        return isBaseBJetHNLLowPt(chain, index)
    elif selection == 'AN2017014':
        return isBaseBJetAN2017014(chain, index)
    elif selection == 'TTT':
        return isBaseBJetTTT(chain, index)
    elif selection == 'tZq':
        return isBaseBJetLuka(chain, index)
    else:
        raise RuntimeError("Unknown selection for jets")

def isLooseBJet(chain, index, selection):
    if selection == 'HNL':
        return isLooseBJetHNL(chain, index)
    elif selection == 'HNLLowPt':
        return isLooseBJetHNLLowPt(chain, index)
    elif selection == 'AN2017014':
        return isLooseBJetAN2017014(chain, index)
    elif selection == 'TTT':
        return isLooseBJetTTT(chain, index)
    elif selection == 'tZq':
        return isLooseBJetLuka(chain, index)
    else:
        raise RuntimeError("Unknown selection for jets")

def isMediumBJet(chain, index, selection):
    if selection == 'tZq':
        return isMediumBJetLuka(chain, index)
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
    elif selection == 'tZq':
        return isTightBJetLuka(chain, index)
    else:
        raise RuntimeError("Unknown selection for jets")

def isGoodBJet(chain, index, wp, selection = None):
    selection = checkJetAlgorithm(chain, selection)

    if wp == 'base':
        return isBaseBJet(chain, index, selection)
    elif wp == 'loose':
        return isLooseBJet(chain, index, selection)
    elif wp == 'medium':
        return isMediumBJet(chain, index, selection)
    elif wp == 'tight':
        return isTightBJet(chain, index, selection)
    else:
        raise RuntimeError("Unknown working point for jets")

def checkMetAlgo(chain, algo):
    if algo is None:
        try:
            chain.obj_sel
        except:
            #Initiate default object selection
            chain.obj_sel = objectSelectionCollection()
        return chain.obj_sel['met']
    else:
        return algo


def getMET(chain, apply_corrections = False):
    syst = chain.obj_sel['systematic']
#    algo = checkMetAlgo(chain, None)
#    apply_corrections = algo == 'corrected'

    if chain.is_reco_level:
        if syst == 'JECUp':
            out_met = chain._met_JECUp
            out_metphi = chain._metPhi_JECUp
        elif syst == 'JECDown':
            out_met = chain._met_JECDown 
            out_metphi = chain._metPhi_JECDown
        elif syst == 'UnclMETUp':
            out_met = chain._met_UnclUp
            out_metphi = chain._metPhi_UnclUp
        elif syst == 'UnclMETDown':
            out_met = chain._met_UnclDown
            out_metphi = chain._metPhi_UnclDown
        else:
            out_met = chain._met
            out_metphi = chain._metPhi
        if apply_corrections:
            from HNL.Weights.metCorrection import ULMETXYCorrection
            out_met, out_metphi = ULMETXYCorrection(out_met, out_metphi, chain._nVertex, chain._runNb, chain.year, chain.era, not chain.is_data)
        return out_met, out_metphi
    
    else:
        return chain._gen_met, chain._gen_metPhi
    
