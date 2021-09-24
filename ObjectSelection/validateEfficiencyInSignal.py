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
argParser.add_argument('--inBackground',   action='store_true', default=False,  help='Look at fake rates instead of efficiency')
argParser.add_argument('--useShapes',   action='store_true', default=False,  help='Look at the shapes')
argParser.add_argument('--logLevel',  action='store', default='INFO', help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])

args = argParser.parse_args()

from HNL.ObjectSelection.objectSelection import getObjectSelection

if args.inBackground:
    if not args.useShapes: 
        in_base_var = lambda sel, sample_name: os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 'data', 'plotVariables', '-'.join([args.strategy, sel, args.region, 'reco']), args.era+'-'+args.year, 'bkgr', sample_name)
else:
    in_base_var = lambda sel, sample_name: os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 'data', 'plotVariables', '-'.join([args.strategy, sel, args.region, 'reco']), args.era+'-'+args.year, 'signal', sample_name)

in_base_eff = lambda sel, flavor: os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'ObjectSelection', 'data', 'compareLeptonId', args.era+args.year, flavor, 'DY', getObjectSelection(sel)['light_algo']+'-ROC-'+flavor+'.root')
# in_base_misid = lambda sel: os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'EventSelection', 'data', 'calcExpectedObjectEfficiency', '-'.join([args.strategy, args.region, sel]), args.era+'-'+args.year, 'averageObjectSelection.root')
in_base_misid = lambda sel: os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'EventSelection', 'data', 'calcExpectedObjectEfficiency', '-'.join([args.strategy, 'baseline', sel]), args.era+'-'+args.year, 'averageObjectSelection.root')
out_dir = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'ObjectSelection', 'data', 'Results', 'validateSignalEfficiency', args.era+args.year, args.first_selection+'-'+args.second_selection)

from HNL.Samples.sampleManager import SampleManager
from HNL.Tools.helpers import isValidRootFile, getObjFromFile
if not args.inBackground:
    sm = SampleManager(args.era, args.year, 'noskim', 'allsignal_'+args.era+args.year)
else:
    # sm = SampleManager(args.era, args.year, 'noskim', 'fulllist_'+args.era+args.year)
    sm = SampleManager(args.era, args.year, 'noskim', 'EventSelection/fulllist_'+args.era+args.year)

from HNL.Tools.ROC import ROC
from HNL.Tools.histogram import Histogram
if not isValidRootFile(in_base_eff(args.first_selection, 'e')) or not isValidRootFile(in_base_eff(args.second_selection, 'mu')):
    raise RuntimeWarning("This code uses output from plotVariables. Please run: python ObjectSelection/compareLeptonId.py --year {0} --era {1}".format(args.year, args.era))
if not isValidRootFile(in_base_misid(args.first_selection)):
    raise RuntimeWarning("This code uses output from EventSelection. Please run: python calcExpectedObjectEfficiency.py --selection {2} --region {3} --year {0} --era {1}".format(args.year, args.era, args.first_selection, args.region))
if not isValidRootFile(in_base_misid(args.second_selection)):
    raise RuntimeWarning("This code uses output from EventSelection. Please run: python calcExpectedObjectEfficiency.py --selection {2} --region {3} --year {0} --era {1}".format(args.year, args.era, args.second_selection, args.region))

efficiencies = {}
for sel in [args.first_selection, args.second_selection]:
    efficiencies[sel] = {}
    for flavor in ['e', 'mu']:
        efficiencies[sel][flavor] = ROC(getObjectSelection(sel)['light_algo'], in_base_eff(sel, flavor)).getEfficiency().GetBinContent(3)

tot_eff = {}
tot_mis = {}
for sel in [args.first_selection, args.second_selection]:
    tot_eff[sel] = {
        'EEE' : efficiencies[sel]['e']**3,
        'EEMu' : efficiencies[sel]['e']* efficiencies[sel]['e'] * efficiencies[sel]['mu'],
        'EMuMu' : efficiencies[sel]['e'] * efficiencies[sel]['mu'] * efficiencies[sel]['mu'],
        'MuMuMu' : efficiencies[sel]['mu']**3,
    }
    tot_mis[sel] = {
        'EEE' : getObjFromFile(in_base_misid(sel), 'EEE').GetMean(),
        'EEMu' : getObjFromFile(in_base_misid(sel), 'EEMu').GetMean(),
        'EMuMu' : getObjFromFile(in_base_misid(sel), 'EMuMu').GetMean(),
        'MuMuMu' : getObjFromFile(in_base_misid(sel), 'MuMuMu').GetMean()
    }

list_of_hist_1 = {}
list_of_hist_2 = {}

from HNL.EventSelection.eventCategorization import CATEGORIES_TO_USE, ANALYSIS_CATEGORIES

if args.inBackground:
    samples_to_use = sm.sample_groups.keys()+['non-prompt']
else:
    samples_to_use = [s for s in sm.sample_outputs if '-e' in s or '-mu' in s]
    
for s in samples_to_use:
    list_of_hist_1[s] = {}
    list_of_hist_2[s] = {}

