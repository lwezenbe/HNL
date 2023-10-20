import os
from HNL.Tools.helpers import getObjFromFile
from HNL.Tools.histogram import Histogram

workspace_base = '/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/postfit'

input_base = '/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output'
shapes_base = '/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/shapes'
output_base = '/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output'

observed_name = 'data_obs'
bkgr_names = ['Other', 'TT-T+X', 'WZ', 'XG', 'ZZ-H', 'charge-misid', 'non-prompt', 'triboson']
year = '2016post-2016pre-2017-2018'
era = 'UL'

from HNL.Plotting.plottingDicts import sample_tex_names
from HNL.Samples.sample import Sample

label_dict = {
    'Hb' : ['Hb{0}'.format(x) for x in xrange(1, 17)],
    'Hbspecial' : ['Hb{0}'.format(x) for x in [1, '2-3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', 15, 16]],
    'Ha' : ['Ha{0}'.format(x) for x in xrange(1, 10)],
    'A' : ['L{0}'.format(x) for x in xrange(1, 5)],
    'B' : ['L{0}'.format(x) for x in xrange(5, 9)],
    'C' : ['L{0}'.format(x) for x in xrange(9, 13)],
    'D' : ['L{0}'.format(x) for x in xrange(13, 17)],
    'None': None
}


def loadBackgrounds(input_file, channel):
    backgrounds = []
    used_bkgr_names = []
    for b in bkgr_names:
        try:
            backgrounds.append(Histogram(getObjFromFile(input_file, channel+'_postfit/'+b)))
            used_bkgr_names.append(b)
        except:
            continue
    return backgrounds, used_bkgr_names

def loadObserved(input_file, channel):
    observed = Histogram(getObjFromFile(input_file, channel+'_postfit/'+observed_name))
    return observed

def loadSyst(input_file, channel):
    observed = Histogram(getObjFromFile(input_file, channel+'_postfit/TotalBkg'))
    return observed

def loadSignal(input_file, name):
    signal = Histogram(getObjFromFile(input_file, name))
    return signal

def loadExtraText(c_name, flavor, coupling):
    from HNL.Plotting.plottingTools import extraTextFormat
    extra_text = []
    extra_text.append(extraTextFormat(c_name, xpos = 0.2, ypos = 0.78, textsize = None, align = 12))  #Text to display event type in plot
    from decimal import Decimal
    et_flavor = flavor if flavor == 'e' else '#'+flavor
    extra_text.append(extraTextFormat('|V_{'+et_flavor+'N}|^{2} = '+'%.0E' % Decimal(str(coupling)), textsize = 0.8))
    extra_text.append(extraTextFormat('Postfit', textsize = 0.8))
    return extra_text


def combineLaterely(hist1, hist2):
    from ROOT import TH1D
    hist1 = hist1.getHist()
    hist2 = hist2.getHist()
    n_bin1 = hist1.GetNbinsX()
    n_bin2 = hist2.GetNbinsX()
    n_newbins = n_bin1 + n_bin2
    new_hist = TH1D('combined_hist', 'combined_hist', n_newbins, 0, n_newbins)
    b = 1
    for h1_bin in xrange(1, n_bin1 + 1):
        new_hist.SetBinContent(b, hist1.GetBinContent(h1_bin))
        new_hist.SetBinError(b, hist1.GetBinError(h1_bin))
        b += 1
    for h2_bin in xrange(1, n_bin2 + 1):
        new_hist.SetBinContent(b, hist2.GetBinContent(h2_bin))
        new_hist.SetBinError(b, hist2.GetBinError(h2_bin))
        b += 1
    return Histogram(new_hist)

def combineLateralyList(list_of_dict):
    out_dict = {}
    out_dict['bkgr_names'] = [x for x in list_of_dict[0]['bkgr_names']]
    out_dict['signal_names'] = [x for x in list_of_dict[0]['signal_names']]
    out_dict['bkgr_hist'] = [x for x in list_of_dict[0]['bkgr_hist']]
    out_dict['signal_hist'] = [x for x in list_of_dict[0]['signal_hist']]
    out_dict['observed'] = list_of_dict[0]['observed']
    out_dict['syst'] = list_of_dict[0]['syst']
    
    for hist_dict in list_of_dict[1:]:
        for ib, b in enumerate(out_dict['bkgr_hist']):
            out_dict['bkgr_hist'][ib] = combineLaterely(b, hist_dict['bkgr_hist'][ib])
        for ib, b in enumerate(out_dict['signal_hist']):
            out_dict['signal_hist'][ib] = combineLaterely(b, hist_dict['signal_hist'][ib])
        out_dict['observed'] = combineLaterely(out_dict['observed'], hist_dict['observed'])
        out_dict['syst'] = combineLaterely(out_dict['syst'], hist_dict['syst'])
    return out_dict

def addHist(hist_list1, hist_list2, hist_names_1, hist_names_2):
    if hist_names_1 == hist_names_2:
        for b3, b4 in zip(hist_list1, hist_list2):
            b3.add(b4)
        return hist_list1, hist_names_1
    else:
        missing_from_hist1 = [x for x in hist_names_2 if x not in hist_names_1]
        missing_from_hist2 = [x for x in hist_names_1 if x not in hist_names_2]

        if len(missing_from_hist1) == 0 and len(missing_from_hist2) > 0:
            for ib, b in enumerate(hist_list1):
                if hist_names_1[ib] in hist_names_2:
                    b.add(hist_list2[hist_names_2.index(hist_names_1[ib])])
            return hist_list1, hist_names_1
        elif len(missing_from_hist2) == 0 and len(missing_from_hist1) > 0:
            for ib, b in enumerate(hist_list2):
                if hist_names_2[ib] in hist_names_1:
                    b.add(hist_list1[hist_names_1.index(hist_names_2[ib])])
            return hist_list2, hist_names_2
        else:
            raise RuntimeError("edge case not implemented yet") 

def getNewWorkspaceLocation(original_folder):
    split_original_folder = original_folder.split('/output/')
    new_workspace = os.path.join(workspace_base, split_original_folder[1])
    return new_workspace
    
def loadHistograms(original_folder, channel_names, signal_dict, target_coupling):
    new_workspace = getNewWorkspaceLocation(original_folder)
    if os.path.isdir(new_workspace):
        os.system('rm -r '+new_workspace)
    from HNL.Tools.helpers import makeDirIfNeeded
    makeDirIfNeeded(new_workspace)

    os.system('scp -r {0} {1}'.format(original_folder, new_workspace))

    #First get the isolated datacard
    from HNL.Stat.combineTools import runCombineCommand
    runCombineCommand('combineCards.py --ic="{0}" .=datacard.txt > datacard-new.txt ; '.format('|'.join([x + '$' for x in channel_names]))
                        + 'text2workspace.py datacard-new.txt -o ws-new.root ; '
                        + 'PostFitShapesFromWorkspace -d datacard-new.txt -w ws-new.root --output postfitshapes.root -f fitDiagnosticsTest.root:fit_s --postfit --sampling --total-shapes' , new_workspace)

    #Now load the backgrounds
    input_file = os.path.join(new_workspace, 'postfitshapes.root')
    bkgr, used_bkgr_names = loadBackgrounds(input_file, channel_names[0])
    for channel in channel_names[1:]:
        tmp_bkgr, tmp_used_bkgr_names = loadBackgrounds(input_file, channel)
        bkgr, used_bkgr_names = addHist(bkgr, tmp_bkgr, used_bkgr_names, tmp_used_bkgr_names)

    #Load in the observed
    observed = Histogram(getObjFromFile(input_file, 'postfit/'+observed_name))

    #Load in systematics
    syst = Histogram(getObjFromFile(input_file, 'postfit/TotalBkg'))

    #Load in the signal
    signal_hist = []
    signal_names = []
    def sortKey(s):
        return float(Sample.getSignalMass(s))

    def signal_path(name):
        return os.path.join(shapes_base, name)

    for i, s in enumerate(sorted(signal_dict.keys(), key=sortKey)):
        coupling = Sample.getSignalCouplingSquared(s)
        sf = target_coupling / coupling

        signal_hist.append(loadSignal(signal_path(signal_dict[s][0][0]), signal_dict[s][0][1]))
        for iss, ss in enumerate(signal_dict[s][1:], start = 1):
            signal_hist[i].add(loadSignal(signal_path(signal_dict[s][iss][0]), signal_dict[s][iss][1]))
        
        signal_hist[i].getHist().Scale(sf)
        signal_names.append(s)

    final_dict = {
        'bkgr_hist' : [x for x in bkgr],
        'bkgr_names' : [x for x in used_bkgr_names],
        'signal_hist' : [x for x in signal_hist],
        'signal_names' : [x for x in signal_names],
        'observed' : observed,
        'syst' : syst
    }
    
    return final_dict
    
