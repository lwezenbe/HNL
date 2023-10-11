import os
from HNL.Tools.helpers import getObjFromFile
from HNL.Tools.histogram import Histogram


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

def loadBackgrounds(input_file, bkgr_names, channel):
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


def drawPlot(signal, bkgr, observed, syst_hist, signal_names, bkgr_names, output_name, x_label, x_name, extra_text, name):

    for b, bn in zip(bkgr, bkgr_names):
        if bn in ['triboson', 'TT-T+X', 'charge-misid']:
            bkgr[bkgr_names.index('Other')].add(b)

    bkgr.pop(bkgr_names.index('triboson'))
    bkgr_names.pop(bkgr_names.index('triboson'))
    bkgr.pop(bkgr_names.index('TT-T+X'))
    bkgr_names.pop(bkgr_names.index('TT-T+X'))
    bkgr.pop(bkgr_names.index('charge-misid'))
    bkgr_names.pop(bkgr_names.index('charge-misid'))

    bkgr_legendnames = [sample_tex_names[x] if x in sample_tex_names.keys() else x for x in bkgr_names]
    from HNL.Samples.sample import Sample
    signal_legendnames = ['HNL '+str(Sample.getSignalMass(signal_name))+ 'GeV' for signal_name in signal_names]
    from HNL.Plotting.plot import Plot
    p = Plot(signal, signal_legendnames+bkgr_legendnames, name, bkgr_hist = bkgr, observed_hist = observed, draw_ratio = True, year = year, era = era, color_palette = 'HNL', color_palette_bkgr = 'HNLfromTau', y_log=True, y_name='Events', x_name = x_name, extra_text = extra_text, syst_hist = syst_hist, ignore_stat_err = True, for_paper = True)

    p.drawHist(output_name, min_cutoff = 1, custom_labels = x_label, normalize_signal='med')


def combineLaterely(hist1, hist2):
    from ROOT import TH1D
    hist1 = hist1.getHist()
    hist2 = hist2.getHist()
    n_bin1 = hist1.GetNbinsX()
    n_bin2 = hist2.GetNbinsX()
    n_newbins = n_bin1 + n_bin2
    new_hist = TH1D('combined_hist', 'combined_hist', n_newbins, 0., n_newbins)
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

    
    


############################################################
##########              PLOTTING                ############
############################################################

#
# Figure 8
#

# Top left
#bkgr_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m60-Vsq2.0em03-prompt/shapes/custom-lowmass/postfit/NoTau', 'postfitshapes.root')
#
#bkgr_eee_L1to4 = Histogram(getObjFromFile(input_file, channel+'/'+signal_name))

############
# Figure 9 #
############

#
# Figure 9.1
#

bkgr_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/e/HNL-e-m30-Vsq4.0em06-prompt/shapes/custom-lowestmass/postfit/NoTau', 'postfitshapes.root')
#ch3 = EEE-Mu L9-12
#ch4 = EEE-Mu L13-16
bkgr_ch3, bkgr_names_ch3 = loadBackgrounds(bkgr_file, bkgr_names, 'ch3')
bkgr_ch4, bkgr_names_ch4 = loadBackgrounds(bkgr_file, bkgr_names, 'ch4')
bkgr_ch3, bkgr_names_ch3 = addHist(bkgr_ch3, bkgr_ch4, bkgr_names_ch3, bkgr_names_ch4)

obs = loadObserved(bkgr_file, 'ch3')
obs.add(loadObserved(bkgr_file, 'ch4'))

sig_20 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/C-EEE-Mu-lowestmasse.shapes.root'), 'C-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt')
sig_20.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/D-EEE-Mu-lowestmasse.shapes.root'), 'D-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt'))
sig_40 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/C-EEE-Mu-lowestmasse.shapes.root'), 'C-EEE-Mu/HNL-e-m40-Vsq6.0em06-prompt')
sig_40.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/D-EEE-Mu-lowestmasse.shapes.root'), 'D-EEE-Mu/HNL-e-m40-Vsq6.0em06-prompt'))
sig_60 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/C-EEE-Mu-lowestmasse.shapes.root'), 'C-EEE-Mu/HNL-e-m60-Vsq2.0em05-prompt')
sig_60.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/D-EEE-Mu-lowestmasse.shapes.root'), 'D-EEE-Mu/HNL-e-m60-Vsq2.0em05-prompt'))
#Scale to 40 GeV sample
sig_20.scale(1.5)
sig_60.scale(0.3)

