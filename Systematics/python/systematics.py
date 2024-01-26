import os
json_location = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Systematics', 'data', 'systematics.json'))

class Systematics:
    def __init__(self, sample, reweighter, datadriven_processes = None, year = None):
        self.sample = sample
        self.chain = self.sample.chain
        self.reweighter = reweighter
        self.sjr = SystematicJSONreader(datadriven_processes)
        if year is None:
            self.year = self.chain.year
        else:
            self.year = year

    def returnBranches(self, proc):
        branches = []
        for syst in self.sjr.getWeights(self.chain.year, proc, split_correlations=True):
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
        weight_name = self.sjr.getCorrName(weight, self.year)
        output_tree.setTreeVariable('{0}UpRaw'.format(weight_name), weight_up)
        output_tree.setTreeVariable('{0}DownRaw'.format(weight_name), weight_down)
        for original_weight in self.reweighter.WEIGHTS_TO_USE:
            if original_weight == self.splitSystName(weight)[0]: continue
            weight_up *= getattr(output_tree.tree, original_weight)
            weight_down *= getattr(output_tree.tree, original_weight)
        output_tree.setTreeVariable('{0}Up'.format(weight_name), weight_up)
        output_tree.setTreeVariable('{0}Down'.format(weight_name), weight_down)

    def storeAllSystematicsForShapes(self, output_tree, proc):
        for syst in self.sjr.getWeights(self.chain.year, proc):
            #print syst
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
            if split_correlations: 
                syst_name = self.getCorrName(k, year)
            else:
                syst_name = k
            if split_syst:
                final_list.append(syst_name+'Up')
                final_list.append(syst_name+'Down')
            else:
                final_list.append(syst_name)
        return final_list

    def getCorrName(self, syst, year):
        syst = str(syst)
        if not self.systIsCorrelated(syst):
            if syst.endswith('Up'):
                return syst.split('Up')[0]+'_'+str(year)+'Up'
            elif syst.endswith('Down'):
                return syst.split('Down')[0]+'_'+str(year)+'Down'
            else:
                return syst+'_'+str(year)
        else:
            return syst 

    def getFlats(self, year, proc = None, final_state = None, split_correlations=False):
        return self.getGeneral("flat", year, proc, final_state, split_correlations = split_correlations)

    def getWeights(self, year, proc = None, final_state = None, split_syst = False, split_correlations=False):
        if '-' in year:
            return self.compileListOfGeneralSystematics('weight', proc, year.split('-'), final_state = final_state, split_syst = split_syst, split_corr = split_correlations)
        else:
            return self.getGeneral("weight", year, proc, final_state, split_syst, split_correlations = split_correlations)

    def getReruns(self, year, proc = None, final_state = None, split_syst = False, split_correlations=False):
        if '-' in year:
            return self.compileListOfGeneralSystematics('rerun', proc, year.split('-'), final_state = final_state, split_syst = split_syst, split_corr = split_correlations)
        else:
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
            return 'Data' in proc or (self.datadriven_processes is not None and proc in self.datadriven_processes)
        elif raw_processes == 'signal':
            return 'HNL' in proc
        else:
            return proc in raw_processes
        
    def getFinalStates(self, syst):
        return self.json_data[syst]['FinalStates']

    def filterFinalStates(self, syst, final_state):
        from HNL.EventSelection.eventCategorization import isLightLeptonFinalState
        fs = self.getFinalStates(syst)
        if fs == '*':
            return True
        elif fs == 'Tau':
            return not isLightLeptonFinalState(final_state)
        else:
            raise RuntimeError("Undefined final state")

    def systIsCorrelated(self, syst):
        base_syst = syst
        if syst.endswith('Up'):
            base_syst = syst.split('Up')[0]
        elif syst.endswith('Down'):
            base_syst = syst.split('Down')[0]
        return self.json_data[base_syst].get('Correlated', False)
    
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

    def compileListOfGeneralSystematics(self, syst_type, proc, years, final_state = None, split_syst=False, split_corr = True):
        final_syst = set()
        for year in years:
            final_syst.update(self.getGeneral(syst_type, year, proc, final_state = final_state, split_correlations = split_corr, split_syst=split_syst))
        return [x for x in final_syst]

    def getGroups(self, year):
        final_groups = set()
        for s in self.getAllSources(year):
            final_groups.add(self.json_data[s]['Group'])
        self.groups = [x for x in final_groups]
        return self.groups

    def getSystInGroup(self, group_name, year, proc, final_state = None):
        final_list = []
        for s in self.getAllSources(year, final_state = final_state):
            if group_name == self.json_data[s]["Group"]:
                final_list.append(s)
        return final_list


