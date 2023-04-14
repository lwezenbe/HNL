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
CATEGORY_NAMES = {1: 'SS-EleEleTau',
                2: 'SS-EleTauEle',
                3: 'SS-TauEleEle',
                4: 'OS-EleEleTau',
                5: 'OS-EleTauEle',
                6: 'OS-TauEleEle',
                7: 'SS-MuMuTau',
                8: 'SS-MuTauMu',
                9: 'SS-TauMuMu',
                10: 'OS-MuMuTau',
                11: 'OS-MuTauMu',
                12: 'OS-TauMuMu',
                13: 'SS-EleMuTau',
                14: 'SS-MuEleTau',
                15: 'SS-EleTauMu',
                16: 'SS-MuTauEle',
                17: 'SS-TauEleMu',
                18: 'SS-TauMuEle',
                19: 'OS-EleMuTau',
                20: 'OS-MuEleTau',
                21: 'OS-EleTauMu',
                22: 'OS-MuTauEle',
                23: 'OS-TauEleMu',
                24: 'OS-TauMuEle',
                25: 'EEE',
                26: 'MuMuMu',
                27: 'SS-EEMu',
                28: 'SS-EMuE',
                29: 'SS-MuEE',
                30: 'OS-EEMu',
                31: 'OS-EMuE',
                32: 'OS-MuEE',
                33: 'SS-EMuMu',
                34: 'SS-MuEMu',
                35: 'SS-MuMuE',
                36: 'OS-EMuMu',
                37: 'OS-MuEMu',
                38: 'OS-MuMuE',
                39: 'Other'}

CATEGORY_FROM_NAME = {'SS-EleEleTau':1,
                'SS-EleTauEle':2,
                'SS-TauEleEle':3,
                'OS-EleEleTau':4,
                'OS-EleTauEle':5,
                'OS-TauEleEle':6,
                'SS-MuMuTau':7,
                'SS-MuTauMu':8,
                'SS-TauMuMu':9,
                'OS-MuMuTau':10,
                'OS-MuTauMu':11,
                'OS-TauMuMu':12,
                'SS-EleMuTau':13,
                'SS-MuEleTau':14,
                'SS-EleTauMu':15,
                'SS-MuTauEle':16,
                'SS-TauEleMu':17,
                'SS-TauMuEle':18,
                'OS-EleMuTau':19,
                'OS-MuEleTau':20,
                'OS-EleTauMu':21,
                'OS-MuTauEle':22,
                'OS-TauEleMu':23,
                'OS-TauMuEle':24,
                'EEE':25,
                'MuMuMu':26,
                'SS-EEMu':27,
                'SS-EMuE':28,
                'SS-MuEE':29,
                'OS-EEMu':30,
                'OS-EMuE':31,
                'OS-MuEE':32,
                'SS-EMuMu':33,
                'SS-MuEMu':34,
                'SS-MuMuE':35,
                'OS-EMuMu':36,
                'OS-MuEMu':37,
                'OS-MuMuE':38,
                'Other':39}

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
                13: 'e^{#pm}#mu^{#pm}#tau',
                14: '#mu^{#pm} e^{#pm}#tau',
                15: 'e^{#pm}#tau#mu^{#pm}',
                16: '#mu^{#pm}#tau e^{#pm}',
                17: '#tau e^{#pm}#mu^{#pm}',
                18: '#tau#mu^{#pm} e^{#pm}',
                19: 'e^{#pm}#mu^{#mp}#tau',
                20: '#mu^{#pm} e^{#mp}#tau',
                21: 'e^{#pm}#tau#mu^{#mp}',
                22: '#mu^{#pm}#tau e^{#mp}',
                23: '#tau e^{#pm}#mu^{#mp}',
                24: '#tau#mu^{#pm} e^{#mp}',
                25: 'eee',
                26: '#mu#mu#mu',
                27: 'e^{#pm}e^{#pm}#mu',
                28: 'e^{#pm}#mu e^{#pm}',
                29: '#mu e^{#pm}e^{#pm}',
                30: 'e^{#pm}e^{#mp}#mu',
                31: 'e^{#pm}#mu e^{#mp}',
                32: '#mu e^{#pm}e^{#mp}',
                33: 'e#mu^{#pm}#mu^{#pm}',
                34: '#mu^{#pm}e#mu^{#pm}',
                35: '#mu^{#pm}#mu^{#pm}e',
                36: 'e#mu^{#pm}#mu^{#mp}',
                37: '#mu^{#pm}e#mu^{#mp}',
                38: '#mu^{#pm}#mu^{#mp}e',
                39: 'Other'
}

CATEGORIES = sorted(CATEGORY_NAMES.keys())
CATEGORIES_TO_USE = range(1, len(CATEGORIES))
                
#
# Super categories are a super collection of categories
# Accompanying function to filter more easily than messing around with these dictionaries
#
SUPER_CATEGORIES = {
    'SingleTau' : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], 
    'NoTau' : [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38], 
    'Other': [39]
    }
