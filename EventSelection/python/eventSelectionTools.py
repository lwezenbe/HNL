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
from HNL.ObjectSelection.leptonSelector import isGoodLepton, isFakeLepton
from HNL.ObjectSelection.leptonSelector import isGoodGenLepton
from HNL.ObjectSelection.jetSelector import isGoodJet, isGoodBJet
from HNL.Tools.helpers import getFourVec, deltaPhi
from HNL.Weights.tauEnergyScale import TauEnergyScale



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
#
def selectLeptonsGeneral(chain, new_chain, nL, cutter=None, sort_leptons = True):

    collection = chain._nL if not chain.obj_sel['notau'] else chain._nLight
    chain.leptons = []
    from HNL.ObjectSelection.leptonSelector import getLeptonPt, getLeptonE
    from HNL.ObjectSelection.electronSelector import getElectronPt, getElectronE
    from HNL.ObjectSelection.muonSelector import getMuonPt, getMuonE

    for l in xrange(collection):
        if chain._lFlavor[l] == 0: 
            pt_to_use = getLeptonPt(chain, l)
        elif chain._lFlavor[l] == 1: 
            pt_to_use = getLeptonPt(chain, l)
        elif chain._lFlavor[l] == 2: 
            pt_to_use = chain._lPt[l]
        else: 
            raise RuntimeError('In selectLeptonsGeneral: flavor provided is neither an electron, muon or tau')

        if isGoodLepton(chain, l):
            chain.leptons.append((pt_to_use, l)) 
        #from HNL.ObjectSelection.leptonSelector import isGoodLeptonGeneral #In case you need prompt leptons
        #if isGoodLeptonGeneral(chain, l, algo = 'prompt'):
        #    chain.leptons.append((pt_to_use, l)) 
     
    keep_sideband = chain.need_sideband

    if keep_sideband is not None:
        if not cutter.cut(len(chain.leptons) == nL, '3 FO leptons'): return False
    else:
        if not cutter.cut(len(chain.leptons) == nL, '3 tight leptons'): return False
        
    if keep_sideband is not None:
        tight = 0
        for (pt, l) in chain.leptons:
            if isGoodLepton(chain, l, 'tight'): tight += 1
        chain.is_sideband = tight != nL
    else:
        chain.is_sideband = False
                
 
    if chain is new_chain:
        new_chain.l_pt = [0.0]*nL
        new_chain.l_eta = [0.0]*nL
        new_chain.l_phi = [0.0]*nL
        new_chain.l_charge = [0.0]*nL
        new_chain.l_flavor = [0.0]*nL
        new_chain.l_e = [0.0]*nL
        new_chain.l_indices = [0.0]*nL
        new_chain.l_isFO = [0.0]*nL
        new_chain.l_istight = [0.0]*nL
        new_chain.light_pt = [0.0]*nL
        new_chain.light_eta = [0.0]*nL
        new_chain.light_phi = [0.0]*nL
        new_chain.light_charge = [0.0]*nL
        new_chain.light_flavor = [0.0]*nL
        new_chain.light_e = [0.0]*nL
        new_chain.light_indices = [0.0]*nL
        if not chain.is_data:
            new_chain.l_isfake = [0.0]*nL

    if sort_leptons: 
        ptAndIndex = sorted(chain.leptons, reverse=True, key = getSortKey)
    else:
        ptAndIndex = chain.leptons

    light_index = 0
    for i in xrange(nL):
        new_chain.l_indices[i] = ptAndIndex[i][1]
        new_chain.l_flavor[i] = chain._lFlavor[ptAndIndex[i][1]]
        new_chain.l_pt[i] = ptAndIndex[i][0]
        new_chain.l_eta[i] = chain._lEta[ptAndIndex[i][1]]
        new_chain.l_phi[i] = chain._lPhi[ptAndIndex[i][1]]
        new_chain.l_e[i] = getLeptonE(chain, ptAndIndex[i][1]) if new_chain.l_flavor[i] < 2 else chain._lE[ptAndIndex[i][1]]
        new_chain.l_charge[i] = chain._lCharge[ptAndIndex[i][1]]
        new_chain.l_isFO[i] = isGoodLepton(chain, ptAndIndex[i][1], 'FO')
        new_chain.l_istight[i] = isGoodLepton(chain, ptAndIndex[i][1], 'tight')
        if not chain.is_data:
            new_chain.l_isfake[i] = isFakeLepton(chain, ptAndIndex[i][1])
        
        if new_chain.l_flavor[i] < 2:
            new_chain.light_indices[light_index] = ptAndIndex[i][1]
            new_chain.light_flavor[light_index] = chain._lFlavor[ptAndIndex[i][1]]
            new_chain.light_pt[light_index] = ptAndIndex[i][0]
            new_chain.light_eta[light_index] = chain._lEta[ptAndIndex[i][1]]
            new_chain.light_phi[light_index] = chain._lPhi[ptAndIndex[i][1]]
            new_chain.light_e[light_index] = getLeptonE(chain, ptAndIndex[i][1])
            new_chain.light_charge[light_index] = chain._lCharge[ptAndIndex[i][1]]
            light_index += 1

    new_chain.n_ele = [x for x in new_chain.l_flavor].count(0)
    new_chain.n_mu = [x for x in new_chain.l_flavor].count(1)
    new_chain.n_tau = [x for x in new_chain.l_flavor].count(2)

    if not chain.is_data:
        prompt_list = [chain._lIsPrompt[l] for l in new_chain.l_indices]
        new_chain.is_prompt = all(prompt_list)
    else:
        new_chain.is_prompt = True
      
    return True

