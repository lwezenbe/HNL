#! /usr/bin/env python

#
#       Code to b-tagging efficiencies in MC
#

#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='prelegacy', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
submission_parser.add_argument('--batchSystem',   action='store', default='HTCondor',  help='help')
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
submission_parser.add_argument('--logLevel',  action='store', default='INFO', help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])
submission_parser.add_argument('--analysis',   action='store', default='HNL',  help='Select the strategy to use to separate signal from background', choices=['HNL', 'AN2017014', 'ewkino'])


argParser.add_argument('--makePlots', action='store_true', default=False,  help='Make plots.')

args = argParser.parse_args()

if args.isTest:
    args.isChild = True
    if args.subJob is None: args.subJob = '0'
    if args.year is None: args.year = '2017'
    if args.era is None: args.era = 'UL'
    if args.sample is None: args.sample = 'TTJets-Dilep'

#
# Open logger
#
from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)
from HNL.Tools.helpers import makeDirIfNeeded
import numpy as np
from HNL.EventSelection.event import Event


#
# Load in the sample list 
#
from HNL.Samples.sampleManager import SampleManager

skim_str = 'noskim'
sublist = 'ObjectSelection/btageff_UL2017'
sample_manager = SampleManager(args.era, args.year, skim_str, sublist)

#
# Define job list
#
jobs = []
for sample_name in sample_manager.sample_names:
    if args.sample and args.sample not in sample_name: continue
    sample = sample_manager.getSample(sample_name)
    # for njob in xrange(sample.returnSplitJobs()):
    for njob in xrange(100):
        jobs += [(sample.name, str(njob))]

#
# Define output name
#
subjobAppendix = 'subJob' + args.subJob if args.subJob else ''
def getOutputBase():
    if not args.isTest:
        output_name = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'ObjectSelection', 'data', 'btagEfficiencies', args.era+'-'+args.year, args.selection)
    else:
        output_name = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'ObjectSelection', 'data', 'testArea', 'btagEfficiencies', args.era+'-'+args.year, args.selection)
    return output_name

def getOutputName():
    output_name = os.path.join(getOutputBase())

    if args.isChild:
        output_name += '/tmp_all'

    output_name += '/'+ sample.name +'_events_' +subjobAppendix+ '.root'
    makeDirIfNeeded(output_name)
    return output_name

from HNL.ObjectSelection.bTagWP import getAllAlgorithms, readBTagValue, getBTagWP, getFlavor
from HNL.Tools.efficiency import Efficiency

all_algos = getAllAlgorithms(args.era, args.year)

flavors = ['b', 'c', 'other']

workingpoints = ['loose', 'medium', 'tight']

#
#   Code to process events if we are not making plots
#
if not args.makePlots: 
    #
    # Submit subjobs
    #
    if not args.isChild and not args.isTest:
        from HNL.Tools.jobSubmitter import submitJobs
        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'btagEff')
        exit(0)

    #
    # Load in sample and chain
    #
    sample = sample_manager.getSample(args.sample)
    chain = sample.initTree(needhcount = False)
    chain.year = args.year
    chain.era = args.era

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
        # event_range = xrange(max_events)
        event_range = xrange(max_events) if max_events < len(sample.getEventRange(args.subJob)) else sample.getEventRange(args.subJob)
    else:
        event_range = sample.getEventRange(args.subJob)    

    efficiencies = {}
    for algo in all_algos:
        efficiencies[algo] = {}
        for flavor in flavors:
            efficiencies[algo][flavor] = {}
            for workingpoint in workingpoints:
                efficiencies[algo][flavor][workingpoint] = Efficiency('btag_efficiencies', lambda c, i: (c._jetSmearedPt[i], c._jetEta[i]), ('p_{T} [GeV]', '|#eta|'), getOutputName(), (np.array([20., 30., 50., 70., 100., 140., 200., 300., 600., 1000.]), np.array([0., 0.8, 1.6, 2.4])), subdirs = [algo, flavor, workingpoint])

    #
    # Define event selection
    #
    event = Event(chain, chain, is_reco_level=True, selection='default', strategy='MVA', region='NoSelection', analysis=args.analysis, year = args.year, era = args.era)    

    #
    # Get luminosity weight
    #
    from HNL.Weights.reweighter import Reweighter
    lw = Reweighter(sample, sample_manager)

    #
    # Loop over all events
    #
    from HNL.Tools.helpers import progress
    from HNL.ObjectSelection.jetSelector import isGoodBJet

    for entry in event_range:

        chain.GetEntry(entry)
        if args.isTest: progress(entry - event_range[0], len(event_range))

        event.initEvent()

        for j in xrange(chain._nJets):
            if not isGoodBJet(chain, j, 'base'): continue
            for algo in all_algos:
                for workingpoint in workingpoints:
                    passed = readBTagValue(chain, j, algo) > getBTagWP(chain.era, chain.year, workingpoint, algo)
#                    print passed, readBTagValue(chain, j, algo), getBTagWP(chain.era, chain.year, workingpoint, algo)
                    efficiencies[algo][getFlavor(chain, j)][workingpoint].fill(chain, lw.getLumiWeight(), passed, index = j)

    for ia, algo in enumerate(all_algos):
        for iflav, flavor in enumerate(flavors):
            for iwp, workingpoint in enumerate(workingpoints):
                efficiencies[algo][flavor][workingpoint].write(append = not (ia == 0 and iflav == 0 and iwp == 0))

    closeLogger(log)

#
# Plotting time
#
else:
    from HNL.Tools.mergeFiles import merge
    import glob
    from HNL.Tools.helpers import makePathTimeStamped
    from HNL.Plotting.plot import Plot

    base_path_in = getOutputBase()
    if args.isTest:
        base_path_out = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'ObjectSelection', 'data', 'testArea', 'Results', 
                        'btagEfficiencies', args.era+'-'+args.year, args.selection)
    else:
        base_path_out = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'ObjectSelection', 'data', 'Results', 
                        'btagEfficiencies', args.era+'-'+args.year, args.selection)
                    
    in_files = glob.glob(os.path.join(base_path_in))
    merge(in_files, __file__, jobs, ('sample', 'subJob'), argParser, istest=args.isTest)

    for algo in all_algos:
        for workingpoint in workingpoints:
            for flavor in flavors:
                efficiency = Efficiency('btag_efficiencies', lambda c, i: (c._jetSmearedPt[i], c._jetEta[i]), ('p_{T} [GeV]', '|#eta|'), base_path_in+'/events.root', bins=None, subdirs = [algo, flavor, workingpoint])
                p = Plot(signal_hist = efficiency.getEfficiency(), name = 'b-tag-efficiency', year = args.year, era = args.era, x_log=True, y_log = False)
                p.draw2D(output_dir = base_path_out, names = ['-'.join([algo, workingpoint, flavor])])     
