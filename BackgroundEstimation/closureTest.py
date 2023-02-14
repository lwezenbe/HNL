#! /usr/bin/env python

#
#       Code to perform closure tests
#

import numpy as np
from HNL.Tools.helpers import makeDirIfNeeded, makePathTimeStamped

#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--flavorToTest',   action='store', nargs='*', default = None,  help='Select flavor to perform closure test on')
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='UL', choices = ['UL', 'prelegacy'],   help='Select era')
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
submission_parser.add_argument('--region', action='store', default=None, type=str,  help='What region was the tau fake closure test you want to use measured in?', choices=['TauFakesDYCT', 'TauFakesTT', 'MCCT', 'LightLepFakesDYCT', 'LightLepFakesTTCT', 'TauMixCT', 'TauFakesDYCTnomet', 'TauFakesTTCT', 'highMassSRnoOSSF', 'highMassSROSSF'])
submission_parser.add_argument('--analysis',   action='store', default='HNL',  help='Select the strategy to use to separate signal from background', choices=['HNL', 'AN2017014', 'ewkino'])
submission_parser.add_argument('--application', action='store', default=None, type=str,  help='What region was the tau fake rate you want to use applied for?', 
    choices=['TauFakesDY', 'TauFakesDYnomet', 'TauFakesTT', 'WeightedMix', 'OSSFsplitMix'])
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
submission_parser.add_argument('--logLevel',  action='store', default='INFO', help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])

argParser.add_argument('--makePlots', action='store_true', default=False,  help='make plots')

args = argParser.parse_args()

#
# Change some settings if this is a test
#
if args.isTest:
    args.isChild = True

    if args.sample is None: args.sample = 'TTJets-Dilep'
    if args.subJob is None: args.subJob = '0'
    if args.year is None: args.year = '2017'
    if args.region is None: args.region = 'TauFakesDY'
    if args.application is None: args.application = args.region if args.region in ['TauFakesDY', 'TauFakesTT'] else 'TauFakesDY'
    from HNL.Tools.helpers import generateArgString
    arg_string =  generateArgString(argParser)
else:
    arg_string = None

#
# Throws exceptions if arguments do not add up
#
#if args.flavorToTest != ['tau']:
#    if args.isCheck:
#        raise RuntimeError("Nothing to check, you are using an imported fakerate")
#
#if args.flavorToTest == ['tau']:
#    if args.region is None:
#        raise RuntimeError("Region should be defined for tau fakes")
#
#if args.selection == 'AN2017014':
#    raise RuntimeError("selection AN2017014 currently not supported")
#
#if args.inData and args.flavorToTest == 'ele' or args.flavorToTest == 'mu':
#    raise RuntimeError("Closure test in data currently not supported for light leptons")

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
    skim_str = 'Reco'

if not args.inData:
    sublist = 'BackgroundEstimation/TauFakes-'+args.era+args.year
else:
    sublist = 'fulllist_'+args.era+args.year
sample_manager = SampleManager(args.era, args.year, skim_str, sublist, skim_selection=args.selection)

this_file_name = __file__.split('.')[0].rsplit('/', 1)[-1]

#
# function to have consistent categories in running and plotting
#
from HNL.EventSelection.eventCategorization import ANALYSIS_CATEGORIES

jobs = []
for sample_name in sample_manager.sample_names:
    if args.sample and args.sample not in sample_name: continue
    if 'HNL' in sample_name: continue
    sample = sample_manager.getSample(sample_name)
