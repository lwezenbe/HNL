#! /usr/bin/env python

#
#       Code to calculate signal and background yields
#

import numpy as np
from HNL.Tools.histogram import Histogram
from HNL.EventSelection.eventSelector import EventSelector
from HNL.ObjectSelection.tauSelector import isTightTau
from HNL.Tools.helpers import makeDirIfNeeded

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
argParser.add_argument('--batchSystem',   action='store', default='HTCondor',  help='help')
argParser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
argParser.add_argument('--noskim', action='store_true', default=False,  help='Use no skim sample list')

argParser.add_argument('--makePlots', action='store_true', default=False,  help='make plots')

argParser.add_argument('--selection',   action='store', default='MVA',  help='Select the strategy to use to separate signal from background', choices=['cut-based', 'AN2017014', 'MVA'])
argParser.add_argument('--logLevel',  action='store',      default='INFO',               help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])


args = argParser.parse_args()

from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)

l1 = 0
l2 = 1
l3 = 2

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

sample_manager = SampleManager(args.year, skim_str, 'TauFakes')

jobs = []
for sample_name in sample_manager.sample_names:
    if args.sample and args.sample not in sample_name: continue
    sample = sample_manager.getSample(sample_name)
    for njob in xrange(sample.split_jobs):
        jobs += [(sample.name, str(njob))]

from HNL.BackgroundEstimation.fakerate import FakeRate

#
#   Code to process events
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

    #
    # Import and create cutter to provide cut flow
    #
    from HNL.EventSelection.cutter import Cutter
    cutter = Cutter(chain = chain)

    if args.isTest:
        max_events = 10000
        event_range = xrange(max_events) if max_events < len(sample.getEventRange(args.subJob)) else sample.getEventRange(args.subJob)
    else:
        event_range = sample.getEventRange(args.subJob)    

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
    from HNL.ObjectSelection.objectSelection import objectSelectionCollection

    if args.selection == 'AN2017014':
        object_selection = objectSelectionCollection('deeptauVSjets', 'cutbased', 'FO', 'tight', 'tight', True)
    else:
        object_selection = objectSelectionCollection('deeptauVSjets', 'leptonMVAtop', 'FO', 'tight', 'tight', False)

    es = EventSelector('TauFakes', args.selection, object_selection, True, ec)            

    subjobAppendix = 'subJob' + args.subJob if args.subJob else ''

    def getOutputName():
        if not args.isTest:
            output_name = os.path.join(os.getcwd(), 'data', __file__.split('.')[0], args.year, sample.output)
        else:
            output_name = os.path.join(os.getcwd(), 'data', 'testArea', __file__.split('.')[0], args.year, sample.output)

        if args.isChild:
            output_name += '/tmp_'+sample.output

        output_name += '/'+ sample.name +'_events_' +subjobAppendix+ '.root'
        makeDirIfNeeded(output_name)
        return output_name

    fakerate = FakeRate('tauttl', lambda c: [c.l_pt[2], abs(c.l_eta[2])], ('pt', 'eta'), getOutputName(), (np.array([20., 25., 35., 50., 70., 100.]), np.arange(0., 3.0, 0.5)))
    
    #
    # Loop over all events
    #
    from HNL.Tools.helpers import progress
    from HNL.Triggers.triggerSelection import applyCustomTriggers, listOfTriggersAN2017014

    nbase = 0.
    npassed = 0.
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
        if not es.passedFilter(chain, chain, cutter): continue
        passed = isTightTau(chain, chain.l_indices[2])
        if 0.5 <abs(chain.l_eta[2]) < 1.0 and 20. <chain.l_pt[2] < 25.: 
            print 'entry ', entry, passed
            print chain.l_pt
            print chain.l_eta
            print chain.l_istight
            print chain.l_flavor
            nbase += 1
            if passed: npassed += 1
        fakerate.fill(chain, 1., passed)

    print npassed, nbase, npassed/nbase
    fakerate.write()
    closeLogger(log)

else:
    from HNL.Tools.mergeFiles import merge
    import glob
    from HNL.Tools.helpers import getObjFromFile
    from HNL.Plotting.plot import Plot

    if not args.isTest:
        base_path = os.path.join(os.getcwd(), 'data', __file__.split('.')[0], args.year)
    else:
        base_path = os.path.join(os.getcwd(), 'data', 'testArea', __file__.split('.')[0], args.year)
    in_files = glob.glob(os.path.join(base_path, '*'))
    merge(in_files, __file__, jobs, ('sample', 'subJob'), argParser)

    in_file = base_path +'/DY/events.root'
    ttl = FakeRate('tauttl', None, None, in_file).getEfficiency()

    output_dir = base_path +'/Results'

    p = Plot(signal_hist = ttl, name = 'ttl', year = int(args.year))
    p.draw2D(output_dir = output_dir)
