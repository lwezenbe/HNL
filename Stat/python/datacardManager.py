import os

# Make final decision on what mass goes where
def getRegionFromMass(mass):
    if mass <= 80:
        return 'lowMassSRloose'
    else:
        return 'highMassSR'

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

def getOutDataCardName(datacards, searchregions = None):
    out_data_card_name = '_'.join(sorted(datacards)) 
    if out_data_card_name in card_names_dict.keys(): 
        out_data_card_name = card_names_dict[out_data_card_name] 
    if searchregions is not None:
        out_data_card_name += '-'+''.join(searchregions)
    return out_data_card_name

class SingleYearDatacardManager:
    
    def __init__(self, year, era, strategy, flavor, selection, regions = None, masstype = 'Majorana', tag = None, search_regions = None):
        self.year = year
        self.era = era
        self.original_strategy = strategy
        self.strategy = strategy
        if 'custom' in strategy or 'MVA' in strategy:
            tmp_split = strategy.split('-')
            if len(tmp_split) == 2:
                self.strategy = tmp_split[0]
                self.sub_strategy = tmp_split[1]
            else:
                self.sub_strategy = None
        else:
            self.sub_strategy = None

        self.flavor = flavor
        self.selection = selection
        self.masstype = masstype
        self.tag = tag
        self.search_regions = search_regions

        self.regions = regions

    def getHNLregion(self, signal_name, region):
        if 'HNL' in signal_name and region is None:
            if self.sub_strategy is None:
                mass_point = self.getHNLmass(signal_name)
                return getRegionFromMass(mass_point)
            else:
                if 'low' in self.sub_strategy:
                    return getRegionFromMass(20)
                else:
                    return getRegionFromMass(800)
        else:
            return region
            

    def getHNLmass(self, signal_name):
        from HNL.Samples.sample import Sample
        return Sample.getSignalMass(signal_name)

    def getDatacardPath(self, signal_name, card_name, region = None, define_strategy = True):
        from HNL.Stat.combineTools import displaced_mass_threshold
        from combineTools import returnDataCardPath
        return returnDataCardPath(self.era, self.year, self.selection, region if region is not None else getRegionFromMass(self.getHNLmass(signal_name)), self.flavor, signal_name, card_name if not define_strategy else self.original_strategy+'/'+card_name, self.masstype, tag = self.tag)

    def getCutbasedName(self, sr, final_state):
        return sr+'-'+final_state+'-searchregion'

    def getMVAName(self, sr, final_state, signal_name, custom_mva=None):
        mass_point = self.getHNLmass(signal_name)
        from HNL.TMVA.mvaVariables import getNameFromMass
        from HNL.EventSelection.eventCategorization import getAllAnalysisCategoriesFromSuper
        mva_name = getNameFromMass(mass_point) if custom_mva is None else custom_mva

        if self.flavor != 'tau':
            return sr+'-'+final_state+'-'+mva_name+self.flavor
        elif final_state == 'NoTau' or final_state not in ['TauEE', 'TauEMu', 'TauMuMu']:
            return sr+'-'+final_state+'-'+mva_name+'taulep'
        else:
            return sr+'-'+final_state+'-'+mva_name+'tauhad'
        
    def getStandardDatacardName(self, sr, final_state, signal_name, strategy, sub_strategy = None):
        if strategy == 'cutbased':
            return self.getCutbasedName(sr, final_state)
        if strategy == 'MVA':
            return self.getMVAName(sr, final_state, signal_name, sub_strategy)
        raise RuntimeError("No known strategy specified in datacardmanager")

    def getStandardDatacardList(self, signal_name, final_state, region, strategy, sub_strategy = None):
        from HNL.EventSelection.searchRegions import SearchRegionManager
        if 'HNL' in signal_name:
            srm = SearchRegionManager(region)

        output_list = []
        for search_region in srm.getListOfSearchRegionGroups():
            if self.search_regions is not None and search_region not in self.search_regions: continue

            if final_state in forbidden_combinations.keys() and search_region in forbidden_combinations[final_state]: continue
            output_list.append(self.getStandardDatacardName(search_region, final_state, signal_name, strategy, sub_strategy))  
        return output_list

    # Highly specified function to be used after all tests
    def getCustomDatacardList(self, signal_name, final_state, region):
        if 'HNL' in signal_name:
            mass_point = self.getHNLmass(signal_name)

            #Cross usage
            if (region == 'highMassSR' and mass_point <= 80) or (region == 'lowMassSRloose' and mass_point > 80):
                strategy_to_use = 'cutbased'
            else:
                strategy_to_use = self.strategy

            if strategy_to_use == 'custom':
                if mass_point <= 80:
                    if final_state != 'TauEMu':
                        return [self.getCutbasedName('A', final_state), self.getCutbasedName('B', final_state), self.getMVAName('C', final_state, signal_name, self.sub_strategy), self.getMVAName('D', final_state, signal_name, self.sub_strategy)]
                    else:
                        return [self.getCutbasedName('A', final_state), self.getCutbasedName('B', final_state)]
                elif mass_point <= 400 and not 'tau' in signal_name:
                    return self.getStandardDatacardList(signal_name, final_state, region, 'MVA', self.sub_strategy)
                else:
                    return self.getStandardDatacardList(signal_name, final_state, region, 'cutbased') 
            elif strategy_to_use == 'cutbased':
                return self.getStandardDatacardList(signal_name, final_state, region, 'cutbased')
            elif strategy_to_use == 'MVA':
                return self.getStandardDatacardList(signal_name, final_state, region, 'MVA', self.sub_strategy)
            elif strategy_to_use == 'combinedSR':
                if mass_point <= 80:
                    return self.getCustomDatacardList(signal_name, final_state, region, 'custom')
                else:
                    return [self.getMVAName('Combined', final_state, signal_name)]
            elif strategy_to_use == 'singlecard':
                return [self.getCutbasedName('All', final_state)]
                

    def getSignalDatacardList(self, signal_name, final_states, region):
        total_list = []
        for fs in final_states:
            print self.getCustomDatacardList(signal_name, fs, region)
            total_list.extend(self.getCustomDatacardList(signal_name, fs, region))
        print total_list
        return total_list
                 

    def mergeDatacards(self, signal_name, in_card_names, out_card_name):
        from HNL.Tools.helpers import makeDirIfNeeded
        makeDirIfNeeded(out_card_name)
        from HNL.Stat.combineTools import runCombineCommand
        runCombineCommand('combineCards.py '+' '.join(in_card_names)+' > '+out_card_name)

    def combineRegionNames(self, signal_name):
        if self.regions is None:
            return self.getHNLregion(signal_name, None)
        else:
            return '-'.join(sorted(self.regions))
 
    def initializeCards(self, signal_name, final_states):
        in_card_names = []
        if self.regions is None:
            print 'A'
            cards_to_merge = self.getSignalDatacardList(signal_name, final_states, self.getHNLregion(signal_name, None))
            in_card_names = [self.getDatacardPath(signal_name, ic, define_strategy = False, region = self.getHNLregion(signal_name, None)) for ic in cards_to_merge]
        else:
            print 'B'
            for region in self.regions:
                cards_to_merge = self.getSignalDatacardList(signal_name, final_states, region)
                in_card_names.extend([self.getDatacardPath(signal_name, ic, define_strategy = False, region = region) for ic in cards_to_merge])

        out_name_tmp = getOutDataCardName(final_states, self.search_regions)
        out_card_name = self.getDatacardPath(signal_name, out_name_tmp, region = self.combineRegionNames(signal_name))
        print out_card_name
        self.mergeDatacards(signal_name, in_card_names, out_card_name)

