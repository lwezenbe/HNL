#! /usr/bin/env python

#
# Code to calculate trigger efficiency
#

import numpy as np

#TODO: Make for all three years and find a better way to deal with the categories

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
argParser.add_argument('--oldTriggers',   action='store_true', default=False,  help='Use triggers from AN 2017-014')
argParser.add_argument('--useRef', action='store_true', default=False,  help='pass ref cuts')
argParser.add_argument('--separateTriggers', action='store', default=None,  
    help='Look at each trigger separately for each category. Single means just one trigger, cumulative uses cumulative OR of all triggers that come before the chosen one in the list, full applies all triggers for a certain category', 
    choices=['single', 'cumulative', 'full'])
args = argParser.parse_args()

#
# Change some settings if this is a test
#
if args.isTest: 
    args.isChild = True
    args.sample = 'HNL-tau-m40'
    args.subJob = '0'
    args.year = '2016'


#
# Load in the sample list 
#
from HNL.Samples.sampleManager import SampleManager
sample_manager = SampleManager(args.year, 'noskim', 'triggerlist_'+str(args.year))

#
# Submit subjobs
#
if not args.isChild:
    from HNL.Tools.jobSubmitter import submitJobs
    jobs = []
    for sample_name in sample_manager.sample_names:
        sample = sample_manager.getSample(sample_name)
        for njob in xrange(sample.split_jobs): 
            jobs += [(sample.name, str(njob))]

    submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'trigger')
    exit(0)


#
# Load in sample and chain
#
sample = sample_manager.getSample(args.sample)
chain = sample.initTree()
chain.year = int(args.year)
chain.is_signal = 'HNL' in sample.name
chain.HNLmass = sample.getMass()

#
# Does an event pass the triggers
#
from HNL.Triggers.triggerSelection import passTriggers

#
# Get the name for the output file for the different efficiencies
#
from HNL.Tools.helpers import makeDirIfNeeded
def getOutputName(var, istest=False):

    subjobAppendix = 'subJob' + args.subJob if args.subJob else ''

    if var == 'HNLmass':
        if args.isTest:
            output_name = os.path.join(os.getcwd(), 'data', 'testArea', __file__.split('.')[0], 'HNLmass')
        else:
            output_name = os.path.join(os.getcwd(), 'data', __file__.split('.')[0], 'HNLmass')
        if args.separateTriggers is not None:
            output_name += '/'+args.separateTriggers
        if args.isChild:
            output_name += '/tmp_HNLmass'
        if args.useRef:        output_name += '/'+ sample.name +'_TrigEff_' +subjobAppendix+ '.root'
        else:   output_name += '/'+ sample.name +'_TrigEffnoMET_' +subjobAppendix+ '.root'

    else:
        if args.isTest:
            output_name = os.path.join(os.getcwd(), 'data', 'testArea', __file__.split('.')[0], sample.output)
        else:
            output_name = os.path.join(os.getcwd(), 'data', __file__.split('.')[0], sample.output)

        if args.separateTriggers is not None:
            output_name += '/'+args.separateTriggers
        if args.isChild:
            output_name += '/tmp_'+sample.output
        
        if args.useRef:        output_name += '/'+ sample.name +'_TrigEff_' +subjobAppendix+ '.root'
        else:   output_name += '/'+ sample.name +'_TrigEffnoMET_' +subjobAppendix+ '.root'

    return output_name 

#
# Define histograms
# Could these lists could have been done in a nicer way but since the wanted lepton is different for different var, I was too lazy for now. Redo later if needed
#                (channel, dim) 
from HNL.EventSelection.eventCategorization import EventCategory
ec = EventCategory(chain)
categories = ec.categories
category_triggers = lambda chain, category : returnCategoryTriggers(chain, category)

#First if keeps old code for reference
# if args.ignoreCategories:
#     category_map = {('eee', '1D') : ['integral'], 
#                     ('eee', '2D') : ['integral'], 
#                     ('eemu', '1D') : ('15to30', '30to55'),
#                     ('eemu', '2D') : ('15to20', '20to25', '25to30', '30to40', '40to50', '55to100'),
#                     ('emumu', '1D') : ('15to30', '30to55'),
#                     ('emumu', '2D') : ('15to20', '20to25', '25to30', '30to40', '40to50', '55to100'),
#                     ('mumumu', '1D') : ['integral'],
#                     ('mumumu', '2D') : ['integral']}

