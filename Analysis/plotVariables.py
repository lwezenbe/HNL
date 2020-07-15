#! /usr/bin/env python

#########################################################################
#                                                                       #
#   Code to plot basic variables that are already contained in a tree   # 
#   that was skimmed for baseline events                                #
#                                                                       #                                   
#########################################################################


#
# Argument parser and logging
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--isChild',  action='store_true',       default=False,  help='mark as subjob, will never submit subjobs by itself')
argParser.add_argument('--year',     action='store',            default=None,   help='Select year', choices=['2016', '2017', '2018'], required=True)
argParser.add_argument('--sample',   action='store',            default=None,   help='Select sample by entering the name as defined in the conf file')
argParser.add_argument('--subJob',   action='store',            default=None,   help='The number of the subjob for this sample')
argParser.add_argument('--isTest',   action='store_true',       default=False,  help='Run a small test')
argParser.add_argument('--runLocal', action='store_true',       default=False,  help='use local resources instead of Cream02')
argParser.add_argument('--dryRun',   action='store_true',       default=False,  help='do not launch subjobs, only show them')
argParser.add_argument('--makePlots',   action='store_true',    default=False,  help='Use existing root files to make the plots')
argParser.add_argument('--showCuts',   action='store_true',     default=False,  help='Show what the pt cuts were for the category in the plots')
argParser.add_argument('--runOnCream',   action='store_true',   default=False,  help='Submit jobs on the cluster')
argParser.add_argument('--genLevel',   action='store_true',     default=False,  help='Use gen level variables')
argParser.add_argument('--signalOnly',   action='store_true',   default=False,  help='Run or plot a only the signal')
argParser.add_argument('--bkgrOnly',   action='store_true',     default=False,  help='Run or plot a only the background')
argParser.add_argument('--masses', type=int, nargs='*',  help='Only run or plot signal samples with mass given in this list')
argParser.add_argument('--flavor', action='store', default='',  help='Which coupling should be active?' , choices=['tau', 'e', 'mu', '2l', ''])
argParser.add_argument('--coupling', action='store', default=0.01, type=float,  help='How large is the coupling?')
argParser.add_argument('--selection', action='store', default='cut-based', type=str,  help='What type of analysis do you want to run?', choices=['cut-based', 'AN2017014', 'MVA'])
argParser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?', choices=['baseline', 'lowMassSR', 'highMassSR', 'ZZCR', 'WZCR', 'ConversionCR'])
argParser.add_argument('--groupSamples',   action='store_true', default=False,  help='plot Search Regions')
argParser.add_argument('--includeData',   action='store_true', default=False,  help='Also run over data')

#argParser.add_argument('--triggerTest', type=str, default=None,  help='Some settings to perform pt cuts for triggers')
args = argParser.parse_args()


if args.includeData and args.region in ['baseline', 'highMassSR', 'lowMassSR']:
    raise RuntimeError('These options combined would mean unblinding. This is not allowed.')

#
# General imports
#
import numpy as np
import os
from ROOT import TFile, TLorentzVector
from HNL.Tools.histogram import Histogram
from HNL.Tools.mergeFiles import merge
from HNL.Tools.helpers import getObjFromFile, progress, makeDirIfNeeded
from HNL.Samples.sample import createSampleList
from HNL.EventSelection.signalLeptonMatcher import SignalLeptonMatcher
from HNL.EventSelection.eventCategorization import EventCategory
from HNL.EventSelection.cutter import Cutter, printSelections

#
# Some constants to make referring to signal leptons more readable
#
l1 = 0
l2 = 1
l3 = 2
l4 = 4

nl = 3 if args.region != 'ZZCR' else 4

if args.isTest:
    if args.year is None: args.year = '2016'
    if args.sample is None: args.sample = 'DYJetsToLL-M-10to50'

#
# Create histograms
#
import HNL.Analysis.analysisTypes as at
var = at.returnVariables(nl, not args.genLevel)


import HNL.EventSelection.eventCategorization as cat
def listOfCategories(region):
    if region in ['baseline', 'highMassSR', 'lowMassSR']:
        return cat.CATEGORIES
    else:
        return [max(cat.CATEGORIES)]

categories = listOfCategories(args.region)
reco_or_gen_str = 'reco' if not args.genLevel else 'gen'

if not args.isTest:
    output_name = lambda st : os.path.join(os.getcwd(), 'data', 'plotVariables', args.year, args.selection, reco_or_gen_str, args.region, st)