#    if not args.inData and args.application == 'TauFakesDY' and not 'DY' in sample.name: continue
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
            #'met':                  (lambda c : c._met,         np.arange(0., 90., 3.),         ('p_{T}^{miss} [GeV]', 'Events')),
            #'met':                  (lambda c : c._met,         np.arange(50., 123., 3.),         ('p_{T}^{miss} [GeV]', 'Events')),
            'mtOther':              (lambda c : c.mtOther,      np.arange(0., 230., 15.),       ('M_{T} (other min(M_{OS}) [GeV])', 'Events')),
            'ptFakes':              (lambda c, i : c.l_pt[i],         np.arange(0., 300., 15.),       ('p_{T} [GeV]', 'Events')),
            'etaFakes':             (lambda c, i : c.l_eta[i],        np.arange(-2.5, 3.0, 0.5),       ('#eta', 'Events')),
            'ptLeading':            (lambda c : c.l_pt[0],         np.arange(0., 100., 15.),       ('p_{T}(leading) [GeV]', 'Events')),
            'ptLeadingLukabins':    (lambda c : c.l_pt[0],         np.linspace(10., 200., num = 10),       ('p_{T}(leading) [GeV]', 'Events')),
            'etaLeading':           (lambda c : abs(c.l_eta[0]),        np.arange(0., 3.0, 0.5),       ('|#eta(leading)|', 'Events')),
            'etaLeadingFine':       (lambda c : abs(c.l_eta[0]),        np.arange(0, 2.75, 0.25),       ('|#eta(leading)|', 'Events')),
            'ptSubleading':         (lambda c : c.l_pt[1],         np.arange(0., 100., 15.),       ('p_{T}(subleading) [GeV]', 'Events')),
            'ptSubleadingLukabins': (lambda c : c.l_pt[1],         np.linspace(10., 200., num = 10),       ('p_{T}(subleading) [GeV]', 'Events')),
            'etaSubleading':        (lambda c : abs(c.l_eta[1]),        np.arange(0., 3.0, 0.5),       ('|#eta(subleading)|', 'Events')),
            'etaSubleadingFine':    (lambda c : abs(c.l_eta[1]),        np.arange(0, 2.75, 0.25),       ('|#eta(subleading)|', 'Events')),
            'ptTrailing':           (lambda c : c.l_pt[2],         np.arange(0., 100., 15.),       ('p_{T}(trailing) [GeV]', 'Events')),
            'ptTrailingLukabins':   (lambda c : c.l_pt[2],         np.linspace(10., 200., num = 10),       ('p_{T}(trailing) [GeV]', 'Events')),
            'etaTrailing':          (lambda c : abs(c.l_eta[2]),        np.arange(0., 3.0, 0.5),       ('|#eta(trailing)|', 'Events')),
            'etaTrailingFine':      (lambda c : abs(c.l_eta[2]),        np.arange(0, 2.75, 0.25),       ('|#eta(trailing)|', 'Events')),
            'mt3':                  (lambda c : c.mt3,          np.arange(0., 315., 15.),         ('M_{T}(3l) [GeV]', 'Events')),
            'LT':                   (lambda c : c.LT,           np.arange(0., 915., 15.),         ('L_{T} [GeV]', 'Events')),
            'HT':                   (lambda c : c.HT,           np.arange(0., 915., 15.),         ('H_{T} [GeV]', 'Events')),
            'ml12':          (lambda c : c.Ml12,      np.arange(0., 240., 5.),         ('M_{l1l2} [GeV]', 'Events')),
            'ml23':          (lambda c : c.Ml23,      np.arange(0., 240., 5.),         ('M_{l2l3} [GeV]', 'Events')),
            'ml13':          (lambda c : c.Ml13,      np.arange(0., 240., 5.),         ('M_{l1l3} [GeV]', 'Events')),
            'mtl1':          (lambda c : c.mtl1,      np.arange(0., 240., 5.),         ('M_{l1l3} [GeV]', 'Events')),
            'mtl2':          (lambda c : c.mtl2,      np.arange(0., 240., 5.),         ('M_{l1l3} [GeV]', 'Events')),
            'mtl3':          (lambda c : c.mtl3,      np.arange(0., 240., 5.),         ('M_{l1l3} [GeV]', 'Events')),
            'mzossf':          (lambda c : c.MZossf,      np.arange(0., 240., 5.),         ('M_{ll,Z} [GeV]', 'Events')),
            'mtnonossf':          (lambda c : c.mtNonZossf,      np.arange(0., 240., 5.),         ('M_{ll,Z} [GeV]', 'Events')),
            'NJet':      (lambda c : c.njets,       np.arange(0., 12., 1.),       ('#Jets', 'Events')),
            'NbJet':      (lambda c : c.nbjets,       np.arange(0., 12., 1.),       ('#B Jets', 'Events')),
            'Nele':      (lambda c : len([x for x in c.l_flavor if x == 0]),       np.arange(0., 4., 1.),       ('#electrons', 'Events')),
            'Nmu':      (lambda c : len([x for x in c.l_flavor if x == 1]),       np.arange(0., 4., 1.),       ('#muons', 'Events')),
            'Ntau':      (lambda c : len([x for x in c.l_flavor if x == 2]),       np.arange(0., 4., 1.),       ('#taus', 'Events')),
            'tauDecayMode':      (lambda c, i : c._tauDecayMode[i],       np.arange(-0.5, 11.5, 1.),       ('tau DM', 'Events'))
    }  

