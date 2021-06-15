#! /usr/bin/env python

#
# Argument parser and logging
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true',       default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store', nargs='*',    default=None,   help='Select year', choices=['2016', '2017', '2018'], required=True)
submission_parser.add_argument('--sample',   action='store',            default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',            default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isTest',   action='store_true',       default=False,  help='Run a small test')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--dryRun',   action='store_true',       default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--genLevel',   action='store_true',     default=False,  help='Use gen level variables')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT', ])
submission_parser.add_argument('--analysis',   action='store', default='HNL',  help='Select the analysis which triggers to use', choices=['An2017014', 'HNL' ])
submission_parser.add_argument('--logLevel',  action='store', default='INFO',  help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])
submission_parser.add_argument('--customList',  action='store',      default=None,               help='Name of a custom sample list. Otherwise it will use the appropriate noskim file.')
submission_parser.add_argument('--useRef', action='store_true', default=False,  help='pass ref cuts')
submission_parser.add_argument('--separateTriggers', action='store', default=None,  
    help='Look at each trigger separately for each set of triggers. Single means just one trigger, cumulative uses cumulative OR of all triggers that come before the chosen one in the list, full applies all triggers for a certain category', 
    choices=['single', 'cumulative', 'full'])
argParser.add_argument('--makePlots',   action='store_true',    default=False,  help='Use existing root files to make the plots')

args = argParser.parse_args()


import numpy as np
import os
from HNL.Tools.efficiency import Efficiency

#
# Change some settings if this is a test
#
if args.isTest: 
    args.isChild = True
    if args.sample is None: args.sample = 'HNL-tau-m40'
    if args.subJob is None: args.subJob = '0'
    if args.year is None: args.year = ['2016']
    from HNL.Tools.helpers import generateArgString
    arg_string =  generateArgString(argParser)
else:
    arg_string = None

#
# Open logger
#
from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)


#
# Load in the sample list 
#
from HNL.Samples.sampleManager import SampleManager
def getSampleManager(year):
    return SampleManager(year, 'Reco', 'Triggers/triggerlist_'+str(year))

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
            jobs[year] += [(sample.name, str(njob), year)]

#
# Get Output Name
#
def getOutputBase(year, sample_name):
    if args.separateTriggers is not None:
        sep_trig_name = "separateTriggers"
    else:
        sep_trig_name = 'allTriggers'

    ref_name = "Ref" if args.useRef else "NoRef"

    if not args.isTest:
        output_string = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Triggers', 'data', __file__.split('.')[0].rsplit('/')[-1], 
                                    year, sep_trig_name, '-'.join([args.selection, args.analysis, ref_name]), sample_name)
    else:
        output_string = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Triggers', 'data', 'testArea', __file__.split('.')[0].rsplit('/')[-1], 
                                    year, sep_trig_name, '-'.join([args.selection, args.analysis, ref_name]), sample_name)
    return output_string


def getOutputName(year, sample_name):
    subjobAppendix = 'subJob' + args.subJob if args.subJob else ''
    return os.path.join(getOutputBase(year, sample_name), 'tmp_'+sample_name, '_'.join([sample_name, 'efficiency', subjobAppendix])+'.root')


