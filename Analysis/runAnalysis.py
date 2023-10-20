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
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'tZq', 'TTT', 'HNLtauTest', 'corrMet', 'prompt'])
submission_parser.add_argument('--strategy',   action='store', default='MVA',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA'])
submission_parser.add_argument('--analysis',   action='store', default='HNL',  help='Select the strategy to use to separate signal from background', choices=['HNL', 'AN2017014', 'ewkino', 'tZq'])
submission_parser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?')
submission_parser.add_argument('--includeData',   action='store', default=None, help='Also run over data', choices=['includeSideband', 'signalregion'])
submission_parser.add_argument('--logLevel',  action='store', default='INFO',  help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])
submission_parser.add_argument('--skimLevel',  action='store', default='Reco',  choices=['noskim', 'Reco', 'RecoGeneral', 'auto'])
submission_parser.add_argument('--customList',  action='store',      default=None,               help='Name of a custom sample list. Otherwise it will use the appropriate noskim file.')
submission_parser.add_argument('--systematics',  action='store',      default='nominal',               help='Choose level of systematics.', choices = ['nominal', 'limited', 'full'])
submission_parser.add_argument('--tag',  action='store',      default=None,               help='Tag with additional information for the output, e.g. TauFakes, sidebandInMC')
submission_parser.add_argument('--bkgrOnly',   action='store_true',     default=False,  help='Run only the background')
submission_parser.add_argument('--blindStorage',   action='store_true',     default=False,  help='Do not store any signal region data')

argParser.add_argument('--makePlots',   action='store_true',    default=False,  help='Use existing root files to make the plots')
argParser.add_argument('--showCuts',   action='store_true',     default=False,  help='Show what the pt cuts were for the category in the plots')
argParser.add_argument('--individualSamples',   action='store_true', default=False,  help='plot each input sample separately')
argParser.add_argument('--makeDataCards', action = 'store_true',  help='Make data cards of the data you have')
argParser.add_argument('--rescaleSignal', type = float,  action='store', default=None,  help='Enter desired signal coupling squared')
argParser.add_argument('--masses', type=float, nargs='*',  help='Only run or plot signal samples with mass given in this list')
argParser.add_argument('--flavor', action='store', default='',  help='Which coupling should be active?' , choices=['tau', 'e', 'mu', '2l', ''])
argParser.add_argument('--cutFlowOnly',   action='store_true',   default=False,  help='Do not overwrite any plots, just produce cutflow tables')
argParser.add_argument('--signalOnly',   action='store_true',   default=False,  help='Run or plot a only the signal')
argParser.add_argument('--plotBkgrOnly',   action='store_true',     default=False,  help='Plot only the background')
argParser.add_argument('--plotSingleBin',   action='store_true',     default=False,  help='Run or plot a only the background')
argParser.add_argument('--categoriesToPlot',   action='store',     default='super',  help='What categories to use', choices=['original', 'analysis', 'super', 'splitanalysis', 'leadingflavor', 'trigger', 'sign'])
argParser.add_argument('--category',   action='store',     default=None,  help='What specific category to use')
argParser.add_argument('--searchregion',   action='store',  nargs='*',   default=None,  help='Is there a specific search region to probe?')
argParser.add_argument('--additionalCondition',   action='store',     default=None,  help='Additional condition for selection')
argParser.add_argument('--variables', nargs='*',  help='list of variables to process')
argParser.add_argument('--ignoreSystematics',   action='store_true',     default=False,  help='ignore systematics in plots')
argParser.add_argument('--mergeYears',   action='store_true',     default=False,  help='combine all years specified in year arg in preparation for plots')
argParser.add_argument('--combineYears',   action='store_true',     default=False,  help='combine all years specified in year arg in plots')
argParser.add_argument('--submitPlotting',   action='store_true',     default=False,  help='Send the plotting code to HTCondor')
argParser.add_argument('--unblind',   action='store_true',     default=False,  help='Also plot the observed data in signal region')
argParser.add_argument('--plotDirac',   action='store_true',     default=False,  help='plot dirac type HNL')
argParser.add_argument('--plotDisplaced',   action='store_true',     default=False,  help='plot displaced type HNL')
argParser.add_argument('--ignoreSideband',   action='store_true',     default=False,  help='if there is a sideband nonprompt selection, please ignore it in the plotting')
argParser.add_argument('--paperPlots',   action='store',     default=None,  help='Slightly adapt the plots to be paper-approved')
argParser.add_argument('--normalizeSignal',   action='store',     default=None,  help='Add a custom signal normalization function')

args = argParser.parse_args()

print '\033[93m Warning: dr_closestJet contained a bug where it was always 0. In order to be consistent with the MVA training, it is now still manually set to 0 at all times. Please change this in the eventSelectionTools when retraining has occured.\033[0m'

USE_CORRECTED_MET = False
if args.selection == 'corrMet':
    args.selection = 'default'
    USE_CORRECTED_MET = True
    

from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)

if args.includeData is not None and args.region == 'NoSelection':
    raise RuntimeError('inData does not work with this selection region')

if args.strategy == 'MVA':
    if args.selection not in ['default', 'corrMet']:
        raise RuntimeError("No MVA available for this selection")
    if args.genLevel:
        raise RuntimeError("No MVA available for at genLevel")
    if args.region == 'ZZCR':
        raise RuntimeError("No MVA available for 4 lepton selection")

if args.genLevel and args.selection == 'AN2017014':
    raise RuntimeError('gen level is currently not implemented on AN2017014 analysis selection')

if args.genLevel and args.tag == 'TauFakes':
    raise RuntimeError('gen level can not be used for estimating TauFake fractions')

if args.combineYears:
    print '\033[93m Warning: Make sure you did a "mergeYears" first\033[0m'

#if args.mergeYears and len(args.year) == 1:
#    raise RuntimeError('Youre going to overwrite it')

#
# General imports
#
import os
from HNL.Tools.histogram import Histogram
from HNL.Tools.mergeFiles import merge
from HNL.Tools.helpers import getObjFromFile, progress, makeDirIfNeeded
from HNL.EventSelection.cutter import CutterCollection
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
    file_list = 'fulllist_'+args.era+str(y) if custom_list_to_use is None else custom_list_to_use

    sm = SampleManager(args.era, y, skim_str, file_list, skim_selection=args.selection, region=args.region)
    return sm

if args.isTest:
    if args.year is None: args.year = ['2017']
    if args.sample is None and not args.makePlots: 
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

categories = listOfCategories(args.region) if args.category is None else [args.category]
reco_or_gen_str = 'reco' if not args.genLevel else 'gen'

import HNL.Analysis.analysisTypes as at
if args.region == 'NoSelection':
    var = at.var_noselection
elif args.strategy == 'MVA':
    var = at.returnVariables(nl, not args.genLevel, args.region)
else:
    var = at.returnVariables(nl, not args.genLevel)

#Loading something in for plot jobs
if args.makePlots or args.makeDataCards:
    sorted_analysis_categories = cat.ANALYSIS_CATEGORIES.keys() if args.category is None else [args.category]
    sorted_splitanalysis_categories = cat.ANALYSIS_SPLITOSSF_CATEGORIES.keys() if args.category is None else [args.category]
    sorted_leadingflavor_categories = cat.LEADING_FLAVOR_CATEGORIES.keys() if args.category is None else [args.category]
    sorted_sign_categories = cat.SIGN_CATEGORIES.keys() if args.category is None else [args.category]
    sorted_trigger_categories = cat.TRIGGER_CATEGORIES.keys() if args.category is None else [args.category]
    from HNL.Analysis.analysisTypes import getRelevantSuperCategories
    sorted_super_categories = getRelevantSuperCategories(cat.SUPER_CATEGORIES.keys(), args.region) if args.category is None else [args.category]

    #Reset list_of_hist
    category_dict = {}
    if args.categoriesToPlot == 'analysis':
        category_dict['analysis'] = (sorted_analysis_categories, ['('+'||'.join(['category=={0}'.format(x) for x in cat.ANALYSIS_CATEGORIES[y]])+')' for y in sorted_analysis_categories], {y :[str(x) for x in cat.ANALYSIS_CATEGORIES[y]] for y in sorted_analysis_categories})
    if args.categoriesToPlot == 'splitanalysis':
        category_dict['splitanalysis'] = (sorted_splitanalysis_categories, ['('+'||'.join(['category=={0}'.format(x) for x in cat.ANALYSIS_SPLITOSSF_CATEGORIES[y]])+')' for y in sorted_splitanalysis_categories], {y :[str(x) for x in cat.ANALYSIS_SPLITOSSF_CATEGORIES[y]] for y in sorted_splitanalysis_categories})
    if args.categoriesToPlot == 'leadingflavor':
        category_dict['leadingflavor'] = (sorted_leadingflavor_categories, ['('+'||'.join(['category=={0}'.format(x) for x in cat.LEADING_FLAVOR_CATEGORIES[y]])+')' for y in sorted_leadingflavor_categories], {y :[str(x) for x in cat.LEADING_FLAVOR_CATEGORIES[y]] for y in sorted_leadingflavor_categories})
    if args.categoriesToPlot == 'sign':
        category_dict['sign'] = (sorted_sign_categories, ['('+'||'.join(['category=={0}'.format(x) for x in cat.SIGN_CATEGORIES[y]])+')' for y in sorted_sign_categories], {y :[str(x) for x in cat.SIGN_CATEGORIES[y]] for y in sorted_sign_categories})
    if args.categoriesToPlot == 'super':
        category_dict['super'] = (sorted_super_categories, ['('+'||'.join(['category=={0}'.format(x) for x in cat.SUPER_CATEGORIES[y]])+')' for y in sorted_super_categories], {y:[str(x) for x in cat.SUPER_CATEGORIES[y]] for y in sorted_super_categories})
    if args.categoriesToPlot == 'trigger':
        category_dict['trigger'] = (sorted_trigger_categories, ['('+'||'.join(['category=={0}'.format(x) for x in cat.TRIGGER_CATEGORIES[y]])+')' for y in sorted_trigger_categories], {y:[str(x) for x in cat.TRIGGER_CATEGORIES[y]] for y in sorted_trigger_categories})
    category_dict['original'] = ([x for x in categories], ['(category=={0})'.format(x) for x in categories], {y : [str(y)] for y in categories})

