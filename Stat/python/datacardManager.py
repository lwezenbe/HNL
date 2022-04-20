import os

# Make final decision on what mass goes where
def getRegionFromMass(mass):
    if mass <= 80:
        return 'lowMassSRloose'
    else:
        return 'highMassSR'

data_card_base = lambda era, year, selection, mass, flavor : os.path.join(os.path.expandvars('$CMSSW_BASE/src/HNL/Stat/data/dataCards'), era+year, selection+'-'+getRegionFromMass(mass), flavor)


class SingleYearDatacardManager:
    
    def __init__(self, year, era, strategy, flavor, selection):
        self.year = year
        self.era = era
        self.strategy = strategy
        self.flavor = flavor
        self.selection = selection

    def getDatacardPath(self, signal_name, card_name, define_strategy = True):
        return os.path.join(data_card_base(self.era, self.year, self.selection, self.getHNLmass(signal_name), self.flavor), signal_name, 'shapes', self.strategy if define_strategy else '', card_name+'.txt')

    def getHNLmass(self, signal_name):
        return int(signal_name.split('-m')[-1])

    def getCutbasedName(self, sr, final_state):
        return sr+'-'+final_state+'-searchregion'

    def getMVAName(self, sr, final_state, signal_name):
        mass_point = self.getHNLmass(signal_name)
        from HNL.TMVA.mvaVariables import getNameFromMass
        return sr+'-'+final_state+'-'+getNameFromMass(mass_point)+self.flavor
        
    def getStandardDatacardName(self, sr, final_state, signal_name, custom_strategy = None):
        if custom_strategy is None: custom_strategy = self.strategy
        if custom_strategy == 'cutbased':
            return self.getCutbasedName(sr, final_state)
        if custom_strategy == 'MVA':
            return self.getMVAName(sr, final_state, signal_name)
        raise RuntimeError("No known strategy specified in datacardmanager")

    def getStandardDatacardList(self, signal_name, final_state, custom_strategy = None):
        if custom_strategy is None: custom_strategy = self.strategy
        from HNL.EventSelection.searchRegions import SearchRegionManager
        if 'HNL' in signal_name:
            mass_point = self.getHNLmass(signal_name)
            if mass_point <= 80:
                srm = SearchRegionManager(getRegionFromMass(mass_point))
            else:
                srm = SearchRegionManager(getRegionFromMass(mass_point))

        output_list = []
        for search_region in srm.getListOfSearchRegionGroups():
            output_list.append(self.getStandardDatacardName(search_region, final_state, signal_name, custom_strategy))  
        return output_list

    # Highly specified function to be used after all tests
    def getCustomDatacardList(self, signal_name, final_state):
        if 'HNL' in signal_name:
            mass_point = self.getHNLmass(signal_name)
            if mass_point <= 80:
                return [self.getCutbasedName('A1', final_state), self.getCutbasedName('B1', final_state), self.getMVAName('AB2', final_state, signal_name)]
            elif mass_point <= 400:
                return self.getStandardDatacardList(signal_name, final_state, 'MVA')
            else:
                return self.getStandardDatacardList(signal_name, final_state, 'cutbased') 

    def getSingleSignalDatacardList(self, signal_name, final_state):
        if self.strategy == 'custom':
            return self.getCustomDatacardList(signal_name, final_state)
        else:
            return self.getStandardDatacardList(signal_name, final_state)
                 

    def mergeDatacards(self, signal_name, in_card_names, out_card_name, initial_merge = False):
        from HNL.Tools.helpers import makeDirIfNeeded
        makeDirIfNeeded(self.getDatacardPath(signal_name, out_card_name))
        from HNL.Stat.combineTools import runCombineCommand
        runCombineCommand('combineCards.py '+' '.join([self.getDatacardPath(signal_name, ic, define_strategy = not initial_merge) for ic in in_card_names])+' > '+self.getDatacardPath(signal_name, out_card_name))
 
    def initializeCards(self, signal_name, final_state):
        cards_to_merge = self.getSingleSignalDatacardList(signal_name, final_state)
        self.mergeDatacards(signal_name, cards_to_merge, final_state, initial_merge = True)

class DatacardManager:

    def __init__(self, years, era, strategy, flavor, selection):
        self.years = years
        self.era = era
        self.strategy = strategy
        self.flavor = flavor
        self.selection = selection
        self.singleyear_managers = [SingleYearDatacardManager(y, era, strategy, flavor, selection) for y in years]

    def getDatacardPath(self, signal_name, card_name, define_strategy = True):
        return os.path.join(data_card_base(self.era, '-'.join(self.years), self.selection, self.singleyear_managers[0].getHNLmass(signal_name), self.flavor), signal_name, 'shapes', self.strategy if define_strategy else '', card_name+'.txt')
    
    def mergeYears(self, signal_name, card_name):
        if len(self.years) == 1:
            return
        else:
            out_path = self.getDatacardPath(signal_name, card_name)
            from HNL.Tools.helpers import makeDirIfNeeded
            makeDirIfNeeded(out_path)
            from HNL.Stat.combineTools import runCombineCommand
            runCombineCommand('combineCards.py '+' '.join([sm.getDatacardPath(signal_name, card_name) for sm in self.singleyear_managers])+' > '+out_path)

    def prepareAllCards(self, signal_name, final_state):
        for iyear, year in enumerate(self.years):
            self.singleyear_managers[iyear].initializeCards(signal_name, final_state)

        self.mergeYears(signal_name, final_state)

    def checkMassAvailability(self, mass):
        signal_name = 'HNL-'+self.flavor+'-m'+str(mass)
        exists = True
        for iyear, year in enumerate(self.years):
            if not os.path.exists(self.singleyear_managers[iyear].getDatacardPath(signal_name, 'x', define_strategy = False).rsplit('/', 1)[0]): exists = False

        return exists
