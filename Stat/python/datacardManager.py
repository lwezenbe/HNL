import os

# Make final decision on what mass goes where
def getRegionFromMass(mass):
    if mass <= 80:
        return 'lowMassSRloose'
    else:
        return 'highMassSR'

data_card_base = lambda era, year, selection, mass, flavor, dirac_str: os.path.join(os.path.expandvars('$CMSSW_BASE/src/HNL/Stat/data/dataCards'), dirac_str, era+year, selection+'-'+getRegionFromMass(mass), flavor)

combined_final_states = {
    'MaxOneTau' : ['NoTau', 'SingleTau']
}

class SingleYearDatacardManager:
    
    def __init__(self, year, era, strategy, flavor, selection, masstype = 'Majorana', tag = 'prompt'):
        self.year = year
        self.era = era
        self.strategy = strategy
        self.flavor = flavor
        self.selection = selection
        self.masstype = masstype
        self.tag = tag

    def getDatacardPath(self, signal_name, card_name, coupling_sq, define_strategy = True):
        from HNL.Stat.combineTools import displaced_mass_threshold
        if self.tag == 'displaced':
            tag_to_use = 'prompt' if self.getHNLmass(signal_name) > displaced_mass_threshold else 'displaced'
        else:
            tag_to_use = self.tag
        return os.path.join(data_card_base(self.era, self.year, self.selection, self.getHNLmass(signal_name), self.flavor, self.masstype), signal_name, tag_to_use+'-{:.2e}'.format(coupling_sq), 'shapes', self.strategy if define_strategy else '', card_name+'.txt')

    def getHNLmass(self, signal_name):
        return int(signal_name.split('-m')[-1])

    def getCutbasedName(self, sr, final_state):
        return sr+'-'+final_state+'-searchregion'

    def getMVAName(self, sr, final_state, signal_name):
        mass_point = self.getHNLmass(signal_name)
        from HNL.TMVA.mvaVariables import getNameFromMass
        from HNL.EventSelection.eventCategorization import getAllAnalysisCategoriesFromSuper
        if self.flavor != 'tau':
            return sr+'-'+final_state+'-'+getNameFromMass(mass_point)+self.flavor
        elif final_state == 'NoTau' or final_state in getAllAnalysisCategoriesFromSuper('NoTau'):
            return sr+'-'+final_state+'-'+getNameFromMass(mass_point)+'taulep'
        else:
            return sr+'-'+final_state+'-'+getNameFromMass(mass_point)+'tauhad'
        
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
    def getCustomDatacardList(self, signal_name, final_state, lod, strategy):
        if lod == 'analysis':
            from HNL.EventSelection.eventCategorization import getAllAnalysisCategoriesFromSuper
            all_cat = getAllAnalysisCategoriesFromSuper(final_state)
            out_cards = []
            for c in all_cat:
                out_cards.extend(self.getCustomDatacardList(signal_name, c, 'super', strategy))
            return out_cards
        elif lod == 'super':
            if 'HNL' in signal_name:
                if strategy == 'custom':
                    mass_point = self.getHNLmass(signal_name)
                    if mass_point <= 80:
                        if final_state == 'OneTau-OSSF':
                            return [self.getMVAName('C', final_state, signal_name), self.getMVAName('D', final_state, signal_name)]
                        elif final_state == 'OneTau-OF' or final_state == 'OneTau-SSSF':
                            return [self.getCutbasedName('A', final_state), self.getCutbasedName('B', final_state)]
                        else:
                            return [self.getCutbasedName('A', final_state), self.getCutbasedName('B', final_state), self.getMVAName('C', final_state, signal_name), self.getMVAName('D', final_state, signal_name)]
                    elif mass_point <= 400:
                        return self.getStandardDatacardList(signal_name, final_state, 'MVA')
                    else:
                        return self.getStandardDatacardList(signal_name, final_state, 'cutbased') 
                elif strategy == 'cutbased':
                    return self.getStandardDatacardList(signal_name, final_state, 'cutbased')
                elif strategy == 'MVA':
                    return self.getStandardDatacardList(signal_name, final_state, 'MVA')
        else:
            raise RuntimeError('Unknown lod: {0}'.format(lod))

    def getSingleSignalDatacardList(self, signal_name, final_state, lod, strategy):
        if final_state in combined_final_states.keys():
            total_list = []
            for fs in combined_final_states[final_state]:
                total_list.extend(self.getSingleSignalDatacardList(signal_name, fs, lod, strategy))
            return total_list
        else:
            return self.getCustomDatacardList(signal_name, final_state, lod, strategy)
                 

    def mergeDatacards(self, signal_name, coupling_sq, in_card_names, out_card_name, initial_merge = False):
        from HNL.Tools.helpers import makeDirIfNeeded
        makeDirIfNeeded(self.getDatacardPath(signal_name, out_card_name, coupling_sq))
        from HNL.Stat.combineTools import runCombineCommand
        runCombineCommand('combineCards.py '+' '.join([self.getDatacardPath(signal_name, ic, coupling_sq, define_strategy = not initial_merge) for ic in in_card_names])+' > '+self.getDatacardPath(signal_name, out_card_name, coupling_sq))
 
    def initializeCards(self, signal_name, coupling_sq, final_state, lod, strategy = 'custom'):
        cards_to_merge = self.getSingleSignalDatacardList(signal_name, final_state, lod, strategy)
        self.mergeDatacards(signal_name, coupling_sq, cards_to_merge, final_state, initial_merge = True)

