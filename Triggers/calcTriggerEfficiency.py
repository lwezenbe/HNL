#! /usr/bin/env python

#
# Argument parser and logging
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true',       default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store', nargs='*',    default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='UL', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--sample',   action='store',            default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',            default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isTest',   action='store_true',       default=False,  help='Run a small test')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--dryRun',   action='store_true',       default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--genLevel',   action='store_true',     default=False,  help='Use gen level variables')
submission_parser.add_argument('--region',   action='store', default='trilepton',  help='Select the type of selection for objects', choices=['trilepton', 'baseline'])
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
submission_parser.add_argument('--analysis',   action='store', default='HNL',  help='Select the analysis which triggers to use', choices=['AN2017014', 'HNL' ])
submission_parser.add_argument('--logLevel',  action='store', default='INFO',  help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])
submission_parser.add_argument('--customList',  action='store',      default=None,               help='Name of a custom sample list. Otherwise it will use the appropriate noskim file.')
submission_parser.add_argument('--useRef', action='store_true', default=False,  help='pass ref cuts')
submission_parser.add_argument('--noskim', action='store_true', default=False,  help='pass ref cuts')
submission_parser.add_argument('--noOfflineThresholds', action='store_true', default=False,  help='Skip offline threshold cut')
submission_parser.add_argument('--closureTest', action='store_true', default=False,  help='apply SF')
submission_parser.add_argument('--separateTriggers', action='store', default=None,  
    help='Look at each trigger separately for each set of triggers. Single means just one trigger, cumulative uses cumulative OR of all triggers that come before the chosen one in the list, full applies all triggers for a certain category', 
    choices=['single', 'cumulative', 'full'])
argParser.add_argument('--makePlots',   action='store_true',    default=False,  help='Use existing root files to make the plots')
argParser.add_argument('--storeSF',   action='store_true',    default=False,  help='Store the SF for use in analysis')

args = argParser.parse_args()

import numpy as np
import os
from HNL.Tools.efficiency import Efficiency
from HNL.EventSelection.eventCategorization import CATEGORIES_TO_USE as CATEGORIES

#
# Change some settings if this is a test
#
if args.isTest: 
    args.isChild = True
    if args.sample is None and not args.makePlots: args.sample = 'WZTo3LNu'
    if args.subJob is None: args.subJob = '0'
    if args.year is None: args.year = ['2017']
    if args.era is None: args.era = 'UL'
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
    if not args.noskim:
        return SampleManager(args.era, year, 'auto', 'Triggers/triggerlist_'+args.era+str(year), skim_selection=args.selection, region = args.region)
    else:
        return SampleManager(args.era, year, 'noskim', 'Triggers/triggerlist_'+args.era+str(year))

#
# Prepare jobs
#
jobs = {}
from HNL.Tools.jobSubmitter import checkShouldMerge
skip_running_jobs = args.makePlots and not any([checkShouldMerge(__file__, argParser, additionalArgs=[('year', year)]) for year in args.year])
if not args.isTest and not skip_running_jobs:
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
                                    args.era+year, sep_trig_name, 'ClosureTest' if args.closureTest else '',  '-'.join([args.selection, args.analysis, ref_name]), sample_name)
    else:
        output_string = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Triggers', 'data', 'testArea', __file__.split('.')[0].rsplit('/')[-1], 
                                    args.era+year, sep_trig_name, 'ClosureTest' if args.closureTest else '', '-'.join([args.selection, args.analysis, ref_name]), sample_name)
    return output_string


def getOutputName(year, sample_name):
    subjobAppendix = 'subJob' + args.subJob if args.subJob else ''
    return os.path.join(getOutputBase(year, sample_name), 'tmp_'+sample_name, '_'.join([sample_name, 'efficiency', subjobAppendix])+'.root')

from HNL.Tools.outputTree import EfficiencyTree
from HNL.Tools.helpers import progress

#
# Define variables
#
leading_lep_split = [15., 30., 55., 'inf']

leading_lep_cat = [str(leading_lep_split[i])+'to'+str(leading_lep_split[i+1]) for i in xrange(len(leading_lep_split)-1)]
if len(leading_lep_split) > 2:
    leading_lep_cat += [str(leading_lep_split[0])+'to'+str(leading_lep_split[-1])]

