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
submission_parser.add_argument('--era',     action='store',       default='prelegacy', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--sample',   action='store',            default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',            default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isTest',   action='store_true',       default=False,  help='Run a small test')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--dryRun',   action='store_true',       default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--genLevel',   action='store_true',     default=False,  help='Use gen level variables')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT', ])
submission_parser.add_argument('--strategy',   action='store', default='MVA',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA'])
submission_parser.add_argument('--analysis',   action='store', default='HNL',  help='Select the strategy to use to separate signal from background', choices=['HNL', 'AN2017014', 'ewkino'])
submission_parser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?')
submission_parser.add_argument('--includeData',   action='store', default=[], nargs='*',  help='Also run over data', choices=['sideband', 'signalregion'])
submission_parser.add_argument('--logLevel',  action='store', default='INFO',  help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])
submission_parser.add_argument('--skimLevel',  action='store', default='auto',  choices=['noskim', 'Reco', 'RecoGeneral', 'auto'])
submission_parser.add_argument('--customList',  action='store',      default=None,               help='Name of a custom sample list. Otherwise it will use the appropriate noskim file.')



argParser.add_argument('--makePlots',   action='store_true',    default=False,  help='Use existing root files to make the plots')
argParser.add_argument('--showCuts',   action='store_true',     default=False,  help='Show what the pt cuts were for the category in the plots')
argParser.add_argument('--groupSamples',   action='store_true', default=False,  help='plot Search Regions')
argParser.add_argument('--makeDataCards', action = 'store_true',  help='Make data cards of the data you have')
argParser.add_argument('--rescaleSignal', type = float,  action='store', default=None,  help='Enter desired signal coupling squared')
argParser.add_argument('--masses', type=float, nargs='*',  help='Only run or plot signal samples with mass given in this list')
argParser.add_argument('--flavor', action='store', default='',  help='Which coupling should be active?' , choices=['tau', 'e', 'mu', '2l', ''])
argParser.add_argument('--signalOnly',   action='store_true',   default=False,  help='Run or plot a only the signal')
argParser.add_argument('--bkgrOnly',   action='store_true',     default=False,  help='Run or plot a only the background')
argParser.add_argument('--plotSingleBin',   action='store_true',     default=False,  help='Run or plot a only the background')
argParser.add_argument('--categoriesToPlot',   action='store',     default='super',  help='What categories to use', choices=['original', 'analysis', 'super'])

args = argParser.parse_args()

from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)

if len(args.includeData) > 0 and args.region == 'NoSelection':
    raise RuntimeError('inData does not work with this selection region')

if len(args.includeData) > 0 and 'signalregion' in args.includeData and args.region in ['baseline', 'highMassSR', 'lowMassSR']:
    raise RuntimeError('These options combined would mean unblinding. This is not allowed.')

if args.strategy == 'MVA':
    if args.selection != 'default':
        raise RuntimeError("No MVA available for this selection")
    if args.genLevel:
        raise RuntimeError("No MVA available for at genLevel")
    if args.region == 'ZZCR':
        raise RuntimeError("No MVA available for 4 lepton selection")

if args.genLevel and args.selection == 'AN2017014':
    raise RuntimeError('gen level is currently not implemented on AN2017014 analysis selection')

#
# General imports
#
import os
from HNL.Tools.histogram import Histogram
from HNL.Tools.mergeFiles import merge
from HNL.Tools.helpers import getObjFromFile, progress, makeDirIfNeeded
from HNL.EventSelection.cutter import Cutter
from HNL.Weights.reweighter import Reweighter
from HNL.TMVA.reader import ReaderArray
from HNL.Samples.sampleManager import SampleManager
from HNL.EventSelection.event import Event
from HNL.Triggers.triggerSelection import passTriggers
from ROOT import TFile
import numpy as np

def getSampleManager(y):
    if args.genLevel or ():
        skim_str = 'noskim'
    elif args.includeData is not None and 'sideband' in args.includeData:
        skim_str = 'Reco'
    else:
        # skim_str = args.skimLevel
        skim_str = 'Reco'
        # skim_str = 'noskim'
    file_list = 'fulllist_'+args.era+str(y) if args.customList is None else args.customList

    sm = SampleManager(args.era, y, skim_str, file_list, skim_selection=args.selection, region=args.region)
    return sm

