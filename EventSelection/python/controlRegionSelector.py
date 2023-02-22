from HNL.EventSelection.eventSelectionTools import selectLeptonsGeneral, selectGenLeptonsGeneral, calculateEventVariables
from HNL.EventSelection.eventSelectionTools import bVeto, massDiff, passesZcuts, containsOSSF, fourthFOVeto, threeSameSignVeto, nBjets
from HNL.EventSelection.eventSelectionTools import l1, l2, l3, l4, MZ
from HNL.ObjectSelection.leptonSelector import isGoodLightLepton
from HNL.Tools.helpers import getFourVec, deltaPhi, deltaR
from HNL.EventSelection.eventSelectionTools import applyConeCorrection
from HNL.EventSelection.signalRegionSelector import SignalRegionSelector

from HNL.EventSelection.eventSelector import FilterObject

class GeneralTrileptonFilter(FilterObject):
    
    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None):
        super(GeneralTrileptonFilter, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)

    def initEvent(self, cutter, kwargs={}):
        return super(GeneralTrileptonFilter, self).initEvent(3, cutter, sort_leptons = True, kwargs=kwargs)

    def passedFilter(self, cutter, kwargs):
        if not self.initEvent(cutter, kwargs=kwargs):           return False
        return True

class HighMassWithBJetfilter(FilterObject):
    
    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None):
        super(HighMassWithBJetfilter, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)

    def initEvent(self, cutter, kwargs={}):
        return super(HighMassWithBJetfilter, self).initEvent(3, cutter, sort_leptons = True, kwargs=kwargs)

    def passedFilter(self, cutter, kwargs={}):
        from HNL.EventSelection.eventFilters import passedFilterHighMassWithBjet
        if not self.initEvent(cutter, kwargs=kwargs):           return False
        if not passedFilterHighMassWithBjet(self.chain, self.new_chain, cutter):                    return False
        return True

class ZZCRfilter(FilterObject):
    
    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None):
        super(ZZCRfilter, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)

    def initEvent(self, cutter, kwargs={}):
        return super(ZZCRfilter, self).initEvent(4, cutter, sort_leptons = True, kwargs=kwargs)

    def passedFilter(self, cutter, kwargs={}):
        from HNL.EventSelection.eventFilters import passedFilterZZCR
        if not self.initEvent(cutter, kwargs=kwargs):           return False
        if not passedFilterZZCR(self.chain, self.new_chain, cutter):                    return False
        return True

class WZCRfilter(FilterObject):

    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None):
        super(WZCRfilter, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)

    def initEvent(self, cutter, kwargs={}):
        return super(WZCRfilter, self).initEvent(3, cutter, sort_leptons = True, kwargs=kwargs)

    def passedFilter(self, cutter, kwargs={}):
        from HNL.EventSelection.eventFilters import passedFilterWZCR, passedFilterWZCRewkino
        if not self.initEvent(cutter, kwargs=kwargs):                                                 return False
        if self.chain.analysis != 'ewkino':
            if not passedFilterWZCR(self.chain, self.new_chain, cutter = cutter):                    return False
        else:
            if not passedFilterWZCRewkino(self.chain, self.new_chain, cutter = cutter):                    return False
        return True

class ConversionCRfilter(FilterObject):

    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None):
        super(ConversionCRfilter, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)

    def initEvent(self, cutter, kwargs={}):
        return super(ConversionCRfilter, self).initEvent(3, cutter, sort_leptons = True, kwargs=kwargs)

    def passedFilter(self, cutter, kwargs={}):
        from HNL.EventSelection.eventFilters import passedFilterConversionCR, passedFilterConversionCRtZq
        if not self.initEvent(cutter, kwargs):                                                 return False
        if self.chain.analysis != 'tZq':
            if not passedFilterConversionCR(self.chain, self.new_chain, cutter = cutter):                    return False
        else:
            if not passedFilterConversionCRtZq(self.chain, self.new_chain, cutter = cutter):                    return False
        return True       

