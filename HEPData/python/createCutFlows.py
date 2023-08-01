from HNL.HEPData.hepdataTools import addCommonQualifiersTo, addCommonKeywordsTo

#categories refers to a list of names for the categories to store in the file
def createCutFlowJSONs(signal, bkgr, observed, output_dir, categories = None, searchregions = None, starting_dir = ''):
    out_dict = {}
    
    out_dict['signal'] = {}
    from HNL.EventSelection.cutter import CutflowReader
    for s in signal:
        out_dict['signal'][s] = {}
        for c in categories:
            cfr = CutflowReader(s+'-'+str(c), signal[s], subdir=starting_dir)
            out_dict['signal'][s][c] = cfr.returnCutFlow(categories[c], searchregions)
    
    if bkgr is not None:    
        out_dict['bkgr'] = {}
        for b in bkgr:
            out_dict['bkgr'][b] = {}
            for c in categories:
                cfr = CutflowReader(b+'-'+str(c), bkgr[b], subdir=starting_dir)
                out_dict['bkgr'][b][c] = cfr.returnCutFlow(categories[c], searchregions)

#    out_dict['observed']
#    for c in categories:
#        cfr = CutFlowReader('observed-'+str(c), observed)
#        out_dict['observed'][c] = cfr.returnCutFlow(categories[c], searchregions)

    # Save cutflows
    from HNL.Tools.helpers import makeDirIfNeeded
    import json
    makeDirIfNeeded(output_dir+'/x')
    with open(output_dir+'/cutflow.json', 'w') as outfile:
        json.dump(out_dict, outfile, indent=2)

    return out_dict

cut_dict = {
    "Sample Skim Baseline"              : 'total',
    "metfilters"                        : 'passes $p_T^{\\textrm{miss}}$ filters',
    "pass_triggers"                     : 'passes trigger',
    "3 tight leptons"                   : 'three tight leptons',
    "Pass offline thresholds"           : 'passes offline trigger thresholds',
    "Fourth FO veto"                    : 'no fourth FO lepton',
    "No three same sign"                : 'veto on three same signs',
    "b-veto"                            : 'b-veto',
    "l1pt<55"                           : '$p_T(\\textrm{leading lepton}) < 55$GeV',
    "m3l<80"                            : '$m(3l) < 80$ GeV',
    "m3l>80"                            : '$m(3l) > 80$ GeV',
    "MET < 75"                          : '$p_T^{\\textrm{miss}} < 75$GeV',
    "M2l_OSSF_Z_veto"                   : '$|m(2l|\\textrm{OSSF}) - m_Z| > 15$GeV',
    "minMossf"                          : 'min $m(2l|\\textrm{OSSF}) > 5$GeV',
    "l1pt>55"                           : '$p_T(\\textrm{leading lepton}) > 55$GeV',
    "l2pt>15"                           : '$p_T(\\textrm{subleading lepton}) > 15$GeV',
    "l3pt>10"                           : '$p_T(\\textrm{trailing lepton}) > 10$GeV',
    "M3l_Z_veto"                        : '$|m(3l) - m_Z| > 15$GeV',
}

#category_dict = {
#    'EEE-Mu'            : 'three electrons or two electrons and a muon',
#    'MuMuMu-E'          : 'three muons or two muons and an electron',
#    'TauEE'             : 'two electrons and a hadronically decayed tau lepton',
#    'TauMuMu'           : 'two muons and a hadronically decayed tau lepton',
#    'TauEMu'            : 'an electron, a muon and a hadronically decayed tau lepton'
#}
category_dict = {
    'EEE-Mu'            : '$eee$ or $ee\mu$',
    'MuMuMu-E'          : '$\mu\mu\mu$ or $\mu\mu e$',
    'TauEE'             : '$ee\\tau$',
    'TauMuMu'           : '$\mu\mu\\tau$',
    'TauEMu'            : '$e\mu\\tau$'
}

def getTranslatedCat(cat):
    if cat in category_dict.keys():
        return category_dict[cat]
    return cat 

flavor_tex_dict = {'e' : 'e', 'mu' : '\mu', 'tau' : '\\tau'}


