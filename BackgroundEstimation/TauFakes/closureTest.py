#! /usr/bin/env python

#
#       Code to perform closure tests
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
argParser.add_argument('--isCheck', action='store_true', default=False,  help='Check the setup by using the exact same region as the ttl measurement')

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
    args.year = '2016'

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
from HNL.BackgroundEstimation.closureObject import ClosureObject

if args.isCheck:
    var =  {'pt':           (lambda c, i : c.l_pt[i],         np.array([20., 25., 35., 50., 70., 100.]),       ('p_{T} [GeV]', 'Events')),
            'eta':          (lambda c, i : c.l_eta[i],        np.arange(0., 3.0, 0.5),       ('#eta', 'Events')),
    }
else:
    var = {
            'minMos':       (lambda c : c.minMos,       np.arange(0., 160., 10.),         ('min(M_{OS}) [GeV]', 'Events')),
            'm3l':          (lambda c : c.M3l,          np.arange(0., 240., 15.),         ('M_{3l} [GeV]', 'Events')),
            'met':          (lambda c : c._met,         np.arange(0., 300., 15.),         ('p_{T}^{miss} [GeV]', 'Events')),
            'mtOther':      (lambda c : c.mtOther,      np.arange(0., 300., 15.),       ('M_{T} (other min(M_{OS}) [GeV])', 'Events')),
            'pt':           (lambda c, i : c.l_pt[i],         np.arange(0., 300., 15.),       ('p_{T} [GeV]', 'Events')),
            'eta':          (lambda c, i : c.l_eta[i],        np.arange(-2.5, 3.0, 0.5),       ('#eta', 'Events')),
            'mt3':          (lambda c : c.mt3,          np.arange(0., 315., 15.),         ('M_{T}(3l) [GeV]', 'Events')),
            'LT':           (lambda c : c.LT,           np.arange(0., 915., 15.),         ('L_{T} [GeV]', 'Events')),
            'HT':           (lambda c : c.HT,           np.arange(0., 915., 15.),         ('H_{T} [GeV]', 'Events'))
    }   

subjobAppendix = 'subJob' + args.subJob if args.subJob else ''
def getOutputName():
    if not args.isTest:
        output_name = os.path.join(os.getcwd(), 'data', __file__.split('.')[0])
    else:
        output_name = os.path.join(os.getcwd(), 'data', 'testArea', __file__.split('.')[0])

    if args.isCheck:
        output_name += '/isCheck'

    output_name += '/'+sample.output

    if args.isChild:
        output_name += '/tmp_'+sample.output

    output_name += '/'+ sample.name +'_events_' +subjobAppendix+ '.root'
    makeDirIfNeeded(output_name)
    return output_name

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
        max_events = 2000
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
        object_selection = objectSelectionCollection('deeptauVSjets', 'cutbased', 'tight', 'tight', 'tight', True)
    else:
        object_selection = objectSelectionCollection('deeptauVSjets', 'leptonMVAtop', 'FO', 'tight', 'tight', True)

    if args.isCheck:
        es = EventSelector('TauFakes', args.selection, object_selection, True, ec)    
    else:
        es = EventSelector('TauCT', args.selection, object_selection, True, ec)    

    co = {}
    for v in var:
        co[v] = ClosureObject('tauClosure-'+v, var[v][0], var[v][2], getOutputName(), bins = var[v][1])

    fakerate = FakeRate('tauttl', lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), '/storage_mnt/storage/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/BackgroundEstimation/TauFakes/data/tightToLoose/DY/events.root')

    #
    # Loop over all events
    #
    from HNL.Tools.helpers import progress
    from HNL.Triggers.triggerSelection import applyCustomTriggers, listOfTriggersAN2017014

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

        fake_factor = fakerate.getFakeWeight(chain)
        
        for v in var:
            if v == 'pt' or v == 'eta':
                if(len(es.selector.loose_taus) == 1):
                    co[v].fillClosure(chain, 1., fake_factor, index = 2)
                elif(len(es.selector.loose_taus) == 2):
                    co[v].fillClosure(chain, 1., fake_factor, index = 1)
                    co[v].fillClosure(chain, 1., fake_factor, index = 2)
                else:
                    pass
            else:
                co[v].fillClosure(chain, 1., fake_factor)

    for i, v in enumerate(var):
        if i == 0:
            co[v].write()
        else:
            co[v].write(append=True)

    cutter.saveCutFlow(getOutputName())

    closeLogger(log)

else:
    from HNL.Tools.mergeFiles import merge
    import glob
    from HNL.Tools.helpers import getObjFromFile
    from HNL.Plotting.plot import Plot

    if not args.isTest:
        base_path = os.path.join(os.getcwd(), 'data', __file__.split('.')[0])
    else:
        base_path = os.path.join(os.getcwd(), 'data', 'testArea', __file__.split('.')[0])

    if args.isCheck:
        base_path += '/isCheck'


    in_files = glob.glob(os.path.join(base_path, '*'))
    merge(in_files, __file__, jobs)

    base_path_split  = base_path.rsplit('/', 1)
    output_dir = base_path_split[0] +'/Results/'+base_path_split[1]

    closureObjects = {}
    for in_file in in_files:
        sample_name = in_file.rsplit('/', 1)[-1]
        closureObjects[sample_name] = {}
        for v in var:
            closureObjects[sample_name][v] = ClosureObject('tauClosure-'+v, None, None, getOutputName().rsplit('/', 1)[0]+'/events.root')

    for sample_name in closureObjects.keys():
        for v in var:
            p = Plot(name = v, signal_hist = closureObjects[sample_name][v].getObserved(), bkgr_hist = closureObjects[sample_name][v].getSideband(), color_palette='Black', tex_names = ["Observed", 'Predicted'], draw_ratio = True)
            p.drawHist(output_dir = output_dir+'/'+sample_name, draw_option='EP')
