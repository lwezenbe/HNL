#! /usr/bin/env python

#########################################################################
#                                                                       #
#   Code to plot basic variables that are already contained in a tree   # 
#   that was skimmed for baseline events                                #
#                                                                       #                                   
#########################################################################


#
# Argument parser and logging
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true',       default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store',            default=None,   help='Select year', choices=['2016', '2017', '2018', 'all'], required=True)
submission_parser.add_argument('--sample',   action='store',            default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',            default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isTest',   action='store_true',       default=False,  help='Run a small test')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--dryRun',   action='store_true',       default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--genLevel',   action='store_true',     default=False,  help='Use gen level variables')
submission_parser.add_argument('--coupling', action='store', default=0.01, type=float,  help='How large is the coupling?')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT', ])
submission_parser.add_argument('--strategy',   action='store', default='MVA',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA'])
submission_parser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?')
submission_parser.add_argument('--includeData',   action='store', default=[], nargs='*',  help='Also run over data', choices=['sideband', 'signalregion'])
submission_parser.add_argument('--logLevel',  action='store', default='INFO',  help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])
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


args = argParser.parse_args()


from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)

if len(args.includeData) > 0 and args.region == 'NoSelection':
    raise RuntimeError('inData does not work with this selection region')

if len(args.includeData) > 0 and 'signalregion' in args.includeData and args.region in ['baseline', 'highMassSR', 'lowMassSR']:
    raise RuntimeError('These options combined would mean unblinding. This is not allowed.')

if args.makeDataCards and args.strategy != 'MVA': 
    raise RuntimeError("makeDataCards here is not supported for anything that is not MVA. Please use calcYields for this."+ 
                            "The eventual plan is to merge calcYields and plotVariables into 1 but for now they are separated")

if args.strategy == 'MVA':
    if args.selection != 'default':
        raise RuntimeError("No MVA available for this selection")
    if args.genLevel:
        raise RuntimeError("No MVA available for at genLevel")
    if args.region == 'ZZCR':
        raise RuntimeError("No MVA available for 4 lepton selection")

#
# General imports
#
import os
from HNL.Tools.histogram import Histogram
from HNL.Tools.mergeFiles import merge
from HNL.Tools.helpers import getObjFromFile, progress, makeDirIfNeeded
from HNL.EventSelection.cutter import Cutter
from HNL.Weights.reweighter import Reweighter
from HNL.TMVA.reader import Reader, listAvailableMVAs
from HNL.Samples.sampleManager import SampleManager
from HNL.EventSelection.event import Event

def getSampleManager(y):
    if args.genLevel:
        skim_str = 'noskim'
    elif args.selection != 'default':
        skim_str = 'noskim'
    elif args.region in ['highMassSR', 'lowMassSR']:
        skim_str = 'RecoGeneral'
    else:
        skim_str = 'Reco'
    file_list = 'fulllist_'+str(y) if args.customList is None else args.customList

    if skim_str == 'RecoGeneral':
        sm = SampleManager(y, skim_str, file_list, skim_selection=args.selection, region=args.region)
    else:
        sm = SampleManager(y, skim_str, file_list)
    return sm

if args.isTest:
    if args.year is None: args.year = '2016'
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
for year in ['2016', '2017', '2018']:
    if args.year != 'all' and year != args.year: 
        continue
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
    from HNL.Tools.jobSubmitter import submitJobs
    for year in jobs.keys():
        submitJobs(__file__, ('sample', 'subJob', 'includeData'), jobs[year], argParser, jobLabel = 'plotVar', additionalArgs= [('year', year)])
    exit(0)


#
# Some constants to make referring to signal leptons more readable
#
l1 = 0
l2 = 1
l3 = 2
l4 = 3

nl = 3 if args.region != 'ZZCR' else 4

#
# Create histograms
#
import HNL.Analysis.analysisTypes as at
if args.makeDataCards and not args.makePlots:
    var = at.var_mva
elif args.region == 'NoSelection':
    var = at.var_noselection
else:
    var = at.returnVariables(nl, not args.genLevel, args.strategy == 'MVA')
    # var = at.var_mva

import HNL.EventSelection.eventCategorization as cat
def listOfCategories(region):
    if nl == 3:
        return cat.CATEGORIES
    else:
        return [max(cat.CATEGORIES)]

