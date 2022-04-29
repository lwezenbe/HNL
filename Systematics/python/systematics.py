
import os
json_location = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Systematics', 'data', 'systematics.json'))

class Systematics:
    DICT_OF_FLATUNCERTAINTIES = {
        'nonprompt_tau' : 1.3,
        'nonprompt_lightlep' : 1.3,
        'luminosity' : 1.025
    }
    LIST_OF_WEIGHTSYSTEMATICS = ['puWeight', 'tauSFWeight', 'electronRecoWeight', 'btagWeight']
    LIST_OF_RERUNSYSTEMATICS = ['tauEnergyScale']
    LIST_OF_SYSTEMATICS = LIST_OF_WEIGHTSYSTEMATICS + LIST_OF_RERUNSYSTEMATICS + DICT_OF_FLATUNCERTAINTIES.keys()

    def __init__(self, sample, reweighter):
        self.sample = sample
        self.chain = self.sample.chain
        self.reweighter = reweighter

    def returnBranches(self):
        branches = []
        for syst in self.LIST_OF_SYSTEMATICS:
            branches.append('{0}Up/F'.format(syst))
            branches.append('{0}UpRaw/F'.format(syst))
            branches.append('{0}Down/F'.format(syst))
            branches.append('{0}DownRaw/F'.format(syst))
        return branches

    def getWeightSystematics(self, weight):
        weight_up = self.reweighter.returnWeight(weight, syst='up')
        weight_down = self.reweighter.returnWeight(weight, syst='down')
        return weight_up, weight_down

    def storeFullWeightSystematics(self, weight, output_tree):
        weight_up, weight_down = self.getWeightSystematics(weight)
        output_tree.setTreeVariable('{0}UpRaw'.format(weight), weight_up)
        output_tree.setTreeVariable('{0}DownRaw'.format(weight), weight_down)
        for original_weight in self.reweighter.WEIGHTS_TO_USE:
            if original_weight == weight: continue
            weight_up *= getattr(output_tree.tree, original_weight)
            weight_down *= getattr(output_tree.tree, original_weight)
        output_tree.setTreeVariable('{0}Up'.format(weight), weight_up)
        output_tree.setTreeVariable('{0}Down'.format(weight), weight_down)

    def storeAllSystematicsForShapes(self, output_tree):
        for syst in self.LIST_OF_SYSTEMATICS:
            if syst in self.reweighter.WEIGHTS_TO_USE:
                self.storeFullWeightSystematics(syst, output_tree)   

class SystematicJSONreader:

    def __init__(self):
        import json
        with open(json_location, 'r') as f:
            self.json_data = json.load(f)

    def isActive(self, syst):
        return self.json_data[syst]['Activate']

    def getType(self, syst):
        return self.json_data[syst]['Type']

    def getYear(self, syst):
        return self.json_data[syst]['Year']

    def getGeneral(self, syst_type, year, split_syst=False):
        if not split_syst:
            return [k for k in self.json_data.keys() if self.getType(k) == syst_type and self.isActive(k) and year in self.getYear(k)]
        else:
            final_list = []
            for k in self.json_data.keys():
                if self.getType(k) != syst_type or not self.isActive(k) or year not in self.getYear(k): continue
                final_list.append(k+'Up')
                final_list.append(k+'Down')
            return final_list

    def getFlats(self, year):
        return self.getGeneral("flat", year)

    def getWeights(self, year):
        return self.getGeneral("weight", year)

    def getReruns(self, year, split_syst = False):
        return self.getGeneral("rerun", year, split_syst)
    
    def getAllSources(self, year):
        return self.getFlats(year)+self.getWeights(year)

    def getProcesses(self, syst):
        return self.json_data[syst]['Processes']
    
    def filterProcesses(self, syst, background_names, sig_name, prompt_from_sideband=True):
        raw_processes = self.getProcesses(syst)
        if raw_processes == '*':
            return background_names + [sig_name]
        elif raw_processes == 'MC':
            return [x for x in background_names if x != 'non-prompt'] + [sig_name] if prompt_from_sideband else background_names + [sig_name]
        else:
            return raw_processes
        
    def getFinalStates(self, syst):
        return self.json_data[syst]['FinalStates']

    def filterFinalStates(self, syst):
        fs = self.getFinalStates(syst)
        if fs == '*':
            from HNL.EventSelection.eventCategorization import SUPER_CATEGORIES
            return SUPER_CATEGORIES.keys()
        else:
            return fs

    def getValue(self, syst):
        return self.json_data[syst]['Value']

def prepareForRerunSyst(chain, event, systematic = 'nominal'):
    event.chain.obj_sel['systematic'] = systematic
    event.original_object_selection['systematic'] = systematic
    return event

def insertSystematics(out_file, bkgr_names, sig_name, bin_name, year):
    
    reader = SystematicJSONreader()
    from HNL.Tools.helpers import tab

    for syst in reader.getAllSources():
        out_str = [syst, 'lnN' if syst in reader.getFlats() else 'shape']
        for proc in bkgr_names + [sig_name]:
            if not any([x in bin_name for x in reader.filterFinalStates(syst)]) or proc not in reader.filterProcesses(syst, bkgr_names, sig_name):
                out_str += ['-']
            else:
                out_str += [reader.getValue(syst)]
        
        out_file.write(tab(out_str))        
         
def returnWeightShapes(tree, vname, hname, bins, condition):
    reader = SystematicJSONreader()
    all_weights = reader.getWeights()
    out_dict = {}
    from HNL.Tools.histogram import Histogram
    for weight in all_weights:
        for syst in ['Up', 'Down']:
            out_dict[weight+syst] = Histogram(tree.getHistFromTree(vname, hname + weight + syst, bins, condition, weight = weight+syst))
    return out_dict     

if __name__ == '__main__':
    sr = SystematicJSONreader()
    print [sr.getValue(syst) for syst in sr.getFlats()]
