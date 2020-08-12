#
# Code to make trees to use in training
#

#
# Argument parser and logging
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
argParser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018'], required = True)
argParser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
argParser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
argParser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
argParser.add_argument('--runLocal', action='store_true', default=False,  help='use local resources instead of Cream02')
argParser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
argParser.add_argument('--logLevel',  action='store',      default='INFO',               help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])

argParser.add_argument('--summaryFile', action='store_true', default=False,  help='Create text file that shows all selected arguments')
argParser.add_argument('--customList',  action='store',      default=None,               help='Name of a custom sample list. Otherwise it will use the appropriate noskim file.')
argParser.add_argument('--selection',   action='store', default='cut-based',
    help='Select the strategy to use to separate signal from background', choices=['cut-based', 'AN2017014', 'MVA'])
argParser.add_argument('--region',   action='store', default='baseline', 
    help='apply the cuts of high or low mass regions, use "all" to run both simultaniously', choices=['baseline', 'highMassSR', 'lowMassSR', 'ZZ', 'WZ', 'Conversion'])
argParser.add_argument('--merge',   action='store_true', default=False,  help='merge existing subjob output')


args = argParser.parse_args()

from HNL.Tools.logger import getLogger
log = getLogger(args.logLevel)

import ROOT
import os
from HNL.Tools.helpers import isValidRootFile, makeDirIfNeeded

#
# Set some args for when performing a test
#
if args.isTest:
    if args.sample is None: args.sample = 'DYJetsToLL-M-50'
    if args.year is None: args.year = '2016'
    args.subJob = 0
    args.isChild = True


if not args.merge:
    #
    #Load in samples
    #
    from HNL.Samples.sampleManager import SampleManager
    file_list = 'fulllist_'+str(args.year) if args.customList is None else args.customList
    sample_manager = SampleManager(args.year, 'Reco', file_list)


    #
    #Get specific sample for this subjob
    #
    sample = sample_manager.getSample(args.sample)
    chain = sample.initTree(needhcount=False)
    chain.year = int(args.year)
    chain.is_signal = 'HNL' in sample.name

    # Import and create cutter to provide cut flow
    #
    from HNL.EventSelection.cutter import Cutter
    cutter = Cutter(chain = chain)

    #
    # Create new reduced tree (except if it already exists and overwrite option is not used)
    #
    

    # output_base = os.path.expandvars(os.path.join('/user/$USER/public/ntuples/HNL')) if not args.isTest else os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'SkimTuples', 'data', 'testArea'))
    output_base = os.path.expandvars(os.path.join('/user/$USER/public/ntuples/HNL'))

    signal_str = 'Signal' if chain.is_signal else 'Background'
    output_name = os.path.join(output_base, str(args.year), 'TMVA', signal_str, 'tmp_'+sample.output, sample.output+'_'+sample.name + '_' + str(args.subJob) + '.root')
    makeDirIfNeeded(output_name)

    if not args.isTest and not args.overwrite and isValidRootFile(output_name):
        log.info('Finished: valid outputfile already exists')
        exit(0)

    output_file = ROOT.TFile(output_name ,"RECREATE")

    #
    # Switch off unused branches and create outputTree
    #

    output_tree = ROOT.TTree('trainingtree', 'trainingtree')

    #
    # Make new branches
    #
    new_branches = []
    new_branches.extend(['M3l/F', 'minMos/F', 'mtOther/F'])
    # new_branches.extend(['l1/I', 'l2/I', 'l3/I', 'index_other/I'])
    # new_branches.extend(['l_pt[3]/F', 'l_eta[3]/F', 'l_phi[3]/F', 'l_e[3]/F', 'l_charge[3]/F', 'l_flavor[3]/I', 'l_indices[3]/I'])
    new_branches.extend(['l1_charge/F', 'l2_charge/F', 'l3_charge/F'])
    new_branches.extend(['njets/I'])
    new_branches.extend(['is_signal/O'])

    from HNL.Tools.makeBranches import makeBranches
    new_vars = makeBranches(output_tree, new_branches)

    #
    # Start event loop
    #
    if args.isTest:
        max_events = 4000
        event_range = xrange(max_events) if max_events < len(sample.getEventRange(args.subJob)) else sample.getEventRange(args.subJob)
        # event_range = sample.getEventRange(args.subJob)    

    else:
        event_range = sample.getEventRange(args.subJob)    

    from HNL.Tools.helpers import progress
    from HNL.EventSelection.eventSelector import EventSelector
    from HNL.EventSelection.eventCategorization import EventCategory
    ec = EventCategory(chain)

    #
    # Object ID param
    #
    if args.selection == 'AN2017014':
        object_selection_param = {
            'no_tau' : True,
            'light_algo' : 'cutbased',
            'workingpoint' : 'tight'
        }
    else:
        object_selection_param = {
            'no_tau' : False,
            'light_algo' : 'leptonMVAtop',
            'workingpoint' : 'medium'
        }
    es = EventSelector(args.region, args.selection, object_selection_param, True, ec)

    for entry in event_range:
        chain.GetEntry(entry)
        progress(entry - event_range[0], len(event_range))
    
        cutter.cut(True, 'Total')

        if not es.passedFilter(chain, chain, cutter): continue

        #Set Variables
        new_vars.M3l = chain.M3l
        # print chain.M3l
        new_vars.minMos = chain.minMos
        new_vars.mtOther = chain.mtOther
        new_vars.l1_charge = chain.l_charge[0]
        new_vars.l2_charge = chain.l_charge[1]
        new_vars.l3_charge = chain.l_charge[2]
        new_vars.njets = chain.njets
        new_vars.is_signal = chain.is_signal

        output_tree.Fill()

    output_tree.AutoSave()
        
    output_file.Close()

else:

    from HNL.Tools.mergeFiles import merge

    signal_mergefiles = '/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/'+str(args.year)+'/TMVA/Signal'
    background_mergefiles = '/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/'+str(args.year)+'/TMVA/Background'
    merge(signal_mergefiles)
    merge(background_mergefiles)

    combined_dir = '/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/'+str(args.year)+'/TMVA/Combined'
    makeDirIfNeeded(combined_dir+'/test')

    import glob
    all_signal_files = glob.glob('/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/'+str(args.year)+'/TMVA/Signal/*root')
    all_bkgr_files = '/storage_mnt/storage/user/lwezenbe/public/ntuples/HNL/'+str(args.year)+'/TMVA/Background/*root'
    for signal in all_signal_files:
        signal_name = signal.rsplit('/', 1)[-1]
        os.system('hadd -f '+combined_dir+'/'+signal_name + ' '+signal+' '+all_bkgr_files)

    
