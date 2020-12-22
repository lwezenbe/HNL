#! /usr/bin/env python

#
#       Code to calculate signal and background yields
#

import numpy as np
from HNL.Tools.histogram import Histogram
from HNL.EventSelection.eventSelector import EventSelector
from HNL.Tools.helpers import makeDirIfNeeded
import ROOT

#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018'])
submission_parser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
submission_parser.add_argument('--runInTerminal', action='store_true', default=False,  help='Quickly run in the terminal')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--coupling', type = float, action='store', default=0.01,  help='Coupling of the sample')
submission_parser.add_argument('--noskim', action='store_true', default=False,  help='Use no skim sample list')
submission_parser.add_argument('--selection',   action='store', default='cutbased',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'AN2017014', 'MVA'])
submission_parser.add_argument('--region',   action='store', default='baseline',  help='apply the cuts of high or low mass regions, use "all" to run both simultaniously', 
    choices=['baseline', 'highMassSR', 'lowMassSR', 'ZZ', 'WZ', 'ConversionCR'])
submission_parser.add_argument('--includeData',   action='store_true', default=False,  help='Also run over data samples')
submission_parser.add_argument('--logLevel',  action='store',      default='INFO',               help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])

argParser.add_argument('--makePlots', action='store_true', default=False,  help='make plots')
argParser.add_argument('--noTextFiles',   action='store_true', default=False,  help='make text files containing the number of events per category and sample')
argParser.add_argument('--noBarCharts',   action='store_true', default=False,  help='make bar charts containing the number of events per category and sample')
argParser.add_argument('--noPieCharts',   action='store_true', default=False,  help='make pie charts containing the number of events per category and sample')
argParser.add_argument('--noCutFlow',   action='store_true', default=False,  help='print the cutflow')
argParser.add_argument('--noSearchRegions',   action='store_true', default=False,  help='plot Search Regions')
argParser.add_argument('--groupSamples',   action='store_true', default=False,  help='plot Search Regions')
argParser.add_argument('--signalOnly', action='store_true', default=False,  help='Only launch jobs with signal samples')
argParser.add_argument('--backgroundOnly', action='store_true', default=False,  help='Only launch jobs with signal samples')
argParser.add_argument('--flavor', action='store', default='',  help='Which coupling should be active?' , choices=['tau', 'e', 'mu', '2l', ''])
argParser.add_argument('--masses', type=int, nargs='*',  help='Only run or plot signal samples with mass given in this list')


argParser.add_argument('--message', type = str, default=None,  help='Add a file with a message in the plotting folder')
argParser.add_argument('--makeDataCards', type = str, default=None,  help='Make data cards of the data you have', choices=['shapes', 'cutAndCount'])
argParser.add_argument('--rescaleSignal', type = float,  action='store', default=None,  help='Enter desired signal coupling squared')



args = argParser.parse_args()


from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)

if args.includeData and args.region in ['baseline', 'highMassSR', 'lowMassSR']:
    raise RuntimeError('These options combined would mean unblinding. This is not allowed.')

l1 = 0
l2 = 1
l3 = 2
l4 = 3
nl = 3 if args.region != 'ZZCR' else 4


#
# Change some settings if this is a test
#
if args.isTest:
    args.isChild = True

    if args.sample is None: args.sample = 'DYJetsToLL-M-50'
    args.subJob = '0'
    if args.year is None: args.year = '2016'

#
# Load in the sample list 
#
from HNL.Samples.sampleManager import SampleManager
if args.noskim:
    skim_str = 'noskim'
else:
    skim_str = 'Old' if args.selection == 'AN2017014' else 'Reco'

sample_manager = SampleManager(args.year, skim_str, 'yields_'+str(args.year))

#
# function to have consistent categories in running and plotting
#
from HNL.EventSelection.eventCategorization import CATEGORIES, SUPER_CATEGORIES
from HNL.EventSelection.eventCategorization import CATEGORY_TEX_NAMES
def listOfCategories(region):
    # if region in ['baseline', 'highMassSR', 'lowMassSR']:
    return CATEGORIES
    # else:
    #     return [max(CATEGORIES)]