var = {
#    'l1pt' : (lambda c : c.l_pt[0],                          np.arange(0., 100., 15.),                 ('p_{T}(l1) [GeV]', 'Efficiency')),
#    'l2pt' : (lambda c : c.l_pt[1],                          np.arange(5., 80., 5.),                  ('p_{T}(l2) [GeV]', 'Efficiency')),
#    'l3pt' : (lambda c : c.l_pt[2],                          np.arange(5., 80., 5.),                  ('p_{T}(l3) [GeV]', 'Efficiency')),
    'light1pt' : (lambda c : c.light_pt[0],                          np.arange(0., 110., 2.),                 ('p_{T}(light lep 1) [GeV]', 'Efficiency')),
    'light2pt' : (lambda c : c.light_pt[1],                          np.arange(10., 110., 2.),                  ('p_{T}(light lep 2) [GeV]', 'Efficiency')),
    #'l1pt' : (lambda c : c.l_pt[0],                          np.arange(0., 100., 2.),                 ('p_{T}(l1) [GeV]', 'Efficiency')),
    #'l2pt' : (lambda c : c.l_pt[1],                          np.arange(5., 80., 2.),                  ('p_{T}(l2) [GeV]', 'Efficiency')),
    #'l3pt' : (lambda c : c.l_pt[2],                          np.arange(5., 80., 2.),                  ('p_{T}(l3) [GeV]', 'Efficiency')),
#    'abs(l1eta)' : (lambda c : abs(c.l_eta[0]),                          np.arange(0., 3., .5),                  ('|#eta|(l1) [GeV]', 'Efficiency')),
#    'abs(l2eta)' : (lambda c : abs(c.l_eta[1]),                          np.arange(0., 3., .5),                  ('|#eta|(l2) [GeV]', 'Efficiency')),
#    'abs(l3eta)' : (lambda c : abs(c.l_eta[2]),                          np.arange(0., 3., .5),                  ('|#eta|(l3) [GeV]', 'Efficiency')),
    'abs(light1eta)' : (lambda c : abs(c.light_eta[0]),                          np.arange(0., 3., .2),                  ('|#eta|(light lep 1) [GeV]', 'Efficiency')),
    'abs(light2eta)' : (lambda c : abs(c.light_eta[1]),                          np.arange(0., 3., .2),                  ('|#eta|(light lep 2) [GeV]', 'Efficiency')),
#    'l1pt-abs(l1eta)' : (lambda c : (c.l_pt[0], abs(c.l_eta[0])),      (np.arange(0., 100., 15.), np.arange(0., 3., .5)), ('p_{T}(l1) [GeV]', '|#eta|(l1)')),
#    'l2pt-abs(l2eta)' : (lambda c : (c.l_pt[1], abs(c.l_eta[1])),      (np.arange(5., 40., 5.), np.arange(0., 3., .5)), ('p_{T}(l2) [GeV]', '|#eta|(subleading)')),
#    'l3pt-abs(l3eta)' : (lambda c : (c.l_pt[2], abs(c.l_eta[2])),      (np.arange(5., 40., 5.), np.arange(0., 3., .5)), ('p_{T}(l3) [GeV]', '|#eta|(subleading)')),
#    'l3pt-l2pt' : (lambda c : (c.l_pt[2], c.l_pt[1]),      (np.arange(5., 50., 5.), np.arange(5., 50., 5.)), ('p_{T}(l3) [GeV]', 'p_{T}(l2) [GeV]')),
#    'l3pt-l2pt' : (lambda c : (c.l_pt[2], c.l_pt[1]),      (np.arange(10., 32., 2.), np.arange(10., 32., 2.)), ('p_{T}(l3) [GeV]', 'p_{T}(l2) [GeV]')),
#    'l2pt-l1pt' : (lambda c : (c.l_pt[1], c.l_pt[0]),      (np.arange(10., 34., 4.), np.arange(15., 35., 4.)), ('p_{T}(l2) [GeV]', 'p_{T}(l1) [GeV]')),
}

from HNL.Triggers.triggerSelection import returnTriggers 

