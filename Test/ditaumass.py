#! /usr/bin/env python

#
# Code to plot mutau mass to compare to POG
#

import numpy as np

#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='prelegacy', choices = ['UL', 'prelegacy'],   help='Select era', required=True)
submission_parser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')

argParser.add_argument('--makePlots',   action='store_true', default=False,  help='Use existing root files to make the plots')

args = argParser.parse_args()



if args.isTest:
    args.year = '2018'
    args.sample = 'DYJetsToLL-M-50'
    args.isChild = True

#
# Create histograms
#
var = { 'mvis':      (lambda c : c.m_vis,       np.arange(0., 310., 10.),       ('m_{vis} [GeV]', 'Events'))}

from HNL.Tools.histogram import Histogram
from HNL.Tools.mergeFiles import merge
from HNL.Tools.helpers import getObjFromFile
list_of_hist = {}
from HNL.EventSelection.eventCategorization import EventCategory
#
# Load in the sample list 
#
from HNL.Samples.sampleManager import SampleManager
sample_manager = SampleManager(args.era, args.year, 'noskim', 'ditaumass_'+args.era+args.year)

#
# Loop over samples and events
#
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

        for v in var:
            list_of_hist[sample.name][v] = Histogram(sample.output + '-' + v, var[v][0], var[v][2], var[v][1])
       
        from HNL.EventSelection.cutter import Cutter
        cutter = Cutter(chain = chain)

        #
        # Get luminosity weight
        #
        from HNL.Weights.lumiweight import LumiWeight
        lw = LumiWeight(sample, sample_manager)

        #
        # Set event range
        #
        if args.isTest:
            max_events = 20000
            event_range = xrange(max_events) if max_events < len(sample.getEventRange(args.subJob)) else sample.getEventRange(args.subJob)
        else:
            event_range = xrange(chain.GetEntries())

        chain.year = args.year
        chain.era = args.era
        
        print sample.name
        #
        # Loop over all events
        #
        from HNL.Tools.helpers import progress, deltaR, getLeptonFourVecFromChain
        from HNL.ObjectSelection.muonSelector import isGoodMuon
        from HNL.ObjectSelection.tauSelector import isGeneralTau
        from HNL.ObjectSelection.leptonSelector import isGoodLightLepton
        ec = EventCategory(chain)
        for entry in event_range:
            
            chain.GetEntry(entry)
            progress(entry - event_range[0], len(event_range))

            cutter.cut(True, 'total')

            keep_event = True

            #
            # Select single muon
            #
            muon_index = None
            for mu in xrange(chain._nMu):
                if not isGoodMuon(chain, mu, 'tight'): continue
                if not chain._lPt[mu] < 25: continue
                if muon_index is not None:  
                    keep_event = False
                    break
                else:
                    muon_index = mu
            
            if not cutter.cut(muon_index is not None, "Found muon"): continue
            if not cutter.cut(keep_event, "More than one tight muon"): continue

            #
            # Veto events with an extra light lepton
            #
            for l in xrange(chain._nLight):
                if l == muon_index: continue
                if isGoodLightLepton(chain, l, 'loose'):
                    keep_event = False
                    break

            if not cutter.cut(keep_event, "Third loose light lepton veto"): continue

            #
            # Select tau candidates
            #
            tau_candidates = []
            for tau in xrange(chain._nLight, chain._nL):
                if not isGeneralTau(chain, tau, 'deeptauVSjets', 'tight', 'deeptauVSe', 'vvloose', 'deeptauVSmu', 'vloose'): continue
                if chain._dz[tau] > 0.2: continue
                if deltaR(chain._lEta[muon_index], chain._lEta[tau], chain._lPhi[muon_index], chain._lPhi[tau]) < 0.5: continue
                tau_candidates.append(tau)
            
            if not cutter.cut(len(tau_candidates) != 0, "Has tau candidates"): continue
            
            #
            # Select most isolated tau candidate
            #
            tau_index = tau_candidates[0]
            for tau in tau_candidates[1:]:
                if chain._tauDeepTauVsJetsRaw[tau] > chain._tauDeepTauVsJetsRaw[tau_index]: 
                    tau_index = tau

            mu_vec = getLeptonFourVecFromChain(chain, muon_index)
            tau_vec = getLeptonFourVecFromChain(chain, tau_index)
            chain.m_vis = (mu_vec + tau_vec).M()

            for v in var.keys():
                list_of_hist[sample.name][v].fill(chain, lw.getLumiWeight())
                    
        #
        # Save histograms
        #
        
        subjobAppendix = '_subJob' + args.subJob if args.subJob else '_0'
        if not args.isTest:
            output_name = os.path.join(os.getcwd(), 'data', __file__.split('.')[0], args.era+'-'+args.year, sample.output)
        else:
            output_name = os.path.join(os.getcwd(), 'data', 'testArea', __file__.split('.')[0], args.era+'-'+args.year, sample.output)

        output_name += '/tmp_'+sample.output+ '/'+sample.name+'_'
                
        for iv, v in enumerate(var.keys()):
            if iv == 0: list_of_hist[sample.name][v].write(output_name + 'variables' +subjobAppendix+ '.root', subdirs=[v], is_test=args.isTest)
            else: list_of_hist[sample.name][v].write(output_name + 'variables' +subjobAppendix+ '.root', subdirs=[v], append=True, is_test=args.isTest)

        cutter.saveCutFlow(output_name +'variables'+subjobAppendix+ '.root')


#If the option to not run over the events again is made, load in the already created histograms here
else:
    import glob
    

    hist_list = glob.glob(os.getcwd()+'/data/'+__file__.split('.')[0]+'/'+args.era+'-'+args.year+'/*')

    # Merge files if necessary
    merge(hist_list, __file__, jobs, ('sample', 'subJob'), argParser)

    list_of_hist = {}
    legend_names = {}
    # Load in the histograms from the files
    for v in var.keys():
        list_of_hist[v] = []
        legend_names[v] = []
        for h in hist_list:
            sample_name = h.split('/')[-1]
            list_of_hist[v].append(Histogram(getObjFromFile(h+'/variables.root', v+'/'+sample_name+'-'+v)))
            legend_names[v].append(sample_name)

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
output_dir = os.path.join(os.getcwd(), 'data', 'Results', __file__.split('.')[0], args.era+'-'+args.year)

output_dir = makePathTimeStamped(output_dir)

#
# Create plots for each category
#
for v in var:
    # Create plot object (if signal and background are displayed, also show the ratio)
    p = Plot(list_of_hist[v], legend_names[v], v, y_log = False, color_palette='StackTauPOGbyName', year = args.year, era = args.era)

    # Draw
    p.drawHist(output_dir = output_dir, draw_option='Stack')
