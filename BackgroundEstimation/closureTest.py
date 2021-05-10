#! /usr/bin/env python

#
#       Code to perform closure tests
#

import numpy as np
from HNL.Tools.histogram import Histogram
from HNL.Tools.helpers import makeDirIfNeeded, makePathTimeStamped

#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--flavorToTest',   action='store', nargs='*', default = None,  help='Select flavor to perform closure test on', choices=['ele', 'mu', 'tau'])
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018'])
submission_parser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
submission_parser.add_argument('--batchSystem',   action='store', default='HTCondor',  help='help')
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--noskim', action='store_true', default=False,  help='Use no skim sample list')
submission_parser.add_argument('--isCheck', action='store_true', default=False,  help='Check the setup by using the exact same region as the ttl measurement')
submission_parser.add_argument('--splitInCategories', action='store_true', default=False,  help='Split into different categories')
submission_parser.add_argument('--inData',   action='store_true', default=False,  help='Run in data')
submission_parser.add_argument('--region', action='store', default=None, type=str,  help='What region was the fake rate you want to use measured in?', 
    choices=['TauFakesDY', 'TauFakesTT', 'Mix'])
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
submission_parser.add_argument('--logLevel',  action='store',      default='INFO',               help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])

argParser.add_argument('--makePlots', action='store_true', default=False,  help='make plots')
argParser.add_argument('--stackMC', action='store_true', default=False,  help='take all MC together')

args = argParser.parse_args()

#
# Change some settings if this is a test
#
if args.isTest:
    args.isChild = True

    if args.sample is None: args.sample = 'DYJetsToLL-M-50'
    if args.subJob is None: args.subJob = '0'
    if args.year is None: args.year = '2016'
    if args.region is None: args.region = 'TauFakesDY'
    from HNL.Tools.helpers import generateArgString
    arg_string =  generateArgString(argParser)
else:
    arg_string = None

#
# Throws exceptions if arguments do not add up
#
if args.flavorToTest != ['tau']:
    if args.isCheck:
        raise RuntimeError("Nothing to check, you are using an imported fakerate")

if args.flavorToTest == ['tau']:
    if args.region is None:
        raise RuntimeError("Region should be defined for tau fakes")
        if args.isCheck:
            raise RuntimeError('Mix can not be used for check')

if args.selection == 'AN2017014':
    raise RuntimeError("selection AN2017014 currently not supported")

if args.inData and args.flavorToTest == 'ele' or args.flavorToTest == 'mu':
    raise RuntimeError("Closure test in data currently not supported for light leptons")

from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)

flavor_dict = {'tau' : 2, 'ele' : 0, 'mu' : 1}

if args.isChild and not args.inData and 'Data' in args.sample: exit(0)

#
# Load in the sample list 
#
from HNL.Samples.sampleManager import SampleManager
if args.noskim:
    skim_str = 'noskim'
else:
    skim_str = 'noskim' if args.selection == 'AN2017014' else 'Reco'

if not args.inData:
    # sublist = 'BackgroundEstimation/ClosureTests'
    sublist = 'fulllist_'+args.year+'_nosignal_mconly'
else:
    sublist = 'fulllist_'+args.year+'_nosignal'
sample_manager = SampleManager(args.year, skim_str, sublist)

this_file_name = __file__.split('.')[0].rsplit('/', 1)[-1]

#
# function to have consistent categories in running and plotting
#
from HNL.EventSelection.eventCategorization import ANALYSIS_CATEGORIES

jobs = []
for sample_name in sample_manager.sample_names:
    if args.sample and args.sample not in sample_name: continue
    sample = sample_manager.getSample(sample_name)
    for njob in xrange(sample.returnSplitJobs()):
        jobs += [(sample.name, str(njob))]

from HNL.BackgroundEstimation.fakerate import FakeRate
from HNL.BackgroundEstimation.fakerateEmulator import FakeRateEmulator
from HNL.BackgroundEstimation.closureObject import ClosureObject

if args.isCheck:
    var =  {'ptFakes':           (lambda c, i : c.l_pt[i],         np.array([20., 25., 35., 50., 70., 100.]),       ('p_{T} [GeV]', 'Events')),
            'etaFakes':          (lambda c, i : abs(c.l_eta[i]),        np.arange(0., 3.0, 0.5),       ('#eta', 'Events')),
    }
