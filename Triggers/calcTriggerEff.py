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
argParser.add_argument('--ignoreRef', action='store_true', default=False,  help='pass ref cuts')
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
# Load in the sample list 
#
from HNL.Samples.sample import createSampleList, getSampleFromList
sample_list = createSampleList(os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/triggerlist_'+str(args.year)+'.conf'))

#
# Submit subjobs
#
if not args.isChild:
    from HNL.Tools.jobSubmitter import submitJobs
    jobs = []
    for sample in sample_list:
        for njob in xrange(sample.splitJobs): 
            jobs += [(sample.name, str(njob))]

    submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'trigger_'+sample.name)
    exit(0)


#
# Load in sample and chain
#
sample = getSampleFromList(sample_list, args.sample)
chain = sample.initTree()
chain.year = int(args.year)

#
# Does an event pass the triggers
#
def passTriggers(c):
    if c._HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL or c._HLT_Mu8_DiEle12_CaloIdL_TrackIdL or c._HLT_DiMu9_Ele9_CaloIdL_TrackIdL or chain._HLT_TripleMu_12_10_5:        return True
    if c._HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ or c._HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ or c._HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_DZ:  return True
    if c._HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL or c._HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL:     return True
    if c._passTrigger_mm: return True
    if c._HLT_Ele27_WPTight_Gsf or c._HLT_IsoMu24 or c._HLT_IsoTkMu24:      return True
    return False


from HNL.Tools.helpers import makeDirIfNeeded
subjobAppendix = 'subJob' + args.subJob if args.subJob else ''
output_name = os.path.join(os.getcwd(), 'data', sample.output)
if args.isChild:
    output_name += '/tmp_'+sample.output
if not args.ignoreRef:        output_name += '/'+ sample.name +'_TrigEff_' +subjobAppendix+ '.root'
else:   output_name += '/'+ sample.name +'_TrigEffnoMET_' +subjobAppendix+ '.root'
    

#
# Define histograms
# Could these lists could have been done in a nicer way but since the wanted lepton is different for different var, I was too lazy for now. Redo later if needed
#                (channel, dim) 
category_map = {('eee', '1D') : ['integral'], 
                ('eee', '2D') : ['integral'], 
                ('eemu', '1D') : ('15to30', '30to55'),
                ('eemu', '2D') : ('15to20', '20to25', '25to30', '30to40', '40to50', '55to100'),
                ('emumu', '1D') : ('15to30', '30to55'),
                ('emumu', '2D') : ('15to20', '20to25', '25to30', '30to40', '40to50', '55to100'),
                ('mumumu', '1D') : ['integral'],
                ('mumumu', '2D') : ['integral']}

var = {('pt', '1D') : (lambda c : c._lPt[c.l3],                                 np.arange(5., 40., 5.),                 ('p_{T}(trailing) [GeV]', 'Events')),
       ('eta', '1D') : (lambda c : abs(c._lEta[c.l1]),                          np.arange(0., 3., .5),                  ('|#eta|(leading) [GeV]', 'Events')),
       ('pt', '2D') : (lambda c : (c._lPt[c.l3], c._lPt[c.l2]),                     (np.arange(5., 40., 5.), np.arange(5., 40., 5.)), ('p_{T}(trailing) [GeV]', 'p_{T}(subleading) [GeV]')),
       ('eta', '2D') : (lambda c : (abs(c._lEta[c.l3]), abs(c._lEta[c.l2])),      (np.arange(0., 3., .5), np.arange(0., 3., .5)), ('|#eta|(trailing) [GeV]', '|#eta|(subleading) [GeV]'))}

from HNL.Tools.efficiency import Efficiency
eff = {}
for channel, d in category_map.keys():
    for v in {k[0] for k in var.keys()}:
        for t in category_map[(channel, d)]:
            name = channel + '_' + d + '_' + v + '_' + t
            eff[name] = Efficiency(name, var[(v, d)][0], var[(v, d)][2], output_name, var[(v, d)][1])

#
# Set event range
#
if args.isTest:
    event_range = xrange(1000)
else:
    event_range = sample.getEventRange(args.subJob)    

#
# Loop over all events
#
from HNL.Tools.helpers import progress
from HNL.Triggers.eventSelection import select3Leptons, passedCategory
for entry in event_range:
    
    chain.GetEntry(entry)
    progress(entry - event_range[0], len(event_range))
     
    if not select3Leptons(chain): continue
    if not args.ignoreRef and not chain._passTrigger_ref:     continue

    weightfactor = 1.
    #if not sample.isData: weightfactor *= chain._weight

    passed = passTriggers(chain) 
    
    for channel, d in category_map.keys():
        for v in {k[0] for k in var.keys()}: 
            for t in category_map[(channel, d)]:
                
                if not passedCategory(chain, channel): continue
                if t != 'integral': 
                    lowpt, highpt = t.split('to')
                    if chain.l1_pt < float(lowpt) or chain.l1_pt > float(highpt): continue
                                
               
                name = channel + '_' + d + '_' + v + '_' + t
                eff[name].fill(chain, weightfactor, passed)

print eff['eee_2D_pt_integral'].getNumerator().GetSumOfWeights()
print eff['eee_2D_pt_integral'].getDenominator().GetSumOfWeights()
#if args.isTest: exit(0)

#
# Save all histograms
#
makeDirIfNeeded(output_name)

for channel, d in category_map.keys():
    for v in {k[0] for k in var.keys()}: 
        for t in category_map[(channel, d)]:
            name = channel + '_' + d + '_' + v + '_' + t
            eff[name].write(append=True)

