#! /usr/bin/env python

#
# Code to validate differences between reconstruction and id algorithms for light leptons
#

#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('first_selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
argParser.add_argument('second_selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
argParser.add_argument('--year',     action='store',      default=None,   help='Select year')
argParser.add_argument('--era',     action='store',       default='prelegacy', choices = ['UL', 'prelegacy'],   help='Select era')
argParser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?')
argParser.add_argument('--analysis',   action='store', default='HNL',  help='Select the strategy to use to separate signal from background', choices=['HNL', 'AN2017014', 'ewkino'])
argParser.add_argument('--strategy',   action='store', default='MVA',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA'])
argParser.add_argument('--logLevel',  action='store', default='INFO', help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])

args = argParser.parse_args()

from HNL.ObjectSelection.objectSelection import getObjectSelection

in_base_var = lambda sel, sample_name, flavor: os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'shapes', '-'.join([args.strategy, sel, args.region]), args.era+args.year, flavor, sample_name, 'NoTau.shapes.root')
# in_base_var = lambda sel, sample_name, flavor: os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'shapes', '-'.join([args.strategy, sel, args.region]), args.era+args.year, flavor, sample_name, 'EMuMu.shapes.root')

out_dir = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'Results', 'compareShapes', args.era+args.year, args.first_selection+'-'+args.second_selection)

from HNL.Samples.sampleManager import SampleManager
from HNL.Tools.helpers import getObjFromFile, rootFileContent
sm = SampleManager(args.era, args.year, 'noskim', 'allsignal_'+args.era+args.year)

from ROOT import TFile
for sample in sm.sample_outputs:
    if not '-e' in sample and not '-mu' in sample: continue
    flavor = sample.split('-')[1]

    
    shape1_file = TFile(in_base_var(args.first_selection, sample, flavor), 'read')
    shape_file1_content = rootFileContent(shape1_file)
    bkgr_samples = [x[0].split('/')[1] for x in shape_file1_content if not 'HNL' in x[0] and not "data_obs" in x[0]]
    shape1_file.Close()

    try:
        signal_shape1 = getObjFromFile(in_base_var(args.first_selection, sample, flavor), sample)
        signal_shape2 = getObjFromFile(in_base_var(args.second_selection, sample, flavor), sample)
    except:
        continue
    tot_bkgr_shape1 = None
    tot_bkgr_shape2 = None
    for ibkgr, bkgr in enumerate(bkgr_samples):
        if bkgr == 'other': 
            if ibkgr == 0: print "WARNING: FAULT IN INDICES"
            continue
        bkgr_shape1 = getObjFromFile(in_base_var(args.first_selection, sample, flavor), bkgr)
        bkgr_shape2 = getObjFromFile(in_base_var(args.second_selection, sample, flavor), bkgr)
        if ibkgr == 0:  
            tot_bkgr_shape1 = bkgr_shape1.Clone(bkgr)
            tot_bkgr_shape2 = bkgr_shape2.Clone(bkgr)
        else:           
            tot_bkgr_shape1.Add(bkgr_shape1)
            tot_bkgr_shape2.Add(bkgr_shape2)

        from HNL.Plotting.plot import Plot
        from HNL.Plotting.plottingTools import extraTextFormat
        scaled_signal_1 = signal_shape1.Clone('scaled_'+sample)
        scaled_signal_2 = signal_shape2.Clone('scaled_'+sample)

        scale_to_use = bkgr_shape1.GetSumOfWeights()/scaled_signal_1.GetSumOfWeights()
        scaled_signal_1.Scale(scale_to_use)
        scaled_signal_2.Scale(scale_to_use)

        from HNL.Tools.helpers import calculateSignificance
        significances = [calculateSignificance(signal_shape1, bkgr_shape1), calculateSignificance(signal_shape2, bkgr_shape2)]
        from HNL.Plotting.style import getHistDidar
        significances[0].SetLineColor(getHistDidar(0))
        significances[1].SetLineColor(getHistDidar(1))
        p = Plot([scaled_signal_1, scaled_signal_2], tex_names=['S '+args.first_selection, 'S '+args.second_selection, 'B '+args.first_selection, 'B '+args.second_selection], name=bkgr, bkgr_hist = [bkgr_shape1, bkgr_shape2], year = args.year, era = args.era, draw_significance=significances, color_palette_bkgr = 'shoop')
        p.drawHist(output_dir = out_dir+'/'+sample, bkgr_draw_option = 'EHistFilled')
        # p.drawHist(output_dir = out_dir+'/'+sample, bkgr_draw_option = 'EP')
    
    scaled_signal_1 = signal_shape1.Clone('scaled_'+sample)
    scaled_signal_2 = signal_shape2.Clone('scaled_'+sample)

    scale_to_use = tot_bkgr_shape1.GetSumOfWeights()/scaled_signal_1.GetSumOfWeights()
    scaled_signal_1.Scale(scale_to_use)
    scaled_signal_2.Scale(scale_to_use)

    significances = [calculateSignificance(signal_shape1, tot_bkgr_shape1), calculateSignificance(signal_shape2, tot_bkgr_shape2)]
    from HNL.Plotting.style import getHistDidar
    significances[0].SetLineColor(getHistDidar(0))
    significances[1].SetLineColor(getHistDidar(1))
    p = Plot([scaled_signal_1, scaled_signal_2], tex_names=['S '+args.first_selection, 'S '+args.second_selection, 'B '+args.first_selection, 'B '+args.second_selection], name='total', bkgr_hist = [tot_bkgr_shape1, tot_bkgr_shape2], year = args.year, era = args.era, draw_significance=significances, color_palette_bkgr = 'shoop')
    p.drawHist(output_dir = out_dir+'/'+sample, bkgr_draw_option = 'EHistFilled')