def trimBins(in_hist, new_bins):
    import numpy as np
    new_bins = np.array(new_bins)

    hist = in_hist.getHist()
    from ROOT import TH1F
    new_hist = Histogram(TH1F(hist.GetName(), hist.GetTitle(), len(new_bins)-1, new_bins))
    for b in xrange(1, new_hist.getHist().GetNbinsX()+1):
        new_hist.getHist().SetBinContent(b, hist.GetBinContent(hist.FindBin(new_hist.getHist().GetBinCenter(b))))
        new_hist.getHist().SetBinError(b, hist.GetBinError(hist.FindBin(new_hist.getHist().GetBinCenter(b))))
    return new_hist

def trimDistributions(hist_dict):
    tot_bkgr = hist_dict['bkgr_hist'][0].clone('new-hist')
    for b in hist_dict['bkgr_hist'][1:]:
        tot_bkgr.add(b)
    
    from HNL.Analysis.helpers import removeEmptyBins
    new_bins = removeEmptyBins([tot_bkgr])

    out_dict = {}
    out_dict['bkgr_names'] = [x for x in hist_dict['bkgr_names']]
    out_dict['signal_names'] = [x for x in hist_dict['signal_names']]
    out_dict['bkgr_hist'] = []
    out_dict['signal_hist'] = []

    for b in hist_dict['bkgr_hist']:
        out_dict['bkgr_hist'].append(trimBins(b, new_bins))
    for s in hist_dict['signal_hist']:
        out_dict['signal_hist'].append(trimBins(s, new_bins))
    out_dict['observed'] = trimBins(hist_dict['observed'], new_bins)
    out_dict['syst'] = trimBins(hist_dict['syst'], new_bins)

    return out_dict

def normalizeBins(in_hist):
    hist = in_hist.getHist()
    n_bins = hist.GetNbinsX()
    from ROOT import TH1F
    new_hist = Histogram(TH1F(hist.GetName(), hist.GetTitle(), n_bins, 0, n_bins))
    for b in xrange(1, new_hist.getHist().GetNbinsX()+1):
        new_hist.getHist().SetBinContent(b, hist.GetBinContent(b))
        new_hist.getHist().SetBinError(b, hist.GetBinError(b))
    return new_hist
    
def normalizeBinsAll(hist_dict):
    out_dict = {}
    out_dict['bkgr_names'] = [x for x in hist_dict['bkgr_names']]
    out_dict['signal_names'] = [x for x in hist_dict['signal_names']]
    out_dict['bkgr_hist'] = []
    out_dict['signal_hist'] = []

    for b in hist_dict['bkgr_hist']:
        out_dict['bkgr_hist'].append(normalizeBins(b))
    for s in hist_dict['signal_hist']:
        out_dict['signal_hist'].append(normalizeBins(s))
    out_dict['observed'] = normalizeBins(hist_dict['observed'])
    out_dict['syst'] = normalizeBins(hist_dict['syst'])

    return out_dict

def drawPlot(hist_dict, output_name, x_label, x_name, extra_text, name, normalize_bins = False):

    hist_dict = trimDistributions(hist_dict)
    if normalize_bins:
        hist_dict = normalizeBinsAll(hist_dict)

    bkgr = [x for x in hist_dict['bkgr_hist']]
    used_bkgr_names = [x for x in hist_dict['bkgr_names']]
    signal = [x for x in hist_dict['signal_hist']]
    signal_names = [x for x in hist_dict['signal_names']]
    observed = hist_dict['observed']
    syst_hist = hist_dict['syst']

    for b, bn in zip(bkgr, used_bkgr_names):
        if bn in ['triboson', 'TT-T+X', 'charge-misid']:
            bkgr[used_bkgr_names.index('Other')].add(b)
    

    bkgr.pop(used_bkgr_names.index('triboson'))
    used_bkgr_names.pop(used_bkgr_names.index('triboson'))
    bkgr.pop(used_bkgr_names.index('TT-T+X'))
    used_bkgr_names.pop(used_bkgr_names.index('TT-T+X'))
    bkgr.pop(used_bkgr_names.index('charge-misid'))
    used_bkgr_names.pop(used_bkgr_names.index('charge-misid'))
    
    bkgr_legendnames = [sample_tex_names[x] if x in sample_tex_names.keys() else x for x in used_bkgr_names]
    from HNL.Samples.sample import Sample
    signal_legendnames = ['HNL '+str(int(Sample.getSignalMass(signal_name)))+ '#scale[0.5]{ }GeV' for signal_name in signal_names]
    from HNL.Plotting.plot import Plot
    p = Plot(signal, signal_legendnames+bkgr_legendnames, name, bkgr_hist = bkgr, observed_hist = observed, draw_ratio = True, year = year, era = era, color_palette = 'HNL', color_palette_bkgr = 'HNLfromTau', y_log=True, y_name='Events', x_name = x_name, extra_text = extra_text, syst_hist = syst_hist, ignore_stat_err = True, for_paper = True)

    p.drawHist(output_name, min_cutoff = 1, custom_labels = x_label, normalize_signal='med', custom_divisions = 804 if x_label is not None else None)

def cleanUp(original_folder):
    new_workspace = getNewWorkspaceLocation(original_folder)
    os.system('rm -r {0}'.format(new_workspace))


############################################################
##########              PLOTTING                ############
############################################################

#
# Figure 8
#

#
# Figure 8.1
#
def plotFig8p1():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/cutbased/postfit/NoTau')
    #ch1 = EEE-Mu L1-4
    #ch2 = EEE-Mu L9-12
    #ch3 = EEE-Mu L5-8
    #ch4 = EEE-Mu L13-16
    #ch5 = MuMuMu-E L1-4
    #ch6 = MuMuMu-E L9-12
    #ch7 = MuMuMu-E L5-8
    #ch8 = MuMuMu-E L13-16
    
    #Stepwise first L1-4
    channels = ['ch1', 'ch5']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/A-EEE-Mu-searchregion.shapes.root', 'A-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/A-MuMuMu-E-searchregion.shapes.root', 'A-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/A-EEE-Mu-searchregion.shapes.root', 'A-EEE-Mu/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/A-MuMuMu-E-searchregion.shapes.root', 'A-MuMuMu-E/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/A-EEE-Mu-searchregion.shapes.root', 'A-EEE-Mu/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/A-MuMuMu-E-searchregion.shapes.root', 'A-MuMuMu-E/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_A = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    
    #Stepwise L5-8
    channels = ['ch3', 'ch7']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/B-EEE-Mu-searchregion.shapes.root', 'B-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/B-MuMuMu-E-searchregion.shapes.root', 'B-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/B-EEE-Mu-searchregion.shapes.root', 'B-EEE-Mu/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/B-MuMuMu-E-searchregion.shapes.root', 'B-MuMuMu-E/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/B-EEE-Mu-searchregion.shapes.root', 'B-EEE-Mu/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/B-MuMuMu-E-searchregion.shapes.root', 'B-MuMuMu-E/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_B = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    
    #Stepwise L5-8
    channels = ['ch2', 'ch6']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-EEE-Mu-searchregion.shapes.root', 'C-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-MuMuMu-E-searchregion.shapes.root', 'C-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-EEE-Mu-searchregion.shapes.root', 'C-EEE-Mu/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-MuMuMu-E-searchregion.shapes.root', 'C-MuMuMu-E/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-EEE-Mu-searchregion.shapes.root', 'C-EEE-Mu/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-MuMuMu-E-searchregion.shapes.root', 'C-MuMuMu-E/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_C = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    
    #Stepwise L5-8
    channels = ['ch4', 'ch8']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-EEE-Mu-searchregion.shapes.root', 'D-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-MuMuMu-E-searchregion.shapes.root', 'D-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-EEE-Mu-searchregion.shapes.root', 'D-EEE-Mu/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-MuMuMu-E-searchregion.shapes.root', 'D-MuMuMu-E/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-EEE-Mu-searchregion.shapes.root', 'D-EEE-Mu/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-MuMuMu-E-searchregion.shapes.root', 'D-MuMuMu-E/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_D = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    
    #Combine
    hist_dict = combineLateralyList([hist_dict_A, hist_dict_B, hist_dict_C, hist_dict_D])
    extra_text = loadExtraText('0#tau_{h}', 'tau', 6e-4)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig8', ['La{0}'.format(x) for x in xrange(1, 9)]+['Lb{0}'.format(x) for x in xrange(1, 9)], 'Search region', extra_text, '8p1', True)
    cleanUp(original_file)

