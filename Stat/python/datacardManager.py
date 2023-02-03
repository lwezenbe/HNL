import os

# Make final decision on what mass goes where
def getRegionFromMass(mass):
    if mass <= 80:
        return 'lowMassSRloose'
    else:
        return 'highMassSR'

data_card_base = lambda era, year, selection, mass, flavor, dirac_str: os.path.join(os.path.expandvars('$CMSSW_BASE/src/HNL/Stat/data/dataCards'), dirac_str, era+year, selection+'-'+getRegionFromMass(mass), flavor)

forbidden_combinations = {
    'TauEMu' : ['E', 'C', 'D'],
#    'OneTau-OF' : ['E', 'C', 'D'],
#    'OneTau-OSSF': ['F', 'A', 'B'],
#    'OneTau-SSSF': ['E', 'C', 'D']   
}

card_names_dict = {
    'EEE-Mu_MuMuMu-E' : 'NoTau',
    'TauEE_TauEMu_TauMuMu' : 'SingleTau',
    'EEE-Mu_MuMuMu-E_TauEE_TauEMu_TauMuMu' : 'MaxOneTau'
}

def getOutDataCardName(datacards):
    out_data_card_name = '_'.join(sorted(datacards)) 
    if out_data_card_name in card_names_dict.keys(): 
        out_data_card_name = card_names_dict[out_data_card_name] 
    return out_data_card_name

class SingleYearDatacardManager:
    
    def __init__(self, year, era, strategy, flavor, selection, masstype = 'Majorana'):
        self.year = year
        self.era = era
        self.strategy = strategy
        self.flavor = flavor
        self.selection = selection
        self.masstype = masstype

    def getDatacardPath(self, signal_name, card_name, define_strategy = True):
        from HNL.Stat.combineTools import displaced_mass_threshold
        return os.path.join(data_card_base(self.era, self.year, self.selection, self.getHNLmass(signal_name), self.flavor, self.masstype), signal_name, 'shapes', self.strategy if define_strategy else '', card_name+'.txt')

    def getHNLmass(self, signal_name):
        from HNL.Samples.sample import Sample
        return Sample.getSignalMass(signal_name)

    def getCutbasedName(self, sr, final_state):
        return sr+'-'+final_state+'-searchregion'

    def getMVAName(self, sr, final_state, signal_name, custom_mva=None):
        mass_point = self.getHNLmass(signal_name)
        from HNL.TMVA.mvaVariables import getNameFromMass
        from HNL.EventSelection.eventCategorization import getAllAnalysisCategoriesFromSuper
        mva_name = getNameFromMass(mass_point) if custom_mva is None else custom_mva

        if self.flavor != 'tau':
            return sr+'-'+final_state+'-'+mva_name+self.flavor
        elif final_state == 'NoTau' or final_state in ['TauEE', 'TauEMu', 'TauMuMu']:
            return sr+'-'+final_state+'-'+mva_name+'taulep'
        else:
            return sr+'-'+final_state+'-'+mva_name+'tauhad'
        
    def getStandardDatacardName(self, sr, final_state, signal_name, custom_strategy = None, sub_strategy = None):
        if custom_strategy is None: custom_strategy = self.strategy
        if custom_strategy == 'cutbased':
            return self.getCutbasedName(sr, final_state)
        if custom_strategy == 'MVA':
            return self.getMVAName(sr, final_state, signal_name, sub_strategy)
        raise RuntimeError("No known strategy specified in datacardmanager")

    def getStandardDatacardList(self, signal_name, final_state, custom_strategy = None, sub_strategy = None):
        if custom_strategy is None: custom_strategy = self.strategy
        from HNL.EventSelection.searchRegions import SearchRegionManager
        if 'HNL' in signal_name:
            if sub_strategy is None: 
                mass_point = self.getHNLmass(signal_name)
                region = getRegionFromMass(mass_point)
            else:
                if 'low' in sub_strategy:
                    region = getRegionFromMass(20)
                else:
                    region = getRegionFromMass(800)
                
            srm = SearchRegionManager(region)

        output_list = []
        for search_region in srm.getListOfSearchRegionGroups():
            if final_state in forbidden_combinations.keys() and search_region in forbidden_combinations[final_state]: continue
            output_list.append(self.getStandardDatacardName(search_region, final_state, signal_name, custom_strategy, sub_strategy))  
        return output_list

    # Highly specified function to be used after all tests
    def getCustomDatacardList(self, signal_name, final_state, strategy):
        if 'HNL' in signal_name:
            if 'custom' in strategy or 'MVA' in strategy:
                tmp_split = strategy.split('-')
                if len(tmp_split) == 2:
                    strategy = tmp_split[0]
                    sub_strategy = tmp_split[1]
                else:
                    sub_strategy = None
            else:
                sub_strategy = None

            print strategy, sub_strategy
            if strategy == 'custom':
                mass_point = self.getHNLmass(signal_name)
                if mass_point <= 80:
                    if final_state != 'TauEMu':
                        return [self.getCutbasedName('A', final_state), self.getCutbasedName('B', final_state), self.getMVAName('C', final_state, signal_name, sub_strategy), self.getMVAName('D', final_state, signal_name, sub_strategy)]
                    else:
                        return [self.getCutbasedName('A', final_state), self.getCutbasedName('B', final_state)]
                elif mass_point <= 400 and not 'tau' in signal_name:
                    return self.getStandardDatacardList(signal_name, final_state, 'MVA', sub_strategy)
                else:
                    return self.getStandardDatacardList(signal_name, final_state, 'cutbased') 
            elif strategy == 'cutbased':
                return self.getStandardDatacardList(signal_name, final_state, 'cutbased')
            elif strategy == 'MVA':
                return self.getStandardDatacardList(signal_name, final_state, 'MVA', sub_strategy)
            elif strategy == 'combinedSR':
                mass_point = self.getHNLmass(signal_name)
                if mass_point <= 80:
                    return self.getCustomDatacardList(signal_name, final_state, 'custom')
                else:
                    print 'here', self.getMVAName('Combined', final_state, signal_name)
                    return [self.getMVAName('Combined', final_state, signal_name)]
                

    def getSignalDatacardList(self, signal_name, final_states, strategy):
        total_list = []
        for fs in final_states:
            total_list.extend(self.getCustomDatacardList(signal_name, fs, strategy))
        return total_list
                 

    def mergeDatacards(self, signal_name, in_card_names, out_card_name, initial_merge = False):
        from HNL.Tools.helpers import makeDirIfNeeded
        makeDirIfNeeded(self.getDatacardPath(signal_name, out_card_name))
        from HNL.Stat.combineTools import runCombineCommand
        print 'combineCards.py '+' '.join([self.getDatacardPath(signal_name, ic, define_strategy = not initial_merge) for ic in in_card_names])+' > '+self.getDatacardPath(signal_name, out_card_name)
        runCombineCommand('combineCards.py '+' '.join([self.getDatacardPath(signal_name, ic, define_strategy = not initial_merge) for ic in in_card_names])+' > '+self.getDatacardPath(signal_name, out_card_name))
 
    def initializeCards(self, signal_name, final_states, strategy = 'custom'):
        cards_to_merge = self.getSignalDatacardList(signal_name, final_states, strategy)
        self.mergeDatacards(signal_name, cards_to_merge, getOutDataCardName(final_states), initial_merge = True)

