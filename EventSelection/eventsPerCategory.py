#! /usr/bin/env python

#
#       Code to calculate signal efficiency
#
# Can be used on RECO level, where you check how many events pass the reco selection
# Is also used to check how many events on a generator level pass certain pt cuts
#

import numpy as np
from HNL.Tools.histogram import Histogram
import ROOT

#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
argParser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018'])
argParser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
argParser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
argParser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
argParser.add_argument('--runLocal', action='store_true', default=False,  help='use local resources instead of Cream02')
argParser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
argParser.add_argument('--masses', type=int, nargs='*',  help='Only run or plot signal samples with mass given in this list')
argParser.add_argument('--coupling', action='store', default='',  help='Which coupling should be active?' , choices=['tau', 'e', 'mu', '2l', ''])
argParser.add_argument('--signalOnly', action='store_true', default=False,  help='Only launch jobs with signal samples')
argParser.add_argument('--backgroundOnly', action='store_true', default=False,  help='Only launch jobs with signal samples')
argParser.add_argument('--noskim', action='store_true', default=False,  help='Use no skim sample list')
argParser.add_argument('--makeTextFiles',   action='store_true', default=False,  help='make text files containing the number of events per category and sample')
argParser.add_argument('--makeBarCharts',   action='store_true', default=False,  help='make bar charts containing the number of events per category and sample')
argParser.add_argument('--makePieCharts',   action='store_true', default=False,  help='make pie charts containing the number of events per category and sample')
argParser.add_argument('--cutflow',   action='store_true', default=False,  help='print the cutflow')
argParser.add_argument('--oldAnalysisCuts',   action='store_true', default=False,  help='apply the cuts as in AN 2017-014')
argParser.add_argument('--massRegion',   action='store', default=None,  help='apply the cuts of high or low mass regions', choices=['high', 'low'])
argParser.add_argument('--message', type = str, default=None,  help='Add a file with a message in the plotting folder')
args = argParser.parse_args()


#
# Change some settings if this is a test
#
if args.isTest:
    args.isChild = True

    args.sample = 'DYJetsToLL-M-50' if not args.signalOnly else 'HNLe-60'
    args.subJob = '0'
    args.year = '2016'


#
# Load in the sample list 
#
from HNL.Samples.sample import createSampleList, getSampleFromList
if args.noskim:
    list_location = os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/sampleList_'+args.year+'_noskim.conf')
else:
    list_location = os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/sampleList_'+args.year+'_Reco.conf')
sample_list = createSampleList(list_location)

#
# function to have consistent categories in running and plotting
#
from HNL.EventSelection.eventCategorization import CATEGORIES, SUPER_CATEGORIES
from HNL.EventSelection.eventCategorization import CATEGORY_TEX_NAMES
def listOfCategories():
    return CATEGORIES + [15, 'total']

