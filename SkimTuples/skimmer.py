import ROOT
import os

#Parse arguments
import argparse

argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--sampleName',          action='store',         default='DYJetsToLL_M-50',      help='Name of sample as specifiec in input file. Default is DYJetsToLL_M-50')
argParser.add_argument('--subJob',              action='store',         default=0,                      help='Index of subjob. Default is 0')
argParser.add_argument('--year',                action='store',         default='2016',                 help='Year of datataking (2016, 2017, 2018)')
argParser.add_argument('--isTest',              action='store_true',                                    help='Perform local run on limited number of events')
argParser.add_argument('--overwrite',           action='store_true',                                    help='Overwrite output files if already present')

args = argParser.parse_args()

print 'Loading in samples'

#Load in samples
from HNL.Samples.sample import createSampleList, getSampleFromList
    sampleList = createSampleList('../Samples/InputFiles/'+args.year+'_sampleList.conf')

#Get specific sample for this subjob
sample = getSampleFromList(sampleList, args.sampleName)
chain = sample.initTree()


# Create new reduced tree (except if it already exists and overwrite option is not used)
from HNL.Tools.helpers import isValidRootFile
outputName = os.path.join('/user/$USER/public/ntuples', str(args.year), sample.output, sample.name + '_' + str(args.subJob) + '.root')

try:    os.makedirs(os.path.dirname(outputName))
except: pass

if not args.overwrite and isValidRootFile(outputName):
  log.info('Finished: valid outputfile already exists')
  exit(0)

outputFile = ROOT.TFile(outputName ,"RECREATE")
outputFile.mkdir('blackJackAndHookers')
outputFile.cd('blackJackAndHookers')

