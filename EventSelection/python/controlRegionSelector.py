from HNL.EventSelection.eventSelectionTools import *
import HNL.EventSelection.eventCategorization as cat
from HNL.ObjectSelection.leptonSelector import *
from HNL.Tools.helpers import getFourVec, deltaPhi, deltaR

class FilterObject(object):

    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None):
        self.name = name
        self.chain = chain
        self.new_chain = new_chain
        self.is_reco_level = is_reco_level
        self.ec = event_categorization

    def initEvent(self, nL, cutter, sort_leptons):
        if self.is_reco_level:
            if not cutter.cut(selectLeptonsGeneral(self.chain, self.new_chain, nL, cutter=cutter, sort_leptons = sort_leptons), 'select leptons'): return False
        else:
            if not cutter.cut(selectGenLeptonsGeneral(self.chain, self.new_chain, nL, cutter=cutter), 'select leptons'): return False
        calculateEventVariables(self.chain, self.new_chain, nL, is_reco_level=self.is_reco_level)
        self.chain.category = max(cat.CATEGORIES)
        return True

class ZZCRfilter(FilterObject):
    
    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None):
        super(ZZCRfilter, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)

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

    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None):
        super(WZCRfilter, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)

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

    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None):
        super(ConversionCRfilter, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)

    def initEvent(self, cutter):
        return super(ConversionCRfilter, self).initEvent(3, cutter, sort_leptons = True)

    def passedFilter(self, cutter):
        if not self.initEvent(cutter):                                                 return False
        if not cutter.cut(containsOSSF(self.chain), 'OSSF present'):         return False
        if not cutter.cut(abs(self.new_chain.M3l-MZ) < 15, 'M3l_onZ'):       return False 
        if not cutter.cut(self.chain.MZossf < 75, 'Mll < 75'):               return False
        if self.chain.selection == 'AN2017014' and not cutter.cut(passesPtCutsAN2017014(self.chain), 'pt_cuts'):     return False 
        if not cutter.cut(not bVeto(self.chain), 'b-veto'):                 return False
        self.chain.category = max(cat.CATEGORIES)
        return True

class TauFakeEnrichedDY(FilterObject):
    
    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None):
        super(TauFakeEnrichedDY, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)

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
    
    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None):
        super(TauFakeEnrichedTT, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)

    def initEvent(self, cutter):
        self.chain.obj_sel['tau_wp'] = 'FO'
        self.chain.obj_sel['ele_wp'] = 'tight'
        self.chain.obj_sel['mu_wp'] = 'tight'
        return super(TauFakeEnrichedTT, self).initEvent(3, cutter, sort_leptons = False)

    def passedFilter(self, cutter):
        if not self.initEvent(cutter):                                return False

        if not cutter.cut(self.new_chain.l_flavor.count(0) == 1, '1 e'):                   return False
        if not cutter.cut(self.new_chain.l_flavor.count(1) == 1, '1 mu'):                  return False
        if not cutter.cut(self.new_chain.l_flavor.count(2) == 1, '1 tau'):                 return False
        if not cutter.cut(self.new_chain.l_charge[0] != self.new_chain.l_charge[1], 'OS'):        return False

        if nBjets(self.chain, 'tight') < 1:      return False

        l1Vec = getFourVec(self.new_chain.l_pt[0], self.new_chain.l_eta[0], self.new_chain.l_phi[0], self.new_chain.l_e[0])
        l2Vec = getFourVec(self.new_chain.l_pt[1], self.new_chain.l_eta[1], self.new_chain.l_phi[1], self.new_chain.l_e[1])

        if not cutter.cut((l1Vec + l2Vec).M() > 20, 'Mll cut'):             return False

        if not cutter.cut(self.chain._met < 50, 'MET < 50'):                                 return False

        # if not cutter.cut(self.chain._tauGenStatus[self.chain.l_indices[2]] == 6, 'fake tau'):    return False
        return True

    def getFakeIndex(self):
        return 2