if args.isTest:
    if args.year is None: args.year = '2017'
    if args.sample is None and not args.makePlots: args.sample = 'DYJetsToLL-M-50'
    args.isChild = True
    if args.subJob is None: args.subJob = '0'
    from HNL.Tools.helpers import generateArgString
    arg_string =  generateArgString(argParser)
else:
    arg_string = None

#
# Prepare jobs
#
jobs = {}
for year in args.year:
    jobs[year] = []
    sample_manager = getSampleManager(year)

    for sample_name in sample_manager.sample_names:
        if len(args.includeData) == 0 and 'Data' in sample_name: continue
        sample = sample_manager.getSample(sample_name)
        if args.sample and args.sample != sample.name: continue
        if not 'Data' in sample_name:
            for njob in xrange(sample.returnSplitJobs()): 
                jobs[year] += [(sample.name, str(njob), None)]
        else:
            for njob in xrange(sample.returnSplitJobs()): 
                for include_data in args.includeData:
                    jobs[year] += [(sample.name, str(njob), include_data)]   

#
# Submit subjobs
#
if not args.isChild and not args.makePlots and not args.makeDataCards:
    from HNL.Tools.jobSubmitter import submitJobs, checkShouldMerge
    # if not args.dryRun and checkShouldMerge(__file__, argParser):
    #     raise RuntimeError("Already existing files available. You would be overwriting")
    for year in jobs.keys():
        submitJobs(__file__, ('sample', 'subJob', 'includeData'), jobs[year], argParser, jobLabel = 'runAnalysis', additionalArgs= [('year', year)])
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

def getOutputName(st, y):
    if not args.isTest:
        return os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 'data', 'runAnalysis', args.analysis, '-'.join([args.strategy, args.selection, args.region, reco_or_gen_str]), args.era+'-'+y, st)
    else:
        return os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 'data', 'testArea', 'runAnalysis', args.analysis, '-'.join([args.strategy, args.selection, args.region, reco_or_gen_str]), args.era+'-'+y, st)

