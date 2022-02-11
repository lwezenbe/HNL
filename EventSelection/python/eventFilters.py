######################################################################
#       Selection of filters to drag and drop into selectors         #
######################################################################

from HNL.EventSelection.eventSelectionTools import bVeto, massDiff, passesZcuts, containsOSSF, fourthFOVeto, threeSameSignVeto, nBjets
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
def baseFilterMVA(chain, new_chain, cutter, for_training=False):
    if not cutter.cut(not fourthFOVeto(chain, new_chain, no_tau=chain.obj_sel['notau']), 'Fourth FO veto'):        return False 
    if not cutter.cut(not threeSameSignVeto(new_chain), 'No three same sign'):        return False
    if not for_training and not cutter.cut(not bVeto(chain), 'b-veto'):              return False
    return True

def passBaseCuts(chain, new_chain, cutter, for_training=False):
    if chain.selection == 'AN2017014':
        return baseFilterAN2017(chain, new_chain, cutter)
    elif chain.strategy == 'MVA':
        return baseFilterMVA(chain, new_chain, cutter, for_training=for_training)
    else:
        return baseFilterCutBased(chain, new_chain, cutter)


#Low mass selection
def passLowMassSelection(chain, new_chain, is_reco_level, cutter, for_training=False):
    if not for_training:
        if not cutter.cut(new_chain.l_pt[l1] < 55, 'l1pt<55'):      return False
        if not cutter.cut(new_chain.M3l < 80, 'm3l<80'):            return False
        if is_reco_level:
            if not cutter.cut(chain._met < 75, 'MET < 75'):             return False
        else:
            if not cutter.cut(chain._gen_met < 75, 'MET < 75'):             return False
        if not cutter.cut(not containsOSSF(new_chain), 'no OSSF'):      return False
    return True 

#High mass selection
def passHighMassSelection(chain, new_chain, is_reco_level, cutter, for_training=False):
    if not cutter.cut(new_chain.l_pt[l1] > 55, 'l1pt>55'):        return False
    if not cutter.cut(new_chain.l_pt[l2] > 15, 'l2pt>15'):        return False
    if not cutter.cut(new_chain.l_pt[l3] > 10, 'l3pt>10'):        return False
    if containsOSSF(new_chain):
        if not cutter.cut(abs(new_chain.MZossf-MZ) > 15, 'M2l_OSSF_Z_veto'):        return False
        if not for_training and not cutter.cut(abs(new_chain.M3l-MZ) > 15, 'M3l_Z_veto'):        return False 
        if not cutter.cut(new_chain.minMossf > 5, 'minMossf'): return False
    return True 

    

#
# CR filters
#

def passedFilterTauMixCT(chain, new_chain, is_reco_level, cutter, high_met = True, b_veto = True, m3lcut = False, no_met=False, m3lcut_inverted = False):
    if not cutter.cut(not fourthFOVeto(chain, new_chain, no_tau=chain.obj_sel['notau']), 'Fourth FO veto'):        return False 
    if not cutter.cut(not threeSameSignVeto(new_chain), 'No three same sign'):        return False
    if b_veto and not cutter.cut(not bVeto(chain), 'b-veto'):              return False
    if not cutter.cut(new_chain.l_pt[l1] < 55, 'l1pt<55'):      return False
    if m3lcut and not cutter.cut(new_chain.M3l < 80, 'm3l<80'):            return False
    if m3lcut_inverted and not cutter.cut(new_chain.M3l > 150, 'm3l>150'):            return False
    if not no_met:
        if is_reco_level:
            if high_met:
                if not cutter.cut(chain._met > 75, 'MET > 75'):             return False
            else:
                if not cutter.cut(chain._met < 75, 'MET < 75'):             return False
        else:
            if high_met:
                if not cutter.cut(chain._gen_met > 75, 'MET > 75'):             return False
            else:
                if not cutter.cut(chain._gen_met < 75, 'MET < 75'):             return False    
        if not cutter.cut(not containsOSSF(chain), 'no OSSF'):      return False
    return True