def select3Leptons(chain, new_chain, cutter = None):
    # chain.obj_sel['tau_wp'] = 'tight'
    # chain.obj_sel['mu_wp'] = 'tight'
    # chain.obj_sel['ele_wp'] = 'tight'
    return selectLeptonsGeneral(chain, new_chain, 3, cutter=cutter, sort_leptons = True)

def select3TightLeptons(chain, new_chain, cutter = None):
    chain.obj_sel['tau_wp'] = 'tight'
    chain.obj_sel['mu_wp'] = 'tight'
    chain.obj_sel['ele_wp'] = 'tight'
    return selectLeptonsGeneral(chain, new_chain, 3, cutter=cutter, sort_leptons = True)

def select4Leptons(chain, new_chain, cutter = None):
    # chain.obj_sel['tau_wp'] = 'tight'
    # chain.obj_sel['mu_wp'] = 'tight'
    # chain.obj_sel['ele_wp'] = 'tight'
    return selectLeptonsGeneral(chain, new_chain, 4, cutter=cutter, sort_leptons = True)

def selectGenLeptonsGeneral(chain, new_chain, nL, cutter=None):
  
    if chain is new_chain:
        new_chain.l_indices = [0.0]*nL
        new_chain.l_pt = [0.0]*nL
        new_chain.l_eta = [0.0]*nL
        new_chain.l_phi = [0.0]*nL
        # new_chain.l_vispt = [0.0]*nL
        # new_chain.l_viseta = [0.0]*nL
        # new_chain.l_visphi = [0.0]*nL
        new_chain.l_charge = [0.0]*nL
        new_chain.l_flavor = [0.0]*nL
        new_chain.l_e = [0.0]*nL
        #new_chain.l_dxy = [0.0]*nL
        #new_chain.l_dz = [0.0]*nL
        # new_chain.l_vise = [0.0]*nL
 
    chain.leptons = []
    for l in xrange(chain._gen_nL):
        if isGoodGenLepton(chain, l): 
            chain.leptons.append((chain._gen_lPt[l], l))  

    if not cutter.cut(len(chain.leptons) == nL, '3 prompt leptons'):  return False

    ptAndIndex = sorted(chain.leptons, reverse=True, key = getSortKey)

    for i in xrange(nL):
        new_chain.l_indices[i] = ptAndIndex[i][1]
        new_chain.l_pt[i] = ptAndIndex[i][0] 
        new_chain.l_eta[i] = chain._gen_lEta[ptAndIndex[i][1]]
        new_chain.l_phi[i] = chain._gen_lPhi[ptAndIndex[i][1]]
        new_chain.l_e[i] = chain._gen_lE[ptAndIndex[i][1]]
        # new_chain.l_vispt[i] = chain._gen_lVisPt[ptAndIndex[i][1]] 
        # new_chain.l_viseta[i] = chain._gen_lVisEta[ptAndIndex[i][1]]
        # new_chain.l_visphi[i] = chain._gen_lVisPhi[ptAndIndex[i][1]]
        # new_chain.l_vise[i] = chain._gen_lVisE[ptAndIndex[i][1]]
        new_chain.l_charge[i] = chain._gen_lCharge[ptAndIndex[i][1]]
        new_chain.l_flavor[i] = chain._gen_lFlavor[ptAndIndex[i][1]]
        #new_chain.l_dxy[i] = chain._gen_dxy[ptAndIndex[i][1]]
        #new_chain.l_dz[i] = chain._gen_dz[ptAndIndex[i][1]]
    
    prompt_list = [chain._gen_lIsPrompt[l] for l in new_chain.l_indices]
    new_chain.is_prompt = all(prompt_list)
    return True

