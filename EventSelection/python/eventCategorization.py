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
CATEGORY_NAMES = {1: 'SS-TauEleEle',
                2: 'SS-EleTauEle',
                3: 'SS-EleEleTau',
                4: 'OS-TauEleEle',
                5: 'OS-EleTauEle',
                6: 'OS-EleEleTau',
                7: 'SS-TauMuMu',
                8: 'SS-MuTauMu',
                9: 'SS-MuMuTau',
                10: 'OS-TauMuMu',
                11: 'OS-MuTauMu',
                12: 'OS-MuMuTau',
                13: 'EleMuTau',
                14: 'MuEleTau',
                15: 'EleTauMu',
                16: 'MuTauEle',
                17: 'TauEleMu',
                18: 'TauMuEle',
                19: 'EEE',
                20: 'MuMuMu',
                21: 'SS-EEMu',
                22: 'SS-EMuE',
                23: 'SS-MuEE',
                24: 'OS-EEMu',
                25: 'OS-EMuE',
                26: 'OS-MuEE',
                27: 'SS-EMuMu',
                28: 'SS-MuEMu',
                29: 'SS-MuMuE',
                30: 'OS-EMuMu',
                31: 'OS-MuEMu',
                32: 'OS-MuMuE',
                33: 'Other'}

CATEGORY_FROM_NAME = {'SS-TauEleEle':1,
                'SS-EleTauEle':2,
                'SS-EleEleTau':3,
                'OS-TauEleEle':4,
                'OS-EleTauEle':5,
                'OS-EleEleTau':6,
                'SS-TauMuMu':7,
                'SS-MuTauMu':8,
                'SS-MuMuTau':9,
                'OS-TauMuMu':10,
                'OS-MuTauMu':11,
                'OS-MuMuTau':12,
                'EleMuTau':13,
                'MuEleTau':14,
                'EleTauMu':15,
                'MuTauEle':16,
                'TauEleMu':17,
                'TauMuEle':18,
                'EEE':19,
                'MuMuMu':20,
                'SS-EEMu':21,
                'SS-EMuE':22,
                'SS-MuEE':23,
                'OS-EEMu':24,
                'OS-EMuE':25,
                'OS-MuEE':26,
                'SS-EMuMu':27,
                'SS-MuEMu':28,
                'SS-MuMuE':29,
                'OS-EMuMu':30,
                'OS-MuEMu':31,
                'OS-MuMuE':32,
                'Other':33}

CATEGORY_TEX_NAMES = {
                1: '#tau e^{#pm}e^{#pm}',
                2: 'e^{#pm}#tau e^{#pm}',
                3: 'e^{#pm}e^{#pm}#tau',
                4: 'e^{#pm}#tau e^{#mp}',
                5: 'e^{#pm}#tau e^{#mp}',
                6: 'e^{#pm}e^{#mp}#tau',
                7: '#tau #mu^{#pm}#mu^{#pm}',
                8: '#mu^{#pm}#tau #mu^{#pm}',
                9: '#mu^{#pm}#mu^{#pm}#tau',
                10: '#tau #mu^{#pm}#mu^{#mp}',
                11: '#mu^{#pm}#tau #mu^{#mp}',
                12: '#mu^{#pm}#mu^{#mp}#tau',
                13: 'e#mu#tau',
                14: '#mu e#tau',
                15: 'e#tau#mu',
                16: '#mu#tau e',
                17: '#tau e#mu',
                18: '#tau#mu e',
                19: 'eee',
                20: '#mu#mu#mu',
                21: 'e^{#pm}e^{#pm}#mu',
                22: 'e^{#pm}#mu e^{#pm}',
                23: '#mu e^{#pm}e^{#pm}',
                24: 'e^{#pm}e^{#mp}#mu',
                25: 'e^{#pm}#mu e^{#mp}',
                26: '#mu e^{#pm}e^{#mp}',
                27: 'e#mu^{#pm}#mu^{#pm}',
                28: '#mu^{#pm}e#mu^{#pm}',
                29: '#mu^{#pm}#mu^{#pm}e',
                30: 'e#mu^{#pm}#mu^{#mp}',
                31: '#mu^{#pm}e#mu^{#mp}',
                32: '#mu^{#pm}#mu^{#mp}e',
                33: 'Other'
}

CATEGORIES = sorted(CATEGORY_NAMES.keys())
CATEGORIES_TO_USE = range(1, len(CATEGORIES))
                