def passedFilterZZCR(chain, new_chain, cutter): 
    if not cutter.cut(chain.l_flavor.count(2) == 0, 'light leptons only'):      return False
    if not cutter.cut(not bVeto(chain), 'b-veto'):                              return False
    if not cutter.cut(massDiff(chain.Mll_Z1, MZ) < 15, 'First Z ok'):           return False
    if not cutter.cut(massDiff(chain.Mll_Z2, MZ) < 15, 'Second Z ok'):           return False
#    if not cutter.cut(new_chain.minMos > 12, 'min Mos > 12'):                   return False
    return True

def passedFilterWZCR(chain, new_chain, is_reco_level, cutter):
    if not cutter.cut(not fourthFOVeto(chain, new_chain, no_tau=chain.obj_sel['notau']), 'Fourth FO veto'):        return False 
    if not cutter.cut(abs(new_chain.MZossf-MZ) < 15, 'On Z OSSF'):              return False
    # if not cutter.cut(not passesZcuts(chain, new_chain, same_flavor=True), 'On Z OSSF'):              return False
    if not cutter.cut(not bVeto(chain), 'b-veto'):                 return False
    if not cutter.cut(new_chain.l_pt[l1] > 25, 'l1pt>25'):          return False
    if not cutter.cut(new_chain.l_pt[l2] > 15, 'l2pt>15'):          return False
    if not cutter.cut(new_chain.l_pt[l3] > 10, 'l3pt>10'):          return False
    if is_reco_level:
        if not cutter.cut(chain._met > 50, 'MET > 50'):             return False
    else:
        if not cutter.cut(chain._gen_met > 50, 'MET > 50'):         return False
    if not cutter.cut(abs(new_chain.M3l-MZ) > 15, 'M3l_Z_veto'):    return False 
    return True

def passedFilterWZCRewkino(chain, new_chain, is_reco_level, cutter):
    if not cutter.cut(abs(new_chain.MZossf-MZ) < 15, 'On Z OSSF'):              return False
    # if not cutter.cut(not passesZcuts(chain, new_chain, same_flavor=True), 'On Z OSSF'):              return False
    if not cutter.cut(not bVeto(chain), 'b-veto'):                 return False
    if not cutter.cut(new_chain.l_pt[l1] > 25, 'l1pt>25'):          return False
    if new_chain.l_flavor[l2] == 1:
        if not cutter.cut(new_chain.l_pt[l2] > 10, 'l2pt>10'):          return False
    else:
        if not cutter.cut(new_chain.l_pt[l2] > 15, 'l2pt>15'):          return False
    if not cutter.cut(new_chain.l_pt[l3] > 10, 'l3pt>10'):          return False
    if is_reco_level:
        if not cutter.cut(100. > chain._met > 50., '100 > MET > 50'):             return False
    else:
        if not cutter.cut(100. > chain._gen_met > 50, '100 > MET > 50'):         return False
    if not cutter.cut(abs(new_chain.M3l-MZ) > 15, 'M3l_Z_veto'):    return False 
    if not cutter.cut(100. > new_chain.mtNonZossf > 50, 'MT cut'):    return False 
    return True

def passedFilterConversionCR(chain, new_chain, cutter):
    if not cutter.cut(containsOSSF(chain), 'OSSF present'):         return False
    if not cutter.cut(abs(new_chain.M3l-MZ) < 15, 'M3l_onZ'):       return False 
    if not cutter.cut(chain.MZossf < 75, 'Mll < 75'):               return False
    #if not cutter.cut(chain.minMossf > 35, 'Mll > 35'):               return False
    if chain.selection == 'AN2017014' and not cutter.cut(passesPtCutsAN2017014(chain), 'pt_cuts'):     return False 
    if not cutter.cut(not bVeto(chain), 'b-veto'):                 return False
    return True   