if not args.makePlots:
    #
    # Submit subjobs
    #
    if not args.isChild:
        from HNL.Tools.jobSubmitter import submitJobs
        for year in jobs.keys():
            submitJobs(__file__, ('sample', 'subJob'), jobs[year], argParser, jobLabel = 'calcTriggerEff-NEW', additionalArgs=[('year', year)])
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
    chain.year = year
    chain.era = args.era
    chain.region = args.region
    chain.analysis = args.analysis
    chain.selection = args.selection
    
    #
    # Initialize reweighter
    #
    from HNL.Weights.reweighter import Reweighter
    reweighter = Reweighter(sample, sample_manager)
    if not args.closureTest:
        reweighter.WEIGHTS_TO_USE.pop(reweighter.WEIGHTS_TO_USE.index('triggerSFWeight'))

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
        #event_range = xrange(max_events) if max_events < len(sample.getEventRange(args.subJob)) else sample.getEventRange(args.subJob)
        event_range = xrange(max_events)
    else:
        event_range = sample.getEventRange(args.subJob)   

    branches = []
    #for v in ['l1pt', 'l1eta', 'l2pt', 'l2eta', 'l3pt', 'l3eta', 'l1flavor', 'l2flavor', 'l3flavor', 'weight', 'category']:
    for v in ['l1pt', 'l1eta', 'light1pt', 'light1eta', 'l2pt', 'l2eta', 'light2pt', 'light2eta', 'l3pt', 'l3eta', 'l1flavor', 'l2flavor', 'l3flavor', 'light1flavor', 'light2flavor', 'weight', 'category']:
        branches.extend(['{0}/F'.format(v)])

    if args.separateTriggers == 'single':
        for index in xrange(len(returnTriggers(chain, args.analysis))):
            branches.append('trigger{0}/F'.format(index))

    efficiency = EfficiencyTree('trigger_efficiency', getOutputName(year, sample.output), branches)

    #
    # Define event selection
    #
    from HNL.EventSelection.event import Event
    event = Event(sample, chain, sample_manager, is_reco_level=True, selection=args.selection, strategy='MVA', region=args.region, analysis=args.analysis, year = year, era = args.era)    

    #
    # Loop over all events
    #
    from HNL.EventSelection.eventSelectionTools import select3Leptons
    for entry in event_range:
        if args.isTest: progress(entry - event_range[0], len(event_range))
        chain.GetEntry(entry)

        cutter.cut(True, 'total')
        if args.useRef and not cutter.cut(chain._passTrigger_ref, 'passed ref filter'):     continue

        event.initEvent()
        if not event.passedFilter(cutter, sample.name, offline_thresholds = not args.noOfflineThresholds, ignore_triggers = True): continue

        if chain.l_flavor.count(2) > 1: continue

        from HNL.Triggers.triggerSelection import passTriggers
        passed = passTriggers(chain, args.analysis)

        chain.light_pt = []
        chain.light_eta = []
        chain.light_flavor = []

        for lep_flavor, lep_pt, lep_eta in zip(chain.l_flavor, chain.l_pt, chain.l_eta):
            if lep_flavor < 2:
                chain.light_pt.append(lep_pt)
                chain.light_eta.append(lep_eta)   
                chain.light_flavor.append(lep_flavor)   

        efficiency.setTreeVariable('l1pt', chain.l_pt[0])
        efficiency.setTreeVariable('light1pt', chain.light_pt[0])
        efficiency.setTreeVariable('l2pt', chain.l_pt[1])
        efficiency.setTreeVariable('light2pt', chain.light_pt[1])
        efficiency.setTreeVariable('l3pt', chain.l_pt[2])
        efficiency.setTreeVariable('l1eta', chain.l_eta[0])
        efficiency.setTreeVariable('light1eta', chain.light_eta[0])
        efficiency.setTreeVariable('l2eta', chain.l_eta[1])
        efficiency.setTreeVariable('light2eta', chain.light_eta[1])
        efficiency.setTreeVariable('l3eta', chain.l_eta[2])
        efficiency.setTreeVariable('l1flavor', chain.l_flavor[0])
        efficiency.setTreeVariable('light1flavor', chain.light_flavor[0])
        efficiency.setTreeVariable('l2flavor', chain.l_flavor[1])
        efficiency.setTreeVariable('light2flavor', chain.light_flavor[1])
        efficiency.setTreeVariable('l3flavor', chain.l_flavor[2])
        efficiency.setTreeVariable('weight', reweighter.getTotalWeight())
        efficiency.setTreeVariable('category', chain.category)
        if args.separateTriggers == 'single':
            for itrigger, trigger in enumerate(returnTriggers(chain, args.analysis)):
                efficiency.setTreeVariable('trigger{0}'.format(itrigger), trigger)
                
        efficiency.fill(passed)

    efficiency.write(is_test=arg_string)

    cutter.saveCutFlow(getOutputName(year, sample.output))

    closeLogger(log)