if not args.makeTextFiles and not args.makeBarCharts and not args.makePieCharts:
    #
    # Submit subjobs
    #
    if not args.isChild:
        from HNL.Tools.jobSubmitter import submitJobs
        jobs = []
        for sample in sample_list:
            if args.sample and args.sample not in sample.name: continue
            if args.signalOnly and not 'HNL' in sample.name: continue
            if args.backgroundOnly and 'HNL' in sample.name: continue
            if 'HNL' in sample.name and not 'HNL'+args.coupling in sample.name: continue
            if args.masses is not None and 'HNL' in sample.name and not any([str(m) in sample.name for m in args.masses]): continue
            for njob in xrange(sample.split_jobs):
                jobs += [(sample.name, str(njob))]

        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'calcSignalEfficiency')
        exit(0)

    #
    # Load in sample and chain
    #
    sample = getSampleFromList(sample_list, args.sample)
    chain = sample.initTree(needhcount=args.noskim)

    #
    # Import and create cutter to provide cut flow
    #
    from HNL.EventSelection.cutter import Cutter
    cutter = Cutter(chain = chain)

    if args.isTest:
        event_range = xrange(50)
    else:
        event_range = sample.getEventRange(args.subJob)    

    if 'HNL' in sample.name:
        chain.HNLmass = float(sample.name.rsplit('-', 1)[1])
    chain.year = int(args.year)

    #
    # Get luminosity weight
    #
    from HNL.Weights.lumiweight import LumiWeight
    lw = LumiWeight(sample, list_location)

    from HNL.EventSelection.eventCategorization import EventCategory
    ec = EventCategory(chain)

    list_of_numbers = {}
    for c in listOfCategories():
        list_of_numbers[c] = Histogram(str(c), lambda c: 0.5, ('', 'Events'), np.arange(0., 2., 1.))

    subjobAppendix = 'subJob' + args.subJob if args.subJob else ''
    selection_str = 'OldSel' if args.oldAnalysisCuts else 'NewCuts'
    mass_str = 'allMass' if args.massRegion is None else args.massRegion
    output_name = os.path.join(os.getcwd(), 'data', __file__.split('.')[0], selection_str, mass_str, sample.output)

    if args.isChild:
        output_name += '/tmp_'+sample.output

    output_name += '/'+ sample.name +'_events_' +subjobAppendix+ '.root'

    #
    # Loop over all events
    #
    from HNL.Tools.helpers import progress
    from HNL.EventSelection.eventSelection import select3Leptons, select3GenLeptons, passBaseCutsAN2017014, lowMassCuts, highMassCuts, calculateKinematicVariables, containsOSSF
    from HNL.EventSelection.signalLeptonMatcher import SignalLeptonMatcher
    from HNL.Triggers.triggerSelection import applyCustomTriggers, listOfTriggersAN2017014
    from HNL.ObjectSelection.leptonSelector import isFOLepton, isTightLepton
    print 'tot_range', len(event_range)
    for entry in event_range:
        
        chain.GetEntry(entry)
        progress(entry - event_range[0], len(event_range))

        if args.noskim: chain.weight = lw.getLumiWeight()
        else: chain.weight = chain.lumiweight

        cutter.cut(True, 'total')

        #Triggers
        if args.oldAnalysisCuts:
            if not cutter.cut(applyCustomTriggers(listOfTriggersAN2017014(chain)), 'pass_triggers'): continue

        #Selecting 3 leptons
        if not args.oldAnalysisCuts:
            if not cutter.cut(select3Leptons(chain, chain, light_algo = 'leptonMVAtZq', cutter=cutter), '3_tight_leptons'):   continue   
        else:            
            selected3FO = [(chain._lPt[l], l) for l in xrange(chain._nLight) if isFOLepton(chain, l, algo = 'cutbased')]
            if not cutter.cut(len(selected3FO) >= 3, '3 FO'): continue
            if not cutter.cut(select3Leptons(chain, chain, no_tau=True, light_algo = 'cutbased', cutter=cutter), '3_tight_leptons'):   continue   

        if args.massRegion == 'low':
            if not cutter.cut(not containsOSSF(chain), 'no OSSF'):      continue

        chain.category = ec.returnCategory()

        calculateKinematicVariables(chain, chain)
        if args.oldAnalysisCuts:
            if not passBaseCutsAN2017014(chain, chain, cutter): continue
            if args.massRegion is not None:
                if args.massRegion == 'high' and not highMassCuts(chain, chain, cutter): continue
                if args.massRegion == 'low' and not lowMassCuts(chain, chain, cutter): continue       

        list_of_numbers['total'].fill(chain, chain.weight)
        list_of_numbers[ec.returnCategory()].fill(chain, chain.weight)

    if args.isTest: exit(0)
    for i, h in enumerate(list_of_numbers.values()):
        if i == 0:
            h.write(output_name)
        else:
            h.write(output_name, append=True)

    cutter.saveCutFlow(output_name)
        
    if args.cutflow:
        from HNL.EventSelection.cutter import printCutFlow
        printCutFlow(output_name, output_name.rsplit('/', 1)[0]+'/cutflow.txt', sample.output)

