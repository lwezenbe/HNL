from HNL.EventSelection.eventSelectionTools import *
import HNL.EventSelection.eventCategorization as cat
from HNL.ObjectSelection.leptonSelector import *
from HNL.Tools.helpers import getFourVec, deltaPhi, deltaR

class FilterObject(object):

    def __init__(self, name, selection, objsel, is_reco_level=True, event_categorization = None):
        self.name = name
        self.selection = selection
        self.objsel = objsel
        self.is_reco_level = is_reco_level
        self.ec = event_categorization

    def initEvent(self, chain, new_chain, nL, cutter, sort_leptons):
        if self.is_reco_level:
            if not cutter.cut(selectLeptonsGeneral(chain, new_chain, nL, self.objsel, cutter=cutter, sort_leptons = sort_leptons), 'select leptons'): return False
        else:
            if not cutter.cut(selectGenLeptonsGeneral(chain, new_chain, nL, self.objsel, cutter=cutter), 'select leptons'): return False
        calculateEventVariables(chain, new_chain, nL, is_reco_level=self.is_reco_level, selection=self.selection)
        chain.category = max(cat.CATEGORIES)
        return True

class ZZCRfilter(FilterObject):
    
    def __init__(self, name, selection, objsel, is_reco_level=True, event_categorization = None):
        super(ZZCRfilter, self).__init__(name, selection, objsel, is_reco_level=True, event_categorization = None)

    def initEvent(self, chain, new_chain, cutter):
        return super(ZZCRfilter, self).initEvent(chain, new_chain, 4, cutter, sort_leptons = True)

    def passedFilter(self, chain, new_chain, cutter):
        if not self.initEvent(chain, new_chain, cutter):                                                 return False
        if not cutter.cut(not bVeto(chain, self.selection, cleaned=False, selection = self.selection), 'b-veto'):                 return False

        #Relaxed
        if not cutter.cut(massDiff(chain.Mll_Z1, MZ) < 15, 'First Z ok'):                                                           return False
        if not cutter.cut(new_chain.minMos > 12, 'min Mos > 12'):                                                                       return False

        return True

class WZCRfilter(FilterObject):

    def __init__(self, name, selection, objsel, is_reco_level=True, event_categorization = None):
        super(WZCRfilter, self).__init__(name, selection, objsel, is_reco_level=True, event_categorization = None)

    def initEvent(self, chain, new_chain, cutter):
        return super(WZCRfilter, self).initEvent(chain, new_chain, 3, cutter, sort_leptons = True)

    def passedFilter(self, chain, new_chain, cutter):
        if not self.initEvent(chain, new_chain, cutter):                                                 return False
        if not cutter.cut(not passesZcuts(chain, new_chain, same_flavor=True), 'On Z OSSF'):              return False
        if not cutter.cut(new_chain.l_pt[l1] > 25, 'l1pt>25'):          return False
        if not cutter.cut(new_chain.l_pt[l2] > 15, 'l2pt>15'):          return False
        if not cutter.cut(new_chain.l_pt[l3] > 10, 'l3pt>10'):          return False
        if self.is_reco_level:
            if not cutter.cut(chain._met > 50, 'MET > 50'):             return False
        else:
            if not cutter.cut(chain._gen_met > 50, 'MET > 50'):         return False
        if not cutter.cut(abs(new_chain.M3l-MZ) > 15, 'M3l_Z_veto'):    return False 
        return True

class ConversionCRfilter(FilterObject):

    def __init__(self, name, selection, objsel, is_reco_level=True, event_categorization = None):
        super(ConversionCRfilter, self).__init__(name, selection, objsel, is_reco_level=True, event_categorization = None)

    def initEvent(self, chain, new_chain, cutter):
        return super(ConversionCRfilter, self).initEvent(chain, new_chain, 3, cutter, sort_leptons = True)

    def passedFilter(self, chain, new_chain, cutter):
        if not self.initEvent(chain, new_chain, cutter):                                                 return False
        if not cutter.cut(containsOSSF(chain), 'OSSF present'):         return False
        if not cutter.cut(abs(new_chain.M3l-MZ) < 15, 'M3l_onZ'):       return False 
        if not cutter.cut(chain.MZossf < 75, 'Mll < 75'):               return False
        if self.selection == 'AN2017014' and not cutter.cut(passesPtCutsAN2017014(chain), 'pt_cuts'):     return False 
        if not cutter.cut(not bVeto(chain, 'Deep', cleaned=False, selection = self.selection), 'b-veto'):                 return False
        chain.category = max(cat.CATEGORIES)
        return True

