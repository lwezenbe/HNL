from HNL.EventSelection.eventSelectionTools import *
import HNL.EventSelection.eventCategorization as cat
from HNL.ObjectSelection.leptonSelector import *
from HNL.Tools.helpers import getFourVec, deltaPhi, deltaR

class FilterObject(object):

    def __init__(self, name, chain, new_chain, selection, is_reco_level=True, event_categorization = None):
        self.name = name
        self.chain = chain
        self.new_chain = new_chain
        self.selection = selection
        self.is_reco_level = is_reco_level
        self.ec = event_categorization

    def initEvent(self, nL, cutter, sort_leptons):
        if self.is_reco_level:
            if not cutter.cut(selectLeptonsGeneral(self.chain, self.new_chain, nL, cutter=cutter, sort_leptons = sort_leptons), 'select leptons'): return False
        else:
            if not cutter.cut(selectGenLeptonsGeneral(self.chain, self.new_chain, nL, cutter=cutter), 'select leptons'): return False
        calculateEventVariables(self.chain, self.new_chain, nL, is_reco_level=self.is_reco_level, selection=self.selection)
        self.chain.category = max(cat.CATEGORIES)
        return True

class ZZCRfilter(FilterObject):
    
    def __init__(self, name, chain, new_chain, selection, is_reco_level=True, event_categorization = None):
        super(ZZCRfilter, self).__init__(name, chain, new_chain, selection, is_reco_level=True, event_categorization = None)

    def initEvent(self, cutter):
        return super(ZZCRfilter, self).initEvent(4, cutter, sort_leptons = True)

    def passedFilter(self, cutter):
        if not self.initEvent(cutter):                                                 return False
        if not cutter.cut(not bVeto(self.chain), 'b-veto'):                 return False

        #Relaxed
        if not cutter.cut(massDiff(self.chain.Mll_Z1, MZ) < 15, 'First Z ok'):                                                           return False
        if not cutter.cut(self.new_chain.minMos > 12, 'min Mos > 12'):                                                                       return False

        return True

class WZCRfilter(FilterObject):

    def __init__(self, name, chain, new_chain, selection, is_reco_level=True, event_categorization = None):
        super(WZCRfilter, self).__init__(name, chain, new_chain, selection, is_reco_level=True, event_categorization = None)

    def initEvent(self, cutter):
        return super(WZCRfilter, self).initEvent(3, cutter, sort_leptons = True)

    def passedFilter(self, cutter):
        if not self.initEvent(cutter):                                                 return False
        if not cutter.cut(not passesZcuts(self.chain, self.new_chain, same_flavor=True), 'On Z OSSF'):              return False
        if not cutter.cut(self.new_chain.l_pt[l1] > 25, 'l1pt>25'):          return False
        if not cutter.cut(self.new_chain.l_pt[l2] > 15, 'l2pt>15'):          return False
        if not cutter.cut(self.new_chain.l_pt[l3] > 10, 'l3pt>10'):          return False
        if self.is_reco_level:
            if not cutter.cut(self.chain._met > 50, 'MET > 50'):             return False
        else:
            if not cutter.cut(self.chain._gen_met > 50, 'MET > 50'):         return False
        if not cutter.cut(abs(self.new_chain.M3l-MZ) > 15, 'M3l_Z_veto'):    return False 
        return True

class ConversionCRfilter(FilterObject):

    def __init__(self, name, chain, new_chain, selection, is_reco_level=True, event_categorization = None):
        super(ConversionCRfilter, self).__init__(name, chain, new_chain, selection, is_reco_level=True, event_categorization = None)

    def initEvent(self, cutter):
        return super(ConversionCRfilter, self).initEvent(3, cutter, sort_leptons = True)

    def passedFilter(self, cutter):
        if not self.initEvent(cutter):                                                 return False
        if not cutter.cut(containsOSSF(self.chain), 'OSSF present'):         return False
        if not cutter.cut(abs(self.new_chain.M3l-MZ) < 15, 'M3l_onZ'):       return False 
        if not cutter.cut(self.chain.MZossf < 75, 'Mll < 75'):               return False
        if self.selection == 'AN2017014' and not cutter.cut(passesPtCutsAN2017014(chain), 'pt_cuts'):     return False 
        if not cutter.cut(not bVeto(self.chain), 'b-veto'):                 return False
        self.chain.category = max(cat.CATEGORIES)
        return True