#
# Super categories are a super collection of categories
# Accompanying function to filter more easily than messing around with these dictionaries
#
SUPER_CATEGORIES = {
    'SingleTau' : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18], 
    'NoTau' : [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32], 
    'Other': [33]
    }
SUPER_CATEGORIES_TEX = {
    'SingleTau' : '2 light lep + #tau_{h}', 
    'NoTau' : '3 light lep', 
#    'Total': [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16], 
    'Other': '4 leptons'
    }
mutual_exclusive_supercategories = ['SingleTau', 'NoTau']

ANALYSIS_CATEGORIES = {
    'OneTau-OSSF': [4, 5, 6, 10, 11, 12],
    'OneTau-OF' : [13, 14, 15, 16, 17, 18],
    'OneTau-SSSF': [1, 2, 3, 7, 8, 9], 
    'EEE-Mu': [19, 21, 22, 23, 24, 25, 26], 
    'MuMuMu-E': [20, 27, 28, 29, 30, 31, 32], 
    }

ANALYSIS_CATEGORIES_TEX = {
    'OneTau-OSSF'       : 'l^{+}l^{-}#tau_{h}',
    'OneTau-OF'         : 'e#mu#tau_{h}',
    'OneTau-SSSF'       : 'l^{#pm}l^{#pm}#tau_{h}',
    'EEE-Mu'            : 'eee/#mu',
    'MuMuMu-E'          : '#mu#mu#mu/e'
}
mutual_exclusive_analysiscategories = ['OneTau-OSSF', 'OneTau-SSSF', 'OneTau-OF', 'EEE-Mu', 'MuMuMu-E']

ANALYSIS_SPLITOSSF_CATEGORIES = {
    'OneTau-OSSF': [4, 5, 6, 10, 11, 12],
    'OneTau-OF' : [13, 14, 15, 16, 17, 18],
    'OneTau-SSSF': [1, 2, 3, 7, 8, 9], 
    'EEE-Mu-OSSF': [19, 24, 25, 26], 
    'EEE-Mu-nOSSF': [21, 22, 23], 
    'MuMuMu-E-OSSF': [20, 30, 31, 32], 
    'MuMuMu-E-nOSSF': [27, 28, 29], 
    }

ANALYSIS_SPLITOSSF_CATEGORIES_TEX = {
    'OneTau-OSSF'       : 'l^{+}l^{-}#tau_{h}',
    'OneTau-OF'         : 'e#mu#tau_{h}',
    'OneTau-SSSF'       : 'l^{#pm}l^{#pm}#tau_{h}',
    'EEE-Mu-OSSF'       : 'e^{+}e^{-}e/#mu',
    'EEE-Mu-nOSSF'      : 'e^{#pm}e^{#pm}e/#mu',
    'MuMuMu-E-OSSF'     : '#mu^{+}#mu^{-}#mu/e',
    'MuMuMu-E-nOSSF'    : '#mu^{#pm}#mu^{#pm}#mu/e'
}

def isLightLeptonFinalState(cat_key):
    if cat_key in SUPER_CATEGORIES.keys():
        return cat_key == 'NoTau'
    elif cat_key in ANALYSIS_CATEGORIES.keys() or cat_key in ANALYSIS_SPLITOSSF_CATEGORIES.keys():
        return not 'OneTau' in cat_key
    else:
        return cat_key in SUPER_CATEGORIES[cat_key]

def translateCategories(in_cat):
    if in_cat in SUPER_CATEGORIES.keys():
        return in_cat
    elif in_cat in ANALYSIS_CATEGORIES.keys():
        det_cat = ANALYSIS_CATEGORIES[in_cat]
        for mut_ex_sup in mutual_exclusive_supercategories:
            correct_cat = True
            for dc in det_cat:
                if dc not in SUPER_CATEGORIES[mut_ex_sup]: 
                    correct_cat = False
                    break
            if correct_cat: return mut_ex_sup
        return None
    else:
        raise RuntimeError("Unknown category")

def getAllAnalysisCategoriesFromSuper(super_cat):
    out_cat = []
    for an_cat in mutual_exclusive_analysiscategories:
        if translateCategories(an_cat) == super_cat: out_cat.append(an_cat)
    return out_cat
            