syst_hist = loadSyst(bkgr_file, 'ch3')
syst_hist.add(loadSyst(bkgr_file, 'ch4'))

extra_text = loadExtraText('eee/ee#mu', 'e', 6.0e-6)
drawPlot([sig_20, sig_40, sig_60], bkgr_ch3, obs, syst_hist, ['HNL-e-m20-Vsq4.0em06-prompt', 'HNL-e-m40-Vsq6.0em06-prompt', 'HNL-e-m60-Vsq2.0em05-prompt'], bkgr_names_ch3, output_base+'/PostFitPlotsForPaper/fig9', None, 'BDT(10-40, e, 0#tau_{h}) score', extra_text, '9p1')

#
# Figure 9.2
#
bkgr_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/mu/HNL-mu-m30-Vsq2.0em06-prompt/shapes/custom-lowestmass/postfit/NoTau', 'postfitshapes.root')
#ch7 = MuMuMu-E L9-12
#ch8 = MuMuMu-E L13-16
bkgr_ch7, bkgr_names_ch7 = loadBackgrounds(bkgr_file, bkgr_names, 'ch7')
bkgr_ch8, bkgr_names_ch8 = loadBackgrounds(bkgr_file, bkgr_names, 'ch8')
bkgr_ch7, bkgr_names_ch7 = addHist(bkgr_ch7, bkgr_ch8, bkgr_names_ch7, bkgr_names_ch8)

obs = loadObserved(bkgr_file, 'ch7')
obs.add(loadObserved(bkgr_file, 'ch8'))

sig_20 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/C-MuMuMu-E-lowestmassmu.shapes.root'), 'C-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt')
sig_20.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/D-MuMuMu-E-lowestmassmu.shapes.root'), 'D-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt'))
sig_40 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/C-MuMuMu-E-lowestmassmu.shapes.root'), 'C-MuMuMu-E/HNL-mu-m40-Vsq2.0em06-prompt')
sig_40.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/D-MuMuMu-E-lowestmassmu.shapes.root'), 'D-MuMuMu-E/HNL-mu-m40-Vsq2.0em06-prompt'))
sig_60 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/C-MuMuMu-E-lowestmassmu.shapes.root'), 'C-MuMuMu-E/HNL-mu-m60-Vsq6.0em06-prompt')
sig_60.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/D-MuMuMu-E-lowestmassmu.shapes.root'), 'D-MuMuMu-E/HNL-mu-m60-Vsq6.0em06-prompt'))
#Scale to 40 GeV sample
sig_20.scale(1.)
sig_60.scale(1./3.)

syst_hist = loadSyst(bkgr_file, 'ch7')
syst_hist.add(loadSyst(bkgr_file, 'ch7'))

extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'mu', 2e-6)
drawPlot([sig_20, sig_40, sig_60], bkgr_ch7, obs, syst_hist, ['HNL-mu-m20-Vsq2.0em06-prompt', 'HNL-mu-m40-Vsq2.0em06-prompt', 'HNL-mu-m60-Vsq6.0em06-prompt'], bkgr_names_ch7, output_base+'/PostFitPlotsForPaper/fig9', None, 'BDT(10-40, #mu, 0#tau_{h}) score', extra_text, '9p2')

#
# Figure 9.3
#

bkgr_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/e/HNL-e-m60-Vsq2.0em05-prompt/shapes/custom-lowmass/postfit/NoTau', 'postfitshapes.root')
#ch3 = EEE-Mu L9-12
#ch4 = EEE-Mu L13-16
bkgr_ch3, bkgr_names_ch3 = loadBackgrounds(bkgr_file, bkgr_names, 'ch3')
bkgr_ch4, bkgr_names_ch4 = loadBackgrounds(bkgr_file, bkgr_names, 'ch4')
bkgr_ch3, bkgr_names_ch3 = addHist(bkgr_ch3, bkgr_ch4, bkgr_names_ch3, bkgr_names_ch4)

obs = loadObserved(bkgr_file, 'ch3')
obs.add(loadObserved(bkgr_file, 'ch4'))