else:
    var = {
            'minMos':               (lambda c : c.minMos,       np.arange(0., 160., 10.),         ('min(M_{OS}) [GeV]', 'Events')),
            'm3l':                  (lambda c : c.M3l,          np.arange(0., 240., 15.),         ('M_{3l} [GeV]', 'Events')),
            'met':                  (lambda c : c._met,         np.arange(0., 300., 15.),         ('p_{T}^{miss} [GeV]', 'Events')),
            'mtOther':              (lambda c : c.mtOther,      np.arange(0., 300., 15.),       ('M_{T} (other min(M_{OS}) [GeV])', 'Events')),
            'ptFakes':              (lambda c, i : c.l_pt[i],         np.arange(0., 300., 15.),       ('p_{T} [GeV]', 'Events')),
            'etaFakes':             (lambda c, i : c.l_eta[i],        np.arange(-2.5, 3.0, 0.5),       ('#eta', 'Events')),
            'ptLeading':            (lambda c : c.l_pt[0],         np.arange(0., 300., 15.),       ('p_{T} [GeV]', 'Events')),
            'ptLeadingLukabins':    (lambda c : c.l_pt[0],         np.linspace(10., 200., num = 10),       ('p_{T} [GeV]', 'Events')),
            'etaLeading':           (lambda c : abs(c.l_eta[0]),        np.arange(0., 3.0, 0.5),       ('|#eta|', 'Events')),
            'etaLeadingFine':       (lambda c : abs(c.l_eta[0]),        np.arange(0, 2.75, 0.25),       ('|#eta|', 'Events')),
            'ptSubleading':         (lambda c : c.l_pt[1],         np.arange(0., 300., 15.),       ('p_{T} [GeV]', 'Events')),
            'ptSubleadingLukabins': (lambda c : c.l_pt[1],         np.linspace(10., 200., num = 10),       ('p_{T} [GeV]', 'Events')),
            'etaSubleading':        (lambda c : abs(c.l_eta[1]),        np.arange(0., 3.0, 0.5),       ('|#eta|', 'Events')),
            'etaSubleadingFine':    (lambda c : abs(c.l_eta[1]),        np.arange(0, 2.75, 0.25),       ('|#eta|', 'Events')),
            'ptTrailing':           (lambda c : c.l_pt[2],         np.arange(0., 300., 15.),       ('p_{T} [GeV]', 'Events')),
            'ptTrailingLukabins':   (lambda c : c.l_pt[2],         np.linspace(10., 200., num = 10),       ('p_{T} [GeV]', 'Events')),
            'etaTrailing':          (lambda c : abs(c.l_eta[2]),        np.arange(0., 3.0, 0.5),       ('|#eta|', 'Events')),
            'etaTrailingFine':      (lambda c : abs(c.l_eta[2]),        np.arange(0, 2.75, 0.25),       ('|#eta|', 'Events')),
            'mt3':                  (lambda c : c.mt3,          np.arange(0., 315., 15.),         ('M_{T}(3l) [GeV]', 'Events')),
            'LT':                   (lambda c : c.LT,           np.arange(0., 915., 15.),         ('L_{T} [GeV]', 'Events')),
            'HT':                   (lambda c : c.HT,           np.arange(0., 915., 15.),         ('H_{T} [GeV]', 'Events'))
    }   