class TauFakeEnrichedDY(FilterObject):
    
    def __init__(self, name, chain, new_chain, selection, is_reco_level=True, event_categorization = None):
        super(TauFakeEnrichedDY, self).__init__(name, chain, new_chain, selection, is_reco_level=True, event_categorization = None)

    def initEvent(self, cutter):
        self.chain.obj_sel['tau_wp'] = 'FO'
        self.chain.obj_sel['ele_wp'] = 'tight'
        self.chain.obj_sel['mu_wp'] = 'tight'
        return super(TauFakeEnrichedDY, self).initEvent(3, cutter, sort_leptons = False)

    def passedFilter(self, cutter):
        if not self.initEvent(cutter):                                return False
    
        if not cutter.cut(self.new_chain.l_flavor.count(2) == 1, '1 tau'):                   return False

        if not cutter.cut(self.new_chain.l_flavor[0] == self.new_chain.l_flavor[1], 'SF'):        return False
        if not cutter.cut(self.new_chain.l_charge[0] != self.new_chain.l_charge[1], 'OS'):        return False

        l1Vec = getFourVec(self.new_chain.l_pt[0], self.new_chain.l_eta[0], self.new_chain.l_phi[0], self.new_chain.l_e[0])
        l2Vec = getFourVec(self.new_chain.l_pt[1], self.new_chain.l_eta[1], self.new_chain.l_phi[1], self.new_chain.l_e[1])

        if not cutter.cut(abs(91.19 - (l1Vec + l2Vec).M()) < 15, 'Z window'):             return False
        if not cutter.cut(self.chain._met < 50, 'MET < 50'):                                 return False

        # if not cutter.cut(self.chain._tauGenStatus[self.chain.l_indices[2]] == 6, 'fake tau'):    return False
        return True

    def getFakeIndex(self):
        return 2

class TauFakeEnrichedTT(FilterObject):
    
    def __init__(self, name, chain, new_chain, selection, is_reco_level=True, event_categorization = None):
        super(TauFakeEnrichedTT, self).__init__(name, chain, new_chain, selection, is_reco_level=True, event_categorization = None)

    def initEvent(self, cutter):
        self.chain.obj_sel['tau_wp'] = 'FO'
        self.chain.obj_sel['ele_wp'] = 'tight'
        self.chain.obj_sel['mu_wp'] = 'tight'
        return super(TauFakeEnrichedTT, self).initEvent(3, cutter, sort_leptons = False)

    def passedFilter(self, cutter):
        if not self.initEvent(cutter):                                return False

        # print 'start'
        if not cutter.cut(self.new_chain.l_flavor.count(0) == 1, '1 e'):                   return False
        # print '1e'
        if not cutter.cut(self.new_chain.l_flavor.count(1) == 1, '1 mu'):                  return False
        # print '1mu'
        if not cutter.cut(self.new_chain.l_flavor.count(2) == 1, '1 tau'):                 return False
        # print '1tau'
        if not cutter.cut(self.new_chain.l_charge[0] != self.new_chain.l_charge[1], 'OS'):        return False

        # print 'os'
        # print self.selection
        if nBjets(self.chain, 'tight') < 1:      return False

        # print 'bjets'
        l1Vec = getFourVec(self.new_chain.l_pt[0], self.new_chain.l_eta[0], self.new_chain.l_phi[0], self.new_chain.l_e[0])
        l2Vec = getFourVec(self.new_chain.l_pt[1], self.new_chain.l_eta[1], self.new_chain.l_phi[1], self.new_chain.l_e[1])

        if not cutter.cut((l1Vec + l2Vec).M() > 20, 'Mll cut'):             return False
        # print 'mll'

        if not cutter.cut(self.chain._met < 50, 'MET < 50'):                                 return False
        # print 'met'

        # if not cutter.cut(self.chain._tauGenStatus[self.chain.l_indices[2]] == 6, 'fake tau'):    return False
        return True

    def getFakeIndex(self):
        return 2

