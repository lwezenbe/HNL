#############################################################
#                                                           #
#   Class that keeps track of the correct event category    #    
#                                                           #
#############################################################

#
# Define constants to keep track of leptons more easily
#
l1 = 0
l2 = 1
l3 = 2

#
# All categories in this analysis. This is where you add more categories if wanted
# CATEGORY_FROM_NAME is just the inverse for easier use
#
CATEGORY_NAMES = {1: 'SS-TauTauEle', 
                    2: 'OS-TauTauEle', 
                    3: 'SS-TauTauMu', 
                    4: 'OS-TauTauMu', 
                    5: 'SS-EleTauEle', 
                    6: 'OS-TauEleEle', 
                    7: 'SS-MuTauMu', 
                    8: 'OS-TauMuMu', 
                    9: 'EleTauMu', 
                    10: 'MuTauEle', 
                    11: 'EEE', 
                    12: 'MuMuMu', 
                    13: 'SS-EEMu', 
                    14: 'OS-EEMu', 
                    15: 'SS-EMuMu',
                    16: 'OS-EMuMu',
                    17: 'Other'}

CATEGORY_FROM_NAME = {'SS-TauTauEle' : 1, 
                    'OS-TauTauEle' : 2, 
                    'SS-TauTauMu' : 3, 
                    'OS-TauTauMu': 4, 
                    'SS-EleTauEle': 5, 
                    'OS-TauEleEle':6, 
                    'SS-MuTauMu':7, 
                    'OS-TauMuMu':8, 
                    'EleTauMu':9, 
                    'MuTauEle':10, 
                    'EEE':11, 
                    'MuMuMu':12, 
                    'SS-EEMu':13, 
                    'OS-EEMu':14, 
                    'SS-EMuMu':15,
                    'OS-EMuMu':16,
                    'Other':17}

CATEGORY_TEX_NAMES = {
                        1: '#tau^{#pm}#tau^{#pm}e',
                        2: '#tau^{#pm}#tau^{#mp}e',
                        3: '#tau^{#pm}#tau^{#pm}mu',
                        4: '#tau^{#pm}#tau^{#mp}mu',
                        5: 'e^{#pm}e^{#pm}#tau',
                        6: 'e^{#pm}e^{#mp}#tau',
                        7: '#mu^{#pm}#mu^{#pm}#tau',
                        8: '#mu^{#pm}#mu^{#mp}#tau',
                        9: 'e#tau#mu',
                        10: '#mu#tau e',
                        11: 'eee',
                        12: '#mu#mu#mu',
                        13: 'e^{#pm}e^{#pm}#mu',
                        14: 'e^{#pm}e^{#mp}#mu',
                        15: 'e#mu^{#pm}#mu^{#pm}',
                        16: 'e#mu^{#pm}#mu^{#mp}',
                        17: 'Other'
}

CATEGORIES = sorted(CATEGORY_NAMES.keys())
                
#
# Super categories are a super collection of categories
# Accompanying function to filter more easily than messing around with these dictionaries
#
SUPER_CATEGORIES = {'Ditau': [1, 2, 3, 4], 'SingleTau' : [5, 6, 7, 8, 9], 'NoTau' : [11, 12, 13, 14, 15, 16], 'Total': [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16], 'TauFinalStates': [1, 2, 3, 4, 5, 6, 7, 8, 9]}
ANALYSIS_CATEGORIES = {'Ditau': [1, 2, 3, 4], 'SingleTau-OS': [6, 8], 'Single-Tau-SS': [5, 7], 'EEE': [11], 'MuMuMu': [12], 'EEMu': [13, 14], 'EMuMu': [15, 16], 'EEE-Mu': [11, 13, 14], 'MuMuMu-E': [12, 15, 16], 'Other':[9, 10, 17]}
#TODO: This category is a bit dodgy, because it is used in trigger calc but it is quite fragile. If the categories dont give the same output when given as input to returnCategoryTriggers, weird things will happen in that code
TRIGGER_CATEGORIES = {'TauTauE': [1, 2], 'TauTauMu': [3, 4], 'TauEE': [5, 6], 'TauMuMu': [7, 8], 'TauEMu':[9, 10], 'EEE': [11], 'MuMuMu': [12], 'EEMu': [13, 14], 'EMuMu': [15, 16]} 

def filterSuperCategory(super_category_name, category):
    if category in SUPER_CATEGORIES[super_category_name]: return True
    return False


#
# Signal truth categories are experimental
#
CATEGORIES_SIGNALTRUTH = [c for c in xrange(1, len(CATEGORY_NAMES)+2, 1)]