def translateCut(cut_name, category):
    if cut_name == 'passed category':
        #return category_dict[category]
        return "pass final state selection"
    elif cut_name in cut_dict.keys():
        return cut_dict[cut_name]
    else:
        return str(cut_name)

def createCutFlowVariable(cutflow):
    from hepdata_lib import Variable
    out_var = Variable("Number of passing events",
                    is_independent = False,
                    is_binned=False,
                    units = "")

    out_var.values = cutflow
    addCommonQualifiersTo(out_var)
    return out_var

def createCutFlowTable(in_path, categories, name):
    from hepdata_lib import Variable, Table
    import json
    with open(in_path, 'r') as infile:
        in_json = json.load(infile)

    from HNL.Samples.sample import Sample
    signals = in_json['signal'].keys()
    def sortKey(s):
        return float(Sample.getSignalMass(s))
    signals = sorted(signals, key=sortKey)

    #Create Table
    table = Table(name)

    for i_sig, sig in enumerate(signals):
        for ic, category in enumerate(categories):
            if i_sig == 0 and ic == 0:
                cut_names = [translateCut(cut, category) for cut in in_json['signal'][sig][category]['cuts']]
                
                #Create the variable
                cut_name_var = Variable("Requirement",
                                        is_independent = True,
                                        is_binned = False,
                                        units = ""  
                                        )
                cut_name_var.values = cut_names
                table.add_variable(cut_name_var)
    
            else:
                #Cross check the cut names
                tmp_check = [translateCut(cut, category) for cut in in_json['signal'][sig][category]['cuts']]
                if tmp_check != cut_names:
                    raise RuntimeError("Trying to add different cutflows in single table")

            tmp_var = createCutFlowVariable(in_json['signal'][sig][category]['values'])
            tmp_var.add_qualifier('Final State', str(getTranslatedCat(category)))
            tmp_var.add_qualifier('HNL mass', '{0} GeV'.format(Sample.getSignalMass(sig)))
            tmp_var.add_qualifier('$|V_{N'+flavor_tex_dict[Sample.getSignalFlavor(sig)]+'}|^2$', str(Sample.getSignalCouplingSquared(sig)))
            table.add_variable(tmp_var)

    return table

def createCutFlowTableTest(in_path, categories, name):
    from hepdata_lib import Variable, Table
    import json
    with open(in_path, 'r') as infile:
        in_json = json.load(infile)

    from HNL.Samples.sample import Sample
    signals = in_json['signal'].keys()
    backgrounds = in_json['bkgr'].keys()

    #Create Table
    table = Table(name)

    for i_sig, sig in enumerate(signals + backgrounds):
        sig_string = 'signal' if sig in signals else 'bkgr'
        for ic, category in enumerate(categories):
            if i_sig == 0 and ic == 0:
                cut_names = [translateCut(cut, category) for cut in in_json[sig_string][sig][category]['cuts']]

                #Create the variable
                cut_name_var = Variable("Requirement",
                                        is_independent = True,
                                        is_binned = False,
                                        units = ""
                                        )
                cut_name_var.values = cut_names
                table.add_variable(cut_name_var)

            else:
                #Cross check the cut names
                tmp_check = [translateCut(cut, category) for cut in in_json[sig_string][sig][category]['cuts'] if translateCut(cut, category) != 'Clean Nonprompt ZG']
                if tmp_check != cut_names:
                    raise RuntimeError("Trying to add different cutflows in single table")

            ignore_index = in_json[sig_string][sig][category]['cuts'].index('Clean Nonprompt ZG') if 'Clean Nonprompt ZG' in in_json[sig_string][sig][category]['cuts'] else None
            cutflow_values = in_json[sig_string][sig][category]['values']
            if ignore_index is not None: cutflow_values.pop(ignore_index)
            tmp_var = createCutFlowVariable(cutflow_values)
            tmp_var.add_qualifier('Final State', str(getTranslatedCat(category)))
            tmp_var.add_qualifier('Sample', str(sig))
            table.add_variable(tmp_var)

    return table