if not args.inData:
    var['tauGenStatus'] = (lambda c, i : c._tauGenStatus[i],       np.arange(0.5, 7.5, 1.),       ('TauGenStatus', '#taus')) 
    var['provenance'] = (lambda c, i : c._lProvenance[i],       np.arange(0.5, 20.5, 1.),       ('Provenance', '#taus')) 
    var['provenanceCompressed'] = (lambda c, i : c._lProvenanceCompressed[i],       np.arange(0.5, 7.5, 1.),       ('Provenance', '#taus')) 

subjobAppendix = 'subJob' + args.subJob if args.subJob else ''
data_str = 'DATA' if args.inData else 'MC'
def getOutputBase():
    flavors_to_test_str = '-'.join(sorted(args.flavorToTest))

    if not args.isTest:
        output_name = os.path.realpath(os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data', this_file_name, args.era+'-'+args.year, data_str, flavors_to_test_str))
    else:
        output_name = os.path.realpath(os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'BackgroundEstimation', 'data', 'testArea', this_file_name, 
                                        args.era+'-'+args.year, data_str, flavors_to_test_str))

    if args.flavorToTest == ['tau']:
        output_name = os.path.join(output_name, args.region, str(args.application))
    else:
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

from HNL.BackgroundEstimation.fakerateArray import FakeRateCollection, SingleFlavorFakeRateCollection
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
        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'closureTest-'+args.era+args.year+'-'+str(args.application))
        exit(0)

    #
    # Load in sample and chain
    #
    sample = sample_manager.getSample(args.sample)
    chain = sample.initTree(needhcount = False)

    #
    # Import and create cutter to provide cut flow
    #
    from HNL.EventSelection.bitCutter import Cutter
    cutter = Cutter(name = 'closure', chain = chain, categories = 'auto')

    if args.isTest:
        max_events = 20000
        event_range = xrange(max_events) if max_events < len(sample.getEventRange(args.subJob)) else sample.getEventRange(args.subJob)
    else:
        event_range = sample.getEventRange(args.subJob)    

    from HNL.Samples.sample import Sample
    chain.HNLmass = Sample.getSignalMass(sample.name)

    from HNL.EventSelection.event import ClosureTestEvent
    if args.isCheck:
        if args.flavorToTest == ['tau']:
            event =  ClosureTestEvent(sample, chain, sample_manager, is_reco_level=True, selection=args.selection, strategy='MVA', region=args.region, flavors_of_interest=args.flavorToTest, in_data=args.inData, analysis=args.analysis, year=args.year, era = args.era) 
        else:
            raise RuntimeError("Wrong input for flavorToTest with isCheck arg on: "+str(args.flavorToTest))
    else:
        event =  ClosureTestEvent(sample, chain, sample_manager, is_reco_level=True, selection=args.selection, strategy='MVA', region=args.region, flavors_of_interest=args.flavorToTest, in_data=args.inData, analysis=args.analysis, year=args.year, era = args.era) 

    #
    # Get luminosity weight
    #
    from HNL.Weights.reweighter import Reweighter
    reweighter = Reweighter(sample, sample_manager, ignore_fakerates=True)

    fakerate = {}
    if 'tau' in args.flavorToTest:
        if not args.inData:
            base_path_tau = lambda proc : os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'BackgroundEstimation', 'data', 'tightToLoose', 
                                                                        args.era+'-'+args.year, data_str, 'tau', 'TauFakes'+proc+'ttl-'+args.selection, proc, 'events.root'))
        else:
            base_path_tau = lambda proc : os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'BackgroundEstimation', 'data', 'tightToLoose', 
                                                                        args.era+'-'+args.year, data_str, 'tau', 'TauFakes'+proc+'ttl-'+args.selection, 'events.root'))
        #bins = (np.array([20., 25., 35., 50., 70., 100.]), np.arange(0., 3.0, 0.5), np.arange(-0.5, 12.5, 0.5))
        bins = (np.array([20., 25., 35., 50., 70., 100.]), np.arange(0., 3.0, 0.5))
        if args.application == 'TauFakesDY':
            #fakerate[2] = FakeRate('tauttl', lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), base_path_tau('DY'), subdirs = ['total'])
            if args.year == '2016pre' and args.inData:
                #fakerate[2] = FakeRate.getFakeRateFromTree('ttl', base_path_tau('DY'), "l_pt-abs(l_eta)-l_decaymode", bins, var = lambda c, i: [c.l_pt[i], abs(c.l_eta[i]), c._tauDecayMode[c.l_indices[i]]])
                fakerate[2] = FakeRate.getFakeRateFromTree('ttl', base_path_tau('DY'), "l_pt-abs(l_eta)", bins, var = lambda c, i: [c.l_pt[i], abs(c.l_eta[i])])
            else:
                #fakerate[2] = FakeRate('tauttl', lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), base_path_tau('DY'), subdirs = ['total'])
                fakerate[2] = FakeRate.getFakeRateFromTree('ttl', base_path_tau('DY'), "l_pt-abs(l_eta)", bins, var = lambda c, i: [c.l_pt[i], abs(c.l_eta[i])])
        elif args.application == 'TauFakesTT':
            fakerate[2] = FakeRate.getFakeRateFromTree('ttl', base_path_tau('TT'), "l_pt-abs(l_eta)", bins, var = lambda c, i: [c.l_pt[i], abs(c.l_eta[i])])
        elif args.application == 'WeightedMix':
            fakerate[2] = SingleFlavorFakeRateCollection([base_path_tau('DY'), base_path_tau('TT')], ['total/tauttl', 'total/tauttl'], ['DY', 'TT'], 
                                                            frac_weights = getWeights(args.era, args.year, args.selection, args.region), frac_names = ['DY', 'TT'])   
        elif args.application == 'OSSFsplitMix':
                fakerate[2] = SingleFlavorFakeRateCollection([base_path_tau('DY'), base_path_tau('TT')], ['total/tauttl', 'total/tauttl'], ['DY', 'TT'], method = 'OSSFsplitMix',
                                                    ossf_map = {True : 'DY', False : 'TT'})  
    else:
        fakerate[2] = None

    luka_year_dict = {
        '2016pre' : '2016Merged',    
        '2016post' : '2016Merged',    
        '2017' : '2017',    
        '2018' : '2018',    
    }
    if 'ele' in args.flavorToTest: 
        if args.inData:
            fakerate[0] = FakeRateEmulator('fakeRate_electron_'+luka_year_dict[args.year], lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), os.path.join(os.path.expandvars('$CMSSW_BASE'), 
                                            'src', 'HNL', 'BackgroundEstimation', 'data', 'FakeRates', args.era+'-'+args.year, 'fakeRateMap_data_electron_'+luka_year_dict[args.year]+'_mT.root'))
        else:
            fakerate[0] = FakeRateEmulator('fakeRate_electron_'+luka_year_dict[args.year], lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), os.path.join(os.path.expandvars('$CMSSW_BASE'), 
                                            'src', 'HNL', 'BackgroundEstimation', 'data', 'FakeRates', args.era+'-'+args.year, 'fakeRateMap_MC_electron_'+luka_year_dict[args.year]+'.root'))
    else:
        fakerate[0] = None
    if 'mu' in args.flavorToTest: 
        if args.inData:
            fakerate[1] = FakeRateEmulator('fakeRate_muon_'+luka_year_dict[args.year], lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 
                                            'HNL', 'BackgroundEstimation', 'data', 'FakeRates', args.era+'-'+args.year, 'fakeRateMap_data_muon_'+luka_year_dict[args.year]+'_mT.root'))
        else:
            fakerate[1] = FakeRateEmulator('fakeRate_muon_'+luka_year_dict[args.year], lambda c, i: [c.l_pt[i], c.l_eta[i]], ('pt', 'eta'), os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 
                                            'HNL', 'BackgroundEstimation', 'data', 'FakeRates', args.era+'-'+args.year, 'fakeRateMap_MC_muon_'+luka_year_dict[args.year]+'.root'))
            
    else:
        fakerate[1] = None

    fakerate_collection = FakeRateCollection(chain, fakerate)

    co = {}
    branches = []
    for v in var.keys():
        branches.extend(['{0}/F'.format(v)]) 
    branches.extend(['category/I'])
    from HNL.BackgroundEstimation.closureObject import ClosureTree
    co = ClosureTree('closure', getOutputName(), branches = branches)

    #
    # Loop over all events
    #
    from HNL.Tools.helpers import progress
    from HNL.Triggers.triggerSelection import passTriggers

    print 'tot_range', len(event_range)
    for entry in event_range:

        chain.GetEntry(entry)
        if args.isTest: progress(entry - event_range[0], len(event_range))

        cutter.cut(True, 'total')
        #
        #Triggers
        #
        if args.selection == 'AN2017014':
            if not cutter.cut(passTriggers(chain, 'HNL_old'), 'pass_triggers'): continue
        else:
            if not cutter.cut(passTriggers(chain, 'HNL'), 'pass_triggers'): continue

        #Event selection 
        event.initEvent()
        if not event.passedFilter(cutter, sample.name): continue

        fake_index = event.getFakeIndex()
        if args.inData and not chain.is_data:
            if any([chain.l_isfake[i] for i in fake_index]): continue
   
        cat = event.event_category.returnCategory()

        fake_factor = fakerate_collection.getFakeWeight()
        weight = reweighter.getTotalWeight()

        for v in var:
            try:
                co.setTreeVariable(v, var[v][0](chain))   
            except:
                co.setTreeVariable(v, var[v][0](chain, fake_index[0]))   
        co.setTreeVariable('category', cat)
        co.fill(weight, fake_factor)

    co.write(is_test=arg_string)

    cutter.saveCutFlow(getOutputName())

    closeLogger(log)

