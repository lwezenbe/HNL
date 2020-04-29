#! /usr/bin/env python

#########################################################################
#                                                                       #
#   Code to plot basic variables that are already contained in a tree   # 
#   that was skimmed for baseline events                                #
#                                                                       #                                   
#########################################################################

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
from HNL.EventSelection.eventSelection import select3Leptons, select3GenLeptons, calculateKinematicVariables
from HNL.EventSelection.eventSelection import passBaseCuts, lowMassCuts, highMassCuts
from HNL.EventSelection.eventCategorization import EventCategory
from HNL.EventSelection.cutter import Cutter


#
# Some constants to make referring to signal leptons more readable
#
l1 = 0
l2 = 1
l3 = 2

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
argParser.add_argument('--massRegion', action='store',          default = None, choices =['low', 'high'], help='Run with low mass region cuts or high mass region cuts')
argParser.add_argument('--masses', type=int, nargs='*',  help='Only run or plot signal samples with mass given in this list')
argParser.add_argument('--flavor', action='store', default='',  help='Which coupling should be active?' , choices=['tau', 'e', 'mu', '2l', ''])
argParser.add_argument('--coupling', action='store', default=0.01, type=float,  help='How large is the coupling?')
#argParser.add_argument('--triggerTest', type=str, default=None,  help='Some settings to perform pt cuts for triggers')
args = argParser.parse_args()

if args.isTest:
    if args.year is None: args.year = '2016'
    if args.sample is None: args.sample = 'DYJetsToLL-M-10to50'

#
# Create histograms
#
if args.genLevel:
    var = {'minMos':        (lambda c : c.minMos,   np.arange(0., 120., 12.),         ('min(M_{OS}) [GeV]', 'Events')),
            'm3l':          (lambda c : c.M3l,      np.arange(0., 240., 5.),         ('M_{3l} [GeV]', 'Events')),
            'ml12':          (lambda c : c.Ml12,      np.arange(0., 240., 5.),         ('M_{l1l2} [GeV]', 'Events')),
            'ml23':          (lambda c : c.Ml23,      np.arange(0., 240., 5.),         ('M_{l2l3} [GeV]', 'Events')),
            'ml13':          (lambda c : c.Ml13,      np.arange(0., 240., 5.),         ('M_{l1l3} [GeV]', 'Events')),
            'met':          (lambda c : c._met,     np.arange(0., 300., 15.),         ('p_{T}^{miss} [GeV]', 'Events')),
            'mtOther':      (lambda c : c.mtOther,  np.arange(0., 300., 5.),       ('M_{T} (other min(M_{OS}) [GeV])', 'Events')),
            'l1pt':      (lambda c : c.l_pt[l1],       np.arange(0., 300., 5.),       ('p_{T} (l1) [GeV]', 'Events')),
            'l2pt':      (lambda c : c.l_pt[l2],       np.arange(0., 300., 5.),       ('p_{T} (l2) [GeV]', 'Events')),
            'l3pt':      (lambda c : c.l_pt[l3],       np.arange(0., 300., 5.),       ('p_{T} (l3) [GeV]', 'Events'))
            }
else:
    var = {'minMos':        (lambda c : c.minMos,   np.arange(0., 120., 12.),         ('min(M_{OS}) [GeV]', 'Events')),
            'm3l':          (lambda c : c.M3l,      np.arange(0., 240., 15.),         ('M_{3l} [GeV]', 'Events')),
            'ml12':          (lambda c : c.Ml12,      np.arange(0., 240., 5.),         ('M_{l1l2} [GeV]', 'Events')),
            'ml23':          (lambda c : c.Ml23,      np.arange(0., 240., 5.),         ('M_{l2l3} [GeV]', 'Events')),
            'ml13':          (lambda c : c.Ml13,      np.arange(0., 240., 5.),         ('M_{l1l3} [GeV]', 'Events')),
            'met':          (lambda c : c._met,     np.arange(0., 300., 15.),         ('p_{T}^{miss} [GeV]', 'Events')),
            'mtOther':      (lambda c : c.mtOther,  np.arange(0., 300., 15.),       ('M_{T} (other min(M_{OS}) [GeV])', 'Events')),
            'l1pt':      (lambda c : c.l_pt[l1],       np.arange(0., 300., 15.),       ('p_{T} (l1) [GeV]', 'Events')),
            'l2pt':      (lambda c : c.l_pt[l2],       np.arange(0., 300., 15.),       ('p_{T} (l2) [GeV]', 'Events')),
            'l3pt':      (lambda c : c.l_pt[l3],       np.arange(0., 300., 15.),       ('p_{T} (l3) [GeV]', 'Events')),
            'l1eta':      (lambda c : c.l_eta[l1],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l1)', 'Events')),
            'l2eta':      (lambda c : c.l_eta[l2],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l2)', 'Events')),
            'l3eta':      (lambda c : c.l_eta[l3],       np.arange(-2.5, 3.0, 0.5),       ('#eta (l3)', 'Events')),
            'NJet':      (lambda c : c.njets,       np.arange(0., 12., 1.),       ('#Jets', 'Events')),
            'NbJet':      (lambda c : c.nbjets,       np.arange(0., 12., 1.),       ('#B Jets', 'Events'))
        }

