#! /usr/bin/env python

#
#       Code to calculate signal and background yields
#

#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--flavor', action='store',  help='flavor for which to run fake rate measurement', choices=['tau', 'e', 'mu'])
submission_parser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='prelegacy', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
submission_parser.add_argument('--inData',   action='store_true', default=False,  help='Run in data')
submission_parser.add_argument('--batchSystem',   action='store', default='HTCondor',  help='help')
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--noskim', action='store_true', default=False,  help='measure in data')
submission_parser.add_argument('--analysis',   action='store', default='HNL',  help='Select the strategy to use to separate signal from background', choices=['HNL', 'AN2017014', 'ewkino'])
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
submission_parser.add_argument('--tauRegion', action='store', type=str, default = None, help='What region do you want to select for?', 
    choices=['TauFakesDYttl', 'TauFakesTTttl', 'TauFakesDYttlnomet'])
submission_parser.add_argument('--logLevel',  action='store', default='INFO', help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])

argParser.add_argument('--makePlots', action='store_true', default=False,  help='Make plots.')

args = argParser.parse_args()


#
# Change some settings if this is a test
#
if args.isTest:
    args.isChild = True
    if args.subJob is None: args.subJob = '0'
    if args.year is None: args.year = '2016'
    if args.flavor is None: args.flavor = 'tau'
    if args.flavor == 'tau' and args.tauRegion is None: args.tauRegion = 'TauFakesDYttl'
    if args.sample is None: 
        if args.inData: args.sample = 'Data-'+args.era+args.year
        elif args.flavor == 'e': args.sample = 'QCDEMEnriched-80to120'
        elif args.flavor == 'mu': args.sample = 'QCDmuEnriched-80to120'
        else:   args.sample = 'DYJetsToLL-M-50'
    from HNL.Tools.helpers import generateArgString
    arg_string =  generateArgString(argParser)
else:
    arg_string = None

#
# Raise errors if needed
#
if args.flavor == 'tau' and args.tauRegion is None:
    raise RuntimeError("Specify the tauRegion in which to measure the tau fake rate")
if args.flavor != 'tau' and args.tauRegion is not None:
    raise RuntimeError("Option tauRegion can not be used for light lepton measurement")
if args.tauRegion == 'AN2017014' and args.flavor == 'tau':
    raise RuntimeError("AN-2017-014 does not consider any taus")
if args.tauRegion == 'ewkino' and args.flavor in ['e', 'mu']:
    raise RuntimeError("Light lepton fakes for ewkino not implemented")

#
# Open logger
#
from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)

#
# Imports
#
import numpy as np
from HNL.EventSelection.event import Event
from HNL.ObjectSelection.leptonSelector import isGoodLepton
from HNL.Tools.helpers import makeDirIfNeeded
from HNL.Weights.reweighter import Reweighter


#
# Load in the sample list 
#
from HNL.Samples.sampleManager import SampleManager
if args.noskim:
    skim_str = 'noskim'
else:
    skim_str = 'Reco'

sublist = None
if args.inData:
    sublist = 'fulllist_'+args.era+args.year+'_nosignal'
elif args.flavor == 'tau':
    sublist = 'BackgroundEstimation/TauFakes-'+args.era+args.year
elif args.flavor == 'mu':
    sublist = 'BackgroundEstimation/MuonFakes-'+args.era+args.year
elif args.flavor == 'e':
    sublist = 'BackgroundEstimation/ElectronFakes-'+args.era+args.year

selection_to_use = args.selection if args.flavor == 'tau' else 'LukaFR'
sample_manager = SampleManager(args.era, args.year, skim_str, sublist, skim_selection=selection_to_use)

#
# Define job list
#
jobs = []
for sample_name in sample_manager.sample_names:
    if args.sample and args.sample not in sample_name: continue
    sample = sample_manager.getSample(sample_name)
    for njob in xrange(sample.returnSplitJobs()):
        jobs += [(sample.name, str(njob))]