else:
    output_name = lambda st : os.path.join(os.getcwd(), 'data', 'testArea', 'plotVariables', args.year, args.selection, reco_or_gen_str, args.region, st)

list_of_hist = {}
for prompt_str in ['prompt', 'nonprompt', 'total']:
    list_of_hist[prompt_str] = {}
    for c in categories:
        list_of_hist[prompt_str][c] = {}
        for v in var:
            list_of_hist[prompt_str][c][v] = {'signal':{}, 'bkgr':{}}
            if args.includeData: list_of_hist[prompt_str][c][v]['data'] = {}

#
# Load in the sample list 
#
from HNL.Samples.sampleManager import SampleManager
if args.genLevel and args.selection == 'AN2017014':
    raise RuntimeError('gen level is currently not implemented on AN2017014 analysis type, will use reco skimmed samples')

if args.genLevel:
    skim_str = 'Gen'
elif args.selection != 'AN2017014':
    skim_str = 'Reco'
else:
    skim_str = 'Old'
# sample_manager = SampleManager(args.year, skim_str, 'fulllist_'+str(args.year))
sample_manager = SampleManager(args.year, skim_str, 'yields_'+str(args.year))

from HNL.Triggers.triggerSelection import applyCustomTriggers, listOfTriggersAN2017014


#
# Loop over samples and events
#
if not args.makePlots:

    #
    # Submit subjobs
    #
    if args.runOnCream and not args.isChild:
        from HNL.Tools.jobSubmitter import submitJobs
        jobs = []
        for sample_name in sample_manager.sample_names:
            if not args.includeData and sample_name == 'Data': continue
            sample = sample_manager.getSample(sample_name)
            if args.signalOnly and not 'HNL' in sample.name: continue
            if args.bkgrOnly and 'HNL' in sample.name: continue
            for njob in xrange(sample.split_jobs): 
                jobs += [(sample.name, str(njob))]

        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'plotVar')
        exit(0)

    #prepare object  and event selection
    if args.selection == 'AN2017014':
        object_selection_param = {
            'no_tau' : True,
            'light_algo' : 'cutbased',
            'workingpoint' : 'tight'
        }
    else:
        object_selection_param = {
            'no_tau' : False,
            'light_algo' : 'leptonMVAtop',
            'workingpoint' : 'medium'
        }

    from HNL.EventSelection.eventSelector import EventSelector

    #Start a loop over samples
    sample_names = []
    for sample in sample_manager.sample_list:
        if sample.name not in sample_manager.sample_names: continue
       
        if args.runOnCream and sample.name != args.sample: continue
        if args.sample and sample.name != args.sample: continue
        if not args.includeData and sample.name == 'Data': continue

        #
        # Load in sample and chain
        #
        chain = sample.initTree(needhcount=False)
        sample_names.append(sample.name)

        #
        # Check if sample is a signal or background sample
        #
        is_signal = 'HNL' in sample.name
        if args.includeData and sample.name == 'Data':
            signal_str = 'data'
        else:
            signal_str = 'signal' if is_signal else 'bkgr'

        if args.signalOnly and not is_signal:   continue
        if args.bkgrOnly and is_signal:         continue

        #
        # Create histogram for all categories and variables
        #
        for prompt_str in ['prompt', 'nonprompt', 'total']:
            for c in categories:
                for v in var:
                    list_of_hist[prompt_str][c][v][signal_str][sample.name] = Histogram(str(c)+'-'+v+'-'+sample.output+'-'+prompt_str, var[v][0], var[v][2], var[v][1])
        
        #
        # Set event range
        #
        if args.isTest:
            if len(sample.getEventRange(0)) < 2000:
                event_range = sample.getEventRange(0)
            else:
                event_range = xrange(2000)
        elif args.runOnCream:
            event_range = sample.getEventRange(args.subJob)
        else:
            event_range = xrange(chain.GetEntries())

        #
        # Some basic variables about the sample to store in the chain
        #
        chain.HNLmass = sample.getMass()
        chain.year = int(args.year)

        #
        # Skip HNL masses that were not defined
        #
        if args.masses is not None and chain.HNLmass not in args.masses: continue

        #
        # Create cutter to provide cut flow
        #
        cutter = Cutter(chain = chain)

        #
        # Loop over all events
        #
        ec = EventCategory(chain)
        es = EventSelector(args.region, args.selection, object_selection_param, not args.genLevel, ec)
        for entry in event_range:
            
            chain.GetEntry(entry)
            progress(entry - event_range[0], len(event_range))
 
            cutter.cut(True, 'Total')

            #
            #Triggers
            #
            if args.selection == 'AN2017014':
                if not cutter.cut(applyCustomTriggers(listOfTriggersAN2017014(chain)), 'pass_triggers'): continue
           
            #
            # Event selection
            #
            if not es.passedFilter(chain, chain, cutter): continue
            nprompt = 0
            if sample.name != 'Data':
                for index in chain.l_indices:
                    if chain._lIsPrompt[index]: nprompt += 1
            
            prompt_str = 'prompt' if nprompt == nl else 'nonprompt'

            #
            # Fill the histograms
            #
            
            for v in var.keys():
                # if v == 'NbJet': continue
                list_of_hist[prompt_str][chain.category][v][signal_str][sample.name].fill(chain, chain.lumiweight)  
                list_of_hist['total'][chain.category][v][signal_str][sample.name].fill(chain, chain.lumiweight)  
             
        #
        # Save histograms
        #
        subjobAppendix = '_subJob' + args.subJob if args.subJob else ''
        
        if args.signalOnly and args.genLevel:       output_name_full = os.path.join(output_name(signal_str), 'signalOrdering', sample.output)
        else:      output_name_full = os.path.join(output_name(signal_str), sample.output) 

        if args.isChild:
            output_name_full += '/tmp_'+sample.output+ '/'+sample.name+'_'
        else:
            output_name_full += '/'
        
        makeDirIfNeeded(output_name_full +'variables'+subjobAppendix+ '.root')
        output_file = TFile(output_name_full + 'variables' +subjobAppendix+ '.root', 'RECREATE')
        
        for v in var.keys():
            output_file.mkdir(v)
            output_file.cd(v)
            for c in categories:
                for prompt_str in ['prompt', 'nonprompt', 'total']:
                    list_of_hist[prompt_str][c][v][signal_str][sample.name].getHist().Write()
        
        output_file.Close()

        cutter.saveCutFlow(output_name_full +'variables'+subjobAppendix+ '.root')

