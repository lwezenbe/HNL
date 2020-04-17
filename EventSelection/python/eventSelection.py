
#
# list of functions to select events
#
import numpy as np

from HNL.ObjectSelection.leptonSelector import isTightLightLepton
from HNL.ObjectSelection.jetSelector import isGoodJet, isBJet

#
# Define a few constants
#

l1 = 0
l2 = 1
l3 = 2

def getSortKey(item): 
    return item[0]

def getSortKeyHNLtruth(item): 
    return item[2]


from HNL.ObjectSelection.leptonSelector import isTightLepton
#
# Function to select 3 good leptons and save their variables in the chain
# no_tau: turn on to only accept 3 light leptons
# tau_algo: if set to 'gen_truth', it will still run over all reco taus but instead of using tight taus it will only look if they were matched to a hadronically decayed gen tau
#
def select3Leptons(chain, new_chain, no_tau=False, light_algo = 'leptonMVAtZq', tau_algo = None, cutter = None):

    if chain is new_chain:
        new_chain.l_pt = [0.0]*3
        new_chain.l_eta = [0.0]*3
        new_chain.l_phi = [0.0]*3
        new_chain.l_charge = [0.0]*3
        new_chain.l_flavor = [0.0]*3
        new_chain.l_e = [0.0]*3

    collection = chain._nL if not no_tau else chain._nLight
    chain.leptons = [(chain._lPt[l], l) for l in xrange(collection) if isTightLepton(chain, l, algo = light_algo, tau_algo=tau_algo)]
    if cutter is not None:
        cutter.cut(len(chain.leptons) > 0, 'at_least_1_lep')
        cutter.cut(len(chain.leptons) > 1, 'at_least_2_lep')
        cutter.cut(len(chain.leptons) > 2, 'at_least_3_lep')
    if len(chain.leptons) != 3:  return False

    ptAndIndex = sorted(chain.leptons, reverse=True, key = getSortKey)
 
    new_chain.l1 = ptAndIndex[0][1]
    new_chain.l2 = ptAndIndex[1][1]
    new_chain.l3 = ptAndIndex[2][1]
    for i in xrange(3):
        new_chain.l_pt[i] = ptAndIndex[i][0] 
        new_chain.l_eta[i] = chain._lEta[ptAndIndex[i][1]]
        new_chain.l_phi[i] = chain._lPhi[ptAndIndex[i][1]]
        new_chain.l_e[i] = chain._lE[ptAndIndex[i][1]]
        new_chain.l_charge[i] = chain._lCharge[ptAndIndex[i][1]]
        new_chain.l_flavor[i] = chain._lFlavor[ptAndIndex[i][1]]
    return True  

def passBaseCuts(chain, new_chain, cutter):
    calculateKinematicVariables(chain, new_chain, is_reco_level = True)
    if not cutter.cut(not bVeto(chain, 'Deep'), 'b-veto'):              return False
    if not cutter.cut(abs(new_chain.M3l-91) > 15, 'M3l_Z_veto'):        return False 
    if not cutter.cut(passesZcuts(chain, new_chain, True), 'M2l_OS_Z_veto'):        return False
    return True

from HNL.ObjectSelection.leptonSelector import isGoodGenLepton

def select3GenLeptons(chain, new_chain):
  
    if chain is new_chain:
        new_chain.l_pt = [0.0]*3
        new_chain.l_eta = [0.0]*3
        new_chain.l_phi = [0.0]*3
        new_chain.l_charge = [0.0]*3
        new_chain.l_flavor = [0.0]*3
        new_chain.l_e = [0.0]*3
 
    chain.leptons = []
    for l in xrange(chain._gen_nL):
        if isGoodGenLepton(chain, l): 
            chain.leptons.append((chain._gen_lPt[l], l))  

    if len(chain.leptons) != 3:  return False

    ptAndIndex = sorted(chain.leptons, reverse=True, key = getSortKey)

    new_chain.l1 = ptAndIndex[0][1]
    new_chain.l2 = ptAndIndex[1][1]
    new_chain.l3 = ptAndIndex[2][1]
    for i in xrange(3):
        new_chain.l_pt[i] = ptAndIndex[i][0] 
        new_chain.l_eta[i] = chain._gen_lEta[ptAndIndex[i][1]]
        new_chain.l_phi[i] = chain._gen_lPhi[ptAndIndex[i][1]]
        new_chain.l_e[i] = chain._gen_lE[ptAndIndex[i][1]]
        new_chain.l_charge[i] = chain._gen_lCharge[ptAndIndex[i][1]]
        new_chain.l_flavor[i] = chain._gen_lFlavor[ptAndIndex[i][1]]
    
    return True
 