class DatacardManager:

    def __init__(self, years, era, strategy, flavor, selection, regions = None, masstype = 'Majorana', tag = None, search_regions = None):
        self.years = years
        self.era = era
        self.strategy = strategy
        self.flavor = flavor
        self.selection = selection
        self.singleyear_managers = [SingleYearDatacardManager(y, era, strategy, flavor, selection, regions, masstype, tag, search_regions) for y in years]
        self.masstype = masstype
        self.tag = tag
        self.regions = regions
        self.search_regions = search_regions

    def getDatacardPath(self, signal_name, card_name, region = None, define_strategy = True):
        from HNL.Stat.combineTools import displaced_mass_threshold
        from combineTools import returnDataCardPath
        return returnDataCardPath(self.era, '-'.join(sorted(self.years)), self.selection, region if region is not None else getRegionFromMass(self.singleyear_managers[0].getHNLmass(signal_name)), self.flavor, signal_name, card_name if not define_strategy else self.singleyear_managers[0].original_strategy+'/'+card_name, self.masstype, tag = self.tag)
    
    def mergeYears(self, signal_name, card_name, region = None):
        if len(self.years) == 1:
            return
        else:
            out_path = self.getDatacardPath(signal_name, card_name, region = region)
            from HNL.Tools.helpers import makeDirIfNeeded
            makeDirIfNeeded(out_path)
            from HNL.Stat.combineTools import runCombineCommand
            runCombineCommand('combineCards.py '+' '.join([sm.getDatacardPath(signal_name, card_name, region = region) for sm in self.singleyear_managers])+' > '+out_path)

    def prepareAllCards(self, signal_name, final_states):
        for iyear, year in enumerate(self.years):
            self.singleyear_managers[iyear].initializeCards(signal_name, final_states)

        out_name_tmp = getOutDataCardName(final_states, self.search_regions)
        self.mergeYears(signal_name, out_name_tmp, self.singleyear_managers[0].combineRegionNames(signal_name))

    def checkMassAvailability(self, signal_name):
        exists = True
        regions = [self.singleyear_managers[0].getHNLregion(signal_name, None)] if self.regions is None else self.regions
        for iyear, year in enumerate(self.years):
            for region in regions:
                if not os.path.exists(self.singleyear_managers[iyear].getDatacardPath(signal_name, 'x', region = region, define_strategy = False).rsplit('/', 1)[0]): 
                    exists = False
                    print 'problem with', self.singleyear_managers[iyear].getDatacardPath(signal_name, 'x', region = region, define_strategy = False).rsplit('/', 1)[0] 

        return exists
    
    def combineRegionNames(self, signal_name):
        return self.singleyear_managers[0].combineRegionNames(signal_name)
