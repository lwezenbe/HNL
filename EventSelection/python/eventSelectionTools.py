#########################################
#       EVENTSELECTIONTOOLS.PY          #
#                                       #
#   LIST OF FUNCTIONS TO SELECT EVENTS  #
#                                       #
#########################################


#
# Imports
#
import numpy as np
from HNL.ObjectSelection.leptonSelector import isFOLepton
from HNL.ObjectSelection.leptonSelector import isGoodLepton, isGoodLeptonTycho
from HNL.ObjectSelection.leptonSelector import isGoodGenLepton
from HNL.ObjectSelection.jetSelector import isGoodJet, isBJet
from HNL.Tools.helpers import getFourVec, deltaPhi



#
# Define a few constants
#

l1 = 0
l2 = 1
l3 = 2
l4 = 3

MZ = 91.1876

#
# Sort keys for the selectLeptons functions
#
def getSortKey(item): 
    return item[0]

def getSortKeyHNLtruth(item): 
    return item[2]

#####################################################

#               selecting the leptons               #

#####################################################

#
# Function to select nL good leptons and save their variables in the chain
# no_tau: turn on to only accept light leptons
# tau_algo: if set to 'gen_truth', it will still run over all reco taus but instead of using tight taus it will only look if they were matched to a hadronically decayed gen tau
#
def selectLeptonsGeneral(chain, new_chain, nL, object_selection, cutter=None, sort_leptons = True):

    collection = chain._nL if not object_selection['notau'] else chain._nLight
    chain.leptons = []
    for l in xrange(collection):
        if chain._lFlavor[l] == 0: workingpoint = object_selection['ele_wp']
        elif chain._lFlavor[l] == 1: workingpoint = object_selection['mu_wp']
        elif chain._lFlavor[l] == 2: workingpoint = object_selection['tau_wp']
        else: raise RuntimeError('In selectLeptonsGeneral: flavor provided is neither an electron, muon or tau')
    
        if isGoodLepton(chain, l, algo=object_selection['light_algo'], tau_algo=object_selection['tau_algo'], workingpoint=workingpoint):
            chain.leptons.append((chain._lPt[l], l))

    if cutter is not None:
        cutter.cut(len(chain.leptons) > 0, 'at_least_1_lep')
        cutter.cut(len(chain.leptons) > 1, 'at_least_2_lep')
        cutter.cut(len(chain.leptons) > 2, 'at_least_3_lep')
    if len(chain.leptons) != nL:  return False

    if chain is new_chain:
        new_chain.l_pt = [0.0]*nL
        new_chain.l_eta = [0.0]*nL
        new_chain.l_phi = [0.0]*nL
        new_chain.l_charge = [0.0]*nL
        new_chain.l_flavor = [0.0]*nL
        new_chain.l_e = [0.0]*nL
        new_chain.l_indices = [0.0]*nL
        new_chain.l_istight = [0.0]*nL

    if sort_leptons: 
        ptAndIndex = sorted(chain.leptons, reverse=True, key = getSortKey)
    else:
        ptAndIndex = chain.leptons

    for i in xrange(nL):
        new_chain.l_indices[i] = ptAndIndex[i][1]
        new_chain.l_pt[i] = ptAndIndex[i][0] 
        new_chain.l_eta[i] = chain._lEta[ptAndIndex[i][1]]
        new_chain.l_phi[i] = chain._lPhi[ptAndIndex[i][1]]
        new_chain.l_e[i] = chain._lE[ptAndIndex[i][1]]
        new_chain.l_charge[i] = chain._lCharge[ptAndIndex[i][1]]
        new_chain.l_flavor[i] = chain._lFlavor[ptAndIndex[i][1]]
        new_chain.l_istight[i] = isGoodLepton(chain, ptAndIndex[i][1], algo=object_selection['light_algo'], tau_algo=object_selection['tau_algo'], workingpoint='tight')

    return True

from HNL.ObjectSelection.objectSelection import objectSelectionCollection
def select3Leptons(chain, new_chain, object_selection, cutter = None):

    object_selection['tau_wp'] = 'tight'
    object_selection['mu_wp'] = 'tight'
    object_selection['ele_wp'] = 'tight'
    return selectLeptonsGeneral(chain, new_chain, 3, object_selection, cutter=cutter, sort_leptons = True)

def select4Leptons(chain, new_chain, object_selection, cutter = None):

    object_selection['tau_wp'] = 'tight'
    object_selection['mu_wp'] = 'tight'
    object_selection['ele_wp'] = 'tight'
    return selectLeptonsGeneral(chain, new_chain, 4, object_selection_collection, cutter=cutter, sort_leptons = True)

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

