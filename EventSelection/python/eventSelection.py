
#
# list of functions to select events
#
import numpy as np

from HNL.ObjectSelection.leptonSelector import isTightLightLepton

def getSortKey(item): 
    return item[0]

def getSortKeyHNLtruth(item): 
    return item[2]

def select3LightLeptons(chain, new_chain):

    chain.leptons = [(chain._lPt[l], l) for l in xrange(chain._nLight) if isTightLightLepton(chain, l)]
    if len(chain.leptons) != 3:  return False

    ptAndIndex = sorted(chain.leptons, reverse=True, key = getSortKey) 
    new_chain.l1 = ptAndIndex[0][1]
    new_chain.l2 = ptAndIndex[1][1]
    new_chain.l3 = ptAndIndex[2][1]
    new_chain.l1_pt = ptAndIndex[0][0]
    new_chain.l2_pt = ptAndIndex[1][0]
    new_chain.l3_pt = ptAndIndex[2][0]

    new_chain.isEEE = (chain._lFlavor[chain.l1] == 0 and chain._lFlavor[chain.l2] == 0 and chain._lFlavor[chain.l3] == 0)
    new_chain.isEEMu = ((chain._lFlavor[chain.l1] == 0 and chain._lFlavor[chain.l2] == 0 and chain._lFlavor[chain.l3] == 1)
                    or (chain._lFlavor[chain.l1] == 0 and chain._lFlavor[chain.l2] == 1 and chain._lFlavor[chain.l3] == 0)
                    or (chain._lFlavor[chain.l1] == 1 and chain._lFlavor[chain.l2] == 0 and chain._lFlavor[chain.l3] == 0))
    new_chain.isEMuMu = ((chain._lFlavor[chain.l1] == 0 and chain._lFlavor[chain.l2] == 1 and chain._lFlavor[chain.l3] == 1)
                    or (chain._lFlavor[chain.l1] == 1 and chain._lFlavor[chain.l2] == 1 and chain._lFlavor[chain.l3] == 0)
                    or (chain._lFlavor[chain.l1] == 1 and chain._lFlavor[chain.l2] == 0 and chain._lFlavor[chain.l3] == 1))
    new_chain.isMuMuMu = (chain._lFlavor[chain.l1] == 1 and chain._lFlavor[chain.l2] == 1 and chain._lFlavor[chain.l3] == 1)
    
    if bVeto(chain, 'AN2017-014'):      return False

    #if not passesPtCuts(chain):         return False
    return True   

from HNL.ObjectSelection.leptonSelector import isTightLepton
from HNL.ObjectSelection.leptonSelector import whichHNLlepton

def select3Leptons(chain, new_chain, no_tau=False):

    collection = chain._nL if not no_tau else chain._nLight
    chain.leptons = [(chain._lPt[l], l) for l in xrange(chain._nL) if isTightLepton(chain, l)]
    if len(chain.leptons) != 3:  return False

    ptAndIndex = sorted(chain.leptons, reverse=True, key = getSortKey)
    
    new_chain.l1 = ptAndIndex[0][1]
    new_chain.l2 = ptAndIndex[1][1]
    new_chain.l3 = ptAndIndex[2][1]
    new_chain.l1_pt = ptAndIndex[0][0]
    new_chain.l2_pt = ptAndIndex[1][0]
    new_chain.l3_pt = ptAndIndex[2][0]
    new_chain.l1_eta = chain._lEta[new_chain.l1]
    new_chain.l2_eta = chain._lEta[new_chain.l2]
    new_chain.l3_eta = chain._lEta[new_chain.l3]
    new_chain.l1_phi = chain._lPhi[new_chain.l1]
    new_chain.l2_phi = chain._lPhi[new_chain.l2]
    new_chain.l3_phi = chain._lPhi[new_chain.l3]
    new_chain.l1_e = chain._lE[new_chain.l1]
    new_chain.l2_e = chain._lE[new_chain.l2]
    new_chain.l3_e = chain._lE[new_chain.l3]
    new_chain.l1_charge = chain._lCharge[new_chain.l1]
    new_chain.l2_charge = chain._lCharge[new_chain.l2]
    new_chain.l3_charge = chain._lCharge[new_chain.l3]

#    if not passesPtCuts(chain):         return False
    
    if bVeto(chain, 'Deep'):      return False

    return True  

