#Same as controlregionselector but with added option for signal vs background extraction (Want to use cut-based analysis selection or MVA based?)
import eventSelectionTools as est

class SignalRegionSelector:

    def __init__(self, region, selection, objsel, is_reco_level=True, event_categorization = None):
        self.region = region
        self.selection = selection
        self.objsel = objsel
        self.is_reco_level = is_reco_level
        self.ec = event_categorization

    def initEvent(self, chain, new_chain, cutter):
        if self.is_reco_level and not cutter.cut(est.select3Leptons(chain, new_chain, light_algo = self.objsel['light_algo'], no_tau=self.objsel['no_tau'], 
            cutter=cutter, workingpoint = self.objsel['workingpoint']), '3_tight_leptons'): return False
        if not self.is_reco_level and not cutter.cut(est.select3GenLeptons(chain, new_chain, light_algo = self.objsel['light_algo'], no_tau=self.objsel['no_tau'], 
            cutter=cutter, workingpoint = self.objsel['workingpoint']), '3_tight_leptons'): return False
        est.calculateGeneralVariables(chain, new_chain, is_reco_level=self.is_reco_level)
        est.calculateThreeLepVariables(chain, new_chain, is_reco_level=self.is_reco_level)
        chain.category = self.ec.returnCategory()
        return True

    def initSkim(self, chain, new_chain, cutter):
        est.select3Leptons(chain, new_chain, light_algo = self.objsel['light_algo'], no_tau=self.objsel['no_tau'], cutter=cutter, workingpoint = self.objsel['workingpoint'])
        if len(chain.l_pt) < 3: return False

    #
    # AN 2017-014 base selection
    #
    def baseFilterAN2017(self, chain, new_chain, cutter):
        if not cutter.cut(est.passesPtCutsAN2017014(chain), 'pt_cuts'):         return False 
        if not cutter.cut(not est.bVeto(chain, 'AN2017014', cleaned=False, selection=self.selection), 'b-veto'):              return False
        if not cutter.cut(not est.threeSameSignVeto(chain), 'three_same_sign_veto'):                    return False
        if not cutter.cut(not est.fourthFOVeto(chain, self.objsel['light_algo'], no_tau=self.objsel['no_tau']), '4th_l_veto'):   return False

        return True
    
    #
    # Basic cuts every event has to pass
    #
    def baseFilterCutBased(self, chain, new_chain, cutter):
        if not cutter.cut(not est.fourthFOVeto(chain, self.objsel['light_algo'], no_tau=self.objsel['no_tau']), 'Fourth FO veto'):        return False 
        if not cutter.cut(not est.threeSameSignVeto(chain), 'No three same sign'):        return False
        if not cutter.cut(not est.bVeto(chain, 'Deep', selection=self.selection), 'b-veto'):              return False
        return True

    def passBaseCuts(self, chain, new_chain, cutter):
        if self.selection == 'AN2017014':
            return self.baseFilterAN2017(chain, new_chain, cutter)
        else:
            return self.baseFilterCutBased(chain, new_chain, cutter)

    
    #Low mass selection
    @classmethod
    def passLowMassSelection(self, chain, new_chain, cutter):
        if not cutter.cut(new_chain.l_pt[l1] < 55, 'l1pt<55'):      return False
        if not cutter.cut(new_chain.M3l < 80, 'm3l<80'):            return False
        if not cutter.cut(chain._met < 75, 'MET < 75'):             return False
        if not cutter.cut(not est.containsOSSF(chain), 'no OSSF'):      return False
        return True 
    
    #High mass selection
    @classmethod
    def passHighMassSelection(self, chain, new_chain, cutter):
        if not cutter.cut(new_chain.l_pt[l1] > 55, 'l1pt>55'):        return False
        if not cutter.cut(new_chain.l_pt[l2] > 15, 'l2pt>15'):        return False
        if not cutter.cut(new_chain.l_pt[l3] > 10, 'l3pt>10'):        return False
        if est.containsOSSF(chain):
            if not cutter.cut(abs(chain.MZossf-MZ) > 15, 'M2l_OSSF_Z_veto'):        return False
            if not cutter.cut(abs(new_chain.M3l-MZ) > 15, 'M3l_Z_veto'):        return False 
            if not cutter.cut(new_chain.minMossf > 5, 'minMossf'): return False
        return True 

    def passedFilter(self, chain, new_chain, cutter):
        if not self.initEvent(chain, new_chain, cutter): return False

        if not self.passBaseCuts(chain, new_chain, cutter): return False

        if self.region == 'lowMassSR':
            return self.passLowMassSelection(chain, new_chain, cutter)
        elif self.region == 'highMassSR':
            return self.passHighMassSelection(chain, new_chain, cutter)
        elif self.region == 'baseline':
            return True
        else:
            raise RuntimeError('Given signal region: "'+ self.region +'" not known')

    