class TauFakeEnrichedDY(FilterObject):
    
    def __init__(self, name, selection, objsel, is_reco_level=True, event_categorization = None):
        super(TauFakeEnrichedDY, self).__init__(name, selection, objsel, is_reco_level=True, event_categorization = None)
        self.objsel['tau_wp'] = 'FO'
        self.objsel['ele_wp'] = 'tight'
        self.objsel['mu_wp'] = 'tight'

    def initEvent(self, chain, new_chain, cutter):
        return super(TauFakeEnrichedDY, self).initEvent(chain, new_chain, 3, cutter, sort_leptons = False)

    def passedFilter(self, chain, new_chain, cutter):
        if not self.initEvent(chain, new_chain, cutter):                                return False
        # print 'after initEvent', new_chain.l_flavor

        if not cutter.cut(new_chain.l_flavor.count(2) == 1, '1 tau'):                   return False

        # print 'inside', new_chain.l_flavor

        if not cutter.cut(new_chain.l_flavor[0] == new_chain.l_flavor[1], 'SF'):        return False
        if not cutter.cut(new_chain.l_charge[0] != new_chain.l_charge[1], 'OS'):        return False

        l1Vec = getFourVec(new_chain.l_pt[l1], new_chain.l_eta[l1], new_chain.l_phi[l1], new_chain.l_e[l1])
        l2Vec = getFourVec(new_chain.l_pt[l2], new_chain.l_eta[l2], new_chain.l_phi[l2], new_chain.l_e[l2])

        if not cutter.cut(abs(91. - (l1Vec + l2Vec).M()) < 15, 'Z window'):             return False
        if not cutter.cut(chain._met < 50, 'MET < 50'):                                 return False

        if not cutter.cut(chain._tauGenStatus[chain.l_indices[2]] == 6, 'fake tau'):    return False
        return True

#
# General Closure Test Selection class
#
from HNL.ObjectSelection.leptonSelector import isTightLepton, isFakeLepton
class ClosureTestSelection(FilterObject):
    def __init__(self, name, selection, objsel, flavor_of_interest, is_reco_level=True, event_categorization = None):
        super(ClosureTestSelection, self).__init__(name, selection, objsel, is_reco_level=True, event_categorization = None)
        self.flavor_of_interest = flavor_of_interest
        self.loose_leptons_of_interest = []

    def initEvent(self, chain, new_chain, cutter):
        return super(ClosureTestSelection, self).initEvent(chain, new_chain, 3, cutter, sort_leptons = False)

    def hasCorrectNumberOfFakes(self, chain):
        self.loose_leptons_of_interest = []
        is_tight_lep = []
        is_fake_lep = []

        #Make input more readable
        for l in xrange(len(chain.l_pt)):
            #Rule out all other flavors so we are only continuing with general functions on leptons of the correct flavor
            if chain.l_flavor[l] != self.flavor_of_interest: 
                if isFakeLepton(chain, chain.l_indices[l]):
                    return False
                else:
                    continue

            self.loose_leptons_of_interest.append(l)
            if isTightLepton(chain, chain.l_indices[l], algo = self.objsel['light_algo'], tau_algo = self.objsel['tau_algo']): 
                is_tight_lep.append(True)
            else:
                is_tight_lep.append(False)
            
            if isFakeLepton(chain, chain.l_indices[l]): 
                is_fake_lep.append(True)
            else:
                is_fake_lep.append(False)
        
        #If only one lep of interest present in the event, it is required to be fake
        if len(self.loose_leptons_of_interest) == 1:
            return is_fake_lep[0]
        elif len(self.loose_leptons_of_interest) == 2:

            #If both leps are tight...
            if (is_tight_lep[0] and is_tight_lep[1]):
                # At least one of the two has to be a fake
                return is_fake_lep[0] or is_fake_lep[1]
            #Otherwise all loose leps should be fake
            else:
                if not is_tight_lep[0] and not is_fake_lep[0]: return False    
                if not is_tight_lep[1] and not is_fake_lep[1]: return False 
                return True
        elif len(self.loose_leptons_of_interest) == 3:

            #If both leps are tight...
            if (is_tight_lep[0] and is_tight_lep[1] and is_tight_lep[2]):
                # At least one of the two has to be a fake
                return is_fake_lep[0] or is_fake_lep[1] or is_fake_lep[2]
            #Otherwise all loose leps should be fake
            else:
                if not is_tight_lep[0] and not is_fake_lep[0]: return False    
                if not is_tight_lep[1] and not is_fake_lep[1]: return False 
                if not is_tight_lep[2] and not is_fake_lep[2]: return False 
                return True
        else:
            return False


