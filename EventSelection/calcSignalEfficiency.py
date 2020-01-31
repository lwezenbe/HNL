#! /usr/bin/env python

#
#       Code to calculate trigger efficiency
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
argParser.add_argument('--oldANcuts',   action='store_true', default=False,  help='do not launch subjobs, only show them')
argParser.add_argument('--FOcut',   action='store_true', default=False,  help='Perform baseline FO cut')
argParser.add_argument('--onlyHadronic',   action='store_true', default=False,  help='Only allow hadronic final states')
argParser.add_argument('--divideByCategory',   action='store_true', default=False,  help='Look at the efficiency per event category')
argParser.add_argument('--genLevel',   action='store_true', default=False,  help='Check how many events pass cuts on gen level')
argParser.add_argument('--triggerTest',   action='store_true', default=False,  help='Check pt cuts separately instead of or-ing them')
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
output_name = os.path.join(os.getcwd(), 'data', __file__.split('.')[0], sample.output)
if args.divideByCategory:
    output_name += '/divideByCategory'
    if args.triggerTest: 
        output_name += '/triggerTest'

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

from HNL.EventSelection.eventCategorization import EventCategory, categoryName, subcategoryName
ec = EventCategory(chain)

from HNL.Tools.efficiency import Efficiency
from HNL.EventSelection.eventCategorization import returnCategoryPtCuts
if not args.divideByCategory:
    efficiency = Efficiency('efficiency', var['HNLmass'][0], var['HNLmass'][2], output_name, var['HNLmass'][1])
else:
    efficiency = {}
    if not args.triggerTest:
        for cat in ec.categories:
            efficiency[cat] = Efficiency('efficiency_'+str(cat[0])+'_'+str(cat[1]), var['HNLmass'][0], var['HNLmass'][2], output_name, var['HNLmass'][1])        
    else:
        for cat in ec.categories:
            efficiency[cat] = {}
            for dink in returnCategoryPtCuts(cat):
                efficiency[cat][dink] = Efficiency('efficiency_'+str(cat[0])+'_'+str(cat[1])+'_l1_'+str(dink[0])+'_l2_'+str(dink[1])+'_l3_'+str(dink[2]), var['HNLmass'][0], var['HNLmass'][2], output_name, var['HNLmass'][1])        

print efficiency

#
# Set event range
#
if args.isTest:
    event_range = xrange(1000)
else:
    event_range = sample.getEventRange(args.subJob)    

chain.HNLmass = float(sample.name.rsplit('-', 1)[1])
chain.year = int(args.year)

#
# Loop over all events
#
from HNL.Tools.helpers import progress
from HNL.EventSelection.eventSelection import select3Leptons, select3LightLeptons, select3GenLeptons, lowMassCuts, passedPtCutsByCategory, passedCustomPtCuts
from HNL.EventSelection.signalLeptonMatcher import SignalLeptonMatcher
from HNL.ObjectSelection.leptonSelector import isFOLepton
for entry in event_range:
    
    chain.GetEntry(entry)
    progress(entry - event_range[0], len(event_range))

    if not select3GenLeptons(chain, chain):   continue
    if args.genLevel:
        slm = SignalLeptonMatcher(chain)
        slm.saveNewOrder()

    true_cat = ec.returnCategory()

    if args.FOcut:
        tmp = [l for l in xrange(chain._nL) if isFOLepton(chain, l)]
        if len(tmp) < 3: continue   
    
    if args.oldANcuts:
        passed = select3LightLeptons(chain, chain)
    elif not args.genLevel:
        passed = select3Leptons(chain, chain)
    elif args.triggerTest:
        passed = False
    else:
        #implement custom cuts here
        passed = passedPtCutsByCategory(chain, true_cat)

    #if args.onlyHadronic and ec.returnCategory()[0] > 3: passed = False

#    if not lowMassCuts:         continue
    weight = chain._weight
    if args.divideByCategory:
        if not args.genLevel and true_cat != ec.returnCategory(): passed = False
        if args.triggerTest:
            for cuts in efficiency[true_cat].keys():
                passed = passedCustomPtCuts(chain, cuts)
                efficiency[true_cat][cuts].fill(chain, weight, passed)   
        else:
            efficiency[true_cat].fill(chain, weight, passed)   
                
    else:
        efficiency.fill(chain, weight, passed)   
        

#if args.isTest: exit(0)

#
# Save all histograms
#
if args.divideByCategory:
    for i, cat in enumerate(ec.categories):
        if not args.triggerTest:
            if i == 0:       efficiency[cat].write()
            else:            efficiency[cat].write(append=True)
        else: 
            for j, cuts in enumerate(efficiency[cat].keys()):
                if i == 0 and j == 0:       efficiency[cat][cuts].write(subdirs=['efficiency_'+str(cat[0])+'_'+str(cat[1]), 'l1_'+str(cuts[0])+'_l2_'+str(cuts[1])+'_l3_'+str(cuts[2])])
                else:                       efficiency[cat][cuts].write(append=True, subdirs=['efficiency_'+str(cat[0])+'_'+str(cat[1]), 'l1_'+str(cuts[0])+'_l2_'+str(cuts[1])+'_l3_'+str(cuts[2])])
else:
    efficiency.write()
