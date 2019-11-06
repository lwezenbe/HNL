import ROOT
import os

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
args = argParser.parse_args()

#Load in samples
from HNL.Samples.sample import createSampleList, getSampleFromList
    sampleList = createSampleList('../Samples/InputFiles/'+args.year+'_sampleList.conf')

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

#Get specific sample for this subjob
sample = getSampleFromList(sampleList, args.sample)
chain = sample.initTree()
chain.year = args.year

# Create new reduced tree (except if it already exists and overwrite option is not used)
from HNL.Tools.helpers import isValidRootFile
output_name = os.path.join('/user/$USER/public/ntuples', str(args.year), sample.output, sample.name + '_' + str(args.subJob) + '.root')

try:    os.makedirs(os.path.dirname(outputName))
except: pass

if not args.overwrite and isValidRootFile(outputName):
  log.info('Finished: valid outputfile already exists')
  exit(0)

outputFile = ROOT.TFile(outputName ,"RECREATE")
outputFile.mkdir('blackJackAndHookers')
outputFile.cd('blackJackAndHookers')

#
# Switch off unused branches and create outputTree
#

delete_branches = []
for i in delete_branches:        chain.SetBranchStatus("*"+i+"*", 0)
output_tree = chain.CloneTree(0)

#
# Make new branches
#
new_branches = ['test/I']

from HNL.Tools.makeBranches import makeBranches
newVars = makeBranches(output_tree, new_branches)