sig_20 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/C-EEE-Mu-lowmasse.shapes.root'), 'C-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt')
sig_20.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/D-EEE-Mu-lowmasse.shapes.root'), 'D-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt'))
sig_40 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/C-EEE-Mu-lowmasse.shapes.root'), 'C-EEE-Mu/HNL-e-m40-Vsq6.0em06-prompt')
sig_40.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/D-EEE-Mu-lowmasse.shapes.root'), 'D-EEE-Mu/HNL-e-m40-Vsq6.0em06-prompt'))
sig_60 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/C-EEE-Mu-lowmasse.shapes.root'), 'C-EEE-Mu/HNL-e-m60-Vsq2.0em05-prompt')
sig_60.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/D-EEE-Mu-lowmasse.shapes.root'), 'D-EEE-Mu/HNL-e-m60-Vsq2.0em05-prompt'))
#Scale to 40 GeV sample
sig_20.scale(1.5)
sig_60.scale(0.3)

syst_hist = loadSyst(bkgr_file, 'ch3')
syst_hist.add(loadSyst(bkgr_file, 'ch4'))

extra_text = loadExtraText('eee/ee#mu', 'e', 6.0e-6)
drawPlot([sig_20, sig_40, sig_60], bkgr_ch3, obs, syst_hist, ['HNL-e-m20-Vsq4.0em06-prompt', 'HNL-e-m40-Vsq6.0em06-prompt', 'HNL-e-m60-Vsq2.0em05-prompt'], bkgr_names_ch3, output_base+'/PostFitPlotsForPaper/fig9', None, 'BDT(50-75, e, 0#tau_{h}) score', extra_text, '9p3')

#
# Figure 9.4
#
bkgr_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/mu/HNL-mu-m60-Vsq6.0em06-prompt/shapes/custom-lowmass/postfit/NoTau', 'postfitshapes.root')
#ch7 = MuMuMu-E L9-12
#ch8 = MuMuMu-E L13-16
bkgr_ch7, bkgr_names_ch7 = loadBackgrounds(bkgr_file, bkgr_names, 'ch7')
bkgr_ch8, bkgr_names_ch8 = loadBackgrounds(bkgr_file, bkgr_names, 'ch8')
bkgr_ch7, bkgr_names_ch8 = addHist(bkgr_ch7, bkgr_ch8, bkgr_names_ch7, bkgr_names_ch8)

obs = loadObserved(bkgr_file, 'ch7')
obs.add(loadObserved(bkgr_file, 'ch8'))

sig_20 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/C-MuMuMu-E-lowmassmu.shapes.root'), 'C-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt')
sig_20.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/D-MuMuMu-E-lowmassmu.shapes.root'), 'D-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt'))
sig_40 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/C-MuMuMu-E-lowmassmu.shapes.root'), 'C-MuMuMu-E/HNL-mu-m40-Vsq2.0em06-prompt')
sig_40.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/D-MuMuMu-E-lowmassmu.shapes.root'), 'D-MuMuMu-E/HNL-mu-m40-Vsq2.0em06-prompt'))
sig_60 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/C-MuMuMu-E-lowmassmu.shapes.root'), 'C-MuMuMu-E/HNL-mu-m60-Vsq6.0em06-prompt')
sig_60.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/D-MuMuMu-E-lowmassmu.shapes.root'), 'D-MuMuMu-E/HNL-mu-m60-Vsq6.0em06-prompt'))
#Scale to 40 GeV sample
sig_20.scale(1.)
sig_60.scale(1./3.)

syst_hist = loadSyst(bkgr_file, 'ch7')
syst_hist.add(loadSyst(bkgr_file, 'ch7'))

extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'mu', 2e-6)
drawPlot([sig_20, sig_40, sig_60], bkgr_ch7, obs, syst_hist, ['HNL-mu-m20-Vsq2.0em06-prompt', 'HNL-mu-m40-Vsq2.0em06-prompt', 'HNL-mu-m60-Vsq6.0em06-prompt'], bkgr_names_ch7, output_base+'/PostFitPlotsForPaper/fig9', None, 'BDT(50-75, #mu, 0#tau_{h}) score', extra_text, '9p4')

#############
# Figure 10 #
#############

#
# Figure 10.1
#

