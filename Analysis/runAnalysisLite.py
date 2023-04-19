#! /usr/bin/env python

#########################################################################
#                                                                       #
#   Code to plot basic variables and calculate yields                   # 
#                                                                       #                                   
#########################################################################

#
# Argument parser and logging
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true',       default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store', nargs='*',       default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='UL', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--sample',   action='store',            default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',            default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isTest',   action='store_true',       default=False,  help='Run a small test')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--dryRun',   action='store_true',       default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--genLevel',   action='store_true',     default=False,  help='Use gen level variables')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'tZq', 'TTT', 'HNLtauTest'])
submission_parser.add_argument('--strategy',   action='store', default='MVA',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA'])
submission_parser.add_argument('--analysis',   action='store', default='HNL',  help='Select the strategy to use to separate signal from background', choices=['HNL', 'AN2017014', 'ewkino', 'tZq'])
submission_parser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?')
submission_parser.add_argument('--includeData',   action='store', default=None, help='Also run over data', choices=['includeSideband', 'signalregion'])
submission_parser.add_argument('--logLevel',  action='store', default='INFO',  help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])
submission_parser.add_argument('--skimLevel',  action='store', default='Reco',  choices=['noskim', 'Reco', 'RecoGeneral', 'auto'])
submission_parser.add_argument('--customList',  action='store',      default=None,               help='Name of a custom sample list. Otherwise it will use the appropriate noskim file.')
submission_parser.add_argument('--tag',  action='store',      default=None,               help='Tag with additional information for the output, e.g. TauFakes, sidebandInMC')
submission_parser.add_argument('--bkgrOnly',   action='store_true',     default=False,  help='Run only the background')
submission_parser.add_argument('--blindStorage',   action='store_true',     default=False,  help='Do not store any signal region data')
argParser.add_argument('--merge', action = 'store_true', default=False)
argParser.add_argument('--ignoreSideband',   action='store_true',     default=False,  help='if there is a sideband nonprompt selection, please ignore it in the plotting')

args = argParser.parse_args()

print '\033[93m Warning: dr_closestJet contained a bug where it was always 0. In order to be consistent with the MVA training, it is now still manually set to 0 at all times. Please change this in the eventSelectionTools when retraining has occured.\033[0m'

from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)

from HNL.Tools.jobSubmitter import checkCompletedJobs, cleanJobFiles, checkShouldMerge, disableShouldMerge
if args.includeData is not None and args.region == 'NoSelection':
    raise RuntimeError('inData does not work with this selection region')

if args.strategy == 'MVA':
    if args.selection != 'default':
        raise RuntimeError("No MVA available for this selection")
    if args.genLevel:
        raise RuntimeError("No MVA available for at genLevel")
    if args.region == 'ZZCR':
        raise RuntimeError("No MVA available for 4 lepton selection")

if args.genLevel and args.selection == 'AN2017014':
    raise RuntimeError('gen level is currently not implemented on AN2017014 analysis selection')

if args.genLevel and args.tag == 'TauFakes':
    raise RuntimeError('gen level can not be used for estimating TauFake fractions')

#
# General imports
#
import os
from HNL.Tools.histogram import Histogram
from HNL.Tools.helpers import getObjFromFile, progress, makeDirIfNeeded
from HNL.EventSelection.bitCutter import Cutter
from HNL.Weights.reweighter import Reweighter
from HNL.TMVA.reader import ReaderArray
from HNL.Samples.sampleManager import SampleManager
from HNL.Samples.sample import Sample
from HNL.EventSelection.event import Event
from HNL.Triggers.triggerSelection import passTriggers
from ROOT import TFile
import numpy as np

def customizeListToUse(y):
    custom_list_to_use = args.customList
    if args.customList is not None:
        for tmp_year in args.year:
            if tmp_year in custom_list_to_use:
                custom_list_to_use = custom_list_to_use.replace(tmp_year, str(y))
    return custom_list_to_use


def getSampleManager(y):
    if args.genLevel:
        skim_str = 'noskim'
#    elif args.includeData == 'includeSideband':
#        skim_str = 'Reco'
    else:
        skim_str = args.skimLevel
    
    #Translate the custom list to the correct year if needed
    custom_list_to_use = customizeListToUse(y)
    file_list = 'runAnalysisLite/fulllist_'+args.era+str(y) if custom_list_to_use is None else custom_list_to_use
#    file_list = 'Skimmer/skimlist_{0}{1}'.format(args.era, y) if args.customList is None else args.customList


    sm = SampleManager(args.era, y, skim_str, file_list, skim_selection=args.selection, region=args.region)
    return sm

if args.isTest:
    if args.year is None: args.year = ['2017']
    if args.sample is None: 
        args.sample = 'WZTo3LNu' if not args.region == 'ZZCR' else 'ZZTo4L'
    args.isChild = True
    if args.subJob is None: args.subJob = '0'
    from HNL.Tools.helpers import generateArgString
    arg_string =  generateArgString(argParser)
else:
    arg_string = None

