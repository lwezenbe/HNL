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
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'tZq', 'TTT', ])
submission_parser.add_argument('--strategy',   action='store', default='MVA',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA'])
submission_parser.add_argument('--analysis',   action='store', default='HNL',  help='Select the strategy to use to separate signal from background', choices=['HNL', 'AN2017014', 'ewkino', 'tZq'])
submission_parser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?')
submission_parser.add_argument('--includeData',   action='store', default=None, help='Also run over data', choices=['includeSideband', 'signalregion'])
submission_parser.add_argument('--logLevel',  action='store', default='INFO',  help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])
submission_parser.add_argument('--skimLevel',  action='store', default='Reco',  choices=['noskim', 'Reco', 'RecoGeneral', 'auto'])
submission_parser.add_argument('--customList',  action='store',      default=None,               help='Name of a custom sample list. Otherwise it will use the appropriate noskim file.')
submission_parser.add_argument('--systematics',  action='store',      default='nominal',               help='Choose level of systematics.', choices = ['nominal', 'limited', 'full'])
submission_parser.add_argument('--tag',  action='store',      default=None,               help='Tag with additional information for the output, e.g. TauFakes, sidebandInMC')

argParser.add_argument('--makePlots',   action='store_true',    default=False,  help='Use existing root files to make the plots')
argParser.add_argument('--showCuts',   action='store_true',     default=False,  help='Show what the pt cuts were for the category in the plots')
argParser.add_argument('--individualSamples',   action='store_true', default=False,  help='plot each input sample separately')
argParser.add_argument('--makeDataCards', action = 'store_true',  help='Make data cards of the data you have')
argParser.add_argument('--rescaleSignal', type = float,  action='store', default=None,  help='Enter desired signal coupling squared')
argParser.add_argument('--masses', type=float, nargs='*',  help='Only run or plot signal samples with mass given in this list')
argParser.add_argument('--flavor', action='store', default='',  help='Which coupling should be active?' , choices=['tau', 'e', 'mu', '2l', ''])
argParser.add_argument('--signalOnly',   action='store_true',   default=False,  help='Run or plot a only the signal')
argParser.add_argument('--bkgrOnly',   action='store_true',     default=False,  help='Run or plot a only the background')
argParser.add_argument('--plotSingleBin',   action='store_true',     default=False,  help='Run or plot a only the background')
argParser.add_argument('--categoriesToPlot',   action='store',     default='super',  help='What categories to use', choices=['original', 'analysis', 'super'])
argParser.add_argument('--additionalCondition',   action='store',     default=None,  help='Additional condition for selection')
argParser.add_argument('--ignoreSystematics',   action='store_true',     default=False,  help='ignore systematics in plots')
argParser.add_argument('--combineYears',   action='store_true',     default=False,  help='combine all years specified in year arg in plots')
argParser.add_argument('--submitPlotting',   action='store_true',     default=False,  help='Send the plotting code to HTCondor')

args = argParser.parse_args()

print '\033[93m Warning: dr_closestJet contained a bug where it was always 0. In order to be consistent with the MVA training, it is now still manually set to 0 at all times. Please change this in the eventSelectionTools when retraining has occured.\033[0m'

from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)

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

if args.includeData == 'signalregion' and args.region in ['baseline', 'lowMassSR', 'highMassSR']:
    raise RuntimeError('Running data in signal region without looking at the sideband. Either run in sideband or do not attempt this before approval')

#
# General imports
#
import os
from HNL.Tools.histogram import Histogram
from HNL.Tools.mergeFiles import merge
from HNL.Tools.helpers import getObjFromFile, progress, makeDirIfNeeded
from HNL.EventSelection.bitCutter import Cutter
from HNL.Weights.reweighter import Reweighter
from HNL.TMVA.reader import ReaderArray
from HNL.Samples.sampleManager import SampleManager
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
    elif args.includeData == 'includeSideband':
        skim_str = 'Reco'
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
# Prepare jobs
#
if not args.isTest:
    jobs = {}
    if args.makePlots and args.submitPlotting and not args.isChild:
        jobs = [['0']]
    else:
        for year in args.year:
            jobs[year] = []
            sample_manager = getSampleManager(year)
        
            for sample_name in sample_manager.sample_names:
                if args.includeData is None and 'Data' in sample_name: continue
                sample = sample_manager.getSample(sample_name)
                if args.sample and args.sample != sample.name: continue
                for njob in xrange(sample.returnSplitJobs()): 
                    jobs[year] += [(sample.name, str(njob), None)]

#
# Submit subjobs
#

from HNL.Tools.jobSubmitter import submitJobs, checkShouldMerge
if args.makePlots and args.submitPlotting and not args.isChild:
    submitJobs(__file__, ['subJob'], jobs, argParser, jobLabel='runAnalysis-plotting-'+args.region, include_all_groups = True)
    exit(0)

if not args.isChild and not args.makePlots and not args.makeDataCards:
    # if not args.dryRun and checkShouldMerge(__file__, argParser):
    #     raise RuntimeError("Already existing files available. You would be overwriting")
    for year in jobs.keys():
        submitJobs(__file__, ('sample', 'subJob'), jobs[year], argParser, jobLabel = 'runAnalysis-'+str(year)+'-'+args.region, additionalArgs= [('year', year)])
        exit(0)

#
# Some constants to make referring to signal leptons more readable
#
l1 = 0
l2 = 1
l3 = 2
l4 = 3

nl = 3 if args.region != 'ZZCR' else 4

import HNL.Analysis.analysisTypes as at
if args.region == 'NoSelection':
    var = at.var_noselection
elif args.strategy == 'MVA':
    var = at.returnVariables(nl, not args.genLevel, args.region)
else:
    var = at.returnVariables(nl, not args.genLevel)

from HNL.EventSelection.eventSelector import signal_regions
#
# Define categories to use
#
import HNL.EventSelection.eventCategorization as cat
def listOfCategories(region):
    if nl == 3:
        return cat.CATEGORIES
    else:
        return [max(cat.CATEGORIES)]

categories = listOfCategories(args.region)
reco_or_gen_str = 'reco' if not args.genLevel else 'gen'

