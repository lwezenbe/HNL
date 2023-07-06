######################################################################
#       Selection of filters to drag and drop into selectors         #
######################################################################

from HNL.EventSelection.eventSelectionTools import bVeto, massDiff, passesZcuts, isOSSF, containsOSSF, fourthFOVeto, threeSameSignVeto, nBjets
from HNL.EventSelection.eventSelectionTools import l1, l2, l3, l4, MZ
from HNL.Tools.helpers import getFourVec, deltaPhi, deltaR


l1 = 0
l2 = 1
l3 = 2
l4 = 3

#
# SR filters
#

# AN 2017-014 base selection
def baseFilterAN2017(chain, new_chain, cutter):
    if not cutter.cut(not bVeto(chain), 'b-veto'):              return False
    if not cutter.cut(not threeSameSignVeto(new_chain), 'three_same_sign_veto'):                    return False
    if not cutter.cut(not fourthFOVeto(chain, new_chain, no_tau=chain.obj_sel['notau']), '4th_l_veto'):   return False

    return True

# Basic cuts every event has to pass
def baseFilterCutBased(chain, new_chain, cutter):
    if not cutter.cut(not fourthFOVeto(chain, new_chain, no_tau=chain.obj_sel['notau']), 'Fourth FO veto'):        return False 
    if not cutter.cut(not threeSameSignVeto(new_chain), 'No three same sign'):        return False
    if not cutter.cut(not bVeto(chain), 'b-veto'):              return False
    return True

# Basic cuts every event has to pass
def baseFilterMVA(chain, new_chain, cutter):
    if not cutter.cut(not fourthFOVeto(chain, new_chain, no_tau=chain.obj_sel['notau']), 'Fourth FO veto'):        return False 
    if not cutter.cut(not threeSameSignVeto(new_chain), 'No three same sign'):        return False
    if not cutter.cut(not bVeto(chain), 'b-veto'):              return False
    return True

def passBaseCuts(chain, new_chain, cutter):
    if chain.selection == 'AN2017014':
        return baseFilterAN2017(chain, new_chain, cutter)
    elif chain.strategy == 'MVA':
        return baseFilterMVA(chain, new_chain, cutter)
    else:
        return baseFilterCutBased(chain, new_chain, cutter)


#Low mass selection
def passLowMassSelection(chain, new_chain, cutter, loose_selection = False, inverted_m3l = False, early_stop = False):
    if not cutter.cut(new_chain.l_pt[l1] < 55, 'l1pt<55'):      return False
    if not inverted_m3l:
        if not cutter.cut(new_chain.M3l < 80, 'm3l<80'):            return False
    else:
        if not cutter.cut(new_chain.M3l > 80, 'm3l>80'):            return False
    
    if not cutter.cut(chain.met < 75, 'MET < 75'):             return False
    if early_stop: return True

    if not loose_selection:
        if not cutter.cut(not containsOSSF(new_chain), 'no OSSF'):      return False
    else:
        if containsOSSF(new_chain):
            if not cutter.cut(abs(new_chain.MZossf-MZ) > 15, 'M2l_OSSF_Z_veto'):        return False
            if not cutter.cut(new_chain.minMossf > 5, 'minMossf'): return False
        else:
            #This is just to correctly fill the cutter
            cutter.cut(True, 'M2l_OSSF_Z_veto')
            cutter.cut(True, 'minMossf')
    return True 

#High mass selection
def passHighMassSelection(chain, new_chain, cutter, ossf = None, invert_pt = False):
    if not invert_pt:
        if not cutter.cut(new_chain.l_pt[l1] > 55, 'l1pt>55'):        return False
    else:
        if not cutter.cut(new_chain.l_pt[l1] < 55, 'l1pt<55'):        return False
    if not cutter.cut(new_chain.l_pt[l2] > 15, 'l2pt>15'):        return False
    if not cutter.cut(new_chain.l_pt[l3] > 10, 'l3pt>10'):        return False
    if containsOSSF(new_chain):
        if not cutter.cut(abs(new_chain.MZossf-MZ) > 15, 'M2l_OSSF_Z_veto'):        return False
        if not cutter.cut(abs(new_chain.M3l-MZ) > 15, 'M3l_Z_veto'):        return False 
        if not cutter.cut(new_chain.minMossf > 5, 'minMossf'): return False
    else:
        cutter.cut(True, 'M2l_OSSF_Z_veto')
        cutter.cut(True, 'M3l_Z_veto')
        cutter.cut(True, 'minMossf')
    
    if ossf is not None:
        if ossf == False and not cutter.cut(not containsOSSF(chain), 'no OSSF'):      return False
        if ossf == True and not cutter.cut(containsOSSF(chain), 'OSSF'):      return False

    return True 

    

