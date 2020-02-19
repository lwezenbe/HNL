
#
# Class that keeps track of the correct event category
#

l1 = 0
l2 = 1
l3 = 2

#
# Structure of Categorization
# Categories according to l1 and l2
# 1: l1 and l2 SS tau, l3 any lepton (N to W decay)
# 2: l1, l2 OS tau, l3 any lepton (N to W decay)
# 3: l1 tau, l2l3 OSSF pair (N to Z decay)
# 4: l2 tau, l1l3 SSSF pair (second tau to lepton decay)
# 5: eee
# 6: mumumu
# 7: eemu
# 8: emumu    
#
# subcategories show what the remaining lepton(s) are (l3 when N to W decay and l2l3 in case of N to Z)
# 1: tau
# 2: ele
# 3: mu

SUPER_CATEGORY_NAMES = {1: 'TauTauEle', 2: 'TauTauMu', 3 : 'TauEleEle', 4: 'TauEleMu', 5: 'TauMuMu'}
CATEGORY_NAMES = {1: 'SSTau', 2: 'OSTau', 3: 'SingleTau+OS-l', 4: 'SingleTau+SS-l', 5: 'eee', 6: 'mumumu', 7: 'eemu', 8: 'emumu'}
CATEGORY_SUBCATEGORY_LINK = {1: 'DoubleTau', 2: 'DoubleTau', 3: 'SingleTau', 4: 'SingleTau', 5: 'NoTau', 6: 'NoTau', 7: 'NoTau', 8: 'NoTau', 9: 'SingleTau'}
SUBCATEGORY_NAMES = {'DoubleTau' : {1: 'e', 2: 'mu', 3: 'tau'},
                    'SingleTau' : {1: 'ee', 2: 'emu', 3:'mue', 4:'mumu'}, 
                    'NoTau':    {1: 'All'}}

CATEGORIES = []
SUPER_CATEGORIES = [c for c in xrange(1, len(SUPER_CATEGORY_NAMES)+2, 1)]
#len(names) + 2 to add an extra bin where everything else goes
for i in xrange(1, len(CATEGORY_NAMES) + 2, 1):
    for j in xrange(1, len(SUBCATEGORY_NAMES[CATEGORY_SUBCATEGORY_LINK[i]]) + 2, 1):
        CATEGORIES.append((i, j))


CATEGORY_TEX_NAMES = {
                       # 1: '#tau^{#pm}#tau^{#pm}',
                       # 2: '#tau^{#pm}#tau^{#mp}',
                        1: '#tau#tau',
                        2: '#tau#tau',
                        3: '#tau',
                        4: '#tau',
                        5: 'eee',
                        6: '#mu#mu#mu',
                        7: 'ee#mu',
                        8: 'e#mu#mu'
}

SUBCATEGORY_TEX_NAMES = {'DoubleTau' : {1: 'e', 2: '#mu', 3: '#tau'},
                    'SingleTau' : {1: 'ee', 2: 'e#mu', 3:'#mu e', 4:'#mu#mu'},
                    'NoTau' : {1: ''}}

SUPERCATEGORY_TEX_NAMES = {1: '#tau#tau e', 2: '#tau#tau#mu', 3 : '#tau e e', 4: '#tau e #mu', 5: '#tau#mu#mu'}