bkgr_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowestmass/postfit/NoTau', 'postfitshapes.root')
#ch3 = EEE-Mu L9-12
#ch4 = EEE-Mu L13-16
#ch7 = MuMuMu-E L9-12
#ch8 = MuMuMu-E L13-16
bkgr_ch3, bkgr_names_ch3 = loadBackgrounds(bkgr_file, bkgr_names, 'ch3')
bkgr_ch4, bkgr_names_ch4 = loadBackgrounds(bkgr_file, bkgr_names, 'ch4')
bkgr_ch7, bkgr_names_ch7 = loadBackgrounds(bkgr_file, bkgr_names, 'ch7')
bkgr_ch8, bkgr_names_ch8 = loadBackgrounds(bkgr_file, bkgr_names, 'ch8')

bkgr_ch3, bkgr_names_ch3 = addHist(bkgr_ch3, bkgr_ch4, bkgr_names_ch3, bkgr_names_ch4)
bkgr_ch3, bkgr_names_ch3 = addHist(bkgr_ch3, bkgr_ch7, bkgr_names_ch3, bkgr_names_ch7)
bkgr_ch3, bkgr_names_ch3 = addHist(bkgr_ch3, bkgr_ch8, bkgr_names_ch3, bkgr_names_ch8)

obs = loadObserved(bkgr_file, 'ch3')
obs.add(loadObserved(bkgr_file, 'ch4'))
obs.add(loadObserved(bkgr_file, 'ch7'))
obs.add(loadObserved(bkgr_file, 'ch8'))

sig_20 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-EEE-Mu-lowestmasstaulep.shapes.root'), 'C-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt')
sig_20.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-EEE-Mu-lowestmasstaulep.shapes.root'), 'D-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt'))
sig_20.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-MuMuMu-E-lowestmasstaulep.shapes.root'), 'C-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt'))
sig_20.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-MuMuMu-E-lowestmasstaulep.shapes.root'), 'D-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt'))
sig_40 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-EEE-Mu-lowestmasstaulep.shapes.root'), 'C-EEE-Mu/HNL-tau-m40-Vsq6.0em04-prompt')
sig_40.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-EEE-Mu-lowestmasstaulep.shapes.root'), 'D-EEE-Mu/HNL-tau-m40-Vsq6.0em04-prompt'))
sig_40.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-MuMuMu-E-lowestmasstaulep.shapes.root'), 'C-MuMuMu-E/HNL-tau-m40-Vsq6.0em04-prompt'))
sig_40.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-MuMuMu-E-lowestmasstaulep.shapes.root'), 'D-MuMuMu-E/HNL-tau-m40-Vsq6.0em04-prompt'))
sig_60 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-EEE-Mu-lowestmasstaulep.shapes.root'), 'C-EEE-Mu/HNL-tau-m60-Vsq2.0em03-prompt')
sig_60.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-EEE-Mu-lowestmasstaulep.shapes.root'), 'D-EEE-Mu/HNL-tau-m60-Vsq2.0em03-prompt'))
sig_60.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-MuMuMu-E-lowestmasstaulep.shapes.root'), 'C-MuMuMu-E/HNL-tau-m60-Vsq2.0em03-prompt'))
sig_60.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-MuMuMu-E-lowestmasstaulep.shapes.root'), 'D-MuMuMu-E/HNL-tau-m60-Vsq2.0em03-prompt'))
#Scale to 40 GeV sample
sig_20.scale(1.2)
sig_60.scale(0.3)

syst_hist = loadSyst(bkgr_file, 'ch3')
syst_hist.add(loadSyst(bkgr_file, 'ch4'))
syst_hist.add(loadSyst(bkgr_file, 'ch7'))
syst_hist.add(loadSyst(bkgr_file, 'ch8'))

extra_text = loadExtraText('0#tau_{h}', 'tau', 6.0e-4)
drawPlot([sig_20, sig_40, sig_60], bkgr_ch3, obs, syst_hist, ['HNL-tau-m20-Vsq5.0em04-prompt', 'HNL-tau-m40-Vsq6.0em04-prompt', 'HNL-tau-m60-Vsq2.0em03-prompt'], bkgr_names_ch3, output_base+'/PostFitPlotsForPaper/fig10', None, 'BDT(10-40, #tau, 0#tau_{h}) score', extra_text, '10p1')

#
# Figure 10.2
#

