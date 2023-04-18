input_file = '/storage_mnt/storage/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/e/HNL-e-m250-Vsq5.0em03-prompt/shapes/custom-mediummass250400/asymptotic/NoTau-SingleDataset/postfitshapes.root'
signal_name = 'HNL-e-m250-Vsq5.0em03-prompt'
observed_name = 'data_obs'
bkgr_names = ['Other', 'TT-T+X', 'WZ', 'XG', 'ZZ-H', 'charge-misid', 'non-prompt', 'triboson']
year = '2016post-2016pre-2017-2018'
era = 'UL'

from HNL.Plotting.plottingDicts import sample_tex_names
bkgr_legendnames = [sample_tex_names[x] if x in sample_tex_names.keys() else x for x in bkgr_names]
from HNL.Samples.sample import Sample
signal_legendname = 'HNL m_{N}='+str(Sample.getSignalMass(signal_name))+ 'GeV'


# Find all channels
from HNL.Tools.helpers import rootFileContent
from ROOT import TFile
root_input_file = TFile(input_file, 'read')
all_channels = [x[0] for x in rootFileContent(root_input_file)]
prefit_channels = [x for x in all_channels if 'prefit' in x]
postfit_channels = [x for x in all_channels if 'postfit' in x]
root_input_file.Close()

# Make plots
for channel in all_channels:
    from HNL.Tools.helpers import getObjFromFile
    from HNL.Tools.histogram import Histogram
    signal = Histogram(getObjFromFile(input_file, channel+'/'+signal_name))
    observed = Histogram(getObjFromFile(input_file, channel+'/'+observed_name))
    backgrounds = [Histogram(getObjFromFile(input_file, channel+'/'+b)) for b in bkgr_names]

    

    from HNL.Plotting.plot import Plot
    p = Plot(signal, [signal_legendname]+bkgr_legendnames, channel.split('/')[1], bkgr_hist = backgrounds, observed_hist = observed, draw_ratio = True, year = year, era = era, color_palette = 'HNL', color_palette_bkgr = 'HNLfromTau')

    p.drawHist(input_file.rsplit('/', 1)[0])