class EventCategory():
    
    def __init__(self, chain):
        self.chain = chain
        self.n_mu = 0
        self.n_ele = 0
        self.n_tau = 0
        self.super_category = None
        self.category = None
        self.sub_category = None
        self.categories = CATEGORIES
        self.super_categories = SUPER_CATEGORIES

    def flavorContent(self):

        self.n_mu = 0
        self.n_ele = 0
        self.n_tau = 0
        
        for f in self.chain.l_flavor:
            if f == 0:  self.n_ele += 1
            elif f == 1:  self.n_mu += 1
            elif f == 2:  self.n_tau += 1

    def determineCategory(self):
        self.flavorContent()
        #Category 1 and 2:
        if self.n_tau >= 2: 
            if self.chain.l_flavor[l1] == 2 and self.chain.l_flavor[l2] == 2:
                #Category 1:
                if self.chain.l_charge[l1] == self.chain.l_charge[l2]:
                    self.category = 1
                #Category 2:
                else:
                    self.category = 2
            else:
                self.category = len(CATEGORY_NAMES) + 1

        #Category 3 and 4:
        elif self.n_tau == 1:
            #Category 3
            if self.chain.l_flavor[l1] == 2:
                if self.chain.l_charge[l2] != self.chain.l_charge[l3]:
                    self.category = 3
                else:
                    self.category = len(CATEGORY_NAMES) + 1
                
            #Category 4:
            elif self.chain.l_flavor[l2] == 2:
                if self.chain.l_charge[l1] == self.chain.l_charge[l3]:
                    self.category = 4
                else:
                    self.category = len(CATEGORY_NAMES) + 1 
            
            else:
                self.category = len(CATEGORY_NAMES) + 1

        #All light lepton categories
        elif self.n_tau == 0:
            if self.n_ele == 3:
                self.category = 5
            elif self.n_ele == 0 and self.n_mu == 3:
                self.category = 6
            elif self.n_ele == 2 and self.n_mu == 1:
                self.category = 7
            elif self.n_ele == 1 and self.n_mu == 2:
                self.category = 8

        else:
            self.category = len(CATEGORY_NAMES) + 1


    def determineSubCategory(self):
        #Double Tau
        if CATEGORY_SUBCATEGORY_LINK[self.category] == 'DoubleTau':
            if self.chain.l_flavor[l3] == 0:
                self.sub_category = 1 
            elif self.chain.l_flavor[l3] == 1:
                self.sub_category = 2 
            elif self.chain.l_flavor[l3] == 2:
                self.sub_category = 3 
        elif CATEGORY_SUBCATEGORY_LINK[self.category] == 'SingleTau':
            flavs = [self.chain.l_flavor[i] for i in xrange(3) if self.chain.l_flavor[i] != 2]
            if len(flavs) != 2: 
                self.sub_category = len(SUBCATEGORY_NAMES[CATEGORY_SUBCATEGORY_LINK[self.category]]) + 1
            elif flavs[0] == 0 and flavs[1] == 0:
                self.sub_category = 1
            elif flavs[0] == 0 and flavs[1] == 1:
                self.sub_category = 2
            elif flavs[0] == 1 and flavs[1] == 0:
                self.sub_category = 3
            elif flavs[0] == 1 and flavs[1] == 1:
                self.sub_category = 4
        elif CATEGORY_SUBCATEGORY_LINK[self.category] == 'SingleTau':
            self.sub_category = 1
        else:
#            print "No subcategory assigned"
            self.sub_category = len(SUBCATEGORY_NAMES[CATEGORY_SUBCATEGORY_LINK[self.category]]) + 1
 
    def returnCategory(self):
        self.determineCategory()
        self.determineSubCategory()
        return self.category, self.sub_category
    
    def returnSuperCategory(self):
        self.flavorContent()
        if self.n_tau == 2:
            if self.n_ele == 1: self.super_category = 1
            elif self.n_mu == 1: self.super_category = 2
        elif self.n_tau == 1:
            if self.n_ele == 2: self.super_category = 3
            elif self.n_ele == 1 and self.n_mu == 1:    self.super_category = 4
            elif self.n_mu ==2: self.super_category = 5
        else:
            self.super_category = len(SUPER_CATEGORY_NAMES) + 1

        return self.super_category

