#
# Code to make trees to use in training
#

#
# Argument parser and logging
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018'])
submission_parser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--logLevel',  action='store',      default='INFO',               help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])

submission_parser.add_argument('--summaryFile', action='store_true', default=False,  help='Create text file that shows all selected arguments')
submission_parser.add_argument('--noskim', action='store_true', default=False,  help='Use unskimmed files')
submission_parser.add_argument('--customList',  action='store',      default=None,               help='Name of a custom sample list. Otherwise it will use the appropriate noskim file.')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
submission_parser.add_argument('--strategy',   action='store', default='cutbased',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA'])
submission_parser.add_argument('--region',   action='store', default='baseline', 
    help='apply the cuts of high or low mass regions, use "all" to run both simultaniously', choices=['baseline', 'highMassSR', 'lowMassSR', 'ZZ', 'WZ', 'Conversion'])

argParser.add_argument('--merge',   action='store_true', default=False,  help='merge existing subjob output')


args = argParser.parse_args()

from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)

import ROOT
import os
from HNL.Tools.helpers import isValidRootFile, makeDirIfNeeded
from HNL.Weights.reweighter import Reweighter
from random import randrange


#
# Set some args for when performing a test
#
if args.isTest:
    if args.sample is None: args.sample = 'DYJetsToLL-M-50'
    if args.year is None: args.year = '2016'
    if args.subJob is None: args.subJob = 0
    args.isChild = True


#
#Load in samples
#
from HNL.Samples.sampleManager import SampleManager
file_list = 'fulllist_'+str(args.year)+'_mconly' if args.customList is None else args.customList
skim_str = 'noskim' if args.noskim else 'Reco'
sample_manager = SampleManager(args.year, skim_str, file_list)
jobs = []
for sample_name in sample_manager.sample_names:
    if sample_name == 'Data': continue
    sample = sample_manager.getSample(sample_name)
    for njob in xrange(sample.returnSplitJobs()): 
        jobs += [(sample.name, str(njob))]

if not args.merge:


    #
    # Submit subjobs
    #
    if not args.isChild:
        from HNL.Tools.jobSubmitter import submitJobs

        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'prepareTMVA')
        exit(0)


    #
    #Get specific sample for this subjob
    #
    sample = sample_manager.getSample(args.sample)
    chain = sample.initTree(needhcount=False)
    chain.year = int(args.year)
    chain.is_signal = 'HNL' in sample.name
    chain.selection = args.selection
    chain.strategy = args.strategy

    reweighter = Reweighter(sample, sample_manager)

    # Import and create cutter to provide cut flow
    #
    from HNL.EventSelection.cutter import Cutter
    cutter = Cutter(chain = chain)

    #
    # Create new reduced tree (except if it already exists and overwrite option is not used)
    #
    output_base = os.path.expandvars(os.path.join('/user/$USER/public/ntuples/HNL')) if not args.isTest else os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'TMVA', 'data', 'testArea'))
    # output_base = os.path.expandvars(os.path.join('/user/$USER/public/ntuples/HNL'))

    signal_str = 'Signal' if chain.is_signal else 'Background'
    output_name = os.path.join(output_base, 'TMVA', str(args.year), args.region, signal_str, 'tmp_'+sample.output, sample.output+'_'+sample.name + '_' + str(args.subJob) + '.root')
    makeDirIfNeeded(output_name)

    # if not args.isTest and isValidRootFile(output_name):
    #     log.info('Finished: valid outputfile already exists')
    #     exit(0)

    output_file = ROOT.TFile(output_name ,"RECREATE")

    #
    # Switch off unused branches and create outputTree
    #

    output_tree = ROOT.TTree('trainingtree', 'trainingtree')

    #
    # Make new branches
    #
    from HNL.TMVA.mvaVariables import getAllVariableList
    new_branches = []
    new_branches.extend(getAllVariableList())
    new_branches.extend(['is_signal/O', 'event_weight/F', 'HNL_mass/F', 'HNL_lowmass/F', 'HNL_highmass/F'])

    from HNL.Tools.makeBranches import makeBranches
    new_vars = makeBranches(output_tree, new_branches)

    #
    # Start event loop
    #
    if args.isTest:
        max_events = 20000
        event_range = xrange(max_events) if max_events < len(sample.getEventRange(args.subJob)) else sample.getEventRange(args.subJob)

    else:
        event_range = sample.getEventRange(args.subJob)    

    from HNL.Tools.helpers import progress
    from HNL.EventSelection.eventSelector import EventSelector
    from HNL.EventSelection.eventCategorization import EventCategory
    ec = EventCategory(chain)

    #prepare object  and event selection
    from HNL.ObjectSelection.objectSelection import getObjectSelection
    chain.obj_sel = getObjectSelection(args.selection)
    es = EventSelector(args.region, chain, chain, True, ec)

    for entry in event_range:
        chain.GetEntry(entry)
        progress(entry - event_range[0], len(event_range))
    
        cutter.cut(True, 'Total')

        if not es.passedFilter(cutter): continue
        if len(chain.l_flavor) == chain.l_flavor.count(2): continue

        #Set Variables
        new_vars.M3l = chain.M3l
        new_vars.MT3l = chain.mt3
        new_vars.minMss = chain.minMss
        new_vars.minMos = chain.minMos
        new_vars.maxMos = chain.maxMos
        new_vars.maxMossf = chain.maxMossf
        new_vars.mtOther = chain.mtOther
        new_vars.mtl1 = chain.mtl1
        new_vars.mtl2 = chain.mtl2
        new_vars.l1_charge = chain.l_charge[0]
        new_vars.l2_charge = chain.l_charge[1]
        new_vars.l3_charge = chain.l_charge[2]
        new_vars.l1_pt = chain.l_pt[0]
        new_vars.l2_pt = chain.l_pt[1]
        new_vars.l3_pt = chain.l_pt[2]
        new_vars.l1_eta = chain.l_eta[0]
        new_vars.l2_eta = chain.l_eta[1]
        new_vars.l3_eta = chain.l_eta[2]
        new_vars.l1_phi = chain.l_phi[0]
        new_vars.l2_phi = chain.l_phi[1]
        new_vars.l3_phi = chain.l_phi[2]
        new_vars.j1_pt = chain.j_pt[0]
        new_vars.j2_pt = chain.j_pt[1]
        new_vars.j1_eta = chain.j_eta[0]
        new_vars.j2_eta = chain.j_eta[1]
        new_vars.j1_phi = chain.j_phi[0]
        new_vars.j2_phi = chain.j_phi[1]
        new_vars.HT = chain.HT
        new_vars.LT = chain.LT
        new_vars.njets = chain.njets
        new_vars.is_signal = chain.is_signal
        new_vars.ptConeLeading = chain.pt_cone[0]
        new_vars.met = chain._met
        new_vars.dr_minOS = chain.dr_minOS
        new_vars.HNL_mass = sample.getMass() if chain.is_signal else randrange(10, 800)
        new_vars.HNL_lowmass = sample.getMass() if chain.is_signal else randrange(10, 80)
        new_vars.HNL_highmass = sample.getMass() if chain.is_signal else randrange(80, 800)
        new_vars.event_weight = reweighter.getLumiWeight() if not chain.is_signal else 1.

        output_tree.Fill()

    output_tree.AutoSave()


    output_file.Close()

    closeLogger(log)


    # cutter.saveCutFlow(output_name) #TODO: For some reason cuts become None after closing file


