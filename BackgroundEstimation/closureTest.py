#! /usr/bin/env python

#
#       Code to perform closure tests
#

import numpy as np
from HNL.Tools.histogram import Histogram
from HNL.EventSelection.eventSelector import EventSelector
from HNL.ObjectSelection.tauSelector import isTightTau
from HNL.ObjectSelection.leptonSelector import isGoodLepton
from HNL.Tools.helpers import makeDirIfNeeded

#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--flavorToTest',   action='store', default = None,  help='Select flavor to perform closure test on', choices=['e', 'mu', 'tau'])
argParser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018'])
argParser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
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

#
# Throws exceptions if arguments do not add up
#
if args.flavorToTest != 'tau' and args.isCheck:
    raise RuntimeError("Nothing to check, you are using an imported fakerate")
if args.selection == 'AN2017014':
    raise RuntimeError("selection AN2017014 currently not supported")

from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)


flavor_dict = {'tau' : 2, 'e' : 0, 'mu' : 1}
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

sample_manager = SampleManager(args.year, skim_str, 'ClosureTests')

#
# function to have consistent categories in running and plotting
#
from HNL.EventSelection.eventCategorization import ANALYSIS_CATEGORIES

jobs = []
for sample_name in sample_manager.sample_names:
    if args.sample and args.sample not in sample_name: continue
    sample = sample_manager.getSample(sample_name)
    for njob in xrange(sample.split_jobs):
        jobs += [(sample.name, str(njob))]

from HNL.BackgroundEstimation.fakerate import FakeRate
from HNL.BackgroundEstimation.fakerateEmulator import FakeRateEmulator
from HNL.BackgroundEstimation.closureObject import ClosureObject

if args.isCheck:
    var =  {'pt':           (lambda c, i : c.l_pt[i],         np.array([20., 25., 35., 50., 70., 100.]),       ('p_{T} [GeV]', 'Events')),
            'eta':          (lambda c, i : abs(c.l_eta[i]),        np.arange(0., 3.0, 0.5),       ('#eta', 'Events')),
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
        output_name = os.path.join(os.getcwd(), 'data', __file__.split('.')[0], args.year, args.flavorToTest)
    else:
        output_name = os.path.join(os.getcwd(), 'data', 'testArea', __file__.split('.')[0], args.year, args.flavorToTest)

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
        max_events = 1000
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

    if args.flavorToTest == 'tau':
        object_selection = objectSelectionCollection('deeptauVSjets', 'leptonMVAtop', 'FO', 'tight', 'tight', False)
        if args.isCheck:
            es = EventSelector('TauFakes', args.selection, object_selection, True, ec)    
        else:
            es = EventSelector('TauCT', args.selection, object_selection, True, ec) 

        if not args.isTest:    
            fakerate = FakeRate('tauttl', lambda c, i: [c.l_pt[i], abs(c.l_eta[i])], ('pt', 'eta'), os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'BackgroundEstimation', 'TauFakes', 'data', 'tightToLoose', args.year, 'DY', 'events.root')))
        else:
            print os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'BackgroundEstimation', 'TauFakes', 'data', 'tightToLoose', args.year, 'DY', 'events.root'))
            fakerate = FakeRate('tauttl', lambda c, i: [c.l_pt[i], abs(c.l_eta[i])], ('pt', 'eta'), os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'BackgroundEstimation', 'TauFakes', 'data', 'tightToLoose', args.year, 'DY', 'events.root')))
            # fakerate = FakeRate('tauttl', lambda c, i: [c.l_pt[i], abs(c.l_eta[i])], ('pt', 'eta'), os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'BackgroundEstimation', 'TauFakes', 'data', 'testArea', 'tightToLoose', args.year, 'DY', 'events.root')))

    elif args.flavorToTest == 'e':
        object_selection = objectSelectionCollection('deeptauVSjets', 'TTT', 'tight', 'FO', 'tight', True)
        es = EventSelector('ElectronCT', args.selection, object_selection, True, ec)    
        fakerate = FakeRateEmulator('h_tight_e', lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), os.path.join('data','FakeRates', args.year, 'FR_QCD_'+args.year+'_140920.root'))
    elif args.flavorToTest == 'mu':
        object_selection = objectSelectionCollection('deeptauVSjets', 'TTT', 'tight', 'tight', 'FO', True)
        es = EventSelector('MuonCT', args.selection, object_selection, True, ec)    
        fakerate = FakeRateEmulator('h_tight_mu', lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), os.path.join('data','FakeRates', args.year, 'FR_QCD_'+args.year+'_140920.root'))
    else:
        raise RuntimeError('defined flavor input inconsistent')


    co = {}
    for c in ANALYSIS_CATEGORIES.keys() + ['total']:
        co[c] = {}
        for v in var:
            co[c][v] = ClosureObject(args.flavorToTest+'closure-'+v+'-'+c, var[v][0], var[v][2], getOutputName(), bins = var[v][1])

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
        cat = ec.returnAnalysisCategory()

        fake_factor = fakerate.returnFakeWeight(chain, flavor_dict[args.flavorToTest])

        # if 2.0 <abs(chain.l_eta[2]) < 2.5 and 20. <chain.l_pt[2] < 25.: 
        # print 'entry ', entry, isTightTau(chain, chain.l_indices[2]), isGoodLepton(chain, chain.l_indices[2], algo=object_selection['light_algo'], tau_algo=object_selection['tau_algo'], workingpoint='tight'),  chain.l_istight[2]
        # print chain.l_flavor[2], chain.l_pt[2]
        # print fakerate.evaluateEfficiency(chain, 2)
        # print fakerate.returnFakeFactor(chain, 2)
        # print fake_factor
        
        for v in var:
            if v == 'pt' or v == 'eta':
                #Special case, only for taus, in which case there is only one tau which is in the last position
                if args.isCheck:
                    co[cat][v].fillClosure(chain, 1., fake_factor, index=2)
                    co['total'][v].fillClosure(chain, 1., fake_factor, index=2)
                else:
                    #General case
                    for l in es.selector.loose_leptons_of_interest:
                        co[cat][v].fillClosure(chain, 1., fake_factor, index=l)
                        co['total'][v].fillClosure(chain, 1., fake_factor, index=l)
            else:
                co[cat][v].fillClosure(chain, 1., fake_factor)
                co['total'][v].fillClosure(chain, 1., fake_factor)
    
    for i, c in enumerate(ANALYSIS_CATEGORIES.keys() + ['total']):
        for j, v in enumerate(var):
            if i == 0 and j == 0:
                co[c][v].write()
            else:
                co[c][v].write(append=True)

    cutter.saveCutFlow(getOutputName())

    closeLogger(log)

