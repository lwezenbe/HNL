from HNL.ObjectSelection.objectSelection import getObjectSelection
from HNL.ObjectSelection.leptonSelector import isGoodLepton, isFakeLepton
from HNL.EventSelection.eventSelectionTools import applyConeCorrection
from HNL.EventSelection.eventSelector import EventSelector
from HNL.EventSelection.eventCategorization import EventCategory
from HNL.Weights.tauEnergyScale import TauEnergyScale

def setSideband(chain):
    if 0 in chain.need_sideband:
        chain.obj_sel['ele_wp'] = 'FO'
    if 1 in chain.need_sideband:
        chain.obj_sel['mu_wp'] = 'FO'
    if 2 in chain.need_sideband:
        chain.obj_sel['tau_wp'] = 'FO'


class Event(object):

    def __init__(self, sample, new_chain, sample_manager, is_reco_level=True, **kwargs):
        self.sample = sample
        self.sample_manager = sample_manager
        self.chain = sample.chain
        self.new_chain = new_chain

        self.chain.strategy = kwargs.get('strategy')
        self.chain.region = kwargs.get('region')
        self.chain.selection = kwargs.get('selection')
        self.chain.analysis = kwargs.get('analysis')
        self.chain.year = kwargs.get('year')
        self.chain.era = kwargs.get('era')
        self.additional_options = kwargs.get('additional_options', None)
        self.chain.is_reco_level = is_reco_level

        self.use_corrected_met = kwargs.get('use_corrected_met', False) 
        self.chain.obj_sel = kwargs.get('obj_sel', getObjectSelection(self.chain.selection))
        self.chain.need_sideband = kwargs.get('sideband', None)
        self.chain.original_object_selection = {k:self.chain.obj_sel[k] for k in self.chain.obj_sel.keys()}
        if self.chain.need_sideband is not None:
            setSideband(self.chain)       
 
        self.event_category = EventCategory(self.chain, self.new_chain)
        self.chain.category = None
        self.chain.weight = None
        self.chain.lumiweight = None

        from HNL.EventSelection.searchRegions import SearchRegionManager
        ignore_sr = kwargs.get('ignore_searchregions', False)
        if not ignore_sr:
            self.srm = SearchRegionManager(self.chain.region)
        else:
            self.srm = None
        self.chain.searchregion = None

        self.event_selector = EventSelector(self.chain.region, self.chain, self.new_chain, is_reco_level=is_reco_level, event_categorization=self.event_category, search_region_manager = self.srm, additional_options=self.additional_options)
        
        self.tau_energy_scale = TauEnergyScale(self.chain.era, self.chain.year, self.chain.obj_sel['tau_algo'])
        self.tau_energy_scale_syst = 'nominal'


        from HNL.Weights.reweighter import Reweighter
        from HNL.Systematics.systematics import Systematics
        tau_method = kwargs.get('tau_method', 'TauFakesDY' if self.chain.region == 'ZZCR' else None)
        ignore_fakerates = kwargs.get('ignore_fakerates', False)
        fakerate_from_data = kwargs.get('fakerate_from_data', None)
        nonprompt_scalefactors = kwargs.get('nonprompt_scalefactors', False)
        ignore_weights = kwargs.get('ignore_weights', False)
        if not ignore_weights:
            self.reweighter = Reweighter(self.sample, self.sample_manager, tau_method = tau_method, ignore_fakerates = ignore_fakerates, nonprompt_scalefactors = nonprompt_scalefactors)
            self.systematics = Systematics(self.sample, self.reweighter)
        else:
            self.reweighter = None
            self.systematics = None

    def initEvent(self, reset_obj_sel = False):
        if reset_obj_sel: 
            self.chain.obj_sel = {k:self.chain.original_object_selection[k] for k in self.chain.obj_sel.keys()} #reset object selection
            if self.chain.need_sideband is not None:
                setSideband(self.chain)       
        self.chain.category = None
        self.chain.searchregion = None
        if self.chain.weight is not None: self.chain.weight = self.reweighter.getLumiWeight()
        if self.reweighter is not None: self.chain.lumiweight = self.reweighter.getLumiWeight()
        self.chain.is_loose_lepton = [None]*self.chain._nL
        self.chain.is_FO_lepton = [None]*self.chain._nL
        self.chain.is_tight_lepton = [None]*self.chain._nL
        self.chain.conecorrection_applied = False
        self.chain.is_sideband = None if self.chain.is_reco_level else False
        self.chain.is_charge_flip_event = False
        self.processLeptons(tau_energy_scale = self.tau_energy_scale_syst)

        from HNL.ObjectSelection.jetSelector import getMET
        self.chain.met, self.chain.metPhi = getMET(self.chain, apply_corrections = self.use_corrected_met)

    def processLeptons(self, tau_energy_scale = 'nominal'):
        self.processMuons()
        self.processElectrons()
        self.processTaus(tau_energy_scale)

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

    def processTaus(self, energy_scale_syst = 'nominal'):
        for l in xrange(self.chain._nLight, self.chain._nL):
            # First apply energy scale
            if not self.chain.is_data:
                from HNL.Tools.helpers import getFourVec
                tlv = getFourVec(self.chain._lPt[l], self.chain._lEta[l], self.chain._lPhi[l], self.chain._lE[l])
                es = self.tau_energy_scale.readES(tlv, self.chain._tauDecayMode[l], self.chain._tauGenStatus[l], syst=energy_scale_syst)
                self.chain._lPt[l] *= es
                self.chain._lE[l] *= es

            self.chain.is_loose_lepton[l] = (isGoodLepton(self.chain, l, 'loose'), self.chain.obj_sel['tau_algo'])
            self.chain.is_FO_lepton[l] = (isGoodLepton(self.chain, l, 'FO'), self.chain.obj_sel['tau_algo'])
            self.chain.is_tight_lepton[l] = (isGoodLepton(self.chain, l, 'tight'), self.chain.obj_sel['tau_algo'])

    def passedFilter(self, cutter, sample_name, **kwargs):
        if kwargs.get('calculate_weights', False): kwargs['reweighter'] = self.reweighter
        passed =  self.event_selector.passedFilter(cutter, sample_name, kwargs)
        if passed:
            if self.srm is not None:
                self.chain.searchregion = self.srm.getSearchRegion(self.chain)
            else:
                self.chain.searchregion = 1

            self.chain.category = self.event_category.returnCategory()
            from HNL.EventSelection.eventSelectionTools import isChargeFlip
            if not self.sample.is_data and self.chain.is_reco_level: self.chain.is_charge_flip_event = isChargeFlip(self.chain, self.new_chain)
            return True
        return False

    def resetObjSelection(self):
        self.chain.obj_sel = getObjectSelection(self.chain.selection)