SUPER_CATEGORIES_TEX = {
    'SingleTau' : '2 light lep + #tau_{h}', 
    'NoTau' : '3 light lep', 
#    'Total': [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16], 
    'Other': '4 leptons'
    }
mutual_exclusive_supercategories = ['SingleTau', 'NoTau']

ANALYSIS_CATEGORIES = {
#    'OneTau-OSSF': [4, 5, 6, 10, 11, 12],
#    'OneTau-OF' : [13, 14, 15, 16, 17, 18],
#    'OneTau-SSSF': [1, 2, 3, 7, 8, 9], 
    'TauEE' : [1, 2, 3, 4, 5, 6],
    'TauMuMu' : [7, 8, 9, 10, 11, 12],
    'TauEMu' : [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
    'EEE-Mu': [25, 27, 28, 29, 30, 31, 32], 
    'MuMuMu-E': [26, 33, 34, 35, 36, 37, 38], 
    #'EEE': [19], 
    #'EEMu': [ 21, 22, 23, 24, 25, 26], 
    #'MuMuMu': [20], 
    #'MuMuE': [27, 28, 29, 30, 31, 32], 
    }

ANALYSIS_CATEGORIES_TEX = {
    #'OneTau-OSSF'       : 'l^{+}l^{-}#tau_{h}',
    #'OneTau-OF'         : 'e#mu#tau_{h}',
    #'OneTau-SSSF'       : 'l^{#pm}l^{#pm}#tau_{h}',
    'TauEE'             : 'ee#tau_{h}',
    'TauMuMu'           : '#mu#mu#tau_{h}',
    'TauEMu'           : '#e#mu#tau_{h}',
    'EEE-Mu'            : 'eee/#mu',
    'MuMuMu-E'          : '#mu#mu#mu/e',
    #'EEE'               : 'eee',
    #'EEMu'              : 'ee#mu',
    #'MuMuMu'            : '#mu#mu#mu',
    #'MuMuE'             : '#mu#mu e',
}

SIGN_CATEGORIES = {
    'SS-EEM': [27, 28, 29],
    'OS-EEM': [30, 31, 32],
    'SS-EMT': [13, 14, 15, 16, 17, 18],
    'OS-EMT': [19, 20, 21, 22, 23, 24]
}
SIGN_CATEGORIES_TEX = {
    'SS-EEM': 'e^{#pm}e^{#pm}#mu',
    'OS-EEM': 'e^{#pm}e^{#mp}#mu',
    'SS-EMT': 'e^{#pm}#mu^{#pm}#tau',
    'OS-EMT': 'e^{#pm}#mu^{#mp}#tau'
}

mutual_exclusive_analysiscategories = ['OneTau-OSSF', 'OneTau-SSSF', 'OneTau-OF', 'EEE-Mu', 'MuMuMu-E']

ANALYSIS_SPLITOSSF_CATEGORIES = {
    'OneTau-OSSF': [4, 5, 6, 10, 11, 12],
    'OneTau-OF' : [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
    'OneTau-SSSF': [1, 2, 3, 7, 8, 9], 
    'EEE-Mu-OSSF': [25, 30, 31, 32], 
    'EEE-Mu-nOSSF': [27, 28, 29], 
    'MuMuMu-E-OSSF': [26, 36, 37, 38], 
    'MuMuMu-E-nOSSF': [33, 34, 35], 
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

LEADING_FLAVOR_CATEGORIES = {
    'LeadingElectron': [25, 27, 28, 30, 31, 33, 36], 
    'LeadingMuon': [26, 29, 32, 34, 35, 37, 38], 
    'LeadingTau':  [3, 6, 9, 12, 17, 18, 23, 24],
    'SubleadingTau' : [2, 5, 8, 11, 15, 16, 21, 22],
    'TrailingTau' : [1, 4, 7, 10, 13, 14, 19, 20],
}

LEADING_FLAVOR_CATEGORIES_TEX = {
    'LeadingElectron'           : 'ell',
    'LeadingMuon'               : '#mu ll',
    'LeadingTau'                : '#tau ll',
    'SubleadingTau'             : 'l#tau l',
    'TrailingTau'               : 'll#tau',
}

def isLightLeptonFinalState(cat_key):
    if cat_key in SUPER_CATEGORIES.keys():
        return cat_key == 'NoTau'
    elif cat_key in ANALYSIS_CATEGORIES.keys() or cat_key in ANALYSIS_SPLITOSSF_CATEGORIES.keys():
        return not 'Tau' in cat_key
    elif cat_key in LEADING_FLAVOR_CATEGORIES.keys():
        return not 'Electron' in cat_key and not 'Muon' in cat_key
    elif cat_key in TRIGGER_CATEGORIES.keys():
        return not 'Tau' in cat_key
    else:
        return float(cat_key) > 18

def isPartOfCategory(in_name, cat_key):
    if in_name == cat_key: return True

    if in_name in ANALYSIS_CATEGORIES.keys():
        return cat_key in ANALYSIS_CATEGORIES[in_name] 
    elif in_name in SUPER_CATEGORIES.keys():
        return cat_key in SUPER_CATEGORIES[in_name]
    elif in_name in CATEGORY_NAME.keys():
        return cat_key == in_name
    else:
        raise RuntimeError('Unknown category grouping')
        

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
    'TauEMu':[13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24], 
    'EEE': [25], 
    'MuMuMu': [26], 
    'EEMu': [27, 28, 29, 30, 31, 32], 
    'EMuMu': [33, 34, 35, 36, 37, 38],
    'LeadingLightLepElectron' : [1, 2, 3, 4, 5, 6, 13, 15, 17, 19, 21, 23, 25, 27, 28, 30, 31, 33, 36], 
    'LeadingLightLepMuon' : [7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 29, 32, 34, 35, 37, 38],
    } 

TRIGGER_CATEGORIES_TEX = {
    'TauEE': 'ee#tau', 
    'TauMuMu': '#mu#mu#tau', 
    'TauEMu': 'e#mu#tau', 
    'EEE': 'eee', 
    'MuMuMu': '#mu#mu#mu', 
    'EEMu': 'ee#mu', 
    'EMuMu': 'e#mu#mu',
    'LeadingLightLepElectron' : 'ell', 
    'LeadingLightLepMuon' : '#mu ll'
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
                        if self.new_chain.l_charge[0] == self.new_chain.l_charge[1]:
                            return 13
                        else:
                            return 19
                    if self.new_chain.l_flavor[0] == 1 and self.new_chain.l_flavor[1] == 0:
                        if self.new_chain.l_charge[0] == self.new_chain.l_charge[1]:
                            return 14
                        else:
                            return 20
                    if self.new_chain.l_flavor[0] == 1 and self.new_chain.l_flavor[1] == 2:
                        if self.new_chain.l_charge[0] == self.new_chain.l_charge[2]:
                            return 15
                        else:
                            return 21
                    if self.new_chain.l_flavor[0] == 0 and self.new_chain.l_flavor[1] == 2:
                        if self.new_chain.l_charge[0] == self.new_chain.l_charge[2]:
                            return 16
                        else:
                            return 22
                    if self.new_chain.l_flavor[0] == 2 and self.new_chain.l_flavor[1] == 0:
                        if self.new_chain.l_charge[1] == self.new_chain.l_charge[2]:
                            return 17
                        else:
                            return 23
                    if self.new_chain.l_flavor[0] == 2 and self.new_chain.l_flavor[1] == 1:
                        if self.new_chain.l_charge[1] == self.new_chain.l_charge[2]:
                            return 18
                        else:
                            return 24
                    return CATEGORY_FROM_NAME['Other']
            else:
                return CATEGORY_FROM_NAME['Other']

        #All light lepton categories
        elif self.n_tau == 0:
            if self.n_ele == 3:
                return 25
            elif self.n_ele == 0 and self.n_mu == 3:
                return 26
            elif self.n_ele == 2 and self.n_mu == 1:
                if self.hasSSSFpair(0): 
                    if self.new_chain.l_flavor[2] == 1:
                        return 27
                    if self.new_chain.l_flavor[1] == 1:
                        return 28
                    if self.new_chain.l_flavor[0] == 1:
                        return 29
                    return CATEGORY_FROM_NAME['Other']
                elif self.hasOSSFpair(0):            
                    if self.new_chain.l_flavor[2] == 1:
                        return 30
                    if self.new_chain.l_flavor[1] == 1:
                        return 31
                    if self.new_chain.l_flavor[0] == 1:
                        return 32
                    return CATEGORY_FROM_NAME['Other']
            elif self.n_ele == 1 and self.n_mu == 2:
                if self.hasSSSFpair(1): 
                    if self.new_chain.l_flavor[2] == 0:
                        return 33
                    if self.new_chain.l_flavor[1] == 0:
                        return 34
                    if self.new_chain.l_flavor[0] == 0:
                        return 35
                    return CATEGORY_FROM_NAME['Other']
                elif self.hasOSSFpair(1):            
                    if self.new_chain.l_flavor[2] == 0:
                        return 36
                    if self.new_chain.l_flavor[1] == 0:
                        return 37
                    if self.new_chain.l_flavor[0] == 0:
                        return 38
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
        return 39

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
    
   
def returnAnalysisCategory(cat):
    for k in ANALYSIS_CATEGORIES.keys():
        if cat in ANALYSIS_CATEGORIES[k]: return k
    return 39

 
def categoryName(c):
    if c > len(CATEGORY_NAMES):      return 'all'
    return CATEGORY_NAMES[c]

def returnTexName(c, super_cat = False):
    if c > len(CATEGORY_NAMES):      return 'all'
    return CATEGORY_TEX_NAMES[c]

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
