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
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='UL', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--logLevel',  action='store',     default='INFO', help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])

submission_parser.add_argument('--summaryFile', action='store_true', default=False,  help='Create text file that shows all selected arguments')
submission_parser.add_argument('--noskim', action='store_true', default=False,  help='Use unskimmed files')
submission_parser.add_argument('--customList',  action='store',      default=None,               help='Name of a custom sample list. Otherwise it will use the appropriate noskim file.')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
submission_parser.add_argument('--strategy',   action='store', default='MVA',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA'])
submission_parser.add_argument('--region',   action='store', default='baseline', 
    help='apply the cuts of high or low mass regions, use "all" to run both simultaniously', choices=['baseline', 'highMassSR', 'lowMassSRloose', 'ZZ', 'WZ', 'Conversion'])
submission_parser.add_argument('--analysis',   action='store', default='HNL',  help='Select the strategy to use to separate signal from background', choices=['HNL', 'AN2017014', 'ewkino'])

argParser.add_argument('--merge',   action='store_true', default=False,  help='merge existing subjob output')


args = argParser.parse_args()

from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)

import ROOT
import os
from HNL.Tools.helpers import isValidRootFile, makeDirIfNeeded
from random import randrange
nl = 3 if args.region != 'ZZCR' else 4

#
# Set some args for when performing a test
#
if args.isTest:
    if args.sample is None: args.sample = 'DYJetsToLL-M-50'
    if args.year is None: args.year = '2018'
    if args.subJob is None: args.subJob = 0
    args.isChild = True

from HNL.TMVA.mvaVariables import mass_ranges

#
#Load in samples
#
from HNL.Samples.sampleManager import SampleManager
file_list = 'fulllist_'+args.era+args.year if args.customList is None else args.customList
skim_str = 'noskim' if args.noskim else 'Reco'
sample_manager = SampleManager(args.era, args.year, skim_str, file_list, skim_selection=args.selection, region = args.region)
jobs = []
for sample_name in sample_manager.sample_names:
    if 'Data' in sample_name: continue
    sample = sample_manager.getSample(sample_name)
    try:
        for njob in xrange(sample.returnSplitJobs()): 
            jobs += [(sample.name, str(njob))]
    except:
        continue

from HNL.EventSelection.eventCategorization import SUPER_CATEGORIES

# if args.batchSystem == 'HTCondor':
#     output_base = os.path.expandvars(os.path.join('/pnfs/iihe/cms/store/user', '$USER', 'skimmedTuples/HNL')) if not args.isTest else os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'TMVA', 'data', 'testArea'))
# else:
#     output_base = os.path.expandvars(os.path.join('/user/$USER/public/ntuples/HNL')) if not args.isTest else os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'TMVA', 'data', 'testArea'))
output_base = os.path.expandvars(os.path.join('/user/$USER/public/ntuples/HNL')) if not args.isTest else os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'TMVA', 'data', 'testArea'))

