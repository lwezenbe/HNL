#! /usr/bin/env python

#
#       Code to calculate signal and background yields
#

#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--flavor', action='store', required=True,  help='flavor for which to run fake rate measurement', choices=['tau', 'e', 'mu'])
argParser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
argParser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018'])
argParser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
argParser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
argParser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
argParser.add_argument('--inData',   action='store_true', default=False,  help='Run in data')
argParser.add_argument('--batchSystem',   action='store', default='HTCondor',  help='help')
argParser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
argParser.add_argument('--noskim', action='store_true', default=False,  help='Use no skim sample list')
argParser.add_argument('--selection',   action='store', default='MVA',  help='Select the strategy to use to separate signal from background', choices=['cut-based', 'AN2017014', 'MVA', 'ewkino', 'TTT'])
argParser.add_argument('--tauRegion', action='store', type=str, default = None, help='What region do you want to select for?', 
    choices=['TauFakesDY', 'TauFakesTT'])
argParser.add_argument('--logLevel',  action='store',      default='INFO',               help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])
argParser.add_argument('--makePlots', action='store_true', default=False,  help='Make plots.')

args = argParser.parse_args()


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
from HNL.Tools.histogram import Histogram
from HNL.EventSelection.eventSelector import EventSelector
from HNL.ObjectSelection.leptonSelector import isGoodLepton
from HNL.Tools.helpers import makeDirIfNeeded
from HNL.Weights.reweighter import Reweighter

#
# Change some settings if this is a test
#
if args.isTest:
    args.isChild = True

    if args.sample is None: args.sample = 'DYJetsToLL-M-50'
    args.subJob = '0'

#
# Load in the sample list 
#
from HNL.Samples.sampleManager import SampleManager
if args.noskim:
    skim_str = 'noskim'
else:
    skim_str = 'Old' if args.selection == 'AN2017014' else 'Reco'

sublist = None
if args.flavor == 'tau':
    sublist = 'TauFakes'
elif args.flavor == 'mu':
    sublist = 'MuonFakes'
elif args.flavor == 'e':
    sublist = 'ElectronFakes'

sample_manager = SampleManager(args.year, skim_str, sublist)

#
# Define job list
#
jobs = []
for sample_name in sample_manager.sample_names:
    if args.sample and args.sample not in sample_name: continue
    sample = sample_manager.getSample(sample_name)
    for njob in xrange(sample.split_jobs):
        jobs += [(sample.name, str(njob))]