#
# Actual class
#
class EventCategory():
    
    def __init__(self, chain):
        self.chain = chain
        self.n_mu = 0
        self.n_ele = 0
        self.n_tau = 0
        self.n_l = 0
        self.category = None
        self.categories = CATEGORIES
        self.categories_signaltruth = CATEGORIES_SIGNALTRUTH

    def flavorContent(self):

        self.n_l = 0
        self.n_mu = 0
        self.n_ele = 0
        self.n_tau = 0
        
        for f in self.chain.l_flavor:
            self.n_l  += 1
            if f == 0:  self.n_ele += 1
            elif f == 1:  self.n_mu += 1
            elif f == 2:  self.n_tau += 1
        
        if self.n_l != 3: 
            print "flavorContent in eventCategorization is seeing inconsistent entries"
            exit(0)

    def hasOSSFpair(self, flavor):
        for first_lepton in [l1, l2]:
            if self.chain.l_flavor[first_lepton] != flavor: continue
            for second_lepton in [l2, l3]:
                if self.chain.l_flavor[second_lepton] != flavor: continue
                if first_lepton == second_lepton: continue

                if self.chain.l_charge[first_lepton] != self.chain.l_charge[second_lepton]: return True

        return False

    def hasSSSFpair(self, flavor):
        for first_lepton in [l1, l2]:
            if self.chain.l_flavor[first_lepton] != flavor: continue
            for second_lepton in [l2, l3]:
                if self.chain.l_flavor[second_lepton] != flavor: continue
                if first_lepton == second_lepton: continue

                if self.chain.l_charge[first_lepton] == self.chain.l_charge[second_lepton]: return True

        return False
            

    def returnCategory(self):
        self.flavorContent()
        if self.n_tau > 2:
            return CATEGORY_FROM_NAME['Other']

        #Category 1, 2, 3, 4:
        if self.n_tau == 2: 
            if self.n_ele == 1:
                if self.hasSSSFpair(2): return 1
                elif self.hasOSSFpair(2): return 2
            elif self.n_mu == 1:
                if self.hasSSSFpair(2): return 3
                elif self.hasOSSFpair(2): return 4
            else:
                return CATEGORY_FROM_NAME['Other']

        #Category 5, 6, 7, 8, 9:
        elif self.n_tau == 1:
            if self.n_ele == 2:
                if self.hasSSSFpair(0): return 5
                elif self.hasOSSFpair(0): return 6
            elif self.n_mu == 2:
                if self.hasSSSFpair(1): return 7
                elif self.hasOSSFpair(1): return 8
            elif self.n_mu == 1 and self.n_ele == 1:
                return 9
            else:
                return CATEGORY_FROM_NAME['Other']

        #All light lepton categories
        elif self.n_tau == 0:
            if self.n_ele == 3:
                return 11
            elif self.n_ele == 0 and self.n_mu == 3:
                return 12
            elif self.n_ele == 2 and self.n_mu == 1:
                if self.hasSSSFpair(0): return 13
                elif self.hasOSSFpair(0): return 14            
            elif self.n_ele == 1 and self.n_mu == 2:
                if self.hasSSSFpair(1): return 15
                elif self.hasOSSFpair(1): return 16
            else:
                return CATEGORY_FROM_NAME['Other']

        else:
            return CATEGORY_FROM_NAME['Other']
        
        return self.category

    def returnAnalysisCategory(self):
        cat = self.returnCategory()
        for k in ANALYSIS_CATEGORIES.keys():
            if cat in ANALYSIS_CATEGORIES[k]: return k
        return None

    def returnSignalTruthCategory(self):
        self.flavorContent()
        #Category 1 and 2:
        if self.chain.l_flavor[l1] == 2 and self.chain.l_flavor[l2] == 2:
            if self.chain.l_flavor[l3] == 0:
                #Category 1:
                if self.chain.l_charge[l1] == self.chain.l_charge[l2]:
                    self.category = 1
                #Category 2:
                else:
                    self.category = 2
            elif self.chain.l_flavor[l3] == 1:
                #Category 1:
                if self.chain.l_charge[l1] == self.chain.l_charge[l2]:
                    self.category = 3
                #Category 2:
                else:
                    self.category = 4
            else:
                self.category = CATEGORY_FROM_NAME['Other']

        elif self.chain.l_flavor[l1] == 2:
            if self.chain.l_charge[l2] != self.chain.l_charge[l3]:
                if self.chain.l_flavor[l2] == 0 and self.chain.l_flavor[l3] == 0: self.category = 6 
                elif self.chain.l_flavor[l2] == 1 and self.chain.l_flavor[l3] == 1: self.category = 8
                else:
                    self.category = CATEGORY_FROM_NAME['Other'] 
        elif self.chain.l_flavor[l2] == 2:
            if self.chain.l_charge[l2] == self.chain.l_charge[l3]:
                if self.chain.l_flavor[l1] == 0 and self.chain.l_flavor[l3] == 0: self.category = 5 
                elif self.chain.l_flavor[l1] == 1 and self.chain.l_flavor[l3] == 1: self.category = 7
                else:
                    self.category = CATEGORY_FROM_NAME['Other']  
            if self.chain.l_flavor[l1] == 0 and self.chain.l_flavor[l3] == 1: self.category = 9 
            if self.chain.l_flavor[l1] == 1 and self.chain.l_flavor[l3] == 0: self.category = 10 

        #All light lepton categories
        elif self.n_tau == 0:
            if self.n_ele == 3:
                self.category = 11
            elif self.n_ele == 0 and self.n_mu == 3:
                self.category = 12
            elif self.n_ele == 2 and self.n_mu == 1:
                if self.hasSSSFpair(0): self.category = 13
                elif self.hasOSSFpair(0): self.category = 14            
            elif self.n_ele == 1 and self.n_mu == 2:
                if self.hasSSSFpair(1): self.category = 15
                elif self.hasOSSFpair(1): self.category = 16
            else:
                self.category = CATEGORY_FROM_NAME['Other']

        else:
            self.category = CATEGORY_FROM_NAME['Other']
        return self.category
        
