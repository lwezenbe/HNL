#! /usr/bin/env python

#
#       Code to look at the cutflow of taus in our current object selection
#

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
argParser.add_argument('--masses', type=int, nargs='*',  help='Only run or plot signal samples with mass given in this list')
argParser.add_argument('--plotCutFlow', action='store_true', default=False,  help='plot the cut flow')
argParser.add_argument('--message', type = str, default=None,  help='Add a file with a message in the plotting folder')
args = argParser.parse_args()

#
# Change some settings if this is a test
#
if args.isTest:
    args.isChild = True

    args.sample = 'HNLtau-60'
    args.subJob = '0'
    args.year = '2016'


#
# Load in the sample list 
#
from HNL.Samples.sample import createSampleList, getSampleFromList
list_location = os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/sampleList_'+args.year+'_noskim.conf')
sample_list = createSampleList(list_location)

if not args.plotCutFlow:
    #
    # Submit subjobs
    #
    if not args.isChild:
        from HNL.Tools.jobSubmitter import submitJobs
        jobs = []
        for sample in sample_list:
            if args.sample and args.sample not in sample.name: continue
            if not 'HNLtau' in sample.name: continue
            if args.masses is not None and 'HNL' in sample.name and not any([str(m) in sample.name for m in args.masses]): continue
            for njob in xrange(sample.split_jobs):
                jobs += [(sample.name, str(njob))]

        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'calcSignalEfficiency')
        exit(0)

    #
    # Load in sample and chain
    #
    sample = getSampleFromList(sample_list, args.sample)
    chain = sample.initTree(needhcount = False)

    #
    # Import and create cutter to provide cut flow
    #
    from HNL.EventSelection.cutter import Cutter
    cutter = Cutter(chain = chain)

    if args.isTest:
        event_range = xrange(500)
    else:
        event_range = sample.getEventRange(args.subJob)    

    if 'HNL' in sample.name:
        chain.HNLmass = float(sample.name.rsplit('-', 1)[1])
    chain.year = int(args.year)

    #
    # Loop over all events
    #
    from HNL.Tools.helpers import progress
    from HNL.ObjectSelection.tauSelector import tau_DMfinding, isCleanFromLightLeptons, passedMuonDiscr, passedElectronDiscr, tau_id_WP, isGoodGenTau
    algo_iso = 'deeptauVSjets'
    for entry in event_range:
        
        chain.GetEntry(entry)
        progress(entry - event_range[0], len(event_range))

        for index in xrange(chain._gen_nL):      
            cutter.cut(isGoodGenTau(chain, index), 'total gen tau')

        for index in xrange(chain._nLight, chain._nL):
            if chain._tauGenStatus[index] != 5: continue
            cutter.cut(True, 'total reconstructed tau')
            if not cutter.cut(chain._lFlavor[index] == 2, 'lFlavor == 2'):              continue
            if not cutter.cut(chain._lPt[index] > 20, 'pt > 20 GeV'):                   continue
            if not cutter.cut(chain._lEta[index] < 2.3, 'eta < 2.3'):                   continue
            if not cutter.cut(tau_DMfinding[algo_iso](chain)[index] and chain._tauDecayMode[index] != 5 and chain._tauDecayMode[index] != 6, 'DM finding'):     continue
            if not cutter.cut(isCleanFromLightLeptons(chain, index), 'clean from light lep'):                           continue
            if not cutter.cut(passedElectronDiscr(chain, index, algo_iso, 'loose'), 'loose deeptauVSe'):    continue
            if not cutter.cut(passedMuonDiscr(chain, index, algo_iso, 'loose'), 'loose deeptauVSmu'):    continue
            if not cutter.cut(tau_id_WP[(algo_iso, 'tight')](chain)[index], 'tight deeptauVSjets'):                   continue

    output_name = os.getcwd() +'/tauCutFlow/'+sample.output+'.root'
    cutter.saveCutFlow(output_name)

else:
    import glob
    all_files = glob.glob(os.getcwd() +'/tauCutFlow/*.root')
    all_files = sorted(all_files, key = lambda k : int(k.split('/')[-1].split('.')[0].split('-M')[1]))
    all_names = [k.split('/')[-1].split('.')[0] for k in all_files]

    from HNL.EventSelection.cutter import plotCutFlow
    out_name = os.getcwd() +'/tauCutFlow/Output'
    plotCutFlow(all_files, out_name, all_names)