#
# Function mainly used for designing pt cuts, to be able to load the correct cuts to draw text on canvas
# When all cuts are designed, this will no longer be used, or adapted
#
def returnCategoryPtCuts(cat):
    if cat[0] == 1 or cat[0] == 2:
        if cat[1] == 1:       
            return [(None, None, 27), (None, 20, 24), (35, 35, None)]    
        elif cat[1] == 2:       
            return [(None, None, 22), (None, 20, 19), (35, 35, None)]    
        elif cat[1] == 3: 
            return [(35, 35, None)]
        else:
            return [(None, None, None)]
    elif cat[0] == 3:
        if cat[1] == 1:
            return [(None, 23, 12), (20, 24, None), (None, 27, None)]
        elif cat[1] == 2:
            return [(None, None, 22), (20, 24, None), (None, 23, 12), (None, 27, None)]
        elif cat[1] == 3:
            return [(None, 23, 8), (None, 22, None), (20, 19, None), (20, None, 24), (None, None, 27)]
        elif cat[1] == 4:
            return [(None, 17, 8), (20, 19, None), (None, 22, None)]
        else:
            return [(None, None, None)]
    elif cat[0] == 4:
        if cat[1] == 1:
            return [(24, 20, None), (23, None, 12), (27, None, None)]
        elif cat[1] == 2:
            return [(23, None, 12), (24, 20, None), (27, None, None), (None, None, 22)]
        elif cat[1] == 3:
            return [(22, None, None), (23, None, 8), (19, 20, None), (None, None, 27)]
        elif cat[1] == 4:
            return [(17, None, 8), (20, None, 10), (22, None, None), (19, 20, None), (None, None, 22)]
        else:
            return [(None, None, None)]
    
    return [(None, None, None)]
        
#
# Function to return triggers interesting to the specific category
# Used to study triggers
#

def returnCategoryTriggers(chain, cat):
    if cat[0] == 1 or cat[0] == 2:
        if cat[1] == 1:       
            return [chain._HLT_Ele27_WPTight_Gsf, chain._HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20, chain._HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg]    
        elif cat[1] == 2:       
            return [chain._HLT_IsoMu22_eta2p1, chain._HLT_IsoMu19_eta2p1_LooseIsoPFTau20, chain._HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg]    
        elif cat[1] == 3: 
            return [chain._HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg]
        else:
            return [None]
    elif cat[0] == 3:
        if cat[1] == 1:
            return [chain._HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ, chain._HLT_Ele27_WPTight_Gsf, chain._HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20]
        elif cat[1] == 2:
            return [chain._HLT_IsoMu22_eta2p1, chain._HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ, chain._HLT_Ele27_WPTight_Gsf, chain._HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20]
        elif cat[1] == 3:
            return [chain._HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL, chain._HLT_IsoMu22_eta2p1, chain._HLT_Ele27_WPTight_Gsf, chain._HLT_IsoMu19_eta2p1_LooseIsoPFTau20, chain._HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20]
        elif cat[1] == 4:
            return [chain._HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ, chain._HLT_IsoMu22_eta2p1, chain._HLT_IsoMu19_eta2p1_LooseIsoPFTau20]
        else:
            return [None]
    elif cat[0] == 4:
        if cat[1] == 1:
            return [chain._HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ, chain._HLT_Ele27_WPTight_Gsf, chain._HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20]
        elif cat[1] == 2:
            return [chain._HLT_IsoMu22_eta2p1, chain._HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ, chain._HLT_Ele27_WPTight_Gsf, chain._HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20]
        elif cat[1] == 3:
            return [chain._HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL, chain._HLT_IsoMu22_eta2p1, chain._HLT_Ele27_WPTight_Gsf, chain._HLT_IsoMu19_eta2p1_LooseIsoPFTau20, chain._HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20]
        elif cat[1] == 4:
            return [chain._HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ, chain._HLT_IsoMu22_eta2p1, chain._HLT_IsoMu19_eta2p1_LooseIsoPFTau20]
        else:
            return [None]
    
    return [None]
    