else:
    from HNL.Tools.mergeFiles import merge
    import glob
    from HNL.Tools.helpers import makePathTimeStamped
    from HNL.Plotting.plot import Plot

    def setHistogram(original_dict, new_key, histogram):
        if new_key not in original_dict or original_dict[new_key] is None:
            original_dict[new_key] = histogram
        else:
            original_dict[new_key].add(histogram)

    combined_years = '-'.join(sorted(args.year))
    efficiencies = {combined_years : {}}
    for year in args.year:
        base_path_in = getOutputBase(year, '*')
                       
        in_files = glob.glob(base_path_in)
        if not skip_running_jobs: merge(in_files, __file__, jobs[year], ('sample', 'subJob'), argParser, istest=args.isTest, additionalArgs=[('year', year)])

        sample_manager = getSampleManager(year)  
        #samples_to_plot = sample_manager.getOutputs()
        samples_to_plot = ['WZ']

        efficiencies[year] = {}

        triggers_to_run = ['total']
        #triggers_to_run = []
        if args.separateTriggers == 'single':
            efficiency_tree = EfficiencyTree('trigger_efficiency', getOutputName(year, list(samples_to_plot)[0]).rsplit('/', 2)[0]+'/efficiency.root')
            triggers_to_run += [b.GetName() for b in efficiency_tree.tree.GetListOfBranches() if 'trigger' in b.GetName()]
        
        for trigger in triggers_to_run:
            print "Working on", trigger, 'for', year
            passed_name = 'passed' if trigger == 'total' else trigger
            efficiencies[year][trigger] = {}
            if trigger not in efficiencies[combined_years].keys(): efficiencies[combined_years][trigger] = {}
            for isample, sample_output in enumerate(samples_to_plot):
                if args.sample and sample_output != args.sample: continue
                progress(isample, len(samples_to_plot))
   
                efficiencies[year][trigger][sample_output] = {}
                if sample_output not in efficiencies[combined_years][trigger].keys(): efficiencies[combined_years][trigger][sample_output] = {}
                
                efficiency_tree = EfficiencyTree('trigger_efficiency', getOutputName(year, sample_output).rsplit('/', 2)[0]+'/efficiency.root')
    
                #Gather all the information
                # from HNL.EventSelection.eventCategorization import DETAILED_TRIGGER_CATEGORIES as TRIGGER_CATEGORIES
                from HNL.EventSelection.eventCategorization import TRIGGER_CATEGORIES
                for v in var:
                    efficiency_tree.setBins(var[v][1])
                    efficiencies[year][trigger][sample_output][v] = {'Total' : None}
                    if v not in efficiencies[combined_years][trigger][sample_output].keys(): efficiencies[combined_years][trigger][sample_output][v] = {'Total' : None}
                    for llc in leading_lep_cat:
                        lowpt, highpt = llc.split('to')
                        llc_condition = "l1pt>{0}".format(lowpt)
                        if highpt != 'inf': llc_condition += "&&l1pt<{0}".format(highpt)
                        efficiencies[year][trigger][sample_output][v][llc] = {}
                        if llc not in efficiencies[combined_years][trigger][sample_output][v].keys(): efficiencies[combined_years][trigger][sample_output][v][llc] = {'Total' : None}
                        for tc in TRIGGER_CATEGORIES:
                            #if tc != 'TauEE' : continue
                            #tc_condition = "("+"||".join(['category=={0}'.format(cat) for cat in TRIGGER_CATEGORIES[tc]])+")&&l1flavor==2"
                            tc_condition = "("+"||".join(['category=={0}'.format(cat) for cat in TRIGGER_CATEGORIES[tc]])+")"
                            setHistogram(efficiencies[year][trigger][sample_output][v][llc], tc, efficiency_tree.getEfficiency(v, v+'-'+str(tc)+'-'+llc, condition = llc_condition+'&&'+tc_condition, passed_name = passed_name))
                            setHistogram(efficiencies[combined_years][trigger][sample_output][v][llc], tc, efficiencies[year][trigger][sample_output][v][llc][tc])
                        setHistogram(efficiencies[year][trigger][sample_output][v][llc], 'Total', efficiency_tree.getEfficiency(v, v+'-'+llc+'-total', condition = llc_condition, passed_name = passed_name))
                        setHistogram(efficiencies[combined_years][trigger][sample_output][v][llc], 'Total', efficiencies[year][trigger][sample_output][v][llc]['Total'])
                    #Now also add to the total
                    setHistogram(efficiencies[year][trigger][sample_output][v], 'Total', efficiency_tree.getEfficiency(v, v+'-total', passed_name = passed_name))
                    setHistogram(efficiencies[combined_years][trigger][sample_output][v], 'Total', efficiencies[year][trigger][sample_output][v]['Total'])
    
    

            if args.storeSF:
                sf_output_name = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Weights', 'data', 'triggerSF', args.era+year, 'triggerSF.root'))
                from HNL.Tools.helpers import makeDirIfNeeded
                makeDirIfNeeded(sf_output_name)
                from ROOT import TFile
                out_file = TFile(sf_output_name, 'RECREATE')
                for cat in ['LeadingLightLepElectron', 'LeadingLightLepMuon']:
                    sf_to_store = efficiencies[year]['total']['Data']['light1pt'][leading_lep_cat[-1]][cat].getEfficiency().Clone()
                    sf_to_store.Divide(efficiencies[year]['total']['WZ']['light1pt'][leading_lep_cat[-1]][cat].getEfficiency())
                    sf_to_store.Write(cat)
                out_file.Close()
    
        
    years_to_plot = [combined_years] if len(args.year)>1 else []    
    years_to_plot.extend(args.year)     
    for year in years_to_plot:
  
        print 'Making regular plots for', year 
        for trigger in triggers_to_run:
            for isample, sample_output in enumerate(samples_to_plot):
                for tc in TRIGGER_CATEGORIES.keys()+['Total']:
                    #if tc != 'TauEE' : continue
                    output_string = getOutputBase(year, sample_output).replace('Triggers/data/', 'Triggers/data/Results/')
                    for v in var:
                        if '-' in v:
                            for llc in leading_lep_cat:
                                name_for_plot = "".join([x for x in v if x not in ['(', ')']])
                                p = Plot(efficiencies[year][trigger][sample_output][v][llc][tc].getEfficiency(), 'efficiency', trigger+'/'+tc+'/'+name_for_plot+'/'+llc, year = year, era = args.era, x_name = var[v][2][0], y_name = var[v][2][1])
                                p.draw2D(output_dir=output_string, names = [trigger+'/'+tc+'/'+name_for_plot+'/'+llc.replace('.0', '')])
                        else:
                            for llc in leading_lep_cat:
                                xvar = var[v][2][0]
                                if llc in ['LeadingLightLepElectron', 'CrossCategoryLeadingElectron'] and v == 'light1pt':
                                    xvar = 'p_{T}(leading e) [GeV]'
                                elif llc in ['LeadingLightLepMuon', 'CrossCategoryLeadingMuon'] and v == 'light1pt':
                                    xvar = 'p_{T}(leading #mu) [GeV]'
                                name_for_plot = "".join([x for x in v if x not in ['(', ')']])
                                p = Plot(efficiencies[year][trigger][sample_output][v][llc][tc].getEfficiency(), 'efficiency', trigger+'/'+tc+'/'+name_for_plot+'/'+llc, year = year, era = args.era, x_name = xvar, y_name = var[v][2][1], color_palette = 'Black')
                                p.drawHist(output_string, max_cutoff = 1.4)
    
        print 'Making comparison plots for', year
        # Make comparative 1D plots with multiple processes in the plot
        if 'Data' in efficiencies[year]['total'].keys() and 'WZ' in efficiencies[year]['total'].keys():
            signal_dict = {
                'EEE' : 'HNL-e-m50',
                'EEMu' : 'HNL-e-m50',
                'EMuMu' : 'HNL-mu-m50',
                'MuMuMu' : 'HNL-mu-m50',
                'TauEE' : 'HNL-tau-m50',
                'TauEMu' : 'HNL-tau-m50',
                'TauMuMu' : 'HNL-tau-m50',
                'Total' : 'HNL-e-m50',
                'NoTau' : 'HNL-e-m50',
                'LeadingLightLepElectron' : 'HNL-e-m50',
                'LeadingLightLepMuon' : 'HNL-mu-m50',
                'TauFinalStates' : 'HNL-tau-m50'
            }
    
            for v in var:
                if '3D' in v  or '-' in v: continue
                output_string = getOutputBase(year, 'Combined').replace('Triggers/data/', 'Triggers/data/Results/')