# def selectLeptonsGeneral(chain, new_chain, nL, no_tau=False, light_algo = None, tau_algo = None, cutter = None, workingpoint = 'tight'):

#     collection = chain._nL if not no_tau else chain._nLight
#     chain.leptons = [(chain._lPt[l], l) for l in xrange(collection) if isGoodLepton(chain, l, algo = light_algo, tau_algo=tau_algo, workingpoint=workingpoint)]
#     if cutter is not None:
#         cutter.cut(len(chain.leptons) > 0, 'at_least_1_lep')
#         cutter.cut(len(chain.leptons) > 1, 'at_least_2_lep')
#         cutter.cut(len(chain.leptons) > 2, 'at_least_3_lep')
#     if len(chain.leptons) != nL:  return False

#     if chain is new_chain:
#         new_chain.l_pt = [0.0]*nL
#         new_chain.l_eta = [0.0]*nL
#         new_chain.l_phi = [0.0]*nL
#         new_chain.l_charge = [0.0]*nL
#         new_chain.l_flavor = [0.0]*nL
#         new_chain.l_e = [0.0]*nL
#         new_chain.l_indices = [0.0]*nL


#     ptAndIndex = sorted(chain.leptons, reverse=True, key = getSortKey)

#     for i in xrange(nL):
#         chain.l_indices[i] = ptAndIndex[i][1]
#         new_chain.l_pt[i] = ptAndIndex[i][0] 
#         new_chain.l_eta[i] = chain._lEta[ptAndIndex[i][1]]
#         new_chain.l_phi[i] = chain._lPhi[ptAndIndex[i][1]]
#         new_chain.l_e[i] = chain._lE[ptAndIndex[i][1]]
#         new_chain.l_charge[i] = chain._lCharge[ptAndIndex[i][1]]
#         new_chain.l_flavor[i] = chain._lFlavor[ptAndIndex[i][1]]

#     return True

#
# Meant for training NN, select up to two jets, if less than two jets, 
#
def selectFirstTwoJets(chain, new_chain, selection = None):
    if chain is new_chain:
        new_chain.j_pt = [0.0]*2
        new_chain.j_eta = [0.0]*2
        new_chain.j_phi = [0.0]*2
        new_chain.j_e = [0.0]*2
        new_chain.j_indices = [0.0]*2

    chain.jets = [(chain._jetPt[j], j) for j in xrange(chain._nJets) if isGoodJet(chain, j, selection = selection)]

    ptAndIndex = sorted(chain.jets, reverse=True, key = getSortKey)
 
    for i in xrange(2):
        if i < len(chain.jets):
            new_chain.j_pt[i] = ptAndIndex[i][0] 
            new_chain.j_eta[i] = chain._jetEta[ptAndIndex[i][1]]
            new_chain.j_phi[i] = chain._jetPhi[ptAndIndex[i][1]]
            new_chain.j_e[i] = chain._jetE[ptAndIndex[i][1]]
            new_chain.j_indices[i] = ptAndIndex[i][0] 
        else:
            new_chain.j_pt[i] = 0. 
            new_chain.j_eta[i] = 0.
            new_chain.j_phi[i] = 0.
            new_chain.j_e[i] = 0.
            new_chain.j_indices[i] = -1

    return True 


#########################################

#   calculating the event variables     #

#########################################

#
# Function to calculate all kinematic variables to be used later on in the selection steps
# All variables are stored in the chain so they can be called anywhere
#
def calculateEventVariables(chain, new_chain, nL = None, is_reco_level = True, selection = None):
    calculateGeneralVariables(chain, new_chain, is_reco_level=is_reco_level, selection=selection)
    if nL == 3:
        calculateThreeLepVariables(chain, new_chain, is_reco_level = is_reco_level)
    if nL == 4:
        calculateFourLepVariables(chain, new_chain)

def calculateGeneralVariables(chain, new_chain, is_reco_level = True, selection = None):
    if is_reco_level:
        #ptCone
        new_chain.pt_cone = []
        for l in xrange(chain._nLight):
            new_chain.pt_cone.append(chain._lPt[l]*(1+max(0., chain._miniIso[l]-0.4))) #TODO: is this the correct definition?

    #calculate #jets and #bjets
    njets = 0
    nbjets = 0
    for jet in xrange(chain._nJets):
        if isGoodJet(chain, jet):     
            njets += 1        
            if isBJet(chain, jet, 'Deep', 'loose'): nbjets += 1

    new_chain.njets = njets
    new_chain.nbjets = nbjets
        
    new_chain.hasOSSF = containsOSSF(new_chain)

    new_chain.HT = calcHT(chain, new_chain, selection)
    new_chain.LT = calcLT(chain, new_chain)

    selectFirstTwoJets(chain, new_chain, selection = selection)