def returnCategoryTriggerNames(cat):
    if cat[0] == 1 or cat[0] == 2:
        if cat[1] == 1:
            return ['HLT_Ele27_WPTight_Gsf', 'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20', 'HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg']
        elif cat[1] == 2:
            return ['HLT_IsoMu22_eta2p1', 'HLT_IsoMu19_eta2p1_LooseIsoPFTau20', 'HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg']
        elif cat[1] == 3:
            return ['HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg']
        else:
            return [None]
    elif cat[0] == 3:
        if cat[1] == 1:
            return ['HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ', 'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20', 'HLT_Ele27_WPTight_Gsf']
        elif cat[1] == 2:
            return ['HLT_IsoMu22_eta2p1', 'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20', 'HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ', 'HLT_Ele27_WPTight_Gsf']
        elif cat[1] == 3:
            return ['HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL', 'HLT_IsoMu22_eta2p1', 'HLT_IsoMu19_eta2p1_LooseIsoPFTau20', 'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20', 'HLT_Ele27_WPTight_Gsf']
        elif cat[1] == 4:
            return ['HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ', 'HLT_IsoMu19_eta2p1_LooseIsoPFTau20', 'HLT_IsoMu22_eta2p1']
        else:
            return [None]
    elif cat[0] == 4:
        if cat[1] == 1:
            return ['HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ', 'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20', 'HLT_Ele27_WPTight_Gsf']
        elif cat[1] == 2:
            return ['HLT_IsoMu22_eta2p1', 'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20', 'HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ', 'HLT_Ele27_WPTight_Gsf']
        elif cat[1] == 3:
            return ['HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL', 'HLT_IsoMu22_eta2p1', 'HLT_IsoMu19_eta2p1_LooseIsoPFTau20', 'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20', 'HLT_Ele27_WPTight_Gsf']
        elif cat[1] == 4:
            return ['HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ', 'HLT_IsoMu19_eta2p1_LooseIsoPFTau20', 'HLT_IsoMu22_eta2p1']
        else:
            return [None]

    return [None]

def returnSuperCategoryTriggers(chain, cat):
    if cat == 1:
        return [chain._HLT_Ele27_WPTight_Gsf, chain._HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20, chain._HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg]
    elif cat == 2:        
        return [chain._HLT_IsoMu24, chain._HLT_IsoMu19_eta2p1_LooseIsoPFTau20, chain._HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg]
    elif cat == 3:
        return [chain._HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ, chain._HLT_Ele27_WPTight_Gsf, chain._HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20]
    elif cat == 4:
        return [chain._HLT_IsoMu24, chain._HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ, chain._HLT_Ele27_WPTight_Gsf, chain._HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL, chain._HLT_IsoMu19_eta2p1_LooseIsoPFTau20, chain._HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20]
    elif cat == 5:
        return [chain._HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ, chain._HLT_IsoMu24, chain._HLT_IsoMu19_eta2p1_LooseIsoPFTau20]
    return [None]

def returnSuperCategoryTriggerNames(cat):
    if cat == 1:
        return ['HLT_Ele27_WPTight_Gsf', 'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20', 'HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg']
    elif cat == 2:        
        return ['HLT_IsoMu24', 'HLT_IsoMu19_eta2p1_LooseIsoPFTau20', 'HLT_DoubleMediumCombinedIsoPFTau35_Trk1_eta2p1_Reg']
    elif cat == 3:
        return ['HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ', 'HLT_Ele27_WPTight_Gsf', 'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20']
    elif cat == 4:
        return ['HLT_IsoMu24', 'HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ', 'HLT_Ele27_WPTight_Gsf', 'HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL', 'HLT_IsoMu19_eta2p1_LooseIsoPFTau20', 'HLT_Ele24_eta2p1_WPLoose_Gsf_LooseIsoPFTau20']
    elif cat == 5:
        return ['HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ', 'HLT_IsoMu24', 'HLT_IsoMu19_eta2p1_LooseIsoPFTau20']
    return [None]

def categoryName(c):
    if c[0] > len(CATEGORY_NAMES):      return 'all'
    return CATEGORY_NAMES[c[0]]

def subcategoryName(c):
    if c[1] > len(SUBCATEGORY_NAMES[CATEGORY_SUBCATEGORY_LINK[c[0]]]): return 'all'
    return SUBCATEGORY_NAMES[CATEGORY_SUBCATEGORY_LINK[c[0]]][c[1]]

def returnTexName(c, super_cat = False):
    if isinstance(c, list) or isinstance(c, tuple):
        if c[0] > len(CATEGORY_TEX_NAMES):
            name = 'All'
        else:
            name = CATEGORY_TEX_NAMES[c[0]]
        
        if c[1] <= len(SUBCATEGORY_TEX_NAMES[CATEGORY_SUBCATEGORY_LINK[c[0]]]):
            name += SUBCATEGORY_TEX_NAMES[CATEGORY_SUBCATEGORY_LINK[c[0]]][c[1]]
    else:
        if c > len(SUPERCATEGORY_TEX_NAMES):
            name = 'All'
        else:
            name = SUPERCATEGORY_TEX_NAMES[c]

    return name 
 
            