else:
    from HNL.Tools.mergeFiles import merge
    import glob
    from HNL.Tools.helpers import mergeHistograms
    from HNL.Plotting.plot import Plot

    base_path = getOutputBase()

    in_files = [x for x in glob.glob(os.path.join(base_path, '*')) if x.rsplit('/', 1)[-1] in sample_manager.sample_outputs]
    merge(in_files, __file__, jobs, ('sample', 'subJob'), argParser, istest=args.isTest)

    base_path_split  = base_path.rsplit('/data/')
    output_dir = makePathTimeStamped(base_path_split[0] +'/data/Results/'+base_path_split[1])

    from HNL.BackgroundEstimation.closureObject import ClosureTree
    closure_trees = {}
    for in_file in in_files:
        if 'Results' in in_file: continue
        if 'isCheck' in in_file and not args.isCheck: continue
        sample_name = in_file.rsplit('/', 1)[-1]
        closure_trees[sample_name] = ClosureTree('closure', in_file+'/events.root')

    #condition = "tauDecayMode!=0"
    condition = None
    if not args.inData:
        for sample_name in closure_trees.keys():
            for v in var:
                p = Plot(name = v, observed_hist = closure_trees[sample_name].getObserved(v, v+'-'+sample_name, var[v][1], condition=condition), bkgr_hist = closure_trees[sample_name].getSideband(v, v+'-'+sample_name, var[v][1], condition=condition), 
                            color_palette='Black', color_palette_bkgr='Stack', tex_names = ['Predicted'], draw_ratio = True, year = args.year, era = args.era,
                            x_name = var[v][2][0], y_name = var[v][2][1])
                p.setLegend(x1 = 0.5, ncolumns = 1)
                p.drawHist(output_dir = output_dir+'/'+sample_name+'/total', observed_name = 'Observed')

    for v in var:
        if args.inData:
            observed_h = closure_trees['Data'].getObserved(v, v+'-'+sample_name, var[v][1], condition)
            for isample, sample_name in enumerate(closure_trees.keys()):
                if 'Data' in sample_name: continue
                else:
                    observed_h.Add(closure_trees[sample_name].getSideband(v, v+'-'+sample_name, var[v][1], condition), -1.)
        else:
            for isample, sample_name in enumerate(closure_trees.keys()):
                if 'Data' in sample_name: continue
                if isample == 0:
                    observed_h = closure_trees[sample_name].getObserved(v, v+'-'+sample_name, var[v][1], condition)
                else:
                    observed_h.Add(closure_trees[sample_name].getObserved(v, v+'-'+sample_name, var[v][1], condition))

            
        bkgr_collection = {}
        if args.inData:
            backgrounds = [closure_trees["Data"].getSideband(v, v+'-'+sample_name, var[v][1], condition)]
            background_names = ['Predicted']
            for sample_name in closure_trees.keys():
                if 'Data' in sample_name: continue
                bkgr_collection[sample_name] = closure_trees[sample_name].getObserved(v, v+'-'+sample_name, var[v][1])
                backgrounds[0].Add(closure_trees[sample_name].getSideband(v, v+'-'+sample_name, var[v][1], condition), -1.)
        else:
            backgrounds = []
            background_names = []

            for sample_name in closure_trees.keys():
                if 'Data' in sample_name: continue
                bkgr_collection[sample_name] = closure_trees[sample_name].getSideband(v, v+'-'+sample_name, var[v][1])

        for b in bkgr_collection:
            backgrounds.append(bkgr_collection[b])
            background_names.append(b)

        p = Plot(name = v, bkgr_hist = backgrounds, observed_hist = observed_h, color_palette='Black', tex_names = background_names, 
                    draw_ratio = True, year = args.year, era = args.era, x_name = var[v][2][0], y_name = var[v][2][1], syst_hist = 0.3)
        p.setLegend(x1 = 0.5, ncolumns = 2)
        p.drawHist(output_dir = output_dir+'/Stacked/total', observed_name = 'Observed')

