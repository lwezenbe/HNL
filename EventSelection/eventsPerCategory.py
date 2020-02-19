#! /usr/bin/env python

#
#       Code to calculate signal efficiency
#
# Can be used on RECO level, where you check how many events pass the reco selection
# Is also used to check how many events on a generator level pass certain pt cuts
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
args = argParser.parse_args()


#
# Change some settings if this is a test
#
if args.isTest:
    args.isChild = True
    args.sample = 'HNLtau-200'
    args.subJob = '0'
    args.year = '2016'


#
# Load in the sample list 
#
from HNL.Samples.sample import createSampleList, getSampleFromList
list_location = os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/sampleList_'+args.year+'_noskim.conf')
sample_list = createSampleList(list_location)

#
# Submit subjobs
#
if not args.isChild:
    from HNL.Tools.jobSubmitter import submitJobs
    jobs = []
    for sample in sample_list:
        print sample.name
        for njob in xrange(sample.split_jobs):
            jobs += [(sample.name, str(njob))]

    submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'calcSignalEfficiency')
    exit(0)


#
# Load in sample and chain
#
sample = getSampleFromList(sample_list, args.sample)
chain = sample.initTree()

if args.isTest:
    event_range = xrange(1000)
    #event_range = sample.getEventRange(args.subJob)    
else:
    event_range = sample.getEventRange(args.subJob)    

if 'HNL' in sample.name:
    chain.HNLmass = float(sample.name.rsplit('-', 1)[1])
chain.year = int(args.year)

#
# Get luminosity weight
#
from HNL.Weights.lumiweight import LumiWeight
lw = LumiWeight(sample, chain, list_location)

from HNL.EventSelection.eventCategorization import EventCategory
ec = EventCategory(chain)

from HNL.Tools.histogram import Histogram



list_of_numbers = {}
list_of_numbers['total'] = Histogram('total', lambda c: 0.5, ('', 'Events'), np.arange(0., 2., 1.))
for c in ec.super_categories:
    list_of_numbers[c] = Histogram(str(c), lambda c: 0.5, ('', 'Events'), np.arange(0., 2., 1.))


subjobAppendix = 'subJob' + args.subJob if args.subJob else ''
output_name = os.path.join(os.getcwd(), 'data', __file__.split('.')[0], sample.output)

if args.isChild:
    output_name += '/tmp_'+sample.output

output_name += '/'+ sample.name +'_events_' +subjobAppendix+ '.root'



#
# Loop over all events
#
from HNL.Tools.helpers import progress
from HNL.EventSelection.eventSelection import select3Leptons, select3LightLeptons, select3GenLeptons, lowMassCuts, passedPtCutsByCategory, passedCustomPtCuts
from HNL.EventSelection.signalLeptonMatcher import SignalLeptonMatcher
from HNL.ObjectSelection.leptonSelector import isFOLepton, isTightLepton
for entry in event_range:
    
    chain.GetEntry(entry)
    progress(entry - event_range[0], len(event_range))

    lw.getLumiWeight()
    if not select3Leptons(chain, chain, tau_algo='gen_truth'):   continue   

    list_of_numbers['total'].fill(chain, lw.getLumiWeight())
    list_of_numbers[ec.returnSuperCategory()].fill(chain, lw.getLumiWeight())

for i, h in enumerate(list_of_numbers.values()):
    if i == 0:
        h.write(output_name)
    else:
        h.write(output_name, append=True)
        
