#! /usr/bin/env python

#
# Code to calculate trigger efficiency
#

import numpy as np

#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
argParser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018'])
argParser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
argParser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
argParser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
argParser.add_argument('--runLocal', action='store_true', default=False,  help='use local resources instead of Cream02')
argParser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
argParser.add_argument('--isoAlgo',   action='store',     default='none',  help='do not launch subjobs, only show them')
argParser.add_argument('--eleAlgo',   action='store',     default='none',  help='do not launch subjobs, only show them')
argParser.add_argument('--muAlgo',   action='store',     default='none',  help='do not launch subjobs, only show them')
args = argParser.parse_args()

#
# Change some settings if this is a test
#
if args.isTest:
    args.isChild = True
    args.sample = 'WZ'
    args.subJob = '0'
    args.year = '2016'
    args.isoAlgo = 'MVA2015'
    args.eleAlgo = 'none'

#
# All ID's and WP we want to test
# If you want to add a new algorithm, add a line below
# Make sure all algo keys and WP have a corresponding entry in HNL.ObjectSelection.tauSelector
#

tau_id_algos = {'MVA2017v2': ['vloose', 'loose', 'medium', 'tight', 'vtight'],
                'MVA2017v2New': ['vloose', 'loose', 'medium', 'tight', 'vtight'],
                'MVA2015': ['vloose', 'loose', 'medium', 'tight', 'vtight'],
                'MVA2015New': ['vloose', 'loose', 'medium', 'tight', 'vtight'],
                #'cut_based': ['vvloose', 'vloose', 'loose', 'medium', 'tight']),
                'deeptauVSjets': ['vvvloose', 'vvloose', 'vloose', 'loose', 'medium', 'tight', 'vtight', 'vvtight']
                }

ele_discr_algos = {'againstElectron': ['loose', 'tight'],
                  'deeptauVSe': ['vvvloose', 'vvloose', 'vloose', 'loose', 'medium', 'tight', 'vtight', 'vvtight']
                }
muon_discr_algos = {'againstMuon': ['loose', 'tight'],
                  'deeptauVSmu': ['vloose', 'loose', 'medium', 'tight']
                    }

#
# Make a full list of all algorithms that need to be checked in this event loop
#
full_list = []    
if tau_id_algos:
    full_list.extend([(k, 'none', 'none') for k in tau_id_algos.keys()]) 
if ele_discr_algos:
    full_list.extend([('none', k, 'none') for k in ele_discr_algos.keys()]) 
if muon_discr_algos:
    full_list.extend([('none', 'none', k) for k in muon_discr_algos.keys()]) 

print full_list
#
# Load in the sample list 
#
from HNL.Samples.sample import createSampleList, getSampleFromList
sample_list = createSampleList(os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/compareTauIdList_'+str(args.year)+'.conf'))

#
# Submit Jobs
# TODO: Rewrite so that it checks all ID's in a single event loop instead of using more resources than needed by having jobs for every algorithm
#
if not args.isChild:

    #TODO: find a more elegant way to make combinations of different algos
    #combos is a list of whether the isoAlgo, eleAlgo and muAlgo should be on
    #(isoAlgo, eleAlgo, muAlgo)

    from HNL.Tools.jobSubmitter import submitJobs
    jobs = []
    for sample in sample_list:
        for njob in xrange(sample.split_jobs):
            for c in tau_id_algos.keys():
                jobs += [(sample.name, str(njob), c, 'none', 'none')]
            for c in ele_discr_algos.keys():
                jobs += [(sample.name, str(njob),  'none', c, 'none')]
            for c in muon_discr_algos.keys():
                jobs += [(sample.name, str(njob),  'none', 'none', c)]

    submitJobs(__file__, ('sample', 'subJob', 'isoAlgo', 'eleAlgo', 'muAlgo'), jobs, argParser, jobLabel = 'trigger_'+sample.name)
    exit(0)

#
#Initialize chain
#
sample = getSampleFromList(sample_list, args.sample)
chain = sample.initTree(False)
isBkgr = not 'HNL' in sample.name

#add jets, electrons and muons to bkgr sample if needed
if isBkgr:
    bkgr_allowed_genstatus = []
    if args.isoAlgo != 'none':        bkgr_allowed_genstatus.append(6)
    if args.eleAlgo != 'none':        bkgr_allowed_genstatus.extend([1, 3])
    if args.muAlgo != 'none':         bkgr_allowed_genstatus.extend([2, 4])

#
#Set output dir
#
from HNL.Tools.helpers import makeDirIfNeeded
output_name = os.path.join(os.getcwd(), 'data', os.path.basename(__file__).split('.')[0], sample.output)
if args.isChild:
    output_name += '/tmp_'+sample.output
name = args.isoAlgo + '-' + args.eleAlgo + '-' + args.muAlgo
output_name += '/'+ sample.name + '_'+name+ '_' + args.subJob+'.root'
makeDirIfNeeded(output_name)


print 'Getting things ready to start the event loop'

#Initialize histograms
from HNL.Tools.ROC import ROC
if args.isoAlgo != 'none':
    algo_wp = tau_id_algos[args.isoAlgo]
elif args.eleAlgo != 'none':
    algo_wp = ele_discr_algos[args.eleAlgo]
elif args.muAlgo != 'none':
    algo_wp = muon_discr_algos[args.muAlgo]

algo_bin = np.arange(0., len(algo_wp)+1., 1)
var = lambda c, i : c.var[i]
efficiencies = ROC(name, var, 'tmp', output_name, algo_bin)   #TODO: Currently the way the var is implemented in Histogram class makes this a little cumbersome, change this

#Determine if testrun so it doesn't need to calculate the number of events in the getEventRange
if args.isTest:
    event_range = xrange(1000)
else:
    event_range = sample.getEventRange(int(args.subJob))


chain.var = np.arange(0.5, len(algo_wp)+0.5, 1)

from HNL.Tools.helpers import progress
from HNL.ObjectSelection.tauSelector import isGeneralTau
for entry in event_range:

    chain.GetEntry(entry)
    progress(entry - event_range[0], len(event_range))


    #Loop over real taus for efficiency
    for lepton in xrange(chain._nLight, chain._nL):
        
        if args.isoAlgo and not isGeneralTau(chain, lepton, args.isoAlgo, 'none', 'againstElectron', 'none', 'againstMuon', 'none', needDMfinding=False): continue
        elif args.isoAlgo == 'none' and not isGeneralTau(chain, lepton, args.isoAlgo, 'loose', 'againstElectron', 'none', 'againstMuon', 'none', needDMfinding=True): continue

        if chain._tauGenStatus[lepton] == 5 and not isBkgr: 
        
            for index, wp in enumerate(algo_wp):
                passed = isGeneralTau(chain, lepton, args.isoAlgo, wp, args.eleAlgo, wp, args.muAlgo, wp)
                efficiencies.fillEfficiency(chain, index, passed)


        elif isBkgr and chain._tauGenStatus[lepton] in bkgr_allowed_genstatus:
            for index, wp in enumerate(algo_wp):
                passed = isGeneralTau(chain, lepton, args.isoAlgo, wp, args.eleAlgo, wp, args.muAlgo, wp)
                efficiencies.fillMisid(chain, index, passed)


#
# Write
#
efficiencies.write(True)
