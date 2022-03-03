#! /usr/bin/env python

#
#       Code to calculate signal and background yields
#

import numpy as np
from HNL.Tools.histogram import Histogram
from HNL.EventSelection.event import Event
from HNL.Tools.helpers import makeDirIfNeeded
from HNL.EventSelection.eventSelectionTools import select3TightLeptons
import ROOT

#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store', nargs='*',       default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='prelegacy', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
submission_parser.add_argument('--strategy',   action='store', default='cutbased',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA'])
submission_parser.add_argument('--analysis',   action='store', default='HNL',  help='Select the strategy to use to separate signal from background', choices=['HNL', 'AN2017014', 'ewkino'])
submission_parser.add_argument('--region',   action='store', default='baseline',  help='Choose the selection region')
submission_parser.add_argument('--logLevel',  action='store', default='INFO', help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])
submission_parser.add_argument('--flavor', action='store', default='',  help='Which coupling should be active?' , choices=['tau', 'e', 'mu', '2l', ''])


argParser.add_argument('--makePlots', action='store_true', default=False,  help='make plots')
argParser.add_argument('--masses', type=int, nargs='*',  help='Only run or plot signal samples with mass given in this list')


argParser.add_argument('--message', type = str, default=None,  help='Add a file with a message in the plotting folder')
argParser.add_argument('--makeDataCards', type = str, default=None,  help='Make data cards of the data you have', choices=['shapes', 'cutAndCount'])
argParser.add_argument('--rescaleSignal', type = float,  action='store', default=None,  help='Enter desired signal coupling squared')

args = argParser.parse_args()

nl = 3 if args.region != 'ZZCR' else 4


from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)

#
# Change some settings if this is a test
#
if args.isTest:
    args.isChild = True

    if args.sample is None: args.sample = 'DYJetsToLL-M-50'
    if args.subJob is None: args.subJob = '0'
    if args.year is None: args.year = '2016'
    from HNL.Tools.helpers import generateArgString
    arg_string =  generateArgString(argParser)
else:
    arg_string = None

#
# Load in the sample list 
#
from HNL.Samples.sampleManager import SampleManager
def getSampleManager(y):
    if args.noskim or args.selection != 'default':
        skim_str = 'noskim'
    elif args.region in ['highMassSR', 'lowMassSR']:
        skim_str = 'RecoGeneral'
    else:
        skim_str = 'Reco'
    file_list = 'fulllist_'+args.era+str(y)+'_mconly' if args.customList is None else args.customList

    if skim_str == 'RecoGeneral':
        sm = SampleManager(args.era, y, skim_str, file_list, skim_selection=args.selection, region=args.region)
    else:
        sm = SampleManager(args.era, y, skim_str, file_list)
    return sm

#
# function to have consistent categories in running and plotting
#
from HNL.EventSelection.eventCategorization import CATEGORIES, SUPER_CATEGORIES
from HNL.EventSelection.eventCategorization import CATEGORY_TEX_NAMES
def listOfCategories(region):
    # if region in ['baseline', 'highMassSR', 'lowMassSR']:
    #     return CATEGORIES
    # else:
    #     return [max(CATEGORIES)]
    return CATEGORIES

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

def getOutputBase(sample_name, prompt_string, era, year):
    tag_string = args.tag if args.tag is not None else 'General'
    if not args.isTest:
        output_string = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 'data', __file__.split('.')[0].rsplit('/')[-1], 
                                    era+'-'+year, '-'.join([args.strategy, args.selection, args.region, tag_string]), sample_name, prompt_string)
    else:
        output_string = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 'data', 'testArea', 
                        __file__.split('.')[0].rsplit('/')[-1], era+'-'+year, '-'.join([args.strategy, args.selection, args.region]), sample_name, prompt_string)
    return output_string

def getOutputName(sample, prompt_string, era, year):
    output_string = getOutputBase(sample.output, prompt_string, args.era, year)
    if args.isChild:
        output_string += '/tmp_'+sample.output

    subjobAppendix = 'subJob' + args.subJob if args.subJob else ''
    output_string += '/'+ sample.name +'_events_' +subjobAppendix+ '.root'
    makeDirIfNeeded(output_string)
    return output_string

