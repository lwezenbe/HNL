from HNL.Tools.helpers import deltaR
from HNL.ObjectSelection.leptonSelector import isGoodLepton

default_jet_selection = 'MVA'

#
#       Defines jet WP and b-tagging
#
def isCleanFromLeptons(chain, index):
    for l in xrange(chain._nL):
        if not isGoodLepton(chain, l, chain.obj_sel['light_algo'], chain.obj_sel['tau_algo'], 'loose', analysis = chain.obj_sel['analysis']): continue
        if deltaR(chain._lEta[l], chain._jetEta[index], chain._lPhi[l], chain._jetPhi[index]) < 0.4: return False
    return True

def isGoodJetAN2017014(chain, index, cleaned = True):
    if chain._jetPt[index] < 25:        return False
    if abs(chain._jetEta[index]) > 2.4: return False
    if chain.year != 2018:
        if not chain._jetIsLoose[index]:    return False
    else:
        if not chain._jetIsTight[index]:    return False
    if cleaned and not isCleanFromLeptons(chain, index):       return False
    return True

def isGoodJetCutBased(chain, index, cleaned = True):
    # print "new jet"
    if chain._jetPt[index] < 25:        return False
    # print 'jet pt'
    if abs(chain._jetEta[index]) > 2.4: return False
    # print 'jet eta'
    if not chain._jetIsTight[index]:    return False
    # print 'istight'
    if cleaned and not isCleanFromLeptons(chain, index):       return False
    # print 'cleaned'
    return True

from HNL.ObjectSelection.bTagWP import getBTagWP, readBTagValue
def isBJet(chain, index, algo, wp, cleaned = True, selection = None):

    # print index, isGoodJet(chain, index, cleaned = cleaned, selection = selection)
    # print 'jetindex', index
    if selection is None:
        if not isGoodJet(chain, index, cleaned = cleaned, selection = default_jet_selection): return False
    else:
        if not isGoodJet(chain, index, cleaned = cleaned, selection = selection): return False
        
    # print readBTagValue(chain, index, algo), getBTagWP(chain.year, wp, algo)
    if readBTagValue(chain, index, algo) < getBTagWP(chain.year, wp, algo): return False
    return True
    
def isGoodJet(chain, index, cleaned = True, selection = None):
    if selection is None: selection = default_jet_selection

    if selection == 'cut-based' or selection == 'MVA':
        return isGoodJetCutBased(chain, index, cleaned = cleaned)
    elif selection == 'AN2017014':
        return isGoodJetAN2017014(chain, index, cleaned = cleaned)
    else:
        return True