#
# Extra imports for dividing by region
#
from HNL.EventSelection.searchRegions import SearchRegionManager
regions = []
srm = {}
if args.region == 'lowMassSR':
    regions.append('lowMassSR')
    srm['lowMassSR'] = SearchRegionManager('oldAN_lowMass')
elif args.region == 'highMassSR':
    regions.append('highMassSR')
    srm['highMassSR'] = SearchRegionManager('oldAN_highMass')
else:
    regions.append(args.region)
    srm[args.region] = SearchRegionManager(args.region)

#
# Prepare jobs
#
jobs = []
for sample_name in sample_manager.sample_names:
    if args.sample and args.sample not in sample_name: continue 
    if not args.includeData and sample_name == 'Data': continue
    sample = sample_manager.getSample(sample_name)
    for njob in xrange(sample.split_jobs):
        jobs += [(sample.name, str(njob))]

#
#   Code to process events
#
if not args.makePlots and args.makeDataCards is None:
    #
    # Submit subjobs
    #
    if not args.isChild and not args.runInTerminal:
        from HNL.Tools.jobSubmitter import submitJobs
        print 'submitting'
        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'calcYields')
        exit(0)

    #
    # Load in sample and chain
    #
    for sample in sample_manager.sample_list:
        if sample.name not in sample_manager.sample_names: continue
        if args.sample and sample.name != args.sample: continue

        if not args.includeData and sample.name == 'Data': 
            raise RuntimeError('Trying to run data while it is not allowed. Stopping the program')
        chain = sample.initTree(needhcount = False)

        print 'Processing', sample.name

        #
        # Import and create cutter to provide cut flow
        #
        from HNL.EventSelection.cutter import Cutter
        cutter = Cutter(chain = chain)

        if args.isTest:
            max_events = 20000
            if len(sample.getEventRange(0)) < max_events:
                event_range = sample.getEventRange(0)
            else:
                event_range = xrange(max_events)
        elif not args.runInTerminal:
            event_range = sample.getEventRange(args.subJob)
        else:
            event_range = xrange(chain.GetEntries())   

        chain.HNLmass = sample.getMass()
        chain.year = int(args.year)

        #
        # Get luminosity weight
        #
        from HNL.Weights.lumiweight import LumiWeight
        lw = LumiWeight(sample, sample_manager)

        from HNL.EventSelection.eventCategorization import EventCategory
        ec = EventCategory(chain)

        #
        # Object ID param
        #
        from HNL.ObjectSelection.objectSelection import getObjectSelection
        chain.obj_sel = getObjectSelection(args.selection)

        es = EventSelector(args.region, chain, chain, args.selection, True, ec)

        list_of_numbers = {}
        for c in listOfCategories(args.region):
            list_of_numbers[c] = {}
            for prompt_str in ['prompt', 'nonprompt', 'total']:
                list_of_numbers[c][prompt_str] = Histogram('_'.join([str(c), prompt_str]), lambda c: c.search_region-0.5, ('', 'Events'), 
                    np.arange(0., srm[args.region].getNumberOfSearchRegions()+1., 1.))                

        subjobAppendix = 'subJob' + args.subJob if args.subJob else ''

        def getOutputName(prompt_string):
            if not args.isTest:
                output_string = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 'data', __file__.split('.')[0].rsplit('/')[-1], args.year, args.selection, args.region, sample.output, prompt_string)
            else:
                output_string = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 'data', 'testArea', __file__.split('.')[0].rsplit('/')[-1], args.year, args.selection, args.region, sample.output, prompt_string)

            if args.isChild:
                output_string += '/tmp_'+sample.output

            output_string += '/'+ sample.name +'_events_' +subjobAppendix+ '.root'
            makeDirIfNeeded(output_string)
            return output_string

        #
        # Loop over all events
        #
        from HNL.Tools.helpers import progress
        from HNL.Triggers.triggerSelection import applyCustomTriggers, listOfTriggersAN2017014

        print 'tot_range', len(event_range)
        for entry in event_range:
            
            chain.GetEntry(entry)
            progress(entry - event_range[0], len(event_range))

            cutter.cut(True, 'total')
            
            #
            #Triggers
            #
            if args.selection == 'AN2017014':
                if not cutter.cut(applyCustomTriggers(listOfTriggersAN2017014(chain)), 'pass_triggers'): continue

            #Event selection            
            if not es.passedFilter(cutter): continue
            nprompt = 0
            for index in chain.l_indices:
                if chain._lIsPrompt[index]: nprompt += 1
            
            prompt_str = 'prompt' if nprompt == nl else 'nonprompt'

            # print nprompt, prompt_str, chain.M3l, chain.minMossf

            chain.search_region = srm[args.region].getSearchRegion(chain)
            list_of_numbers[ec.returnCategory()][prompt_str].fill(chain, lw.getLumiWeight())
            list_of_numbers[ec.returnCategory()]['total'].fill(chain, lw.getLumiWeight())


        for prompt_str in ['prompt', 'nonprompt', 'total']:
            for i, c_h in enumerate(list_of_numbers.keys()):
                output_name = getOutputName(prompt_str)
                if i == 0:
                    list_of_numbers[c_h][prompt_str].write(output_name, is_test=args.isTest)
                else:
                    list_of_numbers[c_h][prompt_str].write(output_name, append=True, is_test=args.isTest)

            cutter.saveCutFlow(getOutputName('total'))
    
    closeLogger(log)