import HNL.EventSelection.eventCategorization as cat
categories = [c for c in cat.CATEGORIES]
categories.append(len(cat.CATEGORIES)+1) #other
reco_or_gen_str = 'reco' if not args.genLevel else 'gen'


list_of_hist = {}
for c in categories:
    list_of_hist[c] = {}
    for v in var:
        list_of_hist[c][v] = {'signal':{}, 'bkgr':{}}

#
# Loop over samples and events
#
if not args.makePlots:
    #
    # Load in the sample list 
    #
    from HNL.Samples.sampleManager import SampleManager
    gen_name = 'Gen' if args.genLevel else 'Reco'
    sample_manager = SampleManager(args.year, gen_name, 'fulllist_'+str(args.year))

    #
    # Submit subjobs
    #
    if args.runOnCream and not args.isChild:
        from HNL.Tools.jobSubmitter import submitJobs
        jobs = []
        for sample_name in sample_manager.sample_names:
            sample = sample_manager.getSample(sample_name)
            if args.signalOnly and not 'HNL' in sample.name: continue
            if args.bkgrOnly and 'HNL' in sample.name: continue
            for njob in xrange(sample.split_jobs): 
                jobs += [(sample.name, str(njob))]

        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'plotVar')
        exit(0)


    #Start a loop over samples
    sample_names = []
    for sample in sample_manager.sample_list:
        if sample.name not in sample_manager.sample_names: continue
       
        if args.runOnCream and sample.name != args.sample: continue
        if args.sample and sample.name != args.sample: continue

        #
        # Load in sample and chain
        #
        chain = sample.initTree(needhcount=False)
        sample_names.append(sample.name)

        #
        # Check if sample is a signal or background sample
        #
        is_signal = 'HNL' in sample.name
        signal_str = 'signal' if is_signal else 'bkgr'

        if args.signalOnly and not is_signal:   continue
        if args.bkgrOnly and is_signal:         continue

        #
        # Create histogram for all categories and variables
        #
        for c in categories:
            for v in var:
                list_of_hist[c][v][signal_str][sample.name] = Histogram(str(c)+'-'+v+'-'+sample.output, var[v][0], var[v][2], var[v][1])
        
        #
        # Set event range
        #
        if args.isTest:
            if len(sample.getEventRange(0)) < 500:
                event_range = sample.getEventRange(0)
            else:
                event_range = xrange(500)
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
        for entry in event_range:
            
            chain.GetEntry(entry)
            progress(entry - event_range[0], len(event_range))
 
            cutter.cut(True, 'Total')

            if args.genLevel and args.signalOnly:
                slm = SignalLeptonMatcher(chain)
                if not slm.saveNewOrder(): continue
                calculateKinematicVariables(chain, chain, is_reco_level=False)
           
            if not args.genLevel:
                if not cutter.cut(select3Leptons(chain, chain), 'select_3_leptons'):    continue 
            else:
                if not cutter.cut(select3GenLeptons(chain, chain), 'select_3_genleptons'):    continue 
            calculateKinematicVariables(chain, chain, is_reco_level=not args.genLevel)
            chain.event_category = ec.returnCategory()

            #
            # Event selection
            #
            if not passBaseCuts(chain, chain, cutter): continue
            if args.massRegion == 'low' and not lowMassCuts(chain, chain, cutter): continue
            if args.massRegion == 'high' and not highMassCuts(chain, chain, cutter): continue
            
            #
            # Fill the histograms
            #
            for v in var.keys():
                if chain.event_category < len(cat.CATEGORY_NAMES)+1: 
                    list_of_hist[chain.event_category][v][signal_str][sample.name].fill(chain, chain.lumiweight)  
                list_of_hist[len(cat.CATEGORY_NAMES)+1][v][signal_str][sample.name].fill(chain, chain.lumiweight)
             
        #
        # Save histograms
        #
        subjobAppendix = '_subJob' + args.subJob if args.subJob else ''
        mass_str = 'All' if args.massRegion is None else args.massRegion+'Mass'

        if not args.isTest:
            output_name = os.path.join(os.getcwd(), 'data', 'plotVariables', reco_or_gen_str, mass_str, signal_str)
        else:
            output_name = os.path.join(os.getcwd(), 'data', 'testArea', 'plotVariables', reco_or_gen_str, mass_str, signal_str)
        
        if args.signalOnly and args.genLevel:       output_name = os.path.join(output_name, 'signalOrdering', sample.output)
        else:      output_name = os.path.join(output_name, sample.output) 

        if args.isChild:
            output_name += '/tmp_'+sample.output+ '/'+sample.name+'_'
        else:
            output_name += '/'
        
        makeDirIfNeeded(output_name +'variables'+subjobAppendix+ '.root')
        output_file = TFile(output_name + 'variables' +subjobAppendix+ '.root', 'RECREATE')
        
        for v in var.keys():
            output_file.mkdir(v)
            output_file.cd(v)
            for c in categories:
                list_of_hist[c][v][signal_str][sample.name].getHist().Write()
        
        output_file.Close()

        cutter.saveCutFlow(output_name +'variables'+subjobAppendix+ '.root')