#
# Figure 8.2
#

def plotFig8p2():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/cutbased/postfit/SingleTau')
    #ch1 = TauEE L1-4
    #ch2 = TauEE L9-12
    #ch3 = TauEE L5-8
    #ch4 = TauEE L13-16
    #ch5 = TauEMu L1-4
    #ch6 = TauEMu L5-8
    #ch7 = TauMuMu L1-4
    #ch8 = TauMuMu L9-12
    #ch9 = TauMuMu L5-8
    #ch10 = TauMuMu L13-16
    
    #Stepwise first L1-4
    channels = ['ch1', 'ch5', 'ch7']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/A-TauEE-searchregion.shapes.root', 'A-TauEE/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/A-TauEMu-searchregion.shapes.root', 'A-TauEMu/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/A-TauMuMu-searchregion.shapes.root', 'A-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/A-TauEE-searchregion.shapes.root', 'A-TauEE/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/A-TauEMu-searchregion.shapes.root', 'A-TauEMu/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/A-TauMuMu-searchregion.shapes.root', 'A-TauMuMu/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/A-TauEE-searchregion.shapes.root', 'A-TauEE/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/A-TauEMu-searchregion.shapes.root', 'A-TauEMu/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/A-TauMuMu-searchregion.shapes.root', 'A-TauMuMu/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_A = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    cleanUp(original_file)
    
    #Stepwise L5-8
    channels = ['ch3', 'ch6', 'ch9']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/B-TauEE-searchregion.shapes.root', 'B-TauEE/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/B-TauEMu-searchregion.shapes.root', 'B-TauEMu/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/B-TauMuMu-searchregion.shapes.root', 'B-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/B-TauEE-searchregion.shapes.root', 'B-TauEE/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/B-TauEMu-searchregion.shapes.root', 'B-TauEMu/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/B-TauMuMu-searchregion.shapes.root', 'B-TauMuMu/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/B-TauEE-searchregion.shapes.root', 'B-TauEE/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/B-TauEMu-searchregion.shapes.root', 'B-TauEMu/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/B-TauMuMu-searchregion.shapes.root', 'B-TauMuMu/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_B = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    cleanUp(original_file)
    
    #Stepwise L9-12
    channels = ['ch2', 'ch8']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-TauEE-searchregion.shapes.root', 'C-TauEE/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-TauMuMu-searchregion.shapes.root', 'C-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-TauEE-searchregion.shapes.root', 'C-TauEE/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-TauMuMu-searchregion.shapes.root', 'C-TauMuMu/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-TauEE-searchregion.shapes.root', 'C-TauEE/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-TauMuMu-searchregion.shapes.root', 'C-TauMuMu/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_C = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    cleanUp(original_file)
    
    #Stepwise L13-16
    channels = ['ch4', 'ch10']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-TauEE-searchregion.shapes.root', 'D-TauEE/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-TauMuMu-searchregion.shapes.root', 'D-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-TauEE-searchregion.shapes.root', 'D-TauEE/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-TauMuMu-searchregion.shapes.root', 'D-TauMuMu/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-TauEE-searchregion.shapes.root', 'D-TauEE/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-TauMuMu-searchregion.shapes.root', 'D-TauMuMu/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_D = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    
    #Combine
    hist_dict = combineLateralyList([hist_dict_A, hist_dict_B, hist_dict_C, hist_dict_D])
    extra_text = loadExtraText('1#tau_{h}', 'tau', 6e-4)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig8', ['La{0}'.format(x) for x in xrange(1, 9)]+['Lb{0}'.format(x) for x in xrange(1, 9)], 'Search region', extra_text, '8p2', True)
    cleanUp(original_file)

#
# Figure 8.3
#

def plotFig8p3():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
    #ch1 = EEE-Mu Hb
    #ch2 = EEE-Mu Ha
    #ch3 = MuMuMu-E Hb
    #ch4 = MuMuMu-E Ha
    #ch5 = TauEE Hb
    #ch6 = TauEE Ha
    #ch7 = TauEMu Ha
    #ch8 = TauMuMu Hb
    #ch9 = TauMuMu Ha
    
    #Stepwise first L1-4
    channels = ['ch2', 'ch4']
    signal_files = {
        'HNL-tau-m85-Vsq1.0e+00-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m85-Vsq1.0e+00-prompt/Majorana/F-EEE-Mu-searchregion.shapes.root', 'F-EEE-Mu/HNL-tau-m85-Vsq1.0e+00-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m85-Vsq1.0e+00-prompt/Majorana/F-MuMuMu-E-searchregion.shapes.root', 'F-MuMuMu-E/HNL-tau-m85-Vsq1.0e+00-prompt']],
        'HNL-tau-m200-Vsq4.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m200-Vsq4.0em01-prompt/Majorana/F-EEE-Mu-searchregion.shapes.root', 'F-EEE-Mu/HNL-tau-m200-Vsq4.0em01-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m200-Vsq4.0em01-prompt/Majorana/F-MuMuMu-E-searchregion.shapes.root', 'F-MuMuMu-E/HNL-tau-m200-Vsq4.0em01-prompt']],
        'HNL-tau-m300-Vsq7.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m300-Vsq7.0em01-prompt/Majorana/F-EEE-Mu-searchregion.shapes.root', 'F-EEE-Mu/HNL-tau-m300-Vsq7.0em01-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m300-Vsq7.0em01-prompt/Majorana/F-MuMuMu-E-searchregion.shapes.root', 'F-MuMuMu-E/HNL-tau-m300-Vsq7.0em01-prompt']]
    }
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 4e-1)
    
    extra_text = loadExtraText('0#tau_{h}', 'tau', 4e-1)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig8', ['Ha{0}'.format(x) for x in xrange(1, 10)], 'Search region', extra_text, '8p3', True)
    cleanUp(original_file)
    
#
# Figure 8.4
#
    