def passedFilterConversionCRtZq(chain, new_chain, cutter):
    #print 'start'
    if not cutter.cut(not fourthFOVeto(chain, new_chain, no_tau=chain.obj_sel['notau']), 'Fourth FO veto'):        return False 
    #print 'fourth FO'
    if not cutter.cut(new_chain.l_pt[l1] > 25, 'l1pt>25'):          return False
    if not cutter.cut(new_chain.l_pt[l2] > 15, 'l2pt>15'):          return False
    if not cutter.cut(new_chain.l_pt[l3] > 10, 'l3pt>10'):          return False
    #print 'pt cuts'
    if not cutter.cut(containsOSSF(chain), 'OSSF present'):         return False
    #print 'OSSF'
    if not cutter.cut(abs(new_chain.M3l-MZ) < 15, 'M3l_onZ'):       return False 
    #print 'M3l'
    from HNL.EventSelection.eventSelectionTools import noMllOnZ
    if not cutter.cut(noMllOnZ(new_chain), 'Mll_offZ'):                        return False
    #print 'no Mll on Z'
    if not cutter.cut(chain.minMossf > 35, 'Mll > 35'):             return False
    #print 'minossf > 35'
    return True   

def passedFilterTauFakeEnrichedDY(chain, new_chain, cutter, inverted_cut=False, b_veto=False, nometcut=False):
    if not cutter.cut(new_chain.l_flavor.count(2) == 1, '1 tau'):                   return False

    if not cutter.cut(new_chain.l_flavor[0] == new_chain.l_flavor[1], 'SF'):        return False
    if not cutter.cut(new_chain.l_charge[0] != new_chain.l_charge[1], 'OS'):        return False

    l1Vec = getFourVec(new_chain.l_pt[0], new_chain.l_eta[0], new_chain.l_phi[0], new_chain.l_e[0])
    l2Vec = getFourVec(new_chain.l_pt[1], new_chain.l_eta[1], new_chain.l_phi[1], new_chain.l_e[1])

    if not cutter.cut(abs(91.19 - (l1Vec + l2Vec).M()) < 15, 'Z window'):             return False
    if not nometcut and not cutter.cut(chain._met < 50, 'MET < 50'):                                 return False

    if b_veto and not cutter.cut(not bVeto(chain), 'b-veto'): return False

    # if not cutter.cut(chain._tauGenStatus[chain.l_indices[2]] == 6, 'fake tau'):    return False
    return True

def passedFilterTauFakeEnrichedTT(chain, new_chain, cutter, inverted_cut=False):
    if not cutter.cut(new_chain.l_flavor.count(0) == 1, '1 e'):                   return False
    if not cutter.cut(new_chain.l_flavor.count(1) == 1, '1 mu'):                  return False
    if not cutter.cut(new_chain.l_flavor.count(2) == 1, '1 tau'):                 return False
    if not cutter.cut(new_chain.l_charge[0] != new_chain.l_charge[1], 'OS'):        return False

    if nBjets(chain, 'tight') < 1:      return False

    l1Vec = getFourVec(new_chain.l_pt[0], new_chain.l_eta[0], new_chain.l_phi[0], new_chain.l_e[0])
    l2Vec = getFourVec(new_chain.l_pt[1], new_chain.l_eta[1], new_chain.l_phi[1], new_chain.l_e[1])

    if not cutter.cut((l1Vec + l2Vec).M() > 20, 'Mll cut'):             return False

    if not cutter.cut(chain._met < 50, 'MET < 50'):                                 return False

    # if not cutter.cut(chain._tauGenStatus[chain.l_indices[2]] == 6, 'fake tau'):    return False
    return True

def passedGeneralMCCT(chain, new_chain, cutter, flavors):
    if 'tau' in flavors:
        if not cutter.cut(chain._met < 50, 'MET<50'): return False
        # if not cutter.cut(containsOSSF(chain), 'OSSF present'): return False
        if not cutter.cut(not bVeto(chain), 'b-veto'): return False
    return True
