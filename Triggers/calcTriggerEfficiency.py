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
submission_parser.add_argument('--separateTriggers', action='store', default=None,  
    help='Look at each trigger separately for each set of triggers. Single means just one trigger, cumulative uses cumulative OR of all triggers that come before the chosen one in the list, full applies all triggers for a certain category', 
    choices=['single', 'cumulative', 'full'])
argParser.add_argument('--makePlots',   action='store_true',    default=False,  help='Use existing root files to make the plots')

args = argParser.parse_args()

import numpy as np
import os
from HNL.Tools.efficiency import Efficiency
from HNL.EventSelection.eventCategorization import CATEGORIES_TO_USE as CATEGORIES
# from HNL.EventSelection.eventCategorization import DETAILED_CATEGORIES_TO_USE as CATEGORIES

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
                                    args.era+year, sep_trig_name, '-'.join([args.selection, args.analysis, ref_name]), sample_name)
    else:
        output_string = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Triggers', 'data', 'testArea', __file__.split('.')[0].rsplit('/')[-1], 
                                    args.era+year, sep_trig_name, '-'.join([args.selection, args.analysis, ref_name]), sample_name)
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
    #'l1pt' : (lambda c : c.l_pt[0],                          np.arange(0., 100., 15.),                 ('p_{T}(l1) [GeV]', 'Efficiency')),
    #'l2pt' : (lambda c : c.l_pt[1],                          np.arange(5., 80., 5.),                  ('p_{T}(l2) [GeV]', 'Efficiency')),
    #'l3pt' : (lambda c : c.l_pt[2],                          np.arange(5., 80., 5.),                  ('p_{T}(l3) [GeV]', 'Efficiency')),
    'l1pt' : (lambda c : c.l_pt[0],                          np.arange(0., 100., 2.),                 ('p_{T}(l1) [GeV]', 'Efficiency')),
    'l2pt' : (lambda c : c.l_pt[1],                          np.arange(5., 80., 2.),                  ('p_{T}(l2) [GeV]', 'Efficiency')),
    'l3pt' : (lambda c : c.l_pt[2],                          np.arange(5., 80., 2.),                  ('p_{T}(l3) [GeV]', 'Efficiency')),
    'abs(l1eta)' : (lambda c : abs(c.l_eta[0]),                          np.arange(0., 3., .5),                  ('|#eta|(l1) [GeV]', 'Efficiency')),
    'abs(l2eta)' : (lambda c : abs(c.l_eta[1]),                          np.arange(0., 3., .5),                  ('|#eta|(l2) [GeV]', 'Efficiency')),
    'abs(l3eta)' : (lambda c : abs(c.l_eta[2]),                          np.arange(0., 3., .5),                  ('|#eta|(l3) [GeV]', 'Efficiency')),
    'l1pt-abs(l1eta)' : (lambda c : (c.l_pt[0], abs(c.l_eta[0])),      (np.arange(0., 100., 15.), np.arange(0., 3., .5)), ('p_{T}(l1) [GeV]', '|#eta|(l1)')),
    'l2pt-abs(l2eta)' : (lambda c : (c.l_pt[1], abs(c.l_eta[1])),      (np.arange(5., 40., 5.), np.arange(0., 3., .5)), ('p_{T}(l2) [GeV]', '|#eta|(subleading)')),
    'l3pt-abs(l3eta)' : (lambda c : (c.l_pt[2], abs(c.l_eta[2])),      (np.arange(5., 40., 5.), np.arange(0., 3., .5)), ('p_{T}(l3) [GeV]', '|#eta|(subleading)')),
    'l3pt-l2pt' : (lambda c : (c.l_pt[2], c.l_pt[1]),      (np.arange(5., 40., 5.), np.arange(5., 40., 5.)), ('p_{T}(l3) [GeV]', 'p_{T}(l2) [GeV]')),
}


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
    for v in ['l1pt', 'l1eta', 'l2pt', 'l2eta', 'l3pt', 'l3eta', 'weight', 'category']:
        branches.extend(['{0}/F'.format(v)])
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
        if not event.passedFilter(cutter, sample.name, offline_thresholds = True, ignore_triggers = True): continue

        from HNL.Triggers.triggerSelection import passTriggers
        passed = passTriggers(chain, args.analysis)

        efficiency.setTreeVariable('l1pt', chain.l_pt[0])
        efficiency.setTreeVariable('l2pt', chain.l_pt[1])
        efficiency.setTreeVariable('l3pt', chain.l_pt[2])
        efficiency.setTreeVariable('l1eta', chain.l_eta[0])
        efficiency.setTreeVariable('l2eta', chain.l_eta[1])
        efficiency.setTreeVariable('l3eta', chain.l_eta[2])
        efficiency.setTreeVariable('weight', reweighter.getTotalWeight())
        efficiency.setTreeVariable('category', chain.category)
        efficiency.fill(passed)

    efficiency.write(is_test=arg_string)

    cutter.saveCutFlow(getOutputName(year, sample.output))

    closeLogger(log)

