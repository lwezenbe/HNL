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
# from HNL.EventSelection.controlRegionSelector import ZZCRfilter, WZCRfilter, ConversionCRfilter, TauFakeEnrichedDY, TauFakeEnrichedTT, TauClosureTest, ElectronClosureTest, MuonClosureTest, LightLeptonFakeMeasurementRegion, LukaClosureTest, ClosureTestMC, ClosureTestDATA
from HNL.EventSelection.controlRegionSelector import ZZCRfilter, WZCRfilter, ConversionCRfilter, TauFakeEnrichedDY, TauFakeEnrichedTT, LightLeptonFakeMeasurementRegion, ClosureTestMC, ClosureTestDATA, GeneralMCCTRegion
from HNL.EventSelection.controlRegionSelector import TauMixCTfilter, GeneralTrileptonFilter

class EventSelector:

    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization=None, additional_options=None):
        self.name = name
        self.chain = chain
        self.new_chain = new_chain
        self.is_reco_level = is_reco_level
        if self.name in ['baseline', 'lowMassSR', 'highMassSR']:
            if chain.is_data and not 'sideband' in additional_options:
                raise RuntimeError("Running this would mean unblinding. Dont do this.")
            self.selector = SignalRegionSelector(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_options=additional_options)
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
        elif self.name == 'TauFakesDYCT':
            self.selector = TauFakeEnrichedDY(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_args={'tightWP' : True, 'b_veto' : True})
        elif self.name == 'TauFakesDYCTnomet':
            self.selector = TauFakeEnrichedDY(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_args={'tightWP' : True, 'b_veto' : True, 'nometcut':True})
        elif self.name == 'TauFakesTT':
            self.selector = TauFakeEnrichedTT(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_args={'tightWP' : True})
        elif self.name == 'TauFakesDYttl':
            self.selector = TauFakeEnrichedDY(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'TauFakesTTttl':
            self.selector = TauFakeEnrichedTT(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'LightLeptonFakes':
            self.selector = LightLeptonFakeMeasurementRegion(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'TauMixCT':
            self.selector = TauMixCTfilter(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'TauMixCTNoMet':
            self.selector = TauMixCTfilter(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_options={'no_met' : True})
        elif self.name == 'TauMixCTLowMet':
            self.selector = TauMixCTfilter(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_options={'high_met' : False})
        elif self.name == 'TauMixCTLowMetM3lcut':
            self.selector = TauMixCTfilter(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_options={'high_met' : False, 'm3lcut' : True})
        elif self.name == 'TauMixCTLowMetM3lcutNoBveto':
            self.selector = TauMixCTfilter(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_options={'high_met' : False, 'm3lcut' : True, 'b_veto' : False})
        elif self.name == 'TauMixCTM3lcut':
            self.selector = TauMixCTfilter(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_options={'m3lcut' : True})
        elif self.name == 'TauMixCTM3lcutInverted':
            self.selector = TauMixCTfilter(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_options={'high_met' : False, 'm3lcut_inverted' : True, 'b_veto' : False})
        elif self.name == 'TauMixCTNoBveto':
            self.selector = TauMixCTfilter(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_options={'b_veto' : False})
        elif self.name == 'TauMixCTLowMetNoBveto':
            self.selector = TauMixCTfilter(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_options={'high_met' : False, 'b_veto' : False})
        elif self.name == 'MCCT':
            self.selector = GeneralMCCTRegion(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'NoSelection':
            if chain.is_data and not 'sideband' in additional_options:
                raise RuntimeError("Running this would mean unblinding. Dont do this.")
            self.selector = SignalRegionSelector('baseline', chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        else:
            raise RuntimeError("Unknown region specified.")

    def leptonFromMEExternalConversion(self):
        for lepton_index in xrange(self.chain._nL):
            if self.chain._lMatchPdgId[lepton_index] != 22: continue
            if not (self.chain._lIsPrompt[lepton_index] and self.chain._lProvenanceConversion[lepton_index]): continue
            return True
        return False

    def removeOverlapDYandZG(self, sample_name):
        if sample_name == 'DY' and self.chain._zgEventType >= 3: return False
        if sample_name == 'ZG' and self.leptonFromMEExternalConversion(): return False
        return True

    def passedFilter(self, cutter, sample_name, kwargs={}):
        if not self.removeOverlapDYandZG(sample_name): return False
        if self.name != 'NoSelection':
            return self.selector.passedFilter(cutter, kwargs)
            from HNL.Triggers.triggerSelection import passOfflineThresholds
            offline_thresholds = kwargs.get('offline_tresholds', True)
            if offline_tresholds and not cutter.cut(passOfflineThresholds(chain, chain.analysis), "Pass offline thresholds"): return False
        else:
            return True