from HNL.BackgroundEstimation.fakerateArray import createFakeRatesWithJetBins
region_to_select = args.tauRegion if args.flavor == 'tau' else 'LightLeptonFakes'
#
# Define output name
#
subjobAppendix = 'subJob' + args.subJob if args.subJob else ''
def getOutputBase(region):
    if not args.isTest:
        output_name = os.path.join(os.getcwd(), 'data', __file__.split('.')[0].rsplit('/', 1)[-1], args.year, args.flavor, region)
    else:
        output_name = os.path.join(os.getcwd(), 'data', 'testArea', __file__.split('.')[0].rsplit('/', 1)[-1], args.year, args.flavor, region)
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
        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'calcYields')
        exit(0)

    #
    # Load in sample and chain
    #
    sample = sample_manager.getSample(args.sample)
    chain = sample.initTree(needhcount = False)
    chain.HNLmass = sample.getMass()
    chain.year = int(args.year)

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
        max_events = 5000
        event_range = xrange(max_events) if max_events < len(sample.getEventRange(args.subJob)) else sample.getEventRange(args.subJob)
    else:
        # event_range = sample.getEventRange(args.subJob)    
        event_range = xrange(100)  

    #
    # Get luminosity weight
    #
    from HNL.Weights.lumiweight import LumiWeight
    lw = LumiWeight(sample, sample_manager)

    from HNL.EventSelection.eventCategorization import EventCategory
    try:
        ec = EventCategory(chain)
    except:
        ec = None

    #
    # Object ID param
    # Working points are set in the controlRegionSelector
    #
    from HNL.ObjectSelection.objectSelection import objectSelectionCollection, getObjectSelection
    chain.obj_sel = getObjectSelection(args.selection)

    #
    # Define event selection
    #
    es = EventSelector(region_to_select, chain, chain, args.selection, True, ec)            

    #
    # Create fake rate objects
    #
    if args.flavor == 'tau':
        fakerates = createFakeRatesWithJetBins('tauttl', lambda c, i: [c.l_pt[i], abs(c.l_eta[i])], ('pt', 'eta'), getOutputName(region_to_select), (np.array([20., 25., 35., 50., 70., 100.]), np.arange(0., 3.0, 0.5)))
    elif args.flavor == 'mu':
        fakerates = createFakeRatesWithJetBins('tauttl', lambda c, i: [c.l_pt[i], abs(c.l_eta[i])], ('pt', 'eta'), getOutputName(region_to_select), (np.array([10., 20., 30., 45., 65., 100.]), np.array([0., 1.2, 2.1, 2.4])))
    elif args.flavor == 'e':
        fakerates = createFakeRatesWithJetBins('tauttl', lambda c, i: [c.l_pt[i], abs(c.l_eta[i])], ('pt', 'eta'), getOutputName(region_to_select), (np.array([10., 20., 30., 45., 65., 100.]), np.array([0., .8, 1.442, 2.5])))
    else:
        raise RuntimeError('Invalid flavor')
    
    #
    # Loop over all events
    #
    from HNL.Tools.helpers import progress
    from HNL.Triggers.triggerSelection import passTriggers

    for entry in event_range:
        # if entry != 405: continue
        chain.GetEntry(entry)
        progress(entry - event_range[0], len(event_range))

        cutter.cut(True, 'total')
        
        #
        #Triggers
        #
        if args.selection == 'AN2017014':
            if not cutter.cut(passTriggers(chain, 'HNL_old'), 'pass_triggers'): continue
        
        # if not cutter.cut(passTriggers(chain, 'ewkino'), 'pass_triggers'): continue

        #Event selection
        if args.flavor == 'e':
            if not es.selector.passedFilter(cutter, only_electrons=True, require_jets=True): continue
        elif args.flavor == 'mu':
            if not es.selector.passedFilter(cutter, only_muons=True, require_jets=True): continue
        else:
            if not es.passedFilter(cutter): continue
        fake_index = es.selector.getFakeIndex()
        if args.inData and not chain.is_data:
            if not chain._lIsPrompt[chain.l_indices[fake_index]]: continue
            passed = True
            weight = -1.*reweighter.getLumiWeight()
        else:
            if not chain.is_data and not cutter.cut(chain.l_isfake[fake_index], 'fake lepton'): continue
            passed = isGoodLepton(chain, chain.l_indices[fake_index], 'tight')
            weight = reweighter.getLumiWeight()
        
        # print entry

        fakerates.fillFakeRates(chain, weight, passed, index = fake_index)

        # print chain.njets
    print fakerates.getFakeRate('total').getNumerator().GetSumOfWeights(), fakerates.getFakeRate('total').getDenominator().GetSumOfWeights()
    print fakerates.getFakeRate('total').getNumerator().GetEntries(), fakerates.getFakeRate('total').getDenominator().GetEntries()
    print fakerates.getFakeRate('0jets').getNumerator().GetSumOfWeights(), fakerates.getFakeRate('0jets').getDenominator().GetSumOfWeights()
    print fakerates.getFakeRate('0jets').getNumerator().GetEntries(), fakerates.getFakeRate('0jets').getDenominator().GetEntries()
    print fakerates.getFakeRate('njets').getNumerator().GetSumOfWeights(), fakerates.getFakeRate('njets').getDenominator().GetSumOfWeights()
    print fakerates.getFakeRate('njets').getNumerator().GetEntries(), fakerates.getFakeRate('njets').getDenominator().GetEntries()
    fakerates.writeFakeRates()
    cutter.saveCutFlow(getOutputName(region_to_select))
    closeLogger(log)

#
# Plotting time
#
else:
    from HNL.Tools.mergeFiles import merge
    import glob
    from HNL.Tools.helpers import getObjFromFile, makePathTimeStamped
    from HNL.Plotting.plot import Plot

    base_path = getOutputBase(region_to_select)
    in_files = glob.glob(os.path.join(base_path, '*'))
    merge(in_files, __file__, jobs, ('sample', 'subJob'), argParser)

    for sample_output in sample_manager.getOutputs():
        output_dir = makePathTimeStamped(base_path +'/'+sample_output +'/Results')
        in_file = base_path +'/'+sample_output+'/events.root'
        fakerates = createFakeRatesWithJetBins('tauttl', None, None, in_file)
        for fr in fakerates.bin_collection:
            ttl = fakerates.getFakeRate(fr).getEfficiency()


            p = Plot(signal_hist = ttl, name = 'ttl_'+fr, year = int(args.year))
            p.draw2D(output_dir = output_dir, names = ['ttl_'+fr])