def select3GenLeptons(chain, new_chain):
   
    chain.leptons = []
    for l in xrange(chain._gen_nL):
        if chain._gen_lFlavor[l] == 2 and not chain._gen_lDecayedHadr[l]:       continue
        if chain._gen_lIsPrompt[l]: chain.leptons.append((chain._gen_lPt[l], l))  

    if len(chain.leptons) != 3:  return False

    ptAndIndex = sorted(chain.leptons, reverse=True, key = getSortKey)

    new_chain.l1 = ptAndIndex[0][1]
    new_chain.l2 = ptAndIndex[1][1]
    new_chain.l3 = ptAndIndex[2][1]
    new_chain.l1_pt = ptAndIndex[0][0]
    new_chain.l2_pt = ptAndIndex[1][0]
    new_chain.l3_pt = ptAndIndex[2][0]
    new_chain.l1_eta = chain._gen_lEta[new_chain.l1]
    new_chain.l2_eta = chain._gen_lEta[new_chain.l2]
    new_chain.l3_eta = chain._gen_lEta[new_chain.l3]
    new_chain.l1_phi = chain._gen_lPhi[new_chain.l1]
    new_chain.l2_phi = chain._gen_lPhi[new_chain.l2]
    new_chain.l3_phi = chain._gen_lPhi[new_chain.l3]
    new_chain.l1_e = chain._gen_lE[new_chain.l1]
    new_chain.l2_e = chain._gen_lE[new_chain.l2]
    new_chain.l3_e = chain._gen_lE[new_chain.l3]
    new_chain.l1_charge = chain._gen_lCharge[new_chain.l1]
    new_chain.l2_charge = chain._gen_lCharge[new_chain.l2]
    new_chain.l3_charge = chain._gen_lCharge[new_chain.l3]
    
    return True
 

from HNL.ObjectSelection.jetSelector import isGoodJet, isBJet
def bVeto(chain, algo):
    for jet in xrange(chain._nJets):
        if not isGoodJet(chain, jet): continue
        if isBJet(chain, jet, algo, 'loose'): return True    
    return False


def passesPtCuts(chain):
    
    if chain.l1_pt < 15: return False
    if chain.l2_pt < 10: return False
    if chain._lFlavor[chain.l3] == 1 and chain.l3_pt < 5:      return False    
    if chain._lFlavor[chain.l3] == 0 and chain.l3_pt < 10:      return False    


    #TODO: Update 
    if chain.isEEE:
        if (chain.l1_pt > 19 and chain.l2_pt > 15) or chain.l1_pt > 30:  return True

    if chain.isEEMu:
        if chain._lFlavor[chain.l3] == 0 and chain.l3_pt < 15:  return (chain.l1_pt > 23)
        if chain._lFlavor[chain.l3] == 1 and chain.l3_pt < 8:   return (chain.l1_pt > 25 and chain.l2_pt > 15)
        if chain._lFlavor[chain.l3] == 1 and chain.l3_pt > 8:   return (chain.l1_pt > 23 or chain.l2_pt > 15)

    if chain.isEMuMu:
        if chain._lFlavor[chain.l3] == 1 and chain.l3_pt < 9:  return (chain.l1_pt > 23)

    return True
    
def passedCategory(chain, cat_name):
    
    if cat_name == 'eee' and not chain.isEEE: return False
    if cat_name == 'eemu' and not chain.isEEMu: return False
    if cat_name == 'emumu' and not chain.isEMuMu: return False
    if cat_name == 'mumumu' and not chain.isMuMuMu: return False
    return True

from HNL.Tools.helpers import getFourVec, deltaPhi
def calculateKinematicVariables(chain, new_chain, is_reco_level = True):
    l1Vec = getFourVec(new_chain.l1_pt, new_chain.l1_eta, new_chain.l1_phi, new_chain.l1_e)
    l2Vec = getFourVec(new_chain.l2_pt, new_chain.l2_eta, new_chain.l2_phi, new_chain.l2_e)
    l3Vec = getFourVec(new_chain.l3_pt, new_chain.l3_eta, new_chain.l3_phi, new_chain.l3_e)
    lVec = [l1Vec, l2Vec, l3Vec]

    #M3l
    new_chain.M3l = (l1Vec + l2Vec + l3Vec).M()
    
    #min(M_OS)
    min_mos = 9999999.
    os = [10, 10]
    charge = [new_chain.l1_charge, new_chain.l2_charge, new_chain.l3_charge]
    for i1, l in enumerate([new_chain.l1, new_chain.l2, new_chain.l3]):
        for i2, sl in enumerate([new_chain.l1, new_chain.l2, new_chain.l3]):
            if i2 <= i1:        continue
            if charge[i1] == charge[i2]: continue
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
        for l in xrange(chain._nLight):
            new_chain.pt_cone[l] = chain._lPt[l]*(1+max(0., chain._miniIso[l]-0.4)) #TODO: is this the correct definition?

    else:
        new_chain.mtOther = np.sqrt(2*chain._gen_met*chain._gen_lPt[new_chain.index_other]*(1-np.cos(deltaPhi(chain._gen_lPhi[new_chain.index_other], chain._gen_metPhi))))
        #ptCone
        for l in xrange(chain._nLight):
            new_chain.pt_cone[l] = chain._lPt[l] #TODO: is this the correct definition?
    
    return


def lowMassCuts(chain, new_chain):
    calculateKinematicVariables(chain, new_chain)
    if new_chain._met > 75:         return False
    if new_chain.m3l > 80:          return False
    if new_chain.l1_pt > 55:        return False
    return True 
     
def highMassCuts(chain, new_chain):
    calculateKinematicVariables(chain, new_chain)
    if new_chain._met > 75:         return False
    if new_chain.m3l > 80:          return False
    if new_chain.l1_pt < 55:        return False
    return True 
