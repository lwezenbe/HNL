#! /usr/bin/env python

#
# Code to calculate trigger efficiency
#

import numpy as np

#TODO: NEEDS AN UPDATE BADLY

#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='UL', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--flavor', type=int, default=0,  help='flavor of lepton under consideration. 0 = electron, 1 = muon', choices = [0, 1])
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--includeReco',   action='store_true', default=False, 
    help='look at the efficiency for a gen tau to be both reconstructed and identified. Currently just fills the efficiency for isolation')
submission_parser.add_argument('--onlyReco',   action='store_true', default=False,  help='look at the efficiency for a gen tau to be reconstructed. Currently just fills the efficiency for isolation')
submission_parser.add_argument('--logLevel',  action='store',      default='INFO',               help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])
args = argParser.parse_args()

from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)


#
# Change some settings if this is a test
#
if args.isTest:
    args.isChild = True
    if args.sample is None: args.sample = 'DYJetsToLL-M-50'
    if args.subJob is None: args.subJob = '0'
    if args.year is None: args.year = '2016'
    from HNL.Tools.helpers import generateArgString
    arg_string =  generateArgString(argParser)
else:
    arg_string = None

#
# All ID's and WP we want to test
# If you want to add a new algorithm, add a line below
# Make sure all algo keys and WP have a corresponding entry in HNL.ObjectSelection.tauSelector
#
algos = {'cutbased': ['loose', 'FO', 'tight'],
            'leptonMVAtop' : ['loose', 'FO', 'tight']}

#
# Load in the sample list 
#
from HNL.Samples.sampleManager import SampleManager
sample_manager = SampleManager(args.era, args.year, 'noskim', 'ObjectSelection/compareTauIdList_'+args.era+str(args.year))

#
# Submit Jobs
# TODO: Rewrite so that it checks all ID's in a single event loop instead of using more resources than needed by having jobs for every algorithm
#
jobs = []
for sample_name in sample_manager.sample_names:
    sample = sample_manager.getSample(sample_name)
    for njob in xrange(sample.returnSplitJobs()):
        jobs += [(sample.name, str(njob))]

if not args.isChild:

    from HNL.Tools.jobSubmitter import submitJobs
    submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'compareLightLepID')
    exit(0)

#
#Initialize chain
#
sample = sample_manager.getSample(args.sample)
chain = sample.initTree(False)
chain.year = int(args.year)
chain.era = args.era
isBkgr = not 'HNL' in sample.name

#
#Set output dir
#
from HNL.Tools.helpers import makeDirIfNeeded
if args.isTest:
    output_name = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'ObjectSelection', 'data', 'testArea', __file__.split('.')[0].rsplit('/')[-1], args.era+args.year)
else:
    output_name = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'ObjectSelection', 'data', __file__.split('.')[0].rsplit('/')[-1], args.era+args.year)
if args.includeReco: output_name = os.path.join(output_name, 'includeReco')
if args.onlyReco: output_name = os.path.join(output_name, 'onlyReco')
output_name = os.path.join(output_name, sample.output)
if args.isChild:
    output_name += '/tmp_'+sample.output

print 'Getting things ready to start the event loop'

#Initialize histograms
from HNL.Tools.ROC import ROC
from HNL.Tools.efficiency import Efficiency
list_of_roc = []
list_of_var_hist = {'efficiency' : {}, 'fakerate' : {}}
for algo in algos:

    algo_wp = algos[algo]

    tot_name = output_name+'/'+ sample.name + '_'+algo+'-ROC-'+str(args.flavor)+'_' + args.subJob+'.root'
    makeDirIfNeeded(tot_name)
    list_of_roc.append(ROC(algo, tot_name, working_points = algo_wp))

    #Efficiency histograms for variables
    var_hist = {'pt': [lambda c : c.pt_l, np.arange(0., 210., 10.),  ('p_T^{#tau}(offline) [GeV]' , 'Efficiency')],
                'eta': [lambda c : c.eta_l, np.arange(-2.5, 3., 0.5), ('#eta^{#tau}(offline) [GeV]' , 'Efficiency')]}
    
    list_of_var_hist['efficiency'][algo] = {}
    list_of_var_hist['fakerate'][algo] = {}
    for v in var_hist.keys():
        list_of_var_hist['efficiency'][algo][v] = {}
        list_of_var_hist['fakerate'][algo][v] = {}
        for wp in algo_wp:
            tot_name = output_name+'/'+ sample.name + '_efficiency-'+str(args.flavor)+'_' + args.subJob+'.root'
            list_of_var_hist['efficiency'][algo][v][wp] = Efficiency('efficiency_'+v+algo, var_hist[v][0], var_hist[v][2], tot_name, var_hist[v][1], subdirs = [algo + '-' + wp, 'efficiency_'+v])
            tot_name = output_name+'/'+ sample.name + '_fakerate-'+str(args.flavor)+'_' + args.subJob+'.root'
            list_of_var_hist['fakerate'][algo][v][wp] = Efficiency('fakerate_'+v+algo, var_hist[v][0], var_hist[v][2], tot_name, var_hist[v][1], subdirs = [algo + '-' + wp, 'fakerate_'+v])

