#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--year',     action='store',      default=None,   help='Select year')
argParser.add_argument('--era',     action='store',       default='prelegacy', choices = ['UL', 'prelegacy'],   help='Select era', required=True)
argParser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
argParser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
argParser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
args = argParser.parse_args()

if args.isTest:
    if args.year is None: args.year = '2016'
    if args.sample is None: args.sample = 'DYJetsToLL-M-10to50' 
    if args.subJob is None: args.subJob = 0

    from HNL.Tools.logger import getLogger, closeLogger
    log = getLogger('INFO')

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
list_location = os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/sampleList_'+args.era+args.year+'_noskim.conf')
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
    max_events = 20000
    event_range = xrange(max_events) if max_events < len(sample.getEventRange(args.subJob)) else sample.getEventRange(args.subJob)
else:
    event_range = xrange(chain.GetEntries())

chain.HNLmass = float(sample.name.rsplit('-', 1)[1]) if is_signal else None
chain.year = args.year
chain.era = args.era
#
# Loop over all events
#
from HNL.Tools.helpers import progress
from HNL.EventSelection.eventSelectionTools import select3Leptons
from HNL.EventSelection.eventCategorization import EventCategory
from HNL.ObjectSelection.tauSelector import isGoodTau
from HNL.ObjectSelection.leptonSelector import isGoodLepton

ec = EventCategory(chain)
for entry in event_range:
    
    chain.GetEntry(entry)
    progress(entry - event_range[0], len(event_range))

    #if not select3GenLeptons(chain, chain): continue

    #chain.event_supercategory = ec.returnSuperCategory()
    #if chain.event_supercategory > 2: continue

    #Add here any additional cuts
    list_of_numbers['total'] += 1
    
    chain.leptons = [l for l in xrange(chain._nLight) if isGoodLepton(chain, l, 'tight')]
    if len(chain.leptons) == 0:  continue
    list_of_numbers['single_lep'] += 1

    if chain._nTau == 0: continue 
    list_of_numbers['reco_tau'] += 1
   
    chain.leptons = [l for l in xrange(chain._nLight, chain._nL) if isGoodTau(chain, l, 'tight')] 
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

if args.isTest: closeLogger(log)