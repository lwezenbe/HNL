import ROOT
import numpy as np
import os

lumi = 35545.499065
output_dir = '/user/lwezenbe/private/PhD/Code/TauStudy/FakeRate/ClosureTest/Data'

#Parse arguments
import argparse

argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--sampleName',          action='store',         default='HNLe',      help='Name of sample as specifiec in input file. Default is DYJetsToLL_M-50')
argParser.add_argument('--subJob',              action='store',         default=0,                      help='Index of subjob. Default is 0')
argParser.add_argument('--year',                action='store',         default='2016',                 help='Year of datataking (2016, 2017, 2018)')
argParser.add_argument('--isTest',              action='store_true',                                    help='Perform local run on limited number of events')

args = argParser.parse_args()
print 'Loading in samples'

#Load in samples and get the specific sample for this job
from HNL.Samples.sample import createSampleList, getSampleFromList
sampleList = createSampleList('/storage_mnt/storage/user/lwezenbe/private/PhD/CMSSW_10_2_17/src/HNL/Samples/InputFiles/signalCompression.conf')
sample = getSampleFromList(sampleList, args.sampleName)

#Set output dir
from HNL.Tools.helpers import makeDirIfNeeded
output_name = os.path.join('/storage_mnt/storage/user/lwezenbe/private/PhD/CMSSW_10_2_17/src/HNL/Test/Data', args.year, sample.output, sample.name  + '.root') 
makeDirIfNeeded(output_name)

#Initialize chain
print 'Initializing chain'
chain = sample.initTree()
print 'Chain initialized'

print 'Getting things ready to start the event loop'

#Initialize histograms
pt_hist = [ROOT.TH1D('leading_pt', 'leading pt', 100, 0, 100),
           ROOT.TH1D('subleading_pt', 'subleading pt', 100, 0, 100),
           ROOT.TH1D('trailing_pt', 'trailing pt', 100, 0, 100)]

#Determine if testrun so it doesn't need to calculate the number of events in the getEventRange
if args.isTest:
    eventRange = xrange(100)
else:
    eventRange = sample.getEventRange(int(args.subJob))

from HNL.Tools.helpers import progress 

#Loop over events
for entry in eventRange:
    
    #print progress and load in entry
    progress(entry-eventRange[0], len(eventRange))
    chain.GetEntry(entry)

    if chain._gen_nL < 3: continue

    pts = sorted([chain._gen_lPt[0], chain._gen_lPt[1], chain._gen_lPt[2]], reverse=True)

    pt_hist[0].Fill(pts[0])
    pt_hist[1].Fill(pts[1])
    pt_hist[2].Fill(pts[2])

#Write and plot
if not args.isTest:
    out_file = ROOT.TFile(output_name, 'recreate')
    out_file.cd() 
    for subh in pt_hist:
        subh.Write()
    out_file.Close()


    from HNL.Plotting.plottingTools import DrawHist
    plot_name = os.path.join('/storage_mnt/storage/user/lwezenbe/private/PhD/CMSSW_10_2_17/src/HNL/Test/Plots', sample.output)
    DrawHist(pt_hist, 'p_{T} [GeV]', 'Events', ['leading gen p_{T}', 'subleading gen p_{T}', 'trailing gen p_{T}'], plot_name)