class TauFakeEnrichedDY(FilterObject):
    
    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None, additional_args = None):
        super(TauFakeEnrichedDY, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        self.use_default_objects = additional_args.get('tightWP', False) if additional_args is not None else False
        self.nometcut = additional_args.get('nometcut', False) if additional_args is not None else False
        self.inverted_met_cut = additional_args.get('inverted_met_cut', False) if additional_args is not None else False
        self.b_veto = additional_args.get('b_veto', False) if additional_args is not None else False
        if not self.use_default_objects:
            self.chain.obj_sel['tau_wp'] = 'FO'
            self.chain.obj_sel['ele_wp'] = 'tight'
            self.chain.obj_sel['mu_wp'] = 'tight'

    def initEvent(self, cutter, kwargs={}):
        if not self.use_default_objects:        kwargs['sideband'] = None
        return super(TauFakeEnrichedDY, self).initEvent(3, cutter, sort_leptons = False, kwargs=kwargs)

    def passedFilter(self, cutter, kwargs={}):
        if not self.initEvent(cutter, kwargs):                                return False
        from HNL.EventSelection.eventFilters import passedFilterTauFakeEnrichedDY
        if not passedFilterTauFakeEnrichedDY(self.chain, self.new_chain, cutter, nometcut = self.nometcut, b_veto = self.b_veto, inverted_met_cut = self.inverted_met_cut): return False
        return True

    def getFakeIndex(self):
        return 2

class TauFakeEnrichedTT(FilterObject):
    
    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None, additional_args = None):
        super(TauFakeEnrichedTT, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        self.use_default_objects = additional_args.get('tightWP', False) if additional_args is not None else False
        self.inverted_cut = additional_args.get('inverted_cut', False) if additional_args is not None else False
        if not self.use_default_objects:
            self.chain.obj_sel['tau_wp'] = 'FO'
            self.chain.obj_sel['ele_wp'] = 'tight'
            self.chain.obj_sel['mu_wp'] = 'tight'

    def initEvent(self, cutter, kwargs={}):
        if not self.use_default_objects:        kwargs['sideband'] = None
        return super(TauFakeEnrichedTT, self).initEvent(3, cutter, sort_leptons = False, kwargs=kwargs)

    def passedFilter(self, cutter, kwargs={}):
        if not self.initEvent(cutter, kwargs):                                return False
        from HNL.EventSelection.eventFilters import passedFilterTauFakeEnrichedTT
        if not passedFilterTauFakeEnrichedTT(self.chain, self.new_chain, cutter, inverted_cut = self.inverted_cut): return False        
        return True

    def getFakeIndex(self):
        return 2

class LightLepFakeEnrichedDY(FilterObject):
    
    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None, additional_args = None):
        super(LightLepFakeEnrichedDY, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        self.use_default_objects = additional_args.get('tightWP', False) if additional_args is not None else False
        self.fake_flavors = additional_args.get('fake_flavors', [0, 1]) if additional_args is not None else [0, 1]
        self.chain.obj_sel['notau'] = True
        if not self.use_default_objects:
            self.chain.obj_sel['ele_wp'] = 'FO'
            self.chain.obj_sel['mu_wp'] = 'FO'

    def initEvent(self, cutter, kwargs={}):
        if not self.use_default_objects:        kwargs['sideband'] = None
        return super(LightLepFakeEnrichedDY, self).initEvent(3, cutter, sort_leptons = False, kwargs=kwargs)

    def passedFilter(self, cutter, kwargs={}):
        if not self.initEvent(cutter, kwargs):                                return False
        from HNL.EventSelection.eventFilters import passedFilterLightLepFakeEnrichedDY
        self.fake_index = passedFilterLightLepFakeEnrichedDY(self.chain, self.new_chain, cutter, tightwp = self.use_default_objects, fake_flavors = self.fake_flavors)
        return self.fake_index is not None

    def getFakeIndex(self):
        return self.fake_index

class LightLepFakeEnrichedTT(FilterObject):
    
    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None, additional_args = None):
        super(LightLepFakeEnrichedTT, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        self.use_default_objects = additional_args.get('tightWP', False) if additional_args is not None else False
        self.fake_flavors = additional_args.get('fake_flavors', [0, 1]) if additional_args is not None else [0, 1]
        self.chain.obj_sel['notau'] = True

    def initEvent(self, cutter, kwargs = {}):
        if not self.use_default_objects:        kwargs['sideband'] = None
        return super(LightLepFakeEnrichedTT, self).initEvent(3, cutter, sort_leptons = False, kwargs=kwargs)

    def passedFilter(self, cutter, kwargs={}):
        if not self.initEvent(cutter, kwargs):                                return False
        from HNL.EventSelection.eventFilters import passedFilterLightLepFakeEnrichedTT
        return passedFilterLightLepFakeEnrichedTT(self.chain, self.new_chain, cutter, fake_flavors = self.fake_flavors)

from HNL.ObjectSelection.leptonSelector import isGoodLepton, isFakeLepton
from HNL.EventSelection.eventSelectionTools import selectJets
#Orthogonal due to selection of exactly 1 lepton
class LightLeptonFakeMeasurementRegion(FilterObject):
    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None, additional_args = None):
        super(LightLeptonFakeMeasurementRegion, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        self.use_default_objects = additional_args.get('tightWP', False) if additional_args is not None else False
        self.chain.obj_sel['ele_wp'] = 'loose'
        self.chain.obj_sel['mu_wp'] = 'loose'
        self.chain.obj_sel['notau'] = True

    def initEvent(self, cutter, kwargs={}):
        if not self.use_default_objects:        kwargs['sideband'] = None
        return super(LightLeptonFakeMeasurementRegion, self).initEvent(1, cutter, sort_leptons = False, kwargs=kwargs)

    def passedFilter(self, cutter, kwargs={}):
        if not cutter.cut(self.chain._passMETFilters, 'pass met filters'): return False

        #Select exactly one lepton and veto a second loose lepton
        if not self.initEvent(cutter, kwargs):                                return False
        if not cutter.cut(isGoodLightLepton(self.chain, self.chain.l_indices[0], 'FO'), 'is FO lepton'): return False

        only_muons = kwargs.get('only_muons', False)
        only_electrons = kwargs.get('only_electrons', False)
        require_jets = kwargs.get('require_jets', False)

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

class GeneralMCCTRegion(FilterObject):
    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None):
        super(GeneralMCCTRegion, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)

    def initEvent(self, cutter, kwargs={}):
        #kwargs['sideband'] = None
        return super(GeneralMCCTRegion, self).initEvent(3, cutter, sort_leptons = False, kwargs=kwargs)

    def passedFilter(self, cutter, kwargs={}):
        if not self.initEvent(cutter, kwargs):                                return False
        from HNL.EventSelection.eventFilters import passedGeneralMCCT
        flavors = kwargs.get('flavors', [])
        if not passedGeneralMCCT(self.chain, self.new_chain, cutter, flavors=flavors): return False        
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

        self.loose_leptons_of_interest = []

    def initEvent(self, cutter, kwargs):
        kwargs['sideband'] = None
        return super(ClosureTestMC, self).initEvent(3, cutter, sort_leptons = False, kwargs=kwargs)

    def hasCorrectNumberOfFakes(self):
        self.loose_leptons_of_interest = []
        is_tight_lep = []
        is_fake_lep = []
        translated_flavors_of_interest = [self.flavor_dict[i] for i in self.flavors_of_interest]

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
        else:
            if all(is_tight_lep):
                return any(is_fake_lep)
            else:
                for tl, fl in zip(is_tight_lep, is_fake_lep):
                    if not tl and not fl: return False
                return True

    def passedFilter(self, cutter, kwargs):
        if not self.initEvent(cutter, kwargs):                                return False
        applyConeCorrection(self.chain, self.new_chain)
        region = kwargs.get('region')
        if 'tau' in self.flavors_of_interest:
            if region != 'Mix':
                if not cutter.cut(self.chain._met < 50, 'MET<50'): return False
                # if not cutter.cut(containsOSSF(self.chain), 'OSSF present'): return False
                if not cutter.cut(not bVeto(self.chain), 'b-veto'): return False
            else:
                if not passedFilterTauMixCT(self.chain, self.new_chain, self.is_reco_level, cutter): return False

        if not cutter.cut(self.hasCorrectNumberOfFakes(), 'correct number of fakes'): return False
        # if not cutter.cut(self.chain._passMETFilters, 'pass met filters'): return False

        return True

class TauMixCTfilter(FilterObject):

    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization = None, additional_options={}):
        super(TauMixCTfilter, self).__init__(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        self.high_met = additional_options.get('high_met', True)
        self.b_veto = additional_options.get('b_veto', True)
        self.no_met = additional_options.get('no_met', False)

    def initEvent(self, cutter, kwargs={}):
        return super(TauMixCTfilter, self).initEvent(3, cutter, sort_leptons = True, kwargs=kwargs)

    def passedFilter(self, cutter, kwargs={}):
        if not self.initEvent(cutter, kwargs):                                return False
        from HNL.EventSelection.eventFilters import passedFilterTauMixCT
        return passedFilterTauMixCT(self.chain, self.new_chain, cutter, high_met = self.high_met, b_veto = self.b_veto, no_met = self.no_met)


