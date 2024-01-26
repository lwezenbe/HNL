from HNL.HEPData.hepdataTools import addCommonQualifiersTo, addCommonKeywordsTo
from HNL.Samples.sample import Sample

def createYieldJson(signal, bkgr, observed, syst_signal, syst_bkgr, signal_names, bkgr_names, combine_bkgr = True, binned = False, signal_coupling = None, signal_mass = None):
    import numpy as np
    up = 0
    down = 1

    #First combine bkgr 
    if combine_bkgr and len(bkgr) > 0:
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
        try:
            out_dict['signal'][sname] = fillSingleSample(s, syst_signal[up][i], syst_signal[down][i], binned) 
        except:
            out_dict['signal'][sname] = fillSingleSample(s, None, None, binned) 
    if signal_coupling is not None: 
        out_dict['signal']['coupling'] = signal_coupling
    if signal_mass is not None: 
        out_dict['signal']['mass'] = signal_mass
    
    #Loop over bkgr
    out_dict['bkgr'] = {}
    if len(bkgr) > 0:
        for i, (b, bname) in enumerate(zip(bkgr, bkgr_names)):
            try:
                out_dict['bkgr'][bname] = fillSingleSample(b, syst_bkgr[up][i], syst_bkgr[down][i], binned) 
            except:
                out_dict['bkgr'][bname] = fillSingleSample(b, None, None, binned) 

    #Get data
    if observed is not None:  out_dict['data'] = fillSingleSample(observed, None, None, binned)['nominal']

    return out_dict
            

def fillSingleSample(in_hist, in_syst_up = None, in_syst_down = None, binned=False):
    out_obj = {'bins' : [], 'nominal' : [], 'up' : [], 'down' : []}

    def filteredNumber(n):
        if n < -900.:
            return '-'
        elif n < 0.:
            return -1
        elif n < 1e-6: 
            return 0.
        else:
            return n

    for b in xrange(1, in_hist.getHist().GetNbinsX()+1):

        if not binned:
            bin_name = b
        else:
            bin_name = [in_hist.getHist().GetXaxis().GetBinLowEdge(b), in_hist.getHist().GetXaxis().GetBinUpEdge(b)]

        out_obj['bins'].append(bin_name)
        out_obj['nominal'].append(filteredNumber(in_hist.getHist().GetBinContent(b)))
        stat_err = in_hist.getHist().GetBinError(b)
        if in_syst_up is not None:
            out_obj['up'].append(filteredNumber(np.sqrt(in_syst_up.getHist().GetBinError(b) ** 2 + stat_err ** 2)))
        else:
            out_obj['up'].append(filteredNumber(stat_err))
            
        if in_syst_down is not None:
            out_obj['down'].append(filteredNumber(np.sqrt(in_syst_down.getHist().GetBinError(b) ** 2 + stat_err ** 2)))
        else:
            out_obj['down'].append(filteredNumber(stat_err))

    return out_obj
            
def writePostfitYieldJson(hist_dict, out_name):
    import numpy as np
    up = 0
    down = 1

    #Start actually making the json
    out_dict = {
        'is_binned' : True,
    }

    
    out_dict['bkgr'] = {'Total Background' : fillSingleSample(hist_dict['syst'], None, None, True)}
    
    out_dict['data'] = fillSingleSample(hist_dict['observed'], None, None, True)['nominal']

    #Loop over signal
    out_dict['signal'] = {}
    for i, (s, sname) in enumerate(zip(hist_dict['signal_hist'], hist_dict['signal_names'])):
        out_dict['signal'][sname] = fillSingleSample(s, None, None, True)

    from HNL.Tools.helpers import makeDirIfNeeded
    makeDirIfNeeded(out_name)
    import json
    with open(out_name+'.json', 'w') as outfile:
        json.dump(out_dict, outfile, indent=2)


    
