#Combine signalRegionSelector and controlRegionSelector here
import HNL.EventSelection.eventCategorization as cat
from HNL.EventSelection.eventSelectionTools import selectLeptonsGeneral, selectGenLeptonsGeneral, calculateEventVariables, removeOverlapDYandZG
from HNL.ObjectSelection.leptonSelector import isGoodLepton
class FilterObject(object):

    def __init__(self, region, chain, new_chain, is_reco_level=True, event_categorization = None):
        self.region = region
        self.chain = chain
        self.new_chain = new_chain
        self.is_reco_level = is_reco_level
        self.ec = event_categorization

    def initEvent(self, nL, cutter, sort_leptons, kwargs={}):
        offline_thresholds = kwargs.get('offline_thresholds', True)       

        if self.is_reco_level:
            if not selectLeptonsGeneral(self.chain, self.new_chain, nL, cutter=cutter, sort_leptons = sort_leptons): return False
        else:
            if not selectGenLeptonsGeneral(self.chain, self.new_chain, nL, cutter=cutter): return False

        if 'ZG' in kwargs['sample_name'] or 'DY' in kwargs['sample_name']:
            if not cutter.cut(not removeOverlapDYandZG(self.new_chain.is_prompt, kwargs['sample_name']), 'Clean Nonprompt ZG'): return False

        self.chain.category = self.ec.returnCategory()
        reweighter = kwargs.get('reweighter')
        if kwargs.get('calculate_weights', False) and reweighter is not None:
            self.chain.weight = reweighter.getTotalWeight(sideband = self.chain.need_sideband, tau_fake_method = 'TauFakesDY' if self.region == 'ZZCR' else None)

        from HNL.Triggers.triggerSelection import passOfflineThresholds
        if offline_thresholds and not cutter.cut(passOfflineThresholds(self.chain, self.new_chain, self.chain.analysis), "Pass offline thresholds"): 
            return False

        calculateEventVariables(self.chain, self.new_chain, nL, is_reco_level=self.is_reco_level)
        return True


from HNL.EventSelection.signalRegionSelector import SignalRegionSelector
from HNL.EventSelection.controlRegionSelector import ZZCRfilter, WZCRfilter, ConversionCRfilter, TauFakeEnrichedDY, TauFakeEnrichedTT, LightLeptonFakeMeasurementRegion, ClosureTestMC, GeneralMCCTRegion
from HNL.EventSelection.controlRegionSelector import TauMixCTfilter, GeneralTrileptonFilter, LightLepFakeEnrichedDY, LightLepFakeEnrichedTT, HighMassWithBJetfilter

signal_regions = ['baseline', 'lowMassSR', 'highMassSR', 'lowMassSRloose', 'highMassSROSSF', 'highMassSRnoOSSF']

