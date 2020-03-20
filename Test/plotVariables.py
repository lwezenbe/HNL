#! /usr/bin/env python

#
# Code to plot basic variables that are already contained in a tree that was skimmed for baseline events
#

import numpy as np
l1 = 0
l2 = 1
l3 = 2

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
argParser.add_argument('--runLocal', action='store_true', default=False,  help='use local resources instead of Cream02')
argParser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
argParser.add_argument('--makePlots',   action='store_true', default=False,  help='Use existing root files to make the plots')
argParser.add_argument('--showCuts',   action='store_true', default=False,  help='Show what the pt cuts were for the category in the plots')
argParser.add_argument('--runOnCream',   action='store_true', default=False,  help='Submit jobs on the cluster')
argParser.add_argument('--genLevel',   action='store_true', default=False,  help='Use gen level variables')
argParser.add_argument('--signalOnly',   action='store_true', default=False,  help='Run or plot a only the signal')
argParser.add_argument('--bkgrOnly',   action='store_true', default=False,  help='Run or plot a only the background')
argParser.add_argument('--lowMass',   action='store_true', default=False,  help='Only run or plot samples with mass below or equal to 80 GeV')
argParser.add_argument('--highMass',   action='store_true', default=False,  help='Only run or plot samples with mass below or equal to 80 GeV')
argParser.add_argument('--masses', type=int, nargs='*',  help='Only run or plot signal samples with mass given in this list')
argParser.add_argument('--coupling', action='store', default='',  help='Which coupling should be active?' , choices=['tau', 'e', 'mu', ''])
#argParser.add_argument('--triggerTest', type=str, default=None,  help='Some settings to perform pt cuts for triggers')
args = argParser.parse_args()

if args.isTest:
    args.year = '2016'
    args.sample = 'DYJetsToLL-M-10to50'

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
            'NJet':      (lambda c : c.njets,       np.arange(0., 12., 1.),       ('#Jets', 'Events')),
            'NbJet':      (lambda c : c.nbjets,       np.arange(0., 12., 1.),       ('#B Jets', 'Events'))
        }

import HNL.EventSelection.eventCategorization as cat
#categories = cat.CATEGORIES
categories = cat.SUPER_CATEGORIES
reco_or_gen_str = 'reco' if not args.genLevel else 'gen'