def printTexTable(in_path, category, name, scale_signal=None):
    import json
    with open(in_path, 'r') as infile:
        in_json = json.load(infile)

    from HNL.Samples.sample import Sample
    signals = in_json['signal'].keys()
    backgrounds = in_json['bkgr'].keys()


    cutflow_values = {}
    for i_sig, sig in enumerate(signals):
        if i_sig == 0:
            cut_names = [translateCut(cut, category) for cut in in_json['signal'][sig][category]['cuts']]
        else:
            #Cross check the cut names
            tmp_check = [translateCut(cut, category) for cut in in_json['signal'][sig][category]['cuts'] if translateCut(cut, category) != 'Clean Nonprompt ZG']
            if tmp_check != cut_names:
                raise RuntimeError("Trying to add different cutflows in single table")

        ignore_index = in_json['signal'][sig][category]['cuts'].index('Clean Nonprompt ZG') if 'Clean Nonprompt ZG' in in_json['signal'][sig][category]['cuts'] else None
        cutflow_values[sig] = in_json['signal'][sig][category]['values']
        if ignore_index is not None: cutflow_values[sig].pop(ignore_index)
        if scale_signal is not None: 
            cutflow_values[sig] = [x*scale_signal for x in cutflow_values[sig]]    

    for i_sig, sig in enumerate(backgrounds):
        tmp_check = [translateCut(cut, category) for cut in in_json['bkgr'][sig][category]['cuts'] if translateCut(cut, category) != 'Clean Nonprompt ZG']
        if tmp_check != cut_names:
            raise RuntimeError("Trying to add different cutflows in single table")
    
        ignore_index = in_json['bkgr'][sig][category]['cuts'].index('Clean Nonprompt ZG') if 'Clean Nonprompt ZG' in in_json['bkgr'][sig][category]['cuts'] else None
        tmp_cutflow_values = in_json['bkgr'][sig][category]['values']
        if ignore_index is not None: tmp_cutflow_values.pop(ignore_index)
        if i_sig == 0:
            cutflow_values['Bkgr'] = [x for x in tmp_cutflow_values]
        else:
            for i, tv in enumerate(tmp_cutflow_values):
                cutflow_values['Bkgr'][i] += tv

            
    cutflow_values_keys = ['Bkgr'] + sorted(signals)
    print ' & '.join(['Selection'] + cutflow_values_keys)+ '\\\\'
    for ic, c in enumerate(cut_names):
        print ' & '.join([c]+[str(round(cutflow_values[sn][ic], 1)) for sn in cutflow_values_keys]) + '\\\\'


def addCutflowTo(submission):
    #
    #Low mass
    #
    in_path_lowmass_e = '/storage_mnt/storage/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-lowMassSRloose-/UL2016post-2016pre-2017-2018/signalAndBackground-Majorana/e_coupling/customMasses/10.0to75.0/CutFlows/cutflow.json'
    table_lowmass_e = createCutFlowTable(in_path_lowmass_e, ['EEE-Mu', 'MuMuMu-E'], 'Cut flow: e-coupling, low mass region')
    submission.add_table(table_lowmass_e)
    
    in_path_lowmass_mu = '/storage_mnt/storage/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-lowMassSRloose-/UL2016post-2016pre-2017-2018/signalAndBackground-Majorana/mu_coupling/customMasses/10.0to75.0/CutFlows/cutflow.json'
    table_lowmass_mu = createCutFlowTable(in_path_lowmass_mu, ['EEE-Mu', 'MuMuMu-E'], 'Cut flow: mu-coupling, low mass region')
    submission.add_table(table_lowmass_mu)
    
    in_path_lowmass_tau = '/storage_mnt/storage/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-lowMassSRloose-/UL2016post-2016pre-2017-2018/signalAndBackground-Majorana/tau_coupling/customMasses/10.0to75.0/CutFlows/cutflow.json'
    table_lowmass_tau = createCutFlowTable(in_path_lowmass_tau, ['EEE-Mu', 'MuMuMu-E', 'TauEE', 'TauMuMu', 'TauEMu'], 'Cut flow: tau-coupling, low mass region')
    submission.add_table(table_lowmass_tau)

    #
    #High mass
    #
    in_path_highmass_e = '/storage_mnt/storage/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-highMassSR-/UL2016post-2016pre-2017-2018/signalAndBackground-Majorana/e_coupling/customMasses/85.0to1500.0/CutFlows/cutflow.json'
    table_highmass_e = createCutFlowTable(in_path_highmass_e, ['EEE-Mu', 'MuMuMu-E'], 'Cut flow: e-coupling, high mass region')
    submission.add_table(table_highmass_e)
    
    in_path_highmass_mu = '/storage_mnt/storage/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-highMassSR-/UL2016post-2016pre-2017-2018/signalAndBackground-Majorana/mu_coupling/customMasses/85.0to1500.0/CutFlows/cutflow.json'
    table_highmass_mu = createCutFlowTable(in_path_highmass_mu, ['EEE-Mu', 'MuMuMu-E'], 'Cut flow: mu-coupling, high mass region')
    submission.add_table(table_highmass_mu)

    in_path_highmass_tau = '/storage_mnt/storage/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-highMassSR-/UL2016post-2016pre-2017-2018/signalAndBackground-Majorana/tau_coupling/customMasses/85.0to1500.0/CutFlows/cutflow.json'
    table_highmass_tau = createCutFlowTable(in_path_highmass_tau, ['EEE-Mu', 'MuMuMu-E', 'TauEE', 'TauMuMu', 'TauEMu'], 'Cut flow: tau-coupling, high mass region')
    submission.add_table(table_highmass_tau)

