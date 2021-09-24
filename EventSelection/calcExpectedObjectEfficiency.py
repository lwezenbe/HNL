#! /usr/bin/env python

#
#       Code to calculate signal efficiency
#
# Can be used on RECO level, where you check how many events pass the reco selection
# Is also used to check how many events on a generator level pass certain pt cuts
#

import numpy as np

#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='UL', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
submission_parser.add_argument('--strategy',   action='store', default='MVA',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA'])
submission_parser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?', 
    choices=['baseline', 'lowMassSR', 'highMassSR'])
submission_parser.add_argument('--analysis',   action='store', default='HNL',  help='Select the strategy to use to separate signal from background', choices=['HNL', 'AN2017014', 'ewkino'])
argParser.add_argument('--merge',   action='store_true', default=False)
submission_parser.add_argument('--logLevel',  action='store', default='INFO', help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])

args = argParser.parse_args()

from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)

#
# Change some settings if this is a test
#
if args.isTest: 
    args.isChild = True
    if args.sample is None: args.sample = 'DYJetsToLL-M-50'
    if args.subJob is None: args.subJob = '0'
    if args.year is None: args.year = '2017'
    from HNL.Tools.helpers import generateArgString
    arg_string =  generateArgString(argParser)
else:
    arg_string = None

#
# Load in the sample list 
#
def getSampleManager(y):
    skim_str = 'auto'
    file_list = 'EventSelection/fulllist_'+args.era+str(y)

    sm = SampleManager(args.era, y, skim_str, file_list, skim_selection=args.selection, region=args.region)
    return sm

from HNL.Samples.sampleManager import SampleManager
sample_manager = getSampleManager(args.year)

subjobAppendix = 'subJob' + args.subJob if args.subJob is not None else ''

jobs = []
for sample_name in sample_manager.sample_names:
    sample = sample_manager.getSample(sample_name)
    for njob in xrange(sample.returnSplitJobs()): 
        jobs += [(sample.name, str(njob))]

from HNL.Tools.helpers import getMassRange

def getOutputBase():
    if not args.isTest: 
        output_name = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'EventSelection', 'data', __file__.split('.')[0].rsplit('/')[-1], 
                        '-'.join([args.strategy, args.region, args.selection]), args.era+'-'+args.year)
    else:
        output_name = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'EventSelection', 'data', 'testArea', __file__.split('.')[0].rsplit('/')[-1], 
                        '-'.join([args.strategy, args.region, args.selection]), args.era+'-'+args.year)
    return output_name