from ROOT import TFile, TLorentzVector
from HNL.Tools.histogram import Histogram
from HNL.Tools.mergeFiles import merge
from HNL.Tools.helpers import getObjFromFile
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
    from HNL.Samples.sample import createSampleList
    gen_name = 'Gen' if args.genLevel else 'Reco'
    list_location = os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/sampleList_'+str(args.year)+'_'+gen_name+'.conf')
    #list_location = os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/sampleList_'+str(args.year)+'_noskim.conf')
    sample_list = createSampleList(list_location)


    #
    # Submit subjobs
    #
    if args.runOnCream and not args.isChild:
        from HNL.Tools.jobSubmitter import submitJobs
        jobs = []
        for sample in sample_list:
            if args.signalOnly and not 'HNL' in sample.name: continue
            if args.bkgrOnly and 'HNL' in sample.name: continue
            for njob in xrange(sample.split_jobs): 
                jobs += [(sample.name, str(njob))]

        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'plotVar')
        exit(0)


    #Start a loop over samples
    sample_names = []
    for sample in sample_list:
       
        if args.runOnCream and sample.name != args.sample: continue
        if args.sample and sample.name != args.sample: continue
        #
        # Load in sample and chain
        #
        chain = sample.initTree(needhcount=False)
        sample_names.append(sample.name)

        is_signal = 'HNL' in sample.name
        signal_str = 'signal' if is_signal else 'bkgr'

        if args.signalOnly and not is_signal:   continue
        if args.bkgrOnly and is_signal:         continue

        for c in categories:
            for v in var:
                #list_of_hist[c][v][signal_str][sample.name] = Histogram(cat.categoryName(c)+'-'+cat.subcategoryName(c)+'-'+v+'-'+sample.output, var[v][0], var[v][2], var[v][1])
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

        chain.HNLmass = float(sample.name.rsplit('-', 1)[1]) if is_signal else None
        chain.year = int(args.year)
        if args.lowMass and chain.HNLmass > 80: continue
        if args.highMass and chain.HNLmass < 80: continue
        if args.masses is not None and chain.HNLmass not in args.masses: continue
        #
        # Loop over all events
        #
        from HNL.Tools.helpers import progress, makeDirIfNeeded
        from HNL.EventSelection.signalLeptonMatcher import SignalLeptonMatcher
        from HNL.EventSelection.eventSelection import select3Leptons, calculateKinematicVariables
        from HNL.EventSelection.eventCategorization import EventCategory
        ec = EventCategory(chain)
        for entry in event_range:
            
            chain.GetEntry(entry)
            progress(entry - event_range[0], len(event_range))
 
            if args.genLevel and args.signalOnly:
                slm = SignalLeptonMatcher(chain)
                if not slm.saveNewOrder(): continue
                calculateKinematicVariables(chain, chain, is_reco_level=False)
           
            if not select3Leptons(chain, chain):    continue 
            calculateKinematicVariables(chain, chain, is_reco_level=not args.genLevel)

            chain.event_category, chain.event_subcategory = ec.returnCategory()
            chain.event_supercategory = ec.returnSuperCategory()
            if chain.event_category == 2:       chain.event_category = 1

            #Add here any additional cuts
            l1Vec = TLorentzVector(chain.l_pt[0], chain.l_eta[0], chain.l_phi[0], chain.l_e[0])
            l2Vec = TLorentzVector(chain.l_pt[1], chain.l_eta[1], chain.l_phi[1], chain.l_e[1])
            l3Vec = TLorentzVector(chain.l_pt[2], chain.l_eta[2], chain.l_phi[2], chain.l_e[2])
            chain.Ml12 = (l1Vec+l2Vec).M()         
            chain.Ml23 = (l2Vec+l3Vec).M()         
            chain.Ml13 = (l1Vec+l3Vec).M()         

            for v in var.keys():
                #if chain.event_category < len(cat.CATEGORY_NAMES)+1 and chain.event_subcategory < len(cat.SUBCATEGORY_NAMES[cat.CATEGORY_SUBCATEGORY_LINK[chain.event_category]])+1: 
                    #list_of_hist[(chain.event_category, chain.event_subcategory)][v][signal_str][sample.name].fill(chain, chain.lumiweight)
                if chain.event_supercategory < len(cat.SUPER_CATEGORY_NAMES)+1: 
                    
                    list_of_hist[chain.event_supercategory][v][signal_str][sample.name].fill(chain, chain.lumiweight)
                    
                #list_of_hist[(len(cat.CATEGORY_NAMES)+1, len(cat.SUBCATEGORY_NAMES[cat.CATEGORY_SUBCATEGORY_LINK[len(cat.CATEGORY_NAMES)+1]])+1)][v][signal_str][sample.name].fill(chain, chain.lumiweight)
                list_of_hist[len(cat.SUPER_CATEGORY_NAMES)+1][v][signal_str][sample.name].fill(chain, chain.lumiweight)
            #if chain.event_category == 1 and chain.event_subcategory == 3: 
            #    print list_of_hist[(chain.event_category, chain.event_subcategory)]['l1pt'][signal_str][sample.name].getHist().GetSumOfWeights()
            #    print len(cat.SUBCATEGORY_NAMES[cat.CATEGORY_SUBCATEGORY_LINK[chain.event_category]])                

        #
        # Save histograms
        #
        if args.isTest:  continue
        subjobAppendix = '_subJob' + args.subJob if args.subJob else ''
        output_name = os.path.join(os.getcwd(), 'data', 'plotVariables', reco_or_gen_str, signal_str)
        
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

#If the option to not run over the events again is made, load in the already created histograms here
else:
    import glob
    
    # Collect signal file locations
    if args.genLevel and args.signalOnly:
        signal_list = glob.glob(os.getcwd()+'/data/plotVariables/'+reco_or_gen_str+'/signal/signalOrdering/*'+args.coupling+'*')
        
    elif not args.bkgrOnly:
        signal_list = glob.glob(os.getcwd()+'/data/plotVariables/'+reco_or_gen_str+'/signal/*'+args.coupling+'*')
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
                    if args.lowMass and sample_mass > 80: continue
                    if args.highMass and sample_mass < 80: continue
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
from HNL.EventSelection.eventCategorization import returnCategoryPtCuts

#
# Set output directory, taking into account the different options
#
output_dir = os.path.join(os.getcwd(), 'data', 'Results', 'plotVariables', reco_or_gen_str)

if args.masses is not None:        output_dir = os.path.join(output_dir, 'customMasses')
if args.lowMass:        output_dir = os.path.join(output_dir, 'lowMass')
elif args.highMass:        output_dir = os.path.join(output_dir, 'highMass')
else:                           output_dir = os.path.join(output_dir, 'allMass')

if args.signalOnly:
    output_dir = os.path.join(output_dir, 'signalOnly')
if args.bkgrOnly:
    output_dir = os.path.join(output_dir, 'bkgrOnly')

output_dir = makePathTimeStamped(output_dir)