#
# Extra imports for dividing by region
#
from HNL.EventSelection.searchRegions import SearchRegionManager
srm = {}
srm[args.region] = SearchRegionManager(args.region)

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
    if args.systematics == 'full' and not args.ignoreSystematics: syst_to_run += sjr.getReruns(year, proc, split_syst=True, split_correlations = split_corr)
    return syst_to_run    

#
# Loop over samples and events
#
if not args.makePlots and not args.makeDataCards:

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
    if chain.is_data and args.includeData == 'includeSideband':
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
    if args.masses is not None and chain.HNLmass not in args.masses: exit(0)

    def runEventLoop(chain, output_name, systematic='nominal'):

        #
        # Load in sample and chain
        #
        event = Event(sample, chain, sample_manager, is_reco_level=not args.genLevel, selection=args.selection, strategy=args.strategy, region=args.region, analysis=args.analysis, year = year, era = args.era)

        #
        # Prepare output tree
        #
        from HNL.Tools.outputTree import OutputTree
        branches = []
        for v in var.keys():
            branches.extend(['{0}/F'.format(v)])
        branches.extend(['weight/F', 'isprompt/O', 'category/I', 'searchregion/I', 'issideband/O'])
        if args.tag == 'TauFakePurity': branches.extend(['istight/O'])
        branches.extend(event.reweighter.returnBranches())
        branches.extend(event.systematics.returnBranches(args.sample))
        output_tree = OutputTree('events_{0}'.format(systematic), output_name_full, branches = branches, branches_already_defined = systematic != 'nominal')


        #
        # Create cutter to provide cut flow
        #
        cutter = Cutter(name = systematic, chain = chain, categories = listOfCategories(args.region))

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
            #if args.isTest: progress(entry - event_range[0], len(event_range))
            progress(entry - event_range[0], len(event_range))
 
            cutter.cut(True, 'Total')

            #
            # Event selection
            #
 
            event.initEvent(reset_obj_sel = True)
            if args.tag == 'TauFakePurity':
                chain.obj_sel['tau_wp'] = 'FO'            
       
            is_sideband_event = False
            manually_blinded = True
            passed_tight_selection = event.passedFilter(cutter, sample.name, sideband = [2] if args.tag == 'TauFakes' else None, for_training = 'ForTraining' in args.region, manually_blinded = manually_blinded, calculate_weights = True)
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
            # If you ever remove these next lines, set remove manually_blinded as well
            #
            if args.region in signal_regions and chain.is_data and not is_sideband_event:
                continue            

            #
            # Determine if it is a prompt event
            # Depending on the previous step, the selection should be the tight or the FO (because of rerunning)
            #
            prompt_str = None
            if args.region != 'NoSelection':
                if len(chain.l_flavor) == chain.l_flavor.count(2): continue #Not all taus

                nprompt = 0
                if not 'Data' in sample.name:
                    for i, index in enumerate(chain.l_indices):
                        #For taufakes we're only interested in FO tau to make the prompt consideration
                        if args.tag == 'TauFakes':
                            if chain._lIsPrompt[index] or chain._lFlavor[index] < 2 or chain.l_istight[i]: nprompt += 1
                        elif args.tag == 'TauFakePurity':
                            if chain._lIsPrompt[index] or chain._lFlavor[index] < 2: nprompt += 1
                        else:            
                            if not args.genLevel and chain._lIsPrompt[index]: nprompt += 1
                            elif args.genLevel and chain._gen_lIsPrompt[index]: nprompt += 1
                   
                    print nprompt, nprompt == nl 
                    prompt_str = 'prompt' if nprompt == nl else 'nonprompt'
                    if args.tag == 'TauFakePurity':
                        chain.istight = all([chain.l_istight[l] for l in range(nl) if chain.l_flavor[l] == 2])
            else:
                prompt_str = None
                chain.category = 17

            if args.strategy == 'MVA':
                tmva.predictAndWriteAll(chain)

            #
            # Fill tree
            #
            event.reweighter.fillTreeWithWeights(output_tree)
            for v in var.keys():
                output_tree.setTreeVariable(v, var[v][0](chain))
           
            output_tree.setTreeVariable('weight', event.reweighter.getTotalWeight(sideband = is_sideband_event, tau_fake_method = 'TauFakesDY' if args.region == 'ZZCR' else None))
            output_tree.setTreeVariable('isprompt', prompt_str == 'prompt')
            output_tree.setTreeVariable('category', chain.category)
            output_tree.setTreeVariable('searchregion', srm[args.region].getSearchRegion(chain))
            output_tree.setTreeVariable('issideband', is_sideband_event)
            if args.tag == 'TauFakePurity':
                output_tree.setTreeVariable('istight', chain.istight)
                
            event.systematics.storeAllSystematicsForShapes(output_tree, args.sample)
            output_tree.fill()
 
        #
        # Save histograms
        #
        output_tree.write(is_test = arg_string if args.isTest else None, append = systematic != 'nominal')
        
        cutter.saveCutFlow(output_name, arg_string = arg_string if args.isTest else None)
   
    for syst in getSystToRun(year, args.sample): 
        print 'Running {0}'.format(syst)
        runEventLoop(chain, output_name_full, syst)
    
    closeLogger(log)