class EventSelector:

    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization=None, additional_options=None):
        self.name = name
        self.chain = chain
        self.new_chain = new_chain
        self.is_reco_level = is_reco_level
        if self.name in signal_regions:
            self.selector = SignalRegionSelector(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization)
        elif self.name == 'trilepton':
            self.selector = GeneralTrileptonFilter(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization)
        elif self.name == 'ZZCR':
            self.selector = ZZCRfilter(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization)
        elif self.name == 'WZCR':
            self.selector = WZCRfilter(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization)
        elif self.name == 'ConversionCR':
            self.selector = ConversionCRfilter(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization)
        elif self.name == 'TauFakesDY':
            self.selector = TauFakeEnrichedDY(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization, additional_args={'tightWP' : True})
        elif self.name == 'TauFakesDYnomet':
            self.selector = TauFakeEnrichedDY(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization, additional_args={'tightWP' : True, 'nometcut' : True})
        elif self.name == 'TauFakesDYCT':
            self.selector = TauFakeEnrichedDY(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization, additional_args={'tightWP' : True, 'b_veto' : True, 'inverted_met_cut':True})
        elif self.name == 'TauFakesDYCTnomet':
            self.selector = TauFakeEnrichedDY(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization, additional_args={'tightWP' : True, 'b_veto' : True, 'nometcut':True})
        elif self.name == 'TauFakesTT':
            self.selector = TauFakeEnrichedTT(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization, additional_args={'tightWP' : True})
        elif self.name == 'TauFakesTTCT':
            self.selector = TauFakeEnrichedTT(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization, additional_args={'tightWP' : True, 'inverted_cut' : True})
        elif self.name == 'TauFakesDYttl':
            self.selector = TauFakeEnrichedDY(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization)
        elif self.name == 'TauFakesDYttlnomet':
            self.selector = TauFakeEnrichedDY(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization, additional_args={'nometcut' : True})
        elif self.name == 'TauFakesTTttl':
            self.selector = TauFakeEnrichedTT(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization)
        elif self.name == 'LightLepFakesDY':
            self.selector = LightLepFakeEnrichedDY(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization, additional_args = additional_options)
        elif self.name == 'LightLepFakesTT':
            self.selector = LightLepFakeEnrichedTT(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization, additional_args = additional_options)
        elif self.name == 'LightLepFakesDYCT':
            self.selector = LightLepFakeEnrichedDY(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization, additional_args = {'tightWP' : True})
        elif self.name == 'LightLepFakesTTCT':
            self.selector = LightLepFakeEnrichedTT(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization, additional_args = {'tightWP' : True})
        elif self.name == 'LightLeptonFakes':
            self.selector = LightLeptonFakeMeasurementRegion(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization)
        elif self.name == 'TauMixCT':
            self.selector = TauMixCTfilter(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization)
        elif self.name == 'TauMixCThighmet':
            self.selector = TauMixCTfilter(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization, additional_options={'high_met' : True, 'no_met' : False})
        elif self.name == 'MCCT':
            self.selector = GeneralMCCTRegion(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization)
        elif self.name == 'HighMassWithB':
            self.selector = HighMassWithBJetfilter(name, chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization)
        elif self.name == 'HighMassWithInvertedPt':
            self.selector = SignalRegionSelector('highMassSRInvertedPt', chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization)
        elif self.name == 'NoSelection':
            #if chain.is_data and not ('sideband' in additional_options or 'for_skim' in additional_options):
            #    raise RuntimeError("Running this would mean unblinding. Dont do this.")
            self.selector = SignalRegionSelector('baseline', chain, new_chain, is_reco_level = is_reco_level, event_categorization = event_categorization)
        else:
            raise RuntimeError("Unknown region specified.")

    #def removeOverlapDYandZG(self, sample_name, cutter):
    #    if 'DY' in sample_name and not cutter.cut(self.chain._zgEventType < 3, 'Cleaning DY'): 
    #        return False
    #    if sample_name == 'ZG' and not cutter.cut(self.chain._zgEventType > 2, 'Cleaning XG'): 
    #        return False
    #    return True

    def leptonFromMEExternalConversion(self):
        for lepton_index in xrange(self.chain._nL):
            if self.chain._lMatchPdgId[lepton_index] != 22: continue
            if not (self.chain._lIsPrompt[lepton_index] and self.chain._lProvenanceConversion[lepton_index]): continue
            return True
        return False

    def passedFilter(self, cutter, sample_name, kwargs={}):
        if not cutter.cut(self.chain._passMETFilters, 'metfilters'): return False

        #Triggers
        from HNL.Triggers.triggerSelection import passTriggers
        ignore_triggers = kwargs.get('ignore_triggers', False)
        if not ignore_triggers and not cutter.cut(passTriggers(self.chain, analysis=self.chain.analysis), 'pass_triggers'): return False 

        if self.name != 'NoSelection':
            kwargs['sample_name'] = sample_name
            passed = self.selector.passedFilter(cutter, kwargs)
            if not passed: return False
            return True
        else:
            if 'ZG' in sample_name or 'DY' in sample_name:
                if not cutter.cut(not removeOverlapDYandZG(self.new_chain.is_prompt, sample_name), 'Clean Nonprompt ZG'): return False
            return True