class DatacardManager:

    def __init__(self, years, era, strategy, flavor, selection, masstype = 'Majorana'):
        self.years = years
        self.era = era
        self.strategy = strategy
        self.flavor = flavor
        self.selection = selection
        self.singleyear_managers = [SingleYearDatacardManager(y, era, strategy, flavor, selection, masstype) for y in years]
        self.masstype = masstype

    def getDatacardPath(self, signal_name, card_name, define_strategy = True):
        from HNL.Stat.combineTools import displaced_mass_threshold
        return os.path.join(data_card_base(self.era, '-'.join(sorted(self.years)), self.selection, self.singleyear_managers[0].getHNLmass(signal_name), self.flavor, self.masstype), signal_name, 'shapes', self.strategy if define_strategy else '', card_name+'.txt')
    
    def mergeYears(self, signal_name, card_name):
        if len(self.years) == 1:
            return
        else:
            out_path = self.getDatacardPath(signal_name, card_name)
            from HNL.Tools.helpers import makeDirIfNeeded
            makeDirIfNeeded(out_path)
            from HNL.Stat.combineTools import runCombineCommand
            runCombineCommand('combineCards.py '+' '.join([sm.getDatacardPath(signal_name, card_name) for sm in self.singleyear_managers])+' > '+out_path)

    def prepareAllCards(self, signal_name, final_states, strategy = 'cutbased'):
        for iyear, year in enumerate(self.years):
            self.singleyear_managers[iyear].initializeCards(signal_name, final_states, strategy)

        self.mergeYears(signal_name, getOutDataCardName(final_states))

    def checkMassAvailability(self, signal_name):
        exists = True
        for iyear, year in enumerate(self.years):
            if not os.path.exists(self.singleyear_managers[iyear].getDatacardPath(signal_name, 'x', define_strategy = False).rsplit('/', 1)[0]): exists = False

        return exists