#
# Meant for training NN, select up to two jets, if less than two jets, 
#
from HNL.ObjectSelection.bTagWP import returnBTagValueBySelection
def selectFirstTwoJets(chain, new_chain):
    if chain is new_chain:
        new_chain.j_pt = [0.0]*2
        new_chain.j_eta = [0.0]*2
        new_chain.j_phi = [0.0]*2
        new_chain.j_e = [0.0]*2
        new_chain.j_indices = [0.0]*2
        new_chain.j_btag = [0.0]*2

    from HNL.ObjectSelection.jetSelector import getJetPt
    chain.jets = [(getJetPt(chain, j), j) for j in xrange(chain._nJets) if isGoodJet(chain, j)]

    ptAndIndex = sorted(chain.jets, reverse=True, key = getSortKey)
 
    for i in xrange(2):
        if i < len(chain.jets):
            new_chain.j_pt[i] = ptAndIndex[i][0] 
            new_chain.j_eta[i] = chain._jetEta[ptAndIndex[i][1]]
            new_chain.j_phi[i] = chain._jetPhi[ptAndIndex[i][1]]
            new_chain.j_e[i] = chain._jetE[ptAndIndex[i][1]]
            new_chain.j_indices[i] = ptAndIndex[i][1] 
            new_chain.j_btag[i] = returnBTagValueBySelection(chain, ptAndIndex[i][1]) 
        else:
            new_chain.j_pt[i] = 0. 
            new_chain.j_eta[i] = 0.
            new_chain.j_phi[i] = 0.
            new_chain.j_e[i] = 0.
            new_chain.j_indices[i] = -1
            new_chain.j_btag[i] = -99.

    new_chain.dphi_j1met = deltaPhi(new_chain.j_phi[0], chain.metPhi) if new_chain.j_indices[0] >= 0 else -1
    new_chain.dphi_j2met = deltaPhi(new_chain.j_phi[1], chain.metPhi) if new_chain.j_indices[1] >= 0 else -1

    return True 


#########################################

#   calculating the event variables     #

#########################################

#
# Function to calculate all kinematic variables to be used later on in the selection steps
# All variables are stored in the chain so they can be called anywhere
#
from HNL.Tools.helpers import deltaR
def calculateEventVariables(chain, new_chain, nL = None, is_reco_level = True):
    calculateGeneralVariables(chain, new_chain, is_reco_level=is_reco_level)
    if nL == 3:
        calculateThreeLepVariables(chain, new_chain, is_reco_level = is_reco_level)
    if nL == 4:
        calculateFourLepVariables(chain, new_chain)

