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
args = argParser.parse_args()

#
# Change some settings if this is a test
#
if args.isTest:
    args.isChild = True
    args.sample = 'WZ'
    args.subJob = '0'
    args.year = '2016'

#
# All ID's and WP we want to test
# If you want to add a new algorithm, add a line below
# Make sure all algo keys and WP have a corresponding entry in HNL.ObjectSelection.tauSelector
#
algos = {}
algos['tau_id'] = {'MVA2017v2': ['vloose', 'loose', 'medium', 'tight', 'vtight'],
                'MVA2017v2New': ['vloose', 'loose', 'medium', 'tight', 'vtight'],
                'MVA2015': ['vloose', 'loose', 'medium', 'tight', 'vtight'],
                'MVA2015New': ['vloose', 'loose', 'medium', 'tight', 'vtight'],
                #'cut_based': ['vvloose', 'vloose', 'loose', 'medium', 'tight']),
                'deeptauVSjets': ['vvvloose', 'vvloose', 'vloose', 'loose', 'medium', 'tight', 'vtight', 'vvtight']
                }

algos['ele_discr'] = {'againstElectron': ['loose', 'tight'],
                  'deeptauVSe': ['vvvloose', 'vvloose', 'vloose', 'loose', 'medium', 'tight', 'vtight', 'vvtight']
                } 

algos['mu_discr'] = {'againstMuon': ['loose', 'tight'],
                  'deeptauVSmu': ['vloose', 'loose', 'medium', 'tight']
                    }

def getHighestLen():
    max_len = 0
    for a in ['tau_id', 'ele_discr', 'mu_discr']:
        for ak in algos[a].keys():
            if len(algos[a][ak]) > max_len:      max_len = len(algos[a][ak])
    return max_len    

#
# Make a full list of all algorithms that need to be checked in this event loop
# Not really needed at the moment but implemented with idea of combining algorithms later
#
full_list = []    
full_list.extend([(k, 'none', 'none') for k in algos['tau_id'].keys()]) 
full_list.extend([('none', k, 'none') for k in algos['ele_discr'].keys()]) 
full_list.extend([('none', 'none', k) for k in algos['mu_discr'].keys()]) 

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

    from HNL.Tools.jobSubmitter import submitJobs
    jobs = []
    for sample in sample_list:
        for njob in xrange(sample.split_jobs):
            jobs += [(sample.name, str(njob))]

    submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'compareTauID')
    exit(0)

#
#Initialize chain
#
sample = getSampleFromList(sample_list, args.sample)
chain = sample.initTree(False)
isBkgr = not 'HNL' in sample.name

#add jets, electrons and muons to bkgr sample if needed

def allowedGenstatus(isoAlgo, eleAlgo, muAlgo):
    bkgr_allowed_genstatus = []
    if isoAlgo != 'none':        bkgr_allowed_genstatus.append(6)
    if eleAlgo != 'none':        bkgr_allowed_genstatus.extend([1, 3])
    if muAlgo != 'none':         bkgr_allowed_genstatus.extend([2, 4])
    return bkgr_allowed_genstatus
#
#Set output dir
#
from HNL.Tools.helpers import makeDirIfNeeded
output_name = os.path.join(os.getcwd(), 'data', os.path.basename(__file__).split('.')[0], sample.output)
if args.isChild:
    output_name += '/tmp_'+sample.output


print 'Getting things ready to start the event loop'

def getWP(algorithm):
    
    algorithm_wp = None
    if algorithm[0] != 'none':
        algorithm_wp = algos['tau_id'][algorithm[0]]
    elif algorithm[1] != 'none':
        algorithm_wp = algos['ele_discr'][algorithm[1]]
    elif algorithm[2] != 'none':
        algorithm_wp = algos['mu_discr'][algorithm[2]]
    return algorithm_wp

#Initialize histograms
from HNL.Tools.ROC import ROC
list_of_roc = []
for algo in full_list:

    algo_wp = getWP(algo) 
 
    algo_bin = np.arange(0., len(algo_wp)+1., 1)
    var = lambda c, i : c.var[i]
    
    name = algo[0] + '-' + algo[1] + '-' + algo[2]
    tot_name = output_name+'/'+ sample.name + '_'+name+ '_' + args.subJob+'.root'
    makeDirIfNeeded(tot_name)
    list_of_roc.append(ROC(name, var, 'tmp', tot_name, algo_bin))   #TODO: Currently the way the var is implemented in Histogram class makes this a little cumbersome, change this

#Determine if testrun so it doesn't need to calculate the number of events in the getEventRange
if args.isTest:
    event_range = xrange(1000)
else:
    event_range = sample.getEventRange(int(args.subJob))

chain.var = np.arange(0.5, getHighestLen()+0.5, 1)

from HNL.Tools.helpers import progress
from HNL.ObjectSelection.tauSelector import isGeneralTau
for entry in event_range:

    chain.GetEntry(entry)
    progress(entry - event_range[0], len(event_range))


    #Loop over real taus for efficiency
    for lepton in xrange(chain._nLight, chain._nL):
       
        for i, algo in enumerate(full_list): 
            if algo[0] != 'none' and not isGeneralTau(chain, lepton, algo[0], 'none', 'againstElectron', 'none', 'againstMuon', 'none', needDMfinding=False): continue
            elif algo[0] == 'none' and not isGeneralTau(chain, lepton, algo[0], 'loose', 'againstElectron', 'none', 'againstMuon', 'none', needDMfinding=True): continue

            if chain._tauGenStatus[lepton] == 5 and not isBkgr: 
            
                for index, wp in enumerate(getWP(algo)):
                    passed = isGeneralTau(chain, lepton, algo[0], wp, algo[1], wp, algo[2], wp)
                    list_of_roc[i].fillEfficiency(chain, index, passed)


            elif isBkgr and chain._tauGenStatus[lepton] in allowedGenstatus(algo[0], algo[1], algo[2]):
                for index, wp in enumerate(getWP(algo)):
                    passed = isGeneralTau(chain, lepton, algo[0], wp, algo[1], wp, algo[2], wp)
                    list_of_roc[i].fillMisid(chain, index, passed)


#
# Write
#
for r in list_of_roc:
    r.write(True)