categories = listOfCategories(args.region)
reco_or_gen_str = 'reco' if not args.genLevel else 'gen'

def getOutputName(st, y):
    if not args.isTest:
        return os.path.join(os.getcwd(), 'data', 'plotVariables', '-'.join([args.strategy, args.selection, args.region, reco_or_gen_str]), y, st)
    else:
        return os.path.join(os.getcwd(), 'data', 'testArea', 'plotVariables', '-'.join([args.strategy, args.selection, args.region, reco_or_gen_str]), y, st)

#
# Load in the sample list 
#
if args.genLevel and args.selection == 'AN2017014':
    raise RuntimeError('gen level is currently not implemented on AN2017014 analysis selection')

from HNL.Triggers.triggerSelection import passTriggers
#
# Loop over samples and events
#
if not args.makePlots and not args.makeDataCards:

    sample_manager = getSampleManager(args.year)

    #Start a loop over samples
    sample_names = []
    for sample in sample_manager.sample_list:
        if sample.name not in sample_manager.sample_names: continue
        if sample.name != args.sample: continue
        if args.sample and sample.name != args.sample: continue

        chain = sample.initTree(needhcount=False)
        if len(args.includeData) == 0 and chain.is_data: continue

        list_of_hist = {}
        if chain.is_data: prompt_string = ['total']
        else: prompt_string = ['prompt', 'nonprompt', 'total']
        for c in categories:
            list_of_hist[c] = {}
            for v in var.keys():
                list_of_hist[c][v] = {}
                for ps in prompt_string:
                    list_of_hist[c][v][ps] = Histogram(str(c)+'-'+v+'-'+sample.output+'-'+ps, var[v][0], var[v][2], var[v][1])

        #
        # Load in sample and chain
        #

        sample_names.append(sample.name)
        event = Event(chain, chain, is_reco_level=not args.genLevel, selection=args.selection, strategy=args.strategy, region=args.region)


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
        # Some basic variables about the sample to store in the chain
        #
        chain.HNLmass = sample.getMass()
        chain.year = int(args.year)

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
            tmva = {}
            for sel in ['lowMassSR', 'highMassSR']:
                tmva[sel] = {}
                for n in listAvailableMVAs():
                    try:
                        tmva[sel][n] = Reader(chain, 'kBDT', n, sel)
                    except:
                        print 'Error when trying to load in BDT with {0} selection for name {1}'.format(sel, n)

        #
        # Loop over all events
        #
        for entry in event_range:
            
            chain.GetEntry(entry)
            progress(entry - event_range[0], len(event_range))
 
            cutter.cut(True, 'Total')

            #
            #Triggers
            #
            if args.selection == 'AN2017014':
                if not cutter.cut(passTriggers(chain, analysis='HNL_old'), 'pass_triggers'): continue
           
            #
            # Event selection
            #
            event.initEvent()

            need_sideband = [0, 1, 2] if chain.is_data and 'sideband' in args.includeData else None
            if not event.passedFilter(cutter, sample.output, sideband = need_sideband): continue
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
                chain.mva_high_mu_lowMassSR = tmva['lowMassSR']['high_mu'].predict()
                chain.mva_low_mu_lowMassSR = tmva['lowMassSR']['low_mu'].predict()
                chain.mva_high_tau_lowMassSR = tmva['lowMassSR']['high_tau'].predict()
                chain.mva_low_tau_lowMassSR = tmva['lowMassSR']['low_tau'].predict()
                chain.mva_low_e_lowMassSR = tmva['lowMassSR']['low_e'].predict()
                chain.mva_high_e_lowMassSR = tmva['lowMassSR']['high_e'].predict()
                chain.mva_high_mu_highMassSR = tmva['highMassSR']['high_mu'].predict()
                chain.mva_low_mu_highMassSR = tmva['highMassSR']['low_mu'].predict()
                chain.mva_high_tau_highMassSR = tmva['highMassSR']['high_tau'].predict()
                chain.mva_low_tau_highMassSR = tmva['highMassSR']['low_tau'].predict()
                chain.mva_low_e_highMassSR = tmva['highMassSR']['low_e'].predict()
                chain.mva_high_e_highMassSR = tmva['highMassSR']['high_e'].predict()

            #
            # Fill the histograms
            #
            weight = reweighter.getTotalWeight()
            for v in var.keys():
                if prompt_str is not None: list_of_hist[chain.category][v][prompt_str].fill(chain, reweighter.getTotalWeight(sideband='sideband' in args.includeData))  
                list_of_hist[chain.category][v]['total'].fill(chain, reweighter.getTotalWeight(sideband='sideband' in args.includeData))  
 
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


        if args.signalOnly and args.genLevel:       output_name_full = os.path.join(getOutputName(signal_str, args.year), 'signalOrdering', sample_output_name)
        else:      output_name_full = os.path.join(getOutputName(signal_str, args.year), sample_output_name) 


        if args.isChild:
            output_name_full += '/tmp_'+sample_output_name+ '/'+sample.name+'_'
        else:
            output_name_full += '/'
                
        if len(args.includeData) > 0 and chain.is_data: writename = 'variables-'+args.includeData
        else: writename = 'variables'

        for iv, v in enumerate(var.keys()):
            for ic, c in enumerate(categories):
                for ip, prompt_str in enumerate(list_of_hist[c][v].keys()):
                    if iv == 0 and ic == 0 and ip == 0:
                        list_of_hist[c][v][prompt_str].write(output_name_full +writename+subjobAppendix+ '.root', subdirs=[v], is_test=arg_string)
                    else:
                        list_of_hist[c][v][prompt_str].write(output_name_full +writename+subjobAppendix+ '.root', subdirs=[v], append=True, is_test=arg_string)

        cutter.saveCutFlow(output_name_full +writename+subjobAppendix+ '.root')

    closeLogger(log)

