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
submission_parser.add_argument('--strategy',   action='store', default='MVA',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA'])
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
nl = 3 if args.region != 'ZZCR' else 4

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
file_list = 'TMVA/fulllist_'+str(args.year)+'_mconly' if args.customList is None else args.customList
skim_str = 'noskim' if args.noskim else 'Reco'
sample_manager = SampleManager(args.year, skim_str, file_list)
jobs = []
for sample_name in sample_manager.sample_names:
    if sample_name == 'Data': continue
    sample = sample_manager.getSample(sample_name)
    for njob in xrange(sample.returnSplitJobs()): 
        jobs += [(sample.name, str(njob))]

from HNL.EventSelection.eventCategorization import SUPER_CATEGORIES

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

    signal_str = 'Signal' if chain.is_signal else 'Background'
    output_name = os.path.join(output_base, 'TMVA', str(args.year), args.region + '-'+args.selection, signal_str, 'tmp_'+sample.output, sample.name + '_' +sample.output+'_'+ str(args.subJob) + '.root')
    makeDirIfNeeded(output_name)

    # if not args.isTest and isValidRootFile(output_name):
    #     log.info('Finished: valid outputfile already exists')
    #     exit(0)

    output_file = ROOT.TFile(output_name ,"RECREATE")

    #
    # Switch off unused branches and create outputTree
    #
    output_tree = {}
    for prompt_str in ['prompt', 'nonprompt']:
        output_tree[prompt_str] = {}
        for c in SUPER_CATEGORIES.keys():
            output_tree[prompt_str][c] = ROOT.TTree('trainingtree', 'trainingtree')
            output_file.mkdir(prompt_str+'/'+c)

    #
    # Make new branches
    #
    from HNL.TMVA.mvaVariables import getAllVariableList, getVariableValue, getVariables
    new_branches = []
    new_branches.extend(getAllVariableList())
    new_branches.extend(['is_signal/O', 'event_weight/F', 'HNL_mass/F', 'HNL_lowmass/F', 'HNL_highmass/F', 'eventNb/I', 'entry/I'])

    from HNL.Tools.makeBranches import makeBranches
    new_vars = {}
    for ip, prompt_str in enumerate(['prompt', 'nonprompt']):
        new_vars[prompt_str] = {}
        for ic, c in enumerate(SUPER_CATEGORIES.keys()):
            new_vars[prompt_str][c] = makeBranches(output_tree[prompt_str][c], new_branches, already_defined = ic > 0 or ip > 0)

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

        if not es.removeOverlapDYandZG(sample.output): continue
        if not es.selector.passedFilter(cutter, for_training=True): continue
        if len(chain.l_flavor) == chain.l_flavor.count(2): continue

        category = ec.returnCategory()
        super_cat = [sc for sc in SUPER_CATEGORIES.keys() if category in SUPER_CATEGORIES[sc]]

        nprompt = 0
        for index in chain.l_indices:
            if chain._lIsPrompt[index]: nprompt += 1
        
        prompt_str = 'prompt' if nprompt == nl else 'nonprompt'

        for sc in super_cat:
            #Set Variables
            for v in getVariables():
                setattr(new_vars[prompt_str][sc], v, getVariableValue(v)(chain))

            new_vars[prompt_str][sc].is_signal = chain.is_signal
            new_vars[prompt_str][sc].HNL_mass = sample.getMass() if chain.is_signal else randrange(10, 800)
            new_vars[prompt_str][sc].HNL_lowmass = sample.getMass() if chain.is_signal else randrange(10, 80)
            new_vars[prompt_str][sc].HNL_highmass = sample.getMass() if chain.is_signal else randrange(80, 800)
            new_vars[prompt_str][sc].event_weight = reweighter.getLumiWeight() if not chain.is_signal else 1.
            new_vars[prompt_str][sc].eventNb = chain._eventNb
            new_vars[prompt_str][sc].entry = entry

            output_tree[prompt_str][sc].Fill()

    for prompt_str in ['prompt', 'nonprompt']:
        for c in SUPER_CATEGORIES.keys():
            output_file.cd(prompt_str+'/'+c)
            output_tree[prompt_str][c].Write()

    output_file.Close()

    closeLogger(log)

    cutter.saveCutFlow(output_name)


else:

    #
    # Check subjobs
    #
    from HNL.Tools.jobSubmitter import checkCompletedJobs

    from HNL.Tools.mergeFiles import merge
    from HNL.Tools.helpers import isValidRootFile
    from HNL.Tools.makeBranches import makeBranches

    import uproot
    def mergeSignal(out_name, in_names):
        num_of_entries = {'tot': {}}
        for in_name in in_names:
            mass = int(in_name.rsplit('/')[-1].split('-m')[-1].split('.')[0])
            num_of_entries[mass] = {}
            for c in SUPER_CATEGORIES.keys():
                num_of_entries[mass][c] = 0.
                for prompt_str in ['prompt', 'nonprompt']:
                    in_file = uproot.open(in_name)
                    num_of_entries[mass][c] += len(in_file[prompt_str][c]['trainingtree']['event_weight'])
        for c in SUPER_CATEGORIES.keys():
            num_of_entries['tot'][c] = 0.
            for ent in num_of_entries.keys():
                if ent == 'tot': continue
                num_of_entries['tot'][c] +=  num_of_entries[ent][c]

        out_file = ROOT.TFile(out_name, 'recreate')
        out_trees = {}
        new_vars = {}
        for ip, prompt_str in enumerate(['prompt', 'nonprompt']):
            out_trees[prompt_str] = {}
            new_vars[prompt_str] = {}
            for ic, c in enumerate(SUPER_CATEGORIES.keys()):
                out_file.mkdir(prompt_str+'/'+c)
                chain = ROOT.TChain(prompt_str+'/'+c+'/trainingtree')
                for in_name in in_names:
                    chain.Add(in_name)
                chain.SetBranchStatus('event_weight', 0)
                out_trees[prompt_str][c] = chain.CloneTree(0)
                if chain.GetEntries() > 0: 
                    new_vars[prompt_str][c] = makeBranches(out_trees[prompt_str][c], ['event_weight/F'], already_defined = ip > 0 or ic > 0)

                    for entry in xrange(chain.GetEntries()):
                        chain.GetEntry(entry)
                        new_vars[prompt_str][c].event_weight = num_of_entries['tot'][c]/num_of_entries[chain.HNL_mass][c]
                        out_trees[prompt_str][c].Fill()
                    out_file.cd(prompt_str+'/'+c)
                    out_trees[prompt_str][c].Write()
                

    merge_base = '/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/' if not args.isTest else '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/TMVA/data/testArea/'

    signal_mergefiles = merge_base+'TMVA/'+str(args.year)+'/'+args.region+'-'+args.selection+'/Signal'
    background_mergefiles = merge_base+'TMVA/'+str(args.year)+'/'+args.region+'-'+args.selection+'/Background'
    merge([signal_mergefiles, background_mergefiles], __file__, jobs, ('sample', 'subJob'), argParser)

    combined_dir = lambda sd : merge_base+'TMVA/'+str(args.year)+'/'+args.region+'-'+args.selection+'/Combined/'+sd
    makeDirIfNeeded(combined_dir('SingleTree')+'/test')
    makeDirIfNeeded(combined_dir('TwoTrees')+'/test')

    import glob
    all_signal_files = glob.glob(merge_base+'TMVA/'+str(args.year)+'/'+args.region+'-'+args.selection+'/Signal/*root')
    low_mass = [10, 20, 40, 50, 60, 70, 80]
    high_mass = [90, 100, 120, 130, 150, 200, 300, 400, 500, 600, 800]
    tau = lambda mass : merge_base+'TMVA/'+str(args.year)+'/'+args.region+'-'+args.selection+'/Signal/HNL-tau-m'+str(mass)+'.root'
    ele = lambda mass : merge_base+'TMVA/'+str(args.year)+'/'+args.region+'-'+args.selection+'/Signal/HNL-e-m'+str(mass)+'.root'
    mu = lambda mass : merge_base+'TMVA/'+str(args.year)+'/'+args.region+'-'+args.selection+'/Signal/HNL-mu-m'+str(mass)+'.root'


    all_bkgr_files = merge_base+'TMVA/'+str(args.year)+'/'+args.region+'-'+args.selection+'/Background/*root'

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

    mergeSignal(signal_mergefiles+'/high_e.root', high_mass_e)
    mergeSignal(signal_mergefiles+'/high_tau.root', high_mass_tau)
    mergeSignal(signal_mergefiles+'/high_mu.root', high_mass_mu)
    mergeSignal(signal_mergefiles+'/low_e.root', low_mass_e)
    mergeSignal(signal_mergefiles+'/low_tau.root', low_mass_tau)
    mergeSignal(signal_mergefiles+'/low_mu.root', low_mass_mu)
    mergeSignal(signal_mergefiles+'/all_e.root', low_mass_e+high_mass_e)
    mergeSignal(signal_mergefiles+'/all_tau.root', low_mass_tau+high_mass_tau)
    mergeSignal(signal_mergefiles+'/all_mu.root', low_mass_mu+high_mass_mu)

    # makeDirIfNeeded(signal_mergefiles+'/x')
    # os.system('hadd -f ' + signal_mergefiles+'/low_tau.root '+' '.join(low_mass_tau))
    # os.system('hadd -f ' + signal_mergefiles+'/high_tau.root '+' '.join(high_mass_tau))
    # os.system('hadd -f ' + signal_mergefiles+'/all_tau.root '+' '.join(low_mass_tau) +' '+' '.join(high_mass_tau))
    # os.system('hadd -f ' + signal_mergefiles+'/low_e.root '+' '.join(low_mass_e))
    # os.system('hadd -f ' + signal_mergefiles+'/high_e.root '+' '.join(high_mass_e))
    # os.system('hadd -f ' + signal_mergefiles+'/all_e.root '+' '.join(low_mass_e)+' '+' '.join(high_mass_e))
    # os.system('hadd -f ' + signal_mergefiles+'/low_mu.root '+' '.join(low_mass_mu))
    # os.system('hadd -f ' + signal_mergefiles+'/high_mu.root '+' '.join(high_mass_mu))
    # os.system('hadd -f ' + signal_mergefiles+'/all_mu.root '+' '.join(low_mass_mu) +' '+' '.join(high_mass_mu))

    makeDirIfNeeded(background_mergefiles+'/Combined/x')
    os.system('hadd -f ' + background_mergefiles+'/Combined/all_bkgr.root '+ all_bkgr_files)

    os.system('hadd -f ' + combined_dir('SingleTree')+'/low_tau.root '+signal_mergefiles+'/low_tau.root ' +background_mergefiles+'/Combined/all_bkgr.root ')
    os.system('hadd -f ' + combined_dir('SingleTree')+'/high_tau.root '+signal_mergefiles+'/high_tau.root ' +background_mergefiles+'/Combined/all_bkgr.root ')
    os.system('hadd -f ' + combined_dir('SingleTree')+'/all_tau.root '+signal_mergefiles+'/all_tau.root  ' +background_mergefiles+'/Combined/all_bkgr.root ')
    os.system('hadd -f ' + combined_dir('SingleTree')+'/low_e.root '+signal_mergefiles+'/low_e.root '+background_mergefiles+'/Combined/all_bkgr.root ')
    os.system('hadd -f ' + combined_dir('SingleTree')+'/high_e.root '+signal_mergefiles+'/high_e.root '+background_mergefiles+'/Combined/all_bkgr.root ')
    os.system('hadd -f ' + combined_dir('SingleTree')+'/all_e.root '+signal_mergefiles+'/all_e.root ' +background_mergefiles+'/Combined/all_bkgr.root ')
    os.system('hadd -f ' + combined_dir('SingleTree')+'/low_mu.root '+signal_mergefiles+'/low_mu.root '+background_mergefiles+'/Combined/all_bkgr.root ')
    os.system('hadd -f ' + combined_dir('SingleTree')+'/high_mu.root '+signal_mergefiles+'/high_mu.root ' +background_mergefiles+'/Combined/all_bkgr.root ')
    os.system('hadd -f ' + combined_dir('SingleTree')+'/all_mu.root '+signal_mergefiles+'/all_mu.root ' +background_mergefiles+'/Combined/all_bkgr.root ')