def calculateThreeLepVariables(chain, new_chain, is_reco_level = True):

    l1Vec = getFourVec(new_chain.l_pt[l1], new_chain.l_eta[l1], new_chain.l_phi[l1], new_chain.l_e[l1])
    l2Vec = getFourVec(new_chain.l_pt[l2], new_chain.l_eta[l2], new_chain.l_phi[l2], new_chain.l_e[l2])
    l3Vec = getFourVec(new_chain.l_pt[l3], new_chain.l_eta[l3], new_chain.l_phi[l3], new_chain.l_e[l3])
    metVec = getFourVec(chain._met, 0., chain._metPhi, chain._met)
    lVec = [l1Vec, l2Vec, l3Vec]

    #M3l
    new_chain.M3l = (l1Vec + l2Vec + l3Vec).M()

    #All combinations of dilepton masses
    new_chain.Ml12 = (l1Vec+l2Vec).M()         
    new_chain.Ml23 = (l2Vec+l3Vec).M()         
    new_chain.Ml13 = (l1Vec+l3Vec).M()

    #
    # Get OS, OSSF, SS, SSSF variables
    #
    min_os = None
    max_os = None
    min_ss = None
    max_ss = None
    min_ossf = None
    max_ossf = None
    min_sssf = None
    max_sssf = None
    z_ossf = None

    tmp_minos = 99999999.
    tmp_minss = 99999999.
    tmp_minossf = 99999999.
    tmp_minsssf = 99999999.
    tmp_maxos = 0
    tmp_maxss = 0
    tmp_maxossf = 0
    tmp_maxsssf = 0
    tmp_Zossf = 0


    for i1 in xrange(3):
        for i2 in xrange(3):
            if i2 <= i1:        continue

            tmp_mass = (lVec[i1]+lVec[i2]).M()
            if new_chain.l_charge[i1] == new_chain.l_charge[i2]:
                if tmp_mass < tmp_minss: 
                    min_ss = [i1, i2]
                    tmp_minss = tmp_mass
                if tmp_mass > tmp_maxss: 
                    max_ss = [i1, i2]
                    tmp_maxss = tmp_mass
                if new_chain.l_flavor[i1] == new_chain.l_flavor[i2]:
                    if tmp_mass < tmp_minsssf: 
                        min_sssf = [i1, i2]
                        tmp_minsssf = tmp_mass
                    if tmp_mass > tmp_maxsssf: 
                        max_sssf = [i1, i2]
                        tmp_maxsssf = tmp_mass
            else:
                # print "OS"
                if tmp_mass < tmp_minos: 
                    min_os = [i1, i2]
                    tmp_minos = tmp_mass
                if tmp_mass > tmp_maxos: 
                    max_os = [i1, i2]
                    tmp_maxos = tmp_mass
                if new_chain.l_flavor[i1] == new_chain.l_flavor[i2]:
                    # print "SF"
                    if tmp_mass < tmp_minossf: 
                        min_ossf = [i1, i2]
                        tmp_minossf = tmp_mass
                    if massDiff(tmp_mass, MZ) < massDiff(tmp_Zossf, MZ):
                        z_ossf = [i1, i2]
                        tmp_Zossf = tmp_mass
                    if tmp_mass > tmp_maxossf: 
                        max_ossf = [i1, i2]
                        tmp_maxossf = tmp_mass
            



    #Mass variables
    # print min_os
    new_chain.minMos = (lVec[min_os[0]]+lVec[min_os[1]]).M() if min_os is not None else -1
    new_chain.maxMos = (lVec[max_os[0]]+lVec[max_os[1]]).M() if max_os is not None else -1
    new_chain.minMss = (lVec[min_ss[0]]+lVec[min_ss[1]]).M() if min_ss is not None else -1
    new_chain.maxMss = (lVec[max_ss[0]]+lVec[max_ss[1]]).M() if max_ss is not None else -1
    new_chain.minMossf = (lVec[min_ossf[0]]+lVec[min_ossf[1]]).M() if min_ossf is not None else -1
    new_chain.maxMossf = (lVec[max_ossf[0]]+lVec[max_ossf[1]]).M() if max_ossf is not None else -1
    new_chain.minMsssf = (lVec[min_sssf[0]]+lVec[min_sssf[1]]).M() if min_sssf is not None else -1
    new_chain.maxMsssf = (lVec[max_sssf[0]]+lVec[max_sssf[1]]).M() if max_sssf is not None else -1
    new_chain.MZossf = (lVec[z_ossf[0]]+lVec[z_ossf[1]]).M() if z_ossf is not None else -1

    #MTother
    index_other = [item for item in [0, 1, 2] if item not in min_os][0] if min_os is not None else None
    new_chain.index_other = new_chain.l_indices[index_other] if index_other is not None else -1

    if new_chain.index_other != -1:
        if is_reco_level:    
            new_chain.mtOther = np.sqrt(2*chain._met*chain._lPt[new_chain.index_other]*(1-np.cos(deltaPhi(chain._lPhi[new_chain.index_other], chain._metPhi))))
            leading_os = min_os[0] if chain._lPt[min_os[0]] > chain._lPt[min_os[1]] else min_os[1]
            subleading_os = min_os[0] if chain._lPt[min_os[0]] < chain._lPt[min_os[1]] else min_os[1]
            new_chain.mtl1 = np.sqrt(2*chain._met*chain._lPt[leading_os]*(1-np.cos(deltaPhi(chain._lPhi[leading_os], chain._metPhi))))
            new_chain.mtl2 = np.sqrt(2*chain._met*chain._lPt[subleading_os]*(1-np.cos(deltaPhi(chain._lPhi[subleading_os], chain._metPhi))))
        else:
            new_chain.mtOther = np.sqrt(2*chain._gen_met*chain._gen_lPt[new_chain.index_other]*(1-np.cos(deltaPhi(chain._gen_lPhi[new_chain.index_other], chain._gen_metPhi))))
    else:
        new_chain.mtOther = -1
        new_chain.mtl1 = -1
        new_chain.mtl2 = -1
    #MT3 
    new_chain.mt3 = (l1Vec+l2Vec+l3Vec+metVec).Mt()

    #
    # dR variables
    # 
    new_chain.dr_l1l2 = l1Vec.DeltaR(l2Vec)
    new_chain.dr_l1l3 = l1Vec.DeltaR(l2Vec)
    new_chain.dr_l2l3 = l1Vec.DeltaR(l2Vec)

    new_chain.dr_minOS = lVec[min_os[0]].DeltaR(lVec[min_os[1]]) if min_os is not None else -999.
    new_chain.dr_maxOS = lVec[max_os[0]].DeltaR(lVec[max_os[1]]) if max_os is not None else -999.
    new_chain.dr_minSS = lVec[min_ss[0]].DeltaR(lVec[min_ss[1]]) if min_ss is not None else -999.
    new_chain.dr_maxSS = lVec[max_ss[0]].DeltaR(lVec[max_ss[1]]) if max_ss is not None else -999.
    new_chain.dr_minOSSF = lVec[min_ossf[0]].DeltaR(lVec[min_ossf[1]]) if min_ossf is not None else -999.
    new_chain.dr_maxOSSF = lVec[max_ossf[0]].DeltaR(lVec[max_ossf[1]]) if max_ossf is not None else -999.
    new_chain.dr_minSSSF = lVec[min_sssf[0]].DeltaR(lVec[min_sssf[1]]) if min_sssf is not None else -999.
    new_chain.dr_maxSSSF = lVec[max_sssf[0]].DeltaR(lVec[max_sssf[1]]) if max_sssf is not None else -999.

    new_chain.mindr_l1 = min(new_chain.dr_l1l2, new_chain.dr_l1l3)
    new_chain.maxdr_l1 = max(new_chain.dr_l1l2, new_chain.dr_l1l3)
    new_chain.mindr_l2 = min(new_chain.dr_l1l2, new_chain.dr_l2l3)
    new_chain.maxdr_l2 = max(new_chain.dr_l1l2, new_chain.dr_l2l3)
    new_chain.mindr_l3 = min(new_chain.dr_l1l3, new_chain.dr_l2l3)
    new_chain.maxdr_l3 = max(new_chain.dr_l1l3, new_chain.dr_l2l3)

