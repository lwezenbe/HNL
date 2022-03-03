#Same as controlregionselector but with added option for signal vs background extraction (Want to use cut-based analysis selection or MVA based?)
from eventSelectionTools import select3Leptons, selectGenLeptonsGeneral, calculateEventVariables
from HNL.ObjectSelection.leptonSelector import isGoodLepton

from HNL.EventSelection.eventSelector import FilterObject
from HNL.EventSelection.eventFilters import passBaseCuts, passLowMassSelection, passHighMassSelection

class SignalRegionSelector(FilterObject):

    def __init__(self, region, chain, new_chain, is_reco_level=True, event_categorization = None):
        super(SignalRegionSelector, self).__init__(region, chain, new_chain, is_reco_level=is_reco_level, event_categorization = event_categorization)


    def initEvent(self, cutter, sideband = None):
        return super(SignalRegionSelector, self).initEvent(3, cutter, sort_leptons = True, sideband = sideband)
        if self.ec is not None: self.chain.category = self.ec.returnCategory()
        return True

    def initSkim(self, cutter):
        est.select3Leptons(self.chain, self.new_chain, cutter=cutter)
        if len(self.new_chain.l_pt) < 3: return False

    # @classmethod
    def passedStandaloneFilter(self, cutter, region, kwargs):
        for_training = kwargs.get('for_training')
        if not passBaseCuts(self.chain, self.new_chain, cutter, for_training=for_training): return False
        if region == 'lowMassSR':
            return passLowMassSelection(self.chain, self.new_chain, self.is_reco_level, cutter, for_training=for_training)
        elif region == 'highMassSR':
            return passHighMassSelection(self.chain, self.new_chain, self.is_reco_level, cutter, for_training=for_training)
        elif region == 'lowMassSRForTraining':
            return passLowMassSelection(self.chain, self.new_chain, self.is_reco_level, cutter, for_training=True)
        elif region == 'highMassSRForTraining':
            return passHighMassSelection(self.chain, self.new_chain, self.is_reco_level, cutter, for_training=True)
        elif region == 'lowMassTrainingEmulation':
            return passLowMassSelection(self.chain, self.new_chain, self.is_reco_level, cutter, for_training=True) and self.new_chain.M3l < 80
        elif region == 'baseline':
            return True
        else:
            raise RuntimeError("Unknown signal region: "+region)

    def passedFilter(self, cutter, kwargs):
        sideband=kwargs.get('sideband', None)
        manually_blinded = kwargs.get('manually_blinded', False)

        if self.chain.is_data and sideband is None and not manually_blinded:
            raise RuntimeError("\033[93m Running this would mean unblinding. Make sure you dont store the results. \033[0m")

        if not self.initEvent(cutter, sideband=sideband): return False

        # if not self.is_reco_level:  return True #It has passed the basic selection

        if not self.passedStandaloneFilter(cutter, self.region, kwargs): return False

        return True
