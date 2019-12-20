#! /usr/bin/env python

#
# Code to plot basic variables that are already contained in a tree that was skimmed for baseline events
#

import numpy as np
lumi = 36000

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
argParser.add_argument('--runOnCream',   action='store_true', default=False,  help='Submit jobs on the cluster')
argParser.add_argument('--genLevel',   action='store_true', default=False,  help='Use gen level variables')
argParser.add_argument('--signalOnly',   action='store_true', default=False,  help='Run or plot a only the signal')
argParser.add_argument('--bkgrOnly',   action='store_true', default=False,  help='Run or plot a only the background')
args = argParser.parse_args()


#
# Create histograms
#
var = {'minMos':        (lambda c : c.minMos,   np.arange(0., 80., 8.),         ('min(M_{OS}) [GeV]', 'Events')),
        'm3l':          (lambda c : c.M3l,      np.arange(0., 240., 4.),         ('M_{3l} [GeV]', 'Events')),
        'met':          (lambda c : c._met,     np.arange(0., 300., 15.),         ('p_{T}^{miss} [GeV]', 'Events')),
        'mtOther':      (lambda c : c.mtOther,  np.arange(0., 300., 15.),       ('M_{T} (other min(M_{OS}) [GeV])', 'Events')),
        'l1pt':      (lambda c : c.l1_pt,       np.arange(0., 300., 5.),       ('p_{T} (l1) [GeV])', 'Events')),
        'l2pt':      (lambda c : c.l2_pt,       np.arange(0., 300., 5.),       ('p_{T} (l2) [GeV])', 'Events')),
        'l3pt':      (lambda c : c.l3_pt,       np.arange(0., 300., 5.),       ('p_{T} (l3) [GeV])', 'Events'))
        }

from HNL.Tools.histogram import Histogram
from HNL.Tools.mergeFiles import merge
from HNL.Tools.helpers import getObjFromFile
list_of_hist = {}
for v in var:
    list_of_hist[v] = {'signal':{}, 'bkgr':{}}

#
# Loop over samples and events
#
if not args.makePlots:
    #
    # Load in the sample list 
    #
    from HNL.Samples.sample import createSampleList, getSampleFromList
    gen_name = 'Gen' if args.genLevel else 'Reco'
    list_location = os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/sampleList_'+str(args.year)+'_'+gen_name+'.conf')
    sample_list = createSampleList(list_location)


    #
    # Submit subjobs
    #
    if args.runOnCream and not args.isChild:
        from HNL.Tools.jobSubmitter import submitJobs
        jobs = []
        for sample in sample_list:
            for njob in xrange(sample.split_jobs): 
                jobs += [(sample.name, str(njob))]

        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'plotVar_'+sample.name)
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

        for v in var:
            list_of_hist[v][signal_str][sample.name] = Histogram(v+'-'+sample.output, var[v][0], var[v][2], var[v][1])
        
        #
        # Set event range
        #
        if args.isTest:
            event_range = xrange(1000)
        elif args.runOnCream:
            event_range = sample.getEventRange(args.subJob)
        else:
            event_range = xrange(chain.GetEntries())
        print sample.name, len(event_range)    

        chain.HNLmass = float(sample.name.rsplit('-', 1)[1]) if is_signal else None
        chain.year = int(args.year)


        #
        # Loop over all events
        #
        from HNL.Tools.helpers import progress, makeDirIfNeeded
        from HNL.EventSelection.eventSelection import lowMassCuts, highMassCuts
        for entry in event_range:
           
 
            chain.GetEntry(entry)
            progress(entry - event_range[0], len(event_range))
        
            #Add here any additional cuts
            for v in var.keys():
                list_of_hist[v][signal_str][sample.name].fill(chain, chain.lumiweight)

        #
        # Save histograms
        #
        if args.runOnCream:
            subjobAppendix = 'subJob' + args.subJob if args.subJob else ''
            output_name = os.path.join(os.getcwd(), 'data', 'plotVariables', signal_str, sample.output)
            if args.isChild:
                output_name += '/tmp_'+sample.output
            for v in var.keys():
                makeDirIfNeeded(output_name + '/'+ sample.name +'_'+v+'_' +subjobAppendix+ '.root')
                list_of_hist[v][signal_str][sample.name].getHist().SaveAs(output_name + '/'+ sample.name +'_'+v+'_' +subjobAppendix+ '.root')

#TODO: This feels like it can easily make plots that make no sense
else:
    import glob
    signal_list = glob.glob(os.getcwd()+'/data/plotVariables/signal/*')
    bkgr_list = glob.glob(os.getcwd()+'/data/plotVariables/bkgr/*')
    for n in signal_list + bkgr_list:
        merge(n)
   
    for v in var.keys():
        if not args.bkgrOnly:
            for s in signal_list:
                sample_name = s.split('/')[-1]
                list_of_hist[v]['signal'][sample_name] = Histogram(getObjFromFile(s+'/'+v+'.root', v+'-'+sample_name)) 

        if not args.signalOnly:
            for b in bkgr_list:
                sample_name = b.split('/')[-1]
                list_of_hist[v]['bkgr'][sample_name] = Histogram(getObjFromFile(b+'/'+v+'.root', v+'-'+sample_name)) 

#
#       Plot!
#
if args.runOnCream or args.isTest: 
    exit(0)

from HNL.Plotting.plot import Plot
from HNL.Tools.helpers import makePathTimeStamped
output_dir =  makePathTimeStamped(os.getcwd()+'/data/Results')
for v in var:
    legend_names = list_of_hist[v]['signal'].keys()+list_of_hist[v]['bkgr'].keys()
    p = Plot(list_of_hist[v]['signal'].values(), legend_names, v, bkgr_hist = list_of_hist[v]['bkgr'].values(), y_log = True)
    p.drawHist(output_dir = output_dir, normalize_signal=True, signal_style=True)