#If the option to not run over the events again is made, load in the already created histograms here
else:
    import glob
    from HNL.Analysis.analysisTypes import signal_couplingsquared

    for year in ['2016', '2017', '2018']:
        print 'Processing ', year
        if args.year != 'all' and year != args.year: continue

        sample_manager = getSampleManager(year)
        # Collect signal file locations
        # if args.genLevel and args.signalOnly:
        #     signal_list = glob.glob(getOutputName('signal', year)+'/signalOrdering/*')
            
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
            data_list = glob.glob(getOutputName('data', year)+'/Data')
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
        list_of_hist = {}
        for c in categories:
            list_of_hist[c] = {}
            for v in var:
                list_of_hist[c][v] = {'signal':{}, 'bkgr':{}, 'data':{}}

        # Load in the signal histograms from the files
        for c in categories: 
            print 'loading signal ', c
            for v in var.keys():
                if not args.bkgrOnly:
                    for s in signal_list:
                        sample_name = s.split('/')[-1]

                        sample_mass = float(sample_name.split('-m')[-1])
                        list_of_hist[c][v]['signal'][sample_name] = Histogram(getObjFromFile(s+'/variables.root', v+'/'+str(c)+'-'+v+'-'+sample_name+'-total')) 

                        coupling_squared = args.rescaleSignal if args.rescaleSignal is not None else signal_couplingsquared[args.flavor][sample_mass]
                        list_of_hist[c][v]['signal'][sample_name].hist.Scale(coupling_squared/(args.coupling**2))

                        # if args.rescaleSignal is not None:
                        #    list_of_hist[c][v]['signal'][sample_name].hist.Scale(args.rescaleSignal/(args.coupling**2))


        if len(args.includeData) > 0:
            for c in categories:
                for v in var:
                    list_of_hist[c][v]['data']['sideband'] = Histogram(getObjFromFile(data_list[0]+'/variables.root', v+'/'+str(c)+'-'+v+'-'+'Data-total'))
                    list_of_hist[c][v]['data']['signalregion'] = Histogram(getObjFromFile(data_list[0]+'/variables.root', v+'/'+str(c)+'-'+v+'-'+'Data-total'))

        for c in categories: 
            print 'loading', c
            for v in var.keys():   
                if not args.signalOnly:
                    for b in background_collection:
                        list_of_hist[c][v]['bkgr'][b] = Histogram(b+v+str(c), var[v][0], var[v][2], var[v][1])

        for ic, c in enumerate(categories): 
            print 'loading', c
            for iv, v in enumerate(var.keys()):   
                if not args.signalOnly:
                    for b in bkgr_list:
                        bkgr = b.split('/')[-1]
                        if 'QCD' in bkgr: continue

                        tmp_hist_total = Histogram(getObjFromFile(b+'/variables.root', v+'/'+str(c)+'-'+v+'-'+bkgr+'-total'))
                        tmp_hist_prompt = Histogram(getObjFromFile(b+'/variables.root', v+'/'+str(c)+'-'+v+'-'+bkgr+'-prompt'))
                        tmp_hist_nonprompt = Histogram(getObjFromFile(b+'/variables.root', v+'/'+str(c)+'-'+v+'-'+bkgr+'-nonprompt'))

                        if args.groupSamples:
                            sg = [sk for sk in sample_manager.sample_groups.keys() if bkgr in sample_manager.sample_groups[sk]]
                            if len(sg) == 0:
                                if c == 1 and iv == 0: print bkgr, "not part of any sample group"
                                continue
                            list_of_hist[c][v]['bkgr'][sg[0]].add(tmp_hist_prompt)
                            if len(args.includeData) == 0 or 'sideband' not in args.includeData:
                                list_of_hist[c][v]['bkgr']['non-prompt'].add(tmp_hist_nonprompt)
                        else:
                            list_of_hist[c][v]['bkgr'][bkgr].add(tmp_hist_total)

                        del(tmp_hist_total)
                        del(tmp_hist_prompt)
                        del(tmp_hist_nonprompt)

                    if len(args.includeData) > 0 and 'sideband' in args.includeData:
                        list_of_hist[c][v]['bkgr']['non-prompt'].add(list_of_hist[c][v]['data']['sideband'])


        if args.region in ['baseline', 'lowMassSR', 'highMassSR']:
            for ac in cat.ANALYSIS_CATEGORIES.keys():
                list_of_hist[ac] = {}
                for v in var.keys():
                    list_of_hist[ac][v] = {}
                    if not args.bkgrOnly:
                        list_of_hist[ac][v]['signal'] = {}
                        for s in signal_list:
                            sample_name = s.split('/')[-1]
                            sample_mass = float(sample_name.split('-m')[-1])
                            list_of_hist[ac][v]['signal'][sample_name] = list_of_hist[cat.ANALYSIS_CATEGORIES[ac][0]][v]['signal'][sample_name].clone(ac)
                            if len(cat.ANALYSIS_CATEGORIES[ac]) > 1:
                                for c in cat.ANALYSIS_CATEGORIES[ac][1:]:
                                    list_of_hist[ac][v]['signal'][sample_name].add(list_of_hist[c][v]['signal'][sample_name])
                    if not args.signalOnly:
                        list_of_hist[ac][v]['bkgr'] = {}
                        for b in background_collection:
                            sample_name = b.split('/')[-1]
                            list_of_hist[ac][v]['bkgr'][sample_name] = list_of_hist[cat.ANALYSIS_CATEGORIES[ac][0]][v]['bkgr'][sample_name].clone(ac)
                            if len(cat.ANALYSIS_CATEGORIES[ac]) > 1:
                                for c in cat.ANALYSIS_CATEGORIES[ac][1:]:
                                    list_of_hist[ac][v]['bkgr'][sample_name].add(list_of_hist[c][v]['bkgr'][sample_name])

            for ac in cat.SUPER_CATEGORIES.keys():
                if ac in list_of_hist.keys():
                    continue
                list_of_hist[ac] = {}
                for v in var.keys():
                    list_of_hist[ac][v] = {}
                    if not args.bkgrOnly:
                        list_of_hist[ac][v]['signal'] = {}
                        for s in signal_list:
                            sample_name = s.split('/')[-1]
                            sample_mass = float(sample_name.split('-m')[-1])
                            list_of_hist[ac][v]['signal'][sample_name] = list_of_hist[cat.SUPER_CATEGORIES[ac][0]][v]['signal'][sample_name].clone(ac)
                            if len(cat.SUPER_CATEGORIES[ac]) > 1:
                                for c in cat.SUPER_CATEGORIES[ac][1:]:
                                    list_of_hist[ac][v]['signal'][sample_name].add(list_of_hist[c][v]['signal'][sample_name])
                    if not args.signalOnly:
                        list_of_hist[ac][v]['bkgr'] = {}
                        for b in background_collection:
                            sample_name = b.split('/')[-1]
                            list_of_hist[ac][v]['bkgr'][sample_name] = list_of_hist[cat.SUPER_CATEGORIES[ac][0]][v]['bkgr'][sample_name].clone(ac)
                            if len(cat.SUPER_CATEGORIES[ac]) > 1:
                                for c in cat.SUPER_CATEGORIES[ac][1:]:
                                    list_of_hist[ac][v]['bkgr'][sample_name].add(list_of_hist[c][v]['bkgr'][sample_name])


        #
        #       Plot!
        #

        #
        # Necessary imports
        #
        from HNL.Plotting.plot import Plot
        from HNL.Plotting.plottingTools import extraTextFormat
        from HNL.Tools.helpers import makePathTimeStamped


        if args.makeDataCards:
            from HNL.Stat.combineTools import makeDataCard

            #
            # If we want to use shapes, first make shape histograms, then make datacards
            #
            for ac in cat.SUPER_CATEGORIES.keys():
                # # Observed
                # shape_hist['data_obs'] = ROOT.TH1D('data_obs', 'data_obs', n_search_regions, 0.5, n_search_regions+0.5)
                # shape_hist['data_obs'].SetBinContent(1, 1.)

                # # Background
                # for sample_name in sample_manager.sample_groups.keys():
                #     shape_hist[sample_name] = ROOT.TH1D(sample_name, sample_name, n_search_regions, 0.5, n_search_regions+0.5)
                #     for sr in xrange(1, n_search_regions+1):
                #         shape_hist[sample_name].SetBinContent(sr, list_of_values['bkgr'][sample_name][ac][sr])
                #         shape_hist[sample_name].SetBinError(sr, list_of_errors['bkgr'][sample_name][ac][sr])
                
                # Signal 
                for s in signal_list:
                    sample_name = s.split('/')[-1]
                    sample_mass = float(sample_name.split('-m')[-1])
                    if sample_mass not in args.masses: continue
                    if sample_mass <= 80:
                        mva_to_use = 'mva_low_'+args.flavor+'_'+args.region
                    else:
                        mva_to_use = 'mva_high_'+args.flavor+'_'+args.region
                    out_path = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'shapes', '-'.join([args.strategy, args.selection, args.region]), 
                                            str(year), args.flavor, sample_name, ac+'.shapes.root')
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
                    
                    makeDataCard(str(ac), args.flavor, year, 0, sample_name, bkgr_names, args.selection, args.strategy, args.region, shapes=True, coupling_sq = coupling_squared)

        if args.makePlots:
            #
            # Set output directory, taking into account the different options
            #
            if not args.isTest:
                output_dir = os.path.join(os.getcwd(), 'data', 'Results', 'plotVariables', '-'.join([args.strategy, args.selection, args.region]), str(year))
            else:
                output_dir = os.path.join(os.getcwd(), 'data', 'testArea', 'Results', 'plotVariables', '-'.join([args.strategy, args.selection, args.region]), str(year))



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
            # Create plots for each category
            #
            from HNL.EventSelection.eventCategorization import CATEGORY_NAMES
            # for c in list_of_hist.keys():
            for c in cat.SUPER_CATEGORIES.keys():
                c_name = CATEGORY_NAMES[c] if c not in cat.SUPER_CATEGORIES.keys() else c

                # extra_text = [extraTextFormat(cat.returnTexName(c), xpos = 0.2, ypos = 0.82, textsize = None, align = 12)]  #Text to display event type in plot
                extra_text = [extraTextFormat(c_name, xpos = 0.2, ypos = 0.82, textsize = None, align = 12)]  #Text to display event type in plot
                if not args.bkgrOnly:
                    extra_text.append(extraTextFormat('V_{'+args.flavor+'N} = '+str(args.coupling)))  #Text to display event type in plot
                    # if not args.signalOnly: extra_text.append(extraTextFormat('Signal scaled to background', textsize = 0.7))  #Text to display event type in plot

                # Plots that display chosen for chosen signal masses and backgrounds the distributions for the different variables
                # S and B in same canvas for each variable
                for v in var:
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

                    # Create plot object (if signal and background are displayed, also show the ratio)

                    draw_ratio = None if args.signalOnly or args.bkgrOnly else True
                    if args.groupSamples:
                        p = Plot(signal_hist, legend_names, c_name+'-'+v, bkgr_hist = bkgr_hist, observed_hist = observed_hist, y_log = True, extra_text = extra_text, draw_ratio = draw_ratio, year = int(year), 
                                color_palette = 'Didar', color_palette_bkgr = 'AN2017')
                        # p = Plot(signal_hist, legend_names, c_name+'-'+v, bkgr_hist = bkgr_hist, observed_hist = observed_hist, y_log = False, extra_text = extra_text, draw_ratio = draw_ratio, year = int(year), 
                                # color_palette = 'Didar', color_palette_bkgr = 'AN2017')
                    else:
                        p = Plot(signal_hist, legend_names, c_name+'-'+v, bkgr_hist = bkgr_hist, y_log = False, extra_text = extra_text, draw_ratio = draw_ratio, year = int(year), 
                                color_palette = 'Didar')


                    # Draw
                    # p.drawHist(output_dir = os.path.join(output_dir, c_name), normalize_signal = True, draw_option='EHist', min_cutoff = 1)
                    p.drawHist(output_dir = os.path.join(output_dir, c_name), normalize_signal = False, draw_option='EHist', min_cutoff = 1)

                # if args.
                
                #TODO: I broke this when changing the eventCategorization, fix this again
                # # If looking at signalOnly, also makes plots that compares the three lepton pt's for every mass point
                # if args.signalOnly:

                #     all_cuts = returnCategoryPtCuts(c)
                    
                #     for cuts in all_cuts:   
            
                #         # Load in efficiency to print on canvas if requested
                #         if args.showCuts:
                #             eff_file = os.path.expandvars('$CMSSW_BASE/src/HNL/EventSelection/data/calcSignalEfficiency/HNLtau/divideByCategory/triggerTest/signalSelectionFull.root')
                #             eff = Efficiency('efficiency_'+str(c[0])+'_'+str(c[1]) + '_l1_'+str(cuts[0])+'_l2_'+str(cuts[1])+'_l3_'+str(cuts[2]), None, None, eff_file, 
                #                   subdirs=['efficiency_'+str(c[0])+'_'+str(c[1]), 'l1_'+str(cuts[0])+'_l2_'+str(cuts[1])+'_l3_'+str(cuts[2])])           
            
                #         # Loop over different signals and draw the pt
                #         for n in list_of_hist[c][v]['signal'].keys():
                #             h = [list_of_hist[c]['l1pt']['signal'][n], list_of_hist[c]['l2pt']['signal'][n], list_of_hist[c]['l3pt']['signal'][n]]
                #             legend_names = ['l1', 'l2', 'l3']
                            
                #             # Prepare to draw the pt cuts on the canvas if requested
                #             if args.showCuts:
                #                 draw_cuts = [cuts, eff.getEfficiency(inPercent=True).GetBinContent(eff.getEfficiency().FindBin(float(n.split('-')[1].split('M')[1])))]
                #             else:
                #                 draw_cuts = None
                #             # Create plot object and draw
                #             #p = Plot(h, legend_names, cat.categoryName(c)+'-'+cat.subcategoryName(c)+'-pt-'+n, extra_text=extra_text)
                #             p = Plot(h, legend_names, str(c)+'-pt-'+n, extra_text=extra_text)
                #             #p.drawHist(output_dir = os.path.join(output_dir, cat.categoryName(c), cat.subcategoryName(c), 'pt', 'l1_'+str(cuts[0])+'_l2_'+str(cuts[1])+'_l3_'+str(cuts[2])), 
                #                    normalize_signal=False, draw_option='EHist', draw_cuts=draw_cuts)
                #             p.drawHist(output_dir = os.path.join(output_dir, str(c), 'pt', 'l1_'+str(cuts[0])+'_l2_'+str(cuts[1])+'_l3_'+str(cuts[2])), 
                                    # normalize_signal=False, draw_option='EHist', draw_cuts=draw_cuts)
