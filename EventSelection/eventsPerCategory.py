#! /usr/bin/env python

#
#       Code to calculate signal efficiency
#
# Can be used on RECO level, where you check how many events pass the reco selection
# Is also used to check how many events on a generator level pass certain pt cuts (TODO: not anymore it seems)
#

# TODO: Since high and low mass regions are orthogonal, you could fill both at the same time

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
argParser.add_argument('--makePlots', action='store_true', default=False,  help='make plots')

argParser.add_argument('--noTextFiles',   action='store_true', default=False,  help='make text files containing the number of events per category and sample')
argParser.add_argument('--noBarCharts',   action='store_true', default=False,  help='make bar charts containing the number of events per category and sample')
argParser.add_argument('--noPieCharts',   action='store_true', default=False,  help='make pie charts containing the number of events per category and sample')
argParser.add_argument('--noCutFlow',   action='store_true', default=False,  help='print the cutflow')
argParser.add_argument('--noSearchRegions',   action='store_true', default=False,  help='plot Search Regions')
argParser.add_argument('--oldAnalysisCuts',   action='store_true', default=False,  help='apply the cuts as in AN 2017-014')
argParser.add_argument('--massRegion',   action='store', default=None,  help='apply the cuts of high or low mass regions', choices=['high', 'low'])
argParser.add_argument('--message', type = str, default=None,  help='Add a file with a message in the plotting folder')
args = argParser.parse_args()

#
# Change some settings if this is a test
#
if args.isTest:
    args.isChild = True

    if args.sample is None: args.sample = 'DYJetsToLL-M-50' if not args.signalOnly else 'HNL-tau-m40'
    args.subJob = '0'
    args.year = '2016'

#
# Load in the sample list 
#
from HNL.Samples.sampleManager import SampleManager
skim_str = 'noskim' if args.noskim else 'Reco'
sample_manager = SampleManager(args.year, skim_str, 'fulllist_'+str(args.year))

#
# function to have consistent categories in running and plotting
#
from HNL.EventSelection.eventCategorization import CATEGORIES, SUPER_CATEGORIES
from HNL.EventSelection.eventCategorization import CATEGORY_TEX_NAMES
def listOfCategories():
    return CATEGORIES + ['total']


#
# Extra imports if dividing by search region
#
from HNL.EventSelection.searchRegions import *

search_regions_name = None
if args.massRegion == 'low':
    search_regions_name = 'oldAN_lowMass'
elif args.massRegion == 'high':
    search_regions_name = 'oldAN_highMass'
srm = SearchRegionManager(search_regions_name)