from HNL.ObjectSelection.jetSelector import isGoodJet, isBJet
def bVeto(chain, algo, cleaned = True):
    for jet in xrange(chain._nJets):
        if not isGoodJet(chain, jet, cleaned): continue
        if isBJet(chain, jet, algo, 'loose'): return True    
    return False

def passesZcuts(chain, new_chain, same_flavor=False):
    for fl in [0, 1]:
        l1Vec = getFourVec(new_chain.l_pt[fl], new_chain.l_eta[fl], new_chain.l_phi[fl], new_chain.l_e[fl])
        for sl in [1, 2]:
            if fl == sl: continue
            if new_chain.l_charge[fl] == new_chain.l_charge[sl]: continue
            if same_flavor and new_chain.l_flavor[fl] != new_chain.l_flavor[sl]: continue 
            l2Vec = getFourVec(new_chain.l_pt[sl], new_chain.l_eta[sl], new_chain.l_phi[sl], new_chain.l_e[sl])
            if abs((l1Vec + l2Vec).M() - 90) < 15: return False
    return True

#TODO: include taus?
from HNL.ObjectSelection.leptonSelector import isFOLightLepton
def fourthFOVeto(chain, selection='cutbased'):
    for lepton in xrange(chain._nLight):
        if lepton in [chain.l1, chain.l2, chain.l3]: continue
        if isFOLightLepton(chain, lepton, selection): return True
    return False

from HNL.EventSelection.eventCategorization import CATEGORY_FROM_NAME
def passesPtCutsAN2017014(chain):
    if chain.l_pt[l1] < 15: return False
    if chain.l_pt[l2] < 10: return False
    if chain._lFlavor[chain.l3] == 1 and chain.l_pt[l3] < 5:      return False    
    if chain._lFlavor[chain.l3] == 0 and chain.l_pt[l3] < 10:      return False    

    if chain.category == CATEGORY_FROM_NAME['EEE']:
        return (chain.l_pt[l1] > 19 and chain.l_pt[l2] > 15) or chain.l_pt[l1] > 30
    elif chain.category == CATEGORY_FROM_NAME['SS-EEMu'] or chain.category == CATEGORY_FROM_NAME['SS-EEMu']:
        if chain.l_flavor[l3] == 0 and chain.l_pt[l3] < 15:
            return chain.l_pt[l1] > 23
        elif chain.l_flavor[l3] == 1:
            if chain.l_pt[l3] < 8:
                return chain.l_pt[l1] > 25 and chain.l_pt[l2] > 15
            else:
                return chain.l_pt[l1] > 23 or chain.l_pt[l2] > 15
    elif chain.category == CATEGORY_FROM_NAME['SS-EMuMu'] or chain.category == CATEGORY_FROM_NAME['OS-EMuMu']:
        if chain.l_flavor[l3] == 1 and chain.l_pt[l3] < 9:
            return chain.l_pt[l1] > 23

    return True

def threeSameSignVeto(chain):
    return chain.l_charge[l1] == chain.l_charge[l2] and chain.l_charge[l2] == chain.l_charge[l3]

def passBaseCutsAN2017014(chain, new_chain, cutter):
   
    if not cutter.cut(passesPtCutsAN2017014(chain), 'pt_cuts'):         return False 
    if not cutter.cut(not bVeto(chain, 'AN2017-014', uncleaned=True), 'b-veto'):              return False
    if not cutter.cut(not threeSameSignVeto(chain), 'three_same_sign_veto'):                    return False
    if not cutter.cut(not fourthFOVeto(chain), '4th_l_veto'):   return False
    return True

def passedCustomPtCuts(chain, cuts):
    multiple_cut_collections = isinstance(cuts[0], (tuple,))   #cuts should always be an array of cuts for the three leptons, so no error expected
    if multiple_cut_collections:
        passed = [passedCustomPtCuts(chain, cuts_collection) for cuts_collection in cuts]
        return any(passed)
    else:  
        for i, c in enumerate(cuts):
            if c is None: continue
            if chain.l_pt[i] < c: return False
        return True


