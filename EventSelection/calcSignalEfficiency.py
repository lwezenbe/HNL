#! /usr/bin/env python

#
#       Code to calculate signal efficiency
#
# Can be used on RECO level, where you check how many events pass the reco selection
# Is also used to check how many events on a generator level pass certain pt cuts
#

#TODO: This code still uses the old categorization, this needs to be updated as well here

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
argParser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
argParser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
argParser.add_argument('--selection', action='store', default='cut-based', type=str,  help='What type of analysis do you want to run?', choices=['cut-based', 'AN2017014', 'MVA'])
argParser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?', 
    choices=['baseline', 'lowMassSR', 'highMassSR'])
argParser.add_argument('--FOcut',   action='store_true', default=False,  help='Perform baseline FO cut')
argParser.add_argument('--divideByCategory',   action='store_true', default=False,  help='Look at the efficiency per event category')
argParser.add_argument('--genLevel',   action='store_true', default=False,  help='Check how many events pass cuts on gen level')
argParser.add_argument('--compareTriggerCuts', action='store', default=None,  
    help='Look at each trigger separately for each category. Single means just one trigger, cumulative uses cumulative OR of all triggers that come before the chosen one in the list, full applies all triggers for a certain category', 
    choices=['single', 'cumulative', 'full'])
argParser.add_argument('--flavor', action='store', default=None,  help='Which coupling should be active?' , choices=['tau', 'e', 'mu', '2l'])
argParser.add_argument('--logLevel',  action='store',      default='INFO',               help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])


args = argParser.parse_args()

from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)

#
# Change some settings if this is a test
#
if args.isTest: 
    args.isChild = True
    args.sample = 'HNL-tau-m200'
    args.subJob = '0'
    args.year = '2016'
    args.flavor = 'tau'


#
# Load in the sample list 
#
from HNL.Samples.sampleManager import SampleManager
sample_manager = SampleManager(args.year, 'noskim', 'signallist_'+str(args.year))


jobs = []
flavors = ['tau', 'e', 'mu', '2l'] if args.flavor is None else [args.flavor]
for sample_name in sample_manager.sample_names:
    for flavor in flavors:
        if not '-'+flavor+'-' in sample_name: continue
        sample = sample_manager.getSample(sample_name)
        for njob in xrange(sample.split_jobs): 
            jobs += [(sample.name, str(njob), flavor)]


#
# Submit subjobs
#
if not args.isChild:
    from HNL.Tools.jobSubmitter import submitJobs
    submitJobs(__file__, ('sample', 'subJob', 'flavor'), jobs, argParser, jobLabel = 'calcSignalEfficiency')
    exit(0)


#
# Load in sample and chain
#
sample = sample_manager.getSample(args.sample)
chain = sample.initTree()

subjobAppendix = 'subJob' + args.subJob if args.subJob else ''
category_split_str = 'allCategories' if not args.divideByCategory else 'divideByCategory'
trigger_str = args.compareTriggerCuts if args.compareTriggerCuts is not None else 'regularRun'
flavor_name = args.flavor if args.flavor else 'allFlavor'


if not args.isTest: 
    output_name = os.path.join(os.path.expandvars('$CMSSW_BASE'),'src', 'EventSelection', 'data', __file__.split('.')[0].rsplit('/')[-1], category_split_str, trigger_str, args.region, flavor_name, sample.output)
else:
    output_name = os.path.join(os.path.expandvars('$CMSSW_BASE'),'src', 'EventSelection', 'data', 'testArea', __file__.split('.')[0].rsplit('/')[-1], category_split_str, trigger_str, args.region, flavor_name, sample.output)


if args.isChild:
    output_name += '/tmp_'+sample.output

if not args.FOcut:
    output_name += '/'+ sample.name +'_signalSelectionFull_' +subjobAppendix+ '.root'
else:
    output_name += '/'+ sample.name +'_signalSelectionFObase_' +subjobAppendix+ '.root'

#
# Calculate the range for the histograms. These are as a function of the mass of the signal samples.
# This function looks at the names of all samples and returns an array with all values right the middle of those
# It assumes the samples are ordered by mass in the input list
#
from HNL.Tools.helpers import getMassRange
print [sample_name for sample_name in sample_manager.sample_names if '-'+args.flavor+'-' in sample_name]
mass_range = getMassRange([sample_name for sample_name in sample_manager.sample_names if '-'+args.flavor+'-' in sample_name])

#
# Define the variables and axis name of the variable to fill and create efficiency objects
#
var = {'HNLmass': (lambda c : c.HNLmass,        np.array(mass_range),   ('m_{N} [GeV]', 'Events'))}

from HNL.EventSelection.eventCategorization import EventCategory
ec = EventCategory(chain)

from HNL.Tools.efficiency import Efficiency
from HNL.EventSelection.eventCategorization import returnCategoryPtCuts

efficiency = {}

if not args.divideByCategory:
    efficiency['noCategories'] = {}
else:
    for c in ec.categories:
        efficiency[c] = {}

if args.compareTriggerCuts is None:
    for k in efficiency.keys():
        efficiency[k]['regularRun'] = Efficiency('efficiency_'+str(k), var['HNLmass'][0], var['HNLmass'][2], output_name, bins=var['HNLmass'][1])
elif args.compareTriggerCuts == 'full':
    if not args.divideByCategory:
        print "Inconsistent input: This mode is to be used together with divideByCategory. Exiting"
        exit(0)
    for k in efficiency.keys():
        efficiency[k]['full'] = Efficiency('efficiency_'+str(k), var['HNLmass'][0], var['HNLmass'][2], output_name, bins=var['HNLmass'][1])