#
# Loop over samples and events
#
if not args.makePlots and not args.makeDataCards:

    if len(args.year) != 1:
        raise RuntimeError("At this point a single year should have been selected")
    year = args.year[0]
    sample_manager = getSampleManager(year)

    #Start a loop over samples
    sample_names = []
    for sample in sample_manager.sample_list:
        if args.sample and sample.name != args.sample: continue
        if sample.name not in sample_manager.sample_names: continue

        chain = sample.initTree(needhcount=False)
        if len(args.includeData) == 0 and chain.is_data: continue

        from ROOT import TTree
        output_tree = TTree('events', 'events')
        branches = []
        for v in var.keys():
            branches.extend(['{0}/F'.format(v)])
        branches.extend(['weight/F', 'isprompt/O', 'category/I', 'searchregion/I'])
        from HNL.Tools.makeBranches import makeBranches
        new_vars = makeBranches(output_tree, branches)

        # list_of_hist = {}
        # if chain.is_data: prompt_string = ['total']
        # else: prompt_string = ['prompt', 'nonprompt', 'total']
        # for c in categories:
        #     list_of_hist[c] = {}
        #     for v in var.keys():
        #         list_of_hist[c][v] = {}
        #         for ps in prompt_string:
        #             list_of_hist[c][v][ps] = Histogram(str(c)+'-'+v+'-'+sample.output+'-'+ps, var[v][0], var[v][2], var[v][1])

        #
        # Load in sample and chain
        #

        sample_names.append(sample.name)
        event = Event(chain, chain, is_reco_level=not args.genLevel, selection=args.selection, strategy=args.strategy, region=args.region, analysis=args.analysis, year = year, era = args.era)

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

        #
        # Skip HNL masses that were not defined
        #
        if args.masses is not None and chain.HNLmass not in args.masses: continue

        #
        # Create cutter to provide cut flow
        #
        cutter = Cutter(chain = chain)

        #
        # Initialize reweighter
        #
        reweighter = Reweighter(sample, sample_manager)

        #
        # Load in MVA reader if needed
        #
        if args.strategy == 'MVA':
            tmva = ReaderArray(chain, 'kBDT', args.region, args.era)

        #
        # Loop over all events
        #
        for entry in event_range:
            
            chain.GetEntry(entry)
            if args.isTest: progress(entry - event_range[0], len(event_range))
 
            cutter.cut(True, 'Total')

            #
            #Triggers
            #
            from HNL.Triggers.triggerSelection import passTriggers
            if not cutter.cut(passTriggers(chain, analysis=args.analysis), 'pass_triggers'): continue
           
            #
            # Event selection
            #
            event.initEvent()

            need_sideband = [0, 1, 2] if chain.is_data and 'sideband' in args.includeData else None
            if not event.passedFilter(cutter, sample.output, sideband = need_sideband, for_training = 'ForTraining' in args.region): continue

            prompt_str = None
            if args.region != 'NoSelection':
                if len(chain.l_flavor) == chain.l_flavor.count(2): continue #Not all taus

                nprompt = 0
                if not 'Data' in sample.name:
                    for index in chain.l_indices:
                        if not args.genLevel and chain._lIsPrompt[index]: nprompt += 1
                        elif args.genLevel and chain._gen_lIsPrompt[index]: nprompt += 1
                    
                    prompt_str = 'prompt' if nprompt == nl else 'nonprompt'
            else:
                prompt_str = None
                chain.category = 17

            if args.strategy == 'MVA':
                tmva.predictAndWriteAll(chain)

            #
            # Fill tree
            #
            for v in var.keys():
                setattr(new_vars, v, var[v][0](chain))
            new_vars.weight = reweighter.getTotalWeight(sideband='sideband' in args.includeData)
            new_vars.isprompt = prompt_str == 'prompt'
            new_vars.category = chain.category
            new_vars.searchregion = srm[args.region].getSearchRegion(chain)
            output_tree.Fill()

 
        #
        # Save histograms
        #
        subjobAppendix = '_subJob' + args.subJob if args.subJob else ''
        
        is_signal = 'HNL' in sample.name
        if len(args.includeData) > 0 and chain.is_data:
            signal_str = 'data'
            sample_output_name = sample.output +'-'+args.includeData[0] if len(args.includeData) == 1 else None
        else:
            signal_str = 'signal' if is_signal else 'bkgr'
            sample_output_name = sample.output


        if args.signalOnly and args.genLevel:       output_name_full = os.path.join(getOutputName(signal_str, year), 'signalOrdering', sample_output_name)
        else:      output_name_full = os.path.join(getOutputName(signal_str, year), sample_output_name) 


        if args.isChild:
            output_name_full += '/tmp_'+sample_output_name+ '/'+sample.name+'_'
        else:
            output_name_full += '/'
                
        if len(args.includeData) > 0 and chain.is_data: writename = 'variables-'+args.includeData[0]
        else: writename = 'variables'

        from HNL.Tools.helpers import makeDirIfNeeded
        makeDirIfNeeded(output_name_full +writename+subjobAppendix+ '.root')
        out_file = TFile(output_name_full +writename+subjobAppendix+ '.root', 'recreate')
        output_tree.Write()
        out_file.Write()
        out_file.Close()

        cutter.saveCutFlow(output_name_full +writename+subjobAppendix+ '.root')

    closeLogger(log)

