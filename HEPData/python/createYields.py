from HNL.HEPData.hepdataTools import addCommonQualifiersTo, addCommonKeywordsTo

def createYieldJson(signal, bkgr, observed, syst_signal, syst_bkgr, signal_names, bkgr_names, combine_bkgr = True, binned = False, signal_coupling = None, signal_mass = None):
    import numpy as np
    up = 0
    down = 1

    #First combine bkgr 
    if combine_bkgr:
        for i, b in enumerate(bkgr):
            if i == 0:
                tmp_bkgr = b.clone('bkgr')
                tmp_syst_up = syst_bkgr[up][i].clone('up')
                tmp_syst_down = syst_bkgr[down][i].clone('down')
            else:
                tmp_bkgr.add(b)
                for syst_bin in range(1, tmp_syst_up.getHist().GetNbinsX()+1):
                    tmp_syst_up.getHist().SetBinError(syst_bin, np.sqrt(tmp_syst_up.getHist().GetBinError(syst_bin) ** 2 + syst_bkgr[up][i].getHist().GetBinError(syst_bin) ** 2))
                    tmp_syst_down.getHist().SetBinError(syst_bin, np.sqrt(tmp_syst_down.getHist().GetBinError(syst_bin) ** 2 + syst_bkgr[down][i].getHist().GetBinError(syst_bin) ** 2))

        bkgr = [tmp_bkgr]
        syst_bkgr = [[tmp_syst_up], [tmp_syst_down]]
        bkgr_names = ['Total Background']

    #Start actually making the json
    out_dict = {
        'is_binned' : True,
    }

    def fillSingleSample(in_hist, in_syst_up = None, in_syst_down = None, binned=False):
        out_obj = {'bins' : [], 'nominal' : [], 'up' : [], 'down' : []}
        for b in xrange(1, in_hist.getHist().GetNbinsX()+1):

            if not binned:
                bin_name = b
            else:
                bin_name = [in_hist.getHist().GetXaxis().GetBinLowEdge(b), in_hist.getHist().GetXaxis().GetBinUpEdge(b)]

            out_obj['bins'].append(bin_name)
            out_obj['nominal'].append(in_hist.getHist().GetBinContent(b))
            stat_err = in_hist.getHist().GetBinError(b)
            if in_syst_up is not None:
                out_obj['up'].append(np.sqrt(in_syst_up.getHist().GetBinError(b) ** 2 + stat_err ** 2))
            else:
                out_obj['up'].append(stat_err)
                
            if in_syst_down is not None:
                out_obj['down'].append(np.sqrt(in_syst_down.getHist().GetBinError(b) ** 2 + stat_err ** 2))
            else:
                out_obj['down'].append(stat_err)

        return out_obj

    #Loop over signal
    out_dict['signal'] = {}
    for i, (s, sname) in enumerate(zip(signal, signal_names)):
        out_dict['signal'][sname] = fillSingleSample(s, syst_signal[up][i], syst_signal[down][i], binned) 
    if signal_coupling is not None: 
        out_dict['signal']['coupling'] = signal_coupling
    if signal_mass is not None: 
        out_dict['signal']['mass'] = signal_mass
    
    #Loop over bkgr
    out_dict['bkgr'] = {}
    for i, (b, bname) in enumerate(zip(bkgr, bkgr_names)):
        out_dict['bkgr'][bname] = fillSingleSample(b, syst_bkgr[up][i], syst_bkgr[down][i], binned) 

    #Get data
    out_dict['data'] = fillSingleSample(observed, None, None, binned)['nominal']

    return out_dict
            

def createYieldVariable(nominal, up = None, down = None):
    from hepdata_lib import Variable, Uncertainty
    out_var = Variable("Event Yield",
                    is_independent = False,
                    is_binned=False,
                    units = "")

    out_var.values = nominal
    addCommonQualifiersTo(out_var)

    if up is None or len(up) == 0 or down is None or len(down) == 0: return out_var

    is_symmetric = up == down
    unc = Uncertainty("stat+syst", is_symmetric = is_symmetric)
    if is_symmetric:
        unc.values = up
    else:
        unc.values = [(d, u) for u,d in zip(up, down)]

    out_var.add_uncertainty(unc)
    return out_var


GEV = "GeV"
    