for sample in sm.sample_outputs:
    if args.inBackground:
        if 'HNL' in sample: continue
    else:
        if not '-e' in sample and not '-mu' in sample: continue
    if not isValidRootFile(in_base_var(args.first_selection, sample)+'/variables.root'):
        raise RuntimeWarning("This code uses output from plotVariables. Please run: python Analysis/plotVariables.py --year {0} --era {1} --selection {2} --customList allsignal_{1}{0} --region {3}".format(args.year, args.era, args.first_selection, args.region))
    if not isValidRootFile(in_base_var(args.second_selection, sample)+'/variables.root'):
        raise RuntimeWarning("This code uses output from plotVariables. Please run: python Analysis/plotVariables.py --year {0} --era {1} --selection {2} --customList allsignal_{1}{0} --region {3}".format(args.year, args.era, args.second_selection, args.region))
        
    var_dist = {}
    for sel in [args.first_selection, args.second_selection]:
        var_dist[sel] = {}
        for typ in ['prompt', 'nonprompt', 'total']:
            var_dist[sel][typ]= {}

            for c in CATEGORIES_TO_USE: 
                var_dist[sel][typ][c] = Histogram(getObjFromFile(in_base_var(sel, sample)+'/variables.root', 'l3eta/'+str(c)+'-l3eta-'+sample+'-'+typ)) 

            for ac in tot_eff[sel].keys():
                var_dist[sel][typ][ac] = var_dist[sel][typ][ANALYSIS_CATEGORIES[ac][0]].clone(ac)
                if len(ANALYSIS_CATEGORIES[ac]) > 1:
                    for c in ANALYSIS_CATEGORIES[ac][1:]:
                        var_dist[sel][typ][ac].add(var_dist[sel][typ][c])

    for ac in tot_eff[sel].keys():
        if args.inBackground:
            sg = [sk for sk in sm.sample_groups.keys() if sample in sm.sample_groups[sk]]
            if len(sg) == 0:
                print bkgr, "not part of any sample group"
                continue

            #Sort prompt into correct prompt category
            if ac not in list_of_hist_1[sg[0]].keys():
                list_of_hist_1[sg[0]][ac] = var_dist[args.first_selection]['prompt'][ac].clone(sg[0]+ac)
                list_of_hist_2[sg[0]][ac] = var_dist[args.second_selection]['prompt'][ac].clone(sg[0]+ac)
            else:
                list_of_hist_1[sg[0]][ac].add(var_dist[args.first_selection]['prompt'][ac])
                list_of_hist_2[sg[0]][ac].add(var_dist[args.second_selection]['prompt'][ac])

            if ac not in list_of_hist_1['non-prompt'].keys(): 
                list_of_hist_1['non-prompt'][ac] = var_dist[args.first_selection]['nonprompt'][ac].clone('non-prompt'+ac)
                list_of_hist_2['non-prompt'][ac] = var_dist[args.second_selection]['nonprompt'][ac].clone('non-prompt'+ac)
            else:

                list_of_hist_1['non-prompt'][ac].add(var_dist[args.first_selection]['nonprompt'][ac])
                list_of_hist_2['non-prompt'][ac].add(var_dist[args.second_selection]['nonprompt'][ac])                    
        else:
            list_of_hist_1[sample][ac] = var_dist[args.first_selection]['prompt'][ac].clone(sample+ac)
            list_of_hist_2[sample][ac] = var_dist[args.second_selection]['prompt'][ac].clone(sample+ac)

for sample in samples_to_use:
    for ac in tot_eff[args.first_selection].keys():
        if sample != 'non-prompt':
            SF = tot_eff[args.first_selection][ac]/tot_eff[args.second_selection][ac]
        else:
            SF = tot_mis[args.first_selection][ac]/tot_mis[args.second_selection][ac]
        from HNL.Plotting.plot import Plot
        from HNL.Plotting.plottingTools import extraTextFormat
        extra_text = [extraTextFormat(str(SF))]  #Text to display event type in plot
        p = Plot(list_of_hist_1[sample][ac], tex_names=[args.first_selection, args.second_selection], name=ac, bkgr_hist = list_of_hist_2[sample][ac], draw_ratio = True, year = args.year, era = args.era, extra_text = extra_text)
        p.drawHist(output_dir = out_dir+'/'+sample, ref_line = SF)

# if args.inBackground:
#     samples = [s for s in samples_to_use]
#     for c in tot_eff_1.keys():
#         tot_hist_1 = list_of_hist_1[samples[0]][c]
#         tot_hist_2 = list_of_hist_2[samples[0]][c]
#         for s in samples[1:]:
#             tot_hist_1.add(list_of_hist_1[s][c])
#             tot_hist_2.add(list_of_hist_2[s][c])
    
#         # SF = tot_eff_1[c]/tot_eff_2[c]
#         from HNL.Plotting.plot import Plot
#         from HNL.Plotting.plottingTools import extraTextFormat
#         # extra_text = [extraTextFormat(str(SF))]  #Text to display event type in plot
#         # p = Plot(tot_hist_1, tex_names=[args.first_selection, args.second_selection], name=c, bkgr_hist = tot_hist_2, draw_ratio = True, year = args.year, era = args.era, extra_text = extra_text)
#         p = Plot(tot_hist_1, tex_names=[args.first_selection, args.second_selection], name=c, bkgr_hist = tot_hist_2, draw_ratio = True, year = args.year, era = args.era)
#         p.drawHist(output_dir = out_dir+'/total', ref_line = SF)
    