def calculateFourLepVariables(chain, new_chain):
    l1Vec = getFourVec(new_chain.l_pt[l1], new_chain.l_eta[l1], new_chain.l_phi[l1], new_chain.l_e[l1])
    l2Vec = getFourVec(new_chain.l_pt[l2], new_chain.l_eta[l2], new_chain.l_phi[l2], new_chain.l_e[l2])
    l3Vec = getFourVec(new_chain.l_pt[l3], new_chain.l_eta[l3], new_chain.l_phi[l3], new_chain.l_e[l3])
    l4Vec = getFourVec(new_chain.l_pt[l4], new_chain.l_eta[l4], new_chain.l_phi[l4], new_chain.l_e[l4])
    lVec = [l1Vec, l2Vec, l3Vec, l4Vec]

    if len(chain.l_pt) < 4:
        raise RuntimeError('Inconsistent input: No 4 leptons to use in 4 lepton calculations')

    min_os = None
    tmp_minos = 99999999.
    for i1 in xrange(len(new_chain.l_indices)):
        for i2 in xrange(i1, len(new_chain.l_indices)):
            if i2 <= i1:        continue

            tmp_mass = (lVec[i1]+lVec[i2]).M()
            if new_chain.l_charge[i1] != new_chain.l_charge[i2] and tmp_mass < tmp_minos:
                min_os = [i1, i2]
                tmp_minos = tmp_mass
            
    new_chain.minMos = (lVec[min_os[0]]+lVec[min_os[1]]).M() if min_os is not None else -1

    new_chain.M4l = (l1Vec + l2Vec + l3Vec + l4Vec).M()

    #Mll(Z1) amd Mll(Z2)
    trial_pairs = [[(l1, l2), (l3, l4)], 
                       [(l1, l3), (l2, l4)],
                       [(l1, l4), (l2, l3)]
    ]
    candidate_pairs = []

    for t in trial_pairs:
        if isOSSF(chain, t[0][0], t[0][1]) and isOSSF(chain, t[1][0], t[1][1]): candidate_pairs.append(t)

    if len(candidate_pairs) == 0:
        mass1, mass2 = (-1., -1.)
    elif len(candidate_pairs) == 1:
        mass1 = (lVec[candidate_pairs[0][0][0]]+lVec[candidate_pairs[0][0][1]]).M()
        mass2 = (lVec[candidate_pairs[0][1][0]]+lVec[candidate_pairs[0][1][1]]).M()
    else:
        mass1 = (lVec[candidate_pairs[0][0][0]]+lVec[candidate_pairs[0][0][1]]).M()
        mass2 = (lVec[candidate_pairs[1][0][0]]+lVec[candidate_pairs[1][0][1]]).M()
        for c in candidate_pairs[1:]:
            tmp_mass1 = (lVec[c[0][0]]+lVec[c[0][1]]).M()
            tmp_mass2 = (lVec[c[1][0]]+lVec[c[1][1]]).M()
            if (massDiff(tmp_mass1, MZ) + massDiff(tmp_mass2, MZ)) < (massDiff(mass1, MZ) + massDiff(mass1, MZ)):
                mass1 = tmp_mass1
                mass2 = tmp_mass2
        
    if massDiff(mass1, MZ) < massDiff(mass2, MZ):
        new_chain.Mll_Z1 = mass1
        new_chain.Mll_Z2 = mass2
    else:
        new_chain.Mll_Z1 = mass2
        new_chain.Mll_Z2 = mass1