else:
    from HNL.Tools.mergeFiles import merge
    import glob
    from HNL.Tools.helpers import makePathTimeStamped
    from HNL.Plotting.plot import Plot

    for year in args.year:
        base_path_in = getOutputBase(year, '*')
                       
        in_files = glob.glob(base_path_in)
        if not skip_running_jobs: merge(in_files, __file__, jobs[year], ('sample', 'subJob'), argParser, istest=args.isTest, additionalArgs=[('year', year)])

        sample_manager = getSampleManager(year)  
        #samples_to_plot = sample_manager.getOutputs()
        samples_to_plot = ['WZ']

        overall_efficiencies = {}
        for isample, sample_output in enumerate(samples_to_plot):
            if args.sample and sample_output != args.sample: continue
            progress(isample, len(samples_to_plot))

            efficiency_tree = EfficiencyTree('trigger_efficiency', getOutputName(year, sample_output).rsplit('/', 2)[0]+'/efficiency.root')

            #Gather all the information
            # from HNL.EventSelection.eventCategorization import DETAILED_TRIGGER_CATEGORIES as TRIGGER_CATEGORIES
            from HNL.EventSelection.eventCategorization import TRIGGER_CATEGORIES
            efficiencies = {}
            for v in var:
                efficiency_tree.setBins(var[v][1])
                efficiencies[v] = {'Total' : None}
                for llc in leading_lep_cat:
                    lowpt, highpt = llc.split('to')
                    llc_condition = "l1pt>{0}".format(lowpt)
                    if highpt != 'inf': llc_condition += "&&l1pt<{0}".format(highpt)
                    efficiencies[v][llc] = {}
                    for tc in TRIGGER_CATEGORIES:
                        if tc != 'EEE' : continue
                        tc_condition = "&&".join(['category=={0}'.format(cat) for cat in TRIGGER_CATEGORIES[tc]])
                        efficiencies[v][llc][tc] = efficiency_tree.getEfficiency(v, v+'-'+str(tc)+'-'+llc, condition = llc_condition+'&&'+tc_condition)
                    efficiencies[v][llc]['Total'] = efficiency_tree.getEfficiency(v, v+'-'+llc+'-total', condition = llc_condition)
                #Now also add to the total
                efficiencies[v]['Total'] = efficiency_tree.getEfficiency(v, v+'-total')

                for tc in TRIGGER_CATEGORIES:
                    if tc != 'EEE' : continue
                    output_string = getOutputBase(year, sample_output).replace('Triggers/data/', 'Triggers/data/Results/')
                    if '-' in v:
                        for llc in leading_lep_cat:
                            name_for_plot = "".join([x for x in v if x not in ['(', ')']])
                            p = Plot(efficiencies[v][llc][tc], 'efficiency', tc+'/'+name_for_plot+'/'+llc, year = year, era = args.era, x_name = var[v][2][0], y_name = var[v][2][1])
                            p.draw2D(output_dir=output_string, names = [tc+'/'+name_for_plot+'/'+llc.replace('.0', '')])
                    else:
                        for llc in leading_lep_cat:
                            name_for_plot = "".join([x for x in v if x not in ['(', ')']])
                            p = Plot(efficiencies[v][llc][tc], 'efficiency', tc+'/'+name_for_plot+'/'+llc, year = year, era = args.era, x_name = var[v][2][0], y_name = var[v][2][1])
                            p.drawHist(output_string)

            overall_efficiencies[sample_output] = efficiencies.copy()

