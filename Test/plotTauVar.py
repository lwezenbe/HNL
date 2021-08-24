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
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='prelegacy', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--genLevel',   action='store_true', default=False,  help='Use gen level variables')

argParser.add_argument('--makePlots',   action='store_true', default=False,  help='Use existing root files to make the plots')
args = argParser.parse_args()

from HNL.Tools.logger import getLogger, closeLogger
log = getLogger('INFO')

if args.isTest:
    if args.year is None: args.year = '2016'
    if args.sample is None: args.sample = 'DYJetsToLL-M-50'
    args.isChild = True

#
# Create histograms
#
var = { 'pt':      (lambda c : c.tau_pt,       np.arange(20., 200., 10.),       ('p_{T}^{#tau} [GeV]', 'Events')),
        'eta':      (lambda c : c.tau_eta,       np.arange(-2.5, 3., 0.5),       ('#eta_{#tau}', 'Events'))}

import HNL.EventSelection.eventCategorization as cat
categories = cat.CATEGORIES
reco_or_gen_str = 'reco' if not args.genLevel else 'gen'

from ROOT import TFile
from HNL.Tools.histogram import Histogram
from HNL.Tools.mergeFiles import merge
from HNL.Tools.helpers import getObjFromFile
list_of_hist = {}
from HNL.EventSelection.eventCategorization import EventCategory


#
# Loop over samples and events
#
from HNL.Samples.sampleManager import SampleManager
sample_manager = SampleManager(args.era, args.year, 'noskim', 'ObjectSelection/compareTauIdList_'+args.era+args.year)
jobs = []
for sample_name in sample_manager.sample_names:
    sample = sample_manager.getSample(sample_name)
    for njob in xrange(sample.returnSplitJobs()): 
        jobs += [(sample.name, str(njob))]

if not args.makePlots:
    #
    # Submit subjobs
    #
    if not args.isChild:
        from HNL.Tools.jobSubmitter import submitJobs
        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'plotTau')
        exit(0)


    #Start a loop over samples
    sample_names = []
    for sample in sample_manager.sample_list:
        if sample.name not in sample_manager.sample_names: continue
       
        if sample.name != args.sample: continue
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
            max_events = 20000
            event_range = xrange(max_events) if max_events < len(sample.getEventRange(args.subJob)) else sample.getEventRange(args.subJob)
        else:
            event_range = sample.getEventRange(args.subJob)

        chain.HNLmass = sample.getMass()
        chain.year = int(args.year)

        from HNL.Weights.lumiweight import LumiWeight
        lw = LumiWeight(sample, sample_manager)
        
        print sample.name
        #
        # Loop over all events
        #
        from HNL.Tools.helpers import progress, makeDirIfNeeded
        from HNL.EventSelection.eventSelectionTools import select3GenLeptons
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
        output_name = os.path.join(os.getcwd(), 'data', 'plotTau', args.era+args.year, reco_or_gen_str, sample.output)
        
        if args.isChild:
            output_name += '/tmp_'+sample.output+ '/'+sample.name+'_'
        else:
            output_name += '/'
        
        for iv, v in enumerate(var.keys()):
            if iv == 0: list_of_hist[sample.output][v].write(output_name + 'variables' +subjobAppendix+ '.root', subdirs=[v], is_test=args.isTest)
            else: list_of_hist[sample.output][v].write(output_name + 'variables' +subjobAppendix+ '.root', subdirs=[v], is_test=args.isTest, append=True)
        
#If the option to not run over the events again is made, load in the already created histograms here
else:
    import glob
    

    hist_list = glob.glob(os.getcwd()+'/data/plotTau/'+reco_or_gen_str+'/*')

    # Merge files if necessary
    merge(hist_list, __file__, jobs, ('sample', 'subJob'), argParser)

    list_of_hist = {}
    # Load in the histograms from the files
    for h in hist_list:
        sample_name = h.split('/')[-1]
        list_of_hist[sample_name] = {}
        for v in var.keys():
            list_of_hist[sample_name][v] = Histogram(getObjFromFile(h+'/variables.root', v+'/'+sample_name+'-'+v)) 

closeLogger(log)

#
#       Plot!
#
if args.isTest: 
    exit(0)

#
# Necessary imports
#
from HNL.Plotting.plot import Plot
from HNL.Tools.helpers import makePathTimeStamped

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
        p.drawHist(output_dir = output_dir, draw_option='EHist')