#
# Merge if needed
#
else:
    from HNL.Tools.mergeFiles import merge
    import glob
    import os
    from HNL.Tools.helpers import getObjFromFile
    from HNL.Plotting.plot import Plot
    selection_str = 'OldSel' if args.oldAnalysisCuts else 'NewCuts'
    mass_str = 'allMass' if args.massRegion is None else args.massRegion
    in_files = glob.glob(os.path.expandvars('$CMSSW_BASE/src/HNL/EventSelection/data/eventsPerCategory/'+selection_str+'/'+mass_str+'/*')) 
    for f in in_files:
        if '.txt' in f: continue
        merge(f)

    #
    # Gather all the files
    #
    
    list_of_numbers = {'signal' : {}, 'bkgr' : {}}
    # if args.coupling == 'e':
    #     accepted_categories = [1, 3, 4, 6, 8, 9] # e coupling
    # elif args.coupling == 'mu':
    #     accepted_categories = [4, 5, 7, 8, 9] # mu coupling
    # else:
    accepted_categories = [i for i in CATEGORIES]
    x_names = [CATEGORY_TEX_NAMES[i] for i in accepted_categories]
    for sample in sample_list:
        path_name = os.path.expandvars('$CMSSW_BASE/src/HNL/EventSelection/data/eventsPerCategory/'+selection_str+'/'+mass_str+'/'+sample.output+'/events.root')
        is_signal = 'signal' if 'HNL' in sample.output else 'bkgr'
        if 'HNL' in sample.name and not 'HNL'+args.coupling in sample.name: continue
        if args.masses is not None and is_signal=='signal' and not any([str(m) == sample.output.rsplit('-M')[-1] for m in args.masses]): continue
        list_of_numbers[is_signal][sample.output] = {}
        for c in listOfCategories():
            if c not in accepted_categories: continue
            print sample.name, path_name, c
            list_of_numbers[is_signal][sample.output][c]= Histogram(getObjFromFile(path_name, str(c)+'/'+str(c)))
            
from HNL.Tools.helpers import makePathTimeStamped
destination = makePathTimeStamped(os.path.expandvars('$CMSSW_BASE/src/HNL/EventSelection/data/Results/eventsPerCategory/'+selection_str+'/'+mass_str))

#
# Make text files if requested
#
if args.makeTextFiles:
    def signalSortKey(sample_name):
        return int(sample_name.split('-M')[-1].split('/')[0])

    from HNL.Tools.helpers import getObjFromFile, rootFileContent
    from ROOT import TFile

    out_file = open(os.path.expandvars('$CMSSW_BASE/src/HNL/EventSelection/data/eventsPerCategory/'+selection_str+'/'+mass_str+'/table.txt'), 'w')
    out_file.write('\t \t tte \t ttm \t tee \t tem \t tmm \t lll \t total \n')

    out_file_tex = open(os.path.expandvars('$CMSSW_BASE/src/HNL/EventSelection/data/eventsPerCategory/'+selection_str+'/'+mass_str+'/table_tex.txt'), 'w')
    out_file_tex.write('\\begin{table}[] \n')
    out_file_tex.write("\\begin{tabular}{|l|l|l|l|l|l|l|l|} \n")
    out_file_tex.write("\hline \n")
    out_file_tex.write('& \\tau\\tau e & \\tau \\tau \\mu & \\tau e e & \\tau e \\mu & \\tau\\mu\\mu & lll & total \n')
    out_file_tex.write("\hline \n")

    for sample_name in sorted(list_of_numbers['signal'].keys(), key=lambda n : int(n.split('-M')[1])):
        out_file.write(sample_name+'\t')
        out_file_tex.write(sample_name+' & ')

        for c in sorted(list_of_numbers['signal'][sample_name].keys()):
            out_file.write('%4.3f' % list_of_numbers['signal'][sample_name][c].getHist().GetSumOfWeights()+'\t')
            out_file_tex.write('%4.3f' % list_of_numbers['signal'][sample_name][c].getHist().GetSumOfWeights())
            if not 'total' in str(c):
                out_file_tex.write(' & ')

        out_file.write('\n')
        out_file_tex.write('\\\\ \hline \n')

    out_file.write('-------------------------------------------------------------------- \n')
    out_file_tex.write('\\\\ \hline \n')

    for sample_name in list_of_numbers['bkgr'].keys():
        out_file.write(sample_name+'\t')
        out_file_tex.write(sample_name+' & ')

        for c in sorted(list_of_numbers['bkgr'][sample_name].keys()):
            out_file.write('%4.1f' % list_of_numbers['bkgr'][sample_name][c].getHist().GetSumOfWeights()+'\t')
            out_file_tex.write('%4.1f' % list_of_numbers['bkgr'][sample_name][c].getHist().GetSumOfWeights())
            if not 'total' in str(c):
                out_file_tex.write(' & ')

        out_file.write('\n')
        out_file_tex.write('\\\\ \hline \n')


    out_file.close()

    out_file_tex.write('\end{tabular} \n')
    out_file_tex.write('\end{table} \n')
    out_file_tex.close()