from HNL.BackgroundEstimation.fakerateArray import createFakeRatesWithJetBins
region_to_select = args.tauRegion if args.flavor == 'tau' else 'LightLeptonFakes'
#
# Define output name
#
subjobAppendix = 'subJob' + args.subJob if args.subJob else ''
data_str = 'DATA' if args.inData else 'MC'
def getOutputBase(region):
    if not args.isTest:
        output_name = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data', __file__.split('.')[0].rsplit('/', 1)[-1], args.era+'-'+args.year, data_str, args.flavor, '-'.join([region, args.selection]))
    else:
        output_name = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data', 'testArea', __file__.split('.')[0].rsplit('/', 1)[-1], args.era+'-'+args.year, data_str, args.flavor, '-'.join([region, args.selection]))
    return output_name

def getOutputName(region):
    output_name = os.path.join(getOutputBase(region), sample.output)

    if args.isChild:
        output_name += '/tmp_'+sample.output

    output_name += '/'+ sample.name +'_events_' +subjobAppendix+ '.root'
    makeDirIfNeeded(output_name)
    return output_name

#
#   Code to process events if we are not making plots
#
if not args.makePlots:
    #
    # Submit subjobs
    #
    if not args.isChild:
        from HNL.Tools.jobSubmitter import submitJobs
        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'tightToLoose')
        exit(0)

    #
    # Load in sample and chain
    #
    sample = sample_manager.getSample(args.sample)
    if not args.inData and 'Data' in sample.name: exit(0)
    chain = sample.initTree(needhcount = False)
    chain.HNLmass = sample.getMass()
    chain.year = args.year
    chain.era = args.era
    chain.analysis = args.analysis
    chain.selection = args.selection

    #
    # Initialize reweighter
    #
    reweighter = Reweighter(sample, sample_manager)

    #
    # Import and create cutter to provide cut flow
    #
    from HNL.EventSelection.cutter import Cutter
    cutter = Cutter(chain = chain)

    #
    # Set range of events to process
    #
    if args.isTest:
        max_events = 20000
        event_range = xrange(max_events) if max_events < len(sample.getEventRange(args.subJob)) else sample.getEventRange(args.subJob)
    else:
        event_range = sample.getEventRange(args.subJob)    

    #
    # Get luminosity weight
    #
    from HNL.Weights.reweighter import Reweighter
    lw = Reweighter(sample, sample_manager)

    from HNL.EventSelection.eventCategorization import EventCategory
    try:
        ec = EventCategory(chain)
    except:
        ec = None

    #
    # Define event selection
    #
    event = Event(chain, chain, is_reco_level=True, selection=args.selection, strategy='MVA', region=region_to_select, analysis = args.analysis, year = args.year, era = args.era)    

    #
    # Create fake rate objects
    #
    if args.flavor == 'tau':
        fakerates = createFakeRatesWithJetBins('tauttl', lambda c, i: [c.l_pt[i], abs(c.l_eta[i])], ('pt', 'eta'), getOutputName(region_to_select), 
                                                (np.array([20., 25., 35., 50., 70., 100.]), np.arange(0., 3.0, 0.5)))
    elif args.flavor == 'mu':
        fakerates = createFakeRatesWithJetBins('tauttl', lambda c, i: [c.l_pt[i], abs(c.l_eta[i])], ('pt', 'eta'), getOutputName(region_to_select), 
                                                (np.array([10., 20., 30., 45., 65., 100.]), np.array([0., 1.2, 2.1, 2.4])))
    elif args.flavor == 'e':
        fakerates = createFakeRatesWithJetBins('tauttl', lambda c, i: [c.l_pt[i], abs(c.l_eta[i])], ('pt', 'eta'), getOutputName(region_to_select), 
                                                (np.array([10., 20., 30., 45., 65., 100.]), np.array([0., .8, 1.442, 2.5])))
    else:
        raise RuntimeError('Invalid flavor')
    
    #
    # Loop over all events
    #
    from HNL.Tools.helpers import progress
    from HNL.Triggers.triggerSelection import passTriggers

    for entry in event_range:

        chain.GetEntry(entry)
        if args.isTest: progress(entry - event_range[0], len(event_range))

        cutter.cut(True, 'total')
        
        #
        #Triggers
        #
        # if args.selection == 'AN2017014':
        #     if not cutter.cut(passTriggers(chain, 'HNL_old'), 'pass_triggers'): continue
        # else:
        #     if not cutter.cut(passTriggers(chain, 'HNL'), 'pass_triggers'): continue

        # if not cutter.cut(passTriggers(chain, 'ewkino'), 'pass_triggers'): continue

        event.initEvent()

        #Event selection
        if args.flavor == 'e':
            if not event.passedFilter(cutter, sample.name, only_electrons = True, require_jets = True, offline_thresholds=False): continue
        elif args.flavor == 'mu':
            if not event.passedFilter(cutter, sample.name, only_muons = True, require_jets = True, offline_thresholds=False): continue
        else:
            if not event.passedFilter(cutter, sample.name): continue
        fake_index = event.event_selector.selector.getFakeIndex()
        
        if args.inData and not chain.is_data:
            if not chain._lIsPrompt[chain.l_indices[fake_index]]: continue
            passed = True #Always fill both denom and enum for this case (subtraction of prompt contribution)
            weight = -1.*reweighter.getLumiWeight()
        else:
            if not chain.is_data and not cutter.cut(chain.l_isfake[fake_index], 'fake lepton'): continue
            passed = isGoodLepton(chain, chain.l_indices[fake_index], 'tight')
            weight = reweighter.getLumiWeight()
        
        fakerates.fillFakeRates(chain, weight, passed, index = fake_index)

    print fakerates.getFakeRate('total').getNumerator().GetSumOfWeights(), fakerates.getFakeRate('total').getDenominator().GetSumOfWeights()
    print fakerates.getFakeRate('total').getNumerator().GetEntries(), fakerates.getFakeRate('total').getDenominator().GetEntries()
    print fakerates.getFakeRate('0jets').getNumerator().GetSumOfWeights(), fakerates.getFakeRate('0jets').getDenominator().GetSumOfWeights()
    print fakerates.getFakeRate('0jets').getNumerator().GetEntries(), fakerates.getFakeRate('0jets').getDenominator().GetEntries()
    print fakerates.getFakeRate('njets').getNumerator().GetSumOfWeights(), fakerates.getFakeRate('njets').getDenominator().GetSumOfWeights()
    print fakerates.getFakeRate('njets').getNumerator().GetEntries(), fakerates.getFakeRate('njets').getDenominator().GetEntries()
    fakerates.writeFakeRates(is_test=arg_string)
    cutter.saveCutFlow(getOutputName(region_to_select))
    closeLogger(log)