def plotFig8p4():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
    #ch1 = EEE-Mu Hb
    #ch2 = EEE-Mu Ha
    #ch3 = MuMuMu-E Hb
    #ch4 = MuMuMu-E Ha
    #ch5 = TauEE Hb
    #ch6 = TauEE Ha
    #ch7 = TauEMu Ha
    #ch8 = TauMuMu Hb
    #ch9 = TauMuMu Ha
    
    channels = ['ch6', 'ch7', 'ch9']
    signal_files = {
        'HNL-tau-m85-Vsq1.0e+00-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m85-Vsq1.0e+00-prompt/Majorana/F-TauEE-searchregion.shapes.root', 'F-TauEE/HNL-tau-m85-Vsq1.0e+00-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m85-Vsq1.0e+00-prompt/Majorana/F-TauEMu-searchregion.shapes.root', 'F-TauEMu/HNL-tau-m85-Vsq1.0e+00-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m85-Vsq1.0e+00-prompt/Majorana/F-TauMuMu-searchregion.shapes.root', 'F-TauMuMu/HNL-tau-m85-Vsq1.0e+00-prompt']],
        'HNL-tau-m200-Vsq4.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m200-Vsq4.0em01-prompt/Majorana/F-TauEE-searchregion.shapes.root', 'F-TauEE/HNL-tau-m200-Vsq4.0em01-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m200-Vsq4.0em01-prompt/Majorana/F-TauEMu-searchregion.shapes.root', 'F-TauEMu/HNL-tau-m200-Vsq4.0em01-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m200-Vsq4.0em01-prompt/Majorana/F-TauMuMu-searchregion.shapes.root', 'F-TauMuMu/HNL-tau-m200-Vsq4.0em01-prompt']],
        'HNL-tau-m300-Vsq7.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m300-Vsq7.0em01-prompt/Majorana/F-TauEE-searchregion.shapes.root', 'F-TauEE/HNL-tau-m300-Vsq7.0em01-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m300-Vsq7.0em01-prompt/Majorana/F-TauEMu-searchregion.shapes.root', 'F-TauEMu/HNL-tau-m300-Vsq7.0em01-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m300-Vsq7.0em01-prompt/Majorana/F-TauMuMu-searchregion.shapes.root', 'F-TauMuMu/HNL-tau-m300-Vsq7.0em01-prompt']]
    }
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 4e-1)
    
    extra_text = loadExtraText('1#tau_{h}', 'tau', 4e-1)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig8', ['Ha{0}'.format(x) for x in xrange(1, 10)], 'Search region', extra_text, '8p4', True)
    cleanUp(original_file)

#
# Figure 8.5
#

def plotFig8p5():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
    #ch1 = EEE-Mu Hb
    #ch2 = EEE-Mu Ha
    #ch3 = MuMuMu-E Hb
    #ch4 = MuMuMu-E Ha
    #ch5 = TauEE Hb
    #ch6 = TauEE Ha
    #ch7 = TauEMu Ha
    #ch8 = TauMuMu Hb
    #ch9 = TauMuMu Ha
    
    #Stepwise first L1-4
    channels = ['ch1', 'ch3']
    signal_files = {
        'HNL-tau-m85-Vsq1.0e+00-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m85-Vsq1.0e+00-prompt/Majorana/E-EEE-Mu-searchregion.shapes.root', 'E-EEE-Mu/HNL-tau-m85-Vsq1.0e+00-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m85-Vsq1.0e+00-prompt/Majorana/E-MuMuMu-E-searchregion.shapes.root', 'E-MuMuMu-E/HNL-tau-m85-Vsq1.0e+00-prompt']],
        'HNL-tau-m200-Vsq4.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m200-Vsq4.0em01-prompt/Majorana/E-EEE-Mu-searchregion.shapes.root', 'E-EEE-Mu/HNL-tau-m200-Vsq4.0em01-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m200-Vsq4.0em01-prompt/Majorana/E-MuMuMu-E-searchregion.shapes.root', 'E-MuMuMu-E/HNL-tau-m200-Vsq4.0em01-prompt']],
        'HNL-tau-m300-Vsq7.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m300-Vsq7.0em01-prompt/Majorana/E-EEE-Mu-searchregion.shapes.root', 'E-EEE-Mu/HNL-tau-m300-Vsq7.0em01-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m300-Vsq7.0em01-prompt/Majorana/E-MuMuMu-E-searchregion.shapes.root', 'E-MuMuMu-E/HNL-tau-m300-Vsq7.0em01-prompt']]
    }
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 4e-1)
    
    extra_text = loadExtraText('0#tau_{h}', 'tau', 4e-1)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig8', ['Hb{0}'.format(x) for x in xrange(1, 17)], 'Search region', extra_text, '8p5', True)
    cleanUp(original_file)

#
# Figure 8.6
#

def plotFig8p6():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
    #ch1 = EEE-Mu Hb
    #ch2 = EEE-Mu Ha
    #ch3 = MuMuMu-E Hb
    #ch4 = MuMuMu-E Ha
    #ch5 = TauEE Hb
    #ch6 = TauEE Ha
    #ch7 = TauEMu Ha
    #ch8 = TauMuMu Hb
    #ch9 = TauMuMu Ha
    
    channels = ['ch5', 'ch8']
    signal_files = {
        'HNL-tau-m85-Vsq1.0e+00-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m85-Vsq1.0e+00-prompt/Majorana/E-TauEE-searchregion.shapes.root', 'E-TauEE/HNL-tau-m85-Vsq1.0e+00-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m85-Vsq1.0e+00-prompt/Majorana/E-TauMuMu-searchregion.shapes.root', 'E-TauMuMu/HNL-tau-m85-Vsq1.0e+00-prompt']],
        'HNL-tau-m200-Vsq4.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m200-Vsq4.0em01-prompt/Majorana/E-TauEE-searchregion.shapes.root', 'E-TauEE/HNL-tau-m200-Vsq4.0em01-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m200-Vsq4.0em01-prompt/Majorana/E-TauMuMu-searchregion.shapes.root', 'E-TauMuMu/HNL-tau-m200-Vsq4.0em01-prompt']],
        'HNL-tau-m300-Vsq7.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m300-Vsq7.0em01-prompt/Majorana/E-TauEE-searchregion.shapes.root', 'E-TauEE/HNL-tau-m300-Vsq7.0em01-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m300-Vsq7.0em01-prompt/Majorana/E-TauMuMu-searchregion.shapes.root', 'E-TauMuMu/HNL-tau-m300-Vsq7.0em01-prompt']]
    }
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 4e-1)
    
    extra_text = loadExtraText('1#tau_{h}', 'tau', 4e-1)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig8', ['Hb1', 'Hb2-3']+['Hb{0}'.format(x) for x in xrange(4, 17)], 'Search region', extra_text, '8p6', True)
    cleanUp(original_file)

############
# Figure 9 #
############

#
# Figure 9.1
#