#
# Function to return triggers interesting to the specific category
# Used to study triggers
#

def returnCategoryTriggers(chain, cat):
    if cat == 1 or cat == 2:
        return [chain._HLT_Ele27_WPTight_Gsf, chain._HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20, chain._HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg]
    elif cat == 3 or cat == 4:        
        return [chain._HLT_IsoMu24, chain._HLT_IsoMu19_eta2p1_LooseIsoPFTau20, chain._HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg]
    elif cat == 5 or cat == 6:
        return [chain._HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ, chain._HLT_Ele27_WPTight_Gsf, chain._HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20]
    elif cat == 7 or cat == 8:
        return [chain._HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ, chain._HLT_IsoMu24, chain._HLT_IsoMu19_eta2p1_LooseIsoPFTau20]
    elif cat == 9 or cat == 10:
        return [chain._HLT_IsoMu24, chain._HLT_Ele27_WPTight_Gsf, chain._HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ, chain._HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL, chain._HLT_IsoMu19_eta2p1_LooseIsoPFTau20, chain._HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20]
    else:  
        return [chain._HLT_Ele27_WPTight_Gsf, chain._HLT_IsoMu24, chain._HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ, chain._passTrigger_mm, chain._passTrigger_em, chain._passTrigger_eee, chain._passTrigger_eem, chain._passTrigger_emm, chain._passTrigger_mmm]

def returnCategoryTriggerNames(cat):
    if cat == 1 or cat == 2:
        return ['HLT_Ele27_WPTight_Gsf', 'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20', 'HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg']
    elif cat == 3 or cat == 4:        
        return ['HLT_IsoMu24', 'HLT_IsoMu19_eta2p1_LooseIsoPFTau20', 'HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg']
    elif cat == 5 or cat == 6:
        return ['HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ', 'HLT_Ele27_WPTight_Gsf', 'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20']
    elif cat == 9 or cat == 10:
        return ['HLT_IsoMu24', 'HLT_Ele27_WPTight_Gsf',  'HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ', 'HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL', 'HLT_IsoMu19_eta2p1_LooseIsoPFTau20', 'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20']
    elif cat == 7 or cat == 8:
        return ['HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ', 'HLT_IsoMu24', 'HLT_IsoMu19_eta2p1_LooseIsoPFTau20']
    else:
        return['HLT_Ele27_WPTight_Gsf', 'HLT_IsoMu24', 'HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ', 'pass_mm', 'pass_em', 'pass_eee', 'pass_eem', 'pass_emm', 'pass_mmm']

def returnCategoryPtCuts(cat):

    if cat == 1 or cat == 2:       
        return [(None, None, 27), (20, None, 24), (35, 35, None)]    
    elif cat == 3 or cat == 4:       
        return [(None, None, 22), (20, None, 19), (35, 35, None)]    
    elif cat == 5:
        return [(23, None, 12), (24, 20, None), (27, None, None)]
    elif cat == 6:
        return [(None, 23, 12), (20, 24, None), (None, 27, None)]
    elif cat == 7:
        return [(22, None, None), (17, None, 8), (19, 20, None)]
    elif cat == 8:
        return [(None, 22, None), (None, 17, 8), (20, 19, None)]
    elif cat == 9:
        return [(27, None, None), (None, None, 22), (23, None, 12), (24, 20, None)]
    elif cat == 10:
        return [(22, None, None), (None, None, 27), (12, None, 23), (None, 20, 19)]
    
    return [(None, None, None)]

def categoryName(c):
    if c > len(CATEGORY_NAMES):      return 'all'
    return CATEGORY_NAMES[c]

def returnTexName(c, super_cat = False):
    if c > len(CATEGORY_NAMES):      return 'all'
    return CATEGORY_TEX_NAMES[c]