#
# Prepare jobs
#
jobs = {}
for year in args.year:
    jobs[year] = []
    
    sample_manager = getSampleManager(year)

    for sample_name in sample_manager.sample_names:
        if args.sample and args.sample not in sample_name: continue 
        sample = sample_manager.getSample(sample_name)
        for njob in xrange(sample.returnSplitJobs()):
            jobs[year] += [(sample.name, str(njob))]

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
        for year in jobs.keys():
            submitJobs(__file__, ('sample', 'subJob'), jobs[year], argParser, jobLabel = 'calcYields', additionalArgs=[('year', year)])
        exit(0)

    if len(args.year) != 1:
        raise RuntimeError("At this point a single year should have been selected")
    year = args.year[0]
    sample_manager = getSampleManager(year)

    #
    # Load in sample and chain
    #
    for sample in sample_manager.sample_list:
        if sample.name not in sample_manager.sample_names: continue
        if args.sample and sample.name != args.sample: continue

        chain = sample.initTree(needhcount = False)

        if chain.is_data and args.region in ['baseline', 'highMassSR', 'lowMassSR']:
            raise RuntimeError('These options combined would mean unblinding. This is not allowed.')

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
        chain.year = year
        chain.era = args.era
        chain.selection = args.selection
        chain.region = args.region
        chain.strategy = args.strategy
        chain.analysis = args.analysis

        #
        # Get luminosity weight
        #
        from HNL.Weights.reweighter import Reweighter
        lw = Reweighter(sample, sample_manager)

        #
        # Object ID param
        #
        from HNL.ObjectSelection.objectSelection import getObjectSelection
        chain.obj_sel = getObjectSelection(args.selection)

        event = Event(chain, chain, is_reco_level=True, selection=args.selection, strategy=args.strategy, region=args.region)

        list_of_numbers = {}
        for c in listOfCategories(args.region):
            list_of_numbers[c] = {}
            for prompt_str in ['prompt', 'nonprompt', 'total']:
                list_of_numbers[c][prompt_str] = Histogram('_'.join([str(c), prompt_str]), lambda c: c.search_region-0.5, ('', 'Events'), 
                    np.arange(0., srm[args.region].getNumberOfSearchRegions()+1., 1.))                

        #
        # Loop over all events
        #
        from HNL.Tools.helpers import progress
        from HNL.Triggers.triggerSelection import passTriggers

        print 'tot_range', len(event_range)
        for entry in event_range:
            
            chain.GetEntry(entry)
            if args.isTest: progress(entry - event_range[0], len(event_range))

            cutter.cut(True, 'total')

            #
            #Triggers
            #
            if args.selection == 'AN2017014':
                if not cutter.cut(passTriggers(chain, analysis='HNL_old'), 'pass_triggers'): continue

            #Event selection    
            event.initEvent()

            if args.region == 'TauFakesTT':
                if not event.passedFilter(cutter, sample.name, inverted_cut = True, sideband = [2] if args.tag == 'TauFakes' else None): continue
            else:
                if not event.passedFilter(cutter, sample.name, sideband = [2] if args.tag == 'TauFakes' else None): continue

            nprompt = 0
            for i, index in enumerate(chain.l_indices):
                if args.tag == 'TauFakes':
                    if chain._lIsPrompt[index] or chain._lFlavor[index] < 2 or chain.l_istight[i]: nprompt += 1
                else:
                    if chain._lIsPrompt[index]: nprompt += 1
            
            prompt_str = 'prompt' if nprompt == nl else 'nonprompt'

            #Split made because for the other regions, the number of leptons is different and eventcategories dont make sense
            if args.region in ['baseline', 'highMassSR', 'lowMassSR']:
                event_category = event.event_category.returnCategory()
            else:
                event_category = max(CATEGORIES)

            chain.search_region = srm[args.region].getSearchRegion(chain)
            list_of_numbers[event_category][prompt_str].fill(chain, lw.getTotalWeight())
            list_of_numbers[event_category]['total'].fill(chain, lw.getTotalWeight())

        for prompt_str in ['prompt', 'nonprompt', 'total']:
            for i, c_h in enumerate(list_of_numbers.keys()):
                output_name = getOutputName(sample, prompt_str, chain.era, chain.year)
                if i == 0:
                    list_of_numbers[c_h][prompt_str].write(output_name, is_test=arg_string)
                else:
                    list_of_numbers[c_h][prompt_str].write(output_name, append=True, is_test=arg_string)

        cutter.saveCutFlow(getOutputName(sample, 'total', chain.era, chain.year))
    
    closeLogger(log)

#
# Merge if needed
#
else:
    from HNL.Tools.mergeFiles import merge
    import glob
    from HNL.Plotting.plot import Plot
    from HNL.EventSelection.eventCategorization import CATEGORY_NAMES

    from HNL.Tools.helpers import makePathTimeStamped
    from HNL.Plotting.plottingTools import extraTextFormat
    from HNL.Tools.helpers import getObjFromFile, tab, isValidRootFile
    from HNL.Analysis.analysisTypes import signal_couplingsquared

    for year in args.year:
        #
        # Check status of the jobs and merge
        #
        base_path = getOutputBase('dummy', 'dummy', args.era, year).rsplit('/', 2)[0]

        in_files = glob.glob(os.path.join(base_path, '*', '*'))
        merge(in_files, __file__, jobs[year], ('sample', 'subJob', 'year'), argParser, istest=args.isTest, additionalArgs= [('year', year)])
