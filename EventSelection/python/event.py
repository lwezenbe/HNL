from HNL.ObjectSelection.objectSelection import getObjectSelection
from HNL.ObjectSelection.leptonSelector import isGoodLepton
from HNL.EventSelection.eventSelector import EventSelector
from HNL.EventSelection.eventCategorization import EventCategory

class Event:

    def __init__(self, chain, new_chain, is_reco_level=True, **kwargs):
        self.chain = chain
        self.new_chain = new_chain

        self.chain.strategy = kwargs.get('strategy')
        self.chain.region = kwargs.get('region')
        self.chain.selection = kwargs.get('selection')
        self.additional_options = kwargs.get('additional_options', None)

        self.chain.obj_sel = getObjectSelection(self.chain.selection)

        self.event_category = EventCategory(self.chain)
        self.event_selector = EventSelector(self.chain.region, self.chain, self.new_chain, is_reco_level=is_reco_level, event_categorization=self.event_category, additional_options=self.additional_options)

    def initEvent(self):
        self.chain.is_loose_lepton = [None]*self.chain._nL
        self.chain.is_FO_lepton = [None]*self.chain._nL
        self.chain.is_tight_lepton = [None]*self.chain._nL
        self.processLeptons()

    def processLeptons(self):
        self.processMuons()
        self.processElectrons()
        self.processTaus()

    def processMuons(self):
        for l in xrange(self.chain._nEle, self.chain._nLight):
            self.chain.is_loose_lepton[l] = (isGoodLepton(self.chain, l, 'loose'), self.chain.obj_sel['light_algo'])
            self.chain.is_FO_lepton[l] = (isGoodLepton(self.chain, l, 'FO'), self.chain.obj_sel['light_algo'])
            self.chain.is_tight_lepton[l] = (isGoodLepton(self.chain, l, 'tight'), self.chain.obj_sel['light_algo'])

    def processElectrons(self):
        for l in xrange(self.chain._nEle):
            self.chain.is_loose_lepton[l] = (isGoodLepton(self.chain, l, 'loose'), self.chain.obj_sel['light_algo'])
            self.chain.is_FO_lepton[l] = (isGoodLepton(self.chain, l, 'FO'), self.chain.obj_sel['light_algo'])
            self.chain.is_tight_lepton[l] = (isGoodLepton(self.chain, l, 'tight'), self.chain.obj_sel['light_algo'])

    def processTaus(self):
        for l in xrange(self.chain._nLight, self.chain._nL):
            self.chain.is_loose_lepton[l] = (isGoodLepton(self.chain, l, 'loose'), self.chain.obj_sel['tau_algo'])
            self.chain.is_FO_lepton[l] = (isGoodLepton(self.chain, l, 'FO'), self.chain.obj_sel['tau_algo'])
            self.chain.is_tight_lepton[l] = (isGoodLepton(self.chain, l, 'tight'), self.chain.obj_sel['tau_algo'])

    def passedFilter(self, cutter, sample_name):
        return self.event_selector.passedFilter(cutter, sample_name)