#
# Some constants to make referring to signal leptons more readable
#
l1 = 0
l2 = 1
l3 = 2
l4 = 3

nl = 3 if args.region != 'ZZCR' else 4

import HNL.EventSelection.eventCategorization as cat

#
# Define categories to use
#
def listOfCategories(region):
    if nl == 3:
        return cat.CATEGORIES
    else:
        return [max(cat.CATEGORIES)]

categories = listOfCategories(args.region) 
reco_or_gen_str = 'reco' if not args.genLevel else 'gen'

import HNL.Analysis.analysisTypes as at
if args.region == 'NoSelection':
    var = at.var_noselection
elif args.strategy == 'MVA':
    var = at.returnVariables(nl, not args.genLevel, args.region)
else:
    var = at.returnVariables(nl, not args.genLevel)

#
# Prepare jobs
#
if not args.isTest:
    jobs = {}
    for year in args.year:
        jobs[year] = []
        sample_manager = getSampleManager(year)
        for sample_name in sample_manager.sample_names:
            #if args.includeData is None and 'Data' in sample_name: continue
            #if args.bkgrOnly and 'HNL' in sample_name: continue
            sample = sample_manager.getSample(sample_name)
            if sample.xsec is not None: continue
            #if args.sample and args.sample != sample.name: continue
            for njob in xrange(sample.returnSplitJobs()): 
                jobs[year] += [(sample.name, str(njob), None)]
            #jobs[year] += [(sample.name, str(0), None)]
#
# Submit subjobs
#

from HNL.Tools.jobSubmitter import submitJobs, checkShouldMerge
if not args.isChild and not args.merge:
    # if not args.dryRun and checkShouldMerge(__file__, argParser):
    #     raise RuntimeError("Already existing files available. You would be overwriting")
    for year in jobs.keys():
        submitJobs(__file__, ('sample', 'subJob'), jobs[year], argParser, jobLabel = 'runAnalysis-'+str(year)+'-'+args.region, additionalArgs= [('year', year)])
    exit(0)

from HNL.EventSelection.eventSelector import signal_regions

#
# Extra imports for dividing by region
#
from HNL.EventSelection.searchRegions import SearchRegionManager
srm = {}
srm[args.region] = SearchRegionManager(args.region)

def getOutputName(st, y, tag=None):
    translated_tag = '' if tag is None else '-'+tag
    if not args.isTest:
        return os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 'data', 'runAnalysisLite', args.analysis+translated_tag, '-'.join([args.strategy, args.selection, args.region, reco_or_gen_str]), args.era+'-'+y, st)
    else:
        return os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 'data', 'testArea', 'runAnalysisLite', args.analysis+translated_tag, '-'.join([args.strategy, args.selection, args.region, reco_or_gen_str]), args.era+'-'+y, st)