class TauClosureTest(ClosureTestSelection):
    def __init__(self, name, selection, objsel, is_reco_level=True, event_categorization = None):
        super(TauClosureTest, self).__init__(name, selection, objsel, 2, is_reco_level=True, event_categorization = None)
        self.objsel['tau_wp'] = 'FO'
        self.objsel['ele_wp'] = 'tight'
        self.objsel['mu_wp'] = 'tight'

    def initEvent(self, chain, new_chain, cutter):
        return super(TauClosureTest, self).initEvent(chain, new_chain, cutter)

    def passedFilter(self, chain, new_chain, cutter):
        if not self.initEvent(chain, new_chain, cutter):                                            return False
        if not cutter.cut(containsOSSF(chain), 'OSSF present'):                                     return False

        # l1Vec = getFourVec(new_chain.l_pt[l1], new_chain.l_eta[l1], new_chain.l_phi[l1], new_chain.l_e[l1])
        # l2Vec = getFourVec(new_chain.l_pt[l2], new_chain.l_eta[l2], new_chain.l_phi[l2], new_chain.l_e[l2])

        # if not cutter.cut(abs(91. - (l1Vec + l2Vec).M()) < 15, 'Z window'): return False
        if not cutter.cut(chain._met < 50, 'MET>50'): return False

        if not cutter.cut(self.hasCorrectNumberOfFakes(chain), 'correct number of fakes'): return False
        return True   

from HNL.EventSelection.signalRegionSelector import SignalRegionSelector
class ElectronClosureTest(ClosureTestSelection):
    def __init__(self, name, selection, objsel, is_reco_level=True, event_categorization = None):
        super(ElectronClosureTest, self).__init__(name, selection, objsel, 0, is_reco_level=True, event_categorization = None)
        self.objsel['tau_wp'] = 'tight'
        self.objsel['ele_wp'] = 'FO'
        self.objsel['mu_wp'] = 'tight'
        self.signalRegionSelector = SignalRegionSelector('baseline', selection, objsel, is_reco_level=is_reco_level, event_categorization = event_categorization)

    def initEvent(self, chain, new_chain, cutter):
        return super(ElectronClosureTest, self).initEvent(chain, new_chain, cutter)

    def passedFilter(self, chain, new_chain, cutter):
        if not self.initEvent(chain, new_chain, cutter):                                return False
        if chain.l_flavor.count(0) == 0:                                                 return False
        if not cutter.cut(containsOSSF(chain), 'OSSF present'):                                     return False
        # if not self.signalRegionSelector.passBaseCuts(chain, new_chain, cutter):        return False
        if not cutter.cut(self.hasCorrectNumberOfFakes(chain), 'correct number of fakes'): return False
        return True

class MuonClosureTest(ClosureTestSelection):
    def __init__(self, name, selection, objsel, is_reco_level=True, event_categorization = None):
        super(MuonClosureTest, self).__init__(name, selection, objsel, 1, is_reco_level=True, event_categorization = None)
        self.objsel['tau_wp'] = 'tight'
        self.objsel['ele_wp'] = 'tight'
        self.objsel['mu_wp'] = 'FO'
        # self.signalRegionSelector = SignalRegionSelector('baseline', selection, objsel, is_reco_level=is_reco_level, event_categorization = event_categorization)

    def initEvent(self, chain, new_chain, cutter):
        # return super(ClosureTestSelection, self).initEvent(chain, new_chain, 2, cutter, sort_leptons = False)
        return super(MuonClosureTest, self).initEvent(chain, new_chain, cutter)

    def passedFilter(self, chain, new_chain, cutter):
        if not self.initEvent(chain, new_chain, cutter):                                return False
        if chain.l_flavor.count(1) == 0:                                                 return False
        if not cutter.cut(containsOSSF(chain), 'OSSF present'):                                     return False
        # if not self.signalRegionSelector.passBaseCuts(chain, new_chain, cutter):        return False
        if not cutter.cut(self.hasCorrectNumberOfFakes(chain), 'correct number of fakes'): return False


        # #
        # #   Experimental mode 
        # #
        # if chain.l_charge[0] != chain.l_charge[1]: return False

        # self.loose_leptons_of_interest = []
        # is_tight_lep = []
        # is_fake_lep = []

        # #Make input more readable
        # for l in xrange(len(chain.l_pt)):
        #     #Rule out all other flavors so we are only continuing with general functions on leptons of the correct flavor

        #     self.loose_leptons_of_interest.append(l)
        #     if isTightLepton(chain, chain.l_indices[l], algo = self.objsel['light_algo'], tau_algo = self.objsel['tau_algo']): 
        #         is_tight_lep.append(True)
        #     else:
        #         is_tight_lep.append(False)
            
        #     if isFakeLepton(chain, chain.l_indices[l]): 
        #         is_fake_lep.append(True)
        #     else:
        #         is_fake_lep.append(False) 
            

        # print is_fake_lep, [t for t in is_fake_lep if t]
        # if len([t for t in is_fake_lep if t]) < 1: return False

        return True