def addLowMassTables(submission):
    from hepdata_lib import Table, Variable

    #First get the independent variables
    bins_ptl1 = Variable("$p_{T}(l_{1})$",
                    is_independent = True,
                    is_binned = False,
                    units = GEV    
                    )
    bins_ptl1.values = ["<30", "<30", "<30", "<30", "30-55", "30-55", "30-55", "30-55"]
 
    bins_minMos = Variable("min $m(2l|$OS)",
                    is_independent = True,
                    is_binned = False,
                    units = GEV    
                    )
    bins_minMos.values = ["<10", "10-20", "20-30", ">30", "<10", "10-20", "20-30", ">30"]

    #Create table and variable for bkgr and data
    

def addHighMassTablesHa(submission):
    from hepdata_lib import Table, Variable
    
    #First get the independent variables
    bins_binnb = Variable("bin number",
                    is_independent = True,
                    is_binned = False,
                    units = ""    
                    )
    bins_binnb.values = range(1, 10)
    
    bins_m3l = Variable("$m(3l)$",
                    is_independent = True,
                    is_binned = False,
                    units = GEV    
                    )
    bins_m3l.values = ["<100", "<100", ">100", ">100", ">100", ">100", ">100", ">100", ">100"]
    
    bins_minMos = Variable("min $m(2l|$OS)",
                    is_independent = True,
                    is_binned = False,
                    units = GEV    
                    )
    bins_minMos.values = ["any", "any", "<100", "<100", "<100", "<100", "100 to 200", "100 to 200", ">200"]
    
    bins_mt = Variable("$m_T$",
                    is_independent = True,
                    is_binned = False,
                    units = GEV    
                    )
    bins_mt.values = ["<100", ">100", "<100", "100 to 150", "150 to 250", ">250", "<100", ">100", "any"]
    
    #Create Table for background and data yields
    #Start by loading in the json
    def loadJsons(coupling_type):
        import json
        eem_path = '/storage_mnt/storage/user/lwezenbe/private/testArea/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL/MVA-default-highMassSR-/UL2017/signalAndBackground-Majorana/{0}_coupling/customMasses/150.0-300.0/Yields/SearchRegions/EEE-Mu/searchregion-F.json'.format(coupling_type)  
        with open(eem_path, 'r') as infile:
            numbers_eem = json.load(infile)
        emm_path = '/storage_mnt/storage/user/lwezenbe/private/testArea/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL/MVA-default-highMassSR-/UL2017/signalAndBackground-Majorana/{0}_coupling/customMasses/150.0-300.0/Yields/SearchRegions/MuMuMu-E/searchregion-F.json'.format(coupling_type)
        with open(emm_path, 'r') as infile:
            numbers_emm = json.load(infile)
        tee_path = '/storage_mnt/storage/user/lwezenbe/private/testArea/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL/MVA-default-highMassSR-/UL2017/signalAndBackground-Majorana/{0}_coupling/customMasses/150.0-300.0/Yields/SearchRegions/TauEE/searchregion-F.json'.format(coupling_type)
        with open(tee_path, 'r') as infile:
            numbers_tee = json.load(infile)
        tmm_path = '/storage_mnt/storage/user/lwezenbe/private/testArea/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL/MVA-default-highMassSR-/UL2017/signalAndBackground-Majorana/{0}_coupling/customMasses/150.0-300.0/Yields/SearchRegions/TauMuMu/searchregion-F.json'.format(coupling_type)
        with open(tmm_path, 'r') as infile:
            numbers_tmm = json.load(infile)
        tem_path = '/storage_mnt/storage/user/lwezenbe/private/testArea/CMSSW_10_2_22/src/HNL/Analysis/data/Results/runAnalysis/HNL/MVA-default-highMassSR-/UL2017/signalAndBackground-Majorana/{0}_coupling/customMasses/150.0-300.0/Yields/SearchRegions/TauEMu/searchregion-F.json'.format(coupling_type)
        with open(tem_path, 'r') as infile:
            numbers_tem = json.load(infile)
        return (numbers_eem, numbers_emm, numbers_tee, numbers_tmm, numbers_tem)

    numbers_eem, numbers_emm, numbers_tee, numbers_tmm, numbers_tem = loadJsons('e')

    yield_eem_data = createYieldVariable(numbers_eem["data"], None, None)
    yield_eem_data.add_qualifier('Channel', '$e^{\pm}e^{\pm}\mu$')
    yield_eem_data.add_qualifier('Process', 'Data')
    yield_eem_bkgr = createYieldVariable(numbers_eem["bkgr"]["Total Background"]["nominal"], numbers_eem["bkgr"]["Total Background"]["up"], numbers_eem["bkgr"]["Total Background"]["down"])
    yield_eem_bkgr.add_qualifier('Channel', '$e^{\pm}e^{\pm}\mu$')
    yield_eem_bkgr.add_qualifier('Process', 'Background')
    
    yield_emm_data = createYieldVariable(numbers_emm["data"], None, None)
    yield_emm_data.add_qualifier('Process', 'Data')
    yield_emm_data.add_qualifier('Channel', '$\mu^{\pm}\mu^{\pm}e$')
    yield_emm_bkgr = createYieldVariable(numbers_emm["bkgr"]["Total Background"]["nominal"], numbers_emm["bkgr"]["Total Background"]["up"], numbers_emm["bkgr"]["Total Background"]["down"])
    yield_emm_bkgr.add_qualifier('Channel', '$\mu^{\pm}\mu^{\pm}e$')
    yield_emm_bkgr.add_qualifier('Process', 'Background')
    
    yield_tee_data = createYieldVariable(numbers_tee["data"], None, None)
    yield_tee_data.add_qualifier('Channel', '$e^{\pm}e^{\pm}\\tau$')
    yield_tee_data.add_qualifier('Process', 'Data')
    yield_tee_bkgr = createYieldVariable(numbers_tee["bkgr"]["Total Background"]["nominal"], numbers_tee["bkgr"]["Total Background"]["up"], numbers_tee["bkgr"]["Total Background"]["down"])
    yield_tee_bkgr.add_qualifier('Process', 'Background')
    yield_tee_bkgr.add_qualifier('Channel', '$e^{\pm}e^{\pm}\\tau$')

    yield_tmm_data = createYieldVariable(numbers_tmm["data"], None, None)
    yield_tmm_data.add_qualifier('Process', 'Data')
    yield_tmm_data.add_qualifier('Channel', '$\mu^{\pm}\mu^{\pm}\\tau$')
    yield_tmm_bkgr = createYieldVariable(numbers_tmm["bkgr"]["Total Background"]["nominal"], numbers_tmm["bkgr"]["Total Background"]["up"], numbers_tmm["bkgr"]["Total Background"]["down"])
    yield_tmm_bkgr.add_qualifier('Process', 'Background')
    yield_tmm_bkgr.add_qualifier('Channel', '$\mu^{\pm}\mu^{\pm}\\tau$')
    
    yield_tem_data = createYieldVariable(numbers_tem["data"], None, None)
    yield_tem_data.add_qualifier('Process', 'Data')
    yield_tem_data.add_qualifier('Channel', '$e\mu\\tau$')
    yield_tem_bkgr = createYieldVariable(numbers_tem["bkgr"]["Total Background"]["nominal"], numbers_tem["bkgr"]["Total Background"]["up"], numbers_tem["bkgr"]["Total Background"]["down"])
    yield_tem_bkgr.add_qualifier('Process', 'Background')
    yield_tem_bkgr.add_qualifier('Channel', '$e\mu\\tau$')
    
    table_bkgr = Table("Data and background yields (High Mass Region Ha)")
    table_bkgr.add_variable(bins_binnb)
    table_bkgr.add_variable(bins_m3l)
    table_bkgr.add_variable(bins_minMos)
    table_bkgr.add_variable(bins_mt)
    table_bkgr.add_variable(yield_eem_data)
    table_bkgr.add_variable(yield_eem_bkgr)
    table_bkgr.add_variable(yield_emm_data)
    table_bkgr.add_variable(yield_emm_bkgr)
    table_bkgr.add_variable(yield_tee_data)
    table_bkgr.add_variable(yield_tee_bkgr)
    table_bkgr.add_variable(yield_tmm_data)
    table_bkgr.add_variable(yield_tmm_bkgr)
    table_bkgr.add_variable(yield_tem_data)
    table_bkgr.add_variable(yield_tem_bkgr)
    addCommonKeywordsTo(table_bkgr)
    submission.add_table(table_bkgr)
   

    #Signal Tables
    yields_eem = []
    yields_emm = []
    from HNL.Samples.sample import Sample

    flavor_tex_dict = {'e' : 'e', 'mu' : '\mu', 'tau' : '\tau'}

    def returnSignalVar(numbers, channel):    
        masses = numbers['signal']['mass']
        out_yields = []
        for mass in masses:
            for sk in numbers['signal']:
                if Sample.getSignalMass(sk) != mass:
                    continue
                else:
                    out_yields.append(createYieldVariable(numbers['signal'][sk]['nominal'], numbers['signal'][sk]['up'], numbers['signal'][sk]['down']))
                    out_yields[-1].add_qualifier('HNL mass', '{0} GeV'.format(mass))
                    out_yields[-1].add_qualifier('$|V_{N'+flavor_tex_dict[Sample.getSignalFlavor(sk)]+'}|^2$', str(Sample.getSignalCouplingSquared(sk)))
                    out_yields[-1].add_qualifier('Channel', channel)

        return out_yields


    #E-coupling
    yields = {}
    yields['eem'] = returnSignalVar(numbers_eem, '$e^{\pm}e^{\pm}\mu$')
    yields['emm'] = returnSignalVar(numbers_eem, '$\mu^{\pm}\mu^{\pm}e$')
    
    table_ecoupl = Table("Predicted signal yields (High Mass Region Ha, $e$-coupling)")
    table_ecoupl.add_variable(bins_binnb)
    table_ecoupl.add_variable(bins_m3l)
    table_ecoupl.add_variable(bins_minMos)
    table_ecoupl.add_variable(bins_mt)
    for k in yields.keys():
        for s in yields[k]:
            table_ecoupl.add_variable(s)
    addCommonKeywordsTo(table_ecoupl)
    submission.add_table(table_ecoupl)

    #Mu-coupling
    numbers_eem, numbers_emm, numbers_tee, numbers_tmm, numbers_tem = loadJsons('mu')
    yields = {}
    yields['eem'] = returnSignalVar(numbers_eem, '$e^{\pm}e^{\pm}\mu$')
    yields['emm'] = returnSignalVar(numbers_eem, '$\mu^{\pm}\mu^{\pm}e$')
    
    table_mcoupl = Table("Predicted signal yields (High Mass Region Ha, $\mu$-coupling)")
    table_mcoupl.add_variable(bins_binnb)
    table_mcoupl.add_variable(bins_m3l)
    table_mcoupl.add_variable(bins_minMos)
    table_mcoupl.add_variable(bins_mt)
    for k in yields.keys():
        for s in yields[k]:
            table_mcoupl.add_variable(s)
    addCommonKeywordsTo(table_mcoupl)
    submission.add_table(table_mcoupl)
    
    #tau-coupling
    numbers_eem, numbers_emm, numbers_tee, numbers_tmm, numbers_tem = loadJsons('tau')
    yields = {}
    yields['eem'] = returnSignalVar(numbers_eem, '$e^{\pm}e^{\pm}\mu$')
    yields['emm'] = returnSignalVar(numbers_eem, '$\mu^{\pm}\mu^{\pm}e$')
    yields['tee'] = returnSignalVar(numbers_eem, '$e^{\pm}e^{\pm}\\tau$')
    yields['tmm'] = returnSignalVar(numbers_eem, '$\mu^{\pm}\mu^{\pm}\\tau$')
    yields['tem'] = returnSignalVar(numbers_eem, '$e\mu\\tau$')
    
    table_tcoupl = Table("Predicted signal yields (High Mass Region Ha, $\\tau$-coupling)")
    table_tcoupl.add_variable(bins_binnb)
    table_tcoupl.add_variable(bins_m3l)
    table_tcoupl.add_variable(bins_minMos)
    table_tcoupl.add_variable(bins_mt)
    for k in yields.keys():
        for s in yields[k]:
            table_tcoupl.add_variable(s)
    addCommonKeywordsTo(table_tcoupl)
    submission.add_table(table_tcoupl)

def addAllYieldTables(submission):
    addHighMassTablesHa(submission)

if __name__ == '__main__':
    from hepdata_lib import Submission

    submission = Submission()
    addAllYieldTables(submission)
    submission.create_files('./submission')
 
