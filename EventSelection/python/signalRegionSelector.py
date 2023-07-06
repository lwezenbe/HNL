#Same as controlregionselector but with added option for signal vs background extraction (Want to use cut-based analysis selection or MVA based?)
from eventSelectionTools import select3Leptons, selectGenLeptonsGeneral, calculateEventVariables
from HNL.ObjectSelection.leptonSelector import isGoodLepton

from HNL.EventSelection.eventSelector import FilterObject
from HNL.EventSelection.eventFilters import passBaseCuts, passLowMassSelection, passHighMassSelection

class SignalRegionSelector(FilterObject):

    def __init__(self, region, chain, new_chain, is_reco_level = True, event_categorization = None, search_region_manager = None):
        super(SignalRegionSelector, self).__init__(region, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization, search_region_manager = search_region_manager)


    def initEvent(self, cutter, kwargs={}):
        return super(SignalRegionSelector, self).initEvent(3, cutter, sort_leptons = True, kwargs=kwargs)
        if self.ec is not None: self.chain.category = self.ec.returnCategory()
        return True

    def initSkim(self, cutter):
        est.select3Leptons(self.chain, self.new_chain, cutter=cutter)
        if len(self.new_chain.l_pt) < 3: return False

    # @classmethod
    def passedStandaloneFilter(self, cutter, region, kwargs):
        if not passBaseCuts(self.chain, self.new_chain, cutter): return False
        if region == 'lowMassSR':
            return passLowMassSelection(self.chain, self.new_chain, cutter)
        elif region == 'lowMassSRloose':
            return passLowMassSelection(self.chain, self.new_chain, cutter, loose_selection = True)
        elif region == 'highMassSR':
            return passHighMassSelection(self.chain, self.new_chain, cutter)
        elif region == 'highMassSRInvertedPt':
            return passHighMassSelection(self.chain, self.new_chain, cutter, invert_pt = True)
        elif region == 'lowMassSRlooseInvertedM3l':
            return passLowMassSelection(self.chain, self.new_chain, cutter, loose_selection = True, inverted_m3l = True)
        elif region == 'lowMassSRlooseBeforeMZcut':
            return passLowMassSelection(self.chain, self.new_chain, cutter, loose_selection = True, early_stop = True)
        elif region == 'highMassSRnoOSSF':
            return passHighMassSelection(self.chain, self.new_chain, cutter, ossf = False)
        elif region == 'highMassSROSSF':
            return passHighMassSelection(self.chain, self.new_chain, cutter, ossf = True)
        elif region == 'baseline':
            return True
        else:
            raise RuntimeError("Unknown signal region: "+region)

    def passedFilter(self, cutter, kwargs):
        manually_blinded = kwargs.get('manually_blinded', False)

        if not self.initEvent(cutter, kwargs=kwargs): return False

        # if not self.is_reco_level:  return True #It has passed the basic selection

        if not self.passedStandaloneFilter(cutter, self.region, kwargs): return False

        return True