#
# Merge if needed
#
else:
    from HNL.Tools.mergeFiles import merge
    import glob
    from HNL.Plotting.plot import Plot
    from HNL.EventSelection.eventCategorization import CATEGORY_NAMES, ANALYSIS_CATEGORIES

    from HNL.Tools.helpers import makePathTimeStamped
    from HNL.Plotting.plottingTools import extraTextFormat
    from HNL.Tools.helpers import getObjFromFile, tab, isValidRootFile
    from HNL.Analysis.analysisTypes import signal_couplingsquared

    #
    # Check status of the jobs and merge
    #
    if not args.isTest:
        base_path = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 'data', __file__.split('.')[0].rsplit('/')[-1], args.year, args.selection, args.region)
    else:
        base_path = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 'data', 'testArea', __file__.split('.')[0].rsplit('/')[-1], args.year, args.selection, args.region)

    in_files = glob.glob(os.path.join(base_path, '*', '*'))
    merge(in_files, __file__, jobs, ('sample', 'subJob'), argParser, istest=args.isTest)

    def mergeValues(val_to_merge, err_to_merge):
        if len(val_to_merge) != len(err_to_merge):
            raise RuntimeError('length of both input arrays should be the same. Now they are: len(values) = '+str(len(val_to_merge)) + ' and len(errors) = '+str(len(err_to_merge)))
        out_val, out_err = (val_to_merge[0], err_to_merge[0])
        if len(val_to_merge) > 1:
            for val, err in zip(val_to_merge[1:], err_to_merge[1:]):
                out_val += val
                out_err = np.sqrt(out_err ** 2 + err ** 2)
        return out_val, out_err

    #
    # Gather all the files
    #
    list_of_values = {'signal' : {}, 'bkgr' : {}}
    list_of_errors = {'signal' : {}, 'bkgr' : {}}
    x_names = [CATEGORY_TEX_NAMES[i] for i in CATEGORIES]


    #Gather sample names
    processed_outputs = set()
    signal_names = []
    bkgr_names = []
    for sample_name in sample_manager.sample_names:
        sample = sample_manager.getSample(sample_name)
        if sample.output in processed_outputs: continue     #Current implementation of sample lists would cause double counting otherwise 
        processed_outputs.add(sample.output)
        is_signal = True if 'HNL' in sample.output else False
        if args.signalOnly and not is_signal: continue
        if args.backgroundOnly and is_signal: continue
        if 'HNL' in sample.name and not 'HNL-'+args.flavor in sample.name: continue
        if not args.includeData and sample.name == 'Data': continue
        if args.masses is not None and is_signal and not any([str(m) == sample.output.rsplit('-m')[-1] for m in args.masses]): continue

        if not isValidRootFile(os.path.join(base_path, sample.output, 'total/events.root')): continue
        if is_signal: 
            signal_names.append(sample.output)
        else:
            bkgr_names.append(sample.output)
    
    #Loading in signal

    for signal in signal_names:
        print 'Loading', signal
        signal_mass = int(signal.split('-m')[-1])
        path_name = os.path.join(base_path, signal, 'total/events.root')

        list_of_values['signal'][signal] = {}
        list_of_errors['signal'][signal] = {}
        for c in listOfCategories(args.region):
            list_of_values['signal'][signal][c] = {}
            list_of_errors['signal'][signal][c] = {}
            tmp_hist = getObjFromFile(path_name, '_'.join([str(c), 'total'])+'/'+'_'.join([str(c), 'total']))
            
            #Rescale if requested
            new_coupling_squared = args.rescaleSignal if args.rescaleSignal is not None else signal_couplingsquared[args.flavor][signal_mass]
            tmp_hist.Scale(new_coupling_squared/(args.coupling**2))

            for sr in xrange(1, srm[args.region].getNumberOfSearchRegions()+1):
                list_of_values['signal'][signal][c][sr] = tmp_hist.GetBinContent(sr)
                list_of_errors['signal'][signal][c][sr] = tmp_hist.GetBinError(sr)

    #Loading in background

    if args.groupSamples:
        background_collection = sample_manager.sample_groups.keys()
    else:
        background_collection = [b for b in bkgr_names]

    for b in background_collection:
        list_of_values['bkgr'][b] = {}
        list_of_errors['bkgr'][b] = {}
        for c in listOfCategories(args.region):
            list_of_values['bkgr'][b][c] = {}
            list_of_errors['bkgr'][b][c] = {}
            for sr in xrange(1, srm[args.region].getNumberOfSearchRegions()+1):
                list_of_values['bkgr'][b][c][sr] = 0.
                list_of_errors['bkgr'][b][c][sr] = 0.

    for bkgr in bkgr_names:
        if 'QCD' in bkgr: continue
        print 'Loading', bkgr

        path_name_total = os.path.join(base_path, bkgr, 'total/events.root')
        path_name_prompt = os.path.join(base_path, bkgr, 'prompt/events.root')
        path_name_nonprompt = os.path.join(base_path, bkgr, 'nonprompt/events.root')

        for c in listOfCategories(args.region):
            tmp_hist_prompt = getObjFromFile(path_name_prompt, '_'.join([str(c), 'prompt'])+'/'+'_'.join([str(c), 'prompt']))
            tmp_hist_nonprompt = getObjFromFile(path_name_nonprompt, '_'.join([str(c), 'nonprompt'])+'/'+'_'.join([str(c), 'nonprompt']))
            tmp_hist_total = getObjFromFile(path_name_total, '_'.join([str(c), 'total'])+'/'+'_'.join([str(c), 'total']))
            for sr in xrange(1, srm[args.region].getNumberOfSearchRegions()+1):
                if args.groupSamples:
                    sg = [sk for sk in sample_manager.sample_groups.keys() if bkgr in sample_manager.sample_groups[sk]][0]
                    if bkgr == 'DY':
                        list_of_values['bkgr']['XG'][c][sr] += tmp_hist_prompt.GetBinContent(sr) 
                        list_of_errors['bkgr']['XG'][c][sr] = np.sqrt(list_of_errors['bkgr'][sg][c][sr] ** 2 + tmp_hist_prompt.GetBinError(sr) ** 2)
                        list_of_values['bkgr']['non-prompt'][c][sr] += tmp_hist_nonprompt.GetBinContent(sr) 
                        list_of_errors['bkgr']['non-prompt'][c][sr] = np.sqrt(list_of_errors['bkgr']['non-prompt'][c][sr] ** 2 + tmp_hist_nonprompt.GetBinError(sr) ** 2)   
                    elif sg == 'non-prompt':
                        list_of_values['bkgr'][sg][c][sr] += tmp_hist_nonprompt.GetBinContent(sr) 
                        list_of_errors['bkgr'][sg][c][sr] = np.sqrt(list_of_errors['bkgr'][sg][c][sr] ** 2 + tmp_hist_nonprompt.GetBinError(sr) ** 2)
                    else:
                        list_of_values['bkgr'][sg][c][sr] += tmp_hist_prompt.GetBinContent(sr) 
                        list_of_errors['bkgr'][sg][c][sr] = np.sqrt(list_of_errors['bkgr'][sg][c][sr] ** 2 + tmp_hist_prompt.GetBinError(sr) ** 2)
                        list_of_values['bkgr']['non-prompt'][c][sr] += tmp_hist_nonprompt.GetBinContent(sr) 
                        list_of_errors['bkgr']['non-prompt'][c][sr] = np.sqrt(list_of_errors['bkgr']['non-prompt'][c][sr] ** 2 + tmp_hist_nonprompt.GetBinError(sr) ** 2)
                else:
                    list_of_values['bkgr'][bkgr][c][sr] = tmp_hist_total.GetBinContent(sr)
                    list_of_errors['bkgr'][bkgr][c][sr] = tmp_hist_total.GetBinError(sr)

    #
    # Add some grouped search regions for easier access
    #
    for sn in signal_names + background_collection:
        is_signal_str = 'signal' if sn in signal_names else 'bkgr'
        for c in listOfCategories(args.region):
            for group_name in srm[args.region].getListOfSearchRegionGroups():
                values_to_merge = [list_of_values[is_signal_str][sn][c][v] for v in srm[args.region].getGroupValues(group_name)]
                errors_to_merge = [list_of_errors[is_signal_str][sn][c][v] for v in srm[args.region].getGroupValues(group_name)]
                list_of_values[is_signal_str][sn][c][group_name], list_of_errors[is_signal_str][sn][c][group_name] = mergeValues(values_to_merge, errors_to_merge)
            values_to_merge = [list_of_values[is_signal_str][sn][c][v] for v in range(1, srm[args.region].getNumberOfSearchRegions()+1)]
            errors_to_merge = [list_of_errors[is_signal_str][sn][c][v] for v in range(1, srm[args.region].getNumberOfSearchRegions()+1)]
            list_of_values[is_signal_str][sn][c]['total'], list_of_errors[is_signal_str][sn][c]['total'] = mergeValues(values_to_merge, errors_to_merge)

    #
    # Add some grouped categories for easier access
    #
    for sn in signal_names + background_collection:
        is_signal_str = 'signal' if sn in signal_names else 'bkgr'
        category_keys = [c for c in CATEGORIES]
        for ac in SUPER_CATEGORIES.keys():
            category_keys.append(ac)
            list_of_values[is_signal_str][sn][ac] = {}
            list_of_errors[is_signal_str][sn][ac] = {}
            for sr in list_of_values[is_signal_str][sn][1].keys():
                values_to_merge = [list_of_values[is_signal_str][sn][v][sr] for v in SUPER_CATEGORIES[ac]]
                errors_to_merge = [list_of_errors[is_signal_str][sn][v][sr] for v in SUPER_CATEGORIES[ac]]
                list_of_values[is_signal_str][sn][ac][sr], list_of_errors[is_signal_str][sn][ac][sr] = mergeValues(values_to_merge, errors_to_merge)
        


        
        #Combine all categories into 1 giant bin
        category_keys.append('total')
        list_of_values[is_signal_str][sn]['total'] = {}
        list_of_errors[is_signal_str][sn]['total'] = {}
        for sr in list_of_values[is_signal_str][sn][1].keys():
            values_to_merge = [list_of_values[is_signal_str][sn][v][sr] for v in CATEGORIES]
            errors_to_merge = [list_of_errors[is_signal_str][sn][v][sr] for v in CATEGORIES]
            list_of_values[is_signal_str][sn]['total'][sr], list_of_errors[is_signal_str][sn]['total'][sr] = mergeValues(values_to_merge, errors_to_merge)

    search_region_keys = range(1, srm[args.region].getNumberOfSearchRegions()+1) + srm[args.region].getListOfSearchRegionGroups() + ['total']

    destination = makePathTimeStamped(os.path.expandvars('$CMSSW_BASE/src/HNL/Analysis/data/Results/calcYields/'+args.selection+'/'+args.region+'/'+args.flavor))

    def protectHist(hist):    
        if hist.Integral() < 0.00001:
            for i in range(1, hist.GetNbinsX()+1):
                if hist.GetBinContent(i) <= 0.00001: hist.SetBinContent(i, 0.00001)
        return hist

    if args.makeDataCards is not None:
        from HNL.Stat.combineTools import makeDataCard

        #
        # If we just want cut and count without shapes, simply write datacards for everything you have
        #
        if args.makeDataCards == 'cutAndCount':
            for ac in ['total']+SUPER_CATEGORIES.keys():
                for sr in search_region_keys:
                    for s in list_of_values['signal'].keys():
                        sig_yield = list_of_values['signal'][s][ac][sr]
                        bkgr_yields = [list_of_values['bkgr'][b][ac][sr] for b in sorted(list_of_values['bkgr'].keys())]
                        bkgr_names = [b for b in sorted(list_of_values['bkgr'].keys())]
                        makeDataCard(str(ac)+'-'+str(sr), args.flavor, args.year, 0, s, bkgr_names, args.selection, sig_yield, bkgr_yields, coupling_sq = coupling_squared)
        #
        # If we want to use shapes, first make shape histograms, then make datacards
        #
        elif args.makeDataCards == 'shapes':
            for ac in ['total']+SUPER_CATEGORIES.keys():
                shape_hist = {}
                n_search_regions = srm[args.region].getNumberOfSearchRegions()

                # Observed
                shape_hist['data_obs'] = ROOT.TH1D('data_obs', 'data_obs', n_search_regions, 0.5, n_search_regions+0.5)
                shape_hist['data_obs'].SetBinContent(1, 1.)

                # Background
                for sample_name in sample_manager.sample_groups.keys():
                    shape_hist[sample_name] = ROOT.TH1D(sample_name, sample_name, n_search_regions, 0.5, n_search_regions+0.5)
                    for sr in xrange(1, n_search_regions+1):
                        shape_hist[sample_name].SetBinContent(sr, list_of_values['bkgr'][sample_name][ac][sr])
                        shape_hist[sample_name].SetBinError(sr, list_of_errors['bkgr'][sample_name][ac][sr])
                        shape_hist[sample_name] = protectHist(shape_hist[sample_name])
                
                # Signal 
                for sample_name in list_of_values['signal'].keys():
                    out_path = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'shapes', str(args.year), args.selection, args.flavor, sample_name, ac+'.shapes.root')
                    makeDirIfNeeded(out_path)
                    out_shape_file = ROOT.TFile(out_path, 'recreate')
                    n_search_regions = srm[args.region].getNumberOfSearchRegions()
                    shape_hist[sample_name] = ROOT.TH1D(sample_name, sample_name, n_search_regions, 0.5, n_search_regions+0.5)
                    for sr in xrange(1, n_search_regions+1):
                        shape_hist[sample_name].SetBinContent(sr, list_of_values['signal'][sample_name][ac][sr])
                        shape_hist[sample_name].SetBinError(sr, list_of_errors['signal'][sample_name][ac][sr])
                        shape_hist[sample_name] = protectHist(shape_hist[sample_name])
                    shape_hist[sample_name].Write(sample_name)
                    bkgr_names = []
                    for bkgr_sample_name in background_collection+['data_obs']:
                        if shape_hist[bkgr_sample_name].GetSumOfWeights() > 0 and bkgr_sample_name != 'data_obs': bkgr_names.append(bkgr_sample_name)
                        shape_hist[bkgr_sample_name].Write(bkgr_sample_name)
                    out_shape_file.Close()
                    coupling_squared = args.rescaleSignal if args.rescaleSignal is not None else signal_couplingsquared[args.flavor][int(sample_name.split('-m')[-1])]
                    makeDataCard(str(ac), args.flavor, args.year, 0, sample_name, bkgr_names, args.selection, shapes=True, coupling_sq = coupling_squared)

    if args.makePlots:

        #
        # Make text files if requested
        #
        if not args.noTextFiles:

            for sr in search_region_keys:
                makeDirIfNeeded(destination+'/Tables/table_allCategories_'+str(sr)+'.txt')
                out_file = open(destination+'/Tables/table_allCategories_'+str(sr)+'.txt', 'w')

                # out_file.write('coupling squared of signal = '+str(coupling_squared) + ' \n')
                out_file.write(tab([CATEGORY_NAMES[i] for i in CATEGORIES]))

                out_file_tex = open(destination+'/Tables/table_allCategories_'+str(sr)+'_tex.txt', 'w')
                out_file_tex.write('\\begin{table}[] \n')
                out_file_tex.write("\\begin{tabular}{|"+'|'.join(['l']*len(CATEGORIES))+"|} \n")
                out_file_tex.write("\hline \n")
                out_file_tex.write('& '+'&'.join([CATEGORY_NAMES[i] for i in CATEGORIES])+' \n')
                # out_file_tex.write('& \\tau\\tau e & \\tau \\tau \\mu & \\tau e e & \\tau e \\mu & \\tau\\mu\\mu & lll & total \n')
                out_file_tex.write("\hline \n")

                for sample_name in sorted(list_of_values['signal'].keys(), key=lambda n : int(n.split('-m')[-1])):
                    out_file.write(sample_name+'\t')
                    out_file_tex.write(sample_name+' & ')

                    for c in CATEGORIES:
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

                for sample_name in background_collection:
                    out_file.write(sample_name+'\t')
                    out_file_tex.write(sample_name+' & ')

                    for c in CATEGORIES:
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
                for sample_name in background_collection:
                    # hist_to_plot[sample_name] = ROOT.TH1D(sample_name, sample_name, len(list_of_values['bkgr'][sample_name]), 0, len(list_of_values['bkgr'][sample_name]))
                    hist_to_plot[sample_name] = ROOT.TH1D(sample_name+supercat, sample_name+supercat, len(SUPER_CATEGORIES[supercat]), 0, len(SUPER_CATEGORIES[supercat]))
                    for i, c in enumerate(SUPER_CATEGORIES[supercat]):
                        # hist_to_plot[sample_name].SetBinContent(i+1, list_of_values['bkgr'][sample_name][c]['total'].getHist().GetSumOfWeights()) 
                        hist_to_plot[sample_name].SetBinContent(i+1, list_of_values['bkgr'][sample_name][c]['total']) 
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
                x_names = [CATEGORY_TEX_NAMES[n] for n in SUPER_CATEGORIES[supercat]]
                p = Plot(hist_to_plot, hist_names, name = 'Events-bar-signal-'+supercat+'-'+args.flavor, x_name = x_names, y_name = 'Events', y_log=True)
                p.drawBarChart(output_dir = destination+'/BarCharts', parallel_bins=True, message = args.message)
        
        if not args.noPieCharts:
            example_sample = background_collection[0]
            for i, c in enumerate(sorted(list_of_values['bkgr'][example_sample].keys())):

                n_filled_hist = len([v for v in list_of_values['bkgr'].values() if v[c]['total'] > 0])    #Remove hist with 0 events, they will otherwise crash the plotting code
                if n_filled_hist == 0: continue
                hist_to_plot_pie = ROOT.TH1D(str(c)+'_pie', str(c), n_filled_hist, 0, n_filled_hist)
                sample_names = []
                j = 1
                for s in background_collection:
                    fill_val = list_of_values['bkgr'][s][c]['total']
                    if fill_val > 0:
                        hist_to_plot_pie.SetBinContent(j, fill_val)
                        sample_names.append(s)
                        j += 1

                try:
                    extra_text = [extraTextFormat(c, ypos = 0.83)] if c is not None else None
                except:
                    extra_text = [extraTextFormat('other', ypos = 0.83)] if c is not None else None
                x_names = CATEGORY_TEX_NAMES.values()
                x_names.append('total')
                p = Plot(hist_to_plot_pie, sample_names, name = 'Events_'+str(c), x_name = CATEGORY_TEX_NAMES, y_name = 'Events', extra_text = extra_text)
                p.drawPieChart(output_dir = destination+'/PieCharts', draw_percent=True, message = args.message)

        # if not args.noCutFlow:
        #     import glob
        #     all_files = glob.glob(os.path.expandvars('$CMSSW_BASE/src/HNL/EventSelection/data/eventsPerCategory/'+selection_str+'/'+args.region+'/HNL-'+args.flavor+'*/events.root'))

        #     all_files = sorted(all_files, key = lambda k : int(k.split('/')[-2].split('.')[0].split('-m')[-1]))
        #     all_names = [k.split('/')[-1].split('.')[0] for k in all_files]

        #     from HNL.EventSelection.cutter import plotCutFlow
        #     out_name = os.path.expandvars('$CMSSW_BASE/src/HNL/EventSelection/data/Results/eventsPerCategory/'+selection_str+'/'+args.region) +'/CutFlow/Output'
        #     plotCutFlow(all_files, out_name, all_names, ignore_weights=True)

        #
        # Produce search region plots
        #
        from decimal import Decimal
        if not args.noSearchRegions:
            from HNL.EventSelection.searchRegions import plotLowMassRegions, plotHighMassRegions

            #First we need to make histograms that have different search region on x-axis
            list_of_sr_hist = {}

            for c in CATEGORIES:
                list_of_sr_hist[c] = {'signal':{}, 'bkgr':{}}
                #
                # Bkgr
                #
                for i_name, sample_name in enumerate(background_collection):
                    list_of_sr_hist[c]['bkgr'][sample_name] = ROOT.TH1D('_'.join([sample_name, str(c)]), '_'.join([sample_name, str(c)]), 
                        srm[args.region].getNumberOfSearchRegions(), 0.5, srm[args.region].getNumberOfSearchRegions()+0.5)
                    for sr in xrange(1, srm[args.region].getNumberOfSearchRegions()+1):
                        list_of_sr_hist[c]['bkgr'][sample_name].SetBinContent(sr, list_of_values['bkgr'][sample_name][c][sr])
                        list_of_sr_hist[c]['bkgr'][sample_name].SetBinError(sr, list_of_errors['bkgr'][sample_name][c][sr]) 

                #
                # Signal
                #   
                for i_name, sample_name in enumerate(list_of_values['signal'].keys()):
                    list_of_sr_hist[c]['signal'][sample_name] = ROOT.TH1D('_'.join([sample_name, str(c)]), '_'.join([sample_name, str(c)]), 
                        srm[args.region].getNumberOfSearchRegions(), 0.5, srm[args.region].getNumberOfSearchRegions()+0.5)
                    for sr in xrange(1, srm[args.region].getNumberOfSearchRegions()+1):
                        list_of_sr_hist[c]['signal'][sample_name].SetBinContent(sr, list_of_values['signal'][sample_name][c][sr]) 
                        list_of_sr_hist[c]['signal'][sample_name].SetBinError(sr, list_of_errors['signal'][sample_name][c][sr])

            def mergeCategories(ac, signalOrBkgr, sample_name):
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
                    list_of_ac_hist[ac]['signal'].append(mergeCategories(ANALYSIS_CATEGORIES[ac], 'signal', sample_name))
                
                bkgr_names = []
                for i_name, sample_name in enumerate(background_collection):
                    bkgr_names.append(sample_name)
                    list_of_ac_hist[ac]['bkgr'].append(mergeCategories(ANALYSIS_CATEGORIES[ac], 'bkgr', sample_name))

                extra_text = [extraTextFormat(ac, ypos = 0.82)]
                print ac
                if args.flavor: extra_text.append(extraTextFormat('|V_{'+args.flavor+'N}|^{2} = '+'%.0E' % Decimal(str(args.coupling**2)), textsize = 0.7))
                if args.rescaleSignal is not None:
                    extra_text.append(extraTextFormat('rescaled to |V_{'+args.flavor+'N}|^{2} = '+'%.0E' % Decimal(str(args.rescaleSignal)), textsize = 0.7))
                if args.region == 'lowMassSR':
                    plotLowMassRegions(list_of_ac_hist[ac]['signal'], list_of_ac_hist[ac]['bkgr'], signal_names+bkgr_names, 
                        out_path = destination+'/SearchRegions/'+ac, extra_text = extra_text, sample_groups = args.groupSamples)
                if args.region == 'highMassSR':
                    plotHighMassRegions(list_of_ac_hist[ac]['signal'], list_of_ac_hist[ac]['bkgr'], signal_names+bkgr_names, 
                        out_path = destination+'/SearchRegions/'+ac, extra_text = extra_text, sample_groups = args.groupSamples)

