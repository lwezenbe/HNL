from HNL.EventSelection.eventSelectionTools import *
import HNL.EventSelection.eventCategorization as cat
from HNL.ObjectSelection.leptonSelector import *
from HNL.Tools.helpers import getFourVec, deltaPhi, deltaR

class ZZCRfilter:
    
    def __init__(self, name, selection, objsel, is_reco_level=True, event_categorization = None):
        self.name = name
        self.selection = selection
        self.objsel = objsel
        self.is_reco_level = is_reco_level
        self.ec = event_categorization

    def initEvent(self, chain, new_chain, cutter):
        if not cutter.cut(selectLeptonsGeneral(chain, new_chain, 4, light_algo = self.objsel['light_algo'], no_tau=self.objsel['no_tau'], 
            cutter=cutter, workingpoint = self.objsel['workingpoint']), '4 tight leptons'): return False
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
        if not cutter.cut(select3Leptons(chain, new_chain, light_algo = self.objsel['light_algo'], no_tau=self.objsel['no_tau'], 
            cutter=cutter, workingpoint = self.objsel['workingpoint']), '4 tight leptons'): return False
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
        if not cutter.cut(select3Leptons(chain, new_chain, light_algo = self.objsel['light_algo'], no_tau=self.objsel['no_tau'], 
            cutter=cutter, workingpoint = self.objsel['workingpoint']), '4 tight leptons'): return False
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

class TauFakeEnrichedDY:
    
    def __init__(self, name, selection, objsel, is_reco_level=True, event_categorization = None):
        self.name = name
        self.selection = selection
        self.objsel = objsel
        self.is_reco_level = is_reco_level
        self.ec = event_categorization

    def selectCustomLeptons(self, chain, new_chain, light_algo = None, tau_algo = None, cutter = None, lightworkingpoint = 'tight'):

        light_leptons = [(chain._lPt[l], l) for l in xrange(chain._nLight) if isGoodLepton(chain, l, algo = light_algo, workingpoint=lightworkingpoint)]
        taus = [(chain._lPt[l], l) for l in xrange(chain._nLight, chain._nL) if isGoodLepton(chain, l, algo = light_algo, tau_algo=tau_algo, workingpoint='loose')]
        chain.leptons = light_leptons + taus
        if len(light_leptons) != 2:  return False
        if len(taus) != 1:  return False
        if len(chain.leptons) != 3:  return False

        if chain is new_chain:
            new_chain.l_pt = [0.0]*3
            new_chain.l_eta = [0.0]*3
            new_chain.l_phi = [0.0]*3
            new_chain.l_charge = [0.0]*3
            new_chain.l_flavor = [0.0]*3
            new_chain.l_e = [0.0]*3
            new_chain.l_indices = [0.0]*3

        ptAndIndex = chain.leptons

        for i in xrange(3):
            chain.l_indices[i] = ptAndIndex[i][1]
            new_chain.l_pt[i] = ptAndIndex[i][0] 
            new_chain.l_eta[i] = chain._lEta[ptAndIndex[i][1]]
            new_chain.l_phi[i] = chain._lPhi[ptAndIndex[i][1]]
            new_chain.l_e[i] = chain._lE[ptAndIndex[i][1]]
            new_chain.l_charge[i] = chain._lCharge[ptAndIndex[i][1]]
            new_chain.l_flavor[i] = chain._lFlavor[ptAndIndex[i][1]]

        return True

    def initEvent(self, chain, new_chain, cutter):
        if not cutter.cut(self.selectCustomLeptons(chain, new_chain, light_algo = self.objsel['light_algo'], cutter=cutter, lightworkingpoint = self.objsel['workingpoint']), '3 leptons'): return False
        chain.category = self.ec.returnCategory()
        return True

    def passedFilter(self, chain, new_chain, cutter):
        if not self.initEvent(chain, new_chain, cutter):                                                 return False

        if new_chain.l_flavor[0] != new_chain.l_flavor[1]:              return False
        if new_chain.l_charge[0] == new_chain.l_charge[1]:              return False

        l1Vec = getFourVec(new_chain.l_pt[l1], new_chain.l_eta[l1], new_chain.l_phi[l1], new_chain.l_e[l1])
        l2Vec = getFourVec(new_chain.l_pt[l2], new_chain.l_eta[l2], new_chain.l_phi[l2], new_chain.l_e[l2])

        if abs(91. - (l1Vec + l2Vec).M()) > 15: return False
        if chain._met > 50: return False
        return True

    