else:

    #
    # Check subjobs
    #
    from HNL.Tools.jobSubmitter import checkCompletedJobs

    from HNL.Tools.mergeFiles import merge
    from HNL.Tools.helpers import isValidRootFile

    merge_base = '/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/' if not args.isTest else '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/TMVA/data/testArea/'

    signal_mergefiles = merge_base+'TMVA/'+str(args.year)+'/'+args.region+'/Signal'
    background_mergefiles = merge_base+'TMVA/'+str(args.year)+'/'+args.region+'/Background'
    merge([signal_mergefiles, background_mergefiles], __file__, jobs, ('sample', 'subJob'), argParser)

    combined_dir = lambda sd : merge_base+'TMVA/'+str(args.year)+'/'+args.region+'/Combined/'+sd
    makeDirIfNeeded(combined_dir('SingleTree')+'/test')
    makeDirIfNeeded(combined_dir('TwoTrees')+'/test')

    import glob
    all_signal_files = glob.glob(merge_base+'TMVA/'+str(args.year)+'/'+args.region+'/Signal/*root')
    low_mass = [10, 20, 40, 50, 60, 70, 80]
    high_mass = [90, 100, 120, 130, 150, 200, 300, 400, 500, 600, 800]
    tau = lambda mass : merge_base+'TMVA/'+str(args.year)+'/'+args.region+'/Signal/HNL-tau-m'+str(mass)+'.root'
    ele = lambda mass : merge_base+'TMVA/'+str(args.year)+'/'+args.region+'/Signal/HNL-e-m'+str(mass)+'.root'
    mu = lambda mass : merge_base+'TMVA/'+str(args.year)+'/'+args.region+'/Signal/HNL-mu-m'+str(mass)+'.root'


    all_bkgr_files = merge_base+'TMVA/'+str(args.year)+'/'+args.region+'/Background/*root'

    #Low mass
    low_mass_tau = []
    low_mass_e = []
    low_mass_mu = []
    for mass in low_mass:
        if isValidRootFile(tau(mass)): low_mass_tau.append(tau(mass))
        if isValidRootFile(ele(mass)): low_mass_e.append(ele(mass))
        if isValidRootFile(mu(mass)): low_mass_mu.append(mu(mass))
    
    #high mass
    high_mass_tau = []
    high_mass_e = []
    high_mass_mu = []
    for mass in high_mass:
        if isValidRootFile(tau(mass)): high_mass_tau.append(tau(mass))
        if isValidRootFile(ele(mass)): high_mass_e.append(ele(mass))
        if isValidRootFile(mu(mass)): high_mass_mu.append(mu(mass))


    makeDirIfNeeded(signal_mergefiles+'/Combined/x')
    os.system('hadd -f ' + signal_mergefiles+'/Combined/low_tau.root '+' '.join(low_mass_tau))
    os.system('hadd -f ' + signal_mergefiles+'/Combined/high_tau.root '+' '.join(high_mass_tau))
    os.system('hadd -f ' + signal_mergefiles+'/Combined/all_tau.root '+' '.join(low_mass_tau) +' '+' '.join(high_mass_tau))
    os.system('hadd -f ' + signal_mergefiles+'/Combined/low_e.root '+' '.join(low_mass_e))
    os.system('hadd -f ' + signal_mergefiles+'/Combined/high_e.root '+' '.join(high_mass_e))
    os.system('hadd -f ' + signal_mergefiles+'/Combined/all_e.root '+' '.join(low_mass_e)+' '+' '.join(high_mass_e))
    os.system('hadd -f ' + signal_mergefiles+'/Combined/low_mu.root '+' '.join(low_mass_mu))
    os.system('hadd -f ' + signal_mergefiles+'/Combined/high_mu.root '+' '.join(high_mass_mu))
    os.system('hadd -f ' + signal_mergefiles+'/Combined/all_mu.root '+' '.join(low_mass_mu) +' '+' '.join(high_mass_mu))

    makeDirIfNeeded(background_mergefiles+'/Combined/x')
    os.system('hadd -f ' + background_mergefiles+'/Combined/all_bkgr.root '+ all_bkgr_files)

    os.system('hadd -f ' + combined_dir('SingleTree')+'/low_tau.root '+signal_mergefiles+'/Combined/low_tau.root ' +background_mergefiles+'/Combined/all_bkgr.root ')
    os.system('hadd -f ' + combined_dir('SingleTree')+'/high_tau.root '+signal_mergefiles+'/Combined/high_tau.root ' +background_mergefiles+'/Combined/all_bkgr.root ')
    os.system('hadd -f ' + combined_dir('SingleTree')+'/all_tau.root '+signal_mergefiles+'/Combined/all_tau.root  ' +background_mergefiles+'/Combined/all_bkgr.root ')
    os.system('hadd -f ' + combined_dir('SingleTree')+'/low_e.root '+signal_mergefiles+'/Combined/low_e.root '+background_mergefiles+'/Combined/all_bkgr.root ')
    os.system('hadd -f ' + combined_dir('SingleTree')+'/high_e.root '+signal_mergefiles+'/Combined/high_e.root '+background_mergefiles+'/Combined/all_bkgr.root ')
    os.system('hadd -f ' + combined_dir('SingleTree')+'/all_e.root '+signal_mergefiles+'/Combined/all_e.root ' +background_mergefiles+'/Combined/all_bkgr.root ')
    os.system('hadd -f ' + combined_dir('SingleTree')+'/low_mu.root '+signal_mergefiles+'/Combined/low_mu.root '+background_mergefiles+'/Combined/all_bkgr.root ')
    os.system('hadd -f ' + combined_dir('SingleTree')+'/high_mu.root '+signal_mergefiles+'/Combined/high_mu.root ' +background_mergefiles+'/Combined/all_bkgr.root ')
    os.system('hadd -f ' + combined_dir('SingleTree')+'/all_mu.root '+signal_mergefiles+'/Combined/all_mu.root ' +background_mergefiles+'/Combined/all_bkgr.root ')

    bkgr_infile = ROOT.TFile(background_mergefiles+'/Combined/all_bkgr.root', 'read')
    bkgr_intree = bkgr_infile.Get('trainingtree')
    for flav in ['e', 'mu', 'tau']:
        for mass_region in ['low', 'high', 'all']:
            print 'Copying', flav, mass_region
            signal_infile = ROOT.TFile(signal_mergefiles+'/Combined/'+mass_region +'_'+flav+'.root', 'read')
            signal_intree = signal_infile.Get('trainingtree')

            two_trees_outfile = ROOT.TFile(combined_dir('TwoTrees')+'/'+mass_region + '_' + flav+'.root', 'recreate')
            signal_intree.CloneTree().Write('signaltree')
            bkgr_intree.CloneTree().Write('backgroundtree')
            two_trees_outfile.Close()
            signal_infile.Close()

    bkgr_infile.Close()