from HNL.ObjectSelection.leptonSelector import coneCorrection
def calculateGeneralVariables(chain, new_chain, is_reco_level = True):
    if is_reco_level:
        #ptCone
        #new_chain.dr_closestJet = [0.0]*20
        new_chain.dr_closestJet = []
        for il, l in enumerate(new_chain.l_indices):

#            closest_jet = findClosestJet(chain, new_chain, il)
#            if closest_jet is None:
#                new_chain.dr_closestJet.append(-1.)
#            else:
#                new_chain.dr_closestJet.append(deltaR(new_chain.l_eta[il], chain._jetEta[closest_jet], new_chain.l_phi[il], chain._jetPhi[closest_jet]))
            new_chain.dr_closestJet.append(0.)

        #calculate #jets and #bjets
        new_chain.njets = len(selectJets(chain))
        new_chain.nbjets = nBjets(chain, 'loose')
        new_chain.HT = calcHT(chain, new_chain)
        selectFirstTwoJets(chain, new_chain)

    

    new_chain.hasOSSF = containsOSSF(new_chain)

    new_chain.LT = calcLT(chain, new_chain)

def calculateThreeLepVariables(chain, new_chain, is_reco_level = True):

    l1Vec = getFourVec(new_chain.l_pt[l1], new_chain.l_eta[l1], new_chain.l_phi[l1], new_chain.l_e[l1])
    l2Vec = getFourVec(new_chain.l_pt[l2], new_chain.l_eta[l2], new_chain.l_phi[l2], new_chain.l_e[l2])
    l3Vec = getFourVec(new_chain.l_pt[l3], new_chain.l_eta[l3], new_chain.l_phi[l3], new_chain.l_e[l3])
    metVec = getFourVec(chain.met, 0., chain.metPhi, chain.met)
    lVec = [l1Vec, l2Vec, l3Vec]

    #M3l
    new_chain.M3l = (l1Vec + l2Vec + l3Vec).M()

    #All combinations of dilepton masses
    new_chain.Ml12 = (l1Vec+l2Vec).M()         
    new_chain.Ml23 = (l2Vec+l3Vec).M()         
    new_chain.Ml13 = (l1Vec+l3Vec).M()

    #All mt's
    new_chain.mtl1 = np.sqrt(2*chain.met*new_chain.l_pt[l1]*(1-np.cos(deltaPhi(new_chain.l_phi[l1], chain.metPhi))))
    new_chain.mtl2 = np.sqrt(2*chain.met*new_chain.l_pt[l2]*(1-np.cos(deltaPhi(new_chain.l_phi[l2], chain.metPhi))))
    new_chain.mtl3 = np.sqrt(2*chain.met*new_chain.l_pt[l3]*(1-np.cos(deltaPhi(new_chain.l_phi[l3], chain.metPhi))))

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
    chain.index_other = [item for item in [0, 1, 2] if item not in min_os][0] if min_os is not None else None
    chain.index_nonZossf = [item for item in [0, 1, 2] if item not in z_ossf][0] if z_ossf is not None else None

    if chain.index_other is not None:
        new_chain.mtOther = np.sqrt(2*chain.met*new_chain.l_pt[chain.index_other]*(1-np.cos(deltaPhi(new_chain.l_phi[chain.index_other], chain.metPhi))))
        leading_os = min_os[0] if new_chain.l_pt[min_os[0]] > new_chain.l_pt[min_os[1]] else min_os[1]
        subleading_os = min_os[0] if new_chain.l_pt[min_os[0]] < new_chain.l_pt[min_os[1]] else min_os[1]
        new_chain.mtl1os = np.sqrt(2*chain.met*new_chain.l_pt[leading_os]*(1-np.cos(deltaPhi(new_chain.l_phi[leading_os], chain.metPhi))))
        new_chain.mtl2os = np.sqrt(2*chain.met*new_chain.l_pt[subleading_os]*(1-np.cos(deltaPhi(new_chain.l_phi[subleading_os], chain.metPhi))))
    else:
        new_chain.mtOther = -1
        new_chain.mtl1os = -1
        new_chain.mtl2os = -1

    if chain.index_nonZossf is not None:
        new_chain.mtNonZossf = np.sqrt(2*chain.met*new_chain.l_pt[chain.index_nonZossf]*(1-np.cos(deltaPhi(new_chain.l_phi[chain.index_nonZossf], chain.metPhi))))
    else:
        new_chain.mtNonZossf = -1


    #MT3 
    new_chain.mt3 = (l1Vec+l2Vec+l3Vec+metVec).Mt()

    #
    # dR variables
    # 
    new_chain.dr_l1l2 = l1Vec.DeltaR(l2Vec)
    new_chain.dr_l1l3 = l1Vec.DeltaR(l3Vec)
    new_chain.dr_l2l3 = l2Vec.DeltaR(l3Vec)

    new_chain.dr_minOS = lVec[min_os[0]].DeltaR(lVec[min_os[1]]) if min_os is not None else -1.
    new_chain.dr_maxOS = lVec[max_os[0]].DeltaR(lVec[max_os[1]]) if max_os is not None else -1.
    new_chain.dr_minSS = lVec[min_ss[0]].DeltaR(lVec[min_ss[1]]) if min_ss is not None else -1.
    new_chain.dr_maxSS = lVec[max_ss[0]].DeltaR(lVec[max_ss[1]]) if max_ss is not None else -1.
    new_chain.dr_minOSSF = lVec[min_ossf[0]].DeltaR(lVec[min_ossf[1]]) if min_ossf is not None else -1.
    new_chain.dr_maxOSSF = lVec[max_ossf[0]].DeltaR(lVec[max_ossf[1]]) if max_ossf is not None else -1.
    new_chain.dr_minSSSF = lVec[min_sssf[0]].DeltaR(lVec[min_sssf[1]]) if min_sssf is not None else -1.
    new_chain.dr_maxSSSF = lVec[max_sssf[0]].DeltaR(lVec[max_sssf[1]]) if max_sssf is not None else -1.

    new_chain.mindr_l1 = min(new_chain.dr_l1l2, new_chain.dr_l1l3)
    new_chain.maxdr_l1 = max(new_chain.dr_l1l2, new_chain.dr_l1l3)
    new_chain.mindr_l2 = min(new_chain.dr_l1l2, new_chain.dr_l2l3)
    new_chain.maxdr_l2 = max(new_chain.dr_l1l2, new_chain.dr_l2l3)
    new_chain.mindr_l3 = min(new_chain.dr_l1l3, new_chain.dr_l2l3)
    new_chain.maxdr_l3 = max(new_chain.dr_l1l3, new_chain.dr_l2l3)

    new_chain.dphi_l1met = deltaPhi(new_chain.l_phi[0], chain.metPhi)
    new_chain.dphi_l2met = deltaPhi(new_chain.l_phi[1], chain.metPhi)
    new_chain.dphi_l3met = deltaPhi(new_chain.l_phi[2], chain.metPhi)

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