#     var = {('pt', '1D') : (lambda c : c._lPt[c.l3],                                 np.arange(5., 40., 5.),                 ('p_{T}(trailing) [GeV]', 'Events')),
#            ('eta', '1D') : (lambda c : abs(c._lEta[c.l1]),                          np.arange(0., 3., .5),                  ('|#eta|(leading) [GeV]', 'Events')),
#            ('pt', '2D') : (lambda c : (c._lPt[c.l3], c._lPt[c.l2]),                     (np.arange(5., 40., 5.), np.arange(5., 40., 5.)), ('p_{T}(trailing) [GeV]', 'p_{T}(subleading) [GeV]')),
#            ('eta', '2D') : (lambda c : (abs(c._lEta[c.l3]), abs(c._lEta[c.l2])),      (np.arange(0., 3., .5), np.arange(0., 3., .5)), ('|#eta|(trailing) [GeV]', '|#eta|(subleading) [GeV]'))}

# Use categorization as defined in eventCategorization.py

from HNL.Tools.helpers import getMassRange

mass_range = getMassRange(sample_manager.sample_names)

category_map = {}
for c in categories:
    # category_map[c] = ['integral', '15to30', '30to55', '15to20', '20to25', '25to30', '30to40', '40to50', '55to100']   
    category_map[c] = ['integral']   
    # category_map[c] = ('15to30', '30to55') 
    # category_map[c] = ('15to20', '20to25', '25to30', '30to40', '40to50', '55to100') 

var = {'l1pt' : (lambda c : c.l_pt[0],                          np.arange(0., 100., 15.),                 ('p_{T}(l1) [GeV]', 'Efficiency')),
        'l2pt' : (lambda c : c.l_pt[1],                          np.arange(0., 100., 15.),                  ('p_{T}(l2) [GeV]', 'Efficiency')),
        'l3pt' : (lambda c : c.l_pt[2],                          np.arange(0., 100., 15.),                  ('p_{T}(l3) [GeV]', 'Efficiency')),
        'l1eta' : (lambda c : abs(c.l_eta[0]),                          np.arange(0., 3., .5),                  ('|#eta|(l1) [GeV]', 'Efficiency')),
        'l2eta' : (lambda c : abs(c.l_eta[1]),                          np.arange(0., 3., .5),                  ('|#eta|(l2) [GeV]', 'Efficiency')),
        'l3eta' : (lambda c : abs(c.l_eta[2]),                          np.arange(0., 3., .5),                  ('|#eta|(l3) [GeV]', 'Efficiency')),
        'l1-2D' : (lambda c : (c.l_pt[0], abs(c.l_eta[0])),      (np.arange(0., 100., 15.), np.arange(0., 3., .5)), ('p_{T}(l1) [GeV]', '|#eta|(l1)')),
        'l2-2D' : (lambda c : (c.l_pt[1], abs(c.l_eta[1])),      (np.arange(0., 100., 15.), np.arange(0., 3., .5)), ('p_{T}(l2) [GeV]', '|#eta|(subleading)')),
        'l3-2D' : (lambda c : (c.l_pt[2], abs(c.l_eta[2])),      (np.arange(0., 100., 15.), np.arange(0., 3., .5)), ('p_{T}(l3) [GeV]', '|#eta|(subleading)'))}

if chain.is_signal:
    var['HNLmass'] = (lambda c : c.HNLmass,        np.array(mass_range),   ('m_{N} [GeV]', 'Efficiency'))