bkgr_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowestmass/postfit/SingleTau', 'postfitshapes.root')
#ch3 = TauEE L9-12
#ch4 = TauEE L13-16
#ch9 = TauMuMu L9-12
#ch10 = TauMuMu L13-16
bkgr_ch3, bkgr_names_ch3 = loadBackgrounds(bkgr_file, bkgr_names, 'ch3')
bkgr_ch4, bkgr_names_ch4 = loadBackgrounds(bkgr_file, bkgr_names, 'ch4')
bkgr_ch9, bkgr_names_ch9 = loadBackgrounds(bkgr_file, bkgr_names, 'ch9')
bkgr_ch10, bkgr_names_ch10 = loadBackgrounds(bkgr_file, bkgr_names, 'ch10')

bkgr_ch3, bkgr_names_ch3 = addHist(bkgr_ch3, bkgr_ch4, bkgr_names_ch3, bkgr_names_ch4)
bkgr_ch3, bkgr_names_ch3 = addHist(bkgr_ch3, bkgr_ch9, bkgr_names_ch3, bkgr_names_ch9)
bkgr_ch3, bkgr_names_ch3 = addHist(bkgr_ch3, bkgr_ch10, bkgr_names_ch3, bkgr_names_ch10)

obs = loadObserved(bkgr_file, 'ch3')
obs.add(loadObserved(bkgr_file, 'ch4'))
obs.add(loadObserved(bkgr_file, 'ch9'))
obs.add(loadObserved(bkgr_file, 'ch10'))

sig_20 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-TauEE-lowestmasstauhad.shapes.root'), 'C-TauEE/HNL-tau-m20-Vsq5.0em04-prompt')
sig_20.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-TauEE-lowestmasstauhad.shapes.root'), 'D-TauEE/HNL-tau-m20-Vsq5.0em04-prompt'))
sig_20.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-TauMuMu-lowestmasstauhad.shapes.root'), 'C-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt'))
sig_20.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-TauMuMu-lowestmasstauhad.shapes.root'), 'D-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt'))
sig_40 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-TauEE-lowestmasstauhad.shapes.root'), 'C-TauEE/HNL-tau-m40-Vsq6.0em04-prompt')
sig_40.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-TauEE-lowestmasstauhad.shapes.root'), 'D-TauEE/HNL-tau-m40-Vsq6.0em04-prompt'))
sig_40.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-TauMuMu-lowestmasstauhad.shapes.root'), 'C-TauMuMu/HNL-tau-m40-Vsq6.0em04-prompt'))
sig_40.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-TauMuMu-lowestmasstauhad.shapes.root'), 'D-TauMuMu/HNL-tau-m40-Vsq6.0em04-prompt'))
sig_60 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-TauEE-lowestmasstauhad.shapes.root'), 'C-TauEE/HNL-tau-m60-Vsq2.0em03-prompt')
sig_60.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-TauEE-lowestmasstauhad.shapes.root'), 'D-TauEE/HNL-tau-m60-Vsq2.0em03-prompt'))
sig_60.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-TauMuMu-lowestmasstauhad.shapes.root'), 'C-TauMuMu/HNL-tau-m60-Vsq2.0em03-prompt'))
sig_60.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-TauMuMu-lowestmasstauhad.shapes.root'), 'D-TauMuMu/HNL-tau-m60-Vsq2.0em03-prompt'))
#Scale to 40 GeV sample
sig_20.scale(1.2)
sig_60.scale(0.3)

syst_hist = loadSyst(bkgr_file, 'ch3')
syst_hist.add(loadSyst(bkgr_file, 'ch4'))
syst_hist.add(loadSyst(bkgr_file, 'ch9'))
syst_hist.add(loadSyst(bkgr_file, 'ch10'))

extra_text = loadExtraText('1#tau_{h}', 'tau', 6.0e-4)
drawPlot([sig_20, sig_40, sig_60], bkgr_ch3, obs, syst_hist, ['HNL-tau-m20-Vsq5.0em04-prompt', 'HNL-tau-m40-Vsq6.0em04-prompt', 'HNL-tau-m60-Vsq2.0em03-prompt'], bkgr_names_ch3, output_base+'/PostFitPlotsForPaper/fig10', None, 'BDT(10-40, #tau, 1#tau_{h}) score', extra_text, '10p2')

#
# Figure 10.3
#