def translateForTraining(chain):
    chain.l1_pt = chain.l_pt[0]
    chain.l2_pt = chain.l_pt[1]
    chain.l3_pt = chain.l_pt[2]
    chain.l1_eta = chain.l_eta[0]
    chain.l1_phi = chain.l_phi[0]
    chain.l2_eta = chain.l_eta[1]
    chain.l2_phi = chain.l_phi[1]
    chain.l3_eta = chain.l_eta[2]
    chain.l3_phi = chain.l_phi[2]
    chain.l1_charge = chain.l_charge[0]
    chain.l2_charge = chain.l_charge[1]
    chain.l3_charge = chain.l_charge[2]


#################################################

#       all components for event selection      #

#################################################

def selectJets(chain, cleaned = 'loose'):
    jet_indices = []
    for jet in xrange(chain._nJets):
        if isGoodJet(chain, jet, cleaned=cleaned): jet_indices.append(jet)
    return jet_indices

def nBjets(chain, wp):
    nbjets = 0
    for jet in xrange(chain._nJets):
        if isGoodBJet(chain, jet, wp): nbjets += 1
    return nbjets

def bVeto(chain):
    for jet in xrange(chain._nJets):
        if isGoodBJet(chain, jet, 'loose'): return True    
    return False

def findClosestJet(chain, new_chain, lepton_index):
    mindr = 1000.
    mindr_jet = None
    for jet in selectJets(chain):
        dr = deltaR(new_chain.l_eta[lepton_index], chain._jetEta[jet], new_chain.l_phi[lepton_index], chain._jetPhi[jet])
        if dr < mindr:
            mindr = dr
            mindr_jet = jet
    return mindr_jet