from HNL.ObjectSelection.leptonSelector import isGoodLepton, isFakeLepton
from HNL.EventSelection.eventSelectionTools import selectJets
#Orthogonal due to selection of exactly 1 lepton
class LightLeptonFakeMeasurementRegion(FilterObject):
    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None):
        super(LightLeptonFakeMeasurementRegion, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)

    def initEvent(self, cutter):
        self.chain.obj_sel['ele_wp'] = 'loose'
        self.chain.obj_sel['mu_wp'] = 'loose'
        self.chain.obj_sel['notau'] = True
        return super(LightLeptonFakeMeasurementRegion, self).initEvent(1, cutter, sort_leptons = False)

    def passedFilter(self, cutter, only_muons = False, only_electrons = False, require_jets = False):
        if not cutter.cut(self.chain._passMETFilters, 'pass met filters'): return False

        #Select exactly one lepton and veto a second loose lepton
        if not self.initEvent(cutter):                                return False
        if not cutter.cut(isGoodLightLepton(self.chain, self.chain.l_indices[0], 'FO'), 'is FO lepton'): return False

        #Select correct lepton flavor
        if only_muons and only_electrons:
            raise RuntimeError("passedFilter in LightLeptonFakeRateMeasurementRegion can not have both only muons and only electrons at the same time")
        if only_muons and not cutter.cut(self.chain.l_flavor[0] == 1, 'is muon'): return False
        if only_electrons and not cutter.cut(self.chain.l_flavor[0] == 0, 'is electron'): return False

        #Require the presence of at least one good jet if option is set to True
        if require_jets:
            jet_indices = selectJets(self.chain, cleaned='loose')
            if len(jet_indices) < 1:      return False
            
            max_delta_r = 0
            for jet in jet_indices:
                delta_r = deltaR(self.chain._jetEta[jet], self.chain.l_eta[0], self.chain._jetPhi[jet], self.chain.l_phi[0])
                if delta_r > max_delta_r:
                    max_delta_r = delta_r
            if not cutter.cut(max_delta_r > 0.7, 'contains jet'): return False

        applyConeCorrection(self.chain, self.new_chain)

        return True

    def getFakeIndex(self):
        return 0

#
# General Closure Test Selection class
#
class ClosureTestSelection(FilterObject):
    def __init__(self, name, chain, new_chain, flavor_of_interest, is_reco_level=True, event_categorization = None):
        super(ClosureTestSelection, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
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
    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None):
        super(TauClosureTest, self).__init__(name, chain, new_chain, 2, is_reco_level=is_reco_level, event_categorization = event_categorization)
        self.chain.obj_sel['tau_wp'] = 'FO'
        self.chain.obj_sel['ele_wp'] = 'tight'
        self.chain.obj_sel['mu_wp'] = 'tight'

    def initEvent(self, cutter):
        return super(TauClosureTest, self).initEvent(cutter)

    def passedFilter(self, cutter):
        if not self.initEvent(cutter):                                            return False
        # if not cutter.cut(containsOSSF(self.chain), 'OSSF present'):                                     return False

        # l1Vec = getFourVec(new_chain.l_pt[l1], new_chain.l_eta[l1], new_chain.l_phi[l1], new_chain.l_e[l1])
        # l2Vec = getFourVec(new_chain.l_pt[l2], new_chain.l_eta[l2], new_chain.l_phi[l2], new_chain.l_e[l2])

        # if not cutter.cut(abs(91. - (l1Vec + l2Vec).M()) < 15, 'Z window'): return False
        if not cutter.cut(self.chain._met < 50, 'MET>50'): return False
        # if not cutter.cut(not bVeto(self.chain), 'b-veto'): return False

        if not cutter.cut(self.hasCorrectNumberOfFakes(), 'correct number of fakes'): return False

        return True   

