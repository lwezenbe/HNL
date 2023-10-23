
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--input_file',   type=str, help='Input file')
submission_parser.add_argument('--output',   type=str, help='Compare to a specific card if it exists. If you want different selection use "selection/card" otherwise just "card"')
submission_parser.add_argument('--signal_name',   type=str, help='Compare to a specific card if it exists. If you want different selection use "selection/card" otherwise just "card"')
submission_parser.add_argument('--xnames', nargs = "*",  type=str, help='Compare to a specific card if it exists. If you want different selection use "selection/card" otherwise just "card"')
submission_parser.add_argument('--extratext', nargs = "*",  type=str, help='Compare to a specific card if it exists. If you want different selection use "selection/card" otherwise just "card"')
submission_parser.add_argument('--xlabels', nargs = "*",  type=str, help='Compare to a specific card if it exists. If you want different selection use "selection/card" otherwise just "card"')
submission_parser.add_argument('--paperPlots',   action='store_true',     default=False,  help='Slightly adapt the plots to be paper-approved')
args = argParser.parse_args()

input_base = '/storage_mnt/storage/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output'

input_file = os.path.join(input_base, args.input_file, 'postfitshapes.root')

#signal_name = 'HNL-e-m250-Vsq5.0em03-prompt'
signal_name = args.signal_name
observed_name = 'data_obs'
bkgr_names = ['Other', 'TT-T+X', 'WZ', 'XG', 'ZZ-H', 'charge-misid', 'non-prompt', 'triboson']
year = '2016post-2016pre-2017-2018'
era = 'UL'

from HNL.Plotting.plottingDicts import sample_tex_names
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


x_names = args.xnames * 2 if args.xnames is not None else [None]*len(all_channels)
extra_text = args.extratext * 2 if args.extratext is not None else [None]*len(all_channels)
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
labels = [label_dict[l] for l in args.xlabels]*2 if args.xlabels is not None else [None]*len(all_channels)

output = os.path.join(input_base, args.output, signal_name)
# Make plots
for ichannel, channel in enumerate(all_channels):
    from HNL.Tools.helpers import getObjFromFile
    from HNL.Tools.histogram import Histogram
    from HNL.Plotting.plottingTools import extraTextFormat
    signal = Histogram(getObjFromFile(input_file, channel+'/'+signal_name))
    observed = Histogram(getObjFromFile(input_file, channel+'/'+observed_name))
#    backgrounds = [Histogram(getObjFromFile(input_file, channel+'/'+b)) for b in bkgr_names] 
    backgrounds = []
    used_bkgr_names = []
    for b in bkgr_names:
        try:
            backgrounds.append(Histogram(getObjFromFile(input_file, channel+'/'+b)))
            used_bkgr_names.append(b)
        except:
            continue
        
    if args.paperPlots:
        for b, bn in zip(backgrounds, used_bkgr_names):
            if bn in ['triboson', 'TT-T+X', 'charge-misid']:
                backgrounds[used_bkgr_names.index('Other')].add(b)
                
        backgrounds.pop(used_bkgr_names.index('triboson'))        
        used_bkgr_names.pop(used_bkgr_names.index('triboson'))        
        backgrounds.pop(used_bkgr_names.index('TT-T+X'))        
        used_bkgr_names.pop(used_bkgr_names.index('TT-T+X'))        
        backgrounds.pop(used_bkgr_names.index('charge-misid'))        
        used_bkgr_names.pop(used_bkgr_names.index('charge-misid'))        


    syst_hist = Histogram(getObjFromFile(input_file, channel+'/TotalBkg'))

    tmp_extra_text = []
    tmp_extra_text.append(extraTextFormat('Postfit' if channel in postfit_channels else 'Prefit', xpos = 0.2, ypos = 0.74, textsize = None, align = 12))
    if extra_text[ichannel] is not None:
        sub_extra_text = extra_text[ichannel].split('|')
        for et in sub_extra_text:
            tmp_extra_text.append(extraTextFormat(et))

    bkgr_legendnames = [sample_tex_names[x] if x in sample_tex_names.keys() else x for x in used_bkgr_names]
    from HNL.Plotting.plot import Plot
    p = Plot(signal, [signal_legendname]+bkgr_legendnames, channel.split('/')[1], bkgr_hist = backgrounds, observed_hist = observed, draw_ratio = True, year = year, era = era, color_palette = 'HNL', color_palette_bkgr = 'HNLfromTau', y_log=True, y_name='Events', x_name = x_names[ichannel], extra_text = tmp_extra_text, syst_hist = syst_hist, ignore_stat_err = True, for_paper = args.paperPlots)

    p.drawHist(output, min_cutoff = 1, custom_labels = labels[ichannel])
