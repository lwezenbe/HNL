#Combine signalRegionSelector and controlRegionSelector here
import HNL.EventSelection.eventCategorization as cat
from HNL.EventSelection.eventSelectionTools import selectLeptonsGeneral, selectGenLeptonsGeneral, calculateEventVariables
from HNL.ObjectSelection.leptonSelector import isGoodLepton
class FilterObject(object):

    def __init__(self, region, chain, new_chain, is_reco_level=True, event_categorization = None):
        self.region = region
        self.chain = chain
        self.new_chain = new_chain
        self.is_reco_level = is_reco_level
        self.ec = event_categorization

    def initEvent(self, nL, cutter, sort_leptons, sideband = None):
        if sideband is not None:
            self.chain.obj_sel['tau_wp'] = 'FO'
            self.chain.obj_sel['ele_wp'] = 'FO'
            self.chain.obj_sel['mu_wp'] = 'FO'

        if self.is_reco_level:
            if not cutter.cut(selectLeptonsGeneral(self.chain, self.new_chain, nL, cutter=cutter, sort_leptons = sort_leptons), 'select leptons'): return False
        else:
            if not cutter.cut(selectGenLeptonsGeneral(self.chain, self.new_chain, nL, cutter=cutter), 'select leptons'): return False

        #If sideband, only select events where not all 3 leptons are tight
        if sideband is not None:
            nfail = 0
            for i, l in enumerate(self.chain.l_indices):
                if isinstance(sideband, list) and self.chain.l_flavor[i] not in sideband: continue
                if not isGoodLepton(self.chain, l, 'tight'):
                    nfail += 1
            if nfail < 1: return False

        calculateEventVariables(self.chain, self.new_chain, nL, is_reco_level=self.is_reco_level)
        self.chain.category = max(cat.CATEGORIES)
        return True


from HNL.EventSelection.signalRegionSelector import SignalRegionSelector
from HNL.EventSelection.controlRegionSelector import ZZCRfilter, WZCRfilter, ConversionCRfilter, TauFakeEnrichedDY, TauFakeEnrichedTT, LightLeptonFakeMeasurementRegion, ClosureTestMC, GeneralMCCTRegion
from HNL.EventSelection.controlRegionSelector import TauMixCTfilter, GeneralTrileptonFilter, LightLepFakeEnrichedDY, LightLepFakeEnrichedTT

signal_regions = ['baseline', 'lowMassSR', 'highMassSR', 'lowMassSRloose']

class EventSelector:

    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization=None, additional_options=None):
        self.name = name
        self.chain = chain
        self.new_chain = new_chain
        self.is_reco_level = is_reco_level
        if self.name in signal_regions:
            self.selector = SignalRegionSelector(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'trilepton':
            self.selector = GeneralTrileptonFilter(name, chain, new_chain, is_reco_level=is_reco_level)
        elif self.name == 'ZZCR':
            self.selector = ZZCRfilter(name, chain, new_chain, is_reco_level=is_reco_level)
        elif self.name == 'WZCR':
            self.selector = WZCRfilter(name, chain, new_chain, is_reco_level=is_reco_level)
        elif self.name == 'ConversionCR':
            self.selector = ConversionCRfilter(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'TauFakesDY':
            self.selector = TauFakeEnrichedDY(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_args={'tightWP' : True})
        elif self.name == 'TauFakesDYnomet':
            self.selector = TauFakeEnrichedDY(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_args={'tightWP' : True, 'nometcut' : True})
        elif self.name == 'TauFakesDYCT':
            self.selector = TauFakeEnrichedDY(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_args={'tightWP' : True, 'b_veto' : True, 'inverted_met_cut':True})
        elif self.name == 'TauFakesDYCTnomet':
            self.selector = TauFakeEnrichedDY(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_args={'tightWP' : True, 'b_veto' : True, 'nometcut':True})
        elif self.name == 'TauFakesTT':
            self.selector = TauFakeEnrichedTT(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_args={'tightWP' : True})
        elif self.name == 'TauFakesTTCT':
            self.selector = TauFakeEnrichedTT(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_args={'tightWP' : True, 'inverted_cut' : True})
        elif self.name == 'TauFakesDYttl':
            self.selector = TauFakeEnrichedDY(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'TauFakesDYttlnomet':
            self.selector = TauFakeEnrichedDY(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_args={'nometcut' : True})
        elif self.name == 'TauFakesTTttl':
            self.selector = TauFakeEnrichedTT(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'LightLepFakesDY':
            self.selector = LightLepFakeEnrichedDY(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_args = additional_options)
        elif self.name == 'LightLepFakesTT':
            self.selector = LightLepFakeEnrichedTT(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_args = additional_options)
        elif self.name == 'LightLeptonFakes':
            self.selector = LightLeptonFakeMeasurementRegion(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'TauMixCT':
            self.selector = TauMixCTfilter(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'TauMixCThighmet':
            self.selector = TauMixCTfilter(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_options={'high_met' : True, 'no_met' : False})
        elif self.name == 'MCCT':
            self.selector = GeneralMCCTRegion(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'NoSelection':
            if chain.is_data and not 'sideband' in additional_options:
                raise RuntimeError("Running this would mean unblinding. Dont do this.")
            self.selector = SignalRegionSelector('baseline', chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
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

    def removeOverlapDYandZG(self, sample_name, cutter):
        if 'DY' in sample_name and not cutter.cut(self.leptonFromMEExternalConversion(), 'Cleaning DY'): return False
        if sample_name == 'ZG' and not cutter.cut(not self.leptonFromMEExternalConversion(), 'Cleaning XG'): return False
        return True

    def removeOverlapInTauSignal(self, sample_name):
        if 'taulep' in sample_name:
            nlight = 0.
            ntau = 0.
            for l in xrange(self.chain._gen_nL):
                if self.chain._gen_lFlavor[l] == 2 and self.chain._gen_lVisPt[l] > 18.: ntau += 1.
                if self.chain._gen_lFlavor[l] != 2 and self.chain._gen_lPt[l] > 15. and self.chain._gen_lEta[l] < 3.: nlight += 1.
            return ntau < 1 or nlight < 1
        else:
            return True

    def passedFilter(self, cutter, sample_name, event_category, kwargs={}):
        if not self.removeOverlapDYandZG(sample_name, cutter): return False

        ignoreSignalOverlapRemoval = kwargs.get('ignoreSignalOverlapRemoval', False)
        #if not ignoreSignalOverlapRemoval and not self.removeOverlapInTauSignal(sample_name): return False

        if not cutter.cut(self.chain._passMETFilters, 'metfilters'): return False

        #Triggers
        from HNL.Triggers.triggerSelection import passTriggers
        if not cutter.cut(passTriggers(self.chain, analysis=self.chain.analysis), 'pass_triggers'): return False 

        if self.name != 'NoSelection':
            passed = self.selector.passedFilter(cutter, kwargs)
            if not passed: return False

            # This info is needed for offline thresholds
            self.chain.category = event_category.returnCategory()
            self.chain.detailed_category = event_category.returnDetailedCategory()

            from HNL.Triggers.triggerSelection import passOfflineThresholds
            offline_thresholds = kwargs.get('offline_thresholds', True)
            if offline_thresholds and not cutter.cut(passOfflineThresholds(self.chain, self.new_chain, self.chain.analysis), "Pass offline thresholds"): 
                return False
            return True
        else:
            return True