#                for llc in leading_lep_cat:
#                    for tc in TRIGGER_CATEGORIES.keys()+['Total']:
#                        if tc != 'Total' and not signal_dict[tc] in efficiencies[year].keys(): continue
#                        p = Plot([efficiencies[year]['WZ'][v][llc][tc].getEfficiency(), efficiencies[year][signal_dict[tc]][v][llc][tc]].getEfficiency(), ['WZ (MC)', 'HNL(m_{N}=50 GeV)', 'MET (data)'], 
#                        #p = Plot([efficiencies[year]['WZ'][v][llc][tc]].getEfficiency(), ['WZ (MC)', 'JetMET (data)'], 
#                                    'Split/'+tc+'/'+''.join([x for x in v if x not in ['(', ')']])+'/'+llc, year = year, era = args.era, bkgr_hist = efficiencies[year]['Data'][v][llc][tc].getEfficiency(), draw_ratio = True, color_palette='StackTauPOGbyName', color_palette_bkgr='Didar', x_name = var[v][2][0], y_name = var[v][2][1])
#                        p.setLegend(x1=0.33, x2=0.96, y1=0.82, y2=.92, ncolumns=3)
#                        p.drawHist(output_string, draw_option='EP', bkgr_draw_option='EP', max_cutoff=1.1)
        
                #p = Plot([efficiencies[year]['WZ'][v]['Total'].getEfficiency(), efficiencies[year][signal_dict[tc]][v]['Total'].getEfficiency()], ['WZ (MC)', 'HNL(m_{N}=50 GeV)', 'MET (data)'], 
                #p = Plot([efficiencies[year]['WZ'][v]['Total'].getEfficiency(), efficiencies[year]['HNL-e-m50'][v]['Total']].getEfficiency(), ['WZ (MC)', 'HNL(m_{N}=50 GeV)', 'MET (data)'], 
                p = Plot([efficiencies[year]['total']['WZ'][v]['Total'].getEfficiency()], ['WZ (MC)', 'JetMET (data)'], 
                         'total/'+v, year = year, era = args.era, bkgr_hist = efficiencies[year]['total']['Data'][v]['Total'].getEfficiency(), draw_ratio = True, color_palette='StackTauPOGbyName', color_palette_bkgr='Didar', x_name = var[v][2][0], y_name = var[v][2][1])
                p.setLegend(x1=0.4, x2=0.96, y1=0.82, y2=.92, ncolumns=2)
                p.drawHist(output_string, draw_option='EP', bkgr_draw_option='EP', max_cutoff=1.3)
                for tc in TRIGGER_CATEGORIES:
                    if tc == 'Total': continue
                    for llc in leading_lep_cat:
                        #p = Plot([efficiencies[year]['WZ'][v][llc][tc].getEfficiency(), efficiencies[year][signal_dict[tc]][v][llc][tc]].getEfficiency(), ['WZ (MC)', 'HNL(m_{N}=50 GeV)', 'JetMET (data)'], 
                        p = Plot([efficiencies[year]['total']['WZ'][v][llc][tc].getEfficiency()], ['WZ (MC)', 'JetMET (data)'], 
                                    'total/'+''.join([x for x in v if x not in ['(', ')']])+'/'+tc+'/'+llc, year = year, era = args.era, bkgr_hist = efficiencies[year]['total']['Data'][v][llc][tc].getEfficiency(), draw_ratio = True, color_palette='StackTauPOGbyName', color_palette_bkgr='Didar', x_name = var[v][2][0], y_name = var[v][2][1])
                        p.setLegend(x1=0.33, x2=0.96, y1=0.82, y2=.92, ncolumns=3)
                        p.drawHist(output_string, draw_option='EP', bkgr_draw_option='EP', max_cutoff=1.1)