def fourthFOVeto(chain, new_chain, no_tau = False):
    if no_tau: collection = chain._nLight 
    else:
        collection = chain._nL

    for lepton in xrange(collection):
        if lepton in new_chain.l_indices: continue
        if isGoodLepton(chain, lepton, 'FO'): return True
    return False

def passesPtCutsUpdated(chain):
    #
    # Copy cuts from last analysis for 
    #
    if not passesPtCutsAN2017014(chain):    return False

    if chain.category == CATEGORY_FROM_NAME['OS-TauEleEle'] or chain.category == CATEGORY_FROM_NAME['OS-EleTauEle']:
        tau_index = chain.l_flavor.index(2)
        other_indices = [s for s in range(3) if s != tau_index]
        if chain.l_pt[other_indices[0]] > 30: return True
        else: return chain.l_pt[other_indices[0]] > 25 and chain.l_pt[other_indices[1]] > 15
    elif chain.category == CATEGORY_FROM_NAME['OS-TauMuMu'] or chain.category == CATEGORY_FROM_NAME['OS-MuTauMu']:
        tau_index = chain.l_flavor.index(2)
        other_indices = [s for s in range(3) if s != tau_index]
        if chain.l_pt[other_indices[0]] > 30: return True
        else: return chain.l_pt[other_indices[0]] > 20 and chain.l_pt[other_indices[1]] > 9
    elif chain.category == CATEGORY_FROM_NAME['EleTauMu']:
        tau_index = chain.l_flavor.index(2)
        other_indices = [s for s in range(3) if s != tau_index]
        if chain.l_flavor[other_indices[1]] == 1:
            if chain.l_pt[other_indices[1]] > 8:    return chain.l_pt[other_indices[0]] > 23
            else:   return chain.l_pt[other_indices[0]] > 30
        else:
            return chain.l_pt[other_indices[0]] > 23 and chain.l_pt[other_indices[1]] > 12

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

def noMllOnZ(chain):
    for first_lepton in xrange(len(chain.l_indices)-1):
        for second_lepton in xrange(first_lepton + 1, len(chain.l_indices)):
            l1_vec = getFourVec(chain.l_pt[first_lepton], chain.l_eta[first_lepton], chain.l_phi[first_lepton], chain.l_e[first_lepton])
            l2_vec = getFourVec(chain.l_pt[second_lepton], chain.l_eta[second_lepton], chain.l_phi[second_lepton], chain.l_e[second_lepton])
            if massDiff((l1_vec+l2_vec).M(), MZ) < 15: return False
    return True


def containsOSSF(chain):
    for first_lepton in xrange(len(chain.l_indices)-1):
        for second_lepton in xrange(first_lepton + 1, len(chain.l_indices)):
            if isOSSF(chain, first_lepton, second_lepton): return True
    return False

def passesOSSFforZZ(chain):
    if massDiff(chain.Mll_Z1, MZ) > 15 or massDiff(chain.Mll_Z2, MZ) > 15: return False
    return True