from HNL.EventSelection.signalRegionSelector import SignalRegionSelector
from HNL.EventSelection.eventSelectionTools import applyConeCorrection
class ElectronClosureTest(ClosureTestSelection):
    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None):
        super(ElectronClosureTest, self).__init__(name, chain, new_chain, 0, is_reco_level=is_reco_level, event_categorization = event_categorization)
        self.chain.obj_sel['tau_wp'] = 'tight'
        self.chain.obj_sel['ele_wp'] = 'FO'
        self.chain.obj_sel['mu_wp'] = 'tight'

    def initEvent(self, cutter):
        return super(ElectronClosureTest, self).initEvent(cutter)

    def passedFilter(self, cutter):
        if not self.initEvent(cutter):                                return False
        applyConeCorrection(self.chain, self.new_chain)
        if self.new_chain.l_flavor.count(0) == 0:                                                 return False
        if not cutter.cut(self.hasCorrectNumberOfFakes(), 'correct number of fakes'): return False
        return True

class MuonClosureTest(ClosureTestSelection):
    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None):
        super(MuonClosureTest, self).__init__(name, chain, new_chain, 1, is_reco_level=is_reco_level, event_categorization = event_categorization)
        self.chain.obj_sel['tau_wp'] = 'tight'
        self.chain.obj_sel['ele_wp'] = 'tight'
        self.chain.obj_sel['mu_wp'] = 'FO'

    def initEvent(self, cutter):
        return super(MuonClosureTest, self).initEvent(cutter)

    def passedFilter(self, cutter):
        if not self.initEvent(cutter):                                return False
        applyConeCorrection(self.chain, self.new_chain) 
        if self.new_chain.l_flavor.count(1) == 0:                                                 return False
        if not cutter.cut(self.hasCorrectNumberOfFakes(), 'correct number of fakes'): return False
        return True

class LukaClosureTest(FilterObject):
    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None):
        super(LukaClosureTest, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)

    def initEvent(self, cutter):
        self.chain.obj_sel['ele_wp'] = 'FO'
        self.chain.obj_sel['mu_wp'] = 'FO'
        self.chain.obj_sel['notau'] = True
        return super(LukaClosureTest, self).initEvent(3, cutter, sort_leptons = True)
    
    def passedFilter(self, cutter, only_muons = False, only_electrons = False):
        if not self.initEvent(cutter):                                return False
        applyConeCorrection(self.chain, self.new_chain)

        nprompt = 0
        nnonprompt = 0
        for i, l in enumerate(self.new_chain.l_indices):
            if self.chain.l_isfake[i]:  
                if only_muons and self.new_chain.l_flavor[i] != 1: return False
                if only_electrons and self.new_chain.l_flavor[i] != 0: return False
                nnonprompt += 1
            else:                       nprompt += 1
        
        if nnonprompt < 1: return False
        if nprompt + nnonprompt != 3: return False

        self.loose_leptons_of_interest = []
        for l in xrange(len(self.new_chain.l_indices)):
            if self.new_chain.l_isFO[l] and not self.new_chain.l_istight[l]: self.loose_leptons_of_interest.append(l)
        return True