from HNL.Tools.efficiency import Efficiency
from HNL.EventSelection.eventCategorization import returnCategoryTriggers
from HNL.Triggers.triggerSelection import applyCustomTriggers
eff = {}
for c in categories:
    for v in {k for k in var.keys()}:
        for t in category_map[c]:
            if args.separateTriggers is None or args.separateTriggers == 'full':
                name = str(c)+ '_' +v + '_' + t
                if v != 'HNLmass':
                    eff[(c, v, t)] = Efficiency(name, var[v][0], var[v][2], getOutputName(v), var[v][1])
                else:
                    eff[(c, v, t)] = Efficiency(name, var[v][0], var[v][2], getOutputName(v), var[v][1])
                makeDirIfNeeded(getOutputName(v))
            else:
                for i, trigger in enumerate(category_triggers(chain, c)):
                    name = str(c)+ '_' +v + '_' + t +'_'+str(i)
                    if v != 'HNLmass':
                        eff[(c, v, t, i)] = Efficiency(name, var[v][0], var[v][2], getOutputName(v), var[v][1])
                    else:
                        eff[(c, v, t, i)] = Efficiency(name, var[v][0], var[v][2], getOutputName(v), var[v][1])
                    makeDirIfNeeded(getOutputName(v))
                
#
# Set event range
#
if args.isTest:
    event_range = xrange(2000)
    # event_range = sample.getEventRange(args.subJob)    

else:
    event_range = sample.getEventRange(args.subJob)    

#
# Loop over all events
#
from HNL.Tools.helpers import progress
from HNL.EventSelection.eventSelectionTools import select3Leptons
for entry in event_range:
    
    chain.GetEntry(entry)
    progress(entry - event_range[0], len(event_range))

    if not select3Leptons(chain, chain, tau_algo = 'gen_truth'): continue
    if args.useRef and not chain._passTrigger_ref:     continue

    weightfactor = 1.
    if not sample.is_data: weightfactor *= chain._weight

    if args.separateTriggers is None:    
        passed = passTriggers(chain, chain.year, oldAN=args.oldTriggers) 
    
    true_cat = ec.returnCategory()

    for c in categories:
        for v in {k for k in var.keys()}: 
            for t in category_map[c]:
                
                # if not true_cat == c: continue

                if t != 'integral': 
                    lowpt, highpt = t.split('to')
                    if chain.l1_pt < float(lowpt) or chain.l1_pt > float(highpt): continue
                                
                if args.separateTriggers is None:
                    eff[(c, v, t)].fill(chain, weightfactor, passed)
                else:
                    if args.separateTriggers == 'full':
                        passed = applyCustomTriggers(category_triggers(chain, c))
                        eff[(c, v, t)].fill(chain, weightfactor, passed)
                    else:
                        for i, trigger in enumerate(category_triggers(chain, c)):
                            if args.separateTriggers == 'single':
                                passed = applyCustomTriggers(trigger)
                                eff[(c, v, t, i)].fill(chain, weightfactor, passed)
                            elif args.separateTriggers == 'cumulative':
                                passed = applyCustomTriggers(category_triggers(chain, c)[:i+1])
                                eff[(c, v, t, i)].fill(chain, weightfactor, passed)

                            
#
# Save all histograms
#
from HNL.EventSelection.eventCategorization import returnCategoryTriggerNames
for i, c in enumerate(categories):
    for l, v in enumerate({k for k in var.keys()}): 
        for t in category_map[c]:
            if args.separateTriggers is None:
                if i == 0 and l == 0:      eff[(c, v, t)].write(subdirs=['efficiency', v, 'allTriggers'])
                else:           eff[(c, v, t)].write(append=True, subdirs=['efficiency', v, 'allTriggers'])
            elif args.separateTriggers == 'full':
                if i == 0 and l == 0:      eff[(c, v, t)].write(subdirs=['efficiency_'+str(c), v, 'allTriggers'])
                else:           eff[(c, v, t)].write(append=True, subdirs=['efficiency_'+str(c), v, 'allTriggers'])               
            else:
                for j, trigger in enumerate(category_triggers(chain, c)):
                    if i == 0 and l == 0 and j == 0:       eff[(c, v, t, j)].write(subdirs=['efficiency_'+str(c), v, str(returnCategoryTriggerNames(c)[j])])
                    else:                       eff[(c, v, t, j)].write(append=True, subdirs=['efficiency_'+str(c), v, str(returnCategoryTriggerNames(c)[j])])