#If the option to not run over the events again is made, load in the already created histograms here
else:
    from ROOT import gROOT
    gROOT.SetBatch(True)
    import glob
    from HNL.Analysis.analysisTypes import signal_couplingsquared, signal_couplingsquaredinsample
    from HNL.Tools.helpers import getHistFromTree

    for year in args.year:
        print 'Processing ', year

        sample_manager = getSampleManager(year)
            
        if not args.bkgrOnly:
            signal_list = [s for s in glob.glob(getOutputName('signal', year)+'/*'+args.flavor+'-*') if s.split('/')[-1] in sample_manager.sample_outputs]
            for i, s in enumerate(signal_list):
                if 'signalOrdering' in s:
                    signal_list.pop(i)
        else:
            signal_list = []

        # Collect background file locations
        if not args.signalOnly:
            bkgr_list = [getOutputName('bkgr', year)+'/'+b for b in sample_manager.sample_outputs]
            bkgr_list = [b for b in glob.glob(getOutputName('bkgr', year)+'/*') if b.split('/')[-1] in sample_manager.sample_outputs]
        else:
            bkgr_list = []

        # data
        if len(args.includeData) > 0:
            data_list = glob.glob(getOutputName('data', year)+'/Data*')
        else:
            data_list = []

        print 'check merge'
        # Merge files if necessary
        mixed_list = signal_list + bkgr_list + data_list
        merge(mixed_list, __file__, jobs[year], ('sample', 'subJob', 'includeData'), argParser, istest=args.isTest, additionalArgs= [('year', year)])

        if args.groupSamples:
            background_collection = sample_manager.sample_groups.keys()+['non-prompt']
        else:
            background_collection = [b.split('/')[-1] for b in bkgr_list]

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
        for i_b, b in enumerate(bkgr_list):
            sample_name = b.split('/')[-1]
            if args.sample is not None and args.sample != sample_name:      continue
            if sample_name not in sample_manager.sample_outputs:              continue 
            tmp_bkgr_list.append(b) 

        signal_list = [x for x in tmp_signal_list]
        bkgr_list = [x for x in tmp_bkgr_list]

        #Reset list_of_hist
        category_dict = {
            'original' : ([x for x in categories], ['(category=={0})'.format(x) for x in categories]),
            'analysis': (cat.ANALYSIS_CATEGORIES.keys(), ['('+'||'.join(['category=={0}'.format(x) for x in cat.ANALYSIS_CATEGORIES[y]])+')' for y in cat.ANALYSIS_CATEGORIES.keys()]),
            'super' : (cat.SUPER_CATEGORIES.keys(), ['('+'||'.join(['category=={0}'.format(x) for x in cat.SUPER_CATEGORIES[y]])+')' for y in cat.SUPER_CATEGORIES.keys()])
        } 
        
        #Add entry for the search regions in the var dictionary
        var['searchregion'] = (lambda c : c.searchregion, np.arange(0.5, srm[args.region].getNumberOfSearchRegions()+1.5, 1.), ('Search Region', 'Events'))

        #
        # Create variable distributions
        #

        def createVariableDistributions(categories_dict, var_dict, signal, background, data):
            categories_to_use = categories_dict[0]
            category_conditions = categories_dict[1]

            tmp_list_of_hist = {}
            for c in categories_to_use:
                tmp_list_of_hist[c] = {}
                for v in var_dict:
                    tmp_list_of_hist[c][v] = {'signal':{}, 'bkgr':{}, 'data':{}}

            # Load in the signal histograms from the files
            if not args.bkgrOnly:
                for s in signal_list:
                    infile = TFile(s+'/variables.root', 'read')
                    intree = infile.Get('events')
                    sample_name = s.split('/')[-1]
                    sample_mass = float(sample_name.split('-m')[-1])

                    for c, cc in zip(categories_to_use, category_conditions): 
                        print 'loading signal ', c
                        for v in var_dict.keys():
                            tmp_list_of_hist[c][v]['signal'][sample_name] = Histogram(getHistFromTree(intree, v, str(c)+'-'+v+'-'+sample_name, var_dict[v][1], cc))

                            coupling_squared = args.rescaleSignal if args.rescaleSignal is not None else signal_couplingsquared[args.flavor][sample_mass]
                            tmp_list_of_hist[c][v]['signal'][sample_name].hist.Scale(coupling_squared/signal_couplingsquaredinsample[args.flavor][sample_mass])

                            # if args.rescaleSignal is not None:
                            #    tmp_list_of_hist[c][v]['signal'][sample_name].hist.Scale(args.rescaleSignal/(args.coupling**2))
                    infile.Close()

            if len(args.includeData) > 0:
                for c, cc in zip(categories_to_use, category_conditions):
                    for v in var_dict:
                        if 'sideband' in args.includeData: 
                            infile = TFile(data_list[0]+'/variables-sideband.root', 'read')
                            intree = infile.Get('events')
                            tmp_list_of_hist[c][v]['data']['sideband'] = Histogram(getHistFromTree(intree, v, str(c)+'-'+v+'-'+'-Data-sideband', var_dict[v][1], cc))
                            infile.Close()
                        if 'signalregion' in args.includeData: 
                            infile = TFile(data_list[0]+'/variables-signalregion.root', 'read')
                            intree = infile.Get('events')
                            tmp_list_of_hist[c][v]['data']['signalregion'] = Histogram(getHistFromTree(intree, v, str(c)+'-'+v+'-'+'-Data-signalregion', var_dict[v][1], cc))
                            infile.Close()


            if not args.signalOnly:
                for c in categories_to_use: 
                    for v in var_dict.keys():   
                        for b in background_collection:
                            tmp_list_of_hist[c][v]['bkgr'][b] = Histogram(b+v+str(c), var_dict[v][0], var_dict[v][2], var_dict[v][1])

                for b in bkgr_list:
                    bkgr = b.split('/')[-1]
                    if 'QCD' in bkgr: continue
                    infile = TFile(b+'/variables.root', 'read')
                    intree = infile.Get('events') 
                    for c, cc in zip(categories_to_use, category_conditions):
                        for iv, v in enumerate(var_dict.keys()):  

                            if args.groupSamples:
                                sg = [sk for sk in sample_manager.sample_groups.keys() if bkgr in sample_manager.sample_groups[sk]]
                                if len(sg) == 0:
                                    if c == 1 and iv == 0: print bkgr, "not part of any sample group"
                                    continue
                                tmp_hist = Histogram(getHistFromTree(intree, v, 'tmp_'+bkgr+v+str(c)+'p', var_dict[v][1], '('+cc+'&&isprompt)'))
                                tmp_list_of_hist[c][v]['bkgr'][sg[0]].add(tmp_hist)
                                del(tmp_hist)

                                if len(args.includeData) == 0 or 'sideband' not in args.includeData:
                                    tmp_hist = Histogram(getHistFromTree(intree, v, 'tmp_'+bkgr+v+str(c)+'np', var_dict[v][1], '('+cc+'&&!isprompt)'))
                                    tmp_list_of_hist[c][v]['bkgr']['non-prompt'].add(tmp_hist)
                                    del(tmp_hist)
                            else:
                                tmp_hist = Histogram(getHistFromTree(intree, v, 'tmp_'+bkgr+v+str(c)+'t', var_dict[v][1], cc))
                                tmp_list_of_hist[c][v]['bkgr'][bkgr].add(tmp_hist)
                                del(tmp_hist)
                    infile.Close()

                for c, cc in zip(categories_to_use, category_conditions):
                    for iv, v in enumerate(var_dict.keys()):
                        if len(args.includeData) > 0 and 'sideband' in args.includeData:
                            tmp_list_of_hist[c][v]['bkgr']['non-prompt'].add(list_of_hist[c][v]['data']['sideband'])

            return tmp_list_of_hist

        list_of_hist = createVariableDistributions(category_dict[args.categoriesToPlot], var, signal_list, bkgr_list, data_list)

        #
        #       Plot!
        #

        #
        # Necessary imports
        #
        from HNL.Plotting.plot import Plot
        from HNL.Plotting.plottingTools import extraTextFormat
        from HNL.Tools.helpers import makePathTimeStamped
        from HNL.TMVA.mvaVariables import getNameFromMass


        if args.makeDataCards:
            from HNL.Stat.combineTools import makeDataCard

            #
            # If we want to use shapes, first make shape histograms, then make datacards
            #
            for ac in cat.SUPER_CATEGORIES.keys():
                # # Observed
                # shape_hist['data_obs'] = TH1D('data_obs', 'data_obs', n_search_regions, 0.5, n_search_regions+0.5)
                # shape_hist['data_obs'].SetBinContent(1, 1.)

                # # Background
                # for sample_name in sample_manager.sample_groups.keys():
                #     shape_hist[sample_name] = TH1D(sample_name, sample_name, n_search_regions, 0.5, n_search_regions+0.5)
                #     for sr in xrange(1, n_search_regions+1):
                #         shape_hist[sample_name].SetBinContent(sr, list_of_values['bkgr'][sample_name][ac][sr])
                #         shape_hist[sample_name].SetBinError(sr, list_of_errors['bkgr'][sample_name][ac][sr])
                
                # Signal 
                for s in signal_list:
                    sample_name = s.split('/')[-1]
                    sample_mass = float(sample_name.split('-m')[-1])
                    if sample_mass not in args.masses: continue

                    if args.strategy == 'MVA':
                        variable_to_use = getNameFromMass(sample_mass)+'-'+args.flavor
                    elif args.strategy == 'cutbased':
                        variable_to_use = 'searchregion'
                    else:
                        raise RuntimeError('Unknown strategy: {0}'.format(args.strategy))

                    mva_to_use = getNameFromMass(sample_mass)+'-'+args.flavor
                    out_path = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'shapes', '-'.join([args.strategy, args.selection, args.region]), 
                                            args.era+str(year), args.flavor, sample_name, ac+'.shapes.root')
                    makeDirIfNeeded(out_path)
                    # out_shape_file = ROOT.TFile(out_path, 'recreate')
                    list_of_hist[ac][mva_to_use]['signal'][sample_name].write(out_path, write_name=sample_name)
                    # out_shape_file.Close()
                    bkgr_names = []
                    for ib, b in enumerate(background_collection):
                        bkgr_name = b.split('/')[-1]
                        # if bkgr_name == 'WZ' or bkgr_name == 'XG': continue
                        if list_of_hist[ac][mva_to_use]['bkgr'][bkgr_name].hist.GetSumOfWeights() > 0:
                            list_of_hist[ac][mva_to_use]['bkgr'][bkgr_name].write(out_path, write_name=bkgr_name, append=True)
                            bkgr_names.append(bkgr_name)
                    
                    data_hist_tmp = list_of_hist[ac][mva_to_use]['signal'][sample_name].clone('Ditau')
                    data_hist_tmp.write(out_path, write_name='data_obs', append=True)
                    
                    makeDataCard(str(ac), args.flavor, args.era, year, 0, sample_name, bkgr_names, args.selection, args.strategy, args.region, shapes=True, coupling_sq = coupling_squared)

        if args.makePlots:

            #
            # Set output directory, taking into account the different options
            #
            if not args.isTest:
                output_dir = os.path.join(os.getcwd(), 'data', 'Results', 'runAnalysis', args.analysis, '-'.join([args.strategy, args.selection, args.region]), args.era+str(year))
            else:
                output_dir = os.path.join(os.getcwd(), 'data', 'testArea', 'Results', 'runAnalysis', args.analysis, '-'.join([args.strategy, args.selection, args.region]), args.era+str(year))



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
            for c in cat.SUPER_CATEGORIES.keys():
                c_name = CATEGORY_NAMES[c] if c not in cat.SUPER_CATEGORIES.keys() else c

                extra_text = [extraTextFormat(c_name, xpos = 0.2, ypos = 0.82, textsize = None, align = 12)]  #Text to display event type in plot
        
                # Plots that display chosen for chosen signal masses and backgrounds the distributions for the different variables
                # S and B in same canvas for each variable
                for v in var.keys():
                    bkgr_legendnames = []
                    # Make list of background histograms for the plot object (or None if no background)
                    if args.signalOnly or not list_of_hist[c][v]['bkgr'].values(): 
                        bkgr_hist = None
                    else:
                        bkgr_hist = []
                        for bk in list_of_hist[c][v]['bkgr'].keys():
                            bkgr_hist.append(list_of_hist[c][v]['bkgr'][bk])
                            bkgr_legendnames.append(bk)
                
                    # Make list of signal histograms for the plot object
                    signal_legendnames = []
                    if args.bkgrOnly or not list_of_hist[c][v]['signal'].values(): 
                        signal_hist = None
                    else:
                        for sk in list_of_hist[c][v]['signal'].keys():
                            signal_hist = list_of_hist[c][v]['signal'].values()
                            # if 'filtered' in sk:
                            #     signal_legendnames.append('HNL m_{N} = 30 GeV w Pythia filter')
                            # else:
                            # signal_legendnames.append('HNL '+ sk.split('-')[1] +' m_{N} = '+sk.split('-m')[-1]+ ' GeV')
                            if not args.rescaleSignal:
                                signal_legendnames.append('#splitline{HNL m_{N}='+sk.split('-m')[-1]+ 'GeV}{V^{2}='+str(signal_couplingsquaredinsample[sk.split('-')[1]][int(sk.split('-m')[-1])])+'}')
                            else:
                                signal_legendnames.append('HNL m_{N}='+sk.split('-m')[-1]+ 'GeV')

                    if len(args.includeData) > 0 and 'signalregion' in args.includeData:
                        observed_hist = list_of_hist[c][v]['data']['signalregion']
                    else:
                        observed_hist = None

                    if not args.signalOnly and not args.bkgrOnly:
                        legend_names = signal_legendnames+bkgr_legendnames
                    elif args.signalOnly:
                        legend_names = signal_legendnames
                    else:
                        legend_names = bkgr_legendnames

                    #Create specialized signal region plots if this is the correct variable
                    if v == 'searchregion' and args.region in ['lowMassSR', 'highMassSR']:
                        extra_text = [extraTextFormat(c, ypos = 0.82)]
                        from decimal import Decimal
                        from HNL.EventSelection.searchRegions import plotLowMassRegions, plotHighMassRegions
                        if args.flavor: 
                            extra_text.append(extraTextFormat('|V_{'+args.flavor+'N}|^{2} = '+'%.0E' % Decimal(str(0.01**2)), textsize = 0.7))
                        if args.rescaleSignal is not None:
                            extra_text.append(extraTextFormat('rescaled to |V_{'+args.flavor+'N}|^{2} = '+'%.0E' % Decimal(str(args.rescaleSignal)), textsize = 0.7))
                        # else:
                        #     signal_names = [s + ' V^{2}=' + str(signal_couplingsquared[s.split('-')[1]][int(s.split('-m')[-1])])  for s in signal_names]
                            
                        if args.region == 'lowMassSR':
                            plotLowMassRegions(signal_hist, bkgr_hist, legend_names, 
                                out_path = os.path.join(output_dir, 'Yields', 'SearchRegions', c), extra_text = extra_text, sample_groups = args.groupSamples)
                        if args.region == 'highMassSR':
                            plotHighMassRegions(signal_hist, bkgr_hist, legend_names, 
                                out_path = os.path.join(output_dir, 'Yields', 'SearchRegions', c), extra_text = extra_text, sample_groups = args.groupSamples)

                    else:

                        # Create plot object (if signal and background are displayed, also show the ratio)
                        draw_ratio = None if args.signalOnly or args.bkgrOnly else True
                        if 'signalregion' in args.includeData: draw_ratio = True
                        if args.groupSamples:
                            # p = Plot(signal_hist, legend_names, c_name+'-'+v, bkgr_hist = bkgr_hist, observed_hist = observed_hist, y_log = True, extra_text = extra_text, draw_ratio = draw_ratio, year = year, era=args.era,
                            #         color_palette = 'Didar', color_palette_bkgr = 'AN2017')
                            p = Plot(signal_hist, legend_names, c_name+'-'+v, bkgr_hist = bkgr_hist, observed_hist = observed_hist, y_log = False, extra_text = extra_text, draw_ratio = draw_ratio, year = year, era=args.era,
                                    color_palette = 'Didar', color_palette_bkgr = 'AN2017')
                        else:
                            p = Plot(signal_hist, legend_names, c_name+'-'+v, bkgr_hist = bkgr_hist, observed_hist = observed_hist, y_log = False, extra_text = extra_text, draw_ratio = draw_ratio, year = year, era=args.era,
                                    color_palette = 'Didar')


                        # Draw
                        p.drawHist(output_dir = os.path.join(output_dir, 'Variables' if v != 'searchregion' else 'Yields/SearchRegions', c_name), normalize_signal = True, draw_option='EHist', min_cutoff = 1)
                        # p.drawHist(output_dir = os.path.join(output_dir, c_name), normalize_signal = False, draw_option='EHist', min_cutoff = 1)

            #
            # Bar charts
            #

            from HNL.EventSelection.eventCategorization import CATEGORY_TEX_NAMES
            from ROOT import TH1D
            grouped_categories = cat.SUPER_CATEGORIES

            print "Making Bar Charts"
            list_of_hist_forbar = createVariableDistributions(category_dict['original'], {'searchregion' : var['searchregion']}, signal_list, bkgr_list, data_list)
            signal_names = [s.split('/')[-1] for s in signal_list]
            for supercat in grouped_categories.keys():
                #
                # Bkgr
                #
                if not args.signalOnly:
                    hist_to_plot = {}
                    for sample_name in background_collection:
                        hist_to_plot[sample_name] = TH1D(sample_name+supercat, sample_name+supercat, len(grouped_categories[supercat]), 0, len(grouped_categories[supercat]))
                        for i, c in enumerate(grouped_categories[supercat]):
                            hist_to_plot[sample_name].SetBinContent(i+1, list_of_hist_forbar[c]['searchregion']['bkgr'][sample_name].getHist().GetSumOfWeights()) 

                    x_names = [CATEGORY_TEX_NAMES[n] for n in grouped_categories[supercat]]
                    p = Plot(hist_to_plot.values(), hist_to_plot.keys(), name = 'Events-bar-bkgr-'+supercat, x_name = x_names, y_name = 'Events', y_log='SingleTau' in supercat)            
                    p.drawBarChart(output_dir = os.path.join(output_dir, 'Yields', 'BarCharts'))
                
                #
                # Signal
                #   
                if not args.bkgrOnly:
                    hist_to_plot = []
                    hist_names = []
                    for sn, sample_name in enumerate(sorted(signal_names, key=lambda k: int(k.split('-m')[-1]))):
                        hist_to_plot.append(TH1D(sample_name, sample_name, len(grouped_categories[supercat]), 0, len(grouped_categories[supercat])))
                        hist_names.append(sample_name)
                        for i, c in enumerate(grouped_categories[supercat]):
                            hist_to_plot[sn].SetBinContent(i+1, list_of_hist_forbar[c]['searchregion']['signal'][sample_name].getHist().GetSumOfWeights()) 
                    x_names = [CATEGORY_TEX_NAMES[n] for n in grouped_categories[supercat]]
                    p = Plot(hist_to_plot, hist_names, name = 'Events-bar-signal-'+supercat+'-'+args.flavor, x_name = x_names, y_name = 'Events', y_log=True)
                    p.drawBarChart(output_dir = os.path.join(output_dir, 'Yields', 'BarCharts'), parallel_bins=True)
            
            print "making Pie Charts"
            example_sample = background_collection[0]
            for i, c in enumerate(sorted(category_dict[args.categoriesToPlot][0])):

                n_filled_hist = len([v for v in background_collection if list_of_hist[c]['searchregion']['bkgr'][v].getHist().GetSumOfWeights() > 0])    #Remove hist with 0 events, they will otherwise crash the plotting code
                if n_filled_hist == 0: continue
                hist_to_plot_pie = TH1D(str(c)+'_pie', str(c), n_filled_hist, 0, n_filled_hist)
                sample_names = []
                j = 1
                for s in background_collection:
                    fill_val = list_of_hist[c]['searchregion']['bkgr'][s].getHist().GetSumOfWeights()
                    if fill_val > 0:
                        hist_to_plot_pie.SetBinContent(j, fill_val)
                        sample_names.append(s)
                        j += 1

                try:
                    extra_text = [extraTextFormat(str(c), ypos = 0.83)] if c is not None else None
                except:
                    extra_text = [extraTextFormat('other', ypos = 0.83)] if c is not None else None
                x_names = CATEGORY_TEX_NAMES.values()
                x_names.append('total')
                p = Plot(hist_to_plot_pie, sample_names, name = 'Events_'+str(c), x_name = CATEGORY_TEX_NAMES, y_name = 'Events', extra_text = extra_text)
                p.drawPieChart(output_dir = os.path.join(output_dir, 'Yields', 'PieCharts'), draw_percent=True)

            print "plotting cutflow"
            for sample_name in sample_manager.sample_outputs:
                in_file = [getOutputName('signal' if 'HNL' in sample_name else 'bkgr', year)+'/'+sample_name+'/variables.root']
                from HNL.Tools.helpers import isValidRootFile
                if not isValidRootFile(in_file[0]): continue
                name = [sample_name]

                # all_files = sorted(all_files, key = lambda k : int(k.split('/')[-2].split('.')[0].split('-m')[-1]))
                # all_names = [k.split('/')[-1].split('.')[0] for k in all_files]

                from HNL.EventSelection.cutter import plotCutFlow
                plotCutFlow(in_file, os.path.join(output_dir, 'Yields', 'CutFlow'), name, ignore_weights=True, output_name = name[0])