#
# Prepare jobs
#
jobs = {}
if not args.isTest:
    if (args.makeDataCards or args.makePlots) and args.submitPlotting and not args.isChild:

        if args.variables is None:
            subjob_var = var.keys()
        else:
            subjob_var = args.variables
        subjob_var.append('searchregion')
        n_var = 8
        subjob_var = [subjob_var[i:i+n_var] for i in range(0, len(subjob_var), n_var)]
        
        if args.category is None:
            subjob_cat = [x for x in category_dict[args.categoriesToPlot][0]]
        else:
            subjob_cat = [args.category] 
       
        jobs = [] 
        if args.makePlots and not args.mergeYears:
            for c in subjob_cat:
                for v in subjob_var:
                    jobs += [(c, v)]
        elif args.makeDataCards and not args.mergeYears:
            for c in subjob_cat:
                jobs += [(c, '0')]
        else:
            for year in args.year:
                jobs += [(year, '0')]
    else:
        for year in args.year:
            jobs[year] = []
            sample_manager = getSampleManager(year)
        
            for sample_name in sample_manager.sample_names:
                if args.includeData is None and 'Data' in sample_name: continue
                if args.bkgrOnly and 'HNL' in sample_name: continue
                if args.signalOnly and not 'HNL' in sample_name: continue
                sample = sample_manager.getSample(sample_name)
                if args.sample and args.sample != sample.name: continue
        #        if args.masses is not None and sample.is_signal and sample.mass not in args.masses: continue
                for njob in xrange(sample.returnSplitJobs()): 
                    jobs[year] += [(sample.name, str(njob), None)]
else:
    for year in args.year:
        jobs[year] = []

#
# Submit subjobs
#

from HNL.Tools.jobSubmitter import submitJobs, checkShouldMerge
if (args.makeDataCards or args.makePlots) and args.submitPlotting and not args.isChild:
    label = 'datacards' if args.makeDataCards else 'plotting'
    if args.makeDataCards and not args.mergeYears:
        args_of_interest = ['category', 'subJob']
    elif args.makePlots and not args.mergeYears:
        args_of_interest = ['category', 'variables']
    else:
        args_of_interest = ['year', 'subJob']
    submitJobs(__file__, args_of_interest, jobs, argParser, jobLabel='runAnalysis-'+label+'-'+args.region, include_all_groups = True)
    exit(0)

if not args.isChild and not args.makePlots and not args.makeDataCards:
    # if not args.dryRun and checkShouldMerge(__file__, argParser):
    #     raise RuntimeError("Already existing files available. You would be overwriting")
    for year in jobs.keys():
        submitJobs(__file__, ('sample', 'subJob'), jobs[year], argParser, jobLabel = 'runAnalysis-'+str(year)+'-'+args.region, additionalArgs= [('year', year)])
    exit(0)

from HNL.EventSelection.eventSelector import signal_regions

def getOutputName(st, y, tag=None):
    translated_tag = '' if tag is None else '-'+tag
    if not args.isTest:
        return os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 'data', 'runAnalysis', args.analysis+translated_tag, '-'.join([args.strategy, args.selection, args.region, reco_or_gen_str]), args.era+'-'+y, st)
    else:
        return os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 'data', 'testArea', 'runAnalysis', args.analysis+translated_tag, '-'.join([args.strategy, args.selection, args.region, reco_or_gen_str]), args.era+'-'+y, st)

def getSystToRun(year, proc, split_corr = False):
    from HNL.Systematics.systematics import SystematicJSONreader
    sjr = SystematicJSONreader(datadriven_processes = ['non-prompt'] if args.includeData == 'includeSideband' else None)
    syst_to_run = ['nominal']
    if args.systematics == 'full' and not args.ignoreSystematics: syst_to_run += sjr.compileListOfGeneralSystematics('rerun', proc, year.split('-'), split_syst=True, split_corr=split_corr)
    return syst_to_run    

#
# Loop over samples and events
#
if not args.makePlots and not args.makeDataCards and not args.mergeYears:

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


    if args.signalOnly and args.genLevel:       output_name_full = os.path.join(getOutputName(signal_str, year, args.tag), 'signalOrdering', sample_output_name)
    else:      output_name_full = os.path.join(getOutputName(signal_str, year, args.tag), sample_output_name) 


    if args.isChild:
        output_name_full += '/tmp_'+sample_output_name+ '/'+sample.name+'_'
    else:
        output_name_full += '/'
            
    write_name = 'variables'
    output_name_full += write_name+subjobAppendix+ '.root'

    #
    # Check if we need to run the sideband
    #
    need_sideband = None
    if args.tag == 'TauFakes':
        need_sideband = [2]
    elif args.includeData == 'includeSideband':
        need_sideband = [0,1,2]
    elif not chain.is_data and args.tag == 'sidebandInMC':
        need_sideband = [0,1,2]

    #
    # Set event range
    #
    if args.isTest:
        up_limit = 20000 if args.systematics != 'full' else 2000
        if len(sample.getEventRange(0)) < up_limit:
            event_range = sample.getEventRange(0)
        else:
            event_range = xrange(up_limit)
    else:
        event_range = sample.getEventRange(args.subJob)


    #
    # Skip HNL masses that were not defined
    #
    if args.masses is not None and sample.mass not in args.masses: exit(0)

    def runEventLoop(chain, output_name, systematic='nominal'):

        #
        # Load in sample and chain
        #
        event = Event(sample, chain, sample_manager, is_reco_level=not args.genLevel, selection=args.selection, strategy=args.strategy, region=args.region, analysis=args.analysis, year = year, era = args.era, ignore_fakerates = args.tag != 'sidebandInMC' and args.includeData != 'includeSideband', fakerate_from_data = args.includeData == 'includeSideband', sideband=need_sideband, nonprompt_scalefactors = args.tag == 'nonpromptSFtest', use_corrected_met = USE_CORRECTED_MET)

        #
        # Prepare output tree
        #
        from HNL.Tools.outputTree import OutputTree
        branches = []
        for v in var.keys():
            branches.extend(['{0}/F'.format(v)])
        branches.extend(['weight/F', 'isprompt/O', 'category/I', 'searchregion/I', 'issideband/O'])
        branches.extend(['isPreHEMrun/O','objectInHEM/O'])
        if args.tag == 'TauFakePurity': branches.extend(['istight/O'])
        if not args.genLevel: 
            branches.extend(event.reweighter.returnBranches())
            if systematic == 'nominal': branches.extend(event.systematics.returnBranches(args.sample))
        if not sample.is_data and not args.genLevel:
            branches.extend(['isChargeFlipEvent/O'])
        if sample.is_signal:
            branches.extend(['isDiracType/O', 'diracSF/F'])
        if args.tag == 'fakePtTest':
            branches.extend(['leadingFakeLeptonPt/F', 'leadingFakeMuonPt/F', 'leadingFakeElectronPt/F'])

        branches.extend(['eventNb/F', 'lumiBlock/F', 'runNb/F'])

        #tmp  
        if not args.genLevel: 
            branches.extend(['passedChargeConsistency/F'])        

        if systematic != 'nominal':
            from HNL.Systematics.systematics import SystematicJSONreader
            sjr = SystematicJSONreader(datadriven_processes = ['non-prompt'] if args.includeData == 'includeSideband' else None)
            systematic_corrname = sjr.getCorrName(systematic, year)
        else:
            systematic_corrname = systematic

        output_tree = OutputTree('events_{0}'.format(systematic_corrname), output_name_full, branches = branches, branches_already_defined = systematic != 'nominal')

        #
        # Create cutter to provide cut flow
        #
        cutter = CutterCollection(names = [systematic+'nominal', systematic+'sideband'], chain = chain, categories = listOfCategories(args.region), searchregions = range(1, event.srm.getNumberOfSearchRegions()+1))

        #
        # Load in MVA reader if needed
        #
        if args.strategy == 'MVA':
            tmva = ReaderArray(chain, 'kBDT', args.region, args.era)

        from HNL.Systematics.systematics import prepareForRerunSyst
        event = prepareForRerunSyst(chain, event, systematic)

        #
        # Loop over all events
        #
        for entry in event_range:
            chain.GetEntry(entry)
            progress(entry - event_range[0], len(event_range), print_every = None if args.isTest else 10000)

            #
            # Event selection
            #

            event.initEvent(reset_obj_sel = True)
            cutter.cut(True, 'Sample Skim Baseline')
            
            if args.tag == 'TauFakePurity':
                chain.obj_sel['tau_wp'] = 'FO'            
       
            if not event.passedFilter(cutter, sample.name, for_training = 'ForTraining' in args.region, calculate_weights = False): continue
            is_sideband_event = chain.is_sideband
      
            if args.tag == 'TauFakes':
                if not is_sideband_event: continue
                is_sideband_event = False

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
     
            if args.tag == 'fakePtTest': 
                if is_sideband_event:
                    leading_fake_index = -1
                    for l in xrange(len(chain.l_pt)):
                        if chain.l_isFO[l] and not chain.l_istight[l]:
                            if leading_fake_index == -1: leading_fake_index = l
                            else:
                                leading_fake_index = l if chain.l_pt[l] > chain.l_pt[leading_fake_index] else leading_fake_index
                    chain.leadingFakeLeptonPt = chain.l_pt[leading_fake_index] if leading_fake_index > -1 else -1.
                    chain.leadingFakeElectronPt = chain.l_pt[leading_fake_index] if leading_fake_index > -1 and chain.l_flavor[leading_fake_index] == 0 else -1.
                    chain.leadingFakeMuonPt = chain.l_pt[leading_fake_index] if leading_fake_index > -1 and chain.l_flavor[leading_fake_index] == 1 else -1.
                else:
                    chain.leadingFakeLeptonPt = -1.
                    chain.leadingFakeElectronPt = -1.
                    chain.leadingFakeMuonPt = -1.
       
            #
            # Fill tree
            #
            if Sample.getSignalDisplacedString(sample.name):
                output_tree.setTreeVariable('ctauHN', chain._ctauHN)
            if not args.genLevel: event.reweighter.fillTreeWithWeights(output_tree)
            for v in var.keys():
                output_tree.setTreeVariable(v, var[v][0](chain))
       
            if not sample.is_data and not args.genLevel:
                from HNL.EventSelection.eventSelectionTools import isChargeFlip
                output_tree.setTreeVariable('isChargeFlipEvent', chain.is_charge_flip_event)
   
            output_tree.setTreeVariable('weight', event.reweighter.getTotalWeight() if not args.genLevel else event.reweighter.getLumiWeight())
            output_tree.setTreeVariable('isprompt', chain.is_prompt)
            output_tree.setTreeVariable('category', chain.category)
            output_tree.setTreeVariable('searchregion', chain.searchregion)
            output_tree.setTreeVariable('issideband', is_sideband_event)
            from HNL.EventSelection.eventSelectionTools import objectInHEMregion
            output_tree.setTreeVariable('objectInHEM', objectInHEMregion(chain, chain))
            output_tree.setTreeVariable('isPreHEMrun', chain._runNb < 319077)
            if args.tag == 'TauFakePurity':
                output_tree.setTreeVariable('istight', chain.istight)
            if sample.is_signal:
                output_tree.setTreeVariable('isDiracType', chain._gen_isDiracType)
                output_tree.setTreeVariable('diracSF', event.reweighter.lumiweighter.getDiracTypeSF())
            if args.tag == 'fakePtTest':
                output_tree.setTreeVariable('leadingFakeLeptonPt', chain.leadingFakeLeptonPt)
                output_tree.setTreeVariable('leadingFakeElectronPt', chain.leadingFakeElectronPt)
                output_tree.setTreeVariable('leadingFakeMuonPt', chain.leadingFakeMuonPt)
            output_tree.setTreeVariable('eventNb', chain._eventNb)
            output_tree.setTreeVariable('lumiBlock', chain._lumiBlock)
            output_tree.setTreeVariable('runNb', chain._runNb)
            
            #tmp
            if not args.genLevel:
                from HNL.EventSelection.eventSelectionTools import passesChargeConsistencyDiElectron
                output_tree.setTreeVariable('passedChargeConsistency', passesChargeConsistencyDiElectron(chain, chain))
                                                  
 
            if systematic == 'nominal' and not args.genLevel: event.systematics.storeAllSystematicsForShapes(output_tree, args.sample)
            output_tree.fill()
 
        #
        # Save histograms
        #
        output_tree.write(is_test = arg_string if args.isTest else None, append = systematic != 'nominal')
        
        if systematic == 'nominal': cutter.saveCutFlow(output_name, arg_string = arg_string if args.isTest else None)
  
    for syst in getSystToRun(year, args.sample): 
        print 'Running {0}'.format(syst)
        runEventLoop(chain, output_name_full, syst)
    
    closeLogger(log)