subjobAppendix = 'subJob' + args.subJob if args.subJob else ''
data_str = 'DATA' if args.inData else 'MC'
def getOutputBase():
    flavors_to_test_str = '-'.join(sorted(args.flavorToTest))

    if not args.isTest:
        output_name = os.path.realpath(os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data', this_file_name, args.year, data_str, flavors_to_test_str))
    else:
        output_name = os.path.realpath(os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data', 'testArea', this_file_name, args.year, data_str, flavors_to_test_str))

    if args.flavorToTest == ['tau']:
        output_name = os.path.join(output_name, args.region)

    if args.isCheck:
        output_name += '/isCheck'
    return output_name

def getOutputName():
    output_name = getOutputBase()

    output_name += '/'+sample.output

    if args.isChild:
        output_name += '/tmp_'+sample.output

    output_name += '/'+ sample.name +'_events_' +subjobAppendix+ '.root'
    makeDirIfNeeded(output_name)
    return output_name

def getCategories():
    if args.splitInCategories:
        return ANALYSIS_CATEGORIES.keys() + ['total']
    else:
        return ['total']

from HNL.BackgroundEstimation.fakerateArray import loadFakeRatesWithJetBins, readFakeRatesWithJetBins, readFakeRatesWithBJetBins, FakeRateCollection, SingleFlavorFakeRateCollection
from HNL.BackgroundEstimation.getTauFakeContributions import getWeights
#
#   Code to process events
#
if not args.makePlots:
    #
    # Submit subjobs
    #
    if not args.isChild:
        from HNL.Tools.jobSubmitter import submitJobs
        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'closureTest')
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
        max_events = 20000
        event_range = xrange(max_events) if max_events < len(sample.getEventRange(args.subJob)) else sample.getEventRange(args.subJob)
    else:
        event_range = sample.getEventRange(args.subJob)    

    chain.HNLmass = sample.getMass()
    chain.year = int(args.year)
    chain.selection = args.selection

    #
    # Get luminosity weight
    #
    from HNL.Weights.reweighter import Reweighter
    reweighter = Reweighter(sample, sample_manager)

    #
    # Object ID param
    #
    from HNL.ObjectSelection.objectSelection import getObjectSelection
    chain.obj_sel = getObjectSelection(args.selection) #Working points are set in controlRegionManager.py

    from HNL.EventSelection.eventCategorization import EventCategory
    ec = EventCategory(chain)

    from HNL.EventSelection.eventSelector import EventSelector
    if args.isCheck:
        if args.flavorToTest == ['tau']:
            es = EventSelector(args.region, chain, chain, True, ec)    
        else:
            raise RuntimeError("Wrong input for flavorToTest with isCheck arg on: "+str(args.flavorToTest))
    else:
        if not args.inData:
            es = EventSelector('MCCT', chain, chain, True, ec, additional_options=args.flavorToTest) 
        else:
            es = EventSelector('DataCT', chain, chain, True, ec, additional_options=args.flavorToTest) 

    fakerate = {}
    if 'tau' in args.flavorToTest:
        base_path_tau = lambda proc : os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'BackgroundEstimation', 'data', 'tightToLoose', args.year, data_str, 'tau', 'TauFakes'+proc, proc, 'events.root'))
        if args.region == 'TauFakesDY':
            fakerate[2] = FakeRate('tauttl', lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), base_path_tau('DY'), subdirs = ['total'])
        elif args.region == 'TauFakesTT':
            fakerate[2] = FakeRate('tauttl', lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), base_path_tau('TT'), subdirs = ['total'])
        else:
            fakerate[2] = SingleFlavorFakeRateCollection([base_path_tau('DY'), base_path_tau('TT')], ['total/tauttl', 'total/tauttl'], ['DY', 'TT'], weights = getWeights(args.year, args.selection, 'TauMixCT'), names = ['DY', 'TT'])
            # fakerate[2] = SingleFlavorFakeRateCollection([base_path_tau('DY'), base_path_tau('TT')], ['total/tauttl', 'total/tauttl'], ['DY', 'TT'], weights = getWeights(args.year, args.selection, 'MCCT'), names = ['DY', 'TT'])
            # fakerate[2] = SingleFlavorFakeRateCollection([base_path_tau('DY'), base_path_tau('TT')], ['total/tauttl', 'total/tauttl'], ['DY', 'TT'], weights = getWeights(args.year, args.selection, 'highMassSR'), names = ['DY', 'TT'])
    else:
        fakerate[2] = None
    if 'ele' in args.flavorToTest: 
        if args.inData:
            fakerate[0] = FakeRateEmulator('fakeRate_electron_'+args.year, lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data','FakeRates', args.year, 'Lukav2', 'fakeRateMap_data_electron_'+args.year+'_mT.root'))
        else:
            fakerate[0] = FakeRateEmulator('fakeRate_electron_'+args.year, lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data','FakeRates', args.year, 'Lukav2', 'fakeRateMap_MC_electron_'+args.year+'.root'))
    else:
        fakerate[0] = None
    if 'mu' in args.flavorToTest: 
        if args.inData:
            fakerate[1] = FakeRateEmulator('fakeRate_muon_'+args.year, lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data','FakeRates', args.year, 'Lukav2', 'fakeRateMap_data_muon_'+args.year+'_mT.root'))
        else:
            fakerate[1] = FakeRateEmulator('fakeRate_muon_'+args.year, lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data','FakeRates', args.year, 'Lukav2', 'fakeRateMap_MC_muon_'+args.year+'.root'))
    else:
        fakerate[1] = None

    fakerate_collection = FakeRateCollection(chain, fakerate)

    co = {}
    for c in getCategories():
        co[c] = {}
        for v in var:
            co[c][v] = ClosureObject('closure-'+v+'-'+c, var[v][0], var[v][2], getOutputName(), bins = var[v][1])

    #
    # Loop over all events
    #
    from HNL.Tools.helpers import progress
    from HNL.Triggers.triggerSelection import passTriggers

    print 'tot_range', len(event_range)
    for entry in event_range:
        chain.GetEntry(entry)
        progress(entry - event_range[0], len(event_range))

        cutter.cut(True, 'total')
        #
        #Triggers
        #
        if args.selection == 'AN2017014':
            if not cutter.cut(passTriggers(chain, 'HNL_old'), 'pass_triggers'): continue
        else:
            if not cutter.cut(passTriggers(chain, 'HNL'), 'pass_triggers'): continue

        #Event selection  
        if not es.removeOverlapDYandZG(sample.output): continue
        if not es.selector.passedFilter(cutter, args.region): continue
            
        if args.inData and not chain.is_data:
            fake_index = es.selector.getFakeIndex()
            if chain.l_isfake[fake_index]: continue

        cat = ec.returnAnalysisCategory()

        fake_factor = fakerate_collection.getFakeWeight()
        weight = reweighter.getLumiWeight()

        for v in var:
            if v == 'ptFakes' or v == 'etaFakes':
                #Special case, only for taus, in which case there is only one tau which is in the last position
                if args.isCheck:
                    if args.splitInCategories: co[cat][v].fillClosure(chain, weight, fake_factor, index=2)
                    co['total'][v].fillClosure(chain, weight, fake_factor, index=2)
                else:
                    #General case
                    for l in es.selector.loose_leptons_of_interest:
                        if args.splitInCategories: co[cat][v].fillClosure(chain, weight, fake_factor, index=l)
                        co['total'][v].fillClosure(chain, weight, fake_factor, index=l)
            else:
                if args.splitInCategories: co[cat][v].fillClosure(chain, weight, fake_factor)
                co['total'][v].fillClosure(chain, weight, fake_factor)
    
    for i, c in enumerate(getCategories()):
        for j, v in enumerate(var):
            if i == 0 and j == 0:
                co[c][v].write(is_test=arg_string)
            else:
                co[c][v].write(append=True, is_test=arg_string)

    print "Observed:", co['total']['m3l'].getObserved().GetSumOfWeights()
    print "Predicted:", co['total']['m3l'].getSideband().GetSumOfWeights()

    for b in xrange(1, co['total']['etaFakes'].getObserved().GetNbinsX()+1):
        print "bin", b, "at eta =", co['total']['etaFakes'].getObserved().GetBinCenter(b), ":" 
        print "OBSERVED:",  co['total']['etaFakes'].getObserved().GetBinContent(b)
        print "PREDICTED:",  co['total']['etaFakes'].getSideband().GetBinContent(b)

    cutter.saveCutFlow(getOutputName())

    closeLogger(log)

else:
    from HNL.Tools.mergeFiles import merge
    import glob
    from HNL.Tools.helpers import getObjFromFile, mergeHistograms
    from HNL.Plotting.plot import Plot

    base_path = getOutputBase()

    in_files = glob.glob(os.path.join(base_path, '*'))
    merge(in_files, __file__, jobs, ('sample', 'subJob'), argParser, istest=args.isTest)

    base_path_split  = base_path.rsplit('/data/')
    output_dir = makePathTimeStamped(base_path_split[0] +'/data/Results/'+base_path_split[1])

    closureObjects = {}
    for in_file in in_files:
        if 'Results' in in_file: continue
        if 'isCheck' in in_file and not args.isCheck: continue
        sample_name = in_file.rsplit('/', 1)[-1]
        closureObjects[sample_name] = {}
        for c in getCategories():
            closureObjects[sample_name][c] = {}
            for v in var:
                print in_file+'/events.root'
                closureObjects[sample_name][c][v] = ClosureObject('closure-'+v+'-'+c, None, None, in_file+'/events.root')

    if not args.inData and not args.stackMC:
        for sample_name in closureObjects.keys():
            for c in getCategories():
                for v in var:
                    p = Plot(name = v, signal_hist = closureObjects[sample_name][c][v].getObserved(), bkgr_hist = closureObjects[sample_name][c][v].getSideband(), color_palette='Black', color_palette_bkgr='Stack', tex_names = ["Observed", 'Predicted'], draw_ratio = True)
                    p.drawHist(output_dir = output_dir+'/'+sample_name+'/'+c, draw_option='EP')
    else:
        for c in getCategories():
            for v in var:
                if args.inData:
                    backgrounds = [closureObjects["Data"][c][v].getSideband()]
                    background_names = ['Predicted']
                else:
                    backgrounds = []
                    background_names = []

                tmp_bkgr_collection = {}
                for sample_name in closureObjects.keys():
                    if 'Data' in sample_name: continue
                    tmp_bkgr_collection[sample_name] = closureObjects[sample_name][c][v].getSideband()

                grouped_backgrounds = mergeHistograms(tmp_bkgr_collection, sample_manager.sample_groups)
                for b in grouped_backgrounds:
                    backgrounds.append(grouped_backgrounds[b])
                    background_names.append(b)

                if args.inData:
                    signal_h = closureObjects['Data'][c][v].getObserved()
                else:
                    for isample, sample_name in enumerate(closureObjects.keys()):
                        if 'Data' in sample_name: continue
                        if isample == 0:
                            signal_h = closureObjects[sample_name][c][v].getObserved()
                        else:
                            signal_h.Add(closureObjects[sample_name][c][v].getObserved())

                p = Plot(name = v, signal_hist = signal_h, bkgr_hist = backgrounds, color_palette='Black', color_palette_bkgr='StackTauPOGbyName', tex_names = ["Observed"]+background_names, draw_ratio = True, year = args.year)
                p.drawHist(output_dir = output_dir+'/'+'/'+c, draw_option='EP')
        