
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
# 4: l1 and l2 SS ele, l3 any lepton (N to W decay)
# 5: l1, l2 OS ele, l3 any lepton (N to W decay)
# 6: l1 ele, l2l3 OSSF pair (N to Z decay)
# 7: l1 and l2 SS mu, l3 any lepton (N to W decay)
# 8: l1, l2 OS mu, l3 any lepton (N to W decay)
# 9: l1 mu, l2l3 OSSF pair (N to Z decay)
# 10: everything else
#
# subcategories show what the remaining lepton(s) are (l3 when N to W decay and l2l3 in case of N to Z)
# 1: tau
# 2: ele
# 3: mu

CATEGORIES = []
CATEGORY_NAMES = {}
for i in xrange(1, 11, 1):
    for j in xrange(1, 5, 1):
        CATEGORIES.append((i, j))
    CATEGORY_NAMES[i] = 'category-'+str(i)

SUBCATEGORY_NAMES = {1 : 'tau', 2 : 'ele', 3 : 'mu', 4 : 'all'}

CATEGORY_TEX_NAMES = {1: '#tau^{#pm}#tau^{#pm}',
                        2: '#tau^{#pm}#tau^{#mp}',
                        3: '#tau',
                        4: 'e^{#pm}e^{#pm}',
                        5: 'e^{#pm}e^{#mp}',
                        6: 'e',
                        7: '#mu^{#pm}#mu^{#pm}',
                        8: '#mu^{#pm}#mu^{#mp}',
                        9: '#mu',
                        10: 'll'
}

SUBCATEGORY_TEX_NAMES = {1 : '#tau', 2 : 'e', 3 : '#mu', 4 : 'l'}


class EventCategory():
    
    def __init__(self, chain):
        self.chain = chain
        self.n_mu = 0
        self.n_ele = 0
        self.n_tau = 0
        self.category = None
        self.sub_category = None
        self.categories = CATEGORIES

    def flavorContent(self):
        for f in self.chain.l_flavor:
            if f == 0:  self.n_ele += 1
            elif f == 1:  self.n_mu += 1
            elif f == 2:  self.n_tau += 1

    def determineCategory(self):
        #Category 1 and 2:
        if self.chain.l_flavor[l1] == 2 and self.chain.l_flavor[l2] == 2:
            #Category 1:
            if self.chain.l_charge[l1] == self.chain.l_charge[l2]:
                self.category = 1
            #Category 2:
            else:
                self.category = 2

        #Category 3:
        elif self.chain.l_flavor[l1] == 2:
            if self.chain.l_flavor[l2] == self.chain.l_flavor[l3] and self.chain.l_charge[l2] != self.chain.l_charge[l3]:
                self.category = 3
            else:
                self.category = 10

        #Category 4 and 5:
        elif self.chain.l_flavor[l1] == 0 and self.chain.l_flavor[l2] == 0:
            #Category 4:
            if self.chain.l_charge[l1] == self.chain.l_charge[l2]:
                self.category = 4
            #Category 5:
            else:
                self.category = 5

        #Category 6:
        elif self.chain.l_flavor[l1] == 0:
            if self.chain.l_flavor[l2] == self.chain.l_flavor[l3] and self.chain.l_charge[l2] != self.chain.l_charge[l3]:
                self.category = 6
            else:
                self.category = 10

        #Category 7 and 8:
        elif self.chain.l_flavor[l1] == 1 and self.chain.l_flavor[l2] == 1:
            #Category 7:
            if self.chain.l_charge[l1] == self.chain.l_charge[l2]:
                self.category = 7
            #Category 8:
            else:
                self.category = 8

        #Category 9:
        elif self.chain.l_flavor[l1] == 1:
            if self.chain.l_flavor[l2] == self.chain.l_flavor[l3] and self.chain.l_charge[l2] != self.chain.l_charge[l3]:
                self.category = 9
            else:
                self.category = 10

        else:
            self.category = 10

    def determineSubCategory(self):
        if self.chain.l_flavor[l3] == 2:
            self.sub_category = 1 
        elif self.chain.l_flavor[l3] == 0:
            self.sub_category = 2 
        elif self.chain.l_flavor[l3] == 1:
            self.sub_category = 3 
        else:
            print "No subcategory assigned"
            self.sub_category = 4   
 
    def returnCategory(self):
        self.determineCategory()
        self.determineSubCategory()
        return self.category, self.sub_category

def categoryName(c):
    return CATEGORY_NAMES[c[0]]

def subcategoryName(c):
    return SUBCATEGORY_NAMES[c[1]]

def returnTexName(c):
    name = CATEGORY_TEX_NAMES[c[0]]
    name += SUBCATEGORY_TEX_NAMES[c[1]]
    if c[0] % 3 == 0:
        name += SUBCATEGORY_TEX_NAMES[c[1]]
    return name 
 
            
