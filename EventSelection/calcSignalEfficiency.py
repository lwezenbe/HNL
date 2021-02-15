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
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018'])
submission_parser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
submission_parser.add_argument('--strategy',   action='store', default='cutbased',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA'])
submission_parser.add_argument('--region', action='store', default='baseline', type=str,  help='What region do you want to select for?', 
    choices=['baseline', 'lowMassSR', 'highMassSR'])
submission_parser.add_argument('--FOcut',   action='store_true', default=False,  help='Perform baseline FO cut')
submission_parser.add_argument('--divideByCategory',   action='store_true', default=False,  help='Look at the efficiency per event category')
submission_parser.add_argument('--genLevel',   action='store_true', default=False,  help='Check how many events pass cuts on gen level')
submission_parser.add_argument('--compareTriggerCuts', action='store', default=None,  
    help='Look at each trigger separately for each category. Single means just one trigger, cumulative uses cumulative OR of all triggers that come before the chosen one in the list, full applies all triggers for a certain category', 
    choices=['single', 'cumulative', 'full'])
submission_parser.add_argument('--flavor', action='store', default=None,  help='Which coupling should be active?' , choices=['tau', 'e', 'mu', '2l'])
submission_parser.add_argument('--logLevel',  action='store',      default='INFO',               help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])

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
        for njob in xrange(sample.returnSplitJobs()): 
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
    output_name = os.path.join(os.path.expandvars('$CMSSW_BASE'),'src', 'HNL', 'EventSelection', 'data', __file__.split('.')[0].rsplit('/')[-1], category_split_str, trigger_str, args.region, flavor_name, sample.output)
else:
    output_name = os.path.join(os.path.expandvars('$CMSSW_BASE'),'src', 'HNL', 'EventSelection', 'data', 'testArea', __file__.split('.')[0].rsplit('/')[-1], category_split_str, trigger_str, args.region, flavor_name, sample.output)


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
        efficiency[k]['regularRun'] = Efficiency('efficiency_'+str(k), var['HNLmass'][0], var['HNLmass'][2], output_name, bins=var['HNLmass'][1], subdirs=['efficiency_'+str(k), 'l1_'+str('r')+'_l2_'+str('e')+'_l3_'+str('g')])
elif args.compareTriggerCuts == 'full':
    if not args.divideByCategory:
        print "Inconsistent input: This mode is to be used together with divideByCategory. Exiting"
        exit(0)
    for k in efficiency.keys():
        efficiency[k]['full'] = Efficiency('efficiency_'+str(k), var['HNLmass'][0], var['HNLmass'][2], output_name, bins=var['HNLmass'][1], subdirs=['efficiency_'+str(k), 'l1_'+str('f')+'_l2_'+str('u')+'_l3_'+str('l')])
else: #'single' or 'cumulative'
    if not args.divideByCategory:
        print "Inconsistent input: This mode is to be used together with divideByCategory. Exiting"
        exit(0)
    for c in ec.categories:
        for ptcuts in returnCategoryPtCuts(c):
            efficiency[c][ptcuts] = Efficiency('efficiency_'+str(c)+'_l1_'+str(ptcuts[0])+'_l2_'+str(ptcuts[1])+'_l3_'+str(ptcuts[2]), 
                var['HNLmass'][0], var['HNLmass'][2], output_name, bins=var['HNLmass'][1], subdirs=['efficiency_'+str(c), 'l1_'+str(ptcuts[0])+'_l2_'+str(ptcuts[1])+'_l3_'+str(ptcuts[2])])

#
# Set event range
#
if args.isTest:
    max_events = 20000
    event_range = xrange(max_events) if max_events < len(sample.getEventRange(args.subJob)) else sample.getEventRange(args.subJob)
else:
    event_range = sample.getEventRange(args.subJob)    

chain.HNLmass = sample.getMass()
chain.year = int(args.year)
chain.selection = args.selection
chain.strategy = args.strategy

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
from HNL.ObjectSelection.leptonSelector import isGoodLepton

def passedPtCutsByCategory(in_chain, cat):
    cuts_collection = returnCategoryPtCuts(cat)
    passes_cuts = [passedCustomPtCuts(in_chain, cut) for cut in cuts_collection]
    return any(passes_cuts)

#
# Object Selection
#
from HNL.ObjectSelection.objectSelection import getObjectSelection
chain.obj_sel = getObjectSelection(args.selection)

from HNL.EventSelection.eventSelector import EventSelector
es = EventSelector(args.region, chain, chain, True, ec)    

for entry in event_range:
    
    chain.GetEntry(entry)
    progress(entry - event_range[0], len(event_range))
    
    if not selectGenLeptonsGeneral(chain, chain, 3):   continue
    
    if args.genLevel:
        slm = SignalLeptonMatcher(chain)
        slm.saveNewOrder()

    true_cat = ec.returnCategory()

    if args.FOcut:
        tmp = [l for l in xrange(chain._nL) if isGoodLepton(chain, l, 'FO')]
        if len(tmp) < 3: continue   
   
    if not args.genLevel:
        passed = es.passedFilter(cutter)
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
        if i == 0 and j == 0:       efficiency[c_key][t_key].write(is_test=args.isTest)
        else:                       efficiency[c_key][t_key].write(append=True, is_test=args.isTest)
        

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