#If the option to not run over the events again is made, load in the already created histograms here
else:
    import glob
    
    # Collect signal file locations
    if args.genLevel and args.signalOnly:
        signal_list = glob.glob(os.getcwd()+'/data/plotVariables/'+reco_or_gen_str+'/signal/signalOrdering/*'+args.flavor+'*')
        
    elif not args.bkgrOnly:
        signal_list = glob.glob(os.getcwd()+'/data/plotVariables/'+reco_or_gen_str+'/signal/*'+args.flavor+'*')
        for i, s in enumerate(signal_list):
            if 'signalOrdering' in s:
                signal_list.pop(i)
    else:
        signal_list = []

    # Collect background file locations
    if not args.signalOnly:
        bkgr_list = glob.glob(os.getcwd()+'/data/plotVariables/'+reco_or_gen_str+'/bkgr/*')
    else:
        bkgr_list = []

    # Merge files if necessary
    for n in signal_list + bkgr_list:
        merge(n)

    # Load in the histograms from the files
    for c in categories: 
        for v in var.keys():
            if not args.bkgrOnly:
                for s in signal_list:
                    sample_name = s.split('/')[-1]
                    sample_mass = int(sample_name.split('-M')[-1])
                    if args.masses is not None and sample_mass not in args.masses: continue
                    #list_of_hist[c][v]['signal'][sample_name] = Histogram(getObjFromFile(s+'/variables.root', v+'/'+cat.categoryName(c)+'-'+cat.subcategoryName(c)+'-'+v+'-'+sample_name)) 
                    list_of_hist[c][v]['signal'][sample_name] = Histogram(getObjFromFile(s+'/variables.root', v+'/'+str(c)+'-'+v+'-'+sample_name)) 
            if not args.signalOnly:
                for b in bkgr_list:
                    sample_name = b.split('/')[-1]
                    #list_of_hist[c][v]['bkgr'][sample_name] = Histogram(getObjFromFile(b+'/variables.root', v+'/'+cat.categoryName(c)+'-'+cat.subcategoryName(c)+'-'+v+'-'+sample_name)) 
                    list_of_hist[c][v]['bkgr'][sample_name] = Histogram(getObjFromFile(b+'/variables.root', v+'/'+str(c)+'-'+v+'-'+sample_name)) 

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
output_dir = os.path.join(os.getcwd(), 'data', 'Results', 'plotVariables', reco_or_gen_str)

if args.masses is not None:         output_dir = os.path.join(output_dir, 'customMasses')

if args.massRegion is not None:     output_dir = os.path.join(output_dir, args.massRegion+'Mass')
else:                               output_dir = os.path.join(output_dir, 'allMass')

if args.signalOnly:
    output_dir = os.path.join(output_dir, 'signalOnly')
if args.bkgrOnly:
    output_dir = os.path.join(output_dir, 'bkgrOnly')

output_dir = makePathTimeStamped(output_dir)

#
# Create plots for each category
#
for c in categories:
    extra_text = [extraTextFormat(cat.returnTexName(c), xpos = 0.33, ypos = 0.9, textsize = None, align = 12)]  #Text to display event type in plot
    extra_text.append(extraTextFormat('V_{'+args.flavor+'N} = '+str(args.coupling)))  #Text to display event type in plot

    # Plots that display chosen for chosen signal masses and backgrounds the distributions for the different variables
    # S and B in same canvas for each variable
    for v in var:
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

        # Create plot object (if signal and background are displayed, also show the ratio)
        p = Plot(list_of_hist[c][v]['signal'].values(), legend_names, str(c)+'-'+v, bkgr_hist = bkgr_hist, y_log = True, extra_text = extra_text, draw_ratio = (not args.signalOnly and not args.bkgrOnly))

        # Draw
        p.drawHist(output_dir = os.path.join(output_dir, str(c)), normalize_signal=False, draw_option='EHist')
    
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