from HNL.ObjectSelection.leptonSelector import isGoodLepton, isFakeLepton
from HNL.EventSelection.eventSelectionTools import selectJets
class LightLeptonFakeMeasurementRegion(FilterObject):
    def __init__(self, name, chain, new_chain, selection, is_reco_level=True, event_categorization = None):
        super(LightLeptonFakeMeasurementRegion, self).__init__(name, chain, new_chain, selection, is_reco_level=True, event_categorization = None)

    def initEvent(self, cutter):
        self.chain.obj_sel['ele_wp'] = 'loose'
        self.chain.obj_sel['mu_wp'] = 'loose'
        self.chain.obj_sel['notau'] = True
        return super(LightLeptonFakeMeasurementRegion, self).initEvent(1, cutter, sort_leptons = False)

    def passedFilter(self, cutter, only_muons = False, only_electrons = False, require_jets = False):
        if not cutter.cut(self.chain._passMETFilters, 'pass met filters'): return False
        # print 'pass met filters'

        #Select exactly one lepton and veto a second loose lepton
        if not self.initEvent(cutter):                                return False
        # print 'init event'
        if not cutter.cut(isGoodLightLepton(self.chain, self.chain.l_indices[0], 'FO'), 'is FO lepton'): return False
        # print 'is FO lepton'

        #Select correct lepton flavor
        if only_muons and only_electrons:
            raise RuntimeError("passedFilter in LightLeptonFakeRateMeasurementRegion can not have both only muons and only electrons at the same time")
        if only_muons and not cutter.cut(self.chain.l_flavor[0] == 1, 'is muon'): return False
        # print 'passed muon', only_muons
        if only_electrons and not cutter.cut(self.chain.l_flavor[0] == 0, 'is electron'): return False
        # print 'passed electron', only_electrons

        #Require the presence of at least one good jet if option is set to True
        if require_jets:
            jet_indices = selectJets(self.chain, cleaned=True, selection='lightlepfakes')
            if len(jet_indices) < 1:      return False
            
            max_delta_r = 0
            for jet in jet_indices:
                delta_r = deltaR(self.chain._jetEta[jet], self.chain.l_eta[0], self.chain._jetPhi[jet], self.chain.l_phi[0])
                if delta_r > max_delta_r:
                    max_delta_r = delta_r
            if not cutter.cut(max_delta_r > 0.7, 'contains jet'): return False
        # print 'has jet'

        applyConeCorrection(self.chain, self.new_chain)

        return True

    def getFakeIndex(self):
        return 0

#
# General Closure Test Selection class
#
class ClosureTestSelection(FilterObject):
    def __init__(self, name, chain, new_chain, selection, flavor_of_interest, is_reco_level=True, event_categorization = None):
        super(ClosureTestSelection, self).__init__(name, chain, new_chain, selection, is_reco_level=True, event_categorization = None)
        self.flavor_of_interest = flavor_of_interest
        self.loose_leptons_of_interest = []

    def initEvent(self, cutter):
        return super(ClosureTestSelection, self).initEvent(3, cutter, sort_leptons = False)

    def hasCorrectNumberOfFakes(self):
        self.loose_leptons_of_interest = []
        is_tight_lep = []
        is_fake_lep = []

        #Make input more readable
        for l in xrange(len(self.new_chain.l_pt)):
            #Rule out all other flavors so we are only continuing with general functions on leptons of the correct flavor
            if self.new_chain.l_flavor[l] != self.flavor_of_interest: 
                if isFakeLepton(self.chain, self.new_chain.l_indices[l]):
                    return False
                else:
                    continue

            self.loose_leptons_of_interest.append(l)
            if isGoodLepton(self.chain, self.new_chain.l_indices[l], 'tight'): 
                is_tight_lep.append(True)
            else:
                is_tight_lep.append(False)
            
            if isFakeLepton(self.chain, self.new_chain.l_indices[l]): 
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
    def __init__(self, name, chain, new_chain, selection, is_reco_level=True, event_categorization = None):
        super(TauClosureTest, self).__init__(name, chain, new_chain, selection, 2, is_reco_level=True, event_categorization = None)
        self.chain.obj_sel['tau_wp'] = 'FO'
        self.chain.obj_sel['ele_wp'] = 'tight'
        self.chain.obj_sel['mu_wp'] = 'tight'

    def initEvent(self, cutter):
        return super(TauClosureTest, self).initEvent(cutter)

    def passedFilter(self, cutter):
        if not self.initEvent(cutter):                                            return False
        if not cutter.cut(containsOSSF(self.chain), 'OSSF present'):                                     return False

        # l1Vec = getFourVec(new_chain.l_pt[l1], new_chain.l_eta[l1], new_chain.l_phi[l1], new_chain.l_e[l1])
        # l2Vec = getFourVec(new_chain.l_pt[l2], new_chain.l_eta[l2], new_chain.l_phi[l2], new_chain.l_e[l2])

        # if not cutter.cut(abs(91. - (l1Vec + l2Vec).M()) < 15, 'Z window'): return False
        if not cutter.cut(self.chain._met < 50, 'MET>50'): return False
        if not cutter.cut(not bVeto(self.chain), 'b-veto'): return False

        if not cutter.cut(self.hasCorrectNumberOfFakes(), 'correct number of fakes'): return False

        return True   