#If the option to not run over the events again is made, load in the already created histograms here
else:
    from ROOT import gROOT
    gROOT.SetBatch(True)
    import glob
    from HNL.Analysis.analysisTypes import signal_couplingsquared, signal_couplingsquaredinsample
    from HNL.Tools.helpers import getHistFromTree


    # Merge and collect histograms
    list_of_hist = {}
    list_of_hist_forbar = {}

    for year in args.year:
        print 'Processing ', year

        sample_manager = getSampleManager(year)

        if not args.bkgrOnly:
            signal_list = [s for s in glob.glob(getOutputName('signal', year, args.tag)+'/*'+args.flavor+'-*') if s.split('/')[-1] in sample_manager.sample_outputs]
            for i, s in enumerate(signal_list):
                if 'signalOrdering' in s:
                    signal_list.pop(i)
        else:
            signal_list = []

        # Collect background file locations
        if not args.signalOnly:
            bkgr_list = [getOutputName('bkgr', year, args.tag)+'/'+b for b in sample_manager.sample_outputs if os.path.isdir(getOutputName('bkgr', year, args.tag)+'/'+b)]
        else:
            bkgr_list = []

        # data
        if args.includeData is not None:
            data_list = glob.glob(getOutputName('data', year, args.tag)+'/Data')
        else:
            data_list = []

        print 'check merge'
        # Merge files if necessary
        mixed_list = signal_list + bkgr_list + data_list
        custom_list_to_use = customizeListToUse(year)
        full_path = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Analysis'))
        merge(mixed_list, __file__, jobs[year], ('sample', 'subJob'), argParser, istest=args.isTest, additionalArgs= [('year', year)], man_changed_args = {'customList':custom_list_to_use}, full_path = full_path)

        if not args.individualSamples:
            background_collection = []
            for x in sample_manager.sample_outputs:
                if 'HNL' in x: continue
                if 'Data' in x: continue
                if not os.path.isdir(getOutputName('bkgr', year, args.tag)+'/'+x): continue
                background_collection.append(x)
            
            background_collection += ['non-prompt']
        else:
            background_collection = [x for x in sample_manager.sample_names if not 'HNL' in x and not 'Data' in x]

        #background_collection = ['XG']

        #Clean list of hist
        tmp_signal_list = []
        tmp_bkgr_list = []
        for i_s, s in enumerate(signal_list):
            sample_name = s.split('/')[-1]
            sample_mass = float(sample_name.split('-m')[-1])
            if args.sample is not None and args.sample != sample_name:      continue
            if sample_name not in sample_manager.sample_outputs:              continue    
            if args.masses is not None and sample_mass not in args.masses:  continue 
            if args.flavor is not None and '-'+args.flavor+'-' not in sample_name:  continue 
            tmp_signal_list.append(s)

        signal_list = [x for x in tmp_signal_list]

        sorted_analysis_categories = cat.ANALYSIS_CATEGORIES.keys()
        sorted_super_categories = cat.SUPER_CATEGORIES.keys()

        #Reset list_of_hist
        category_dict = {
            'original' : ([x for x in categories], ['(category=={0})'.format(x) for x in categories], {y : [str(y)] for y in categories}),
            'analysis': (sorted_analysis_categories, ['('+'||'.join(['category=={0}'.format(x) for x in cat.ANALYSIS_CATEGORIES[y]])+')' for y in sorted_analysis_categories], {y :[str(x) for x in cat.ANALYSIS_CATEGORIES[y]] for y in sorted_analysis_categories}),
            'super' : (sorted_super_categories, ['('+'||'.join(['category=={0}'.format(x) for x in cat.SUPER_CATEGORIES[y]])+')' for y in sorted_super_categories], {y:[str(x) for x in cat.SUPER_CATEGORIES[y]] for y in sorted_super_categories})
        } 
        
        #Add entry for the search regions in the var dictionary
        from HNL.Weights.reweighter import var_weights
        var.update(var_weights)
        var['searchregion'] = (lambda c : c.searchregion, np.arange(0.5, srm[args.region].getNumberOfSearchRegions()+1.5, 1.), ('Search Region', 'Events'))

        # Custom Var that you can create from existing var (i.e. 2D plots)
        # var['l3pt-met'] = (lambda c : [c.l3pt, c.met], (np.array([20., 25., 35., 50., 70., 100.]), np.array([0., 20., 35., 50., 100.])), ('p_{T}(l3) [GeV]', 'met'))

        #
        # Create variable distributions
        #

        def createSingleVariableDistributions(tree, vname, hname, bins, condition, proc, include_systematics = False, split_corr = False):
            #import time
            #init_time = time.time()
            out_dict = {}
            out_dict['nominal'] = Histogram(tree.getHistFromTree(vname, hname, bins, condition))
            if include_systematics:
                from HNL.Systematics.systematics import returnWeightShapes
                out_dict.update(returnWeightShapes(tree, vname, hname, bins, condition, year, proc, ['non-prompt'] if args.includeData == 'includeSideband' else None, split_corr = split_corr))
            #end_time = time.time()
            #print "Time:", end_time - init_time
            return out_dict 


        #TODO: remove split_tau_signal after we can do tau signal cleaning (aka gen info becomes available)
        def createVariableDistributions(categories_dict, var_dict, signal, background, data, sample_manager, additional_condition = None, split_tau_signal = False, include_systematics = False, sr = None, split_corr = False):
            if additional_condition is None:
                additional_condition = ''
            else:
                additional_condition = '&&({0})'.format(additional_condition)

    
            from HNL.Tools.outputTree import OutputTree
            categories_to_use = categories_dict[0]
            category_conditions = categories_dict[1]
            tmp_list_of_hist = {}
            print "Preparing the hist list"
            for c in categories_to_use:
                tmp_list_of_hist[c] = {}
                for v in var_dict:
                    tmp_list_of_hist[c][v] = {'signal':{}, 'bkgr':{}, 'data':{}}

            # Load in the signal histograms from the files
            if not args.bkgrOnly:
                print "Loading signal histograms"
                for isignal, s in enumerate(signal):
                    progress(isignal, len(signal))
                    sample_name = s.split('/')[-1]
                    sample_mass = float(sample_name.split('-m')[-1])

                    from HNL.Tools.helpers import isValidRootFile
                    check_split_tau = all([isValidRootFile(s+'/variables-HNL-{0}-m{1}.root'.format(x, int(sample_mass))) for x in ['taulep', 'tauhad']])
                    if not split_tau_signal or not check_split_tau:
                        syst_to_run = getSystToRun(year, sample_name)            
                        split_syst_to_run = getSystToRun(year, sample_name, split_corr=split_corr)            
                        for syst, corr_syst in zip(syst_to_run, split_syst_to_run):
                            intree = OutputTree('events_{0}'.format(syst), s+'/variables.root')
                            for c, cc in zip(categories_to_use, category_conditions): 
                                for v in var_dict.keys():
                                    if syst == 'nominal':
                                        tmp_list_of_hist[c][v]['signal'][sample_name] = createSingleVariableDistributions(intree, v, str(c)+'-'+v+'-'+syst+'-'+sample_name+'-'+str(sr)+'-'+str(year), var_dict[v][1], '('+cc+'&&!issideband)'+additional_condition, sample_name, include_systematics, split_corr = split_corr)
                                    else:
                                        tmp_list_of_hist[c][v]['signal'][sample_name][corr_syst] = createSingleVariableDistributions(intree, v, str(c)+'-'+v+'-'+syst+'-'+sample_name+'-'+str(sr)+'-'+str(year), var_dict[v][1], '('+cc+'&&!issideband)'+additional_condition, sample_name, split_corr = split_corr)['nominal'] 
                    else:
                        for tausig in ['taulep', 'tauhad']:
                            syst_to_run = getSystToRun(year, sample_name)            
                            split_syst_to_run = getSystToRun(year, sample_name, split_corr=split_corr)            
                            for syst, corr_syst in zip(syst_to_run, split_syst_to_run):
                                sample_name = 'HNL-{0}-m{1}'.format(tausig, int(sample_mass))
                                intree = OutputTree('events_{0}'.format(syst), s+'/variables-{0}.root'.format(sample_name))

                                for c, cc in zip(categories_to_use, category_conditions):
                                    for v in var_dict.keys():
                                        if syst == 'nominal':
                                            tmp_list_of_hist[c][v]['signal'][sample_name] = createSingleVariableDistributions(intree, v, str(c)+'-'+v+'-'+syst+'-'+sample_name+'-'+str(sr)+'-'+str(year), var_dict[v][1], '('+cc+'&&!issideband)'+additional_condition, sample_name, include_systematics, split_corr=split_corr)
                                        else:
                                            tmp_list_of_hist[c][v]['signal'][sample_name][corr_syst] = createSingleVariableDistributions(intree, v, str(c)+'-'+v+'-'+syst+'-'+sample_name+'-'+str(sr)+'-'+str(year), var_dict[v][1], '('+cc+'&&!issideband)'+additional_condition, sample_name, split_corr=split_corr)['nominal']
                                    
 
                    for c, cc in zip(categories_to_use, category_conditions): 
                        for v in var_dict.keys():
                            for syst in tmp_list_of_hist[c][v]['signal'][sample_name].keys():
                                coupling_squared = args.rescaleSignal if args.rescaleSignal is not None else signal_couplingsquared[args.flavor][sample_mass]
                                tmp_list_of_hist[c][v]['signal'][sample_name][syst].hist.Scale(coupling_squared/signal_couplingsquaredinsample[args.flavor][sample_mass])
                print '\n'

            if args.includeData is not None:
                print "Loading data"
                syst_to_run = getSystToRun(year, 'non-prompt') if args.includeData == 'includeSideband' else ['nominal']    
                split_syst_to_run = getSystToRun(year, 'non-prompt', split_corr=split_corr) if args.includeData == 'includeSideband' else ['nominal']           
                for isyst, (syst, corr_syst) in enumerate(zip(syst_to_run, split_syst_to_run)):
                    progress(isyst, len(syst_to_run))
                    intree = OutputTree('events_{0}'.format(syst), data_list[0]+'/variables.root')
                    for ic, (c, cc) in enumerate(zip(categories_to_use, category_conditions)):
                        for v in var_dict:
                            if syst == 'nominal':
                                tmp_list_of_hist[c][v]['data']['sideband'] = createSingleVariableDistributions(intree, v, str(c)+'-'+v+'-'+syst+'-Data-sideband'+'-'+str(sr)+'-'+str(year), var_dict[v][1], '('+cc+'&&issideband)'+additional_condition, 'non-prompt', include_systematics, split_corr=split_corr)
                                tmp_list_of_hist[c][v]['data']['signalregion'] = {'nominal' : Histogram(intree.getHistFromTree(v, str(c)+'-'+v+'-'+'-nominal-Data-signalregion'+'-'+str(sr)+'-'+str(year), var_dict[v][1], '('+cc+'&&!issideband)'+additional_condition))}
                            else:
                                tmp_list_of_hist[c][v]['data']['sideband'][corr_syst] = createSingleVariableDistributions(intree, v, str(c)+'-'+v+'-'+syst+'-Data-sideband'+'-'+str(sr)+'-'+str(year), var_dict[v][1], '('+cc+'&&issideband)'+additional_condition, 'non-prompt', split_corr=split_corr)['nominal']

            if not args.signalOnly:
                print "Loading background histograms"
                for ib, b in enumerate(background):
                    for c, cc in zip(categories_to_use, category_conditions):
                        for iv, v in enumerate(var_dict.keys()): 
                            tmp_list_of_hist[c][v]['bkgr'][b] = {}


                for ib, b in enumerate(background):
                    #print b
                    progress(ib, len(background))
                    if not args.individualSamples:
                        if b == 'non-prompt': continue
                        syst_to_run = getSystToRun(year, b)            
                        
                        split_syst_to_run = getSystToRun(year, b, split_corr=split_corr)            
                        for syst, corr_syst in zip(syst_to_run, split_syst_to_run):
                     #       print syst
                            intree = OutputTree('events_{0}'.format(syst), getOutputName('bkgr', year, args.tag)+'/'+b+'/variables.root')                       
 
                            for c, cc in zip(categories_to_use, category_conditions):
                      #          print c, cc
                                for iv, v in enumerate(var_dict.keys()): 
                       #             print v, var_dict[v][1]
                                    if syst == 'nominal': 
                                        tmp_list_of_hist[c][v]['bkgr'][b] = createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'p'+syst+'-'+str(sr)+'-'+str(year), var_dict[v][1], '('+cc+'&&isprompt&&!issideband)'+additional_condition, b, include_systematics, split_corr=split_corr)
                                    else:
                                        tmp_list_of_hist[c][v]['bkgr'][b][corr_syst] = createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'p'+syst+'-'+str(sr)+'-'+str(year), var_dict[v][1], '('+cc+'&&isprompt&&!issideband)'+additional_condition, b, split_corr=split_corr)['nominal']
                                               
                                    if args.includeData != 'includeSideband':
                                        if syst == 'nominal': 
                                            tmp_hist = createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'np'+syst+'-'+str(sr)+'-'+str(year), var_dict[v][1], '('+cc+'&&!isprompt&&!issideband)'+additional_condition, 'non-prompt', include_systematics)
                                        else:
                                            tmp_hist = createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'np'+syst+'-'+str(sr)+'-'+str(year), var_dict[v][1], '('+cc+'&&!isprompt&&!issideband)'+additional_condition, b)['nominal']

                                        if 'non-prompt' not in tmp_list_of_hist[c][v]['bkgr'].keys():
                                            tmp_list_of_hist[c][v]['bkgr']['non-prompt'] = tmp_hist
                                        else:
                                            tmp_list_of_hist[c][v]['bkgr']['non-prompt'][corr_syst] = tmp_hist['nominal']
                                        del(tmp_hist)
                    else:
                        syst_to_run = getSystToRun(year, b)            
                        split_syst_to_run = getSystToRun(year, sample_name, split_corr=split_corr)            
                        for syst, corr_syst in zip(syst_to_run, split_syst_to_run):
                            intree = OutputTree('events', getOutputName('bkgr', year)+'/'+sample_manager.output_dict[b]+'/variables-'+b+'.root')                       
                            for c, cc in zip(categories_to_use, category_conditions):
                                for iv, v in enumerate(var_dict.keys()):
                                    if syst == 'nominal': 
                                        tmp_list_of_hist[c][v]['bkgr'][b] = createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'t'+syst+'-'+str(sr)+'-'+str(year), var_dict[v][1], '('+cc+'&&!issideband)'+additional_condition, b, include_systematics, split_corr=split_corr)
                                    else:
                                        tmp_list_of_hist[c][v]['bkgr'][b][corr_syst] = createSingleVariableDistributions(intree, v, 'tmp_'+b+v+str(c)+'t'+syst+'-'+str(sr)+'-'+str(year), var_dict[v][1], '('+cc+'&&!issideband)'+additional_condition, b, split_corr=split_corr)['nominal']

                if args.includeData == 'includeSideband':
                    for c, cc in zip(categories_to_use, category_conditions):
                        for iv, v in enumerate(var_dict.keys()):
                            tmp_list_of_hist[c][v]['bkgr']['non-prompt'] = tmp_list_of_hist[c][v]['data']['sideband']

            return tmp_list_of_hist
        
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

            #
            # If we want to use shapes, first make shape histograms, then make datacards
            #
            for sr in srm[args.region].getListOfSearchRegionGroups():
                print 'Making datacards for region', sr
                var_for_datacard = {}
                var_for_datacard['searchregion'] = (lambda c : c.searchregion, np.arange(srm[args.region].getGroupValues(sr)[0]-0.5, srm[args.region].getGroupValues(sr)[-1]+1.5, 1.), ('Search Region', 'Events'))
                if args.strategy == 'MVA':
                    set_of_mvas = set()
                    for sample_mass in args.masses:
                        for mva in getAllRelevantNames(sample_mass, args.flavor):
                            set_of_mvas.add(mva)
                    
                    list_of_mvas = [x for x in set_of_mvas]
                    for mva in list_of_mvas:
                        var_for_datacard[mva] = [x for x in var[mva]]

                hist_for_datacard = createVariableDistributions(category_dict[args.categoriesToPlot], var_for_datacard, signal_list, background_collection, data_list, sample_manager, '||'.join(['searchregion=={0}'.format(x) for x in srm[args.region].getGroupValues(sr)]), split_tau_signal = True, include_systematics = True, sr=sr, split_corr=True)
                   
                for ac in category_dict[args.categoriesToPlot][0]:
                    print 'Filling', ac
                    for s in signal_list:
                        sample_name = s.split('/')[-1]
                        sample_mass = float(sample_name.split('-m')[-1])
                        if sample_mass not in args.masses: continue
                        for v in var_for_datacard.keys():

                            bin_name = sr+'-'+ac+'-'+v
                            out_path = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'shapes', '-'.join([args.selection, args.region]), 
                                                    args.era+str(year), args.flavor, sample_name, bin_name+'.shapes.root')
                            makeDirIfNeeded(out_path)
                            try:
                                if 'HNL-tau' in sample_name:
                                    if ac == 'NoTau': sample_name = sample_name.replace('tau', 'taulep')
                                    else: sample_name = sample_name.replace('tau', 'tauhad')
                                    hist_for_datacard[ac][v]['signal'][sample_name]['nominal']
                            except:
                                sample_name = 'HNL-tau-m{0}'.format(int(sample_mass))
                            hist_for_datacard[ac][v]['signal'][sample_name]['nominal'].replaceZeroBins()
                            hist_for_datacard[ac][v]['signal'][sample_name]['nominal'].write(out_path, write_name='HNL-{0}-m{1}'.format(args.flavor, int(sample_mass)), subdirs = [bin_name.rsplit('-', 1)[0]])
                            for syst in hist_for_datacard[ac][v]['signal'][sample_name].keys():
                                if syst == 'nominal': continue
                                hist_for_datacard[ac][v]['signal'][sample_name][syst].replaceZeroBins()
                                hist_for_datacard[ac][v]['signal'][sample_name][syst].write(out_path, write_name='HNL-{0}-m{1}'.format(args.flavor, int(sample_mass)), subdirs = [bin_name.rsplit('-', 1)[0]+syst], append=True)
                            bkgr_names = []
                            for ib, b in enumerate(background_collection):
                                bkgr_name = b.split('/')[-1]
                                if hist_for_datacard[ac][v]['bkgr'][bkgr_name]['nominal'].hist.GetSumOfWeights() > 0:
                                    hist_for_datacard[ac][v]['bkgr'][bkgr_name]['nominal'].replaceZeroBins()
                                    hist_for_datacard[ac][v]['bkgr'][bkgr_name]['nominal'].write(out_path, write_name=bkgr_name, subdirs = [bin_name.rsplit('-', 1)[0]], append=True)
                                    for syst in hist_for_datacard[ac][v]['bkgr'][bkgr_name].keys():
                                        if syst == 'nominal': continue
                                        hist_for_datacard[ac][v]['bkgr'][bkgr_name][syst].replaceZeroBins()
                                        hist_for_datacard[ac][v]['bkgr'][bkgr_name][syst].write(out_path, write_name=bkgr_name, subdirs = [bin_name.rsplit('-', 1)[0]+syst], append=True)
                                    bkgr_names.append(bkgr_name)
                            
                            data_hist_tmp = hist_for_datacard[ac][v]['signal'][sample_name]['nominal'].clone('Ditau')
                            data_hist_tmp.replaceZeroBins()
                            data_hist_tmp.write(out_path, write_name='data_obs', append=True, subdirs = [bin_name.rsplit('-', 1)[0]])
                            coupling_squared = args.rescaleSignal if args.rescaleSignal is not None else signal_couplingsquared[args.flavor][sample_mass]
                            if 'HNL-tau' in sample_name:
                                sample_name = 'HNL-tau-m{0}'.format(int(sample_mass))
                            makeDataCard(bin_name, args.flavor, args.era, year, 0, sample_name, bkgr_names, args.selection, args.region, ac, shapes=True, coupling_sq = coupling_squared, nonprompt_from_sideband = args.includeData == 'includeSideband')

        if args.makePlots:
            print "Creating list of histograms"
            list_of_hist[year] = createVariableDistributions(category_dict[args.categoriesToPlot], var, signal_list, background_collection, data_list, sample_manager, additional_condition = args.additionalCondition, include_systematics = args.systematics is not None and not args.ignoreSystematics)
            print "Making Bar Charts"
            list_of_hist_forbar[year] = createVariableDistributions(category_dict['original'], {'searchregion' : var['searchregion']}, signal_list, background_collection, data_list, sample_manager, additional_condition = args.additionalCondition)



    years_to_plot = [y for y in args.year]
    if args.combineYears: years_to_plot.extend(['-'.join(args.year)])

    if args.combineYears:
        def combineYears(hist_list, include_systematics = True):
            tmp_hist_list = {}
            for y in args.year:
                for c in hist_list[y].keys():
                    if c not in tmp_hist_list.keys(): tmp_hist_list[c] = {}
                    for v in hist_list[y][c].keys():
                        if v not in tmp_hist_list[c].keys(): tmp_hist_list[c][v] = {}
                        for sob in hist_list[y][c][v].keys():
                            if sob not in tmp_hist_list[c][v].keys(): tmp_hist_list[c][v][sob] = {}
                            for sample in  hist_list[y][c][v][sob].keys():
                                if sample not in tmp_hist_list[c][v][sob].keys(): tmp_hist_list[c][v][sob][sample] = {}
                                if 'nominal' not in tmp_hist_list[c][v][sob][sample].keys(): 
                                    tmp_hist_list[c][v][sob][sample]['nominal'] = hist_list[y][c][v][sob][sample]['nominal'].clone('combined')
                                else:
                                    tmp_hist_list[c][v][sob][sample]['nominal'].add(hist_list[y][c][v][sob][sample]['nominal'])

                                if include_systematics and args.systematics == 'full' and not args.ignoreSystematics:
                                    if sob == 'data': continue
                                    from HNL.Systematics.systematics import makeSystErrorHist
                                    hist_list[y][c][v][sob][sample]['total_syst'] = makeSystErrorHist(hist_list[y][c][v][sob][sample], sample, c, year, 'non-prompt' if args.includeData == 'includeSideband' else None)
                                    if 'total_syst' not in tmp_hist_list[c][v][sob][sample].keys():
                                        tmp_hist_list[c][v][sob][sample]['total_syst'] = hist_list[y][c][v][sob][sample]['total_syst'].clone('combined')
                                    else:
                                        tmp_hist_list[c][v][sob][sample]['total_syst'].add(hist_list[y][c][v][sob][sample]['total_syst'])

            return tmp_hist_list 
       
 
        list_of_hist[years_to_plot[-1]] = combineYears(list_of_hist)
        list_of_hist_forbar[years_to_plot[-1]] = combineYears(list_of_hist_forbar, False)

    for year in years_to_plot:
        
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
                other_hist = hist_dict[sorted_yields[n+1][0]].clone('other_hist')
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
            output_dir = os.path.join(output_dir, 'signalOnly')
        elif args.bkgrOnly:
            output_dir = os.path.join(output_dir, 'bkgrOnly')
        else:
            output_dir = os.path.join(output_dir, 'signalAndBackground')



        if args.flavor:         output_dir = os.path.join(output_dir, args.flavor+'_coupling')
        else:                   output_dir = os.path.join(output_dir, 'all_coupling')

        if args.masses is not None:         output_dir = os.path.join(output_dir, 'customMasses', '-'.join([str(m) for m  in args.masses]))
        else:         output_dir = os.path.join(output_dir, 'allMasses')

        output_dir = makePathTimeStamped(output_dir)

        #
        # Create variable plots for each category
        #
        print "Creating variable plots"

        from HNL.EventSelection.eventCategorization import CATEGORY_NAMES
        # for c in list_of_hist.keys():
        for c in category_dict[args.categoriesToPlot][0]:
            if args.categoriesToPlot == 'original':
                c_name = CATEGORY_NAMES[c]
            elif args.categoriesToPlot == 'analysis':
                from HNL.EventSelection.eventCategorization import ANALYSIS_CATEGORIES_TEX
                c_name = ANALYSIS_CATEGORIES_TEX[c] 
            else:
                from HNL.EventSelection.eventCategorization import SUPER_CATEGORIES_TEX
                c_name = SUPER_CATEGORIES_TEX[c] 

            extra_text = [extraTextFormat(c_name, xpos = 0.2, ypos = 0.74, textsize = None, align = 12)]  #Text to display event type in plot
            if args.flavor: 
                from decimal import Decimal
                et_flavor = args.flavor if args.flavor == 'e' else '#'+args.flavor
                extra_text.append(extraTextFormat('|V_{'+et_flavor+'N}|^{2} = '+'%.0E' % Decimal(str(0.01**2)), textsize = 0.7))
    
            # Plots that display chosen for chosen signal masses and backgrounds the distributions for the different variables
            # S and B in same canvas for each variable
            for v in var.keys():
                syst_hist = []
                bkgr_legendnames = []
                # Make list of background histograms for the plot object (or None if no background)
                if args.signalOnly or not list_of_hist[year][c][v]['bkgr'].values(): 
                    bkgr_hist = None
                else:
                    bkgr_hist = []
                    syst_hist = []
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
            
                                syst_hist.append(list_of_hist[year][c][v]['bkgr'][bk]['total_syst'])

                # Make list of signal histograms for the plot object
                signal_legendnames = []
                if args.bkgrOnly or not list_of_hist[year][c][v]['signal'].values(): 
                    signal_hist = None
                else:
                    signal_hist = []
                    for sk in list_of_hist[year][c][v]['signal'].keys():
                        signal_hist.append(list_of_hist[year][c][v]['signal'][sk]['nominal'])
                        # if 'filtered' in sk:
                        #     signal_legendnames.append('HNL m_{N} = 30 GeV w Pythia filter')
                        # else:
                        # signal_legendnames.append('HNL '+ sk.split('-')[1] +' m_{N} = '+sk.split('-m')[-1]+ ' GeV')
                        signal_legendnames.append('HNL m_{N}='+sk.split('-m')[-1]+ 'GeV')

                if args.includeData is not None and not 'Weight' in v:
                    observed_hist = list_of_hist[year][c][v]['data']['signalregion']['nominal']
                    #tmp blinding
                    if args.region in signal_regions: observed_hist = None
                else:
                    observed_hist = None

                from HNL.Plotting.plottingDicts import sample_tex_names
                #Clean bkgr names
                bkgr_legendnames = [sample_tex_names[x] for x in bkgr_legendnames]


                if not args.signalOnly and not args.bkgrOnly:
                    legend_names = signal_legendnames+bkgr_legendnames
                elif args.signalOnly:
                    legend_names = signal_legendnames
                else:
                    legend_names = bkgr_legendnames
        
                #Create specialized signal region plots if this is the correct variable
                if v == 'searchregion' and args.region in signal_regions:
                    from HNL.EventSelection.searchRegions import plotLowMassRegions, plotHighMassRegions, plotLowMassRegionsLoose
                    # else:
                    #     signal_names = [s + ' V^{2}=' + str(signal_couplingsquared[s.split('-')[1]][int(s.split('-m')[-1])])  for s in signal_names]
                       
                    if args.region == 'lowMassSR':
                        plotLowMassRegions(signal_hist, bkgr_hist, legend_names, 
                            out_path = os.path.join(output_dir, 'Yields', 'SearchRegions', c), extra_text = [x for x in extra_text], year = year, era = args.era)
                    if args.region == 'lowMassSRloose':
                        plotLowMassRegionsLoose(signal_hist, bkgr_hist, legend_names, 
                            out_path = os.path.join(output_dir, 'Yields', 'SearchRegions', c), extra_text = [x for x in extra_text], year = year, era = args.era)
                    if args.region == 'highMassSR':
                        plotHighMassRegions(signal_hist, bkgr_hist, legend_names, 
                            out_path = os.path.join(output_dir, 'Yields', 'SearchRegions', c), extra_text = [x for x in extra_text], year = year, era = args.era)

                else:

                    # Create plot object (if signal and background are displayed, also show the ratio)
                    draw_ratio = None if args.signalOnly or args.bkgrOnly else True
                    if args.includeData is not None: draw_ratio = True
                    if not args.individualSamples:
                        #p = Plot(signal_hist, legend_names, c+'-'+v, bkgr_hist = bkgr_hist, observed_hist = observed_hist, y_log = True, extra_text = extra_text, draw_ratio = draw_ratio, year = year, era=args.era,
                        #p = Plot(signal_hist, legend_names, c+'-'+v, bkgr_hist = bkgr_hist, observed_hist = observed_hist, syst_hist = syst_hist if args.systematics == 'full' and not args.ignoreSystematics else None, y_log = True, extra_text = [x for x in extra_text], draw_ratio = draw_ratio, year = year, era=args.era,
                        p = Plot(signal_hist, legend_names, c+'-'+v, bkgr_hist = bkgr_hist, observed_hist = observed_hist, syst_hist = syst_hist if args.systematics == 'full' and not args.ignoreSystematics else None, y_log = False, extra_text = [x for x in extra_text], draw_ratio = draw_ratio, year = year, era=args.era,
                                color_palette = 'HNL', color_palette_bkgr = 'HNLfromTau' if not args.analysis == 'tZq' else 'tZq', x_name = var[v][2][0], y_name = var[v][2][1])
                    else:
                        p = Plot(signal_hist, legend_names, c+'-'+v, bkgr_hist = bkgr_hist, observed_hist = observed_hist, y_log = True, extra_text = [x for x in extra_text], draw_ratio = draw_ratio, year = year, era=args.era,
                                color_palette = 'Didar', color_palette_bkgr = 'Didar', x_name = var[v][2][0], y_name = var[v][2][1])


                    # Draw
                    #p.drawHist(output_dir = os.path.join(output_dir, 'Variables' if v != 'searchregion' else 'Yields/SearchRegions', c), normalize_signal = True, draw_option='EHist', min_cutoff = 1)
                    if '-' in v:
                        p.draw2D(output_dir = os.path.join(output_dir+'/2D', 'Variables' if v != 'searchregion' else 'Yields/SearchRegions', c))
                    else:
                        p.drawHist(output_dir = os.path.join(output_dir, 'Variables' if v != 'searchregion' else 'Yields/SearchRegions', c), normalize_signal = 'bkgr', draw_option='EHist', min_cutoff = 1)
                        #p.drawHist(output_dir = os.path.join(output_dir, 'Variables' if v != 'searchregion' else 'Yields/SearchRegions', c), normalize_signal = 'med', draw_option='EHist', min_cutoff = 1)
                        #p.drawHist(output_dir = os.path.join(output_dir, 'Variables' if v != 'searchregion' else 'Yields/SearchRegions', c), normalize_signal = None, draw_option='EHist', min_cutoff = 1)
                        #p.drawHist(output_dir = os.path.join(output_dir, 'Variables' if v != 'searchregion' else 'Yields/SearchRegions', c), normalize_signal = 10., draw_option='EHist', min_cutoff = 1)
                    # p.drawHist(output_dir = os.path.join(output_dir, c), normalize_signal = False, draw_option='EHist', min_cutoff = 1)

                if v == 'searchregion':
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
                    if bkgr_hist is not None:
                        for ib, b in enumerate(bkgr_hist):
                            process_line += ' & '+bkgr_legendnames[ib]+'\t'
                            yield_line += ' & %s \t'%float('%.1f' % b.getHist().GetSumOfWeights())
                    if signal_hist is not None:
                        for isig, sig in enumerate(signal_hist):
                            process_line += ' & '+signal_legendnames[isig]+'\t'
                            yield_line +=  ' & %s \t'%float('%.1f' % sig.getHist().GetSumOfWeights())

                    process_line += '\n'
                    yield_line += '\n'
                    out_file.write(process_line)
                    out_file.write(yield_line)
                    out_file.write('\\end{tabular}')
                    out_file.close()


        #
        # Bar charts
        #

        from HNL.EventSelection.eventCategorization import CATEGORY_TEX_NAMES
        from ROOT import TH1D
        grouped_categories = cat.SUPER_CATEGORIES

        signal_names = [s.split('/')[-1] for s in signal_list]
        for supercat in grouped_categories.keys():
            if nl != 3 and supercat != 'Other': continue
            #
            # Bkgr
            #
            if not args.signalOnly:
                hist_to_plot = []
                if args.individualSamples:
                    bkgr_hist_to_draw, bkgr_to_draw = selectNMostContributingHist(list_of_hist[supercat]['searchregion']['bkgr'], 7)
                else:
                    bkgr_to_draw = [b for b in background_collection]
                for i_sample, sample_name in enumerate(bkgr_to_draw):
                    hist_to_plot.append(TH1D(sample_name+supercat, sample_name+supercat, len(grouped_categories[supercat]), 0, len(grouped_categories[supercat])))
                    for i, c in enumerate(grouped_categories[supercat]):
                        if args.individualSamples and sample_name == 'Other':
                            bkgr_hist = selectNMostContributingHist(list_of_hist_forbar[year][c]['searchregion']['bkgr'], 7)[0][-1]
                            hist_to_plot[i_sample].SetBinContent(i+1, bkgr_hist.getHist().GetSumOfWeights()) 
                        else:
                            hist_to_plot[i_sample].SetBinContent(i+1, list_of_hist_forbar[year][c]['searchregion']['bkgr'][sample_name]['nominal'].getHist().GetSumOfWeights()) 

                if args.includeData == 'signalregion':
                    observed_hist = TH1D('data'+supercat, 'data'+supercat, len(grouped_categories[supercat]), 0, len(grouped_categories[supercat]))
                    for i, c in enumerate(grouped_categories[supercat]):
                        observed_hist.SetBinContent(i+1, list_of_hist_forbar[year][c]['searchregion']['data']['signalregion']['nominal'].getHist().GetSumOfWeights()) 
                else:
                    observed_hist = None

                x_names = [CATEGORY_TEX_NAMES[n] for n in grouped_categories[supercat]]
                #p = Plot(hist_to_plot, bkgr_to_draw, name = 'Events-bar-bkgr-'+supercat, observed_hist = observed_hist, x_name = x_names, y_name = 'Events', y_log='SingleTau' in supercat, color_palette = 'Didar')            
                p = Plot(hist_to_plot, bkgr_to_draw, name = 'Events-bar-bkgr-'+supercat, observed_hist = observed_hist, x_name = x_names, y_name = 'Events', y_log='SingleTau' in supercat)            

                p.drawBarChart(output_dir = os.path.join(output_dir, 'Yields', 'BarCharts'))
            
            #
            # Signal
            #   
        #    if not args.bkgrOnly:
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