from HNL.Tools.helpers import getFourVec, deltaPhi
def calculateKinematicVariables(chain, new_chain, is_reco_level = True):
    l1Vec = getFourVec(new_chain.l_pt[l1], new_chain.l_eta[l1], new_chain.l_phi[l1], new_chain.l_e[l1])
    l2Vec = getFourVec(new_chain.l_pt[l2], new_chain.l_eta[l2], new_chain.l_phi[l2], new_chain.l_e[l2])
    l3Vec = getFourVec(new_chain.l_pt[l3], new_chain.l_eta[l3], new_chain.l_phi[l3], new_chain.l_e[l3])
    lVec = [l1Vec, l2Vec, l3Vec]

    #M3l
    new_chain.M3l = (l1Vec + l2Vec + l3Vec).M()

    #min(M_OS)
    min_mos = 9999999.
    os = [10, 10]
    for i1, l in enumerate([new_chain.l1, new_chain.l2, new_chain.l3]):
        for i2, sl in enumerate([new_chain.l1, new_chain.l2, new_chain.l3]):
            if i2 <= i1:        continue
            if new_chain.l_charge[i1] == new_chain.l_charge[i2]: continue
            tmp_mos = (lVec[i1]+lVec[i2]).M()
            if tmp_mos < min_mos:       
                min_mos = tmp_mos
                os = [l, sl]
    new_chain.minMos = min_mos        

    #MTother
    new_chain.index_other = [item for item in [new_chain.l1, new_chain.l2, new_chain.l3] if item not in os][0]   

    #TODO: Seems like there must be a better way to do this
    if is_reco_level:    
        new_chain.mtOther = np.sqrt(2*chain._met*chain._lPt[new_chain.index_other]*(1-np.cos(deltaPhi(chain._lPhi[new_chain.index_other], chain._metPhi))))
        
        #ptCone
        new_chain.pt_cone = []
        for l in xrange(chain._nLight):
            new_chain.pt_cone.append(chain._lPt[l]*(1+max(0., chain._miniIso[l]-0.4))) #TODO: is this the correct definition?

    else:
        new_chain.mtOther = np.sqrt(2*chain._gen_met*chain._gen_lPt[new_chain.index_other]*(1-np.cos(deltaPhi(chain._gen_lPhi[new_chain.index_other], chain._gen_metPhi))))
        #ptCone
        new_chain.pt_cone = []
        for l in xrange(chain._nLight):
            new_chain.pt_cone.append(chain._lPt[l]) #TODO: is this the correct definition?
   
    #calculate #jets and #bjets
    njets = 0
    nbjets = 0
    for jet in xrange(chain._nJets):
        if isGoodJet(chain, jet):       
            njets += 1        
            if isBJet(chain, jet, 'Deep', 'loose'): nbjets += 1

    new_chain.njets = njets
    new_chain.nbjets = nbjets
        
    return

def containsOSSF(chain):
    for first_lepton in [l1, l2]:
        for second_lepton in [l2, l3]:
            if first_lepton == second_lepton: continue
            if chain.l_flavor[first_lepton] != chain.l_flavor[second_lepton]: continue
            if chain.l_charge[first_lepton] == chain.l_charge[second_lepton]: return True  
    return False

def lowMassCuts(chain, new_chain, cutter):
    calculateKinematicVariables(chain, new_chain)
    if not cutter.cut(new_chain.l_pt[l1] < 55, 'l1pt<55'):      return False
    if not cutter.cut(new_chain.M3l < 80, 'm3l<80'):            return False
    if not cutter.cut(chain._met < 75, 'MET'):                  return False
    return True 
     
def highMassCuts(chain, new_chain, cutter):
    calculateKinematicVariables(chain, new_chain)
    if not cutter.cut(new_chain.l_pt[l1] > 55, 'l1pt>55'):        return False
    if not cutter.cut(new_chain.l_pt[l2] > 15, 'l2pt>15'):        return False
    if not cutter.cut(new_chain.l_pt[l3] > 10, 'l3pt>10'):        return False
    if not cutter.cut(passesZcuts(chain, new_chain, same_flavor=True), 'M2l_OSSF_Z_veto'):        return False
    if not cutter.cut(abs(new_chain.M3l-90) > 15, 'M3l_Z_veto'):        return False 
    return True 