else: #'single' or 'cumulative'
    if not args.divideByCategory:
        print "Inconsistent input: This mode is to be used together with divideByCategory. Exiting"
        exit(0)
    for c in ec.categories:
        for ptcuts in returnCategoryPtCuts(c):
            efficiency[c][ptcuts] = Efficiency('efficiency_'+str(c)+'_l1_'+str(ptcuts[0])+'_l2_'+str(ptcuts[1])+'_l3_'+str(ptcuts[2]), 
                var['HNLmass'][0], var['HNLmass'][2], output_name, bins=var['HNLmass'][1])

#
# Set event range
#
if args.isTest:
    event_range = xrange(2000)
else:
    event_range = sample.getEventRange(args.subJob)    

chain.HNLmass = sample.getMass()
chain.year = int(args.year)

#
# Get luminosity weight
#
from HNL.Weights.lumiweight import LumiWeight
lw = LumiWeight(sample, sample_manager)

#
# Import and create cutter to provide cut flow
#
from HNL.EventSelection.cutter import Cutter
cutter = Cutter(chain = chain)

#
# Loop over all events
#
from HNL.Tools.helpers import progress
from HNL.EventSelection.eventSelectionTools import select3Leptons, selectGenLeptonsGeneral, lowMassCuts, highMassCuts, passedCustomPtCuts, passBaseCuts
from HNL.EventSelection.signalLeptonMatcher import SignalLeptonMatcher
from HNL.ObjectSelection.leptonSelector import isFOLepton

def passedPtCutsByCategory(in_chain, cat):
    cuts_collection = returnCategoryPtCuts(cat)
    passes_cuts = [passedCustomPtCuts(in_chain, cut) for cut in cuts_collection]
    return any(passes_cuts)

#
# Object Selection
#
from HNL.ObjectSelection.objectSelection import objectSelectionCollection
if args.selection == 'AN2017014':
    object_selection = objectSelectionCollection('deeptauVSjets', 'cutbased', 'tight', 'tight', 'tight', True)
else:
    object_selection = objectSelectionCollection('deeptauVSjets', 'leptonMVAtop', 'tight', 'tight', 'tight', False)

from HNL.EventSelection.eventSelector import EventSelector
es = EventSelector(args.region, args.selection, object_selection, True, ec)    

for entry in event_range:
    
    chain.GetEntry(entry)
    progress(entry - event_range[0], len(event_range))
    
    if not selectGenLeptonsGeneral(chain, chain, 3):   continue
    
    if args.genLevel:
        slm = SignalLeptonMatcher(chain)
        slm.saveNewOrder()

    true_cat = ec.returnCategory()

    if args.FOcut:
        tmp = [l for l in xrange(chain._nL) if isFOLepton(chain, l)]
        if len(tmp) < 3: continue   
   
    if not args.genLevel:
        passed = es.passedFilter(chain, chain, cutter)
    else:
        passed = True

    weight = lw.getLumiWeight()
    if args.divideByCategory:
        if not args.genLevel and true_cat != ec.returnCategory(): passed = False

        if args.compareTriggerCuts is None:
            efficiency[true_cat]['regularRun'].fill(chain, weight, passed)   
        elif args.compareTriggerCuts == 'single':
            for cuts in efficiency[true_cat].keys():
                passed = passedCustomPtCuts(chain, cuts)
                efficiency[true_cat][cuts].fill(chain, weight, passed)   
        elif args.compareTriggerCuts == 'cumulative':
            for i, cuts in enumerate(returnCategoryPtCuts(true_cat)):
                passed = passedCustomPtCuts(chain, returnCategoryPtCuts(true_cat)[:i+1])
                efficiency[true_cat][cuts].fill(chain, weight, passed) 
        elif args.compareTriggerCuts == 'full':
            passed = passedCustomPtCuts(chain, returnCategoryPtCuts(true_cat))
            efficiency[true_cat]['full'].fill(chain, weight, passed)                
    else:
        efficiency['noCategories']['regularRun'].fill(chain, weight, passed)   
        
#
# Save all histograms
#
for i, c_key in enumerate(efficiency.keys()):
    for j, t_key in enumerate(efficiency[c_key].keys()):
        if i == 0 and j == 0:       efficiency[c_key][t_key].write(subdirs=['efficiency_'+str(c_key), 'l1_'+str(t_key[0])+'_l2_'+str(t_key[1])+'_l3_'+str(t_key[2])])
        else:                       efficiency[c_key][t_key].write(append=True, subdirs=['efficiency_'+str(c_key), 'l1_'+str(t_key[0])+'_l2_'+str(t_key[1])+'_l3_'+str(t_key[2])])
        

closeLogger(log)

# if args.divideByCategory:
#     for i, c in enumerate(ec.categories):
#         if not args.triggerTest and not args.compareTriggerCuts:
#             if i == 0:       efficiency[cat].write()
#             else:            efficiency[cat].write(append=True)
#         else: 
#             for j, cuts in enumerate(efficiency[cat].keys()):
#                 if i == 0 and j == 0:       efficiency[cat][cuts].write(subdirs=['efficiency_'+str(cat[0])+'_'+str(cat[1]), 'l1_'+str(cuts[0])+'_l2_'+str(cuts[1])+'_l3_'+str(cuts[2])])
#                 else:                       efficiency[cat][cuts].write(append=True, subdirs=['efficiency_'+str(cat[0])+'_'+str(cat[1]), 'l1_'+str(cuts[0])+'_l2_'+str(cuts[1])+'_l3_'+str(cuts[2])])
# else:
#     efficiency.write()