#
#   Code to process events
#
if not args.makePlots:
    #
    # Submit subjobs
    #
    if not args.isChild:
        from HNL.Tools.jobSubmitter import submitJobs
        jobs = []
        for sample_name in sample_manager.sample_names:
            sample = sample_manager.getSample(sample_name)
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
    sample = sample_manager.getSample(args.sample)
    chain = sample.initTree(needhcount = False)

    #
    # Import and create cutter to provide cut flow
    #
    from HNL.EventSelection.cutter import Cutter
    cutter = Cutter(chain = chain)

    if args.isTest:
        event_range = xrange(1000)
    else:
        event_range = sample.getEventRange(args.subJob)    

    chain.HNLmass = sample.getMass()
    chain.year = int(args.year)

    #
    # Get luminosity weight
    #
    from HNL.Weights.lumiweight import LumiWeight
    if args.noskim:
        lw = LumiWeight(sample, sample_manager)
        

    from HNL.EventSelection.eventCategorization import EventCategory
    ec = EventCategory(chain)

    list_of_numbers = {}
    for c in listOfCategories():
        list_of_numbers[c] = {}
        for sr in xrange(1, srm.getNumberOfSearchRegions()+1):
            list_of_numbers[c][sr] = Histogram('_'.join([str(c), str(sr)]), lambda c: 0.5, ('', 'Events'), np.arange(0., 2., 1.))

    subjobAppendix = 'subJob' + args.subJob if args.subJob else ''
    selection_str = 'OldSel' if args.oldAnalysisCuts else 'NewCuts'
    mass_str = 'allMass' if args.massRegion is None else args.massRegion

    if not args.isTest:
        output_name = os.path.join(os.getcwd(), 'data', __file__.split('.')[0], selection_str, mass_str, sample.output)
    else:
        output_name = os.path.join(os.getcwd(), 'data', 'testArea', __file__.split('.')[0], selection_str, mass_str, sample.output)

    if args.isChild:
        output_name += '/tmp_'+sample.output

    output_name += '/'+ sample.name +'_events_' +subjobAppendix+ '.root'

    #
    # Loop over all events
    #
    from HNL.Tools.helpers import progress
    from HNL.EventSelection.eventSelectionTools import select3Leptons, select3GenLeptons, passBaseCutsAN2017014, passBaseCuts, lowMassCuts, highMassCuts, calculateKinematicVariables, containsOSSF
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
            if not cutter.cut(select3Leptons(chain, chain, no_tau=True, light_algo = 'cutbased', cutter=cutter), '3_tight_leptons'):   continue   

        # chain.category will be needed in passBaseCutsAN2017014
        chain.category = ec.returnCategory()

        #Check if baseline selection passed, needs to be done after category assignment due to pt cuts dependency on it
        if not args.oldAnalysisCuts:
            if not passBaseCuts(chain, chain, cutter): continue
        else:   
            if not passBaseCutsAN2017014(chain, chain, cutter): continue

        calculateKinematicVariables(chain, chain)

        if args.massRegion is not None:
            if args.massRegion == 'high' and not highMassCuts(chain, chain, cutter): continue
            if args.massRegion == 'low' and not lowMassCuts(chain, chain, cutter): continue       

        chain.search_region = srm.getSearchRegion(chain)


        list_of_numbers['total'][chain.search_region].fill(chain, chain.weight)
        list_of_numbers[ec.returnCategory()][chain.search_region].fill(chain, chain.weight)

    for i, c_h in enumerate(list_of_numbers.keys()):
        for j, sr_h in enumerate(list_of_numbers[c_h].values()):
            if i == 0 and j == 0:
                sr_h.write(output_name)
            else:
                sr_h.write(output_name, append=True)

    cutter.saveCutFlow(output_name)

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
    if not args.isTest:
        in_files = glob.glob(os.path.expandvars('$CMSSW_BASE/src/HNL/EventSelection/data/eventsPerCategory/'+selection_str+'/'+mass_str+'/*')) 
    else:
        in_files = glob.glob(os.path.expandvars('$CMSSW_BASE/src/HNL/EventSelection/data/testArea/eventsPerCategory/'+selection_str+'/'+mass_str+'/*')) 
    for f in in_files:
        if '.txt' in f: continue
        merge(f)

    def mergeSearchRegions(regions_to_merge, values, errors, out_name):
        if not regions_to_merge: 
            raise RuntimeError('Illegal input for mergeSearchRegions in call with output name "'+out_name+'"')
        out_val, out_err = (values[regions_to_merge[0]], errors[regions_to_merge[0]])
        if len(regions_to_merge) > 1:
            for reg in regions_to_merge[1:]:
                out_val += values[reg]
                out_err = np.sqrt(out_err ** 2 + errors[reg] ** 2)
        return out_val, out_err
        # if not regions_to_merge: 
        #     raise RuntimeError('Illegal input for mergeSearchRegions in call with output name "'+out_name+'"')
        # out_hist = hist_collection[regions_to_merge[0]].clone(out_name)
        # if len(regions_to_merge) > 1:
        #     for reg in regions_to_merge[1:]:
        #         out_hist.add(hist_collection[reg])
        # return out_hist


    #
    # Gather all the files
    #
    list_of_values = {'signal' : {}, 'bkgr' : {}}
    list_of_errors = {'signal' : {}, 'bkgr' : {}}
    accepted_categories = [i for i in CATEGORIES]
    x_names = [CATEGORY_TEX_NAMES[i] for i in accepted_categories]
    processed_outputs = set()
    for sample_name in sample_manager.sample_names:
        sample = sample_manager.getSample(sample_name)
        if sample.output in processed_outputs: continue
        processed_outputs.add(sample.output)
        if not args.isTest: 
            path_name = os.path.expandvars('$CMSSW_BASE/src/HNL/EventSelection/data/eventsPerCategory/'+selection_str+'/'+mass_str+'/'+sample.output+'/events.root')
        else:
            path_name = os.path.expandvars('$CMSSW_BASE/src/HNL/EventSelection/data/testArea/eventsPerCategory/'+selection_str+'/'+mass_str+'/'+sample.output+'/events.root')
        is_signal = 'signal' if 'HNL' in sample.output else 'bkgr'
        if args.signalOnly and is_signal == 'bkgr': continue
        if args.backgroundOnly and is_signal == 'signal': continue
        if 'HNL' in sample.name and not 'HNL-'+args.coupling in sample.name: continue
        if args.masses is not None and is_signal=='signal' and not any([str(m) == sample.output.rsplit('-m')[-1] for m in args.masses]): continue
        list_of_values[is_signal][sample.output] = {}
        list_of_errors[is_signal][sample.output] = {}
        for c in listOfCategories():
            if c not in accepted_categories: continue
            list_of_values[is_signal][sample.output][c] = {}
            list_of_errors[is_signal][sample.output][c] = {}
            for sr in xrange(1, srm.getNumberOfSearchRegions()+1):
                #list_of_values[is_signal][sample.output][c][sr]= Histogram(getObjFromFile(path_name, '_'.join([str(c), str(sr)])+'/'+'_'.join([str(c), str(sr)])))
                tmp_hist = getObjFromFile(path_name, '_'.join([str(c), str(sr)])+'/'+'_'.join([str(c), str(sr)]))
                list_of_values[is_signal][sample.output][c][sr]= tmp_hist.GetBinContent(1)
                list_of_errors[is_signal][sample.output][c][sr]= tmp_hist.GetBinError(1)
            
            #
            # Add some grouped search regions for easier access
            #
            for group_name in srm.getListOfSearchRegionGroups():
                list_of_values[is_signal][sample.output][c][group_name], list_of_errors[is_signal][sample.output][c][group_name] = mergeSearchRegions(srm.getGroupValues(group_name), list_of_values[is_signal][sample.output][c], list_of_errors[is_signal][sample.output][c], str(c)+'_'+str(group_name))
            list_of_values[is_signal][sample.output][c]['total'], list_of_errors[is_signal][sample.output][c]['total'] = mergeSearchRegions(range(1, srm.getNumberOfSearchRegions()+1), list_of_values[is_signal][sample.output][c], list_of_errors[is_signal][sample.output][c], str(c)+'_'+str('total'))

    search_region_names = range(1, srm.getNumberOfSearchRegions()+1) + srm.getListOfSearchRegionGroups() + ['total']

    from HNL.Tools.helpers import makePathTimeStamped
    from HNL.Plotting.plottingTools import extraTextFormat

    destination = makePathTimeStamped(os.path.expandvars('$CMSSW_BASE/src/HNL/EventSelection/data/Results/eventsPerCategory/'+selection_str+'/'+mass_str))



    #
    # Make text files if requested
    #
    if not args.noTextFiles:
        from HNL.Tools.helpers import getObjFromFile, rootFileContent, makeDirIfNeeded
        from ROOT import TFile

        for sr in search_region_names:
            makeDirIfNeeded(destination+'/Tables/table_'+str(sr)+'.txt')
            out_file = open(destination+'/Tables/table_'+str(sr)+'.txt', 'w')
            out_file.write('\t \t tte \t ttm \t tee \t tem \t tmm \t lll \t total \n')

            out_file_tex = open(destination+'/Tables/table_'+str(sr)+'_tex.txt', 'w')
            out_file_tex.write('\\begin{table}[] \n')
            out_file_tex.write("\\begin{tabular}{|l|l|l|l|l|l|l|l|} \n")
            out_file_tex.write("\hline \n")
            out_file_tex.write('& \\tau\\tau e & \\tau \\tau \\mu & \\tau e e & \\tau e \\mu & \\tau\\mu\\mu & lll & total \n')
            out_file_tex.write("\hline \n")

            for sample_name in sorted(list_of_values['signal'].keys(), key=lambda n : int(n.split('-m')[-1])):
                out_file.write(sample_name+'\t')
                out_file_tex.write(sample_name+' & ')

                for c in sorted(list_of_values['signal'][sample_name].keys()):
                    out_file.write('%4.3f' % list_of_values['signal'][sample_name][c][sr]+'\t')
                    out_file_tex.write('%4.3f' % list_of_values['signal'][sample_name][c][sr])
                    # out_file.write('%4.3f' % list_of_values['signal'][sample_name][c][sr].getHist().GetSumOfWeights()+'\t')
                    # out_file_tex.write('%4.3f' % list_of_values['signal'][sample_name][c][sr].getHist().GetSumOfWeights())
                    if not 'total' in str(c):
                        out_file_tex.write(' & ')

                out_file.write('\n')
                out_file_tex.write('\\\\ \hline \n')

            out_file.write('-------------------------------------------------------------------- \n')
            out_file_tex.write('\\\\ \hline \n')

            for sample_name in list_of_values['bkgr'].keys():
                out_file.write(sample_name+'\t')
                out_file_tex.write(sample_name+' & ')

                for c in sorted(list_of_values['bkgr'][sample_name].keys()):
                    out_file.write('%4.1f' % list_of_values['bkgr'][sample_name][c][sr]+'\t')
                    out_file_tex.write('%4.1f' % list_of_values['bkgr'][sample_name][c][sr])
                    if not 'total' in str(c):
                        out_file_tex.write(' & ')

                out_file.write('\n')
                out_file_tex.write('\\\\ \hline \n')


            out_file.close()

            out_file_tex.write('\end{tabular} \n')
            out_file_tex.write('\end{table} \n')
            out_file_tex.close()

    #
    # For bar and pie charts, no split in search regions is considered for now
    #
    if not args.noBarCharts:

        for supercat in SUPER_CATEGORIES.keys():
            #
            # Bkgr
            #
            hist_to_plot = {}
            for sample_name in list_of_values['bkgr'].keys():
                # hist_to_plot[sample_name] = ROOT.TH1D(sample_name, sample_name, len(list_of_values['bkgr'][sample_name]), 0, len(list_of_values['bkgr'][sample_name]))
                hist_to_plot[sample_name] = ROOT.TH1D(sample_name+supercat, sample_name+supercat, len(SUPER_CATEGORIES[supercat]), 0, len(SUPER_CATEGORIES[supercat]))
                for i, c in enumerate(SUPER_CATEGORIES[supercat]):
                    # hist_to_plot[sample_name].SetBinContent(i+1, list_of_values['bkgr'][sample_name][c]['total'].getHist().GetSumOfWeights()) 
                    hist_to_plot[sample_name].SetBinContent(i+1, list_of_values['bkgr'][sample_name][c]['total']) 
                    hist_to_plot[sample_name].SetBinError(i+1, list_of_errors['bkgr'][sample_name][c]['total']) 
            x_names = [CATEGORY_TEX_NAMES[n] for n in SUPER_CATEGORIES[supercat]]
            p = Plot(hist_to_plot.values(), hist_to_plot.keys(), name = 'Events-bar-bkgr-'+supercat, x_name = x_names, y_name = 'Events', y_log='SingleTau' in supercat)
            p.drawBarChart(output_dir = destination+'/BarCharts', message = args.message)
            
            #
            # Signal
            #   
            hist_to_plot = []
            hist_names = []
            for sn, sample_name in enumerate(sorted(list_of_values['signal'].keys(), key=lambda k: int(k.split('-m')[-1]))):
                # hist_to_plot.append(ROOT.TH1D(sample_name, sample_name, len(list_of_values['signal'][sample_name]), 0, len(list_of_values['signal'][sample_name])))
                hist_to_plot.append(ROOT.TH1D(sample_name, sample_name, len(SUPER_CATEGORIES[supercat]), 0, len(SUPER_CATEGORIES[supercat])))
                hist_names.append(sample_name)
                for i, c in enumerate(SUPER_CATEGORIES[supercat]):
                    # hist_to_plot[sn].SetBinContent(i+1, list_of_values['signal'][sample_name][c]['total'].getHist().GetSumOfWeights()) 
                    hist_to_plot[sn].SetBinContent(i+1, list_of_values['signal'][sample_name][c]['total']) 
                    hist_to_plot[sn].SetBinError(i+1, list_of_errors['signal'][sample_name][c]['total']) 
            x_names = [CATEGORY_TEX_NAMES[n] for n in SUPER_CATEGORIES[supercat]]
            p = Plot(hist_to_plot, hist_names, name = 'Events-bar-signal-'+supercat+'-'+args.coupling, x_name = x_names, y_name = 'Events', y_log=True)
            p.drawBarChart(output_dir = destination+'/BarCharts', parallel_bins=True, message = args.message)
    
    if not args.noPieCharts:
        example_sample = list_of_values['bkgr'].keys()[0]
        for i, c in enumerate(sorted(list_of_values['bkgr'][example_sample].keys())):
            hist_to_plot_pie = ROOT.TH1D(str(c)+'_pie', str(c), len(list_of_values['bkgr']), 0, len(list_of_values['bkgr']))
            for j, s in enumerate(list_of_values['bkgr'].keys()):
                # hist_to_plot_pie.SetBinContent(j+1, list_of_values['bkgr'][s][c]['total'].getHist().GetSumOfWeights())
                hist_to_plot_pie.SetBinContent(j+1, list_of_values['bkgr'][s][c]['total'])
                hist_to_plot_pie.SetBinError(j+1, list_of_errors['bkgr'][s][c]['total'])

            try:
                extra_text = [extraTextFormat(SUPERCATEGORY_TEX_NAMES[c], ypos = 0.83)] if c is not None else None
            except:
                extra_text = [extraTextFormat('other', ypos = 0.83)] if c is not None else None
            x_names = CATEGORY_TEX_NAMES.values()
            x_names.append('total')
            p = Plot(hist_to_plot_pie, list_of_values['bkgr'].keys(), name = 'Events_'+str(c), x_name = CATEGORY_TEX_NAMES, y_name = 'Events', extra_text = extra_text)
            p.drawPieChart(output_dir = destination+'/PieCharts', draw_percent=True, message = args.message)

    if not args.noCutFlow:
        import glob
        all_files = glob.glob(os.path.expandvars('$CMSSW_BASE/src/HNL/EventSelection/data/eventsPerCategory/'+selection_str+'/'+mass_str+'/HNL-'+args.coupling+'*/events.root'))

        all_files = sorted(all_files, key = lambda k : int(k.split('/')[-2].split('.')[0].split('-m')[-1]))
        all_names = [k.split('/')[-1].split('.')[0] for k in all_files]

        from HNL.EventSelection.cutter import plotCutFlow
        out_name = os.path.expandvars('$CMSSW_BASE/src/HNL/EventSelection/data/Results/eventsPerCategory/'+selection_str+'/'+mass_str) +'/CutFlow/Output'
        plotCutFlow(all_files, out_name, all_names, ignore_weights=True)

    #
    # Produce search region plots
    #
    if not args.noSearchRegions:
        from HNL.EventSelection.searchRegions import plotLowMassRegions, plotHighMassRegions
        from HNL.EventSelection.eventCategorization import CATEGORY_NAMES, ANALYSIS_CATEGORIES

        #First we need to make histograms that have different search region on x-axis
        list_of_sr_hist = {}

        for c in accepted_categories:
            list_of_sr_hist[c] = {'signal':{}, 'bkgr':{}}
            #
            # Bkgr
            #
            for i_name, sample_name in enumerate(list_of_values['bkgr'].keys()):
                list_of_sr_hist[c]['bkgr'][sample_name] = ROOT.TH1D('_'.join([sample_name, str(c)]), '_'.join([sample_name, str(c)]), srm.getNumberOfSearchRegions(), 0.5, srm.getNumberOfSearchRegions()+0.5)
                for sr in xrange(1, srm.getNumberOfSearchRegions()+1):
                    list_of_sr_hist[c]['bkgr'][sample_name].SetBinContent(sr, list_of_values['bkgr'][sample_name][c][sr])
                    list_of_sr_hist[c]['bkgr'][sample_name].SetBinError(sr, list_of_errors['bkgr'][sample_name][c][sr]) 

            #
            # Signal
            #   
            for i_name, sample_name in enumerate(list_of_values['signal'].keys()):
                list_of_sr_hist[c]['signal'][sample_name] = ROOT.TH1D('_'.join([sample_name, str(c)]), '_'.join([sample_name, str(c)]), srm.getNumberOfSearchRegions(), 0.5, srm.getNumberOfSearchRegions()+0.5)
                for sr in xrange(1, srm.getNumberOfSearchRegions()+1):
                    list_of_sr_hist[c]['signal'][sample_name].SetBinContent(sr, list_of_values['signal'][sample_name][c][sr]) 
                    list_of_sr_hist[c]['signal'][sample_name].SetBinError(sr, list_of_errors['signal'][sample_name][c][sr])
                if args.coupling == 'tau' and args.massRegion == 'high': list_of_sr_hist[c]['signal'][sample_name].Scale(1000)

        def mergeCategories(ac, list_of_hist, signalOrBkgr, sample_name):
            filtered_hist = [list_of_sr_hist[c][signalOrBkgr][sample_name] for c in ac]
            if len(filtered_hist) == 0:
                raise RuntimeError("Tried to merge nonexisting categories")
            elif len(filtered_hist) == 1:
                return filtered_hist[0]
            else:
                new_hist = filtered_hist[0]
                for h in filtered_hist[1:]:
                    new_hist.Add(h)
                return new_hist

        #Now add histograms together that belong to same analysis super category
        list_of_ac_hist = {}
        for ac in ANALYSIS_CATEGORIES.keys():
            list_of_ac_hist[ac] = {'signal':[], 'bkgr':[]}

            signal_names = []
            for i_name, sample_name in enumerate(list_of_values['signal'].keys()):
                signal_names.append(sample_name)
                list_of_ac_hist[ac]['signal'].append(mergeCategories(ANALYSIS_CATEGORIES[ac], list_of_sr_hist, 'signal', sample_name))
            
            bkgr_names = []
            for i_name, sample_name in enumerate(list_of_values['bkgr'].keys()):
                bkgr_names.append(sample_name)
                list_of_ac_hist[ac]['bkgr'].append(mergeCategories(ANALYSIS_CATEGORIES[ac], list_of_sr_hist, 'bkgr', sample_name))

            extra_text = [extraTextFormat(ac, ypos = 0.82)]
            if args.coupling: extra_text.append(extraTextFormat('V_{'+args.coupling+'N} = 0.01'))
            if args.coupling == 'tau' and args.massRegion == 'high': extra_text.append(extraTextFormat('signal scaled up by factor 1000.', textsize=0.6))
            if args.massRegion == 'low':
                plotLowMassRegions(list_of_ac_hist[ac]['signal'], list_of_ac_hist[ac]['bkgr'], signal_names+bkgr_names, out_path = destination+'/SearchRegions/'+ac, extra_text = extra_text)
            if args.massRegion == 'high':
                plotHighMassRegions(list_of_ac_hist[ac]['signal'], list_of_ac_hist[ac]['bkgr'], signal_names+bkgr_names, out_path = destination+'/SearchRegions/'+ac, extra_text = extra_text)