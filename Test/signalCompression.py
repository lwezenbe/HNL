#! /usr/bin/env python

import ROOT
import os

lumi = 35545.499065

#Parse arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
argParser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
argParser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
argParser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
argParser.add_argument('--runLocal', action='store_true', default=False,  help='use local resources instead of Cream02')
argParser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
argParser.add_argument('--plotSoftTau',   action='store_true', default=False,  help='Extra overlay of softest tau in the process')
args = argParser.parse_args()

args = argParser.parse_args()
print 'Loading in samples'

#Load in samples and get the specific sample for this job
from HNL.Samples.sample import createSampleList, getSampleFromList
sample_list = createSampleList(os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/signalCompression.conf'))

#
# Change some settings if this is a test
#
if args.isTest: 
    args.isChild = True
    args.sample = 'HNLtau-M10'
    args.subJob = '0'

if not args.isChild:
    from HNL.Tools.jobSubmitter import submitJobs
    jobs = []
    for sample in sample_list:
        for njob in xrange(sample.split_jobs): 
            jobs += [(sample.name, str(njob))]

    submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'compression_'+sample.name)
    exit(0)


#Initialize chain
print 'Initializing chain'
sample = getSampleFromList(sample_list, args.sample)
chain = sample.initTree()
print 'Chain initialized'

#Set output dir
#Since number of subjobs was set to be 1 (HNL samples are small), this name was chosen since no overlap possible
#If this changes, this needs to be changed as well
from HNL.Tools.helpers import makeDirIfNeeded
output_name = os.path.join(os.getcwd(), 'data', os.path.basename(__file__).split('.')[0], sample.output)
output_name += '/'+ sample.name + '.root'
makeDirIfNeeded(output_name)


print 'Getting things ready to start the event loop'

#Initialize histograms
pt_hist = [ROOT.TH1D('leading_pt', sample.name, 100, 0, 100),
           ROOT.TH1D('subleading_pt', sample.name, 100, 0, 100),
           ROOT.TH1D('trailing_pt', sample.name, 100, 0, 100)]
if args.plotSoftTau and 'tau' in sample.name: pt_hist.append(ROOT.TH1D('softest_tau', sample.name, 100, 0, 100))
if args.plotSoftTau and 'tau' in sample.name: pt_hist.append(ROOT.TH1D('subleading_tau', sample.name, 100, 0, 100))

#Determine if testrun so it doesn't need to calculate the number of events in the getEventRange
if args.isTest:
    eventRange = xrange(1000)
else:
    eventRange = sample.getEventRange(int(args.subJob))

from HNL.Tools.helpers import progress 

def getSortKey(item): return item[0]

#Loop over events
for entry in eventRange:
    
    #print progress and load in entry
    progress(entry-eventRange[0], len(eventRange))
    chain.GetEntry(entry)

    if chain._gen_nL < 3: continue

    lep = [(chain._gen_lPt[i], i) for i in xrange(chain._gen_nL)]
    pts = sorted(lep, reverse=True, key = getSortKey)
    taus = [pts[i] for i in xrange(3) if chain._gen_lFlavor[pts[i][1]] == 2]

    pt_hist[0].Fill(pts[0][0])
    pt_hist[1].Fill(pts[1][0])
    pt_hist[2].Fill(pts[2][0])

    if args.plotSoftTau and 'tau' in sample.name:
        print len(taus)
        if len(taus) > 0: pt_hist[3].Fill(taus[-1][0]) 
        if len(taus) > 1: pt_hist[4].Fill(taus[-2][0]) 

#if args.isTest: exit(0)

#Write and plot
out_file = ROOT.TFile(output_name, 'recreate')
out_file.cd() 
for subh in pt_hist:
    subh.Write()
out_file.Close()


from HNL.Plotting.plot import Plot
legend_names = ['leading gen p_{T}', 'subleading gen p_{T}', 'trailing gen p_{T}']
if args.plotSoftTau and 'tau' in sample.name:
    legend_names.append('softest gen tau p_{T}')
    legend_names.append('subleading gen tau p_{T}')
plot = Plot(pt_hist, legend_names, name = sample.name, x_name = 'p_{T} [GeV]', y_name = 'Events')
plot_name = os.path.join(os.path.expandvars('$CMSSW_BASE/src/HNL/Test/data'), os.path.basename(__file__).split('.')[0], 'Plots')
plot.drawHist(plot_name)
#    DrawHist(pt_hist, 'p_{T} [GeV]', 'Events', ['leading gen p_{T}', 'subleading gen p_{T}', 'trailing gen p_{T}'], plot_name)