TRIGGER_CATEGORIES = {
    'TauEE': [1, 2, 3, 4, 5, 6], 
    'TauMuMu': [7, 8, 9, 10, 11, 12], 
    'TauEMu':[13, 14, 15, 16, 17, 18], 
    'EEE': [19], 
    'MuMuMu': [20], 
    'EEMu': [21, 22, 23, 24, 25, 26], 
    'EMuMu': [27, 28, 29, 30, 31, 32],
    'LeadingLightLepElectron' : [1, 2, 3, 4, 5, 6, 13, 15, 17, 19, 21, 22, 24, 25, 27, 30], 
    'LeadingLightLepMuon' : [7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 23, 26, 28, 29, 31, 32],
    #'CrossCategory' : [13, 14, 15, 16, 17, 18, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32],
#    'CrossCategoryLeadingElectron' : [13, 15, 17, 21, 22, 24, 25, 27, 30],
#    'CrossCategoryLeadingMuon' : [14, 16, 18, 23, 26,28, 29, 31, 32],
#    'DoubleElectrons' : [2, 3, 5, 6, 19, 21, 22, 24, 25],
#    'DoubleMuons' : [8, 9, 11, 12, 20, 28, 29, 31, 32]
    } 

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
    
    def __init__(self, chain, new_chain):
        self.chain = chain
        self.new_chain = new_chain
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
        
        for f in self.new_chain.l_flavor:
            self.n_l  += 1
            if f == 0:  self.n_ele += 1
            elif f == 1:  self.n_mu += 1
            elif f == 2:  self.n_tau += 1
        
        # if self.n_l != 3: 
            # print "flavorContent in eventCategorization is seeing inconsistent entries"
            # exit(0)

    def hasOSSFpair(self, flavor):
        for first_lepton in [l1, l2]:
            if self.new_chain.l_flavor[first_lepton] != flavor: continue
            for second_lepton in [l2, l3]:
                if self.new_chain.l_flavor[second_lepton] != flavor: continue
                if first_lepton == second_lepton: continue

                if self.new_chain.l_charge[first_lepton] != self.new_chain.l_charge[second_lepton]: return True

        return False

    def hasSSSFpair(self, flavor):
        for first_lepton in [l1, l2]:
            if self.new_chain.l_flavor[first_lepton] != flavor: continue
            for second_lepton in [l2, l3]:
                if self.new_chain.l_flavor[second_lepton] != flavor: continue
                if first_lepton == second_lepton: continue

                if self.new_chain.l_charge[first_lepton] == self.new_chain.l_charge[second_lepton]: return True

        return False
            

    def returnCategory(self):
        self.flavorContent()

        if self.n_l != 3: 
            return CATEGORY_FROM_NAME['Other']

        if self.n_tau > 1:
            return CATEGORY_FROM_NAME['Other']

        #Category 1 - 18:
        elif self.n_tau == 1:
            if self.n_ele == 2:
                if self.hasSSSFpair(0): 
                    if self.new_chain.l_flavor[2] == 2:
                        return 1
                    if self.new_chain.l_flavor[1] == 2:
                        return 2
                    if self.new_chain.l_flavor[0] == 2:
                        return 3
                    return CATEGORY_FROM_NAME['Other']
                elif self.hasOSSFpair(0): 
                    if self.new_chain.l_flavor[2] == 2:
                        return 4
                    if self.new_chain.l_flavor[1] == 2:
                        return 5
                    if self.new_chain.l_flavor[0] == 2:
                        return 6
                    return CATEGORY_FROM_NAME['Other']
            elif self.n_mu == 2:
                if self.hasSSSFpair(1): 
                    if self.new_chain.l_flavor[2] == 2:
                        return 7
                    if self.new_chain.l_flavor[1] == 2:
                        return 8
                    if self.new_chain.l_flavor[0] == 2:
                        return 9
                    return CATEGORY_FROM_NAME['Other']
                elif self.hasOSSFpair(1): 
                    if self.new_chain.l_flavor[2] == 2:
                        return 10
                    if self.new_chain.l_flavor[1] == 2:
                        return 11
                    if self.new_chain.l_flavor[0] == 2:
                        return 12
                    return CATEGORY_FROM_NAME['Other']
            elif self.n_mu == 1 and self.n_ele == 1:
                    if self.new_chain.l_flavor[0] == 0 and self.new_chain.l_flavor[1] == 1:
                        return 13
                    if self.new_chain.l_flavor[0] == 1 and self.new_chain.l_flavor[1] == 0:
                        return 14
                    if self.new_chain.l_flavor[0] == 1 and self.new_chain.l_flavor[1] == 2:
                        return 15
                    if self.new_chain.l_flavor[0] == 0 and self.new_chain.l_flavor[1] == 2:
                        return 16
                    if self.new_chain.l_flavor[0] == 2 and self.new_chain.l_flavor[1] == 0:
                        return 17
                    if self.new_chain.l_flavor[0] == 2 and self.new_chain.l_flavor[1] == 1:
                        return 18
                    return CATEGORY_FROM_NAME['Other']
            else:
                return CATEGORY_FROM_NAME['Other']

        #All light lepton categories
        elif self.n_tau == 0:
            if self.n_ele == 3:
                return 19
            elif self.n_ele == 0 and self.n_mu == 3:
                return 20
            elif self.n_ele == 2 and self.n_mu == 1:
                if self.hasSSSFpair(0): 
                    if self.new_chain.l_flavor[2] == 1:
                        return 21
                    if self.new_chain.l_flavor[1] == 1:
                        return 22
                    if self.new_chain.l_flavor[0] == 1:
                        return 23
                    return CATEGORY_FROM_NAME['Other']
                elif self.hasOSSFpair(0):            
                    if self.new_chain.l_flavor[2] == 1:
                        return 24
                    if self.new_chain.l_flavor[1] == 1:
                        return 25
                    if self.new_chain.l_flavor[0] == 1:
                        return 26
                    return CATEGORY_FROM_NAME['Other']
            elif self.n_ele == 1 and self.n_mu == 2:
                if self.hasSSSFpair(1): 
                    if self.new_chain.l_flavor[2] == 0:
                        return 27
                    if self.new_chain.l_flavor[1] == 0:
                        return 28
                    if self.new_chain.l_flavor[0] == 0:
                        return 29
                    return CATEGORY_FROM_NAME['Other']
                elif self.hasOSSFpair(1):            
                    if self.new_chain.l_flavor[2] == 0:
                        return 30
                    if self.new_chain.l_flavor[1] == 0:
                        return 31
                    if self.new_chain.l_flavor[0] == 0:
                        return 32
                    return CATEGORY_FROM_NAME['Other']
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

    def returnSuperCategory(self):
        cat = self.returnCategory()
        for k in mutual_exclusive_supercategories:
            if cat in SUPER_CATEGORIES[k]: return k
        return None

    def returnSignalTruthCategory(self):
        self.flavorContent()
        #Category 1 and 2:
        if self.new_chain.l_flavor[l1] == 2 and self.new_chain.l_flavor[l2] == 2:
            if self.new_chain.l_flavor[l3] == 0:
                #Category 1:
                if self.new_chain.l_charge[l1] == self.new_chain.l_charge[l2]:
                    self.category = 1
                #Category 2:
                else:
                    self.category = 2
            elif self.new_chain.l_flavor[l3] == 1:
                #Category 1:
                if self.new_chain.l_charge[l1] == self.new_chain.l_charge[l2]:
                    self.category = 3
                #Category 2:
                else:
                    self.category = 4
            else:
                self.category = CATEGORY_FROM_NAME['Other']

        elif self.new_chain.l_flavor[l1] == 2:
            if self.new_chain.l_charge[l2] != self.new_chain.l_charge[l3]:
                if self.new_chain.l_flavor[l2] == 0 and self.new_chain.l_flavor[l3] == 0: self.category = 6 
                elif self.new_chain.l_flavor[l2] == 1 and self.new_chain.l_flavor[l3] == 1: self.category = 8
                else:
                    self.category = CATEGORY_FROM_NAME['Other'] 
        elif self.new_chain.l_flavor[l2] == 2:
            if self.new_chain.l_charge[l2] == self.new_chain.l_charge[l3]:
                if self.new_chain.l_flavor[l1] == 0 and self.new_chain.l_flavor[l3] == 0: self.category = 5 
                elif self.new_chain.l_flavor[l1] == 1 and self.new_chain.l_flavor[l3] == 1: self.category = 7
                else:
                    self.category = CATEGORY_FROM_NAME['Other']  
            if self.new_chain.l_flavor[l1] == 0 and self.new_chain.l_flavor[l3] == 1: self.category = 9 
            if self.new_chain.l_flavor[l1] == 1 and self.new_chain.l_flavor[l3] == 0: self.category = 10 

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