class ClosureTestMC(FilterObject):
    flavor_dict = {'tau' : 2, 'ele' : 0, 'mu' : 1}

    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None, additional_options=None):
        super(ClosureTestMC, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        self.flavors_of_interest = additional_options
        if self.flavors_of_interest is None: 
            raise RuntimeError('Input for ClosureTestMC for flavors_of_interest is None')
    
        # Set Object Selection
        self.chain.obj_sel['tau_wp'] = 'FO' if 'tau' in self.flavors_of_interest else 'tight'
        self.chain.obj_sel['ele_wp'] = 'FO' if 'ele' in self.flavors_of_interest else 'tight'
        self.chain.obj_sel['mu_wp'] = 'FO' if 'mu' in self.flavors_of_interest else 'tight'
        # if self.flavors_of_interest == ['ele']:
        #     self.chain.obj_sel['notau'] = True

        self.loose_leptons_of_interest = []

    def initEvent(self, cutter):
        return super(ClosureTestMC, self).initEvent(3, cutter, sort_leptons = False)

    def hasCorrectNumberOfFakes(self):
        self.loose_leptons_of_interest = []
        is_tight_lep = []
        is_fake_lep = []
        translated_flavors_of_interest = [self.flavor_dict[i] for i in self.flavors_of_interest]
        # print translated_flavors_of_interest

        #Make input more readable
        for l in xrange(len(self.new_chain.l_pt)):
            #Rule out all other flavors so we are only continuing with general functions on leptons of the correct flavor
            if not self.new_chain.l_flavor[l] in translated_flavors_of_interest: 
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
        
        #If not lepton with flavor of interest, return False
        if len(self.loose_leptons_of_interest) == 0:
            return False
        #If only one lep of interest present in the event, it is required to be fake
        elif len(self.loose_leptons_of_interest) == 1:
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

    def passedFilter(self, cutter):
        if not self.initEvent(cutter):                                return False
        applyConeCorrection(self.chain, self.new_chain)
        if not cutter.cut(self.hasCorrectNumberOfFakes(), 'correct number of fakes'): return False
        # if not cutter.cut(self.chain._passMETFilters, 'pass met filters'): return False
        if 'tau' in self.flavors_of_interest:
            if not cutter.cut(self.chain._met < 50, 'MET>50'): return False
            if not cutter.cut(containsOSSF(self.chain), 'OSSF present'): return False
            if not cutter.cut(not bVeto(self.chain), 'b-veto'): return False
        return True

class ClosureTestDATA(FilterObject):
    flavor_dict = {'tau' : 2, 'ele' : 0, 'mu' : 1}

    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None, additional_options=None):
        super(ClosureTestDATA, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        self.flavors_of_interest = additional_options
        if self.flavors_of_interest is None: 
            raise RuntimeError('Input for ClosureTestDATA for flavors_of_interest is None')
    
        # Set Object Selection
        self.chain.obj_sel['tau_wp'] = 'FO' if 'tau' in self.flavors_of_interest else 'tight'
        self.chain.obj_sel['ele_wp'] = 'FO' if 'ele' in self.flavors_of_interest else 'tight'
        self.chain.obj_sel['mu_wp'] = 'FO' if 'mu' in self.flavors_of_interest else 'tight'

        self.loose_leptons_of_interest = []

    def initEvent(self, cutter):
        return super(ClosureTestDATA, self).initEvent(3, cutter, sort_leptons = False)

    def passedFilter(self, cutter, region):
        if self.flavors_of_interest == ['tau'] and region == 'TauFakesDY':
            if not self.initEvent(cutter):                                return False
        
            if not cutter.cut(self.new_chain.l_flavor.count(2) == 1, '1 tau'):                   return False

            if not cutter.cut(self.new_chain.l_flavor[0] == self.new_chain.l_flavor[1], 'SF'):        return False
            if not cutter.cut(self.new_chain.l_charge[0] != self.new_chain.l_charge[1], 'OS'):        return False

            l1Vec = getFourVec(self.new_chain.l_pt[0], self.new_chain.l_eta[0], self.new_chain.l_phi[0], self.new_chain.l_e[0])
            l2Vec = getFourVec(self.new_chain.l_pt[1], self.new_chain.l_eta[1], self.new_chain.l_phi[1], self.new_chain.l_e[1])

            if not cutter.cut(abs(91.19 - (l1Vec + l2Vec).M()) < 15, 'Z window'):             return False
            if not cutter.cut(self.chain._met < 50, 'MET > 50'):                                 return False
            if not cutter.cut(not bVeto(self.chain), 'b-veto'):                             return False

            self.loose_leptons_of_interest = [2]
            return True
        
        else:
            return False

    def getFakeIndex(self):
        return 2