#
# Define variables
#
var = {'l1pt' : (lambda c : c.l_pt[0],                          np.arange(0., 100., 15.),                 ('p_{T}(l1) [GeV]', 'Efficiency')),
        'l2pt' : (lambda c : c.l_pt[1],                          np.arange(0., 100., 15.),                  ('p_{T}(l2) [GeV]', 'Efficiency')),
        'l3pt' : (lambda c : c.l_pt[2],                          np.arange(0., 100., 15.),                  ('p_{T}(l3) [GeV]', 'Efficiency')),
        'l1eta' : (lambda c : abs(c.l_eta[0]),                          np.arange(0., 3., .5),                  ('|#eta|(l1) [GeV]', 'Efficiency')),
        'l2eta' : (lambda c : abs(c.l_eta[1]),                          np.arange(0., 3., .5),                  ('|#eta|(l2) [GeV]', 'Efficiency')),
        'l3eta' : (lambda c : abs(c.l_eta[2]),                          np.arange(0., 3., .5),                  ('|#eta|(l3) [GeV]', 'Efficiency')),
        'l1-2D' : (lambda c : (c.l_pt[0], abs(c.l_eta[0])),      (np.arange(0., 100., 15.), np.arange(0., 3., .5)), ('p_{T}(l1) [GeV]', '|#eta|(l1)')),
        'l2-2D' : (lambda c : (c.l_pt[1], abs(c.l_eta[1])),      (np.arange(0., 100., 15.), np.arange(0., 3., .5)), ('p_{T}(l2) [GeV]', '|#eta|(subleading)')),
        'l3-2D' : (lambda c : (c.l_pt[2], abs(c.l_eta[2])),      (np.arange(0., 100., 15.), np.arange(0., 3., .5)), ('p_{T}(l3) [GeV]', '|#eta|(subleading)'))}


if not args.makePlots:
    #
    # Submit subjobs
    #
    if not args.isChild:
        from HNL.Tools.jobSubmitter import submitJobs
        print 'submitting'
        for year in jobs.keys():
            submitJobs(__file__, ('sample', 'subJob', 'year'), jobs[year], argParser, jobLabel = 'calcTriggerEff', additionalArgs=[('year', year)])
        exit(0)

    if len(args.year) != 1:
        raise RuntimeError('Length of year argument larger than one')
    year = args.year[0]

    sample_manager = getSampleManager(year)  

    #
    # Load in sample and chain
    #
    sample = sample_manager.getSample(args.sample)
    chain = sample.initTree(needhcount = False)
    chain.HNLmass = sample.getMass()
    chain.year = int(year)

    #
    # Initialize reweighter
    #
    from HNL.Weights.reweighter import Reweighter
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

    efficiencies = {}
    for v in var:
        efficiencies[v] = Efficiency(v, var[v][0], var[v][2], getOutputName(year, sample.output), var[v][1])

    #
    # Define event selection
    #
    from HNL.EventSelection.event import Event
    event = Event(chain, chain, is_reco_level=True, selection=args.selection, strategy='MVA', region='trilepton')    

    #
    # Loop over all events
    #
    from HNL.Tools.helpers import progress
    from HNL.EventSelection.eventSelectionTools import select3Leptons
    for entry in event_range:
        chain.GetEntry(entry)
        progress(entry - event_range[0], len(event_range))

        cutter.cut(True, 'total')
        if args.useRef and not cutter.cut(chain._passTrigger_ref, 'passed ref filter'):     continue

        event.initEvent()
        if not event.passedFilter(cutter, sample.output): continue

        from HNL.Triggers.triggerSelection import passTriggers
        for v in var:
            efficiencies[v].fill(chain, reweighter.getTotalWeight(), passTriggers(chain, args.analysis))

    for iv, v in enumerate(var):
        efficiencies[v].write(append = iv > 0, is_test=arg_string)

    closeLogger(log)

else:
    from HNL.Tools.mergeFiles import merge
    import glob
    from HNL.Tools.helpers import makePathTimeStamped
    from HNL.Plotting.plot import Plot

    for year in args.year:
        base_path_in = getOutputBase(year, '*')
                       
        in_files = glob.glob(base_path_in)
        merge(in_files, __file__, jobs, ('sample', 'subJob'), argParser, istest=args.isTest)

        sample_manager = getSampleManager(year)  
        samples_to_plot = sample_manager.getOutputs()

        for sample_output in samples_to_plot:
            if args.sample and sample_output != args.sample: continue
            for v in var:
                eff = Efficiency(v, var[v][0], var[v][2], getOutputName(year, sample_output).rsplit('/', 2)[0]+'/efficiency.root')
                p = Plot(eff.getEfficiency(), 'efficiency', v, year = int(year))

                output_string = getOutputBase(year, sample_output).replace('Triggers/data/', 'Triggers/data/Results/')
                if '2D' in v:
                    p.draw2D(output_dir=output_string)
                else:
                    p.drawHist(output_string)