bkgr_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowmass/postfit/NoTau', 'postfitshapes.root')
#ch3 = EEE-Mu L9-12
#ch4 = EEE-Mu L13-16
#ch7 = MuMuMu-E L9-12
#ch8 = MuMuMu-E L13-16
bkgr_ch3, bkgr_names_ch3 = loadBackgrounds(bkgr_file, bkgr_names, 'ch3')
bkgr_ch4, bkgr_names_ch4 = loadBackgrounds(bkgr_file, bkgr_names, 'ch4')
bkgr_ch7, bkgr_names_ch7 = loadBackgrounds(bkgr_file, bkgr_names, 'ch7')
bkgr_ch8, bkgr_names_ch8 = loadBackgrounds(bkgr_file, bkgr_names, 'ch8')

bkgr_ch3, bkgr_names_ch3 = addHist(bkgr_ch3, bkgr_ch4, bkgr_names_ch3, bkgr_names_ch4)
bkgr_ch3, bkgr_names_ch3 = addHist(bkgr_ch3, bkgr_ch7, bkgr_names_ch3, bkgr_names_ch7)
bkgr_ch3, bkgr_names_ch3 = addHist(bkgr_ch3, bkgr_ch8, bkgr_names_ch3, bkgr_names_ch8)

obs = loadObserved(bkgr_file, 'ch3')
obs.add(loadObserved(bkgr_file, 'ch4'))
obs.add(loadObserved(bkgr_file, 'ch7'))
obs.add(loadObserved(bkgr_file, 'ch8'))

sig_20 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-EEE-Mu-lowmasstaulep.shapes.root'), 'C-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt')
sig_20.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-EEE-Mu-lowmasstaulep.shapes.root'), 'D-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt'))
sig_20.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-MuMuMu-E-lowmasstaulep.shapes.root'), 'C-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt'))
sig_20.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-MuMuMu-E-lowmasstaulep.shapes.root'), 'D-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt'))
sig_40 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-EEE-Mu-lowmasstaulep.shapes.root'), 'C-EEE-Mu/HNL-tau-m40-Vsq6.0em04-prompt')
sig_40.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-EEE-Mu-lowmasstaulep.shapes.root'), 'D-EEE-Mu/HNL-tau-m40-Vsq6.0em04-prompt'))
sig_40.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-MuMuMu-E-lowmasstaulep.shapes.root'), 'C-MuMuMu-E/HNL-tau-m40-Vsq6.0em04-prompt'))
sig_40.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-MuMuMu-E-lowmasstaulep.shapes.root'), 'D-MuMuMu-E/HNL-tau-m40-Vsq6.0em04-prompt'))
sig_60 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-EEE-Mu-lowmasstaulep.shapes.root'), 'C-EEE-Mu/HNL-tau-m60-Vsq2.0em03-prompt')
sig_60.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-EEE-Mu-lowmasstaulep.shapes.root'), 'D-EEE-Mu/HNL-tau-m60-Vsq2.0em03-prompt'))
sig_60.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-MuMuMu-E-lowmasstaulep.shapes.root'), 'C-MuMuMu-E/HNL-tau-m60-Vsq2.0em03-prompt'))
sig_60.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-MuMuMu-E-lowmasstaulep.shapes.root'), 'D-MuMuMu-E/HNL-tau-m60-Vsq2.0em03-prompt'))
#Scale to 40 GeV sample
sig_20.scale(1.2)
sig_60.scale(0.3)

syst_hist = loadSyst(bkgr_file, 'ch3')
syst_hist.add(loadSyst(bkgr_file, 'ch4'))
syst_hist.add(loadSyst(bkgr_file, 'ch7'))
syst_hist.add(loadSyst(bkgr_file, 'ch8'))

extra_text = loadExtraText('0#tau_{h}', 'tau', 6.0e-4)
drawPlot([sig_20, sig_40, sig_60], bkgr_ch3, obs, syst_hist, ['HNL-tau-m20-Vsq5.0em04-prompt', 'HNL-tau-m40-Vsq6.0em04-prompt', 'HNL-tau-m60-Vsq2.0em03-prompt'], bkgr_names_ch3, output_base+'/PostFitPlotsForPaper/fig10', None, 'BDT(50-75, #tau, 0#tau_{h}) score', extra_text, '10p3')

#
# Figure 10.4
#