#If the option to not run over the events again is made, load in the already created histograms here
else:

    #
    # Extra imports for dividing by region
    #
    from HNL.EventSelection.searchRegions import SearchRegionManager
    srm = {}
    srm[args.region] = SearchRegionManager(args.region)


    ################################
    #                              # 
    #       HELPER FUNCTIONS       #
    #                              # 
    ################################ 
    
    #
    # Create variable distributions
    #
    
    def createSingleVariableDistributions(tree, vname, hname, bins, condition, proc, year, include_systematics = 'nominal', split_corr = False, additional_weight = None, ignore_sideband = False, decorrelate_sr = None):
        out_dict = {}
    
        weight = 'weight'
        if additional_weight is not None:
            weight += '*'+additional_weight
        out_dict['nominal'] = Histogram(tree.getHistFromTree(vname, hname, bins, condition, weight=weight))
        if include_systematics != 'nominal':
            from HNL.Systematics.systematics import returnWeightShapes
            out_dict.update(returnWeightShapes(tree, vname, hname, bins, condition, year, proc, ['non-prompt'] if not ignore_sideband else None, additional_weight=additional_weight, decorrelate_sr = decorrelate_sr))
        return out_dict 
    
    def createVariableDistributions(categories_dict, var_dict, signal, background, data, sample_manager, year, additional_condition = None, include_systematics = 'nominal', sr = None, split_corr = False, for_datacards = False, ignore_sideband = False, custom_bins = None, decorrelate_sr = None):

        from HNL.Analysis.analysisTypes import getBinning
        bins = lambda c, v: getBinning(v, args.region, var_dict[v][1]) if custom_bins is None else custom_bins[c][v] 

        if additional_condition is None:
            additional_condition = ''
        else:
            additional_condition = '&&({0})'.format(additional_condition)
        
        #Add additional cuts
        if args.region == 'highMassSR':
            tmp_searchregion = srm[args.region].getGroupValues('F')
            searchregion_condition = '&&'.join(['searchregion != {0}'.format(x) for x in tmp_searchregion])
            inv_searchregion_condition = '||'.join(['searchregion == {0}'.format(x) for x in tmp_searchregion])
            category_condition = 'category!=27&&category!=28&&category!=29'
            inv_category_condition = 'category==27||category==28||category==29'
            final_condition = '((('+searchregion_condition+')||('+category_condition+'))||(('+inv_category_condition+')&&('+inv_category_condition+')&&(passedChargeConsistency&&abs(minMsssf-91)>15)))'
            additional_condition += '&&'+final_condition
 
        from HNL.Tools.outputTree import OutputTree
        def getTree(name, path):
            if not args.combineYears:
                return OutputTree(name, path+'/variables.root')
            elif args.region not in signal_regions:
                in_paths = [path+'/variables_{0}.root'.format(y) for y in args.year]
                return OutputTree(name, in_paths)
            else:
                return OutputTree(name, path+'/variables.root')
 
        from HNL.EventSelection.eventCategorization import isLightLeptonFinalState
        categories_to_use = categories_dict[0]
        category_conditions = categories_dict[1]
        print "Preparing the hist list"
        tmp_list_of_hist = {}
        for c in categories_to_use:
            tmp_list_of_hist[c] = {}
            for v in var_dict:
                tmp_list_of_hist[c][v] = {'signal':{}, 'bkgr':{}, 'data':{}}
    
        # Load in the signal histograms from the files
        if not args.plotBkgrOnly:
            print "Loading signal histograms"
            for isignal, s in enumerate(signal):
                progress(isignal, len(signal))
                sample_name = s.split('/')[-1]
                sample_mass = Sample.getSignalMass(sample_name)
                cleaned_sample_name = sample_name
                #if 'HNL-tau' in sample_name: cleaned_sample_name = 'HNL-tau-m{0}'.format(int(sample_mass))
                if '-tau' in sample_name: 
                    cleaned_sample_name = sample_name.split('-', 1)[0] + '-tau-'+sample_name.split('-', 2)[-1]
    
                split_syst_to_run = getSystToRun(year, sample_name, split_corr=True) if include_systematics in ['full'] else ['nominal']           
 
                additional_condition_to_use = additional_condition if not args.plotDirac else additional_condition+'&&isDiracType'
                for corr_syst in split_syst_to_run:
                    intree = getTree('events_{0}'.format(corr_syst), s)
                    for c, cc in zip(categories_to_use, category_conditions): 
                        if 'taulep' in sample_name and not isLightLeptonFinalState(c): continue
                        if 'tauhad' in sample_name and isLightLeptonFinalState(c): continue
                        for v in var_dict.keys():
                            if not for_datacards or Sample.getSignalDisplacedString(sample_name) == 'prompt':
                                coupling_squared = args.rescaleSignal if args.rescaleSignal is not None else signal_couplingsquared[args.flavor][sample_mass]
                                vsquared_translated = str(coupling_squared)
                                vsquared_translated = vsquared_translated.replace('e-', 'em')
                                new_name = cleaned_sample_name.split('-Vsq')[0]+'-Vsq'+vsquared_translated + '-' + Sample.getSignalDisplacedString(cleaned_sample_name)
                                additional_weight = str(coupling_squared/Sample.getSignalCouplingSquared(sample_name))
 
                                #tmp
                                #additional_weight += '*(isDiracType*1.2+!isDiracType*0.73)'
                                
                                if args.plotDirac: additional_weight += '*diracSF'
                                if corr_syst == 'nominal':
                                    tmp_list_of_hist[c][v]['signal'][new_name] = createSingleVariableDistributions(intree, v, str(c)+'-'+v+'-'+corr_syst+'-'+sample_name+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&!issideband)'+additional_condition_to_use, sample_name, year, include_systematics, split_corr = split_corr, additional_weight = additional_weight, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)
                                else:
                                    tmp_list_of_hist[c][v]['signal'][new_name][corr_syst] = createSingleVariableDistributions(intree, v, str(c)+'-'+v+'-'+corr_syst+'-'+sample_name+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&!issideband)'+additional_condition_to_use, sample_name, year, split_corr = split_corr, additional_weight = additional_weight, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)['nominal'] 
                            else:
                                additional_weight = 'diracSF' if args.plotDirac else None
                                for iv, vsquared in enumerate(np.ndarray(intree.getTreeVariable('displacement_ncouplings', 0), 'f', intree.getTreeVariable('displacement_vsquared', 0))):
                                    vsquared_translated = str(vsquared)
                                    vsquared_translated = vsquared_translated.replace('e-', 'em')
                                    new_name = cleaned_sample_name.split('-Vsq')[0]+'-Vsq'+vsquared_translated + '-' + Sample.getSignalDisplacedString(cleaned_sample_name)
                                    additional_weight_corrected = '(displacement_lumiweight[{0}]/lumiWeight)'.format(iv) if additional_weight is None else additional_weight+'*(displacement_lumiweight[{0}]/lumiWeight)'.format(iv)
                                    if corr_syst == 'nominal':
                                        tmp_list_of_hist[c][v]['signal'][new_name] = createSingleVariableDistributions(intree, v, str(c)+'-'+v+'-'+corr_syst+'-'+sample_name+'-'+str(sr)+'-'+str(year)+'-'+vsquared_translated, bins(c, v), '('+cc+'&&!issideband)'+additional_condition_to_use, sample_name, year, include_systematics, split_corr = split_corr, additional_weight = additional_weight_corrected, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)
                                    else:
                                        tmp_list_of_hist[c][v]['signal'][new_name][corr_syst] = createSingleVariableDistributions(intree, v, str(c)+'-'+v+'-'+corr_syst+'-'+sample_name+'-'+str(sr)+'-'+str(year)+'-'+vsquared_translated, bins(c, v), '('+cc+'&&!issideband)'+additional_condition_to_use, sample_name, year, split_corr = split_corr, additional_weight = additional_weight_corrected, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)['nominal'] 
    
            print '\n'
   
        if args.includeData is not None and not args.signalOnly:
        #if args.includeData is not None:
            print "Loading data"
            split_syst_to_run = getSystToRun(year, 'non-prompt', split_corr=True) if not ignore_sideband and include_systematics in ['full'] else ['nominal']           
            for isyst, corr_syst in enumerate(split_syst_to_run):
                progress(isyst, len(split_syst_to_run))
                intree = getTree('events_{0}'.format(corr_syst), data[0])
                for ic, (c, cc) in enumerate(zip(categories_to_use, category_conditions)):
                    for v in var_dict:
                        proc_to_use = 'non-prompt' if not ignore_sideband else 'Data'
                        if corr_syst == 'nominal':
                            tmp_list_of_hist[c][v]['data']['sideband'] = createSingleVariableDistributions(intree, v, str(c)+'-'+v+'-'+corr_syst+'-Data-sideband'+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&issideband)'+additional_condition, proc_to_use, year, include_systematics, split_corr=split_corr, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)
                            tmp_list_of_hist[c][v]['data']['signalregion'] = {'nominal' : Histogram(intree.getHistFromTree(v, str(c)+'-'+v+'-'+'-nominal-Data-signalregion'+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&!issideband)'+additional_condition))}
                        else:
                            tmp_list_of_hist[c][v]['data']['sideband'][corr_syst] = createSingleVariableDistributions(intree, v, str(c)+'-'+v+'-'+corr_syst+'-Data-sideband'+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&issideband)'+additional_condition, proc_to_use, year, split_corr=split_corr, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)['nominal']
    
        if not args.signalOnly:

            #
            # Tmp SF for ZZ and ZG
            #
            def getPromptWeight(name):
                if name == 'ZZ-H':
                    return '1.11'
                elif name == 'XG':
                    return '1.12'
                else:
                     return '1.'
            
            print "Loading background histograms"
            for ib, b in enumerate(background):
                for c, cc in zip(categories_to_use, category_conditions):
                    for iv, v in enumerate(var_dict.keys()): 
                        tmp_list_of_hist[c][v]['bkgr'][b] = {}
    
            for ib, b in enumerate(background):
                progress(ib, len(background))

                if not args.individualSamples:
                    if b in ['non-prompt', 'charge-misid']: continue
                    split_syst_to_run = getSystToRun(year, b, split_corr=True) if include_systematics in ['full'] else ['nominal']       
                    for corr_syst in split_syst_to_run:
                        intree = getTree('events_{0}'.format(corr_syst), getOutputName('bkgr', year, args.tag)+'/'+b)                 
                        for c, cc in zip(categories_to_use, category_conditions):
                            for iv, v in enumerate(var_dict.keys()): 
                                if corr_syst == 'nominal':
                                    tmp_list_of_hist[c][v]['bkgr'][b] = createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'p'+corr_syst+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&!isChargeFlipEvent&&isprompt&&!issideband)'+additional_condition, b, year, include_systematics, split_corr=split_corr, ignore_sideband=ignore_sideband, additional_weight = getPromptWeight(b), decorrelate_sr = decorrelate_sr)
                                    #tmp_list_of_hist[c][v]['bkgr'][b] = createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'p'+corr_syst+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&!isChargeFlipEvent&&isprompt&&!issideband)'+additional_condition, b, year, include_systematics, split_corr=split_corr, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)
                                else:
                                    tmp_list_of_hist[c][v]['bkgr'][b][corr_syst] = createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'p'+corr_syst+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&!isChargeFlipEvent&&isprompt&&!issideband)'+additional_condition, b, year, split_corr=split_corr, ignore_sideband=ignore_sideband, additional_weight = getPromptWeight(b), decorrelate_sr = decorrelate_sr)['nominal']
                                
                                #charge
                                if corr_syst == 'nominal': 
                                    tmp_hist = createSingleVariableDistributions(intree, v, 'tmp_'+b+'-chargemisid'+v+str(c)+'p'+corr_syst+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&isChargeFlipEvent&&isprompt&&!issideband)'+additional_condition, b, year, include_systematics, split_corr=split_corr, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)
                                else:
                                    tmp_hist = {corr_syst : createSingleVariableDistributions(intree, v, 'tmp_'+b+'-chargemisid'+v+str(c)+'p'+corr_syst+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&isChargeFlipEvent&&isprompt&&!issideband)'+additional_condition, b, year, split_corr=split_corr, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)['nominal']}
                                    
                                if corr_syst not in tmp_list_of_hist[c][v]['bkgr']['charge-misid'].keys():
                                    tmp_list_of_hist[c][v]['bkgr']['charge-misid'].update(tmp_hist)
                                else:
                                    for sk in tmp_hist.keys():
                                        tmp_list_of_hist[c][v]['bkgr']['charge-misid'][sk].add(tmp_hist[sk])
                                del(tmp_hist)
                                
                                if ignore_sideband:
                                    if corr_syst == 'nominal': 
                                        tmp_hist = createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'np'+corr_syst+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&!isprompt&&!issideband)'+additional_condition, 'non-prompt', year, include_systematics, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)
                                    else:
                                        tmp_hist = {corr_syst : createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'np'+corr_syst+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&!isprompt&&!issideband)'+additional_condition, b, year, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)['nominal']}
           
                                    if corr_syst not in tmp_list_of_hist[c][v]['bkgr']['non-prompt'].keys():
                                        tmp_list_of_hist[c][v]['bkgr']['non-prompt'].update(tmp_hist)
                                    else:
                                        for sk in tmp_hist.keys():
                                            tmp_list_of_hist[c][v]['bkgr']['non-prompt'][sk].add(tmp_hist[sk])
                                    del(tmp_hist)
                                else:
                                    #Load in the prompt sideband so we can remove it from our datadriven estimation
                                    if corr_syst == 'nominal': 
                                        tmp_list_of_hist[c][v]['data'][b] = createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'p'+corr_syst+'-'+str(sr)+'-'+str(year)+'-sideband', bins(c, v), '('+cc+'&&isprompt&&issideband)'+additional_condition, b, year, include_systematics, split_corr=split_corr, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)
                                    else:
                                        tmp_list_of_hist[c][v]['data'][b][corr_syst] = createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'p'+corr_syst+'-'+str(sr)+'-'+str(year)+'-sideband', bins(c, v), '('+cc+'&&isprompt&&issideband)'+additional_condition, b, year, split_corr=split_corr, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)['nominal']
                            
                else:
                    split_syst_to_run = getSystToRun(year, sample_name, split_corr=True) if include_systematics in ['full'] else ['nominal']
                    for corr_syst in split_syst_to_run:
                        intree = getTree('events_{0}'.format(corr_syst), getOutputName('bkgr', year, args.tag)+'/'+sample_manager.output_dict[b]+'/variables-'+b+'.root')                       
                        for c, cc in zip(categories_to_use, category_conditions):
                            for iv, v in enumerate(var_dict.keys()):
                                if corr_syst == 'nominal': 
                                    tmp_list_of_hist[c][v]['bkgr'][b] = createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'t'+corr_syst+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&isprompt&&!issideband)'+additional_condition, b, year, include_systematics, split_corr=split_corr, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)
                                else:
                                    tmp_list_of_hist[c][v]['bkgr'][b][corr_syst] = createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'t'+corr_syst+'-'+str(sr)+'-'+str(year), bins(c, v), '('+cc+'&&isprompt&&!issideband)'+additional_condition, b, year, split_corr=split_corr, ignore_sideband=ignore_sideband, decorrelate_sr = decorrelate_sr)['nominal']
   
            if not ignore_sideband:
                for c, cc in zip(categories_to_use, category_conditions):
                    for iv, v in enumerate(var_dict.keys()):
                        tmp_list_of_hist[c][v]['bkgr']['non-prompt'] = tmp_list_of_hist[c][v]['data']['sideband']
                       
                        #Remove prompt contribution
                        for b in background:  
                            if b in ['charge-misid', 'non-prompt']: continue
                            #if b == 'XG': continue
                            for k in tmp_list_of_hist[c][v]['bkgr']['non-prompt'].keys():
                                tmp_list_of_hist[c][v]['bkgr']['non-prompt'][k].getHist().Add(tmp_list_of_hist[c][v]['data'][b]['nominal'].getHist(), -1.) 
                        
                        for k in tmp_list_of_hist[c][v]['bkgr']['non-prompt'].keys():
                            tmp_list_of_hist[c][v]['bkgr']['non-prompt'][k].removeNegativeBins(error=1.0)

            if args.paperPlots is not None:
                backgrounds_to_merge = ['charge-misid', 'triboson', 'TT-T+X']
                for c, cc in zip(categories_to_use, category_conditions):
                    for iv, v in enumerate(var_dict.keys()):
                        if 'Other' not in tmp_list_of_hist[c][v]['bkgr'].keys():
                            raise RuntimeError("Trying to merge backgrounds for paper into a non-existing category")
                        for btm in backgrounds_to_merge:
                            for k in tmp_list_of_hist[c][v]['bkgr'][btm].keys():
                                tmp_list_of_hist[c][v]['bkgr']['Other'][k].getHist().Add(tmp_list_of_hist[c][v]['bkgr'][btm]['nominal'].getHist())
                            tmp_list_of_hist[c][v]['bkgr'].pop(btm)

 
        return tmp_list_of_hist
    
    def getMergedYears(signal_list, bkgr_list, data_list):
        # Translate tree if years need to be combined
        year_to_plot = '-'.join(sorted(args.year))
        if not (args.mergeYears and args.submitPlotting):
            signal_list[year_to_plot] = []
            bkgr_list[year_to_plot] = []
            data_list[year_to_plot] = []
   
 
        #Translate the input lists
        input_lists = {'signal' : {}, 'bkgr' : {}, 'data' : {}}
        for y in args.year:
            for signal in signal_list[y]:
                if signal.split('/')[-1] not in input_lists['signal'].keys():
                    input_lists['signal'][signal.split('/')[-1]] = {y:signal}
                else:
                    input_lists['signal'][signal.split('/')[-1]][y] = signal
            for bkgr in bkgr_list[y]:
                if bkgr.split('/')[-1] not in input_lists['bkgr'].keys():
                    input_lists['bkgr'][bkgr.split('/')[-1]] = {y:bkgr}
                else:
                    input_lists['bkgr'][bkgr.split('/')[-1]][y] = bkgr
            for data in data_list[y]:
                if data.split('/')[-1] not in input_lists['data'].keys():
                    input_lists['data'][data.split('/')[-1]] = {y:data}
                else:
                    input_lists['data'][data.split('/')[-1]][y] = data

        if args.mergeYears and args.submitPlotting: 
            from HNL.Analysis.mergeTrees import translateTree
            print 'Start translation'
            for year in args.year:
                print '\t', year
                for sob in ['signal', 'bkgr', 'data']:
                    print '\t\t', sob 
                    for sample_name in input_lists[sob]:
                        print '\t\t\t', sample_name
                        if len(input_lists[sob][sample_name].keys()) != len(args.year):
                            continue
                        else:
#                            translateTree(input_lists[sob][sample_name][year]+'/variables.root', input_lists[sob][sample_name][year]+'/tmp_translation/variables.root', sample_name, year, args.year, datadriven_processes = ['non-prompt'] if args.includeData == 'includeSideband' else None, ignore_reruns = args.systematics == 'nominal')
                            translateTree(input_lists[sob][sample_name][year]+'/variables.root', input_lists[sob][sample_name][year]+'/tmp_translation/variables.root', sample_name, year, ['2016post', '2016pre', '2017', '2018'], datadriven_processes = ['non-prompt'] if args.includeData == 'includeSideband' else None, ignore_reruns = args.systematics == 'nominal')
    
        #Hadd everything we need to
        if args.mergeYears and not args.submitPlotting:
            shall_we_merge = raw_input('Would you like to merge existing files? (y/n)\n')
        elif args.mergeYears and args.submitPlotting:
            shall_we_merge = 'n'

        for sob in ['signal', 'bkgr', 'data']:
            for sample_name in input_lists[sob]:
                if len(input_lists[sob][sample_name].keys()) != len(args.year):
                    continue
                else:
                    output_name = input_lists[sob][sample_name][args.year[0]].replace(args.era+'-'+args.year[0], args.era+'-'+year_to_plot)
                    if args.mergeYears and shall_we_merge == 'y':
                        makeDirIfNeeded(output_name+'/variables.root')
                        #os.system('hadd -f '+output_name + '/variables.root ' + ' '.join([input_lists[sob][sample_name][y]+'/tmp_translation/variables.root' for y in args.year]))
                        from HNL.Tools.mergeFiles import haddHNL

                        if args.systematics != 'nominal':
                            haddHNL(output_name + '/variables.root', ' '.join([input_lists[sob][sample_name][y]+'/tmp_translation/variables.root' for y in args.year]))
                           
                            for to_copy in input_lists[sob][sample_name].keys():
                                os.system('scp '+input_lists[sob][sample_name][to_copy]+'/tmp_translation/variables.root '+ output_name+'/variables_{0}.root'.format(to_copy))
                            for to_delete in [input_lists[sob][sample_name][x] for x in input_lists[sob][sample_name].keys()]:
                                os.system('rm -r '+to_delete+'/tmp_translation')
                        else:
                            haddHNL(output_name + '/variables.root', ' '.join([input_lists[sob][sample_name][y]+'/variables.root' for y in args.year]))
    

                    if sob == 'signal':
                        signal_list[year_to_plot].append(output_name)
                    elif sob == 'bkgr':
                        bkgr_list[year_to_plot].append(output_name)
                    elif sob == 'data':
                        data_list[year_to_plot].append(output_name)

        print 'End translation'
        return signal_list, bkgr_list, data_list
        

    def insertRebin(in_var, year, signal_list, bkgr_list, data_list, additional_condition, ignore_sideband, searchregion = None, for_datacards = False):
        from HNL.Analysis.analysisTypes import getBinning
        var_to_rebin = {}

        for v in in_var:
            if isinstance(in_var[v][1], str) and 'rebin' in in_var[v][1]:
                var_to_rebin[v] = [x for x in in_var[v]]
                var_to_rebin[v][1] = np.arange(-1.0, 1.001, 0.001)

        if len(var_to_rebin.keys()) > 0 and not args.signalOnly:
            list_of_probe_hist = createVariableDistributions(category_dict[args.categoriesToPlot], var_to_rebin, signal_list[year], background_collection[year], data_list[year], sample_manager, year, additional_condition = additional_condition, include_systematics = 'nominal', ignore_sideband = ignore_sideband, for_datacards = for_datacards)

        #actual rebinning
        binning = {}
        from HNL.TMVA.rebinning import getEwkinoBinning
        for c in category_dict[args.categoriesToPlot][0]:
            binning[c] = {}
            for v in in_var.keys():
                if v in var_to_rebin.keys():
                    if not args.signalOnly and (searchregion == ['F'] or searchregion == 'F' or (c == 'EEE-Mu' and 'massmu' in v)):
                        bkgrs = list_of_probe_hist[c][v]['bkgr'].keys()
                        tot_hist = list_of_probe_hist[c][v]['bkgr'][bkgrs[0]]['nominal'].clone('tot')
                        for b in bkgrs[1:]:
                            tot_hist.add(list_of_probe_hist[c][v]['bkgr'][b]['nominal'])
                        binning[c][v] = np.array(getEwkinoBinning(tot_hist, 2))
                        del tot_hist
                    else:
                        binning[c][v] = np.arange(-1.0, 1.1, 0.1)
                elif v == 'searchregion':
                    binning[c][v] = srm[args.region].getSearchRegionBinning(searchregion = searchregion, final_state = c)
                else:
                    binning[c][v] = np.array([x for x in getBinning(v, args.region, in_var[v][1])])
        #del list_of_probe_hist

        if args.paperPlots is not None:
            from HNL.Analysis.helpers import removeEmptyBins
            list_of_probe_hist = createVariableDistributions(category_dict[args.categoriesToPlot], in_var, signal_list[year], background_collection[year], data_list[year], sample_manager, year, additional_condition = additional_condition, include_systematics = 'nominal', ignore_sideband = ignore_sideband, for_datacards = for_datacards, custom_bins = binning)
            for c in category_dict[args.categoriesToPlot][0]:
                for v in in_var.keys():
                    if v == 'searchregion': continue
                    bkgrs = list_of_probe_hist[c][v]['bkgr'].keys()
                    tot_hist = list_of_probe_hist[c][v]['bkgr'][bkgrs[0]]['nominal'].clone('tot')
                    for b in bkgrs[1:]:
                        tot_hist.add(list_of_probe_hist[c][v]['bkgr'][b]['nominal'])


                    binning[c][v] = np.array(removeEmptyBins([tot_hist]))
                    


        return binning

    def translateSearchRegions():
        out_regions = set()
        for r in args.searchregion:
            if r in srm[args.region].getListOfSearchRegionGroups():
                out_regions.update(srm[args.region].getGroupValues(r))
            else:
                out_regions.update([r])
        return out_regions

    #############################################
    #                                           #
    #           Actual Plotting Code            #
    #                                           #
    #############################################

    from ROOT import gROOT
    gROOT.SetBatch(True)
    import glob
    from HNL.Analysis.analysisTypes import signal_couplingsquared
    from HNL.Tools.helpers import getHistFromTree

    ignore_sideband = args.includeData != 'includeSideband' or args.ignoreSideband 

    # Merge and collect histograms
    if args.bkgrOnly: args.plotBkgrOnly = True
    
    #Add entry for the search regions in the var dictionary
    from HNL.Weights.reweighter import var_weights
    if not args.genLevel:    var.update(var_weights)
    var['searchregion'] = (lambda c : c.searchregion, 'placeholder', ('Search region', 'Events'))
    #var = {
    #    'leadingFakeLeptonPt' : (lambda c : c.leadingFakeLeptonPt[0],       np.arange(0., 300., 15.),       ('p_{T} (leading fake lepton) [GeV]', 'Events')),
    #    'leadingFakeElectronPt' : (lambda c : c.leadingFakeElectronPt[0],       np.arange(0., 300., 15.),       ('p_{T} (leading fake electron) [GeV]', 'Events')),
    #    'leadingFakeMuonPt' : (lambda c : c.leadingFakeMuonPt[0],       np.arange(0., 300., 15.),       ('p_{T} (leading fake muon) [GeV]', 'Events')),
    #    'l1pt':      (lambda c : c.l_pt[0],       np.arange(0., 300., 15.),       ('p_{T} (l1) [GeV]', 'Events'))
    #}

    # Custom Var that you can create from existing var (i.e. 2D plots)
    # var['l3pt-met'] = (lambda c : [c.l3pt, c.met], (np.array([20., 25., 35., 50., 70., 100.]), np.array([0., 20., 35., 50., 100.])), ('p_{T}(l3) [GeV]', 'met'))

    signal_list = {}
    bkgr_list = {}
    background_collection = {}
    data_list = {}
    for year in args.year:
        print 'Processing ', year

        sample_manager = getSampleManager(year)

        if not args.plotBkgrOnly:
            signal_list[year] = [s for s in glob.glob(getOutputName('signal', year, args.tag)+'/*') if s.split('/')[-1] in sample_manager.sample_outputs]
            for i, s in enumerate(signal_list):
                if 'signalOrdering' in s:
                    signal_list[year].pop(i)
        else:
            signal_list[year] = []

        # Collect background file locations
        if not args.signalOnly:
            bkgr_list[year] = [getOutputName('bkgr', year, args.tag)+'/'+b for b in sample_manager.sample_outputs if os.path.isdir(getOutputName('bkgr', year, args.tag)+'/'+b)]
        else:
            bkgr_list[year] = []

        # data
        if args.includeData is not None and not args.signalOnly:
        #if args.includeData is not None:
            data_list[year] = glob.glob(getOutputName('data', year, args.tag)+'/Data')
        else:
            data_list[year] = []

        print 'check merge'
        # Merge files if necessary
        mixed_list = signal_list[year] + bkgr_list[year] + data_list[year]
        custom_list_to_use = customizeListToUse(year)
        full_path = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Analysis'))
        #merge(mixed_list, __file__, jobs[year], ('sample', 'subJob'), argParser, istest=args.isTest, additionalArgs= [('year', year)], man_changed_args = {'customList':custom_list_to_use}, full_path = full_path)

        if not args.individualSamples:
            background_collection[year] = []
            for x in sample_manager.sample_outputs:
                if 'HNL' in x: continue
                if 'Data' in x: continue
                if not os.path.isdir(getOutputName('bkgr', year, args.tag)+'/'+x): continue
                background_collection[year].append(x)
            
            background_collection[year] += ['non-prompt', 'charge-misid']
        else:
            background_collection[year] = [x for x in sample_manager.sample_names if not 'HNL' in x and not 'Data' in x]

        #background_collection = ['XG']

        #Clean list of hist
        tmp_signal_list = []
        for i_s, s in enumerate(signal_list[year]):
            sample_name = s.split('/')[-1]
            sample_mass = Sample.getSignalMass(sample_name)
            if args.sample is not None and args.sample != sample_name:      continue
            if sample_name not in sample_manager.sample_outputs:              continue    
            if args.masses is not None and sample_mass not in args.masses:  continue 
            if args.flavor != '' and '-'+args.flavor not in sample_name:  continue 
            if not args.plotDisplaced and Sample.getSignalDisplacedString(sample_name) == 'displaced': continue
            if args.plotDisplaced and Sample.getSignalDisplacedString(sample_name) != 'displaced': continue
            tmp_signal_list.append(s)

        signal_list[year] = [x for x in tmp_signal_list]

    years_to_plot = [y for y in args.year]
    if args.combineYears: 
        years_to_plot = ['-'.join(sorted(args.year))]
    
    if args.mergeYears or args.combineYears:
        signal_list, bkgr_list, data_list = getMergedYears(signal_list, bkgr_list, data_list)
        if args.mergeYears: exit(0)
        background_collection[years_to_plot[0]] = [x for x in background_collection[args.year[0]]]

    #
    #       Plot!
    #
    
    #
    # Necessary imports
    #
    from HNL.Plotting.plot import Plot
    from HNL.Plotting.plottingTools import extraTextFormat
    from HNL.Tools.helpers import makePathTimeStamped
    from HNL.TMVA.mvaVariables import getAllRelevantNames


    if args.makeDataCards:
    
        from HNL.Stat.combineTools import makeDataCard

        for year in years_to_plot:
            #
            # If we want to use shapes, first make shape histograms, then make datacards
            #
            for sr in srm[args.region].getListOfSearchRegionGroups():
                if args.searchregion is not None and sr not in args.searchregion: continue
                print 'Making datacards for region', sr
                var_for_datacard = {}
                var_for_datacard['searchregion'] = (lambda c : c.searchregion, 'placeholder', ('Search Region', 'Events'))
                if args.strategy == 'MVA':
                    set_of_mvas = set()
                    for sample_mass in args.masses:
                        for mva in getAllRelevantNames(sample_mass, args.flavor):
                        #for mva in getAllRelevantNames(sample_mass, args.flavor, args.region):
                            set_of_mvas.add(mva)
                    
                    list_of_mvas = [x for x in set_of_mvas]
                    for mva in list_of_mvas:
                        if mva not in var.keys(): continue
                        var_for_datacard[mva] = [x for x in var[mva]]

                sr_condition = '||'.join(['searchregion=={0}'.format(x) for x in srm[args.region].getGroupValues(sr)]) if sr != 'Combined' else None
                #Scout the binning
                binning = insertRebin(var_for_datacard, year, signal_list, background_collection, data_list, additional_condition = sr_condition, ignore_sideband = ignore_sideband, searchregion = sr, for_datacards = True) 
               
                hist_for_datacard = createVariableDistributions(category_dict[args.categoriesToPlot], var_for_datacard, signal_list[year], background_collection[year], data_list[year], sample_manager, year, sr_condition, include_systematics = args.systematics, sr=sr, split_corr=True, for_datacards=True, ignore_sideband = ignore_sideband, custom_bins = binning, decorrelate_sr = sr)
 
                for ac in category_dict[args.categoriesToPlot][0]:
                    print 'Filling', ac
                    for v in var_for_datacard.keys():
                        for sample_name in hist_for_datacard[ac][v]['signal'].keys():
                            sample_mass = Sample.getSignalMass(sample_name)
                            if sample_mass not in args.masses: continue
                            if Sample.getSignalDisplacedString(sample_name) == 'displaced':
                                coupling_squared = Sample.getSignalCouplingSquared(sample_name)
                            else:
                                coupling_squared = args.rescaleSignal if args.rescaleSignal is not None else signal_couplingsquared[args.flavor][sample_mass]
                            
                            bin_name = sr+'-'+ac+'-'+v
                            new_signal_name = sample_name.split('-Vsq')[0]+'-Vsq'+('{:.1e}'.format(coupling_squared).replace('-', 'm'))+'-'+Sample.getSignalDisplacedString(sample_name) 
                            out_path = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'shapes', '-'.join([args.selection, args.region] if args.tag is None else [args.selection, args.region, args.tag]), args.era+str(year), args.flavor, new_signal_name, 'Dirac' if args.plotDirac else 'Majorana', bin_name+'.shapes.root')
                            makeDirIfNeeded(out_path)

                            # Save shapes
                            hist_for_datacard[ac][v]['signal'][sample_name]['nominal'].replaceZeroBins()
                            hist_for_datacard[ac][v]['signal'][sample_name]['nominal'].write(out_path, write_name=new_signal_name, subdirs = [bin_name.rsplit('-', 1)[0]])
                            for syst in hist_for_datacard[ac][v]['signal'][sample_name].keys():
                                if syst == 'nominal': continue
                                hist_for_datacard[ac][v]['signal'][sample_name][syst].replaceZeroBins()
                                hist_for_datacard[ac][v]['signal'][sample_name][syst].write(out_path, write_name=new_signal_name, subdirs = [bin_name.rsplit('-', 1)[0]+syst], append=True)
                            bkgr_names = []
                            for ib, b in enumerate(hist_for_datacard[ac][v]['bkgr'].keys()):
                                if hist_for_datacard[ac][v]['bkgr'][b]['nominal'].hist.GetSumOfWeights() > 0:
                                    hist_for_datacard[ac][v]['bkgr'][b]['nominal'].replaceZeroBins()
                                    hist_for_datacard[ac][v]['bkgr'][b]['nominal'].write(out_path, write_name=b, subdirs = [bin_name.rsplit('-', 1)[0]], append=True)
                                    for syst in hist_for_datacard[ac][v]['bkgr'][b].keys():
                                        if syst == 'nominal': continue
                                        hist_for_datacard[ac][v]['bkgr'][b][syst].replaceZeroBins()
                                        hist_for_datacard[ac][v]['bkgr'][b][syst].write(out_path, write_name=b, subdirs = [bin_name.rsplit('-', 1)[0]+syst], append=True)
                                    bkgr_names.append(b)
                            
                            data_hist_tmp = hist_for_datacard[ac][v]['data']['signalregion']['nominal'].clone('Ditau')
                            data_hist_tmp.replaceZeroBins()
                            data_hist_tmp.write(out_path, write_name='data_obs', append=True, subdirs = [bin_name.rsplit('-', 1)[0]])
                        
                            makeDataCard(bin_name, args.flavor, args.era, year, 0, new_signal_name, bkgr_names, args.selection, args.region, ac, shapes=True, nonprompt_from_sideband = args.includeData == 'includeSideband', majorana_str = 'Majorana' if not args.plotDirac else 'Dirac', shapes_path=out_path, tag = args.tag)
   
    if args.makePlots:
        list_of_hist = {}
        #list_of_hist_forbar = {}
        
        var_to_use = {}
        if args.variables is None:
            var_to_use = var
        else:
            for v in var:
                if v in args.variables:
                    var_to_use[v] = var[v]

        additional_condition = args.additionalCondition
        if args.searchregion is not None:
            searchregion_condition = '||'.join(['searchregion == {0}'.format(x) for x in translateSearchRegions()])
            if additional_condition is None:
                additional_condition = searchregion_condition
            else:
                additional_condition += '&&('+searchregion_condition+')'
        print "Scouting binning"
 
