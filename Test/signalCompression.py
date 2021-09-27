#! /usr/bin/env python

import ROOT
import os

lumi = 35545.499065

#Parse arguments
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
submission_parser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='prelegacy', choices = ['UL', 'prelegacy'],   help='Select era')

argParser.add_argument('--plotSoftTau',   action='store_true', default=False,  help='Extra overlay of softest tau in the process')
argParser.add_argument('--makePlots',   action='store_true', default=False,  help='Use existing root files to make the plots')

args = argParser.parse_args()
print 'Loading in samples'

#Load in samples and get the specific sample for this job
from HNL.Samples.sampleManager import SampleManager
sample_manager = SampleManager(args.era, args.year, 'noskim', 'allsignal_'+args.era+args.year)

#
# Change some settings if this is a test
#
if args.isTest: 
    from HNL.Tools.logger import getLogger, closeLogger
    log = getLogger('INFO')
    args.isChild = True
    if args.sample is None: args.sample = 'HNL-e-m20'
    if args.subJob is None: args.subJob = '0'

if not args.isChild:
    from HNL.Tools.jobSubmitter import submitJobs
    jobs = []
    for sample_name in sample_manager.sample_names:
        print sample_name
        sample = sample_manager.getSample(sample_name)        
        for njob in xrange(sample.returnSplitJobs()): 
            jobs += [(sample.name, str(njob))]

    submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'compression')
    exit(0)


#Initialize chain
print 'Initializing chain'
sample = sample_manager.getSample(args.sample)
chain = sample.initTree()
chain.HNLmass = sample.getMass()
chain.year = args.year
chain.era = args.era
chain.analysis = 'HNL'
print 'Chain initialized'

#Set output dir
#Since number of subjobs was set to be 1 (HNL samples are small), this name was chosen since no overlap possible
#If this changes, this needs to be changed as well
from HNL.Tools.helpers import makeDirIfNeeded
if not args.isTest:
    output_name = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Test', 'data', os.path.basename(__file__).split('.')[0], sample.output)
else:
    output_name = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Test', 'data', 'testArea', os.path.basename(__file__).split('.')[0], sample.output)
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
    eventRange = xrange(20000)
else:
    eventRange = sample.getEventRange(int(args.subJob))

from HNL.Tools.helpers import progress 

def getSortKey(item): return item[0]

from HNL.EventSelection.eventSelector import EventSelector
from HNL.EventSelection.eventCategorization import EventCategory, filterSuperCategory
from HNL.EventSelection.signalLeptonMatcher import SignalLeptonMatcher
slm = SignalLeptonMatcher(chain)
ec = EventCategory(chain)
es = EventSelector('baseline', chain, chain, is_reco_level = False, event_categorization=ec)

#
# Create cutter to provide cut flow
#
from HNL.EventSelection.cutter import Cutter
cutter = Cutter(chain = chain)

#Loop over events
for entry in eventRange:
    
    #print progress and load in entry
    progress(entry-eventRange[0], len(eventRange))
    chain.GetEntry(entry)

    if not es.passedFilter(cutter, sample.output): continue
    slm.saveNewOrder()
    category = ec.returnCategory()
    if not filterSuperCategory('SingleTau', category): continue
    # print category, entry
    # if chain._gen_nL < 3: continue

    # lep = [(chain._gen_lPt[i], i) for i in xrange(chain._gen_nL)]
    # pts = sorted(lep, reverse=True, key = getSortKey)
    # taus = [pts[i] for i in xrange(3) if chain._gen_lFlavor[pts[i][1]] == 2]

    pt_hist[0].Fill(chain.l_pt[0])
    pt_hist[1].Fill(chain.l_pt[1])
    pt_hist[2].Fill(chain.l_pt[2])

    # print chain.l_flavor

    # if args.plotSoftTau and 'tau' in sample.name:
    #     print len(taus)
    #     if len(taus) > 0: pt_hist[3].Fill(taus[-1][0]) 
    #     if len(taus) > 1: pt_hist[4].Fill(taus[-2][0]) 

# if args.isTest: exit(0)

#Write and plot
out_file = ROOT.TFile(output_name, 'recreate')
out_file.cd() 
for subh in pt_hist:
    subh.Write()
out_file.Close()


from HNL.Plotting.plot import Plot
# legend_names = ['leading gen p_{T}', 'subleading gen p_{T}', 'trailing gen p_{T}']
legend_names = ['l1 p_{T}', 'l2 p_{T}', 'l3 p_{T}']
if args.plotSoftTau and 'tau' in sample.name:
    legend_names.append('softest gen tau p_{T}')
    legend_names.append('subleading gen tau p_{T}')
plot = Plot(pt_hist, legend_names, name = sample.name, x_name = 'p_{T} [GeV]', y_name = 'Events')
plot_name = os.path.join(os.path.expandvars('$CMSSW_BASE/src/HNL/Test/data'), os.path.basename(__file__).split('.')[0], 'Plots')
plot.drawHist(plot_name)


if args.isTest:
    closeLogger(log)