#        print "plotting cutflow"
#        in_files = {}
#        for sample_name in background_collection+signal_names: 
#            if not args.individualSamples:
#                if args.flavor != 'tau' or not 'HNL' in sample_name:
#                    in_path = lambda y : getOutputName('signal' if 'HNL' in sample_name else 'bkgr', y, args.tag)+'/'+sample_name+'/variables.root'
#                else:
#                    extra_name = sample_name.replace('tau', 'tauhad')
#                    in_path = lambda y : getOutputName('signal' if 'HNL' in sample_name else 'bkgr', y, args.tag)+'/'+sample_name+'/variables-{0}.root'.format(extra_name)
#            else:
#                in_path = lambda y : getOutputName('bkgr', y, args.tag)+'/'+sample_manager.output_dict[sample_name]+'/variables-'+sample_name+'.root'
#
#            from HNL.Tools.helpers import isValidRootFile
#            print in_path(year), isValidRootFile(in_path(year))
#            if not '-' in year:
#                if not isValidRootFile(in_path(year)): continue
#                in_files[sample_name] = [in_path(year)]
#            else:
#                valid_for_all_years = True
#                for y in args.year:
#                    if not isValidRootFile(in_path(y)): 
#                        valid_for_all_years = False
#                        break
#                if valid_for_all_years:
#                    in_files[sample_name] = [in_path(y) for y in args.year]
#
#            from HNL.EventSelection.bitCutter import plotCutFlow
#        #    plotCutFlow([in_path], os.path.join(output_dir, 'Yields', 'CutFlow'), [sample_name], ignore_weights=True, output_name = sample_name, subdir = 'nominal')
#        for c in category_dict[args.categoriesToPlot][0]:
#            #plotCutFlow(in_files, os.path.join(output_dir, 'Yields', 'CutFlow', c), ignore_weights=True, output_name = 'all', subdir = 'nominal', categories = category_dict[args.categoriesToPlot][2][c])
#            from HNL.EventSelection.bitCutter import printCutFlow
#            split_output_dir = output_dir.split('/src/')[1]
#            public_output_dir = '/user/lwezenbe/public_html/'+split_output_dir.split('/data/Results/')[0]+'/'+split_output_dir.split('/data/Results/')[1]
#            #printCutFlow(in_files, os.path.join(public_output_dir.rsplit('/', 1)[0], 'Yields', 'CutFlow', c), subdir = 'nominal', categories = category_dict[args.categoriesToPlot][2][c], group_backgrounds=False)
#            #printCutFlow(in_files, os.path.join(public_output_dir.rsplit('/', 1)[0], 'Yields', 'CutFlow', c), subdir = 'nominal', group_backgrounds = False)
#            printCutFlow(in_files, os.path.join(public_output_dir.rsplit('/', 1)[0], 'Yields', 'CutFlow', c), subdir = 'nominal', categories = category_dict[args.categoriesToPlot][2][c])