#    from HNL.Analysis.outputConversion import writeYieldTable 
#    writeYieldTable(list_of_hist, 'Other', 'searchregion', os.path.join(os.getcwd(), 'data', 'testArea' if args.isTest else '', 'Results', 'runAnalysis', args.analysis+'-'+args.tag if args.tag is not None else args.analysis, '-'.join([args.strategy, args.selection, args.region, cleanName(args.additionalCondition) if args.additionalCondition is not None else ''])), split_bkgr = True)

        print years_to_plot
        for year in years_to_plot:
            binning = insertRebin(var_to_use, year, signal_list, background_collection, data_list, additional_condition = additional_condition, ignore_sideband = ignore_sideband, searchregion = args.searchregion)
            print "Creating list of histograms"
            if not args.cutFlowOnly:
                list_of_hist[year] = createVariableDistributions(category_dict[args.categoriesToPlot], var_to_use, signal_list[year], background_collection[year], data_list[year], sample_manager, year, additional_condition = additional_condition, include_systematics = args.systematics if not args.ignoreSystematics else 'nominal', ignore_sideband = ignore_sideband, custom_bins = binning)

            def selectNMostContributingHist(hist_dict, n, syst = 'nominal'):
                yield_dict = {x : hist_dict[x][syst].getHist().GetSumOfWeights() for x in hist_dict.keys()}
                no_other = False
                if n > len(yield_dict.keys()): 
                    n = len(yield_dict.keys())
                    no_other = True
                sorted_yields = sorted(yield_dict.iteritems(), key = lambda x : x[1], reverse=True)
                hist_to_return = []
                names_to_return = []
                for (name, y) in sorted_yields[:n+1]:
                    hist_to_return.append(hist_dict[name][syst])
                    names_to_return.append(name)
                
                if not no_other:
                    other_hist = hist_dict[sorted_yields[n+1][0]][syst].clone('other_hist')
                    for (name, y) in sorted_yields[n+2:]:
                        other_hist.add(hist_dict[name][syst])

                    hist_to_return.append(other_hist)
                    names_to_return.append('Other')
                return hist_to_return, names_to_return

            #
            # Set output directory, taking into account the different options
            #
            from HNL.Tools.outputTree import cleanName
            output_dir = os.path.join(os.getcwd(), 'data', 'testArea' if args.isTest else '', 'Results', 'runAnalysis', args.analysis+'-'+args.tag if args.tag is not None else args.analysis, '-'.join([args.strategy, args.selection, args.region, cleanName(args.additionalCondition) if args.additionalCondition is not None else '']), args.era+str(year))

            if args.signalOnly:
                signal_or_background_str = 'signalOnly'
            elif args.plotBkgrOnly:
                signal_or_background_str = 'bkgrOnly'
            else:
                signal_or_background_str = 'signalAndBackground'
            
            if not args.bkgrOnly:
                if not args.plotDirac: signal_or_background_str += '-Majorana'
                else:                  signal_or_background_str += '-Dirac'
            output_dir = os.path.join(output_dir, signal_or_background_str)    

            if args.flavor:         output_dir = os.path.join(output_dir, args.flavor+'_coupling')
            else:                   output_dir = os.path.join(output_dir, 'all_coupling')

            if args.masses is not None:         
                if len(args.masses) <= 3:
                    output_dir = os.path.join(output_dir, 'customMasses', '-'.join([str(m) for m  in args.masses]))
                else:
                    output_dir = os.path.join(output_dir, 'customMasses', str(min(args.masses))+'to'+ str(max(args.masses)))
            else:         output_dir = os.path.join(output_dir, 'allMasses')
            output_dir += '/norm-'+str(args.normalizeSignal)

            if args.paperPlots is not None: 
                if args.paperPlots == 'default':
                    output_dir += "/forPaper"
                if args.paperPlots == 'raw':
                    output_dir += "/forPaperRaw"
            
            output_dir_unstamped = output_dir
            output_dir = makePathTimeStamped(output_dir)

            #
            # Create variable plots for each category
            #
            print "Creating variable plots"

            if args.makePlots and not args.cutFlowOnly:
                from HNL.EventSelection.eventCategorization import CATEGORY_NAMES
                # for c in list_of_hist.keys():
                for c in category_dict[args.categoriesToPlot][0]:
                    if args.categoriesToPlot == 'original':
                        c_name = CATEGORY_NAMES[float(c)]
                    elif args.categoriesToPlot == 'analysis':
                        from HNL.EventSelection.eventCategorization import ANALYSIS_CATEGORIES_TEX
                        c_name = ANALYSIS_CATEGORIES_TEX[c] 
                    elif args.categoriesToPlot == 'splitanalysis':
                        from HNL.EventSelection.eventCategorization import ANALYSIS_SPLITOSSF_CATEGORIES_TEX
                        c_name = ANALYSIS_SPLITOSSF_CATEGORIES_TEX[c] 
                    elif args.categoriesToPlot == 'leadingflavor':
                        from HNL.EventSelection.eventCategorization import LEADING_FLAVOR_CATEGORIES_TEX
                        c_name = LEADING_FLAVOR_CATEGORIES_TEX[c] 
                    elif args.categoriesToPlot == 'sign':
                        from HNL.EventSelection.eventCategorization import SIGN_CATEGORIES_TEX
                        c_name = SIGN_CATEGORIES_TEX[c] 
                    elif args.categoriesToPlot == 'trigger':
                        from HNL.EventSelection.eventCategorization import TRIGGER_CATEGORIES_TEX
                        c_name = TRIGGER_CATEGORIES_TEX[c] 
                    else:
                        from HNL.EventSelection.eventCategorization import SUPER_CATEGORIES_TEX
                        c_name = SUPER_CATEGORIES_TEX[c] 
       
                    extra_text = [] 
                    if args.region in signal_regions: 
                        #extra_text.append(extraTextFormat('#bf{'+c_name+'}', xpos = 0.2, ypos = 0.74, textsize = None, align = 12))  #Text to display event type in plot
                        extra_text.append(extraTextFormat(c_name, xpos = 0.2, ypos = 0.78, textsize = None, align = 12))  #Text to display event type in plot
                    else: 
                        extra_text.append(extraTextFormat("", xpos = 0.2, ypos = 0.78, textsize = None, align = 12))  #Text to display event type in plot
                    if args.flavor: 
                        from decimal import Decimal
                        et_flavor = args.flavor if args.flavor == 'e' else '#'+args.flavor
                        default_coupling = args.rescaleSignal if args.rescaleSignal is not None else signal_couplingsquared[args.flavor][args.masses[0]]
                        extra_text.append(extraTextFormat('|V_{'+et_flavor+'N}|^{2} = '+'%.0E' % Decimal(str(default_coupling)), textsize = 0.8))
                    #if args.searchregion is not None:
                    #    from HNL.EventSelection.searchRegions import searchregion_tex
                    #    extra_text.append(extraTextFormat('SR {0}'.format(searchregion_tex[args.searchregion]), textsize=0.65))       
                    extra_text.append(extraTextFormat('Prefit', textsize = 0.8))
 
                    # Plots that display chosen for chosen signal masses and backgrounds the distributions for the different variables
                    # S and B in same canvas for each variable
                    for v in var_to_use.keys():
                        syst_hist = []
                        bkgr_legendnames = []
                        # Make list of background histograms for the plot object (or None if no background)
                        if args.signalOnly or not list_of_hist[year][c][v]['bkgr'].values(): 
                            bkgr_hist = None
                            syst_hist = None
                            syst_hist_up = None
                            syst_hist_down = None
                        else:
                            bkgr_hist = []
                            syst_hist = []
                            syst_hist_up = []
                            syst_hist_down = []
                            if args.individualSamples:
                                bkgr_hist, bkgr_legendnames = selectNMostContributingHist(list_of_hist[year][c][v]['bkgr'], 7)
                            else:
                                for bk in list_of_hist[year][c][v]['bkgr'].keys():
                                    bkgr_hist.append(list_of_hist[year][c][v]['bkgr'][bk]['nominal'])
                                    bkgr_legendnames.append(bk)
                                    if args.systematics == 'full' and not args.ignoreSystematics:
                                        if 'total_syst' not in list_of_hist[year][c][v]['bkgr'][bk].keys():
                                            from HNL.Systematics.systematics import makeSystErrorHist
                                            list_of_hist[year][c][v]['bkgr'][bk]['total_syst'] = makeSystErrorHist(list_of_hist[year][c][v]['bkgr'][bk], bk, c, year, 'non-prompt' if args.includeData == 'includeSideband' else None)
                                        tmp_hist_up, tmp_hist_down = makeSystErrorHist(list_of_hist[year][c][v]['bkgr'][bk], bk, c, year, 'non-prompt' if args.includeData == 'includeSideband' else None, split_output=True)
                                        syst_hist.append(list_of_hist[year][c][v]['bkgr'][bk]['total_syst'])
                                        syst_hist_up.append(tmp_hist_up.clone('up'))
                                        syst_hist_down.append(tmp_hist_down.clone('down'))

                        if args.systematics != 'full' or args.ignoreSystematics:
                            syst_hist = None
                            syst_hist_up = None
                            syst_hist_down = None
        
                        # Make list of signal histograms for the plot object
                        signal_legendnames = []
                        if args.plotBkgrOnly or not list_of_hist[year][c][v]['signal'].values(): 
                            signal_hist = None
                        else:
                            signal_hist = []
                            signal_coupling = []
                            signal_masses = []
                            for sk in sorted(list_of_hist[year][c][v]['signal'].keys()):
                                signal_hist.append(list_of_hist[year][c][v]['signal'][sk]['nominal'])
                                # if 'filtered' in sk:
                                #     signal_legendnames.append('HNL m_{N} = 30 GeV w Pythia filter')
                                # else:
                                # signal_legendnames.append('HNL '+ sk.split('-')[1] +' m_{N} = '+sk.split('-m')[-1]+ ' GeV')
                                if not 'displaced' in sk:
                                    signal_legendnames.append('HNL '+str(int(Sample.getSignalMass(sk)))+ '#scale[0.5]{ }GeV')
                                else:
                                    signal_legendnames.append('displaced HNL '+str(int(Sample.getSignalMass(sk)))+ '#scale[0.5]{ }GeV')
                                signal_coupling.append(Sample.getSignalCouplingSquared(sk))
                                signal_masses.append(Sample.getSignalMass(sk))
                                    
        
                        if args.includeData is not None and not args.signalOnly and not 'Weight' in v:
                            observed_hist = list_of_hist[year][c][v]['data']['signalregion']['nominal']
                            #tmp blinding
                            if not args.unblind and args.region in signal_regions: observed_hist = None
                        else:
                            observed_hist = None
        
                        from HNL.Plotting.plottingDicts import sample_tex_names
                        #Clean bkgr names
                        if not args.individualSamples:
                            bkgr_legendnames = [sample_tex_names[x] if x in sample_tex_names.keys() else x for x in bkgr_legendnames]
        
        
                        if not args.signalOnly and not args.plotBkgrOnly:
                            legend_names = signal_legendnames+bkgr_legendnames
                        elif args.signalOnly:
                            legend_names = signal_legendnames
                        else:
                            legend_names = bkgr_legendnames
                
                        #Create specialized signal region plots if this is the correct variable
                        if v == 'searchregion':

                            #First Hepdata json
                            from HNL.EventSelection.searchRegions import writeHEPjson
                            if not args.ignoreSystematics and not args.bkgrOnly: writeHEPjson(signal_hist, bkgr_hist, [None, None], [syst_hist_up, syst_hist_down], os.path.join(output_dir_unstamped, 'Yields/SearchRegions', c), args.region, sorted(list_of_hist[year][c][v]['signal'].keys()), bkgr_legendnames, observed_hist = observed_hist, combine_bkgr=True, signal_mass = signal_masses)

                            #then yield file
                            from HNL.Tools.helpers import makeDirIfNeeded
                            makeDirIfNeeded(os.path.join(output_dir, 'Yields/SearchRegions', c, 'yields.txt'))
                            out_file = open(os.path.join(output_dir, 'Yields/SearchRegions', c, 'yields.txt'), 'w')
                            number_of_processes = 0
                            if observed_hist is not None:
                                number_of_processes += 1
                            if bkgr_hist is not None:
                                number_of_processes += len(bkgr_hist)
                            if signal_hist is not None:
                                number_of_processes += len(signal_hist)
        
                            out_file.write('\\begin{tabular}{l'+'|'.join(['c' for p in range(number_of_processes)])+'} \\\\ \n')
                            out_file.write('\\hline \\hline \n')
                            process_line = 'Year\t'
                            yield_line = '{0}\t'.format(year)
                            if observed_hist is not None:
                                process_line += ' & Observed \t'
                                yield_line += ' & %s \t'%float('%.1f' % observed_hist.getHist().GetSumOfWeights())
                            if signal_hist is not None:
                                for isig, sig in enumerate(signal_hist):
                                    process_line += ' & '+signal_legendnames[isig]+'\t'
                                    yield_line +=  ' & %s \t'%float('%.1f' % sig.getHist().GetSumOfWeights())
                            if bkgr_hist is not None:
                                tot_bkgr = 0.
                                for ib, b in enumerate(bkgr_hist):
                                    tot_bkgr += b.getHist().GetSumOfWeights()
                                    process_line += ' & '+bkgr_legendnames[ib]+'\t'
                                    yield_line += ' & %s \t'%float('%.1f' % b.getHist().GetSumOfWeights())
                                process_line += ' & Total Predicted\t'
                                yield_line += ' & %s \t'%float('%.1f' % tot_bkgr)
                                
        
                            process_line += '\n'
                            yield_line += '\n'
                            out_file.write(process_line)
                            out_file.write(yield_line)
                            out_file.write('\\end{tabular}')
                            out_file.close()
                            #then plots
                            if args.region in signal_regions:
                                from HNL.EventSelection.searchRegions import plotLowMassRegions, plotHighMassRegions, plotLowMassRegionsLoose
                                # else:
                                #     signal_names = [s + ' V^{2}=' + str(signal_couplingsquared[s.split('-')[1]][int(s.split('-m')[-1])])  for s in signal_names]
                                  
                                if args.region == 'lowMassSR':
                                    plotLowMassRegions(signal_hist, bkgr_hist, syst_hist, legend_names, 
                                        out_path = os.path.join(output_dir, 'Yields', 'SearchRegions', c, '-'.join(args.searchregion) if args.searchregion is not None else ''), extra_text = [[y for y in x] for x in extra_text], year = year, era = args.era, observed_hist = observed_hist, for_paper = args.paperPlots)
                                if args.region == 'lowMassSRloose':
                                    plotLowMassRegionsLoose(signal_hist, bkgr_hist, syst_hist, legend_names, 
                                        out_path = os.path.join(output_dir, 'Yields', 'SearchRegions', c, '-'.join(args.searchregion) if args.searchregion is not None else ''), extra_text = [[y for y in x] for x in extra_text], year = year, era = args.era, observed_hist = observed_hist, for_paper = args.paperPlots)
                                if args.region == 'highMassSR':
                                    plotHighMassRegions(signal_hist, bkgr_hist, syst_hist, legend_names, 
                                        out_path = os.path.join(output_dir, 'Yields', 'SearchRegions', c, '-'.join(args.searchregion) if args.searchregion is not None else ''), extra_text = [[y for y in x] for x in extra_text], year = year, era = args.era, observed_hist = observed_hist, final_state = c, for_paper = args.paperPlots)
        
        
                        # Create plot object (if signal and background are displayed, also show the ratio)
                        #draw_ratio = 'errorsOnly' if args.signalOnly or args.plotBkgrOnly else True
                        draw_ratio = None if args.signalOnly or args.plotBkgrOnly else True
                        if args.includeData is not None: draw_ratio = True
                        if not args.individualSamples:
                            #p = Plot(signal_hist, legend_names, c+'-'+v, bkgr_hist = bkgr_hist, observed_hist = observed_hist, y_log = True, extra_text = extra_text, draw_ratio = draw_ratio, year = year, era=args.era,
                            p = Plot(signal_hist, legend_names, c+'-'+v, bkgr_hist = bkgr_hist, observed_hist = observed_hist, syst_hist = syst_hist if args.systematics == 'full' and not args.ignoreSystematics else None, y_log = True, extra_text = [[y for y in x] for x in extra_text], draw_ratio = draw_ratio, year = year, era=args.era,
                            #p = Plot(signal_hist, legend_names, c+'-'+v, bkgr_hist = bkgr_hist, observed_hist = observed_hist, syst_hist = syst_hist if args.systematics == 'full' and not args.ignoreSystematics else None, y_log = True, extra_text = [x for x in extra_text], draw_ratio = draw_ratio, year = year, era=args.era, equalize_bins=True,
                            #p = Plot(signal_hist, legend_names, c+'-'+v, bkgr_hist = bkgr_hist, observed_hist = observed_hist, syst_hist = syst_hist if args.systematics == 'full' and not args.ignoreSystematics else None, y_log = False, extra_text = [x for x in extra_text], draw_ratio = draw_ratio, year = year, era=args.era,
                                    color_palette = 'HNL', color_palette_bkgr = 'HNLfromTau' if not args.analysis == 'tZq' else 'tZq', x_name = var[v][2][0], y_name = var[v][2][1], for_paper = args.paperPlots)
                        else:
                            p = Plot(signal_hist, legend_names, c+'-'+v, bkgr_hist = bkgr_hist, observed_hist = observed_hist, y_log = True, extra_text = [[y for y in x] for x in extra_text], draw_ratio = draw_ratio, year = year, era=args.era,
                                    color_palette = 'Didar', color_palette_bkgr = 'Didar', x_name = var[v][2][0], y_name = var[v][2][1], for_paper = args.paperPlots)
        
                        # Draw
                        #p.drawHist(output_dir = os.path.join(output_dir, 'Variables' if v != 'searchregion' else 'Yields/SearchRegions', c), normalize_signal = True, draw_option='EHist', min_cutoff = 1)
                        if '-' in v:
                            p.draw2D(output_dir = os.path.join(output_dir+'/2D', 'Variables' if v != 'searchregion' else 'Yields/SearchRegions', c))
                        else:
                            p.drawHist(output_dir = os.path.join(output_dir, 'Variables' if v != 'searchregion' else 'Yields/SearchRegions', c, '-'.join(args.searchregion) if args.searchregion is not None else ''), normalize_signal = args.normalizeSignal, draw_option='EHist', min_cutoff = 1)
                        # p.drawHist(output_dir = os.path.join(output_dir, c), normalize_signal = False, draw_option='EHist', min_cutoff = 1)
        

                        


        signal_names = [s.split('/')[-1] for s in signal_list[args.year[0]]]