def plotFig9p1():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/e/HNL-e-m30-Vsq4.0em06-prompt/shapes/custom-lowestmass/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    channels = ['ch3', 'ch4']
    
    signal_files = {
        'HNL-e-m20-Vsq4.0em06-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/C-EEE-Mu-lowestmasse.shapes.root', 'C-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/D-EEE-Mu-lowestmasse.shapes.root', 'D-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt']],
        'HNL-e-m40-Vsq6.0em06-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/C-EEE-Mu-lowestmasse.shapes.root', 'C-EEE-Mu/HNL-e-m40-Vsq6.0em06-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/D-EEE-Mu-lowestmasse.shapes.root', 'D-EEE-Mu/HNL-e-m40-Vsq6.0em06-prompt']],
        'HNL-e-m60-Vsq2.0em05-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/C-EEE-Mu-lowestmasse.shapes.root', 'C-EEE-Mu/HNL-e-m60-Vsq2.0em05-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/D-EEE-Mu-lowestmasse.shapes.root', 'D-EEE-Mu/HNL-e-m60-Vsq2.0em05-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 6.0e-6)
    
    extra_text = loadExtraText('eee/ee#mu', 'e', 6.0e-6)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig9', None, 'BDT(10#minus40, e, 0#tau_{h}) score', extra_text, '9p1')
    cleanUp(original_file)

#
# Figure 9.2
#

def plotFig9p2():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/mu/HNL-mu-m30-Vsq2.0em06-prompt/shapes/custom-lowestmass/postfit/NoTau')
    #ch7 = MuMuMu-E L9-12
    #ch8 = MuMuMu-E L13-16
    channels = ['ch7', 'ch8']
    
    signal_files = {
        'HNL-mu-m20-Vsq2.0em06-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/C-MuMuMu-E-lowestmassmu.shapes.root', 'C-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/D-MuMuMu-E-lowestmassmu.shapes.root', 'D-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt']],
        'HNL-mu-m40-Vsq2.0em06-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/C-MuMuMu-E-lowestmassmu.shapes.root', 'C-MuMuMu-E/HNL-mu-m40-Vsq2.0em06-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/D-MuMuMu-E-lowestmassmu.shapes.root', 'D-MuMuMu-E/HNL-mu-m40-Vsq2.0em06-prompt']],
        'HNL-mu-m60-Vsq6.0em06-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/C-MuMuMu-E-lowestmassmu.shapes.root', 'C-MuMuMu-E/HNL-mu-m60-Vsq6.0em06-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/D-MuMuMu-E-lowestmassmu.shapes.root', 'D-MuMuMu-E/HNL-mu-m60-Vsq6.0em06-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 2.0e-6)
    
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'mu', 2e-6)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig9', None, 'BDT(10#minus40, #mu, 0#tau_{h}) score', extra_text, '9p2')
    cleanUp(original_file)

#
# Figure 9.3
#

def plotFig9p3():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/e/HNL-e-m60-Vsq2.0em05-prompt/shapes/custom-lowmass/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    channels = ['ch3', 'ch4']
    
    signal_files = {
        'HNL-e-m20-Vsq4.0em06-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/C-EEE-Mu-lowmasse.shapes.root', 'C-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/D-EEE-Mu-lowmasse.shapes.root', 'D-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt']],
        'HNL-e-m40-Vsq6.0em06-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/C-EEE-Mu-lowmasse.shapes.root', 'C-EEE-Mu/HNL-e-m40-Vsq6.0em06-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/D-EEE-Mu-lowmasse.shapes.root', 'D-EEE-Mu/HNL-e-m40-Vsq6.0em06-prompt']],
        'HNL-e-m60-Vsq2.0em05-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/C-EEE-Mu-lowmasse.shapes.root', 'C-EEE-Mu/HNL-e-m60-Vsq2.0em05-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/D-EEE-Mu-lowmasse.shapes.root', 'D-EEE-Mu/HNL-e-m60-Vsq2.0em05-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 6.0e-6)
    
    extra_text = loadExtraText('eee/ee#mu', 'e', 6.0e-6)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig9', None, 'BDT(50#minus75, e, 0#tau_{h}) score', extra_text, '9p3')
    cleanUp(original_file)

#
# Figure 9.4
#

def plotFig9p4():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/mu/HNL-mu-m60-Vsq6.0em06-prompt/shapes/custom-lowmass/postfit/NoTau')
    #ch7 = MuMuMu-E L9-12
    #ch8 = MuMuMu-E L13-16
    channels = ['ch7', 'ch8']
    
    signal_files = {
        'HNL-mu-m20-Vsq2.0em06-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/C-MuMuMu-E-lowmassmu.shapes.root', 'C-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/D-MuMuMu-E-lowmassmu.shapes.root', 'D-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt']],
        'HNL-mu-m40-Vsq2.0em06-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/C-MuMuMu-E-lowmassmu.shapes.root', 'C-MuMuMu-E/HNL-mu-m40-Vsq2.0em06-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/D-MuMuMu-E-lowmassmu.shapes.root', 'D-MuMuMu-E/HNL-mu-m40-Vsq2.0em06-prompt']],
        'HNL-mu-m60-Vsq6.0em06-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/C-MuMuMu-E-lowmassmu.shapes.root', 'C-MuMuMu-E/HNL-mu-m60-Vsq6.0em06-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/D-MuMuMu-E-lowmassmu.shapes.root', 'D-MuMuMu-E/HNL-mu-m60-Vsq6.0em06-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 2.0e-6)
    
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'mu', 2e-6)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig9', None, 'BDT(50#minus75, #mu, 0#tau_{h}) score', extra_text, '9p4')
    cleanUp(original_file)

#############
# Figure 10 #
#############

#
# Figure 10.1
#

def plotFig10p1():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowestmass/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    #ch7 = MuMuMu-E L9-12
    #ch8 = MuMuMu-E L13-16
    channels = ['ch3', 'ch4', 'ch7', 'ch8']
    
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-EEE-Mu-lowestmasstaulep.shapes.root', 'C-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-EEE-Mu-lowestmasstaulep.shapes.root', 'D-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-MuMuMu-E-lowestmasstaulep.shapes.root', 'C-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-MuMuMu-E-lowestmasstaulep.shapes.root', 'D-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-EEE-Mu-lowestmasstaulep.shapes.root', 'C-EEE-Mu/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-EEE-Mu-lowestmasstaulep.shapes.root', 'D-EEE-Mu/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-MuMuMu-E-lowestmasstaulep.shapes.root', 'C-MuMuMu-E/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-MuMuMu-E-lowestmasstaulep.shapes.root', 'D-MuMuMu-E/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-EEE-Mu-lowestmasstaulep.shapes.root', 'C-EEE-Mu/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-EEE-Mu-lowestmasstaulep.shapes.root', 'D-EEE-Mu/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-MuMuMu-E-lowestmasstaulep.shapes.root', 'C-MuMuMu-E/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-MuMuMu-E-lowestmasstaulep.shapes.root', 'D-MuMuMu-E/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 6.0e-4)
    
    extra_text = loadExtraText('0#tau_{h}', 'tau', 6.0e-4)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig10', None, 'BDT(10#minus40, #tau, 0#tau_{h}) score', extra_text, '10p1')
    cleanUp(original_file)
    
#
# Figure 10.2
#
    
def plotFig10p2():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowestmass/postfit/SingleTau')
    #ch3 = TauEE L9-12
    #ch4 = TauEE L13-16
    #ch9 = TauMuMu L9-12
    #ch10 = TauMuMu L13-16
    channels = ['ch3', 'ch4', 'ch9', 'ch10']
    
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-TauEE-lowestmasstauhad.shapes.root', 'C-TauEE/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-TauEE-lowestmasstauhad.shapes.root', 'D-TauEE/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-TauMuMu-lowestmasstauhad.shapes.root', 'C-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-TauMuMu-lowestmasstauhad.shapes.root', 'D-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-TauEE-lowestmasstauhad.shapes.root', 'C-TauEE/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-TauEE-lowestmasstauhad.shapes.root', 'D-TauEE/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-TauMuMu-lowestmasstauhad.shapes.root', 'C-TauMuMu/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-TauMuMu-lowestmasstauhad.shapes.root', 'D-TauMuMu/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-TauEE-lowestmasstauhad.shapes.root', 'C-TauEE/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-TauEE-lowestmasstauhad.shapes.root', 'D-TauEE/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-TauMuMu-lowestmasstauhad.shapes.root', 'C-TauMuMu/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-TauMuMu-lowestmasstauhad.shapes.root', 'D-TauMuMu/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 6.0e-4)
    
    extra_text = loadExtraText('1#tau_{h}', 'tau', 6.0e-4)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig10', None, 'BDT(10#minus40, #tau, 1#tau_{h}) score', extra_text, '10p2')
    cleanUp(original_file)
    
#
# Figure 10.3
#
    
def plotFig10p3():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowmass/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    #ch7 = MuMuMu-E L9-12
    #ch8 = MuMuMu-E L13-16
    channels = ['ch3', 'ch4', 'ch7', 'ch8']
    
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-EEE-Mu-lowmasstaulep.shapes.root', 'C-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-EEE-Mu-lowmasstaulep.shapes.root', 'D-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-MuMuMu-E-lowmasstaulep.shapes.root', 'C-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-MuMuMu-E-lowmasstaulep.shapes.root', 'D-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-EEE-Mu-lowmasstaulep.shapes.root', 'C-EEE-Mu/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-EEE-Mu-lowmasstaulep.shapes.root', 'D-EEE-Mu/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-MuMuMu-E-lowmasstaulep.shapes.root', 'C-MuMuMu-E/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-MuMuMu-E-lowmasstaulep.shapes.root', 'D-MuMuMu-E/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-EEE-Mu-lowmasstaulep.shapes.root', 'C-EEE-Mu/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-EEE-Mu-lowmasstaulep.shapes.root', 'D-EEE-Mu/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-MuMuMu-E-lowmasstaulep.shapes.root', 'C-MuMuMu-E/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-MuMuMu-E-lowmasstaulep.shapes.root', 'D-MuMuMu-E/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 6.0e-4)
    
    extra_text = loadExtraText('0#tau_{h}', 'tau', 6.0e-4)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig10', None, 'BDT(50#minus75, #tau, 0#tau_{h}) score', extra_text, '10p3')
    cleanUp(original_file)
    
#
# Figure 10.4
#

def plotFig10p4():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowmass/postfit/SingleTau')
    #ch3 = TauEE L9-12
    #ch4 = TauEE L13-16
    #ch9 = TauMuMu L9-12
    #ch10 = TauMuMu L13-16
    channels = ['ch3', 'ch4', 'ch9', 'ch10']
    
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-TauEE-lowmasstauhad.shapes.root', 'C-TauEE/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-TauEE-lowmasstauhad.shapes.root', 'D-TauEE/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-TauMuMu-lowmasstauhad.shapes.root', 'C-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-TauMuMu-lowmasstauhad.shapes.root', 'D-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-TauEE-lowmasstauhad.shapes.root', 'C-TauEE/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-TauEE-lowmasstauhad.shapes.root', 'D-TauEE/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-TauMuMu-lowmasstauhad.shapes.root', 'C-TauMuMu/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-TauMuMu-lowmasstauhad.shapes.root', 'D-TauMuMu/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-TauEE-lowmasstauhad.shapes.root', 'C-TauEE/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-TauEE-lowmasstauhad.shapes.root', 'D-TauEE/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-TauMuMu-lowmasstauhad.shapes.root', 'C-TauMuMu/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-TauMuMu-lowmasstauhad.shapes.root', 'D-TauMuMu/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 6.0e-4)
    
    extra_text = loadExtraText('1#tau_{h}', 'tau', 6.0e-4)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig10', None, 'BDT(50#minus75, #tau, 1#tau_{h}) score', extra_text, '10p4')
    cleanUp(original_file)
    
#############
# Figure 11 #
#############
    
#
# Figure 11.1
#
    
def plotFig11p1():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/e/HNL-e-m200-Vsq5.0em03-prompt/shapes/custom-mediummass85100/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    channels = ['ch1', 'ch2']
    
    signal_files = {
        'HNL-e-m85-Vsq1.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m85-Vsq1.0em03-prompt/Majorana/E-EEE-Mu-mediummass85100e.shapes.root', 'E-EEE-Mu/HNL-e-m85-Vsq1.0em03-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m85-Vsq1.0em03-prompt/Majorana/F-EEE-Mu-mediummass85100e.shapes.root', 'F-EEE-Mu/HNL-e-m85-Vsq1.0em03-prompt']],
        'HNL-e-m150-Vsq3.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m150-Vsq3.0em03-prompt/Majorana/E-EEE-Mu-mediummass85100e.shapes.root', 'E-EEE-Mu/HNL-e-m150-Vsq3.0em03-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m150-Vsq3.0em03-prompt/Majorana/F-EEE-Mu-mediummass85100e.shapes.root', 'F-EEE-Mu/HNL-e-m150-Vsq3.0em03-prompt']],
        'HNL-e-m300-Vsq1.0em02-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m300-Vsq1.0em02-prompt/Majorana/E-EEE-Mu-mediummass85100e.shapes.root', 'E-EEE-Mu/HNL-e-m300-Vsq1.0em02-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m300-Vsq1.0em02-prompt/Majorana/F-EEE-Mu-mediummass85100e.shapes.root', 'F-EEE-Mu/HNL-e-m300-Vsq1.0em02-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 3e-3)
    
    extra_text = loadExtraText('eee/ee#mu', 'e', 3e-3)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig11', None, 'BDT(85#minus150, e, 0#tau_{h}) score', extra_text, '11p1')
    cleanUp(original_file)
    
#
# Figure 11.2
#
    
def plotFig11p2():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/mu/HNL-mu-m200-Vsq4.0em03-prompt/shapes/custom-mediummass85100/postfit/NoTau')
    #ch3 = MuMuMu-E E
    #ch4 = MuMuMu-E F
    channels = ['ch3', 'ch4']
    
    signal_files = {
        'HNL-mu-m85-Vsq7.0em04-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m85-Vsq7.0em04-prompt/Majorana/E-MuMuMu-E-mediummass85100mu.shapes.root', 'E-MuMuMu-E/HNL-mu-m85-Vsq7.0em04-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m85-Vsq7.0em04-prompt/Majorana/F-MuMuMu-E-mediummass85100mu.shapes.root', 'F-MuMuMu-E/HNL-mu-m85-Vsq7.0em04-prompt']],
        'HNL-mu-m150-Vsq2.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m150-Vsq2.0em03-prompt/Majorana/E-MuMuMu-E-mediummass85100mu.shapes.root', 'E-MuMuMu-E/HNL-mu-m150-Vsq2.0em03-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m150-Vsq2.0em03-prompt/Majorana/F-MuMuMu-E-mediummass85100mu.shapes.root', 'F-MuMuMu-E/HNL-mu-m150-Vsq2.0em03-prompt']],
        'HNL-mu-m300-Vsq8.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m300-Vsq8.0em03-prompt/Majorana/E-MuMuMu-E-mediummass85100mu.shapes.root', 'E-MuMuMu-E/HNL-mu-m300-Vsq8.0em03-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m300-Vsq8.0em03-prompt/Majorana/F-MuMuMu-E-mediummass85100mu.shapes.root', 'F-MuMuMu-E/HNL-mu-m300-Vsq8.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 2e-3)
    
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'mu', 2e-3)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig11', None, 'BDT(85#minus150, mu, 0#tau_{h}) score', extra_text, '11p2')
    cleanUp(original_file)
    
#
# Figure 11.3
#
    
def plotFig11p3():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/e/HNL-e-m200-Vsq5.0em03-prompt/shapes/custom-mediummass150200/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    channels = ['ch1', 'ch2']
    
    signal_files = {
        'HNL-e-m85-Vsq1.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m85-Vsq1.0em03-prompt/Majorana/E-EEE-Mu-mediummass150200e.shapes.root', 'E-EEE-Mu/HNL-e-m85-Vsq1.0em03-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m85-Vsq1.0em03-prompt/Majorana/F-EEE-Mu-mediummass150200e.shapes.root', 'F-EEE-Mu/HNL-e-m85-Vsq1.0em03-prompt']],
        'HNL-e-m150-Vsq3.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m150-Vsq3.0em03-prompt/Majorana/E-EEE-Mu-mediummass150200e.shapes.root', 'E-EEE-Mu/HNL-e-m150-Vsq3.0em03-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m150-Vsq3.0em03-prompt/Majorana/F-EEE-Mu-mediummass150200e.shapes.root', 'F-EEE-Mu/HNL-e-m150-Vsq3.0em03-prompt']],
        'HNL-e-m300-Vsq1.0em02-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m300-Vsq1.0em02-prompt/Majorana/E-EEE-Mu-mediummass150200e.shapes.root', 'E-EEE-Mu/HNL-e-m300-Vsq1.0em02-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m300-Vsq1.0em02-prompt/Majorana/F-EEE-Mu-mediummass150200e.shapes.root', 'F-EEE-Mu/HNL-e-m300-Vsq1.0em02-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 3e-3)
    
    extra_text = loadExtraText('eee/ee#mu', 'e', 3e-3)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig11', None, 'BDT(200#minus250, e, 0#tau_{h}) score', extra_text, '11p3')
    cleanUp(original_file)
    
#
# Figure 11.4
#
    
def plotFig11p4():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/mu/HNL-mu-m200-Vsq4.0em03-prompt/shapes/custom-mediummass150200/postfit/NoTau')
    #ch3 = MuMuMu-E E
    #ch4 = MuMuMu-E F
    channels = ['ch3', 'ch4']
    
    signal_files = {
        'HNL-mu-m85-Vsq7.0em04-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m85-Vsq7.0em04-prompt/Majorana/E-MuMuMu-E-mediummass150200mu.shapes.root', 'E-MuMuMu-E/HNL-mu-m85-Vsq7.0em04-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m85-Vsq7.0em04-prompt/Majorana/F-MuMuMu-E-mediummass150200mu.shapes.root', 'F-MuMuMu-E/HNL-mu-m85-Vsq7.0em04-prompt']],
        'HNL-mu-m150-Vsq2.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m150-Vsq2.0em03-prompt/Majorana/E-MuMuMu-E-mediummass150200mu.shapes.root', 'E-MuMuMu-E/HNL-mu-m150-Vsq2.0em03-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m150-Vsq2.0em03-prompt/Majorana/F-MuMuMu-E-mediummass150200mu.shapes.root', 'F-MuMuMu-E/HNL-mu-m150-Vsq2.0em03-prompt']],
        'HNL-mu-m300-Vsq8.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m300-Vsq8.0em03-prompt/Majorana/E-MuMuMu-E-mediummass150200mu.shapes.root', 'E-MuMuMu-E/HNL-mu-m300-Vsq8.0em03-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m300-Vsq8.0em03-prompt/Majorana/F-MuMuMu-E-mediummass150200mu.shapes.root', 'F-MuMuMu-E/HNL-mu-m300-Vsq8.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 2e-3)
    
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'mu', 2e-3)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig11', None, 'BDT(200#minus250, mu, 0#tau_{h}) score', extra_text, '11p4')
    cleanUp(original_file)

#
# Figure 11.5
#
    
def plotFig11p5():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/e/HNL-e-m200-Vsq5.0em03-prompt/shapes/custom-mediummass250400/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    channels = ['ch1', 'ch2']
    
    signal_files = {
        'HNL-e-m85-Vsq1.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m85-Vsq1.0em03-prompt/Majorana/E-EEE-Mu-mediummass250400e.shapes.root', 'E-EEE-Mu/HNL-e-m85-Vsq1.0em03-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m85-Vsq1.0em03-prompt/Majorana/F-EEE-Mu-mediummass250400e.shapes.root', 'F-EEE-Mu/HNL-e-m85-Vsq1.0em03-prompt']],
        'HNL-e-m150-Vsq3.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m150-Vsq3.0em03-prompt/Majorana/E-EEE-Mu-mediummass250400e.shapes.root', 'E-EEE-Mu/HNL-e-m150-Vsq3.0em03-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m150-Vsq3.0em03-prompt/Majorana/F-EEE-Mu-mediummass250400e.shapes.root', 'F-EEE-Mu/HNL-e-m150-Vsq3.0em03-prompt']],
        'HNL-e-m300-Vsq1.0em02-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m300-Vsq1.0em02-prompt/Majorana/E-EEE-Mu-mediummass250400e.shapes.root', 'E-EEE-Mu/HNL-e-m300-Vsq1.0em02-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m300-Vsq1.0em02-prompt/Majorana/F-EEE-Mu-mediummass250400e.shapes.root', 'F-EEE-Mu/HNL-e-m300-Vsq1.0em02-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 3e-3)
    
    extra_text = loadExtraText('eee/ee#mu', 'e', 3e-3)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig11', None, 'BDT(300#minus400, e, 0#tau_{h}) score', extra_text, '11p5')
    cleanUp(original_file)
    
#
# Figure 11.6
#
    
def plotFig11p6():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/mu/HNL-mu-m200-Vsq4.0em03-prompt/shapes/custom-mediummass250400/postfit/NoTau')
    #ch3 = MuMuMu-E E
    #ch4 = MuMuMu-E F
    channels = ['ch3', 'ch4']
    
    signal_files = {
        'HNL-mu-m85-Vsq7.0em04-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m85-Vsq7.0em04-prompt/Majorana/E-MuMuMu-E-mediummass250400mu.shapes.root', 'E-MuMuMu-E/HNL-mu-m85-Vsq7.0em04-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m85-Vsq7.0em04-prompt/Majorana/F-MuMuMu-E-mediummass250400mu.shapes.root', 'F-MuMuMu-E/HNL-mu-m85-Vsq7.0em04-prompt']],
        'HNL-mu-m150-Vsq2.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m150-Vsq2.0em03-prompt/Majorana/E-MuMuMu-E-mediummass250400mu.shapes.root', 'E-MuMuMu-E/HNL-mu-m150-Vsq2.0em03-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m150-Vsq2.0em03-prompt/Majorana/F-MuMuMu-E-mediummass250400mu.shapes.root', 'F-MuMuMu-E/HNL-mu-m150-Vsq2.0em03-prompt']],
        'HNL-mu-m300-Vsq8.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m300-Vsq8.0em03-prompt/Majorana/E-MuMuMu-E-mediummass250400mu.shapes.root', 'E-MuMuMu-E/HNL-mu-m300-Vsq8.0em03-prompt'],
            ['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m300-Vsq8.0em03-prompt/Majorana/F-MuMuMu-E-mediummass250400mu.shapes.root', 'F-MuMuMu-E/HNL-mu-m300-Vsq8.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 2e-3)
    
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'mu', 2e-3)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig11', None, 'BDT(300#minus400, mu, 0#tau_{h}) score', extra_text, '11p6')
    cleanUp(original_file)
   

#
# Figure 8.1 for electrons
#

def plotFig8p1Electron():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/cutbased/postfit/NoTau')
    #ch1 = EEE-Mu L1-4
    #ch2 = EEE-Mu L9-12
    #ch3 = EEE-Mu L5-8
    #ch4 = EEE-Mu L13-16
    #ch5 = MuMuMu-E L1-4
    #ch6 = MuMuMu-E L9-12
    #ch7 = MuMuMu-E L5-8
    #ch8 = MuMuMu-E L13-16
    
    #Stepwise first L1-4
    channels = ['ch1', 'ch5']
    signal_files = {
       'HNL-e-m20-Vsq4.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/A-EEE-Mu-searchregion.shapes.root', 'A-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/A-MuMuMu-E-searchregion.shapes.root', 'A-MuMuMu-E/HNL-e-m20-Vsq4.0em06-prompt']],
       'HNL-e-m40-Vsq6.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/A-EEE-Mu-searchregion.shapes.root', 'A-EEE-Mu/HNL-e-m40-Vsq6.0em06-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/A-MuMuMu-E-searchregion.shapes.root', 'A-MuMuMu-E/HNL-e-m40-Vsq6.0em06-prompt']],
       'HNL-e-m60-Vsq2.0em05-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/A-EEE-Mu-searchregion.shapes.root', 'A-EEE-Mu/HNL-e-m60-Vsq2.0em05-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/A-MuMuMu-E-searchregion.shapes.root', 'A-MuMuMu-E/HNL-e-m60-Vsq2.0em05-prompt']]
    }
    hist_dict_A = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-6)
    
    #Stepwise L5-8
    channels = ['ch3', 'ch7']
    signal_files = {
       'HNL-e-m20-Vsq4.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/B-EEE-Mu-searchregion.shapes.root', 'B-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/B-MuMuMu-E-searchregion.shapes.root', 'B-MuMuMu-E/HNL-e-m20-Vsq4.0em06-prompt']],
       'HNL-e-m40-Vsq6.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/B-EEE-Mu-searchregion.shapes.root', 'B-EEE-Mu/HNL-e-m40-Vsq6.0em06-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/B-MuMuMu-E-searchregion.shapes.root', 'B-MuMuMu-E/HNL-e-m40-Vsq6.0em06-prompt']],
       'HNL-e-m60-Vsq2.0em05-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/B-EEE-Mu-searchregion.shapes.root', 'B-EEE-Mu/HNL-e-m60-Vsq2.0em05-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/B-MuMuMu-E-searchregion.shapes.root', 'B-MuMuMu-E/HNL-e-m60-Vsq2.0em05-prompt']]
    }
    hist_dict_B = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-6)
    
    #Stepwise L5-8
    channels = ['ch2', 'ch6']
    signal_files = {
       'HNL-e-m20-Vsq4.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/C-EEE-Mu-searchregion.shapes.root', 'C-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/C-MuMuMu-E-searchregion.shapes.root', 'C-MuMuMu-E/HNL-e-m20-Vsq4.0em06-prompt']],
       'HNL-e-m40-Vsq6.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/C-EEE-Mu-searchregion.shapes.root', 'C-EEE-Mu/HNL-e-m40-Vsq6.0em06-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/C-MuMuMu-E-searchregion.shapes.root', 'C-MuMuMu-E/HNL-e-m40-Vsq6.0em06-prompt']],
       'HNL-e-m60-Vsq2.0em05-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/C-EEE-Mu-searchregion.shapes.root', 'C-EEE-Mu/HNL-e-m60-Vsq2.0em05-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/C-MuMuMu-E-searchregion.shapes.root', 'C-MuMuMu-E/HNL-e-m60-Vsq2.0em05-prompt']]
    }
    hist_dict_C = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-6)
    
    #Stepwise L5-8
    channels = ['ch4', 'ch8']
    signal_files = {
       'HNL-e-m20-Vsq4.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/D-EEE-Mu-searchregion.shapes.root', 'D-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/D-MuMuMu-E-searchregion.shapes.root', 'D-MuMuMu-E/HNL-e-m20-Vsq4.0em06-prompt']],
       'HNL-e-m40-Vsq6.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/D-EEE-Mu-searchregion.shapes.root', 'D-EEE-Mu/HNL-e-m40-Vsq6.0em06-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/D-MuMuMu-E-searchregion.shapes.root', 'D-MuMuMu-E/HNL-e-m40-Vsq6.0em06-prompt']],
       'HNL-e-m60-Vsq2.0em05-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/D-EEE-Mu-searchregion.shapes.root', 'D-EEE-Mu/HNL-e-m60-Vsq2.0em05-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/D-MuMuMu-E-searchregion.shapes.root', 'D-MuMuMu-E/HNL-e-m60-Vsq2.0em05-prompt']]
    }
    hist_dict_D = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-6)
    
    #Combine
    hist_dict = combineLateralyList([hist_dict_A, hist_dict_B, hist_dict_C, hist_dict_D])
    extra_text = loadExtraText('0#tau_{h}', 'tau', 6e-6)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig8_electron', ['La{0}'.format(x) for x in xrange(1, 9)]+['Lb{0}'.format(x) for x in xrange(1, 9)], 'Search region', extra_text, '8p1')
    cleanUp(original_file)

