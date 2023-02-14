def translateTree(input_path, output_path, sample_name, year, list_of_all_years, datadriven_processes = None, standard_weight = 'weight'):
    from HNL.Systematics.systematics import SystematicJSONreader
    reader = SystematicJSONreader(datadriven_processes)

    from ROOT import TFile
    from HNL.Tools.helpers import makeDirIfNeeded
    makeDirIfNeeded(output_path)
    out_file = TFile.Open(output_path, 'RECREATE')

    #First the weights
    year_syst = reader.getWeights(year, sample_name, split_correlations=True)
    all_syst = reader.compileListOfGeneralSystematics('weight', None, list_of_all_years)
    relevant_syst = reader.compileListOfGeneralSystematics('weight', sample_name, list_of_all_years)
    remaining_syst = [x for x in relevant_syst if x not in year_syst]
 
    from HNL.Tools.helpers import getObjFromFile
    old_nominal = getObjFromFile(input_path, 'events_nominal')
    old_nominal_to_copy = getObjFromFile(input_path, 'events_nominal')
    new_nominal = old_nominal.CloneTree(0)
  
    all_branches = []
    for syst in all_syst:
        all_branches.append('{0}Up/F'.format(syst))     
        all_branches.append('{0}UpRaw/F'.format(syst))     
        all_branches.append('{0}Down/F'.format(syst))     
        all_branches.append('{0}DownRaw/F'.format(syst))     
    from HNL.Tools.makeBranches import makeBranches, createStruct
    createStruct(all_branches)
    
 
    new_branches = []
    for syst in remaining_syst:
        new_branches.append('{0}Up/F'.format(syst))     
        new_branches.append('{0}UpRaw/F'.format(syst))     
        new_branches.append('{0}Down/F'.format(syst))     
        new_branches.append('{0}DownRaw/F'.format(syst))     
    new_vars = makeBranches(new_nominal, new_branches)

    for entry in xrange(old_nominal.GetEntries()):
        old_nominal.GetEntry(entry)
        for syst in remaining_syst:
            setattr(new_vars, '{0}Up'.format(syst), getattr(old_nominal, standard_weight))   
            setattr(new_vars, '{0}Down'.format(syst), getattr(old_nominal, standard_weight))   
            setattr(new_vars, '{0}UpRaw'.format(syst), 1.)   
            setattr(new_vars, '{0}DownRaw'.format(syst), 1.)  
        new_nominal.Fill()
    
    out_file.cd()
    new_nominal.Write('events_nominal')
    
    #Then the reruns
    year_reruns_correlated = reader.getReruns(year, sample_name, split_syst = True, split_correlations = True)
    all_reruns = reader.compileListOfGeneralSystematics('rerun', sample_name, list_of_all_years, split_syst= True)
    for ys in year_syst:
        old_nominal_to_copy.SetBranchStatus('{0}Up'.format(ys), 0)
        old_nominal_to_copy.SetBranchStatus('{0}UpRaw'.format(ys), 0)
        old_nominal_to_copy.SetBranchStatus('{0}Down'.format(ys), 0)
        old_nominal_to_copy.SetBranchStatus('{0}DownRaw'.format(ys), 0)
    pruned_nominal = old_nominal_to_copy.CloneTree()

    for ar in all_reruns:
        if ar not in year_reruns_correlated:
            out_file.cd()
            pruned_nominal.SetObject('events_{0}'.format(ar), 'events_{0}'.format(ar))
            pruned_nominal.Write('events_{0}'.format(ar))
        else:
            out_write_obj = getObjFromFile(input_path, 'events_{0}'.format(ar))
            out_file.cd()
            out_write_obj.Write('events_{0}'.format(ar))
    out_file.Close()
    del new_vars