#If the option to not run over the events again is made, load in the already created histograms here
else:
    import glob

    # Collect signal file locations
    if args.genLevel and args.signalOnly:
        signal_list = glob.glob(output_name('signal')+'/signalOrdering/*'+args.flavor+'-*')
        
    elif not args.bkgrOnly:
        signal_list = glob.glob(output_name('signal')+'/*'+args.flavor+'-*')
        for i, s in enumerate(signal_list):
            if 'signalOrdering' in s:
                signal_list.pop(i)
    else:
        signal_list = []

    # Collect background file locations
    if not args.signalOnly:
        bkgr_list = glob.glob(output_name('bkgr')+'/*')
    else:
        bkgr_list = []

    # data
    if args.includeData:
        data_list = glob.glob(output_name('data')+'/Data')
    else:
        data_list = []

    print 'check merge'
    # Merge files if necessary
    mixed_list = signal_list + bkgr_list + data_list
    for n in mixed_list:
        merge(n)


    if args.groupSamples:
        background_collection = sample_manager.sample_groups.keys()
    else:
        background_collection = [b.split('/')[-1] for b in bkgr_list]


    #Reset list_of_hist
    list_of_hist = {}
    for c in categories:
        list_of_hist[c] = {}
        for v in var:
            list_of_hist[c][v] = {'signal':{}, 'bkgr':{}}


    # Load in the signal histograms from the files
    for c in categories: 
        print 'loading', c
        for v in var.keys():
            if not args.bkgrOnly:
                for s in signal_list:
                    sample_name = s.split('/')[-1]
                    sample_mass = int(sample_name.split('-m')[-1])
                    if args.masses is not None and sample_mass not in args.masses: continue
                    list_of_hist[c][v]['signal'][sample_name] = Histogram(getObjFromFile(s+'/variables.root', v+'/'+str(c)+'-'+v+'-'+sample_name+'-total')) 
                    # list_of_hist[c][v]['signal'][sample_name].hist.Scale(1000.)

    for c in categories: 
        print 'loading', c
        for v in var.keys():   
            if not args.signalOnly:
                for b in background_collection:
                    list_of_hist[c][v]['bkgr'][b] = Histogram(b, var[v][0], var[v][2], var[v][1])

    for c in categories: 
        print 'loading', c
        for v in var.keys():   
            if not args.signalOnly:
                for b in bkgr_list:
                    bkgr = b.split('/')[-1]
                    tmp_hist_total = Histogram(getObjFromFile(b+'/variables.root', v+'/'+str(c)+'-'+v+'-'+bkgr+'-total'))
                    tmp_hist_prompt = Histogram(getObjFromFile(b+'/variables.root', v+'/'+str(c)+'-'+v+'-'+bkgr+'-prompt'))
                    tmp_hist_nonprompt = Histogram(getObjFromFile(b+'/variables.root', v+'/'+str(c)+'-'+v+'-'+bkgr+'-nonprompt'))

                    if args.groupSamples:
                        sg = [sk for sk in sample_manager.sample_groups.keys() if bkgr in sample_manager.sample_groups[sk]]
                        if bkgr == 'DY':
                            list_of_hist[c][v]['bkgr']['XG'].add(tmp_hist_prompt)
                            list_of_hist[c][v]['bkgr']['non-prompt'].add(tmp_hist_nonprompt)
                        elif sg == 'non-prompt':
                            list_of_hist[c][v]['bkgr'][sg[0]].add(tmp_hist_nonprompt)
                        else:
                            list_of_hist[c][v]['bkgr'][sg[0]].add(tmp_hist_prompt)
                            list_of_hist[c][v]['bkgr']['non-prompt'].add(tmp_hist_nonprompt)
                    else:
                        list_of_hist[c][v]['bkgr'][bkgr].add(tmp_hist_total)

    if args.includeData:
        for c in categories:
            for v in var:
                list_of_hist[c][v]['data'] = Histogram(getObjFromFile(data_list[0]+'/variables.root', v+'/'+str(c)+'-'+v+'-'+'Data-total'))



    if args.region in ['baseline', 'lowMassSR', 'highMassSR']:
        for ac in cat.ANALYSIS_CATEGORIES.keys():
            list_of_hist[ac] = {}
            for v in var.keys():
                list_of_hist[ac][v] = {}
                if not args.bkgrOnly:
                    for s in signal_list:
                        sample_name = s.split('/')[-1]
                        sample_mass = int(sample_name.split('-m')[-1])
                        if args.masses is not None and sample_mass not in args.masses: continue
                        list_of_hist[ac][v]['signal'][sample_name] = list_of_hist[cat.ANALYSIS_CATEGORIES[ac][0]][v]['bkgr'][sample_name].Clone(ac)
                        if len(cat.ANALYSIS_CATEGORIES[ac]) > 1:
                            for c in cat.ANALYSIS_CATEGORIES[ac][1:]:
                                list_of_hist[ac][v]['signal'][sample_name].add(list_of_hist[cat.ANALYSIS_CATEGORIES[ac][c]][v]['bkgr'][sample_name])