class DatacardManager:

    def __init__(self, years, era, strategy, flavor, selection, masstype = 'Majorana', tag = 'prompt'):
        self.years = years
        self.era = era
        self.strategy = strategy
        self.flavor = flavor
        self.selection = selection
        self.tag = tag
        self.singleyear_managers = [SingleYearDatacardManager(y, era, strategy, flavor, selection, masstype, tag) for y in years]
        self.masstype = masstype

    def getDatacardPath(self, signal_name, card_name, coupling_sq, define_strategy = True):
        from HNL.Stat.combineTools import displaced_mass_threshold
        if self.tag == 'displaced':
            tag_to_use = 'prompt' if self.singleyear_managers[0].getHNLmass(signal_name) > displaced_mass_threshold else 'displaced'
        else:
            tag_to_use = self.tag
        return os.path.join(data_card_base(self.era, '-'.join(self.years), self.selection, self.singleyear_managers[0].getHNLmass(signal_name), self.flavor, self.masstype), signal_name, tag_to_use+'-{:.2e}'.format(coupling_sq), 'shapes', self.strategy if define_strategy else '', card_name+'.txt')
    
    def mergeYears(self, signal_name, coupling_sq, card_name):
        if len(self.years) == 1:
            return
        else:
            out_path = self.getDatacardPath(signal_name, card_name, coupling_sq)
            from HNL.Tools.helpers import makeDirIfNeeded
            makeDirIfNeeded(out_path)
            from HNL.Stat.combineTools import runCombineCommand
            runCombineCommand('combineCards.py '+' '.join([sm.getDatacardPath(signal_name, card_name, coupling_sq) for sm in self.singleyear_managers])+' > '+out_path)

    def prepareAllCards(self, signal_name, coupling_sq, final_state, lod, strategy = 'cutbased'):
        for iyear, year in enumerate(self.years):
            self.singleyear_managers[iyear].initializeCards(signal_name, final_state, coupling_sq, lod, strategy)

        self.mergeYears(signal_name, coupling_sq, final_state)

    def checkMassAvailability(self, mass, coupling):
        signal_name = 'HNL-'+self.flavor+'-m'+str(mass)
        exists = True
        for iyear, year in enumerate(self.years):
            if not os.path.exists(self.singleyear_managers[iyear].getDatacardPath(signal_name, 'x', coupling, define_strategy = False).rsplit('/', 1)[0]): exists = False

        return exists