bkgr_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowmass/postfit/SingleTau', 'postfitshapes.root')
#ch3 = TauEE L9-12
#ch4 = TauEE L13-16
#ch9 = TauMuMu L9-12
#ch10 = TauMuMu L13-16
bkgr_ch3, bkgr_names_ch3 = loadBackgrounds(bkgr_file, bkgr_names, 'ch3')
bkgr_ch4, bkgr_names_ch4 = loadBackgrounds(bkgr_file, bkgr_names, 'ch4')
bkgr_ch9, bkgr_names_ch9 = loadBackgrounds(bkgr_file, bkgr_names, 'ch9')
bkgr_ch10, bkgr_names_ch10 = loadBackgrounds(bkgr_file, bkgr_names, 'ch10')

bkgr_ch3, bkgr_names_ch3 = addHist(bkgr_ch3, bkgr_ch4, bkgr_names_ch3, bkgr_names_ch4)
bkgr_ch3, bkgr_names_ch3 = addHist(bkgr_ch3, bkgr_ch9, bkgr_names_ch3, bkgr_names_ch9)
bkgr_ch3, bkgr_names_ch3 = addHist(bkgr_ch3, bkgr_ch10, bkgr_names_ch3, bkgr_names_ch10)

obs = loadObserved(bkgr_file, 'ch3')
obs.add(loadObserved(bkgr_file, 'ch4'))
obs.add(loadObserved(bkgr_file, 'ch9'))
obs.add(loadObserved(bkgr_file, 'ch10'))

sig_20 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-TauEE-lowmasstauhad.shapes.root'), 'C-TauEE/HNL-tau-m20-Vsq5.0em04-prompt')
sig_20.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-TauEE-lowmasstauhad.shapes.root'), 'D-TauEE/HNL-tau-m20-Vsq5.0em04-prompt'))
sig_20.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-TauMuMu-lowmasstauhad.shapes.root'), 'C-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt'))
sig_20.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-TauMuMu-lowmasstauhad.shapes.root'), 'D-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt'))
sig_40 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-TauEE-lowmasstauhad.shapes.root'), 'C-TauEE/HNL-tau-m40-Vsq6.0em04-prompt')
sig_40.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-TauEE-lowmasstauhad.shapes.root'), 'D-TauEE/HNL-tau-m40-Vsq6.0em04-prompt'))
sig_40.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-TauMuMu-lowmasstauhad.shapes.root'), 'C-TauMuMu/HNL-tau-m40-Vsq6.0em04-prompt'))
sig_40.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-TauMuMu-lowmasstauhad.shapes.root'), 'D-TauMuMu/HNL-tau-m40-Vsq6.0em04-prompt'))
sig_60 = loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-TauEE-lowmasstauhad.shapes.root'), 'C-TauEE/HNL-tau-m60-Vsq2.0em03-prompt')
sig_60.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-TauEE-lowmasstauhad.shapes.root'), 'D-TauEE/HNL-tau-m60-Vsq2.0em03-prompt'))
sig_60.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-TauMuMu-lowmasstauhad.shapes.root'), 'C-TauMuMu/HNL-tau-m60-Vsq2.0em03-prompt'))
sig_60.add(loadSignal(os.path.join(shapes_base, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-TauMuMu-lowmasstauhad.shapes.root'), 'D-TauMuMu/HNL-tau-m60-Vsq2.0em03-prompt'))
#Scale to 40 GeV sample
sig_20.scale(1.2)
sig_60.scale(0.3)

syst_hist = loadSyst(bkgr_file, 'ch3')
syst_hist.add(loadSyst(bkgr_file, 'ch4'))
syst_hist.add(loadSyst(bkgr_file, 'ch9'))
syst_hist.add(loadSyst(bkgr_file, 'ch10'))

extra_text = loadExtraText('1#tau_{h}', 'tau', 6.0e-4)
drawPlot([sig_20, sig_40, sig_60], bkgr_ch3, obs, syst_hist, ['HNL-tau-m20-Vsq5.0em04-prompt', 'HNL-tau-m40-Vsq6.0em04-prompt', 'HNL-tau-m60-Vsq2.0em03-prompt'], bkgr_names_ch3, output_base+'/PostFitPlotsForPaper/fig10', None, 'BDT(50-75, #tau, 1#tau_{h}) score', extra_text, '10p4')
