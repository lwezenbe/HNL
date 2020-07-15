from eventSelectionTools import *
import HNL.EventSelection.eventCategorization as cat

class ZZCRfilter:
    
    def __init__(self, name, selection, objsel, is_reco_level=True, event_categorization = None):
        self.name = name
        self.selection = selection
        self.objsel = objsel
        self.is_reco_level = is_reco_level
        self.ec = event_categorization

    def initEvent(self, chain, new_chain, cutter):
        if not cutter.cut(selectLeptonsGeneral(chain, new_chain, 4, light_algo = self.objsel['light_algo'], no_tau=self.objsel['no_tau'], cutter=cutter, workingpoint = self.objsel['workingpoint']), '4 tight leptons'): return False
        calculateGeneralVariables(chain, new_chain, is_reco_level=self.is_reco_level)
        calculateFourLepVariables(chain, new_chain, is_reco_level=self.is_reco_level)
        chain.category = max(cat.CATEGORIES)
        return True

    def passedFilter(self, chain, new_chain, cutter):
        if not self.initEvent(chain, new_chain, cutter):                                                 return False
        # if not cutter.cut(passesOSSFforZZ(new_chain), '2 OSSF with Z mass'):                        return False
        if not cutter.cut(not bVeto(chain, self.selection, cleaned=False, selection = self.selection), 'b-veto'):                 return False

        #Relaxed
        if not cutter.cut(massDiff(chain.Mll_Z1, MZ) < 15, 'First Z ok'):                                                           return False
        if not cutter.cut(new_chain.minMos > 12, 'min Mos > 12'):                                                                       return False

        return True

class WZCRfilter:

    def __init__(self, name, selection, objsel, is_reco_level=True, event_categorization = None):
        self.name = name
        self.selection = selection
        self.objsel = objsel
        self.is_reco_level = is_reco_level
        self.ec = event_categorization


    def initEvent(self, chain, new_chain, cutter):
        if not cutter.cut(select3Leptons(chain, new_chain, light_algo = self.objsel['light_algo'], no_tau=self.objsel['no_tau'], cutter=cutter, workingpoint = self.objsel['workingpoint']), '4 tight leptons'): return False
        calculateGeneralVariables(chain, new_chain, is_reco_level=self.is_reco_level)
        calculateThreeLepVariables(chain, new_chain, is_reco_level=self.is_reco_level)
        chain.category = max(cat.CATEGORIES)
        return True

    def passedFilter(self, chain, new_chain, cutter):
        if not self.initEvent(chain, new_chain, cutter):                                                 return False
        if not cutter.cut(not passesZcuts(chain, new_chain, same_flavor=True), 'On Z OSSF'):              return False
        if not cutter.cut(new_chain.l_pt[l1] > 25, 'l1pt>25'):          return False
        if not cutter.cut(new_chain.l_pt[l2] > 15, 'l2pt>15'):          return False
        if not cutter.cut(new_chain.l_pt[l3] > 10, 'l3pt>10'):          return False
        if not cutter.cut(chain._met > 50, 'MET > 50'):                 return False
        if not cutter.cut(abs(new_chain.M3l-MZ) > 15, 'M3l_Z_veto'):    return False 
        return True

class ConversionCRfilter:

    def __init__(self, name, selection, objsel, is_reco_level=True, event_categorization = None):
        self.name = name
        self.selection = selection
        self.objsel = objsel
        self.is_reco_level = is_reco_level
        self.ec = event_categorization


    def initEvent(self, chain, new_chain, cutter):
        if not cutter.cut(select3Leptons(chain, new_chain, light_algo = self.objsel['light_algo'], no_tau=self.objsel['no_tau'], cutter=cutter, workingpoint = self.objsel['workingpoint']), '4 tight leptons'): return False
        calculateGeneralVariables(chain, new_chain, is_reco_level=self.is_reco_level)
        calculateThreeLepVariables(chain, new_chain, is_reco_level=self.is_reco_level)
        chain.category = self.ec.returnCategory()
        return True

    def passedFilter(self, chain, new_chain, cutter):
        if not self.initEvent(chain, new_chain, cutter):                                                 return False
        if not cutter.cut(containsOSSF(chain), 'OSSF present'):         return False
        if not cutter.cut(abs(new_chain.M3l-MZ) < 15, 'M3l_onZ'):       return False 
        if not cutter.cut(chain.MZossf < 75, 'Mll < 75'):               return False
        if self.selection == 'AN2017014' and not cutter.cut(passesPtCutsAN2017014(chain), 'pt_cuts'):     return False 
        if not cutter.cut(not bVeto(chain, self.selection, cleaned=False, selection = self.selection), 'b-veto'):                 return False
        chain.category = max(cat.CATEGORIES)
        return True