else:
    from HNL.Tools.mergeFiles import merge
    import glob
    from HNL.Tools.helpers import getObjFromFile
    from HNL.Plotting.plot import Plot

    if not args.isTest:
        base_path = os.path.join(os.getcwd(), 'data', __file__.split('.')[0], args.year, args.flavorToTest)
    else:
        base_path = os.path.join(os.getcwd(), 'data', 'testArea', __file__.split('.')[0], args.year, args.flavorToTest)

    if args.isCheck:
        base_path += '/isCheck'

    in_files = glob.glob(os.path.join(base_path, '*'))
    merge(in_files, __file__, jobs, ('sample', 'subJob'), argParser)

    base_path_split  = base_path.rsplit('/', 1)
    output_dir = base_path_split[0] +'/Results/'+base_path_split[1]

    closureObjects = {}
    for in_file in in_files:
        if 'Results' in in_file: continue
        if 'isCheck' in in_file and not args.isCheck: continue
        sample_name = in_file.rsplit('/', 1)[-1]
        closureObjects[sample_name] = {}
        for c in ANALYSIS_CATEGORIES.keys() + ['total']:
            closureObjects[sample_name][c] = {}
            for v in var:
                closureObjects[sample_name][c][v] = ClosureObject(args.flavorToTest+'closure-'+v+'-'+c, None, None, in_file+'/events.root')

    for sample_name in closureObjects.keys():
        for c in ANALYSIS_CATEGORIES.keys() + ['total']:
            for v in var:
                p = Plot(name = v, signal_hist = closureObjects[sample_name][c][v].getObserved(), bkgr_hist = closureObjects[sample_name][c][v].getSideband(), color_palette='Black', color_palette_bkgr='Stack', tex_names = ["Observed", 'Predicted'], draw_ratio = True)
                p.drawHist(output_dir = output_dir+'/'+sample_name+'/'+c, draw_option='EP')