#
#       Plot!
#
if args.runOnCream or args.isTest: 
    exit(0)

#
# Necessary imports
#
from HNL.Plotting.plot import Plot
from HNL.Plotting.plottingTools import extraTextFormat
from HNL.Tools.helpers import makePathTimeStamped
from HNL.Tools.efficiency import Efficiency

#
# Set output directory, taking into account the different options
#
output_dir = os.path.join(os.getcwd(), 'data', 'Results', 'plotVariables', args.year, args.selection, reco_or_gen_str, args.region)


if args.signalOnly:
    output_dir = os.path.join(output_dir, 'signalOnly')
elif args.bkgrOnly:
    output_dir = os.path.join(output_dir, 'bkgrOnly')
else:
    output_dir = os.path.join(output_dir, 'signalAndBackground')



if args.flavor:         output_dir = os.path.join(output_dir, args.flavor+'_coupling')
else:                   output_dir = os.path.join(output_dir, 'all_coupling')

if args.masses is not None:         output_dir = os.path.join(output_dir, 'customMasses', '-'.join([str(m) for m  in args.masses]))
else:         output_dir = os.path.join(output_dir, 'allMasses')

output_dir = makePathTimeStamped(output_dir)
#
# Create plots for each category
#
from HNL.EventSelection.eventCategorization import CATEGORY_NAMES, CATEGORY_FROM_NAME
print list_of_hist.keys()
for c in list_of_hist.keys():
    print c
    c_name = CATEGORY_NAMES[c] if c not in cat.ANALYSIS_CATEGORIES.keys() else c

    printSelections(mixed_list[0]+'/variables.root', os.path.join(output_dir, c_name, 'Selections.txt'))

    extra_text = [extraTextFormat(cat.returnTexName(c), xpos = 0.2, ypos = 0.82, textsize = None, align = 12)]  #Text to display event type in plot
    if not args.bkgrOnly:
        extra_text.append(extraTextFormat('V_{'+args.flavor+'N} = '+str(args.coupling)))  #Text to display event type in plot
        extra_text.append(extraTextFormat('Signal scaled to background', textsize = 0.7))  #Text to display event type in plot

    # Plots that display chosen for chosen signal masses and backgrounds the distributions for the different variables
    # S and B in same canvas for each variable
    for v in var:
        print v
        legend_names = list_of_hist[c][v]['signal'].keys()+list_of_hist[c][v]['bkgr'].keys()
        
        # Make list of background histograms for the plot object (or None if no background)
        if not list_of_hist[c][v]['bkgr'].values() or args.signalOnly: 
            bkgr_hist = None
        else:
            bkgr_hist = list_of_hist[c][v]['bkgr'].values()
       
        # Make list of signal histograms for the plot object
        if not list_of_hist[c][v]['signal'].values() or args.bkgrOnly: 
            signal_hist = None
        else:
            signal_hist = list_of_hist[c][v]['signal'].values()

        if args.includeData:
            observed_hist = list_of_hist[c][v]['data']
        else:
            observed_hist = None

        # Create plot object (if signal and background are displayed, also show the ratio)
        if args.groupSamples:
            p = Plot(signal_hist, legend_names, c_name+'-'+v, bkgr_hist = bkgr_hist, observed_hist = observed_hist, y_log = False, extra_text = extra_text, draw_ratio = (not args.signalOnly and not args.bkgrOnly), year = args.year, color_palette = 'AN2017', color_palette_bkgr = 'AN2017')
        else:
            p = Plot(signal_hist, legend_names, c_name+'-'+v, bkgr_hist = bkgr_hist, y_log = False, extra_text = extra_text, draw_ratio = (not args.signalOnly and not args.bkgrOnly), year = args.year)


        # Draw
        p.drawHist(output_dir = os.path.join(output_dir, c_name), normalize_signal=True, draw_option='Hist', min_cutoff = 1)
    
    #TODO: I broke this when changing the eventCategorization, fix this again
    # # If looking at signalOnly, also makes plots that compares the three lepton pt's for every mass point
    # if args.signalOnly:

    #     all_cuts = returnCategoryPtCuts(c)
        
    #     for cuts in all_cuts:   
 
    #         # Load in efficiency to print on canvas if requested
    #         if args.showCuts:
    #             eff_file = os.path.expandvars('$CMSSW_BASE/src/HNL/EventSelection/data/calcSignalEfficiency/HNLtau/divideByCategory/triggerTest/signalSelectionFull.root')
    #             eff = Efficiency('efficiency_'+str(c[0])+'_'+str(c[1]) + '_l1_'+str(cuts[0])+'_l2_'+str(cuts[1])+'_l3_'+str(cuts[2]), None, None, eff_file, subdirs=['efficiency_'+str(c[0])+'_'+str(c[1]), 'l1_'+str(cuts[0])+'_l2_'+str(cuts[1])+'_l3_'+str(cuts[2])])           
 
    #         # Loop over different signals and draw the pt
    #         for n in list_of_hist[c][v]['signal'].keys():
    #             h = [list_of_hist[c]['l1pt']['signal'][n], list_of_hist[c]['l2pt']['signal'][n], list_of_hist[c]['l3pt']['signal'][n]]
    #             legend_names = ['l1', 'l2', 'l3']
                
    #             # Prepare to draw the pt cuts on the canvas if requested
    #             if args.showCuts:
    #                 draw_cuts = [cuts, eff.getEfficiency(inPercent=True).GetBinContent(eff.getEfficiency().FindBin(float(n.split('-')[1].split('M')[1])))]
    #             else:
    #                 draw_cuts = None
    #             # Create plot object and draw
    #             #p = Plot(h, legend_names, cat.categoryName(c)+'-'+cat.subcategoryName(c)+'-pt-'+n, extra_text=extra_text)
    #             p = Plot(h, legend_names, str(c)+'-pt-'+n, extra_text=extra_text)
    #             #p.drawHist(output_dir = os.path.join(output_dir, cat.categoryName(c), cat.subcategoryName(c), 'pt', 'l1_'+str(cuts[0])+'_l2_'+str(cuts[1])+'_l3_'+str(cuts[2])), normalize_signal=False, draw_option='EHist', draw_cuts=draw_cuts)
    #             p.drawHist(output_dir = os.path.join(output_dir, str(c), 'pt', 'l1_'+str(cuts[0])+'_l2_'+str(cuts[1])+'_l3_'+str(cuts[2])), normalize_signal=False, draw_option='EHist', draw_cuts=draw_cuts)
