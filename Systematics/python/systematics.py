import os
json_location = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Systematics', 'data', 'systematics.json'))

class Systematics:
    def __init__(self, sample, reweighter, datadriven_processes = None):
        self.sample = sample
        self.chain = self.sample.chain
        self.reweighter = reweighter
        self.sjr = SystematicJSONreader(datadriven_processes)

    def returnBranches(self, proc):
        branches = []
        for syst in self.sjr.getWeights(self.chain.year, proc):
            branches.append('{0}Up/F'.format(syst))
            branches.append('{0}UpRaw/F'.format(syst))
            branches.append('{0}Down/F'.format(syst))
            branches.append('{0}DownRaw/F'.format(syst))
        return branches

    def splitSystName(self, weight):
        if '_' in weight:
            return weight.split('_')
        else:
            return (weight, '')

    def getWeightSystematics(self, weight):
        short_weight, syst_append = self.splitSystName(weight)
       
        weight_up = self.reweighter.returnWeight(short_weight, syst=syst_append+'up')
        weight_down = self.reweighter.returnWeight(short_weight, syst=syst_append+'down')
        return weight_up, weight_down

    def storeFullWeightSystematics(self, weight, output_tree):
        weight_up, weight_down = self.getWeightSystematics(weight)
        output_tree.setTreeVariable('{0}UpRaw'.format(weight), weight_up)
        output_tree.setTreeVariable('{0}DownRaw'.format(weight), weight_down)
        for original_weight in self.reweighter.WEIGHTS_TO_USE:
            if original_weight == self.splitSystName(weight)[0]: continue
            weight_up *= getattr(output_tree.tree, original_weight)
            weight_down *= getattr(output_tree.tree, original_weight)
        output_tree.setTreeVariable('{0}Up'.format(weight), weight_up)
        output_tree.setTreeVariable('{0}Down'.format(weight), weight_down)

    def storeAllSystematicsForShapes(self, output_tree, proc):
        for syst in self.sjr.getWeights(self.chain.year, proc):
            short_syst = self.splitSystName(syst)[0]
            if short_syst in self.reweighter.WEIGHTS_TO_USE:
                self.storeFullWeightSystematics(syst, output_tree)   

class SystematicJSONreader:

    def __init__(self, datadriven_processes = None):
        import json
        with open(json_location, 'r') as f:
            self.json_data = json.load(f)
        self.datadriven_processes = datadriven_processes

    def isActive(self, syst):
        return self.json_data[syst]['Activate']

    def getType(self, syst):
        return self.json_data[syst]['Type']

    def getYear(self, syst):
        return self.json_data[syst]['Year']

    def getGeneral(self, syst_type, year, proc = None, final_state =  None, split_syst=False, split_correlations=False):
        final_list = []
        for k in self.json_data.keys():
            if self.getType(k) != syst_type or not self.isActive(k) or year not in self.getYear(k): continue
            if proc is not None and not self.filterProcesses(k, proc): continue
            if final_state is not None and not self.filterFinalStates(k, final_state): continue
            if split_correlations and not self.systIsCorrelated(k):
                syst_name = k+'_'+str(year)
            else:
                syst_name = k
            if split_syst:
                final_list.append(syst_name+'Up')
                final_list.append(syst_name+'Down')
            else:
                final_list.append(syst_name)
        return final_list

    def getFlats(self, year, proc = None, final_state = None, split_correlations=False):
        return self.getGeneral("flat", year, proc, final_state, split_correlations = split_correlations)

    def getWeights(self, year, proc = None, final_state = None, split_syst = False, split_correlations=False):
        return self.getGeneral("weight", year, proc, final_state, split_syst, split_correlations = split_correlations)

    def getReruns(self, year, proc = None, final_state = None, split_syst = False, split_correlations=False):
        return self.getGeneral("rerun", year, proc, final_state, split_syst, split_correlations = split_correlations)
    
    def getAllSources(self, year, proc = None, final_state = None, split_correlations=False):
        return self.getFlats(year, proc, final_state, split_correlations = split_correlations)+self.getWeights(year, proc, final_state, split_correlations = split_correlations)+self.getReruns(year, proc, final_state, split_correlations = split_correlations)

    def getProcesses(self, syst):
        return self.json_data[syst]['Processes']
    
    def filterProcesses(self, syst, proc):
        raw_processes = self.getProcesses(syst)
        if raw_processes == '*':
            return True
        elif raw_processes == 'MC':
            if 'Data' in proc: return False
            if self.datadriven_processes is not None and proc in self.datadriven_processes: return False
            return True
        elif raw_processes == 'data':
            return 'Data' in proc
        elif raw_processes == 'signal':
            return 'HNL' in proc
        else:
            return proc in raw_processes
        
    def getFinalStates(self, syst):
        return self.json_data[syst]['FinalStates']

    def filterFinalStates(self, syst, final_state):
        fs = self.getFinalStates(syst)
        if fs == '*':
            return True
        else:
            return final_state in fs

    def systIsCorrelated(self, syst):
        return self.json_data[syst].get('Correlated', False)
    
    def getFunc(self, syst):
        return self.json_data[syst].get('Func', None)

    def getValue(self, syst, year, **kwargs):
        try:
            len(self.json_data[syst]['Value'])
            is_list = True
        except:
            is_list = False

        if self.getFunc(syst) is not None:
            from HNL.Systematics.uncFunctions import returnUncFunc
            return returnUncFunc(self.getFunc(syst), kwargs)
        else:
            if is_list and len(self.json_data[syst]['Value']) != len(self.json_data[syst]['Year']):
                raise RuntimeError("Provided list of values but their length is different from the length of the Years")
            
            if is_list:
                val_index = self.json_data[syst]["Year"].index(year)
                return self.json_data[syst]['Value'][val_index]
            else:
                return self.json_data[syst]['Value']

    def getDescription(self, syst, year):
        return self.json_data[syst]['Description']