from HNL.EventSelection.signalRegionSelector import SignalRegionSelector
from HNL.EventSelection.eventSelectionTools import applyConeCorrection
class ElectronClosureTest(ClosureTestSelection):
    def __init__(self, name, chain, new_chain, selection, is_reco_level=True, event_categorization = None):
        super(ElectronClosureTest, self).__init__(name, chain, new_chain, selection, 0, is_reco_level=True, event_categorization = None)
        self.chain.obj_sel['tau_wp'] = 'tight'
        self.chain.obj_sel['ele_wp'] = 'FO'
        self.chain.obj_sel['mu_wp'] = 'tight'
        # self.signalRegionSelector = SignalRegionSelector('baseline', selection, is_reco_level=is_reco_level, event_categorization = event_categorization)

    def initEvent(self, cutter):
        return super(ElectronClosureTest, self).initEvent(cutter)

    def passedFilter(self, cutter):
        if not self.initEvent(cutter):                                return False
        applyConeCorrection(self.chain, self.new_chain)
        if self.new_chain.l_flavor.count(0) == 0:                                                 return False
        if not cutter.cut(containsOSSF(self.chain), 'OSSF present'):                                     return False
        # if not self.signalRegionSelector.passBaseCuts(chain, new_chain, cutter):        return False
        if not cutter.cut(self.hasCorrectNumberOfFakes(), 'correct number of fakes'): return False
        return True

class MuonClosureTest(ClosureTestSelection):
    def __init__(self, name, chain, new_chain, selection, is_reco_level=True, event_categorization = None):
        super(MuonClosureTest, self).__init__(name, chain, new_chain, selection, 1, is_reco_level=True, event_categorization = None)
        self.chain.obj_sel['tau_wp'] = 'tight'
        self.chain.obj_sel['ele_wp'] = 'tight'
        self.chain.obj_sel['mu_wp'] = 'FO'
        # self.signalRegionSelector = SignalRegionSelector('baseline', selection, is_reco_level=is_reco_level, event_categorization = event_categorization)

    def initEvent(self, cutter):
        # return super(ClosureTestSelection, self).initEvent(2, cutter, sort_leptons = False)
        return super(MuonClosureTest, self).initEvent(cutter)

    def passedFilter(self, cutter):
        if not self.initEvent(cutter):                                return False
        applyConeCorrection(self.chain, self.new_chain) 
        if self.new_chain.l_flavor.count(1) == 0:                                                 return False
        # if not cutter.cut(containsOSSF(self.chain), 'OSSF present'):                                     return False
        # if not self.signalRegionSelector.passBaseCuts(chain, new_chain, cutter):        return False
        if not cutter.cut(self.hasCorrectNumberOfFakes(), 'correct number of fakes'): return False


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
        #     if isTightLepton(chain.l_indices[l], algo = self.chain.obj_sel['light_algo'], tau_algo = self.chain.obj_sel['tau_algo']): 
        #         is_tight_lep.append(True)
        #     else:
        #         is_tight_lep.append(False)
            
        #     if isFakeLepton(chain.l_indices[l]): 
        #         is_fake_lep.append(True)
        #     else:
        #         is_fake_lep.append(False) 
            

        # print is_fake_lep, [t for t in is_fake_lep if t]
        # if len([t for t in is_fake_lep if t]) < 1: return False
        return True


