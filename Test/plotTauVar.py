#! /usr/bin/env python

#
# Code to plot basic variables that are already contained in a tree that was skimmed for baseline events
#

import numpy as np
lumi = 36000
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
args = argParser.parse_args()

if args.isTest:
    args.year = '2016'
    args.sample = 'DY'

#
# Create histograms
#
var = { 'pt':      (lambda c : c.tau_pt,       np.arange(20., 200., 10.),       ('p_{T}^{#tau} [GeV]', 'Events')),
        'eta':      (lambda c : c.tau_eta,       np.arange(-2.5, 3., 0.5),       ('#eta_{#tau}', 'Events'))}

import HNL.EventSelection.eventCategorization as cat
categories = cat.CATEGORIES
reco_or_gen_str = 'reco' if not args.genLevel else 'gen'

from ROOT import TFile, TLorentzVector
from HNL.Tools.histogram import Histogram
from HNL.Tools.mergeFiles import merge
from HNL.Tools.helpers import getObjFromFile
list_of_hist = {}
from HNL.EventSelection.signalLeptonMatcher import SignalLeptonMatcher
from HNL.EventSelection.eventCategorization import EventCategory


#
# Loop over samples and events
#
if not args.makePlots:
    #
    # Load in the sample list 
    #
    from HNL.Samples.sampleManager import SampleManager
    sample_manager = SampleManager(args.year, 'noskim', 'compareTauIdList_'+str(args.year))

    #
    # Submit subjobs
    #
    if args.runOnCream and not args.isChild:
        from HNL.Tools.jobSubmitter import submitJobs
        jobs = []
        for sample_name in sample_manager.sample_names:
            sample = sample_manager.getSample(sample_name)
            for njob in xrange(sample.split_jobs): 
                jobs += [(sample.name, str(njob))]

        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'plotTau')
        exit(0)


    #Start a loop over samples
    sample_names = []
    for sample in sample_manager.sample_list:
        if sample.name not in sample_manager.sample_names: continue
       
        if args.runOnCream and sample.name != args.sample: continue
        if args.sample and sample.name != args.sample: continue

        list_of_hist[sample.name] = {}

        #
        # Load in sample and chain
        #
        chain = sample.initTree(needhcount=False)
        sample_names.append(sample.name)
        is_signal = 'HNL' in sample.name

        if not is_signal: continue

        #for c in categories:
        for v in var:
            list_of_hist[sample.output][v] = Histogram(sample.output + '-' + v, var[v][0], var[v][2], var[v][1])
       
        #
        # Set event range
        #
        if args.isTest:
            if len(sample.getEventRange(0)) < 1000:
                event_range = sample.getEventRange(0)
            else:
                event_range = xrange(1000)
        elif args.runOnCream:
            event_range = sample.getEventRange(args.subJob)
        else:
            event_range = xrange(chain.GetEntries())

        chain.HNLmass = sample.getMass()
        chain.year = int(args.year)

        from HNL.Weights.lumiweight import LumiWeight
        lw = LumiWeight(sample, sample_manager)
        
        print sample.name
        #
        # Loop over all events
        #
        from HNL.Tools.helpers import progress, makeDirIfNeeded
        from HNL.ObjectSelection.tauSelector import isGoodGenTau
        from HNL.EventSelection.eventSelection import select3GenLeptons
        ec = EventCategory(chain)
        for entry in event_range:
            
            chain.GetEntry(entry)
            progress(entry - event_range[0], len(event_range))

            if not select3GenLeptons(chain, chain):    continue

            chain.tau_pt = chain.l_pt[0]
            chain.tau_eta = chain.l_eta[0]
            for v in var.keys():
                list_of_hist[sample.output][v].fill(chain, lw.getLumiWeight())

#            for tau in xrange(chain._gen_nL):
#                if not isGoodGenTau(chain, tau):        continue                
#
#                chain.tau_pt = chain._gen_lPt[tau]
#                chain.tau_eta = chain._gen_lEta[tau]
#                for v in var.keys():
#                    list_of_hist[sample.output][v].fill(chain, 1.)
                    
        #
        # Save histograms
        #
        if args.isTest:  continue
        
        subjobAppendix = '_subJob' + args.subJob if args.subJob else ''
        output_name = os.path.join(os.getcwd(), 'data', 'plotTau', reco_or_gen_str, sample.output)
        
        if args.isChild:
            output_name += '/tmp_'+sample.output+ '/'+sample.name+'_'
        else:
            output_name += '/'
        
        makeDirIfNeeded(output_name +'variables'+subjobAppendix+ '.root')
        output_file = TFile(output_name + 'variables' +subjobAppendix+ '.root', 'RECREATE')
        
        for v in var.keys():
            output_file.mkdir(v)
            output_file.cd(v)
            list_of_hist[sample.output][v].getHist().Write()
        
        output_file.Close()

#If the option to not run over the events again is made, load in the already created histograms here
else:
    import glob
    

    hist_list = glob.glob(os.getcwd()+'/data/plotTau/'+reco_or_gen_str+'/*')

    # Merge files if necessary
    for n in hist_list:
        merge(n)

    list_of_hist = {}
    # Load in the histograms from the files
    for h in hist_list:
        sample_name = h.split('/')[-1]
        list_of_hist[sample_name] = {}
        for v in var.keys():
            list_of_hist[sample_name][v] = Histogram(getObjFromFile(h+'/variables.root', v+'/'+sample_name+'-'+v)) 

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
from HNL.EventSelection.eventCategorization import returnCategoryPtCuts

#
# Set output directory, taking into account the different options
#
output_dir = os.path.join(os.getcwd(), 'data', 'Results', 'plotTau', reco_or_gen_str)

output_dir = makePathTimeStamped(output_dir)

#
# Create plots for each category
#
for sample in list_of_hist.keys():
    for v in var:
        legend_names = [sample]
        # Create plot object (if signal and background are displayed, also show the ratio)
        p = Plot([list_of_hist[sample][v]], legend_names, sample+ '-' +v, y_log = True)

        # Draw
        p.drawHist(output_dir = output_dir,  signal_style=True, draw_option='EHist')
