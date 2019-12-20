#
# Code to perform a skim on samples
#

import ROOT
import os

lumi = {2016 : 35546}

#
# Argument parser and logging
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
argParser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018'])
argParser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
argParser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
argParser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
argParser.add_argument('--runLocal', action='store_true', default=False,  help='use local resources instead of Cream02')
argParser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
argParser.add_argument('--overwrite', action='store_true', default=False,                help='overwrite if valid output file already exists')
argParser.add_argument('--logLevel',  action='store',      default='INFO',               help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])
argParser.add_argument('--genSkim',  action='store_true',      default=False,               help='skim on generator level leptons')

args = argParser.parse_args()

from HNL.Tools.logger import getLogger
log = getLogger(args.logLevel)

#
# Set some args for when performing a test
#
if args.isTest:
    args.sample = 'localSubmission_HNL_5'
    args.year = '2016'
    args.subJob = 0
    args.isChild = True

#
#Load in samples
#
from HNL.Samples.sample import createSampleList, getSampleFromList
sample_list = createSampleList('../Samples/InputFiles/skimList_'+args.year+'_sampleList.conf')
#sample_list = createSampleList('../Samples/InputFiles/signallist_'+args.year+'.conf')

#
# Submit subjobs
#
if not args.isChild and not args.isTest:
    from HNL.Tools.jobSubmitter import submitJobs
    jobs = []
    for sample in sample_list:
        for njob in xrange(sample.split_jobs):
            jobs += [(sample.name, str(njob))]

    submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'trigger_'+sample.name)
    exit(0)

#
#Get specific sample for this subjob
#
sample = getSampleFromList(sample_list, args.sample)
chain = sample.initTree()
chain.year = int(args.year)
chain.is_signal = 'HNL' in sample.name

#
# Create new reduced tree (except if it already exists and overwrite option is not used)
#
from HNL.Tools.helpers import isValidRootFile, makeDirIfNeeded
gen_name = 'Reco' if not args.genSkim else 'Gen'
output_name = os.path.expandvars(os.path.join('/user/$USER/public/ntuples/HNL', str(args.year), gen_name, 'tmp_'+sample.output, sample.name + '_' + str(args.subJob) + '.root'))
makeDirIfNeeded(output_name)

if not args.overwrite and isValidRootFile(output_name):
    log.info('Finished: valid outputfile already exists')
    exit(0)

output_file = ROOT.TFile(output_name ,"RECREATE")
output_file.mkdir('blackJackAndHookers')
output_file.cd('blackJackAndHookers')

#
# Get hCounter
#
hcounter = None
try:    hcounter = sample.hcounter
except: pass

#
# Switch off unused branches and create outputTree
#

#delete_branches = ['lhe', 'Lhe', 'ttg', '_ph']
delete_branches = ['ttg', '_ph']
delete_branches.extend(['HLT']) #TODO: For now using pass_trigger, this may need to change
delete_branches.extend(['tauPOG*2015', 'tau*MvaNew']) #Outdated tau
delete_branches.extend(['lMuon', 'Smeared', 'prefire'])
#delete_branches.extend(['_met'])
delete_branches.extend(['jetNeutral', 'jetCharged', 'jetHF'])
for i in delete_branches:        chain.SetBranchStatus("*"+i+"*", 0)
#chain.SetBranchStatus('_met', 1)  #Reactivate met
#chain.SetBranchStatus('_metPhi', 1)  #Reactivate met
output_tree = chain.CloneTree(0)

#
# Make new branches
#
new_branches = []
new_branches.extend(['M3l/F', 'minMos/F', 'pt_cone[20]/F', 'mtOther/F'])
new_branches.extend(['l1/I', 'l2/I', 'l3/I', 'index_other/I'])
new_branches.extend(['l1_pt/F', 'l2_pt/F', 'l3_pt/F'])
new_branches.extend(['l1_e/F', 'l2_e/F', 'l3_e/F'])
new_branches.extend(['l1_eta/F', 'l2_eta/F', 'l3_eta/F'])
new_branches.extend(['l1_phi/F', 'l2_phi/F', 'l3_phi/F'])
new_branches.extend(['l1_charge/F', 'l2_charge/F', 'l3_charge/F'])
new_branches.extend(['lumiweight/F'])

from HNL.Tools.makeBranches import makeBranches
new_vars = makeBranches(output_tree, new_branches)

#
# Start event loop
#
if args.isTest:
    event_range = range(500)
else:
    event_range = sample.getEventRange(args.subJob)    

from HNL.Tools.helpers import progress
from HNL.EventSelection.eventSelection import calculateKinematicVariables, select3Leptons, select3GenLeptons
for entry in event_range:
    chain.GetEntry(entry)
    progress(entry - event_range[0], len(event_range))
   
    if args.genSkim:
        if not select3GenLeptons(chain, new_vars):      continue
    else:
        if not select3Leptons(chain, new_vars):       continue

    calculateKinematicVariables(chain, new_vars, is_reco_level=not args.genSkim)
    new_vars.lumiweight = chain._weight*(sample.xsec*lumi[chain.year])/sample.hcount
    output_tree.Fill()

output_tree.AutoSave()
if hcounter is not None:
    hcounter.Write()
    
output_file.Close()
