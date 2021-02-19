#Combine signalRegionSelector and controlRegionSelector here
from HNL.EventSelection.signalRegionSelector import SignalRegionSelector
from HNL.EventSelection.controlRegionSelector import ZZCRfilter, WZCRfilter, ConversionCRfilter, TauFakeEnrichedDY, TauFakeEnrichedTT, TauClosureTest, ElectronClosureTest, MuonClosureTest, LightLeptonFakeMeasurementRegion, LukaClosureTest, ClosureTestMC, ClosureTestDATA

class EventSelector:

    def __init__(self, name, chain, new_chain, is_reco_level=True, event_categorization=None, in_data=False, additional_options=None):
        self.name = name
        self.chain = chain
        self.new_chain = new_chain
        self.is_reco_level = is_reco_level
        if self.name in ['baseline', 'lowMassSR', 'highMassSR']:
            if in_data:
                raise RuntimeError("Running this would mean unblinding. Dont do this.")
            self.selector = SignalRegionSelector(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'ZZCR':
            self.selector = ZZCRfilter(name, chain, new_chain, is_reco_level=is_reco_level)
        elif self.name == 'WZCR':
            self.selector = WZCRfilter(name, chain, new_chain, is_reco_level=is_reco_level)
        elif self.name == 'ConversionCR':
            self.selector = ConversionCRfilter(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'TauFakesDY':
            self.selector = TauFakeEnrichedDY(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'TauFakesTT':
            self.selector = TauFakeEnrichedTT(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'LightLeptonFakes':
            self.selector = LightLeptonFakeMeasurementRegion(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'TauCT':
            self.selector = TauClosureTest(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'ElectronCT':
            self.selector = ElectronClosureTest(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'MuonCT':
            self.selector = MuonClosureTest(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'LukaCT':
            self.selector = LukaClosureTest(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'MCCT':
            self.selector = ClosureTestMC(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_options=additional_options)
        elif self.name == 'DataCT':
            self.selector = ClosureTestDATA(name, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, additional_options=additional_options)
        elif self.name == 'NoSelection':
            if in_data:
                raise RuntimeError("Running this would mean unblinding. Dont do this.")
            self.selector = SignalRegionSelector('baseline', chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)

    def passedFilter(self, cutter):
        if self.name != 'NoSelection':
            return self.selector.passedFilter(cutter)
        else:
            return True