if not args.merge:
    #
    # Loop over samples and events
    #
    if len(args.year) != 1:
        raise RuntimeError("At this point a single year should have been selected")
    year = args.year[0]
    sample_manager = getSampleManager(year)
    
    #Start a loop over samples
    sample = sample_manager.getSample(args.sample)
    
    #
    # Do not run over samples that we dont need
    #
    if sample.name not in sample_manager.sample_names: 
        raise RuntimeError("sample not defined in sample_manager list")
    
    #
    # Initialize chain
    #
    chain = sample.initTree(needhcount=False)
    if args.includeData is None and chain.is_data: exit(0)
    
    
    #
    # Define output name
    #
    subjobAppendix = '_subJob' + args.subJob if args.subJob else ''
    
    is_signal = 'HNL' in sample.name
    if chain.is_data:
        signal_str = 'data'
        sample_output_name = sample.output
    else:
        signal_str = 'signal' if is_signal else 'bkgr'
        sample_output_name = sample.output
    
    
    output_name_full = os.path.join(getOutputName(signal_str, year, args.tag), sample_output_name) 
    
    
    if args.isChild:
        output_name_full += '/tmp_'+sample_output_name+ '/'+sample.name+'_'
    else:
        output_name_full += '/'
            
    write_name = 'variables'
    output_name_full += write_name+subjobAppendix+ '.json'
    
    #
    # Check if we need to run the sideband
    #
    need_sideband = None
    if args.includeData == 'includeSideband':
        need_sideband = [0,1,2]
    elif not chain.is_data and args.tag == 'sidebandInMC':
        need_sideband = [0,1,2]
    
    #
    # Set event range
    #
    if args.isTest:
        up_limit = 20000
        if len(sample.getEventRange(0)) < up_limit:
            event_range = sample.getEventRange(0)
        else:
            event_range = xrange(up_limit)
    else:
        event_range = sample.getEventRange(args.subJob)
        #event_range = xrange(chain.GetEntries())
    
    
    #
    # Load in sample and chain
    #
    event = Event(sample, chain, sample_manager, is_reco_level=not args.genLevel, selection=args.selection, strategy=args.strategy, region=args.region, analysis=args.analysis, year = year, era = args.era, ignore_fakerates = args.tag != 'sidebandInMC' and args.includeData != 'includeSideband')
    
    #
    # Create cutter to provide cut flow
    #
    cutter = Cutter(name = 'nominal', chain = chain, categories = listOfCategories(args.region))
    
    #
    # Load in MVA reader if needed
    #
    if args.strategy == 'MVA':
        tmva = ReaderArray(chain, 'kBDT', args.region, args.era)
    
    #
    # Loop over all events
    #
    out_file_obj = [] 
    for entry in event_range:
    
        chain.GetEntry(entry)
        progress(entry - event_range[0], len(event_range), print_every = None if args.isTest else 10000)
    
        cutter.cut(True, 'Total')
        #
        # Event selection
        #
    
        event.initEvent(reset_obj_sel = True)
        
        if args.tag == 'TauFakePurity':
            chain.obj_sel['tau_wp'] = 'FO'            
    
        is_sideband_event = False
        passed_tight_selection = event.passedFilter(cutter, sample.name, sideband = [2] if args.tag == 'TauFakes' else None, for_training = 'ForTraining' in args.region, manually_blinded = True, calculate_weights = args.tag != 'TauFakes') #Dont calculate weights if we're trying to find the tau fake fractions or you'll get an error because the fractions arent stored yet...
        if need_sideband is None:
            if not passed_tight_selection: continue
        else:
            if not passed_tight_selection:
                # If tight selection failed because of something beyond the three tight selection, the next step should be relatively fast
                passed_sideband_selection = event.passedFilter(cutter, sample.name, sideband = need_sideband, for_training = 'ForTraining' in args.region, calculate_weights = True)
                if not passed_sideband_selection: continue
                is_sideband_event = True
            else:
                pass
    
        #
        # Make the code blind in signal regions
        # If you ever remove these next lines, remove manually_blinded as well
        #
        if args.region in signal_regions and chain.is_data and not is_sideband_event and args.blindStorage:
            continue            
    
        #
        # Determine if it is a prompt event
        # Depending on the previous step, the selection should be the tight or the FO (because of rerunning)
        #
        if args.region != 'NoSelection':
            if len(chain.l_flavor) == chain.l_flavor.count(2): continue #Not all taus
    
            #Need to overwrite nonprompt in special cases
            if not 'Data' in sample.name and args.tag in ['TauFakes', 'TauFakePurity']:
                nprompt = 0
                for i, index in enumerate(chain.l_indices):
                    #For taufakes we're only interested in FO tau to make the prompt consideration
                    if args.tag == 'TauFakes':
                        if chain._lIsPrompt[index] or chain._lFlavor[index] < 2 or chain.l_istight[i]: nprompt += 1
                    elif args.tag == 'TauFakePurity':
                        if chain._lIsPrompt[index] or chain._lFlavor[index] < 2: nprompt += 1
               
                chain.is_prompt = True if nprompt == nl else False
                if args.tag == 'TauFakePurity':
                    chain.istight = all([chain.l_istight[l] for l in range(nl) if chain.l_flavor[l] == 2])
        else:
            chain.category = max(cat.CATEGORIES)
    
        if args.strategy == 'MVA':
            tmva.predictAndWriteAll(chain)
    
        if chain.mediummass250400e >= 0.9 and srm[args.region].getSearchRegion(chain) > 16 and chain.category in [19, 21, 22, 23, 24, 25, 26]: 
        #if srm[args.region].getSearchRegion(chain) > 16 and chain.category in [19, 21, 22, 23, 24, 25, 26]: 
            out_file_obj.append([str(chain._runNb), str(chain._lumiBlock), str(chain._eventNb), str(chain.category)])
    
    import json
    json_object = json.dumps(out_file_obj)
    makeDirIfNeeded(output_name_full)
    with open(output_name_full, 'w') as outfile:
        outfile.write(json_object)
    
    #
    # Save histograms
    #
    closeLogger(log)
else:
    
    for y in args.year:
        failed_jobs = checkCompletedJobs(__file__, jobs[y], argParser, additionalArgs= [('year', y)])
        if failed_jobs is not None and len(failed_jobs) != 0:   
            should_resubmit = raw_input("Would you like to resubmit the failed jobs? (y/n) \n")
            if should_resubmit == 'y' or should_resubmit == 'Y':
                print 'resubmitting:'
            else:
                pass    
            if should_resubmit != 'skip': exit(0)    
#        cleanJobFiles(argparser, __file__)

    import glob
    import json
    final_out_file = getOutputName('data', '-'.join(sorted(args.year)))+'/allevents.json'
    from HNL.Tools.helpers import makeDirIfNeeded
    makeDirIfNeeded(final_out_file)
    out_obj = []
    for y in args.year:
        for out_name in glob.glob(getOutputName('data', y)+'/*/*/*.json'):
            f = open(out_name)
            tmp_list = json.load(f)
            out_obj.extend([x for x in tmp_list])
            f.close()

    out_json = json.dumps(out_obj)
    with open(final_out_file, "w") as outfile:
        outfile.write(out_json)
    