#
# Figure 8.1 for muon
#

def plotFig8p1Muon():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/cutbased/postfit/NoTau')
    #ch1 = EEE-Mu L1-4
    #ch2 = EEE-Mu L9-12
    #ch3 = EEE-Mu L5-8
    #ch4 = EEE-Mu L13-16
    #ch5 = MuMuMu-E L1-4
    #ch6 = MuMuMu-E L9-12
    #ch7 = MuMuMu-E L5-8
    #ch8 = MuMuMu-E L13-16
    
    #Stepwise first L1-4
    channels = ['ch1', 'ch5']
    signal_files = {
       'HNL-mu-m20-Vsq2.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/A-EEE-Mu-searchregion.shapes.root', 'A-EEE-Mu/HNL-mu-m20-Vsq2.0em06-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/A-MuMuMu-E-searchregion.shapes.root', 'A-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt']],
       'HNL-mu-m40-Vsq2.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/A-EEE-Mu-searchregion.shapes.root', 'A-EEE-Mu/HNL-mu-m40-Vsq2.0em06-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/A-MuMuMu-E-searchregion.shapes.root', 'A-MuMuMu-E/HNL-mu-m40-Vsq2.0em06-prompt']],
       'HNL-mu-m60-Vsq6.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/A-EEE-Mu-searchregion.shapes.root', 'A-EEE-Mu/HNL-mu-m60-Vsq6.0em06-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/A-MuMuMu-E-searchregion.shapes.root', 'A-MuMuMu-E/HNL-mu-m60-Vsq6.0em06-prompt']]
    }
    hist_dict_A = loadHistograms(original_file, channels, signal_files, target_coupling = 2e-6)
    
    #Stepwise L5-8
    channels = ['ch3', 'ch7']
    signal_files = {
       'HNL-mu-m20-Vsq2.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/B-EEE-Mu-searchregion.shapes.root', 'B-EEE-Mu/HNL-mu-m20-Vsq2.0em06-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/B-MuMuMu-E-searchregion.shapes.root', 'B-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt']],
       'HNL-mu-m40-Vsq2.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/B-EEE-Mu-searchregion.shapes.root', 'B-EEE-Mu/HNL-mu-m40-Vsq2.0em06-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/B-MuMuMu-E-searchregion.shapes.root', 'B-MuMuMu-E/HNL-mu-m40-Vsq2.0em06-prompt']],
       'HNL-mu-m60-Vsq6.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/B-EEE-Mu-searchregion.shapes.root', 'B-EEE-Mu/HNL-mu-m60-Vsq6.0em06-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/B-MuMuMu-E-searchregion.shapes.root', 'B-MuMuMu-E/HNL-mu-m60-Vsq6.0em06-prompt']]
    }
    hist_dict_B = loadHistograms(original_file, channels, signal_files, target_coupling = 2e-6)
    
    #Stepwise L5-8
    channels = ['ch2', 'ch6']
    signal_files = {
       'HNL-mu-m20-Vsq2.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/C-EEE-Mu-searchregion.shapes.root', 'C-EEE-Mu/HNL-mu-m20-Vsq2.0em06-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/C-MuMuMu-E-searchregion.shapes.root', 'C-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt']],
       'HNL-mu-m40-Vsq2.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/C-EEE-Mu-searchregion.shapes.root', 'C-EEE-Mu/HNL-mu-m40-Vsq2.0em06-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/C-MuMuMu-E-searchregion.shapes.root', 'C-MuMuMu-E/HNL-mu-m40-Vsq2.0em06-prompt']],
       'HNL-mu-m60-Vsq6.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/C-EEE-Mu-searchregion.shapes.root', 'C-EEE-Mu/HNL-mu-m60-Vsq6.0em06-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/C-MuMuMu-E-searchregion.shapes.root', 'C-MuMuMu-E/HNL-mu-m60-Vsq6.0em06-prompt']]
    }
    hist_dict_C = loadHistograms(original_file, channels, signal_files, target_coupling = 2e-6)
    
    #Stepwise L5-8
    channels = ['ch4', 'ch8']
    signal_files = {
       'HNL-mu-m20-Vsq2.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/D-EEE-Mu-searchregion.shapes.root', 'D-EEE-Mu/HNL-mu-m20-Vsq2.0em06-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/D-MuMuMu-E-searchregion.shapes.root', 'D-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt']],
       'HNL-mu-m40-Vsq2.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/D-EEE-Mu-searchregion.shapes.root', 'D-EEE-Mu/HNL-mu-m40-Vsq2.0em06-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/D-MuMuMu-E-searchregion.shapes.root', 'D-MuMuMu-E/HNL-mu-m40-Vsq2.0em06-prompt']],
       'HNL-mu-m60-Vsq6.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/D-EEE-Mu-searchregion.shapes.root', 'D-EEE-Mu/HNL-mu-m60-Vsq6.0em06-prompt'],
           ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/D-MuMuMu-E-searchregion.shapes.root', 'D-MuMuMu-E/HNL-mu-m60-Vsq6.0em06-prompt']]
    }
    hist_dict_D = loadHistograms(original_file, channels, signal_files, target_coupling = 2e-6)
    
    #Combine
    hist_dict = combineLateralyList([hist_dict_A, hist_dict_B, hist_dict_C, hist_dict_D])
    extra_text = loadExtraText('0#tau_{h}', 'tau', 2e-6)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForPaper/fig8_muon', ['La{0}'.format(x) for x in xrange(1, 9)]+['Lb{0}'.format(x) for x in xrange(1, 9)], 'Search region', extra_text, '8p1')
    cleanUp(original_file)

if __name__ == '__main__':
    #plotFig8p1() 
    #plotFig8p2() 
    #plotFig8p3() 
    plotFig8p4() 
    #plotFig8p5() 
    #plotFig8p6() 
    #
    #plotFig9p1() 
    #plotFig9p2() 
    #plotFig9p3() 
    #plotFig9p4() 
    #
    #plotFig10p1() 
    #plotFig10p2() 
    #plotFig10p3() 
    #plotFig10p4() 
    #
    #plotFig11p1() 
    #plotFig11p2() 
    #plotFig11p3() 
    #plotFig11p4() 
    #plotFig11p5() 
    #plotFig11p6() 
    
    #plotFig8p1Electron() 
    #plotFig8p1Muon() 
