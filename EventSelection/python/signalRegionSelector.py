#Same as controlregionselector but with added option for signal vs background extraction (Want to use cut-based analysis selection or MVA based?)
import eventSelectionTools as est
from eventSelectionTools import MZ

l1 = 0
l2 = 1
l3 = 2

class SignalRegionSelector:

    def __init__(self, region, chain, new_chain, is_reco_level=True, event_categorization = None):
        self.region = region
        self.chain = chain
        self.new_chain = new_chain
        self.is_reco_level = is_reco_level
        self.ec = event_categorization

    def initEvent(self, cutter):
        if self.is_reco_level and not cutter.cut(est.select3Leptons(self.chain, self.new_chain, cutter=cutter), 'select leptons'): return False
        if not self.is_reco_level and not cutter.cut(est.selectGenLeptonsGeneral(self.chain, self.new_chain, 3, cutter=cutter), 'select leptons'): return False
        est.calculateEventVariables(self.chain, self.new_chain, 3, is_reco_level=self.is_reco_level)
        if self.ec is not None: self.chain.category = self.ec.returnCategory()
        return True

    def initSkim(self, cutter):
        est.select3Leptons(self.chain, self.new_chain, light_algo = self.chain.obj_sel['light_algo'], no_tau=self.chain.obj_sel['notau'], cutter=cutter, workingpoint = self.chain.obj_sel['workingpoint'])
        if len(self.new_chain.l_pt) < 3: return False

    #
    # AN 2017-014 base selection
    #
    def baseFilterAN2017(self, cutter):
        if not cutter.cut(est.passesPtCutsAN2017014(self.chain), 'pt_cuts'):         return False 
        if not cutter.cut(not est.bVeto(self.chain), 'b-veto'):              return False
        if not cutter.cut(not est.threeSameSignVeto(self.chain), 'three_same_sign_veto'):                    return False
        if not cutter.cut(not est.fourthFOVeto(self.chain, no_tau=self.chain.obj_sel['notau']), '4th_l_veto'):   return False

        return True
    
    # Basic cuts every event has to pass
    def baseFilterCutBased(self, cutter):
        if not cutter.cut(not est.fourthFOVeto(self.chain, no_tau=self.chain.obj_sel['notau']), 'Fourth FO veto'):        return False 
        if not cutter.cut(not est.threeSameSignVeto(self.chain), 'No three same sign'):        return False
        if not cutter.cut(not est.bVeto(self.chain), 'b-veto'):              return False
        return True

    # Basic cuts every event has to pass
    def baseFilterMVA(self, cutter):
        if not cutter.cut(not est.fourthFOVeto(self.chain, no_tau=self.chain.obj_sel['notau']), 'Fourth FO veto'):        return False 
        if not cutter.cut(not est.threeSameSignVeto(self.chain), 'No three same sign'):        return False
        if not cutter.cut(not est.bVeto(self.chain), 'b-veto'):              return False
        return True

    def passBaseCuts(self, cutter):
        if self.chain.selection == 'AN2017014':
            return self.baseFilterAN2017(cutter)
        elif self.chain.strategy == 'MVA':
            return self.baseFilterMVA(cutter)
        else:
            return self.baseFilterCutBased(cutter)

    
    #Low mass selection
    # @classmethod
    def passLowMassSelection(self, cutter, for_training=False):
        if not cutter.cut(self.new_chain.l_pt[l1] < 55, 'l1pt<55'):      return False
        if not cutter.cut(self.new_chain.M3l < 80, 'm3l<80'):            return False
        if not for_training:
            if self.is_reco_level:
                if not cutter.cut(self.chain._met < 75, 'MET < 75'):             return False
            else:
                if not cutter.cut(self.chain._gen_met < 75, 'MET < 75'):             return False
            if not cutter.cut(not est.containsOSSF(self.chain), 'no OSSF'):      return False
        return True 
    
    #High mass selection
    # @classmethod
    def passHighMassSelection(self, cutter):
        if not cutter.cut(self.new_chain.l_pt[l1] > 55, 'l1pt>55'):        return False
        if not cutter.cut(self.new_chain.l_pt[l2] > 15, 'l2pt>15'):        return False
        if not cutter.cut(self.new_chain.l_pt[l3] > 10, 'l3pt>10'):        return False
        if est.containsOSSF(self.chain):
            if not cutter.cut(abs(self.chain.MZossf-MZ) > 15, 'M2l_OSSF_Z_veto'):        return False
            if not cutter.cut(abs(self.new_chain.M3l-MZ) > 15, 'M3l_Z_veto'):        return False 
            if not cutter.cut(self.new_chain.minMossf > 5, 'minMossf'): return False
        return True 

    def passedFilter(self, cutter, for_training=False):
        if not self.initEvent(cutter): return False

        if not self.is_reco_level:  return True #It has passed the basic selection

        if not self.passBaseCuts(cutter): return False

        if self.region == 'lowMassSR':
            return self.passLowMassSelection(cutter, for_training=for_training)
        elif self.region == 'highMassSR':
            return self.passHighMassSelection(cutter)
        elif self.region == 'baseline':
            return True
        else:
            raise RuntimeError("Unknown signal region: "+self.region)
