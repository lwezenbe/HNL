#
# Class to match signal leptons
#

from HNL.Tools.helpers import deltaR
PDG_DICT = {0: 11, 1:13, 2:15} 
def getSortKey(item):
    return item[1]

class SignalLeptonMatcher:

    def __init__(self, chain):
        self.c = chain
        self.l1 = None
        self.l2 = None
        self.l3 = None  
        self.m = chain.HNLmass
        self.used_lheparticles = []

    def lheParticleHistory(self, index):
        history = [abs(self.c._lhePdgId[index])]
        while self.c._lheMother1[index] != -1:
            index = self.c._lheMother1[index]
            history.append(abs(self.c._lhePdgId[index]))
        return history


    def matchLheParticle(self, l):
        tmp_match = None
        min_dr = 0.3
        for i in xrange(self.c._nLheParticles):
            #Avoid double matching
            if i in self.used_lheparticles:     continue
            
            #Check if the flavor of the gen lepton corresponds to the pdg id of the lhe particle that we checking as potential match
            if abs(self.c._lhePdgId[i]) != PDG_DICT[self.c._gen_lFlavor[l]]: continue

            #Check for geometric match
            dr = deltaR(self.c._gen_lEta[l], self.c._lheEta[i], self.c._gen_lPhi[l], self.c._lhePhi[i])
            if dr < min_dr:
                tmp_match = i
                min_dr = dr

        self.used_lheparticles.append(tmp_match)
        return tmp_match


    def matchSelectedLeptons(self):
        selected_leptons = [self.c.l1, self.c.l2, self.c.l3]
        match_dict = {}
        l2l3 = []

        for l in selected_leptons:
            match_dict[l] = self.matchLheParticle(l)
            if match_dict[l] is None:   return                  #In case a lepton wasnt matched, return and the self.l will stay None which will cause the event to be skipped
            history = self.lheParticleHistory(match_dict[l])
            if not 9900012 in history:     
                self.l1 = l
            else:
                l2l3.append([l, match_dict[l]])
   
        #At this point, there are slight problems to match l2 and l3, if the W, Z or H from HNL decay is off-shell, it is not stored as lhe particle
        #However, I noticed that the indices of the lhe particles are ordered in a way that l2 is stored before l3
        #TODO: Check if this is correct. Update: Checked, not true in all cases, this needs to be changed

        #If HNL mass is lower than 80 GeV, the second W is off-shell and it becomes hard to rank the two
        if self.m < 80:
            #If same flavor, it becomes hard to distinguish the two entirely as it might either come from a Z or a W, in this case, rank by pt
            if self.c._gen_lFlavor[l2l3[0][0]] == self.c._gen_lFlavor[l2l3[1][0]]:
                self.l2 = l2l3[0][0]
                self.l3 = l2l3[1][0]
            #If opposite flavor, favor the lepton with same flavor as l1 TODO: Will give unwanted effects for mixed coupling, patch this
            else:
                for i, entry in enumerate(l2l3):
                    if self.c._gen_lFlavor[entry[0]] == self.c._gen_lFlavor[self.l1]:
                        self.l2 = entry[0]
                        self.l3 = l2l3[1-i][0]
                if self.l2 is None:
                    self.l2 = l2l3[0][0]
                    self.l3 = l2l3[1][0]
        #If HNL mass is higher than W mass, first boson needs to be off-shell to make higher mass HNL
        elif self.m > 80:
            for i, entry in enumerate(l2l3):
                history = self.lheParticleHistory(entry[1])
                if 24 in history:
                    self.l3 = entry[0]
                    self.l2 = l2l3[1-i][0]
                    break
            #If not filled, there was an intermediate Z or H
            if self.l2 is None:
                self.l2 = l2l3[0][0]
                self.l3 = l2l3[1][0]

        #If HNL mass is 80: Sometimes both W are in there, sometimes not
        else:
            for i, entry in enumerate(l2l3):
                history = self.lheParticleHistory(entry[1])
                if history.count(24) > 1:
                    self.l3 = entry[0]
                    self.l2 = l2l3[1-i][0]
            #If not filled, there was an intermediate Z or H or second W was off-shell
            if self.l2 is None:
                self.l2 = l2l3[0][0]
                self.l3 = l2l3[1][0]
            
            
        #print 'l1 ', self.l1, self.lheParticleHistory(match_dict[self.l1])
        ##l2l3 = sorted(l2l3, key = getSortKey)
        #print 'l2 ', self.l2, self.lheParticleHistory(match_dict[self.l2])
        #print 'l3 ', self.l3, self.lheParticleHistory(match_dict[self.l3])

        ##TODO: implement checks for when on-shell W,Z and H
        #print  (self.c.l1, self.c.l2, self.c.l3), (self.l1, self.l2, self.l3)
        
    def saveNewOrder(self):
        self.matchSelectedLeptons()
        if self.l1 is None: return False
        if self.l2 is None: return False
        if self.l3 is None: return False

        self.c.l1 = self.l1
        self.c.l2 = self.l2
        self.c.l3 = self.l3
        for i, l in enumerate([self.l1, self.l2, self.l3]):
            self.c.l_pt[i] = self.c._gen_lPt[l] 
            self.c.l_eta[i] = self.c._gen_lEta[l]
            self.c.l_phi[i] = self.c._gen_lPhi[l]
            self.c.l_e[i] = self.c._gen_lE[l]
            self.c.l_charge[i] = self.c._gen_lCharge[l]
            self.c.l_flavor[i] = self.c._gen_lFlavor[l]
        
        return True
    
    
    
    