#
# CR filters
#

def passedFilterHighMassWithBjet(chain, new_chain, cutter):
    if not cutter.cut(not fourthFOVeto(chain, new_chain, no_tau=chain.obj_sel['notau']), 'Fourth FO veto'):        return False
    if not cutter.cut(not threeSameSignVeto(new_chain), 'No three same sign'):        return False
    if not cutter.cut(nBjets(chain, 'tight') > 0, '> 0 b-jets'):      return False
    return passHighMassSelection(chain, new_chain, cutter)


def passedFilterTauMixCT(chain, new_chain, cutter, high_met, b_veto, no_met):
    if not cutter.cut(not fourthFOVeto(chain, new_chain, no_tau=chain.obj_sel['notau']), 'Fourth FO veto'):        return False 
    if not cutter.cut(not threeSameSignVeto(new_chain), 'No three same sign'):        return False
    if b_veto and not cutter.cut(not bVeto(chain), 'b-veto'):              return False
    #if not cutter.cut(new_chain.l_flavor.count(2) == 2, '2 tau'):                   return False
    if not cutter.cut(new_chain.l_pt[l1] < 55, 'l1pt<55'):      return False
    if not cutter.cut(new_chain.M3l > 150, 'm3l>150'):            return False
    if not no_met:
        if high_met:
            if not cutter.cut(chain.met > 75, 'MET > 75'):             return False
        else:
            if not cutter.cut(chain.met < 75, 'MET < 75'):             return False
    if not cutter.cut(not containsOSSF(chain), 'no OSSF'):      return False
    return True

def passedFilterZZCR(chain, new_chain, cutter): 
    if not cutter.cut(chain.l_flavor.count(2) == 0, 'light leptons only'):      return False
    if not cutter.cut(not bVeto(chain), 'b-veto'):                              return False
    if not cutter.cut(massDiff(chain.Mll_Z1, MZ) < 15, 'First Z ok'):           return False
    if not cutter.cut(massDiff(chain.Mll_Z2, MZ) < 15, 'Second Z ok'):           return False
#    if not cutter.cut(new_chain.minMos > 12, 'min Mos > 12'):                   return False
    return True

def passedFilterWZCR(chain, new_chain, cutter):
    if not cutter.cut(not fourthFOVeto(chain, new_chain, no_tau=chain.obj_sel['notau']), 'Fourth FO veto'):        return False 
    if not cutter.cut(abs(new_chain.MZossf-MZ) < 15, 'On Z OSSF'):              return False
    if not cutter.cut(not bVeto(chain), 'b-veto'):                 return False
    if not cutter.cut(new_chain.l_pt[l1] > 25, 'l1pt>25'):          return False
    if not cutter.cut(new_chain.l_pt[l2] > 15, 'l2pt>15'):          return False
    if not cutter.cut(new_chain.l_pt[l3] > 10, 'l3pt>10'):          return False
    if not cutter.cut(chain.met > 50, 'MET > 50'):             return False
    if not cutter.cut(abs(new_chain.M3l-MZ) > 15, 'M3l_Z_veto'):    return False 
    return True

def passedFilterWZCRewkino(chain, new_chain, cutter):
    if not cutter.cut(abs(new_chain.MZossf-MZ) < 15, 'On Z OSSF'):              return False
    if not cutter.cut(not bVeto(chain), 'b-veto'):                 return False
    if not cutter.cut(new_chain.l_pt[l1] > 25, 'l1pt>25'):          return False
    if new_chain.l_flavor[l2] == 1:
        if not cutter.cut(new_chain.l_pt[l2] > 10, 'l2pt>10'):          return False
    else:
        if not cutter.cut(new_chain.l_pt[l2] > 15, 'l2pt>15'):          return False
    if not cutter.cut(new_chain.l_pt[l3] > 10, 'l3pt>10'):          return False
    if not cutter.cut(100. > chain.met > 50., '100 > MET > 50'):             return False
    if not cutter.cut(abs(new_chain.M3l-MZ) > 15, 'M3l_Z_veto'):    return False 
    if not cutter.cut(100. > new_chain.mtNonZossf > 50, 'MT cut'):    return False 
    return True