#Determine if testrun so it doesn't need to calculate the number of events in the getEventRange
if args.isTest:
    max_events = 20000
    event_range = xrange(max_events) if max_events < len(sample.getEventRange(args.subJob)) else sample.getEventRange(args.subJob)
else:
    event_range = sample.getEventRange(int(args.subJob))

from HNL.Tools.helpers import progress
from HNL.ObjectSelection.electronSelector import isBaseElectron
from HNL.ObjectSelection.muonSelector import isBaseMuon
from HNL.ObjectSelection.leptonSelector import isGoodLightLeptonGeneral
from HNL.EventSelection.eventSelectionTools import selectGenLeptonsGeneral
from HNL.Tools.helpers import deltaR

def matchGenToReco(in_chain, l):
   
    min_dr = 0.3
    matched_lepton = None
    for lepton_index in xrange(in_chain._nLight):
        if not in_chain._lIsPrompt[lepton_index]: continue
        if in_chain._gen_lFlavor[l] != in_chain._lFlavor[lepton_index]: continue
        dr = deltaR(in_chain._gen_lEta[l], in_chain._lEta[lepton_index], in_chain._gen_lPhi[l], in_chain._lPhi[lepton_index])
        if dr < min_dr:
            matched_lepton = lepton_index
            min_dr = dr
        
    return matched_lepton

for entry in event_range:

    chain.GetEntry(entry)
    if args.isTest: progress(entry - event_range[0], len(event_range))

    #Loop over generator level taus if reco and id are measured
    if args.includeReco:
        if not selectGenLeptonsGeneral(chain, chain, 3): continue
        chain.pt_l = chain.l_pt[0]
        chain.eta_l = chain.l_eta[0]   
        matched_l = matchGenToReco(chain, chain.l_indices[0])
        for i, algo in enumerate(algos):
            passed_tot = []
            for wp in algos[algo]:
                passed = False
                if args.onlyReco: 
                    passed = matched_l is not None
                else:
                    passed = matched_l is not None and isGoodLightLeptonGeneral(chain, matched_l, algo=algo, workingpoint='tight')
                passed_tot.append(passed)
                for v in list_of_var_hist['efficiency'][algo].keys():
                    list_of_var_hist['efficiency'][algo][v][wp].fill(chain, 1., passed)
            list_of_roc[i].fillEfficiency(passed_tot)

    else:
        #Loop over real taus for efficiency
        for lepton in xrange(chain._nLight):
            if chain._lFlavor[lepton] != args.flavor: continue
            if args.flavor == 0 and not isBaseElectron(chain, lepton): continue
            if args.flavor == 1 and not isBaseMuon(chain, lepton): continue

            chain.pt_l = chain._lPt[lepton]
            chain.eta_l = chain._lEta[lepton]   
        
            for i, algo in enumerate(algos): 
                # if algo[0] != 'none' and not isGeneralTau(chain, lepton, algo[0], 'none', 'againstElectron', 'none', 'againstMuon', 'none', needDMfinding=False): continue

                if chain._lIsPrompt[lepton]:
                    passed_tot = []
                    for wp in algos[algo]:
                        passed = isGoodLightLeptonGeneral(chain, lepton, algo = algo, workingpoint = wp)
                        passed_tot.append(passed)
                        for v in list_of_var_hist['efficiency'][algo].keys():
                            list_of_var_hist['efficiency'][algo][v][wp].fill(chain, 1., passed)
                    list_of_roc[i].fillEfficiency(passed_tot)


                else:
                    passed_tot = []
                    for wp in algos[algo]:
                        passed = isGoodLightLeptonGeneral(chain, lepton, algo = algo, workingpoint = wp)
                        for v in list_of_var_hist['fakerate'][algo].keys():
                            list_of_var_hist['fakerate'][algo][v][wp].fill(chain, 1., passed)
                        passed_tot.append(passed)
                    list_of_roc[i].fillMisid(passed_tot)

#
# Write
#
for r in list_of_roc:
    r.write(True)

for eff in ['efficiency', 'fakerate']:
    for a, algo in enumerate(algos): 
        for i, v in enumerate(list_of_var_hist['fakerate'][algo].keys()):
            for j, wp in enumerate(list_of_var_hist['fakerate'][algo][v].keys()):
                if a == 0 and i == 0 and j == 0:
                    list_of_var_hist[eff][algo][v][wp].write(append = False, name = eff+'_'+v, is_test=arg_string)
                else:
                    list_of_var_hist[eff][algo][v][wp].write(append = True, name = eff+'_'+v, is_test=arg_string) 

closeLogger(log)