def prepareForRerunSyst(chain, event, systematic = 'nominal'):
    if not 'tauEnergyScale' in systematic:
        event.chain.obj_sel['systematic'] = systematic
        event.original_object_selection['systematic'] = systematic
        event.tau_energy_scale_syst = 'nominal'
    else:
        event.chain.obj_sel['systematic'] = 'nominal'
        event.original_object_selection['systematic'] = 'nominal'
        event.tau_energy_scale_syst = systematic
    return event

def insertSystematics(out_file, bkgr_names, sig_name, year, final_state, datadriven_processes):
    
    reader = SystematicJSONreader(datadriven_processes = datadriven_processes)
    from HNL.Tools.helpers import tab

    from HNL.EventSelection.eventCategorization import translateCategories
    final_state = translateCategories(final_state)    

    for syst_name, syst in zip(reader.getAllSources(year, split_correlations=True), reader.getAllSources(year, split_correlations=False)):
        out_str = [syst_name, 'lnN' if syst in reader.getFlats(year) else 'shape']
        for proc in bkgr_names + [sig_name]:
            if not reader.filterProcesses(syst, proc) or not reader.filterFinalStates(syst, final_state):
                out_str += ['-']
            else:
                out_str += [reader.getValue(syst, year, process = proc)]
    
        out_file.write(tab(out_str))        
         
def returnWeightShapes(tree, vname, hname, bins, condition, year, proc, datadriven_processes = None, split_corr = False, additional_weight = None):
    reader = SystematicJSONreader(datadriven_processes)
    all_weights = reader.getWeights(year, proc, split_syst=True)
    all_corr_weights = reader.getWeights(year, proc, split_syst=True, split_correlations=True)
    out_dict = {}
    from HNL.Tools.histogram import Histogram
    #print all_weights, all_corr_weights
    for weight, corr_weight in zip(all_weights, all_corr_weights):
        weight_for_name = corr_weight if split_corr else weight
        if additional_weight is not None:
            weight += '*'+additional_weight
        out_dict[weight_for_name] = Histogram(tree.getHistFromTree(vname, hname + weight_for_name, bins, condition, weight = weight))
    return out_dict     

def checkSyst(chain, syst = None):
    if syst is None:
        try:
            chain.obj_sel
        except:
            #Initiate default object selection
            from HNL.ObjectSelection.objectSelection import objectSelectionCollection
            chain.obj_sel = objectSelectionCollection()
        return chain.obj_sel['systematic']
    else:
        return syst

#in_hist is supposed to be a dictionary of hist, one nominal value the rest the up and down variations for weights and reruns
def makeSystErrorHist(in_hist, process_name, final_state, year, datadriven_processes = None):
    reader = SystematicJSONreader(datadriven_processes)

    def sqrErr(a, b):
        import numpy as np
        return np.sqrt(a**2+b**2)

    nominal_hist = in_hist['nominal']
    syst_error_hist = nominal_hist.clone('syst_error')
    for b in xrange(1, nominal_hist.getHist().GetNbinsX() + 1):
        syst_error_hist.getHist().SetBinError(b, 0.)
        for flat_unc in reader.getFlats(year, process_name, final_state):
           # if reader.systIsCorrelated(flat_unc): continue
            percentage = abs(1.-reader.getValue(flat_unc, year, process=process_name))
            syst_error_hist.getHist().SetBinError(b, sqrErr(syst_error_hist.getHist().GetBinError(b), nominal_hist.getHist().GetBinContent(b)*percentage)) 

        for weight in reader.getWeights(year, process_name, final_state, split_syst = False):
            #if reader.systIsCorrelated(weight): continue
            err_up = abs(in_hist[weight+'Up'].getHist().GetBinContent(b) - in_hist['nominal'].getHist().GetBinContent(b))
            err_down = abs(in_hist[weight+'Down'].getHist().GetBinContent(b) - in_hist['nominal'].getHist().GetBinContent(b))
            bin_error = max(err_up, err_down)
            syst_error_hist.getHist().SetBinError(b, sqrErr(syst_error_hist.getHist().GetBinError(b), bin_error))

        for rerun in reader.getReruns(year, process_name, final_state, split_syst = False):
            #if reader.systIsCorrelated(rerun): continue
            err_up = abs(in_hist[rerun+'Up'].getHist().GetBinContent(b) - in_hist['nominal'].getHist().GetBinContent(b))
            err_down = abs(in_hist[rerun+'Down'].getHist().GetBinContent(b) - in_hist['nominal'].getHist().GetBinContent(b))
            bin_error = max(err_up, err_down)
            syst_error_hist.getHist().SetBinError(b, sqrErr(syst_error_hist.getHist().GetBinError(b), bin_error))
            
    return syst_error_hist


if __name__ == '__main__':
    sr = SystematicJSONreader()
    print [sr.getValue(syst) for syst in sr.getFlats()]