from HNL.EventSelection.eventCategorization import CATEGORIES, SUPER_CATEGORIES, CATEGORY_NAMES
if not args.merge:
    #
    # Submit subjobs
    #
    if not args.isChild:
        from HNL.Tools.jobSubmitter import submitJobs
        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'calcSignalEfficiency')
        exit(0)

    #
    # Load in sample and chain
    #
    sample = sample_manager.getSample(args.sample)
    chain = sample.initTree()

    output_name = getOutputBase()

    if args.isChild:
        output_name += '/tmp_'+sample.output

    output_name += '/'+ sample.name +'_averageObjectSelection-'+sample.output+'_' +subjobAppendix+ '.root'

    from HNL.EventSelection.eventCategorization import EventCategory, ANALYSIS_CATEGORIES
    ec = EventCategory(chain)

    from HNL.Tools.histogram import Histogram
    list_of_hist = {}
    for ac in ANALYSIS_CATEGORIES:
        list_of_hist[ac] = Histogram(ac, lambda c : c.efficiency, 'Efficiency', np.arange(0., 1.0001, 0.0001))

    #
    # Set event range
    #
    if args.isTest:
        max_events = 20000
        event_range = xrange(max_events) if max_events < len(sample.getEventRange(args.subJob)) else sample.getEventRange(args.subJob)
    else:
        event_range = sample.getEventRange(args.subJob)    

    chain.HNLmass = sample.getMass()
    chain.year = args.year
    chain.era = args.era
    chain.selection = args.selection
    chain.strategy = args.strategy
    chain.analysis = args.analysis

    #
    # Get luminosity weight
    #
    from HNL.Weights.reweighter import Reweighter
    lw = Reweighter(sample, sample_manager)

    #
    # Import and create cutter to provide cut flow
    #
    from HNL.EventSelection.cutter import Cutter
    cutter = Cutter(chain = chain)

    #
    # Loop over all events
    #
    from HNL.Tools.helpers import progress
    from HNL.EventSelection.eventSelectionTools import selectGenLeptonsGeneral, passedCustomPtCuts
    from HNL.EventSelection.signalLeptonMatcher import SignalLeptonMatcher
    from HNL.ObjectSelection.leptonSelector import isGoodLepton

    #
    # Object Selection
    #
    from HNL.ObjectSelection.objectSelection import getObjectSelection
    chain.obj_sel = getObjectSelection(args.selection)

    from HNL.EventSelection.event import Event
    event = Event(chain, chain, is_reco_level=True, selection=args.selection, strategy=args.strategy, region=args.region)

    from HNL.Tools.efficiency import Efficiency
    from HNL.Tools.ROC import ROC
    from HNL.ObjectSelection.objectSelection import getObjectSelection
    # in_base_eff = lambda flavor: os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'ObjectSelection', 'data', 'compareLeptonId', args.era+args.year, flavor, 'DY', 'efficiency-'+flavor+'.root')
    # eff_hist_e = Efficiency('efficiency_pt', 'test', 'test', in_base_eff('e'), subdirs = [getObjectSelection(args.selection)['light_algo']+'-tight', 'efficiency_pt'])
    # eff_hist_mu = Efficiency('efficiency_pt', 'test', 'test',in_base_eff('mu'), subdirs = [getObjectSelection(args.selection)['light_algo']+'-tight', 'efficiency_pt'])
    # in_base_mis = lambda flavor: os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'ObjectSelection', 'data', 'compareLeptonId', args.era+args.year, flavor, 'DY', 'fakerate-'+flavor+'.root')
    # mis_hist_e = Efficiency('fakerate_pt', 'test', 'test',in_base_mis('e'), subdirs = [getObjectSelection(args.selection)['light_algo']+'-tight', 'fakerate_pt'])
    # mis_hist_mu = Efficiency('fakerate_pt', 'test', 'test',in_base_mis('mu'), subdirs = [getObjectSelection(args.selection)['light_algo']+'-tight', 'fakerate_pt'])
    in_base_eff = lambda flavor: os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'ObjectSelection', 'data', 'compareLeptonId', args.era+args.year, flavor, 'DY', getObjectSelection(args.selection)['light_algo']+'-ROC-'+flavor+'.root')
    eff_hist_e = ROC(getObjectSelection(args.selection)['light_algo'], in_base_eff('e')).getEfficiency().GetBinContent(3)
    eff_hist_mu = ROC(getObjectSelection(args.selection)['light_algo'], in_base_eff('mu')).getEfficiency().GetBinContent(3)
    mis_hist_e = ROC(getObjectSelection(args.selection)['light_algo'], in_base_eff('e')).getMisid().GetBinContent(3)
    mis_hist_mu = ROC(getObjectSelection(args.selection)['light_algo'], in_base_eff('mu')).getMisid().GetBinContent(3)

    for entry in event_range:
        
        chain.GetEntry(entry)
        if args.isTest: progress(entry - event_range[0], len(event_range))
        
        event.initEvent()
        if not event.passedFilter(cutter, sample.output): continue

        # print "passed filter"
            
        cat = ec.returnAnalysisCategory()
        if cat not in ['EEE', 'EEMu', 'EMuMu', 'MuMuMu']: continue

        # print 'light lep'

        weight = lw.getLumiWeight()
        chain.efficiency = 1.
        nfakes = 0.
        for pt, isfake, flavor in zip(chain.l_pt, chain.l_isfake, chain.l_flavor):
            if isfake:
                # if flavor == 0: chain.efficiency *= mis_hist_e.evaluateEfficiency(chain, manual_var_entry = pt)
                # elif flavor == 1: chain.efficiency *= mis_hist_mu.evaluateEfficiency(chain, manual_var_entry = pt)
                # # if flavor == 0: print 'ele misid', pt,  mis_hist_e.evaluateEfficiency(chain, manual_var_entry = pt)
                # # elif flavor == 1: print 'muon misid', pt, mis_hist_mu.evaluateEfficiency(chain, manual_var_entry = pt)
                if flavor == 0: chain.efficiency *= mis_hist_e
                elif flavor == 1: chain.efficiency *= mis_hist_mu
                if flavor == 0: print 'ele misid', pt,  mis_hist_e
                elif flavor == 1: print 'muon misid', pt, mis_hist_mu
                nfakes += 1.
            else:
                # if flavor == 0: chain.efficiency *= eff_hist_e.evaluateEfficiency(chain, manual_var_entry = pt)
                # elif flavor == 1: chain.efficiency *= eff_hist_mu.evaluateEfficiency(chain, manual_var_entry = pt)
                # # if flavor == 0: print 'muon eff', eff_hist_e.evaluateEfficiency(chain, manual_var_entry = pt)
                # # elif flavor == 1: print 'eff', eff_hist_mu.evaluateEfficiency(chain, manual_var_entry = pt)
                if flavor == 0: chain.efficiency *= eff_hist_e
                elif flavor == 1: chain.efficiency *= eff_hist_mu
                if flavor == 0: print 'muon eff', eff_hist_e
                elif flavor == 1: print 'eff', eff_hist_mu

        # print 'tot:', chain.efficiency

        if nfakes > 0: list_of_hist[cat].fill(chain, weight)

            
    #
    # Save all histograms
    #
    for i, c_key in enumerate(list_of_hist.keys()):
            if i == 0:       list_of_hist[c_key].write(output_name, is_test=arg_string)
            else:            list_of_hist[c_key].write(output_name, is_test=arg_string, append=True)
            
    closeLogger(log)

else:

    from HNL.Tools.mergeFiles import merge
    import glob
    in_files = glob.glob(os.path.join(getOutputBase()))
    merge(in_files, __file__, jobs, ('sample', 'subJob'), argParser, istest=args.isTest)

    os.system('hadd -f '+getOutputBase()+'/averageObjectSelection.root '+getOutputBase()+'/averageObjectSelection-*.root')
