#Combine signalRegionSelector and controlRegionSelector here
from HNL.EventSelection.signalRegionSelector import SignalRegionSelector
from HNL.EventSelection.controlRegionSelector import ZZCRfilter, WZCRfilter, ConversionCRfilter, TauFakeEnrichedDY

class EventSelector:

    def __init__(self, name, selection, objsel, is_reco_level=True, event_categorization = None):
        self.name = name
        self.selection = selection
        self.objsel = objsel
        self.is_reco_level = is_reco_level
        if self.name in ['baseline', 'lowMassSR', 'highMassSR']:
            self.selector = SignalRegionSelector(name, selection, objsel, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'ZZCR':
            self.selector = ZZCRfilter(name, selection, objsel, is_reco_level=is_reco_level)
        elif self.name == 'WZCR':
            self.selector = WZCRfilter(name, selection, objsel, is_reco_level=is_reco_level)
        elif self.name == 'ConversionCR':
            self.selector = ConversionCRfilter(name, selection, objsel, is_reco_level=is_reco_level, event_categorization = event_categorization)
        elif self.name == 'TauFakes':
            self.selector = TauFakeEnrichedDY(name, selection, objsel, is_reco_level=is_reco_level, event_categorization = event_categorization)




    def passedFilter(self, chain, new_chain, cutter):
        return self.selector.passedFilter(chain, new_chain, cutter)
