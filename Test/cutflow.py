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

if args.isTest:
    args.year = '2016'
    args.sample = 'DYJetsToLL-M-10to50' 

import HNL.EventSelection.eventCategorization as cat

list_of_numbers = {'total' : 0,
                    'single_lep' : 0,
                    'reco_tau' : 0,
                    'reco_tau_good' : 0,
                    'two_reco_tau' : 0,
                    'two_good_reco_tau' : 0,
                    'final' : 0, 
                    'cat_n' : 0} 
#
# Loop over samples and events
#
#
# Load in the sample list 
#
from HNL.Samples.sample import createSampleList, getSampleFromList
list_location = os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/sampleList_'+str(args.year)+'_noskim.conf')
sample_list = createSampleList(list_location)
sample = getSampleFromList(sample_list, args.sample)

#
# Load in sample and chain
#
chain = sample.initTree(needhcount=False)

is_signal = 'HNL' in sample.name

#
# Set event range
#
if args.isTest:
    if len(sample.getEventRange(0)) < 50:
        event_range = sample.getEventRange(0)
    else:
        event_range = xrange(50)
else:
    event_range = xrange(chain.GetEntries())

chain.HNLmass = float(sample.name.rsplit('-', 1)[1]) if is_signal else None
chain.year = int(args.year)
#
# Loop over all events
#
from HNL.Tools.helpers import progress, makeDirIfNeeded
from HNL.EventSelection.signalLeptonMatcher import SignalLeptonMatcher
from HNL.EventSelection.eventSelection import select3Leptons, select3GenLeptons, calculateKinematicVariables
from HNL.EventSelection.eventCategorization import EventCategory
from HNL.ObjectSelection.tauSelector import isLooseTau, isTightTau
from HNL.ObjectSelection.leptonSelector import isTightLepton

ec = EventCategory(chain)
for entry in event_range:
    
    chain.GetEntry(entry)
    progress(entry - event_range[0], len(event_range))

    #if not select3GenLeptons(chain, chain): continue

    #chain.event_supercategory = ec.returnSuperCategory()
    #if chain.event_supercategory > 2: continue

    #Add here any additional cuts
    list_of_numbers['total'] += 1
    
    chain.leptons = [l for l in xrange(chain._nLight) if isTightLepton(chain, l, algo = 'leptonMVAtZq')]
    if len(chain.leptons) == 0:  continue
    list_of_numbers['single_lep'] += 1

    if chain._nTau == 0: continue 
    list_of_numbers['reco_tau'] += 1
   
    chain.leptons = [l for l in xrange(chain._nLight, chain._nL) if isTightTau(chain, l)] 
    if len(chain.leptons) == 0:  continue
    list_of_numbers['reco_tau_good'] += 1
    
    if chain._nTau < 2: continue 
    list_of_numbers['two_reco_tau'] += 1
   
    if len(chain.leptons) < 2:  continue
    list_of_numbers['two_good_reco_tau'] += 1

    if not select3Leptons(chain, chain): 
        continue
    list_of_numbers['final'] += 1

    chain.event_supercategory = ec.returnSuperCategory()
    if chain.event_supercategory > 1: continue
    list_of_numbers['cat_n'] += 1

print 'total', list_of_numbers['total']
print 'single_lep', list_of_numbers['single_lep']
print 'reco_tau', list_of_numbers['reco_tau']
print 'reco_tau_good', list_of_numbers['reco_tau_good']
print 'two_reco_tau', list_of_numbers['two_reco_tau']
print 'two_good_reco_tau', list_of_numbers['two_good_reco_tau']
print 'final', list_of_numbers['final']
print 'cat_n', list_of_numbers['cat_n']