#        #
#        # Bar charts
#        #
#
#        from HNL.EventSelection.eventCategorization import CATEGORY_TEX_NAMES
#        from ROOT import TH1D
#        grouped_categories = cat.SUPER_CATEGORIES
#
#        for supercat in grouped_categories.keys():
#            if nl != 3 and supercat != 'Other': continue
#            #
#            # Bkgr
#            #
#            if not args.signalOnly:
#                hist_to_plot = []
#                if args.individualSamples:
#                    bkgr_hist_to_draw, bkgr_to_draw = selectNMostContributingHist(list_of_hist[supercat]['searchregion']['bkgr'], 7)
#                else:
#                    bkgr_to_draw = [b for b in background_collection]
#                for i_sample, sample_name in enumerate(bkgr_to_draw):
#                    hist_to_plot.append(TH1D(sample_name+supercat, sample_name+supercat, len(grouped_categories[supercat]), 0, len(grouped_categories[supercat])))
#                    for i, c in enumerate(grouped_categories[supercat]):
#                        if args.individualSamples and sample_name == 'Other':
#                            bkgr_hist = selectNMostContributingHist(list_of_hist_forbar[year][c]['searchregion']['bkgr'], 7)[0][-1]
#                            hist_to_plot[i_sample].SetBinContent(i+1, bkgr_hist.getHist().GetSumOfWeights()) 
#                        else:
#                            hist_to_plot[i_sample].SetBinContent(i+1, list_of_hist_forbar[year][c]['searchregion']['bkgr'][sample_name]['nominal'].getHist().GetSumOfWeights()) 
#
#                if args.includeData == 'signalregion':
#                    observed_hist = TH1D('data'+supercat, 'data'+supercat, len(grouped_categories[supercat]), 0, len(grouped_categories[supercat]))
#                    for i, c in enumerate(grouped_categories[supercat]):
#                        observed_hist.SetBinContent(i+1, list_of_hist_forbar[year][c]['searchregion']['data']['signalregion']['nominal'].getHist().GetSumOfWeights()) 
#                else:
#                    observed_hist = None
#
#                x_names = [CATEGORY_TEX_NAMES[n] for n in grouped_categories[supercat]]
#                #p = Plot(hist_to_plot, bkgr_to_draw, name = 'Events-bar-bkgr-'+supercat, observed_hist = observed_hist, x_name = x_names, y_name = 'Events', y_log='SingleTau' in supercat, color_palette = 'Didar')            
#                p = Plot(hist_to_plot, bkgr_to_draw, name = 'Events-bar-bkgr-'+supercat, observed_hist = observed_hist, x_name = x_names, y_name = 'Events', y_log='SingleTau' in supercat)            
#
#                p.drawBarChart(output_dir = os.path.join(output_dir, 'Yields', 'BarCharts'))
            
            #
            # Signal
            #   
        #    if not args.plotBkgrOnly:
        #        hist_to_plot = []
        #        hist_names = []
        #        for sn, sample_name in enumerate(sorted(signal_names, key=lambda k: int(k.split('-m')[-1]))):
        #            hist_to_plot.append(TH1D(sample_name, sample_name, len(grouped_categories[supercat]), 0, len(grouped_categories[supercat])))
        #            hist_names.append(sample_name)
        #            for i, c in enumerate(grouped_categories[supercat]):
        #                hist_to_plot[sn].SetBinContent(i+1, list_of_hist_forbar[year][c]['searchregion']['signal'][sample_name]['nominal'].getHist().GetSumOfWeights()) 
        #        x_names = [CATEGORY_TEX_NAMES[n] for n in grouped_categories[supercat]]
        #        p = Plot(hist_to_plot, hist_names, name = 'Events-bar-signal-'+supercat+'-'+args.flavor, x_name = x_names, y_name = 'Events', y_log=True)
        #        p.drawBarChart(output_dir = os.path.join(output_dir, 'Yields', 'BarCharts'), parallel_bins=True)
        
        #print "making Pie Charts"
        #example_sample = background_collection[0]
        #for i, c in enumerate(sorted(category_dict[args.categoriesToPlot][0])):

        #    n_filled_hist = len([v for v in background_collection if list_of_hist[year][c]['searchregion']['bkgr'][v]['nominal'].getHist().GetSumOfWeights() > 0])    #Remove hist with 0 events, they will otherwise crash the plotting code
        #    if n_filled_hist == 0: continue
        #    hist_to_plot_pie = TH1D(str(c)+'_pie', str(c), n_filled_hist, 0, n_filled_hist)
        #    sample_names = []
        #    j = 1
        #    for s in background_collection:
        #        fill_val = list_of_hist[year][c]['searchregion']['bkgr'][s]['nominal'].getHist().GetSumOfWeights()
        #        if fill_val > 0:
        #            hist_to_plot_pie.SetBinContent(j, fill_val)
        #            sample_names.append(s)
        #            j += 1

        #    try:
        #        extra_text = [extraTextFormat(str(c), ypos = 0.83)] if c is not None else None
        #    except:
        #        extra_text = [extraTextFormat('other', ypos = 0.83)] if c is not None else None
        #    x_names = CATEGORY_TEX_NAMES.values()
        #    x_names.append('total')
        #    p = Plot(hist_to_plot_pie, sample_names, name = 'Events_'+str(c), x_name = CATEGORY_TEX_NAMES, y_name = 'Events', extra_text = extra_text)
        #    p.drawPieChart(output_dir = os.path.join(output_dir, 'Yields', 'PieCharts'), draw_percent=True)

        print "plotting cutflow"
        for year in years_to_plot:

            in_files = {'signal' : {}, 'bkgr' : {}}
            for sample_name in background_collection[year]+signal_names: 
            #for sample_name in signal_names: 
                if not args.individualSamples:
                    in_path = lambda y : getOutputName('signal' if 'HNL' in sample_name else 'bkgr', y, args.tag)+'/'+sample_name+'/variables.root'
                    #if args.flavor != 'tau' or not 'HNL' in sample_name:
                    #    in_path = lambda y : getOutputName('signal' if 'HNL' in sample_name else 'bkgr', y, args.tag)+'/'+sample_name+'/variables.root'
                    #else:
                    #    extra_name = sample_name.replace('tau', 'tauhad')
                    #    in_path = lambda y : getOutputName('signal' if 'HNL' in sample_name else 'bkgr', y, args.tag)+'/'+sample_name+'/variables-{0}.root'.format(extra_name)
                else:
                    in_path = lambda y : getOutputName('bkgr', y, args.tag)+'/'+sample_manager.output_dict[sample_name]+'/variables-'+sample_name+'.root'
    
                from HNL.Tools.helpers import isValidRootFile
                if not isValidRootFile(in_path(year)): continue
                in_files['signal' if 'HNL' in sample_name else 'bkgr'][sample_name] = in_path(year)
            
            from HNL.HEPData.createCutFlows import createCutFlowJSONs
            out_cat = {}
            for c in category_dict[args.categoriesToPlot][0]:
                out_cat[c] = [int(x) for x in category_dict[args.categoriesToPlot][2][c]]
            #Write cutflow to json
            out_json_cutflow = createCutFlowJSONs(in_files['signal'], in_files['bkgr'], None, os.path.join(output_dir_unstamped, 'CutFlows'), out_cat, None, starting_dir='nominalnominal')
            