if __name__ == '__main__':
    from hepdata_lib import Submission
    submission = Submission()
    #addCutflowTo(submission)
    
    table_elow = createCutFlowTableTest('/storage_mnt/storage/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-lowMassSRloose-/UL2016post-2016pre-2017-2018/signalAndBackground-Majorana/e_coupling/customMasses/20.0-40.0-60.0/CutFlows/cutflow.json', ['NoTau'], 'cutflow: low mass region: NoTau')
    table_taulow = createCutFlowTableTest('/storage_mnt/storage/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-lowMassSRloose-/UL2016post-2016pre-2017-2018/signalAndBackground-Majorana/tau_coupling/customMasses/20.0-40.0-60.0/CutFlows/cutflow.json', ['SingleTau'], 'cutflow: low mass region: SingleTau')
    table_ehigh = createCutFlowTableTest('/storage_mnt/storage/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-highMassSR-/UL2016post-2016pre-2017-2018/signalAndBackground-Majorana/e_coupling/customMasses/150.0-500.0-800.0/CutFlows/cutflow.json', ['NoTau'], 'cutflow: high mass region: NoTau')
    submission.add_table(table_elow) 
    submission.add_table(table_taulow) 
    submission.add_table(table_ehigh) 

    submission.create_files('./submission')
    #printTexTable('/storage_mnt/storage/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-lowMassSRloose-/UL2016post-2016pre-2017-2018/signalAndBackground-Majorana/e_coupling/customMasses/20.0-40.0-60.0/CutFlows/cutflow.json', 'NoTau', 'cutflow: low mass region: NoTau')
    #printTexTable('/storage_mnt/storage/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-lowMassSRloose-/UL2016post-2016pre-2017-2018/signalAndBackground-Majorana/tau_coupling/customMasses/20.0-40.0-60.0/CutFlows/cutflow.json', 'SingleTau', 'cutflow: low mass region: SingleTau', scale_signal=100.)
    #printTexTable('/storage_mnt/storage/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-highMassSR-/UL2016post-2016pre-2017-2018/signalAndBackground-Majorana/e_coupling/customMasses/150.0-500.0-800.0/CutFlows/cutflow.json', 'NoTau', 'cutflow: high mass region: NoTau', scale_signal = 1000.)
    printTexTable('/storage_mnt/storage/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-highMassSR-/UL2016post-2016pre-2017-2018/signalAndBackground-Majorana/tau_coupling/customMasses/150.0-500.0-800.0/CutFlows/cutflow.json', 'SingleTau', 'cutflow: high mass region: NoTau', scale_signal = 1000.)