#################################################

#       all components for event selection      #

#################################################


def bVeto(chain, algo, cleaned = True, selection = None):
    for jet in xrange(chain._nJets):
        if isBJet(chain, jet, algo, 'loose', cleaned=cleaned, selection = selection): return True    
    return False

def fourthFOVeto(chain, light_lep_selection = None, tau_selection = None, no_tau = False):
    if no_tau: collection = chain._nLight 
    else:
        collection = chain._nL

    for lepton in xrange(collection):
        if lepton in chain.l_indices: continue
        if isFOLepton(chain, lepton, light_lep_selection, tau_selection): return True
    return False

from HNL.EventSelection.eventCategorization import CATEGORY_FROM_NAME
def passesPtCutsAN2017014(chain):
    if chain.l_pt[l1] < 15: return False
    if chain.l_pt[l2] < 10: return False
    if chain._lFlavor[chain.l3] == 1 and chain.l_pt[l3] < 5:      return False    
    if chain._lFlavor[chain.l3] == 0 and chain.l_pt[l3] < 10:      return False

    if chain.category == CATEGORY_FROM_NAME['EEE']:
        return (chain.l_pt[l1] > 19 and chain.l_pt[l2] > 15) or chain.l_pt[l1] > 30
    elif chain.category == CATEGORY_FROM_NAME['SS-EEMu'] or chain.category == CATEGORY_FROM_NAME['OS-EEMu']:
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