if not args.merge:

    #
    # Submit subjobs
    #
    if not args.isChild:
        from HNL.Tools.jobSubmitter import submitJobs

        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'prepareTMVA-'+args.region+'-'+args.year)
        exit(0)


    #
    #Get specific sample for this subjob
    #
    sample = sample_manager.getSample(args.sample)
    chain = sample.initTree(needhcount=False)
    chain.year = args.year
    chain.era = args.era
    chain.is_signal = 'HNL' in sample.name
    chain.selection = args.selection
    chain.strategy = args.strategy
    chain.analysis = args.analysis
    chain.region = args.region

    # Import and create cutter to provide cut flow
    #
    from HNL.EventSelection.bitCutter import CutterCollection
    cutters = CutterCollection(['sideband', 'tight'], chain = chain, categories = 'auto')

    #
    # Create new reduced tree (except if it already exists and overwrite option is not used)
    #
    signal_str = 'Signal' if chain.is_signal else 'Background'

    output_name = os.path.join(output_base, 'TMVA', args.era+args.year, args.region + '-'+args.selection, signal_str, 
                                'tmp_'+sample.output, sample.name + '_' +sample.output+'_'+ str(args.subJob) + '.root')
    makeDirIfNeeded(output_name)

    # if not args.isTest and isValidRootFile(output_name):
    #     log.info('Finished: valid outputfile already exists')
    #     exit(0)

    output_file = ROOT.TFile(output_name ,"RECREATE")

    #
    # Switch off unused branches and create outputTree
    #
    output_tree = {}
    for prompt_str in ['prompt', 'nonprompt', 'sideband']:
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
    new_branches.extend(['fake_weight_lowMassSRloose/F', 'fake_weight_highMassSR/F'])

    from HNL.Tools.makeBranches import makeBranches
    new_vars = {}
    for ip, prompt_str in enumerate(['prompt', 'nonprompt', 'sideband']):
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
    from HNL.EventSelection.event import Event

    #prepare object  and event selection
    event =  Event(sample, chain, sample_manager, is_reco_level=True, selection=args.selection, strategy=args.strategy, region=args.region, analysis=args.analysis, year = args.year, era = args.era, ignore_fakerates=True)

    from HNL.Weights.fakeRateWeights import FakeRateWeighter
    fakerates = {
        'lowMassSRloose' : FakeRateWeighter(chain, region = 'lowMassSRloose').fake_collection,
        'highMassSR' : FakeRateWeighter(chain,region =  'highMassSR').fake_collection,
    }


    for entry in event_range:
        chain.GetEntry(entry)
        if args.isTest: progress(entry - event_range[0], len(event_range))
    
        cutters.cut(True, 'Total', 'sideband')

        event.initEvent()
        # First run sideband for non-prompt
        chain.obj_sel['ele_wp'] = 'FO'
        chain.obj_sel['mu_wp'] = 'FO'
        chain.obj_sel['tau_wp'] = 'FO'
        if not event.passedFilter(cutters.getCutter('sideband'), sample.name, ignoreSignalOverlapRemoval=True): continue
        is_sideband_event = not all(chain.l_istight)

        if len(chain.l_flavor) == chain.l_flavor.count(2): continue

        category = event.event_category.returnCategory()
        super_cat = [sc for sc in SUPER_CATEGORIES.keys() if category in SUPER_CATEGORIES[sc]]

        nprompt = 0
        for index in chain.l_indices:
            if chain._lIsPrompt[index]: nprompt += 1
   
        prompt_str = 'prompt' if nprompt == nl else 'nonprompt'

        weight = event.reweighter.getLumiWeight()

        chain.weight = weight
        chain.entry = entry
        chain.prompt_str = prompt_str
        chain.is_sideband_event = is_sideband_event
        def setVariables(outtree, inchain, fakerates):
            for v in getVariables():
                setattr(outtree, v, getVariableValue(v)(chain))

            outtree.is_signal = chain.is_signal
            outtree.HNL_mass = sample.getMass() if chain.is_signal else randrange(10, 800)
            outtree.HNL_lowmass = sample.getMass() if chain.is_signal else randrange(10, 80)
            outtree.HNL_highmass = sample.getMass() if chain.is_signal else randrange(80, 800)
            outtree.event_weight = weight if not chain.is_signal else 1.
            outtree.eventNb = chain._eventNb
            outtree.entry = entry
            if chain.is_sideband_event: 
                outtree.fake_weight_highMassSR = fakerates['highMassSR'].getFakeWeight()
                outtree.fake_weight_lowMassSRloose = fakerates['lowMassSRloose'].getFakeWeight()
            else:
                outtree.fake_weight_highMassSR = 1.
                outtree.fake_weight_lowMassSRloose = 1.

        for sc in super_cat:
            #Set Variables
            if is_sideband_event:
                setVariables(new_vars['sideband'][sc], chain, fakerates)
                output_tree['sideband'][sc].Fill()
            else:
                if prompt_str == 'prompt':
                    setVariables(new_vars['prompt'][sc], chain, fakerates)    
                    output_tree['prompt'][sc].Fill()
                else:
                    setVariables(new_vars['nonprompt'][sc], chain, fakerates)
                    output_tree['nonprompt'][sc].Fill()


    for prompt_str in ['prompt', 'nonprompt', 'sideband']:
        for c in SUPER_CATEGORIES.keys():
            output_file.cd(prompt_str+'/'+c)
            output_tree[prompt_str][c].Write()

    output_file.Close()

    closeLogger(log)

    cutters.saveCutFlow(output_name)