def passedFilterConversionCR(chain, new_chain, cutter):
    if not cutter.cut(containsOSSF(chain), 'OSSF present'):         return False
    if not cutter.cut(abs(new_chain.M3l-MZ) < 10, 'M3l_onZ'):       return False 
    if not cutter.cut(chain.MZossf < 75, 'Mll < 75'):               return False
    if chain.selection == 'AN2017014' and not cutter.cut(passesPtCutsAN2017014(chain), 'pt_cuts'):     return False 
    if not cutter.cut(not bVeto(chain), 'b-veto'):                 return False
    return True   

def passedFilterConversionCRtZq(chain, new_chain, cutter):
    if not cutter.cut(not fourthFOVeto(chain, new_chain, no_tau=chain.obj_sel['notau']), 'Fourth FO veto'):        return False 
    if not cutter.cut(new_chain.l_pt[l1] > 25, 'l1pt>25'):          return False
    if not cutter.cut(new_chain.l_pt[l2] > 15, 'l2pt>15'):          return False
    if not cutter.cut(new_chain.l_pt[l3] > 10, 'l3pt>10'):          return False
    if not cutter.cut(containsOSSF(chain), 'OSSF present'):         return False
    if not cutter.cut(abs(new_chain.M3l-MZ) < 15, 'M3l_onZ'):       return False 
    from HNL.EventSelection.eventSelectionTools import noMllOnZ
    if not cutter.cut(noMllOnZ(new_chain), 'Mll_offZ'):                        return False
    if not cutter.cut(chain.minMossf > 35, 'Mll > 35'):             return False
    return True   

def passedFilterTauFakeEnrichedDY(chain, new_chain, cutter, b_veto, nometcut, inverted_met_cut):
    if not cutter.cut(new_chain.l_flavor.count(2) == 1, '1 tau'):                   return False
    if not cutter.cut(not fourthFOVeto(chain, new_chain, no_tau=chain.obj_sel['notau']), 'Fourth FO veto'):        return False 

    if not cutter.cut(new_chain.l_flavor[0] == new_chain.l_flavor[1], 'SF'):        return False
    if not cutter.cut(new_chain.l_charge[0] != new_chain.l_charge[1], 'OS'):        return False

    l1Vec = getFourVec(new_chain.l_pt[0], new_chain.l_eta[0], new_chain.l_phi[0], new_chain.l_e[0])
    l2Vec = getFourVec(new_chain.l_pt[1], new_chain.l_eta[1], new_chain.l_phi[1], new_chain.l_e[1])

    if not cutter.cut(abs(91.19 - (l1Vec + l2Vec).M()) < 15, 'Z window'):             return False
    if not nometcut:
        if not inverted_met_cut and not cutter.cut(chain.met < 50, 'MET < 50'):                                 return False
        if inverted_met_cut and not cutter.cut(chain.met > 50, 'MET > 50'):                                 return False

    if b_veto and not cutter.cut(not bVeto(chain), 'b-veto'): return False

    # if not cutter.cut(chain._tauGenStatus[chain.l_indices[2]] == 6, 'fake tau'):    return False
    return True