def threeSameSignVeto(chain):
    return chain.l_charge[l1] == chain.l_charge[l2] and chain.l_charge[l2] == chain.l_charge[l3]

def isOSSF(chain, first_lepton, second_lepton):
    if first_lepton == second_lepton: return False
    if chain.l_flavor[first_lepton] != chain.l_flavor[second_lepton]: return False
    if chain.l_charge[first_lepton] == chain.l_charge[second_lepton]: return False
    return True  

def containsOSSF(chain):
    for first_lepton in [l1, l2]:
        for second_lepton in [l2, l3]:
            if isOSSF(chain, first_lepton, second_lepton): return True
    return False

def passesOSSFforZZ(chain):
    if massDiff(chain.Mll_Z1, MZ) > 15 or massDiff(chain.Mll_Z2, MZ) > 15: return False
    return True

def massDiff(m1, m2):
    return abs(m1-m2)

def calcHT(chain, new_chain, selection = None):
    HT = 0.
    for jet in xrange(chain._nJets):
        if not isGoodJet(chain, jet, selection):    continue 
        HT += chain._jetPt[jet]
    return HT

def calcLT(chain, new_chain):
    LT = 0.
    for lep in new_chain.l_indices:
        LT += chain._lPt[lep]
    LT += chain._met
    return LT


#
# TMP REMOVE AFTER TESTS
#


#
# Basic cuts every event has to pass
#
def passBaseCuts(chain, new_chain, cutter):
    calculateKinematicVariables(chain, new_chain, is_reco_level = True)
    if not cutter.cut(not fourthFOVeto(chain), 'Fourth FO veto'):        return False 
    if not cutter.cut(not threeSameSignVeto(chain), 'No three same sign'):        return False
    if not cutter.cut(not bVeto(chain, 'Deep'), 'b-veto'):              return False
    # if not cutter.cut(abs(new_chain.M3l-91) > 15, 'M3l_Z_veto'):        return False 
    # if not cutter.cut(passesZcuts(chain, new_chain, True), 'M2l_OS_Z_veto'):        return False
    return True
    
#
# Basic cuts every event has to pass
#
def passBaseCutsNoBVeto(chain, new_chain, cutter):
    calculateKinematicVariables(chain, new_chain, is_reco_level = True)
    if not cutter.cut(not fourthFOVeto(chain), 'Fourth FO veto'):        return False 
    if not cutter.cut(not threeSameSignVeto(chain), 'No three same sign'):        return False 
    # if not cutter.cut(abs(new_chain.M3l-91) > 15, 'M3l_Z_veto'):        return False 
    # if not cutter.cut(passesZcuts(chain, new_chain, True), 'M2l_OS_Z_veto'):        return False
    return True

#
# Basic cuts from AN-2017
#
def passBaseCutsAN2017014(chain, new_chain, cutter):
   
    if not cutter.cut(passesPtCutsAN2017014(chain), 'pt_cuts'):         return False 
    if not cutter.cut(not bVeto(chain, 'AN2017014', cleaned=False), 'b-veto'):              return False
    if not cutter.cut(not threeSameSignVeto(chain), 'three_same_sign_veto'):                    return False
    if not cutter.cut(not fourthFOVeto(chain), '4th_l_veto'):   return False
    return True

#
# Low mass region cuts modeled after AN-2017
#
def lowMassCuts(chain, new_chain, cutter):
    calculateKinematicVariables(chain, new_chain)
    if not cutter.cut(new_chain.l_pt[l1] < 55, 'l1pt<55'):      return False
    if not cutter.cut(new_chain.M3l < 80, 'm3l<80'):            return False
    if not cutter.cut(chain._met < 75, 'MET < 75'):             return False
    if not cutter.cut(not containsOSSF(chain), 'no OSSF'):      return False
    return True 

#
# High mass region cuts modeled after AN-2017
#     
def highMassCuts(chain, new_chain, cutter):
    calculateKinematicVariables(chain, new_chain)
    if not cutter.cut(new_chain.l_pt[l1] > 55, 'l1pt>55'):        return False
    if not cutter.cut(new_chain.l_pt[l2] > 15, 'l2pt>15'):        return False
    if not cutter.cut(new_chain.l_pt[l3] > 10, 'l3pt>10'):        return False
    if not cutter.cut(passesZcuts(chain, new_chain, same_flavor=True), 'M2l_OSSF_Z_veto'):        return False
    if not cutter.cut(abs(new_chain.M3l-91) > 15, 'M3l_Z_veto'):        return False 
    return True 