#
# Create plots for each category
#
for c in categories:
    extra_text = [extraTextFormat(cat.returnTexName(c), xpos = 0.6, ypos = 0.75, textsize = None, align = 12)]  #Text to display event type in plot

    # Plots that displays chosen for chosen signal masses and backgrounds the distributions for the different variables
    # S and B in same canvas for each variable
    for v in var:
        legend_names = list_of_hist[c][v]['signal'].keys()+list_of_hist[c][v]['bkgr'].keys()
        
        # Make list of background histograms for the plot object (or None if no background)
        if not list_of_hist[c][v]['bkgr'].values(): 
            bkgr_hist = None
        else:
            bkgr_hist = list_of_hist[c][v]['bkgr'].values()
       
        # Make list of signal histograms for the plot object
        if not list_of_hist[c][v]['signal'].values(): 
            signal_hist = None
        else:
            signal_hist = list_of_hist[c][v]['signal'].values()

        # Create plot object (if signal and background are displayed, also show the ratio)
        if not args.signalOnly:
            #p = Plot(list_of_hist[c][v]['signal'].values(), legend_names, cat.categoryName(c)+'-'+cat.subcategoryName(c)+'-'+v, bkgr_hist = bkgr_hist, y_log = True, extra_text = extra_text, draw_ratio=True)
            #p = Plot(list_of_hist[c][v]['signal'].values(), legend_names, str(c)+'-'+v, bkgr_hist = bkgr_hist, y_log = False, extra_text = extra_text, draw_ratio=True)
            p = Plot(list_of_hist[c][v]['signal'].values(), legend_names, str(c)+'-'+v, bkgr_hist = bkgr_hist, y_log = True, draw_ratio=True)
        else:
            #p = Plot(list_of_hist[c][v]['signal'].values(), legend_names, cat.categoryName(c)+'-'+cat.subcategoryName(c)+'-'+v, bkgr_hist = bkgr_hist, y_log = True, extra_text = extra_text)
            p = Plot(list_of_hist[c][v]['signal'].values(), legend_names, str(c)+'-'+v, bkgr_hist = bkgr_hist, y_log = True, extra_text = extra_text)

        # Draw
        #p.drawHist(output_dir = os.path.join(output_dir, cat.categoryName(c), cat.subcategoryName(c)), normalize_signal=False, signal_style=True, draw_option='EHist')
        p.drawHist(output_dir = os.path.join(output_dir, str(c)), normalize_signal=False, signal_style=True, draw_option='EHist')
    
    # If looking at signalOnly, also makes plots that compares the three lepton pt's for every mass point
    if args.signalOnly:

        all_cuts = returnCategoryPtCuts(c)
        
        for cuts in all_cuts:   
 
            # Load in efficiency to print on canvas if requested
            if args.showCuts:
                eff_file = os.path.expandvars('$CMSSW_BASE/src/HNL/EventSelection/data/calcSignalEfficiency/HNLtau/divideByCategory/triggerTest/signalSelectionFull.root')
                eff = Efficiency('efficiency_'+str(c[0])+'_'+str(c[1]) + '_l1_'+str(cuts[0])+'_l2_'+str(cuts[1])+'_l3_'+str(cuts[2]), None, None, eff_file, subdirs=['efficiency_'+str(c[0])+'_'+str(c[1]), 'l1_'+str(cuts[0])+'_l2_'+str(cuts[1])+'_l3_'+str(cuts[2])])           
 
            # Loop over different signals and draw the pt
            for n in list_of_hist[c][v]['signal'].keys():
                h = [list_of_hist[c]['l1pt']['signal'][n], list_of_hist[c]['l2pt']['signal'][n], list_of_hist[c]['l3pt']['signal'][n]]
                legend_names = ['l1', 'l2', 'l3']
                
                # Prepare to draw the pt cuts on the canvas if requested
                if args.showCuts:
                    draw_cuts = [cuts, eff.getEfficiency(inPercent=True).GetBinContent(eff.getEfficiency().FindBin(float(n.split('-')[1].split('M')[1])))]
                else:
                    draw_cuts = None
                # Create plot object and draw
                #p = Plot(h, legend_names, cat.categoryName(c)+'-'+cat.subcategoryName(c)+'-pt-'+n, extra_text=extra_text)
                p = Plot(h, legend_names, str(c)+'-pt-'+n, extra_text=extra_text)
                #p.drawHist(output_dir = os.path.join(output_dir, cat.categoryName(c), cat.subcategoryName(c), 'pt', 'l1_'+str(cuts[0])+'_l2_'+str(cuts[1])+'_l3_'+str(cuts[2])), normalize_signal=False, draw_option='EHist', draw_cuts=draw_cuts)
                p.drawHist(output_dir = os.path.join(output_dir, str(c), 'pt', 'l1_'+str(cuts[0])+'_l2_'+str(cuts[1])+'_l3_'+str(cuts[2])), normalize_signal=False, draw_option='EHist', draw_cuts=draw_cuts)