class ClosureTestEvent(Event):
    flavor_dict = {'tau' : 2, 'ele' : 0, 'mu' : 1}

    def __init__(self, sample, new_chain, sample_manager, strategy, region, selection, flavors_of_interest, in_data, analysis, year, era, is_reco_level = True):
        self.flavors_of_interest = flavors_of_interest
        self.translated_flavors_of_interest = [self.flavor_dict[i] for i in self.flavors_of_interest]
        super(ClosureTestEvent, self).__init__(sample, new_chain, sample_manager, is_reco_level, strategy=strategy, region=region, selection=selection, analysis=analysis, year=year, era=era, additional_options={'fake_flavors' : self.translated_flavors_of_interest}, ignore_fakerates = True) #ignore_fakerates set to True because they are calculated elsewhere in the closure tests, quite messy, I know
        self.in_data = in_data
        if self.flavors_of_interest is None: 
            raise RuntimeError('Input for ClosureTestMC for flavors_of_interest is None')

        # Set Object Selection
        self.chain.obj_sel['tau_wp'] = 'FO' if 'tau' in self.flavors_of_interest else 'tight'
        self.chain.obj_sel['ele_wp'] = 'FO' if 'ele' in self.flavors_of_interest else 'tight'
        self.chain.obj_sel['mu_wp'] = 'FO' if 'mu' in self.flavors_of_interest else 'tight'

        self.loose_leptons_of_interest = []



    def hasCorrectNumberOfFakes(self):
        self.loose_leptons_of_interest = []
        is_tight_lep = []
        is_fake_lep = []

        #Make input more readable
        for l in xrange(len(self.new_chain.l_pt)):
            #Rule out all other flavors so we are only continuing with general functions on leptons of the correct flavor
            if not self.new_chain.l_flavor[l] in self.translated_flavors_of_interest: 
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

    def passedFilter(self, cutter, sample_name, **kwargs):
        passed =  self.event_selector.passedFilter(cutter, sample_name, kwargs)
        if not passed: return False
        applyConeCorrection(self.chain, self.new_chain)

        if not self.in_data:
            if not cutter.cut(self.hasCorrectNumberOfFakes(), 'correct number of fakes'): return False
        elif self.chain.region in ['TauFakesDYCT', 'TauFakesTT']:
            self.loose_leptons_of_interest = [2]
        elif self.chain.region in ['baseline', 'lowMassSR', 'highMassSR']:
            raise RuntimeError('Not allowed')
        return True

    def getFakeIndex(self):
        try:
            return [self.event_selector.selector.getFakeIndex()]
        except:
            return [x for x in xrange(3) if self.new_chain.l_flavor[x] in self.translated_flavors_of_interest]

    