def massDiff(m1, m2):
    return abs(m1-m2)

def calcHT(chain, new_chain):
    HT = 0.
    from HNL.ObjectSelection.jetSelector import getJetPt
    for jet in xrange(chain._nJets):
        if not isGoodJet(chain, jet):    continue 
        HT += getJetPt(chain, jet)
    return HT

def calcLT(chain, new_chain, is_reco_level = True):
    LT = 0.
    for lep in xrange(len(new_chain.l_indices)):
        LT += new_chain.l_pt[lep]
    LT += chain.met
    return LT

def objectInHEMregion(chain, new_chain):
    for eta, phi in zip(new_chain.l_eta, new_chain.l_phi):
        if eta < 1.3 and -1.57 < phi < -0.87: return True
    for j_index in selectJets(chain):
        if chain._jetEta[j_index] < 1.3 and -1.57 < chain._jetPhi[j_index] < -0.87: return True
    return False
    
#
# Functions that change some values in the tree
#
from HNL.ObjectSelection.leptonSelector import coneCorrection
def applyConeCorrection(chain, new_chain, light_algo = None, tau_algo = None):
    try:
        chain.conecorrection_applied
    except:
        chain.conecorrection_applied = False

    if not chain.conecorrection_applied:
        for i, chain_index in enumerate(new_chain.l_indices):
            if isGoodLepton(chain, chain_index, workingpoint = 'FO') and not isGoodLepton(chain, chain_index, workingpoint = 'tight'):
                new_chain.l_pt[i] *= coneCorrection(chain, chain_index, light_algo)
                new_chain.l_e[i] *= coneCorrection(chain, chain_index, light_algo)
    
    chain.conecorrection_applied = True



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
    if not cutter.cut(not bVeto(chain), 'b-veto'):              return False
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
    if not cutter.cut(not bVeto(chain), 'b-veto'):              return False
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
    if not cutter.cut(chain.met < 75, 'MET < 75'):             return False
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
    for i1, l in enumerate(new_chain.l_indices):
        for i2, sl in enumerate(new_chain.l_indices):
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
    chain.index_other = [item for item in range(3) if item not in min_os][0]   

    #TODO: Seems like there must be a better way to do this
    new_chain.mtOther = np.sqrt(2*chain.met*new_chain.l_pt[chain.index_other]*(1-np.cos(deltaPhi(new_chain.l_phi[chain.index_other], chain.metPhi))))
    if is_reco_level:    
        
        #ptCone
        new_chain.pt_cone = []
        for il, l in xrange(chain.l_flavor):
            if l < 2:
                new_chain.pt_cone.append(new_chain.l_pt[il]*(1+max(0., chain._miniIso[new_chain.l_indices[il]]-0.4))) #TODO: is this the correct definition?

   
    #calculate #jets and #bjets
    new_chain.njets = selectJets(chain)
    new_chain.nbjets = nBjets(chain, 'loose')
        
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

def isChargeFlip(chain, new_chain):
    for i, original_i in enumerate(new_chain.l_indices):
        if new_chain.l_flavor[i] == 2: continue
        if chain._lMatchCharge[original_i] * new_chain.l_charge[i] == -1.: return True
    return False

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

def passesChargeConsistencyDiElectron(chain, new_chain):
    electrons = []
    for i, l in enumerate(new_chain.l_indices):
        if new_chain.l_flavor[i] == 0:
            electrons.append(i)

    if len(electrons) != 2:
        return True

    if new_chain.l_charge[electrons[0]] != new_chain.l_charge[electrons[1]]:
        return True

    if not chain._lElectronChargeConst[new_chain.l_indices[electrons[0]]]:
        return False
    if not chain._lElectronChargeConst[new_chain.l_indices[electrons[1]]]:
        return False
    return True

def removeOverlapDYandZG(is_prompt, sample_name):
    if 'DY' in sample_name and is_prompt: return True
    if sample_name == 'ZG' and not is_prompt: return True
    return False