def passedFilterLightLepFakeEnrichedDY(chain, new_chain, cutter, tightwp, fake_flavors):

    if not cutter.cut(new_chain.l_flavor.count(2) == 0, 'no tau'):                   return None

    l1Vec = getFourVec(new_chain.l_pt[0], new_chain.l_eta[0], new_chain.l_phi[0], new_chain.l_e[0])
    l2Vec = getFourVec(new_chain.l_pt[1], new_chain.l_eta[1], new_chain.l_phi[1], new_chain.l_e[1])
    l3Vec = getFourVec(new_chain.l_pt[2], new_chain.l_eta[2], new_chain.l_phi[2], new_chain.l_e[2])
    lVec = [l1Vec, l2Vec, l3Vec]

    if tightwp:
        if not cutter.cut(abs(new_chain.MZossf-MZ) < 15, 'On Z OSSF'):              return None
        fake_index = new_chain.index_nonZossf
        ossf_pair = [item for item in [0, 1, 2] if item != fake_index]
    else:
        ossf_pair = None
        closest_mass = 99999.
        for i1 in xrange(3):
            if not new_chain.l_istight[i1]: continue
            for i2 in xrange(3):
                if i2 <= i1 or not new_chain.l_istight[i2]: continue
                if not isOSSF(new_chain, i1, i2): continue
                tmp_mass = (lVec[i1]+lVec[i2]).M()
                if abs(tmp_mass - 91.) < abs(closest_mass - 91.): 
                    ossf_pair = [i1, i2]
                    closest_mass = tmp_mass
        if ossf_pair is None:   return None
        fake_index = [item for item in [0, 1, 2] if item not in ossf_pair][0] 

    if new_chain.l_flavor[fake_index] not in fake_flavors: return None     
    
    if not cutter.cut(chain.met < 50, 'MET < 50'):                                 return None

    if not cutter.cut(not bVeto(chain), 'b-veto'):                   return None 

    if isOSSF(new_chain, fake_index, ossf_pair[0]) and abs((lVec[fake_index]+lVec[ossf_pair[0]]).M() - 91.) < 15: return None
    if isOSSF(new_chain, fake_index, ossf_pair[1]) and abs((lVec[fake_index]+lVec[ossf_pair[1]]).M() - 91.) < 15: return None

    if not cutter.cut(abs(new_chain.M3l-MZ) > 15, 'Off-Z m3l'):              return None
    metVec = getFourVec(chain.met, 0., chain.metPhi, chain.met)
    if not cutter.cut((metVec+lVec[fake_index]).Mt() > 80, 'Remove WZ'):              return None

    return fake_index


def passedFilterTauFakeEnrichedTT(chain, new_chain, cutter, inverted_cut):
    if not cutter.cut(new_chain.l_flavor.count(0) == 1, '1 e'):                   return False
    if not cutter.cut(new_chain.l_flavor.count(1) == 1, '1 mu'):                  return False
    if not cutter.cut(new_chain.l_flavor.count(2) == 1, '1 tau'):                 return False
    if not cutter.cut(new_chain.l_charge[0] != new_chain.l_charge[1], 'OS'):        return False

    if not cutter.cut(nBjets(chain, 'tight') > 0, '> 0 b-jets'):      return False

    l1Vec = getFourVec(new_chain.l_pt[0], new_chain.l_eta[0], new_chain.l_phi[0], new_chain.l_e[0])
    l2Vec = getFourVec(new_chain.l_pt[1], new_chain.l_eta[1], new_chain.l_phi[1], new_chain.l_e[1])

    if not inverted_cut:
        if not cutter.cut((l1Vec + l2Vec).M() > 20, 'Mll > 20'):             return False
    else:
        if not cutter.cut((l1Vec + l2Vec).M() < 20, 'Mll < 20'):             return False

    #if not cutter.cut(chain.met < 50, 'MET < 50'):                                 return False

    # if not cutter.cut(chain._tauGenStatus[chain.l_indices[2]] == 6, 'fake tau'):    return False
    return True

def passedFilterLightLepFakeEnrichedTT(chain, new_chain, cutter, fake_flavors):

    if not cutter.cut(new_chain.l_flavor.count(2) == 0, 'no tau'):                   return False

    n_tight_ele = 0
    n_tight_mu = 0
    passed_charges = []
    for il, fl in enumerate(new_chain.l_flavor):
        if new_chain.l_istight[il]:
            if fl == 0: n_tight_ele += 1
            if fl == 1: n_tight_mu += 1
            passed_charges.append(new_chain.l_charge[il])
        else:
            if fl not in fake_flavors: return False  
    
    if not cutter.cut(n_tight_ele > 0, '> 0 tight ele'):                return False
    if not cutter.cut(n_tight_mu > 0, '> 0 tight mu'):                return False

    from HNL.EventSelection.eventSelectionTools import noMllOnZ
    if not cutter.cut(noMllOnZ(new_chain), 'Mll_offZ'):                        return False

    #At this stage at least 1 ele and 1 mu in passed_charges, if not all charges the same, at least one OSOF pair
    if not cutter.cut(not all([x == passed_charges[0] for x in passed_charges]), 'OSOF pair'): return False 
    
    if not cutter.cut(nBjets(chain, 'tight') > 0, '> 0 b-jets'):      return False

    return True

def passedGeneralMCCT(chain, new_chain, cutter, flavors):
    if 'tau' in flavors:
        if not cutter.cut(chain.met < 50, 'MET<50'): return False
        # if not cutter.cut(containsOSSF(chain), 'OSSF present'): return False
        if not cutter.cut(not bVeto(chain), 'b-veto'): return False
    return True