def calculateKinematicVariables(chain, new_chain, is_reco_level = True):
    l1Vec = getFourVec(new_chain.l_pt[l1], new_chain.l_eta[l1], new_chain.l_phi[l1], new_chain.l_e[l1])
    l2Vec = getFourVec(new_chain.l_pt[l2], new_chain.l_eta[l2], new_chain.l_phi[l2], new_chain.l_e[l2])
    l3Vec = getFourVec(new_chain.l_pt[l3], new_chain.l_eta[l3], new_chain.l_phi[l3], new_chain.l_e[l3])
    lVec = [l1Vec, l2Vec, l3Vec]

    #M3l
    new_chain.M3l = (l1Vec + l2Vec + l3Vec).M()

    #All combinations of dilepton masses
    new_chain.Ml12 = (l1Vec+l2Vec).M()         
    new_chain.Ml23 = (l2Vec+l3Vec).M()         
    new_chain.Ml13 = (l1Vec+l3Vec).M()

    #
    # Get OS, OSSF, SS, SSSF variables
    #
    min_os = [None, None]
    max_os = [None, None]
    min_ss = [None, None]
    max_ss = [None, None]
    min_ossf = [None, None]
    max_ossf = [None, None]
    min_sssf = [None, None]
    max_sssf = [None, None]

    tmp_minos = 99999999.
    tmp_minss = 99999999.
    tmp_minossf = 99999999.
    tmp_minsssf = 99999999.
    tmp_maxos = 0
    tmp_maxss = 0
    tmp_maxossf = 0
    tmp_maxsssf = 0
    for i1, l in enumerate([new_chain.l1, new_chain.l2, new_chain.l3]):
        for i2, sl in enumerate([new_chain.l1, new_chain.l2, new_chain.l3]):
            if i2 <= i1:        continue
            tmp_mass = (lVec[i1]+lVec[i2]).M()
            if new_chain.l_charge[i1] == new_chain.l_charge[i2]:
                if tmp_mass < tmp_minss: 
                    min_ss = [i1, i2]
                    tmp_minss = tmp_mass
                if tmp_mass > tmp_maxss: 
                    max_ss = [i1, i2]
                    tmp_maxss = tmp_mass
                if new_chain.l_flavor[i1] == new_chain.l_flavor[i2]:
                    if tmp_mass < tmp_minsssf: 
                        min_sssf = [i1, i2]
                        tmp_minsssf = tmp_mass
                    if tmp_mass > tmp_maxsssf: 
                        max_sssf = [i1, i2]
                        tmp_maxsssf = tmp_mass
            else:
                if tmp_mass < tmp_minos: 
                    min_os = [i1, i2]
                    tmp_minos = tmp_mass
                if tmp_mass > tmp_maxos: 
                    max_os = [i1, i2]
                    tmp_maxos = tmp_mass
                if new_chain.l_flavor[i1] == new_chain.l_flavor[i2]:
                    if tmp_mass < tmp_minossf: 
                        min_ossf = [i1, i2]
                        tmp_minossf = tmp_mass
                    if tmp_mass > tmp_maxossf: 
                        max_ossf = [i1, i2]
                        tmp_maxossf = tmp_mass


    #Mass variables
    chain.minMos = (lVec[min_os[0]]+lVec[min_os[1]]).M() if all(min_os) else 0
    chain.maxMos = (lVec[max_os[0]]+lVec[max_os[1]]).M() if all(max_os) else 0
    chain.minMss = (lVec[min_ss[0]]+lVec[min_ss[1]]).M() if all(min_ss) else 0
    chain.maxMss = (lVec[max_ss[0]]+lVec[max_ss[1]]).M() if all(max_ss) else 0
    chain.minMossf = (lVec[min_ossf[0]]+lVec[min_ossf[1]]).M() if all(min_ossf) else 0
    chain.maxMossf = (lVec[max_ossf[0]]+lVec[max_ossf[1]]).M() if all(max_ossf) else 0
    chain.minMsssf = (lVec[min_sssf[0]]+lVec[min_sssf[1]]).M() if all(min_sssf) else 0
    chain.maxMsssf = (lVec[max_sssf[0]]+lVec[max_sssf[1]]).M() if all(max_sssf) else 0  

    #MTother
    new_chain.index_other = [item for item in [new_chain.l1, new_chain.l2, new_chain.l3] if item not in min_os][0]   

    #TODO: Seems like there must be a better way to do this
    if is_reco_level:    
        new_chain.mtOther = np.sqrt(2*chain._met*chain._lPt[new_chain.index_other]*(1-np.cos(deltaPhi(chain._lPhi[new_chain.index_other], chain._metPhi))))
        
        #ptCone
        new_chain.pt_cone = []
        for l in xrange(chain._nLight):
            new_chain.pt_cone.append(chain._lPt[l]*(1+max(0., chain._miniIso[l]-0.4))) #TODO: is this the correct definition?

    else:
        new_chain.mtOther = np.sqrt(2*chain._gen_met*chain._gen_lPt[new_chain.index_other]*(1-np.cos(deltaPhi(chain._gen_lPhi[new_chain.index_other], chain._gen_metPhi))))
        # #ptCone
        # new_chain.pt_cone = []
        # for l in xrange(chain._nLight):
        #     new_chain.pt_cone.append(chain._lPt[l]) #TODO: is this the correct definition?
   
    #calculate #jets and #bjets
    njets = 0
    nbjets = 0
    # print 'start'
    for jet in xrange(chain._nJets):
        if isGoodJet(chain, jet): 
            # print 'new good jet with index : ', jet
            # print 'Is good b jet? ', isBJet(chain, jet, 'Deep', 'loose')    
            njets += 1        
            if isBJet(chain, jet, 'Deep', 'loose'): nbjets += 1

    new_chain.njets = njets
    new_chain.nbjets = nbjets
        
    new_chain.hasOSSF = containsOSSF(new_chain)

    #
    # dR variables
    # 
    new_chain.dr_l1l2 = l1Vec.DeltaR(l2Vec)
    new_chain.dr_l1l3 = l1Vec.DeltaR(l2Vec)
    new_chain.dr_l2l3 = l1Vec.DeltaR(l2Vec)

    new_chain.dr_minOS = lVec[min_os[0]].DeltaR(lVec[min_os[1]]) if all(min_os) else -999.
    new_chain.dr_maxOS = lVec[max_os[0]].DeltaR(lVec[max_os[1]]) if all(max_os) else -999.
    new_chain.dr_minSS = lVec[min_ss[0]].DeltaR(lVec[min_ss[1]]) if all(min_ss) else -999.
    new_chain.dr_maxSS = lVec[max_ss[0]].DeltaR(lVec[max_ss[1]]) if all(max_ss) else -999.
    new_chain.dr_minOSSF = lVec[min_ossf[0]].DeltaR(lVec[min_ossf[1]]) if all(min_ossf) else -999.
    new_chain.dr_maxOSSF = lVec[max_ossf[0]].DeltaR(lVec[max_ossf[1]]) if all(max_ossf) else -999.
    new_chain.dr_minSSSF = lVec[min_sssf[0]].DeltaR(lVec[min_sssf[1]]) if all(min_sssf) else -999.
    new_chain.dr_maxSSSF = lVec[max_sssf[0]].DeltaR(lVec[max_sssf[1]]) if all(max_sssf) else -999.

    new_chain.mindr_l1 = min(new_chain.dr_l1l2, new_chain.dr_l1l3)
    new_chain.maxdr_l1 = max(new_chain.dr_l1l2, new_chain.dr_l1l3)
    new_chain.mindr_l2 = min(new_chain.dr_l1l2, new_chain.dr_l2l3)
    new_chain.maxdr_l2 = max(new_chain.dr_l1l2, new_chain.dr_l2l3)
    new_chain.mindr_l3 = min(new_chain.dr_l1l3, new_chain.dr_l2l3)
    new_chain.maxdr_l3 = max(new_chain.dr_l1l3, new_chain.dr_l2l3)

    return

def passesZcuts(chain, new_chain, same_flavor=False):
    for fl in [0, 1]:
        l1Vec = getFourVec(new_chain.l_pt[fl], new_chain.l_eta[fl], new_chain.l_phi[fl], new_chain.l_e[fl])
        for sl in [1, 2]:
            if fl == sl: continue
            if new_chain.l_charge[fl] == new_chain.l_charge[sl]: continue
            if same_flavor and new_chain.l_flavor[fl] != new_chain.l_flavor[sl]: continue 
            l2Vec = getFourVec(new_chain.l_pt[sl], new_chain.l_eta[sl], new_chain.l_phi[sl], new_chain.l_e[sl])
            if abs((l1Vec + l2Vec).M() - 90.) < 15: return False
    return True