#
# Plotting time
#
else:
    from HNL.Tools.mergeFiles import merge
    import glob
    from HNL.Tools.helpers import makePathTimeStamped
    from HNL.Plotting.plot import Plot

    base_path_in = getOutputBase(region_to_select)
    if args.isTest:
        base_path_out = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data', 'testArea', 'Results', 
                        __file__.split('.')[0].rsplit('/', 1)[-1], data_str, args.era+'-'+args.year, args.flavor, '-'.join([region_to_select, args.selection]))
    else:
        base_path_out = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data', 'Results', 
                        __file__.split('.')[0].rsplit('/', 1)[-1], data_str, args.era+'-'+args.year, args.flavor, '-'.join([region_to_select, args.selection]))
                    
    in_files = glob.glob(os.path.join(base_path_in, '*'))
    merge(in_files, __file__, jobs, ('sample', 'subJob'), argParser, istest=args.isTest)

    if args.inData:
        os.system("hadd -f "+base_path_in+"/events.root "+base_path_in+'/*/events.root')

    samples_to_plot = ['Data'] if args.inData else sample_manager.getOutputs()

    for sample_output in samples_to_plot:
        if args.isTest and sample_output != 'DY': continue
        if args.inData:
            output_dir = makePathTimeStamped(base_path_out)
            in_file = base_path_in+'/events.root'
        else:
            output_dir = makePathTimeStamped(base_path_out +'/'+sample_output)
            in_file = base_path_in+'/'+sample_output+'/events.root'

        fakerates = createFakeRatesWithJetBins('tauttl', None, None, in_file)
        for fr in fakerates.bin_collection:
            ttl = fakerates.getFakeRate(fr).getEfficiency()

            p = Plot(signal_hist = ttl, name = 'ttl_'+fr, year = args.year, era = args.era, x_name="p_{T} [GeV]", y_name = "|#eta|")
            p.draw2D(output_dir = output_dir, names = ['ttl_'+fr])