#        print 'Making comparison plots'
#        # Make comparative 1D plots with multiple processes in the plot
#        if 'Data' in overall_efficiencies.keys() and 'WZ' in overall_efficiencies.keys():
#            signal_dict = {
#                'EEE' : 'HNL-e-m50',
#                'EEMu' : 'HNL-e-m50',
#                'EMuMu' : 'HNL-mu-m50',
#                'MuMuMu' : 'HNL-mu-m50',
#                'TauEE' : 'HNL-tau-m50',
#                'TauEMu' : 'HNL-tau-m50',
#                'TauMuMu' : 'HNL-tau-m50',
#                'Total' : 'HNL-e-m50'
#            }
#
#            for v in var:
#                if '3D' in v  or '-' in v: continue
#                output_string = getOutputBase(year, 'Combined').replace('Triggers/data/', 'Triggers/data/Results/')
#                for llc in leading_lep_cat:
#                    for tc in TRIGGER_CATEGORIES.keys()+['Total']:
#                        if tc != 'Total' and not signal_dict[tc] in overall_efficiencies.keys(): continue
#                        #p = Plot([overall_efficiencies['WZ'][v][llc][tc], overall_efficiencies[signal_dict[tc]][v][llc][tc]], ['WZ (MC)', 'HNL(m_{N}=50 GeV)', 'MET (data)'], 
#                        p = Plot([overall_efficiencies['WZ'][v][llc][tc]], ['WZ (MC)', 'JetMET (data)'], 
#                                    'Split/'+tc+'/'+''.join([x for x in v if x not in ['(', ')']])+'/'+llc, year = year, era = args.era, bkgr_hist = overall_efficiencies['Data'][v][llc][tc], draw_ratio = True, color_palette='StackTauPOGbyName', color_palette_bkgr='Didar', x_name = var[v][2][0], y_name = var[v][2][1])
#                        p.setLegend(x1=0.33, x2=0.96, y1=0.82, y2=.92, ncolumns=3)
#                        p.drawHist(output_string, draw_option='EP', bkgr_draw_option='EP', max_cutoff=1.1)
#        
#                #p = Plot([overall_efficiencies['WZ'][v]['Total'].getEfficiency(), overall_efficiencies[signal_dict[tc]][v]['Total'].getEfficiency()], ['WZ (MC)', 'HNL(m_{N}=50 GeV)', 'MET (data)'], 
#                #p = Plot([overall_efficiencies['WZ'][v]['Total'], overall_efficiencies['HNL-e-m50'][v]['Total']], ['WZ (MC)', 'HNL(m_{N}=50 GeV)', 'MET (data)'], 
#                p = Plot([overall_efficiencies['WZ'][v]['Total']], ['WZ (MC)', 'JetMET (data)'], 
#                         'total/'+v, year = year, era = args.era, bkgr_hist = overall_efficiencies['Data'][v]['Total'], draw_ratio = True, color_palette='StackTauPOGbyName', color_palette_bkgr='Didar', x_name = var[v][2][0], y_name = var[v][2][1])
#                p.setLegend(x1=0.4, x2=0.96, y1=0.82, y2=.92, ncolumns=2)
#                p.drawHist(output_string, draw_option='EP', bkgr_draw_option='EP', max_cutoff=1.3)
#                for tc in TRIGGER_CATEGORIES:
#                    if tc == 'Total': continue
#                    for llc in leading_lep_cat:
#                        p = Plot([overall_efficiencies['WZ'][v][llc][tc], overall_efficiencies[signal_dict[tc]][v][llc][tc]], ['WZ (MC)', 'HNL(m_{N}=50 GeV)', 'JetMET (data)'], 
#                                    'total/'+''.join([x for x in v if x not in ['(', ')']])+'/'+tc+'/'+llc, year = year, era = args.era, bkgr_hist = overall_efficiencies['Data'][v][llc][tc], draw_ratio = True, color_palette='StackTauPOGbyName', color_palette_bkgr='Didar')
#                        p.setLegend(x1=0.33, x2=0.96, y1=0.82, y2=.92, ncolumns=3)
#                        p.drawHist(output_string, draw_option='EP', bkgr_draw_option='EP', max_cutoff=1.1)
