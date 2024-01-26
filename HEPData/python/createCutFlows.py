from HNL.HEPData.hepdataTools import addCommonQualifiersTo, addCommonKeywordsTo
from HNL.Samples.sample import Sample

#categories refers to a list of names for the categories to store in the file
def createCutFlowJSONs(signal, bkgr, observed, output_dir, categories = None, searchregions = None, starting_dir = ''):
    out_dict = {}
    
    out_dict['signal'] = {}
    from HNL.EventSelection.cutter import CutflowReader
    for s in signal:
        for c in categories:
            flav = Sample.getSignalFlavor(s)
            print s, c
            if 'tau' in flav:
                if 'lep' in flav:
                    if 'Tau' in c: continue
                    new_s = s.replace('taulep', 'tau')
                if 'had' in flav:
                    if not 'Tau' in c: continue
                    new_s = s.replace('tauhad', 'tau')
            else:
                 new_s = s
            if new_s not in out_dict['signal'].keys(): out_dict['signal'][new_s] = {}
            cfr = CutflowReader(new_s+'-'+str(c), signal[s], subdir=starting_dir)
            out_dict['signal'][new_s][c] = cfr.returnCutFlow(categories[c], searchregions)
    
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

def loadJson(in_file):
    import json
    with open(in_file, 'r') as f:
        out_json = json.load(f)
    return out_json

def copyCutFlows():
    import os
    import json
    from HNL.HEPData.settings import hepdata_folder
    hepdata_base = hepdata_folder +'/data/cutflows'
    from HNL.Tools.helpers import makeDirIfNeeded
    makeDirIfNeeded(hepdata_base+'/x')

    #Merge displaced and nondisplaced at low mass
    low_mass_disp_e = loadJson('/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-lowMassSRloose-/UL2016post-2016pre-2017-2018/signalOnly-Majorana/e_coupling/customMasses/10.0to25.0/norm-None/CutFlows/cutflow.json') 
    low_mass_prompt_e = loadJson('/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-lowMassSRloose-/UL2016post-2016pre-2017-2018/signalOnly-Majorana/e_coupling/customMasses/30.0to75.0/norm-None/CutFlows/cutflow.json') 
    low_mass_disp_e['signal'].update(low_mass_prompt_e['signal'])
    low_mass_e = json.dumps(low_mass_disp_e)
    with open(hepdata_base+'/low_mass_e.json', 'w') as f:
        f.write(low_mass_e)    
    
    low_mass_disp_mu = loadJson('/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-lowMassSRloose-/UL2016post-2016pre-2017-2018/signalOnly-Majorana/mu_coupling/customMasses/10.0to25.0/norm-None/CutFlows/cutflow.json') 
    low_mass_prompt_mu = loadJson('/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-lowMassSRloose-/UL2016post-2016pre-2017-2018/signalOnly-Majorana/mu_coupling/customMasses/30.0to75.0/norm-None/CutFlows/cutflow.json') 
    low_mass_disp_mu['signal'].update(low_mass_prompt_mu['signal'])
    low_mass_mu = json.dumps(low_mass_disp_mu)
    with open(hepdata_base+'/low_mass_mu.json', 'w') as f:
        f.write(low_mass_mu)    
    
    low_mass_disp_tau = loadJson('/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-lowMassSRloose-/UL2016post-2016pre-2017-2018/signalOnly-Majorana/tau_coupling/customMasses/10.0to25.0/norm-None/CutFlows/cutflow.json') 
    low_mass_prompt_tau = loadJson('/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-lowMassSRloose-/UL2016post-2016pre-2017-2018/signalOnly-Majorana/tau_coupling/customMasses/30.0to75.0/norm-None/CutFlows/cutflow.json') 
    low_mass_disp_tau['signal'].update(low_mass_prompt_tau['signal'])
    low_mass_tau = json.dumps(low_mass_disp_tau)
    with open(hepdata_base+'/low_mass_tau.json', 'w') as f:
        f.write(low_mass_tau)    

    #Copy high mass
    os.system('scp /ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-highMassSR-/UL2016post-2016pre-2017-2018/signalOnly-Majorana/e_coupling/customMasses/85.0to1500.0/norm-None/CutFlows/cutflow.json '+hepdata_base+'/high_mass_e.json')
    os.system('scp /ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-highMassSR-/UL2016post-2016pre-2017-2018/signalOnly-Majorana/mu_coupling/customMasses/85.0to1500.0/norm-None/CutFlows/cutflow.json '+hepdata_base+'/high_mass_mu.json')
    os.system('scp /ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL-CutFlow/MVA-default-highMassSR-/UL2016post-2016pre-2017-2018/signalOnly-Majorana/tau_coupling/customMasses/85.0to1000.0/norm-None/CutFlows/cutflow.json '+hepdata_base+'/high_mass_tau.json')

if __name__ == '__main__':
    copyCutFlows()