else:
    #
    # Check subjobs
    #
    from HNL.Tools.jobSubmitter import checkCompletedJobs

    from HNL.Tools.mergeFiles import merge
    from HNL.Tools.makeBranches import makeBranches

    import uproot
    def mergeSignal(out_name, in_names, first_definition=False):
        print "Merging {}".format(out_name.split('/')[-1])
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
        already_defined = not first_definition
        for prompt_str in ['prompt', 'nonprompt']:
            out_trees[prompt_str] = {}
            new_vars[prompt_str] = {}
            for c in SUPER_CATEGORIES.keys():
                out_file.mkdir(prompt_str+'/'+c)
                chain = ROOT.TChain(prompt_str+'/'+c+'/trainingtree')
                for in_name in in_names:
                    chain.Add(in_name)
                chain.SetBranchStatus('event_weight', 0)
                out_trees[prompt_str][c] = chain.CloneTree(0)
                if chain.GetEntries() > 0: 
                    new_vars[prompt_str][c] = makeBranches(out_trees[prompt_str][c], ['event_weight/F'], already_defined = already_defined)
                    already_defined = True

                    for entry in xrange(chain.GetEntries()):
                        chain.GetEntry(entry)
                        new_vars[prompt_str][c].event_weight = num_of_entries['tot'][c]/num_of_entries[chain.HNL_mass][c]
                        out_trees[prompt_str][c].Fill()
                    out_file.cd(prompt_str+'/'+c)
                    out_trees[prompt_str][c].Write()       

        out_file.Close()

    pnfs_base = os.path.expandvars(os.path.join('/pnfs/iihe/cms/store/user', '$USER', 'skimmedTuples/HNL/'))


    signal_mergefiles = output_base+'/TMVA/'+args.era+args.year+'/'+args.region+'-'+args.selection+'/Signal'
    background_mergefiles = output_base+'/TMVA/'+args.era+args.year+'/'+args.region+'-'+args.selection+'/Background'
    background_mergefiles_pnfs = pnfs_base+'TMVA/'+args.era+args.year+'/'+args.region+'-'+args.selection+'/Background'
    merge([signal_mergefiles, background_mergefiles], __file__, jobs, ('sample', 'subJob'), argParser)

    local_base = os.path.expandvars(os.path.join('/pnfs/iihe/cms/store/user', '$USER', 'skimmedTuples/HNL/'))
    makeDirIfNeeded(pnfs_base+'TMVA/'+args.era+args.year+'/'+args.region+'-'+args.selection+'/*')

    if not args.isTest:
        os.system('cp -rf '+output_base+'/TMVA/'+args.era+args.year+'/'+args.region+'-'+args.selection+'/Signal ' + pnfs_base+'TMVA/'+args.era+args.year+'/'+args.region+'-'+args.selection+'/.')
        os.system('cp -rf '+output_base+'/TMVA/'+args.era+args.year+'/'+args.region+'-'+args.selection+'/Background ' + pnfs_base+'TMVA/'+args.era+args.year+'/'+args.region+'-'+args.selection+'/.')

    combined_dir = lambda base, sd : base+'TMVA/'+args.era+args.year+'/'+args.region+'-'+args.selection+'/Combined/'+sd
    makeDirIfNeeded(combined_dir(pnfs_base, 'SingleTree')+'/test')
    makeDirIfNeeded(combined_dir(local_base, 'TwoTrees')+'/test')

    import glob
    all_signal_files = glob.glob(pnfs_base+'TMVA/'+args.era+args.year+'/'+args.region+'-'+args.selection+'/Signal/*root')
    flavor_file = {
        'tauhad' : lambda mass : pnfs_base+'TMVA/'+args.era+args.year+'/'+args.region+'-'+args.selection+'/Signal/HNL-tau-m'+str(mass)+'.root',
        'taulep' : lambda mass : pnfs_base+'TMVA/'+args.era+args.year+'/'+args.region+'-'+args.selection+'/Signal/HNL-tau-m'+str(mass)+'.root',
        'e' : lambda mass : pnfs_base+'TMVA/'+args.era+args.year+'/'+args.region+'-'+args.selection+'/Signal/HNL-e-m'+str(mass)+'.root',
        'mu' : lambda mass : pnfs_base+'TMVA/'+args.era+args.year+'/'+args.region+'-'+args.selection+'/Signal/HNL-mu-m'+str(mass)+'.root'
    }

    bkgr_file = lambda bkgr_name : pnfs_base+'TMVA/'+args.era+args.year+'/'+args.region+'-'+args.selection+'/Background/'+bkgr_name+'.root'
    all_bkgrs = sample_manager.getOutputs()
    all_bkgr_files = ' '.join([bkgr_file(b) for b in all_bkgrs if not 'HNL' in b])
    nonprompts_of_interest = ['XG', 'TT-T+X']


    makeDirIfNeeded(background_mergefiles_pnfs+'/Combined/x')
    os.system('hadd -f ' + background_mergefiles_pnfs+'/Combined/all_bkgr.root '+ all_bkgr_files)

    os.system('hadd -f ' + bkgr_file('Combined/nonprompt_bkgr')+' ' + ' '.join([bkgr_file(n) for n in nonprompts_of_interest]))

    first_pass = True
    for mass_range in mass_ranges:
        if mass_range not in ['lowestmass', 'lowmass']: continue
        for flavor in ['e', 'mu', 'taulep', 'tauhad']:
            all_files_to_merge = []
            for mass in mass_ranges[mass_range]:
                if args.year == '2016pre' and mass == 70: continue
                if isValidRootFile(flavor_file[flavor](mass)): all_files_to_merge.append(flavor_file[flavor](mass))
            mergeSignal(pnfs_base + '/TMVA/'+args.era+args.year+'/'+args.region+'-'+args.selection+'/Signal' +'/'+mass_range+'-'+flavor+'.root', all_files_to_merge, first_pass)
            first_pass = False

            # os.system('hadd -f ' + combined_dir(pnfs_base, 'SingleTree')+'/'+mass_range+'-'+flavor+'.root '+signal_mergefiles+'/'+mass_range+'-'+flavor+'.root ' +background_mergefiles+'/Combined/all_bkgr.root ')