def prepareForRerunSyst(chain, event, systematic = 'nominal'):
    if not 'tauEnergyScale' in systematic:
        event.chain.obj_sel['systematic'] = systematic
        event.chain.original_object_selection['systematic'] = systematic
        event.tau_energy_scale_syst = 'nominal'
    else:
        event.chain.obj_sel['systematic'] = 'nominal'
        event.chain.original_object_selection['systematic'] = 'nominal'
        event.tau_energy_scale_syst = systematic
    return event

def decorrelateSearchRegions(syst_name, sr):
    if 'nonprompt_tau' in syst_name:
        if sr in ['F', 'A', 'B']:
            syst_name = syst_name.replace('nonprompt_tau', 'nonprompt_tau_nonossf')
        else:   
            syst_name = syst_name.replace('nonprompt_tau', 'nonprompt_tau_ossf')
    return syst_name

def insertSystematics(out_file, bkgr_names, sig_name, year, final_state, datadriven_processes, decorrelate_sr = None):
    
    reader = SystematicJSONreader(datadriven_processes = datadriven_processes)
    from HNL.Tools.helpers import tab

    from HNL.EventSelection.eventCategorization import translateCategories
    final_state = translateCategories(final_state)    

    for syst in reader.getAllSources(year, split_correlations=False):
        if not '-' in year or syst in reader.getFlats(year) or reader.systIsCorrelated(syst):
            out_str = [decorrelateSearchRegions(reader.getCorrName(syst, year), decorrelate_sr) if decorrelate_sr is not None else reader.getCorrName(syst, year), 'lnN' if syst in reader.getFlats(year) else 'shape']
            for proc in bkgr_names + [sig_name]:
                if not reader.filterProcesses(syst, proc) or not reader.filterFinalStates(syst, final_state):
                    out_str += ['-']
                else:
                    out_str += [reader.getValue(syst, year, process = proc)]
            out_file.write(tab(out_str))        
        else:
            for y in [x for x in reader.getYear(syst) if x in year.split('-')]:
                out_str = [decorrelateSearchRegions(reader.getCorrName(syst, y), decorrelate_sr) if decorrelate_sr is not None else reader.getCorrName(syst, y), 'shape']
                for proc in bkgr_names + [sig_name]:
                    if not reader.filterProcesses(syst, proc) or not reader.filterFinalStates(syst, final_state):
                        out_str += ['-']
                    else:
                        out_str += [reader.getValue(syst, year, process = proc)]
                out_file.write(tab(out_str))        

def insertGroups(out_file, bkgr_names, sig_name, year, final_state, datadriven_processes, decorrelate_sr = None):
    
    reader = SystematicJSONreader(datadriven_processes = datadriven_processes)
    from HNL.Tools.helpers import tab

    from HNL.EventSelection.eventCategorization import translateCategories
    final_state = translateCategories(final_state)    

    out_file.write('\n')

    groups = reader.getGroups(year)
    for group in groups:
        out_str = group + ' group = '
        list_of_syst = reader.getSystInGroup(group, year, bkgr_names + [sig_name], final_state)
        for syst in list_of_syst:
            if not '-' in year or syst in reader.getFlats(year) or reader.systIsCorrelated(syst):
                tmp_str = decorrelateSearchRegions(reader.getCorrName(syst, year), decorrelate_sr) if decorrelate_sr is not None else reader.getCorrName(syst, year)
                out_str += " "+tmp_str
            else:
                for y in [x for x in reader.getYear(syst) if x in year.split('-')]:
                    tmp_str = decorrelateSearchRegions(reader.getCorrName(syst, y), decorrelate_sr) if decorrelate_sr is not None else reader.getCorrName(syst, y)
                    out_str += " "+tmp_str
        out_file.write(out_str+ '\n') 
    out_file.write('\n')
         
