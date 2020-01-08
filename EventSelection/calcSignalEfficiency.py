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
argParser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
argParser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
argParser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
argParser.add_argument('--runLocal', action='store_true', default=False,  help='use local resources instead of Cream02')
argParser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
argParser.add_argument('--oldANcuts',   action='store_true', default=False,  help='do not launch subjobs, only show them')
argParser.add_argument('--FOcut',   action='store_true', default=False,  help='Perform baseline FO cut')
args = argParser.parse_args()


#
# Change some settings if this is a test
#
if args.isTest: 
    args.isChild = True
    args.sample = 'HNLtau-5'
    args.subJob = '0'
    args.year = '2016'


#
# Load in the sample list 
#
from HNL.Samples.sample import createSampleList, getSampleFromList
list_location = os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/signallist_'+str(args.year)+'.conf')
sample_list = createSampleList(list_location)

#
# Submit subjobs
#
if not args.isChild:
    from HNL.Tools.jobSubmitter import submitJobs
    jobs = []
    for sample in sample_list:
        for njob in xrange(sample.split_jobs): 
            jobs += [(sample.name, str(njob))]

    submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'calcSignalEfficiency')
    exit(0)


#
# Load in sample and chain
#
sample = getSampleFromList(sample_list, args.sample)
chain = sample.initTree()

subjobAppendix = 'subJob' + args.subJob if args.subJob else ''
output_name = os.path.join(os.getcwd(), 'data', sample.output)
if args.isChild:
    output_name += '/tmp_'+sample.output
output_name += '/'+ sample.name +'_signalSelection_' +subjobAppendix+ '.root'

#
# Calculate the range for the histograms. These are as a function of the mass of the signal samples.
# This function looks at the names of all samples and returns an array with all values right the middle of those
# It assumes the samples are ordered by mass in the input list
#
from HNL.Samples.sample import getListOfSampleNames
def getMassRange(sample_list_location):
    list_of_names = getListOfSampleNames(sample_list_location)
    all_masses = [float(name.rsplit('-', 1)[-1]) for name in list_of_names]
    m_range = []
    if len(all_masses) == 1:
        m_range = [all_masses[0]/2, all_masses[0]*1.5]
    else:
        for i, mass in enumerate(all_masses):
            if i != len(all_masses)-1: distance_to_next = all_masses[i+1] - mass
            if i == 0: m_range.append(mass - 0.5*distance_to_next)
            m_range.append(mass+0.5*distance_to_next)  #For last run, distance_to_next should still be the same
    return m_range

mass_range = getMassRange(list_location)

#
# Define the variables and axis name of the variable to fill and create efficiency objects
#
var = {'HNLmass': (lambda c : c.HNLmass,        np.array(mass_range),   ('m_{N} [GeV]', 'Events'))}

from HNL.Tools.efficiency import Efficiency
efficiency = Efficiency('efficiency', var['HNLmass'][0], var['HNLmass'][2], output_name, var['HNLmass'][1])
    
#
# Set event range
#
if args.isTest:
    #event_range = sample.getEventRange(args.subJob)    
    event_range = xrange(1000)
else:
    event_range = sample.getEventRange(args.subJob)    

chain.HNLmass = float(sample.name.rsplit('-', 1)[1])
chain.year = int(args.year)


#
# Loop over all events
#
from HNL.Tools.helpers import progress
from HNL.EventSelection.eventSelection import select3Leptons, select3LightLeptons,  lowMassCuts
from HNL.ObjectSelection.leptonSelector import isFOLepton
for entry in event_range:
    
    chain.GetEntry(entry)
    progress(entry - event_range[0], len(event_range))

    if args.FOcut:
        tmp = [l for l in xrange(chain._nL) if isFOLepton(chain, l)]
        if len(tmp) < 3: continue   

    if args.oldANcuts:
        passed = select3LightLeptons(chain, chain)
    else:
        passed = select3Leptons(chain, chain)

    if not lowMassCuts:         continue
    weight = chain._weight
    efficiency.fill(chain, weight, passed)   
    

#if args.isTest: exit(0)

#
# Save all histograms
#
efficiency.write()