if args.makeBarCharts:

    for supercat in SUPER_CATEGORIES.keys():
        #
        # Bkgr
        #
        hist_to_plot = {}
        for sample_name in list_of_numbers['bkgr'].keys():
            # hist_to_plot[sample_name] = ROOT.TH1D(sample_name, sample_name, len(list_of_numbers['bkgr'][sample_name]), 0, len(list_of_numbers['bkgr'][sample_name]))
            hist_to_plot[sample_name] = ROOT.TH1D(sample_name+supercat, sample_name+supercat, len(SUPER_CATEGORIES[supercat]), 0, len(SUPER_CATEGORIES[supercat]))
            for i, c in enumerate(SUPER_CATEGORIES[supercat]):
                hist_to_plot[sample_name].SetBinContent(i+1, list_of_numbers['bkgr'][sample_name][c].getHist().GetSumOfWeights()) 
        x_names = [CATEGORY_TEX_NAMES[n] for n in SUPER_CATEGORIES[supercat]]
        p = Plot(hist_to_plot.values(), hist_to_plot.keys(), name = 'Events-bar-bkgr-'+supercat, x_name = x_names, y_name = 'Events', y_log='SingleTau' in supercat)
        p.drawBarChart(output_dir = destination, message = args.message)
        
        #
        # Signal
        #   
        hist_to_plot = []
        hist_names = []
        for sn, sample_name in enumerate(sorted(list_of_numbers['signal'].keys(), key=lambda k: int(k.split('-M')[-1]))):
            # hist_to_plot.append(ROOT.TH1D(sample_name, sample_name, len(list_of_numbers['signal'][sample_name]), 0, len(list_of_numbers['signal'][sample_name])))
            hist_to_plot.append(ROOT.TH1D(sample_name, sample_name, len(SUPER_CATEGORIES[supercat]), 0, len(SUPER_CATEGORIES[supercat])))
            hist_names.append(sample_name)
            for i, c in enumerate(SUPER_CATEGORIES[supercat]):
                hist_to_plot[sn].SetBinContent(i+1, list_of_numbers['signal'][sample_name][c].getHist().GetSumOfWeights()) 
        x_names = [CATEGORY_TEX_NAMES[n] for n in SUPER_CATEGORIES[supercat]]
        p = Plot(hist_to_plot, hist_names, name = 'Events-bar-signal-'+supercat+'-'+args.coupling, x_name = x_names, y_name = 'Events', y_log=True)
        p.drawBarChart(output_dir = destination, parallel_bins=True, message = args.message)
 
if args.makePieCharts:
    from HNL.Plotting.plottingTools import extraTextFormat
    example_sample = list_of_numbers['bkgr'].keys()[0]
    for i, c in enumerate(sorted(list_of_numbers['bkgr'][example_sample].keys())):
        hist_to_plot_pie = ROOT.TH1D(str(c)+'_pie', str(c), len(list_of_numbers['bkgr']), 0, len(list_of_numbers['bkgr']))
        for j, s in enumerate(list_of_numbers['bkgr'].keys()):
            hist_to_plot_pie.SetBinContent(j+1, list_of_numbers['bkgr'][s][c].getHist().GetSumOfWeights())

        try:
            extra_text = [extraTextFormat(SUPERCATEGORY_TEX_NAMES[c], ypos = 0.83)] if c is not None else None
        except:
            extra_text = [extraTextFormat('other', ypos = 0.83)] if c is not None else None
        x_names = CATEGORY_TEX_NAMES.values()
        x_names.append('total')
        p = Plot(hist_to_plot_pie, list_of_numbers['bkgr'].keys(), name = 'Events_'+str(c), x_name = CATEGORY_TEX_NAMES, y_name = 'Events', extra_text = extra_text)
        p.drawPieChart(output_dir = destination, draw_percent=True, message = args.message)