def returnWeightShapes(tree, vname, hname, bins, condition, year, proc, datadriven_processes = None, additional_weight = None, decorrelate_sr = None):
    reader = SystematicJSONreader(datadriven_processes)
    #all_corr_weights = reader.getWeights(year, proc, split_syst=True, split_correlations=True)
    all_corr_weights = reader.compileListOfGeneralSystematics('weight', proc, year.split('-'), split_syst=True)
    out_dict = {}
    from HNL.Tools.histogram import Histogram
    for weight in all_corr_weights:
        weight_for_name = weight
        if additional_weight is not None:
            weight += '*'+additional_weight

        if decorrelate_sr is not None:
            weight_for_name = decorrelateSearchRegions(weight_for_name, decorrelate_sr)
        out_dict[weight_for_name] = Histogram(tree.getHistFromTree(vname, hname + weight, bins, condition, weight = weight))
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
def makeSystErrorHist(in_hist, process_name, final_state, year, datadriven_processes = None, split_output = False):
    reader = SystematicJSONreader(datadriven_processes)

    def sqrErr(a, b):
        import numpy as np
        return np.sqrt(a**2+b**2)

    nominal_hist = in_hist['nominal']

    if not split_output:
        syst_error_hist = nominal_hist.clone('syst_error')
    else:
        up = 0
        down = 1
        syst_error_hist = [nominal_hist.clone('syst_error_up'), nominal_hist.clone('syst_error_down')]


    for b in xrange(1, nominal_hist.getHist().GetNbinsX() + 1):
        if not split_output:
            syst_error_hist.getHist().SetBinError(b, 0.)
        else:
            for i in range(2):
                syst_error_hist[i].getHist().SetBinError(b, 0.)
        for flat_unc in reader.getFlats(year, process_name, final_state):
           # if reader.systIsCorrelated(flat_unc): continue
            percentage = abs(1.-reader.getValue(flat_unc, year, process=process_name))
            if not split_output:
                syst_error_hist.getHist().SetBinError(b, sqrErr(syst_error_hist.getHist().GetBinError(b), nominal_hist.getHist().GetBinContent(b)*percentage)), '('+ str(nominal_hist.getHist().GetBinContent(b)/nominal_hist.getHist().GetBinContent(b)*percentage) if nominal_hist.getHist().GetBinContent(b)*percentage != 0 else '0'+')'
            else:
                for i in range(2):
                    syst_error_hist[i].getHist().SetBinError(b, sqrErr(syst_error_hist[i].getHist().GetBinError(b), nominal_hist.getHist().GetBinContent(b)*percentage)), '('+ str(nominal_hist.getHist().GetBinContent(b)/nominal_hist.getHist().GetBinContent(b)*percentage) if nominal_hist.getHist().GetBinContent(b)*percentage != 0 else '0'+')'

        for weight in reader.getWeights(year, process_name, final_state, split_syst = False, split_correlations=True):
            #if reader.systIsCorrelated(weight): continue
            err_up = abs(in_hist[weight+'Up'].getHist().GetBinContent(b) - in_hist['nominal'].getHist().GetBinContent(b))
            err_down = abs(in_hist[weight+'Down'].getHist().GetBinContent(b) - in_hist['nominal'].getHist().GetBinContent(b))
            if not split_output:
                bin_error = max(err_up, err_down)
                syst_error_hist.getHist().SetBinError(b, sqrErr(syst_error_hist.getHist().GetBinError(b), bin_error))
            else:
                syst_error_hist[up].getHist().SetBinError(b, sqrErr(syst_error_hist[up].getHist().GetBinError(b), err_up))
                syst_error_hist[down].getHist().SetBinError(b, sqrErr(syst_error_hist[down].getHist().GetBinError(b), err_down))

        for rerun in reader.getReruns(year, process_name, final_state, split_syst = False, split_correlations=True):
            #if reader.systIsCorrelated(rerun): continue
            err_up = abs(in_hist[rerun+'Up'].getHist().GetBinContent(b) - in_hist['nominal'].getHist().GetBinContent(b))
            err_down = abs(in_hist[rerun+'Down'].getHist().GetBinContent(b) - in_hist['nominal'].getHist().GetBinContent(b))
            if not split_output:
                bin_error = max(err_up, err_down)
                syst_error_hist.getHist().SetBinError(b, sqrErr(syst_error_hist.getHist().GetBinError(b), bin_error))
            else:
                syst_error_hist[up].getHist().SetBinError(b, sqrErr(syst_error_hist[up].getHist().GetBinError(b), err_up))
                syst_error_hist[down].getHist().SetBinError(b, sqrErr(syst_error_hist[down].getHist().GetBinError(b), err_down))
            
    return syst_error_hist

def addYears(original_syst, syst_to_add, syst_name, datadriven_processes = None):
    reader = SystematicJSONreader(datadriven_processes)

if __name__ == '__main__':
    sr = SystematicJSONreader()
    print [sr.getValue(syst) for syst in sr.getFlats()]

