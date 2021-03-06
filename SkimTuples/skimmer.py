#
# Code to perform a skim on samples
#

import ROOT
import os

#
# Argument parser and logging
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
submission_parser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018'], required = True)
submission_parser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
submission_parser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--overwrite', action='store_true', default=False,                help='overwrite if valid output file already exists')
submission_parser.add_argument('--logLevel',  action='store',      default='INFO',               help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])
submission_parser.add_argument('--summaryFile', action='store_true', default=False,  help='Create text file that shows all selected arguments')
submission_parser.add_argument('--genSkim',  action='store_true',      default=False,               help='skim on generator level leptons')
submission_parser.add_argument('--customList',  action='store',      default=None,               help='Name of a custom sample list. Otherwise it will use the appropriate noskim file.')
submission_parser.add_argument('--removeOverlap',  action='store_true',      default=False,               help='Name of a custom sample list. Otherwise it will use the appropriate noskim file.')
submission_parser.add_argument('--skimSelection',  action='store',      default=None,               help='Selection for the skim.', choices=['top', 'TTT', 'Luka', 'Old'])

argParser.add_argument('--checkLogs',  action='store_true',      default=False,               help='Check if all files completed successfully')

args = argParser.parse_args()

#
# Set some args for when performing a test
#
if args.isTest:
    if args.sample is None: args.sample = 'DYJetsToLL-M-50'
    if args.year is None: args.year = '2016'
    args.subJob = 0
    args.isChild = True

#
#Load in samples
#
from HNL.Samples.sampleManager import SampleManager
file_list = 'fulllist_'+str(args.year)+'_mconly' if args.customList is None else args.customList
sample_manager = SampleManager(args.year, 'noskim', file_list, is_test = args.isTest)

#
# Subjobs
#
jobs = []
for sample_name in sample_manager.sample_names:
    sample = sample_manager.getSample(sample_name)
    if sample is None:
        print sample_name, "not found. Will skip this sample"
        continue
    for njob in xrange(sample.split_jobs):
        jobs += [(sample.name, str(njob))]

if not args.checkLogs:
    from HNL.Tools.logger import getLogger, closeLogger
    log = getLogger(args.logLevel)

    #
    # Submit subjobs
    #        
    if not args.isChild and not args.isTest:
        from HNL.Tools.jobSubmitter import submitJobs
        print 'submitjobs'
        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'skim')
        print 'endsubmit'
        
        if args.summaryFile:
            gen_name = 'Gen' if args.genSkim else 'Reco'
            f = open(os.path.expandvars(os.path.join('/user/$USER/public/ntuples/HNL', args.skimSelection, str(args.year), gen_name, 'summary.txt')), 'w')
            for arg in vars(args):
                if not getattr(args, arg): continue
                f.write(arg + '    ' + str(getattr(args, arg)) +  '\n')
            f.close()

        print "Submitted "+str(len(jobs))+" jobs to cream"
        exit(0)

    #
    #Get specific sample for this subjob
    #
    sample = sample_manager.getSample(args.sample)
    chain = sample.initTree()
    chain.year = int(args.year)
    chain.is_signal = 'HNL' in sample.name

    #
    # Import and create cutter to provide cut flow
    #
    from HNL.EventSelection.cutter import Cutter
    cutter = Cutter(chain = chain)

    #
    # Get lumiweight
    #
    from HNL.Weights.lumiweight import LumiWeight
    lw = LumiWeight(sample, sample_manager)

    #
    # Create new reduced tree (except if it already exists and overwrite option is not used)
    #
    from HNL.Tools.helpers import isValidRootFile, makeDirIfNeeded
    gen_name = 'Reco' if not args.genSkim else 'Gen'
    if sample.is_data:
        output_file_name = 'Data'
    elif chain.is_signal: 
        output_file_name = sample.path.split('/')[-1].rsplit('.', 1)[0]
    else:
        output_file_name = sample.path.split('/')[-2]

    if args.batchSystem == 'HTCondor':
        output_base = os.path.expandvars(os.path.join('/pnfs/iihe/cms/store/user', '$USER', 'skimmedTuples/HNL', args.skimSelection)) if not args.isTest else os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'SkimTuples', 'data', 'testArea', args.skimSelection))
    else:
        output_base = os.path.expandvars(os.path.join('/user/$USER/public/ntuples/HNL', args.skimSelection)) if not args.isTest else os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'SkimTuples', 'data', 'testArea', args.skimSelection))
    
    output_name = os.path.join(output_base, str(args.year), gen_name, 'tmp_'+output_file_name, sample.name + '_' + str(args.subJob) + '.root')

    makeDirIfNeeded(output_name)

    if not args.isTest and not args.overwrite and isValidRootFile(output_name):
        log.info('Finished: valid outputfile already exists')
        exit(0)

    output_file = ROOT.TFile(output_name ,"RECREATE")
    output_file.mkdir('blackJackAndHookers')
    output_file.cd('blackJackAndHookers')

    #
    # Switch off unused branches and create outputTree
    #

    delete_branches = ['lhe', 'Lhe', 'ttg', '_ph']
    delete_branches = ['ttg', '_ph']
    #delete_branches.extend(['HLT']) #TODO: For now using pass_trigger, this may need to change
    delete_branches.extend(['tauPOG*2015', 'tau*MvaNew']) #Outdated tau
    delete_branches.extend(['lMuon', 'Smeared', 'prefire'])
    #delete_branches.extend(['_met'])
    delete_branches.extend(['jetNeutral', 'jetCharged', 'jetHF'])
    for i in delete_branches:        chain.SetBranchStatus("*"+i+"*", 0)
    #chain.SetBranchStatus('_met', 1)  #Reactivate met
    #chain.SetBranchStatus('_metPhi', 1)  #Reactivate met
    output_tree = chain.CloneTree(0)

    #
    # Make new branches
    #
    new_branches = []
    # new_branches.extend(['M3l/F', 'minMos/F', 'pt_cone[20]/F', 'mtOther/F'])
    # new_branches.extend(['M3l/F', 'minMos/F', 'mtOther/F'])
    # new_branches.extend(['l1/I', 'l2/I', 'l3/I', 'index_other/I'])
    # new_branches.extend(['l_pt[3]/F', 'l_eta[3]/F', 'l_phi[3]/F', 'l_e[3]/F', 'l_charge[3]/F', 'l_flavor[3]/I', 'l_indices[3]/I', 'l_istight[3]/O'])
    new_branches.extend(['lumiweight/F'])
    # new_branches.extend(['event_category/I'])
    # new_branches.extend(['njets/I', 'nbjets/I'])

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
        
    #prepare object  and event selection
    from HNL.ObjectSelection.objectSelection import objectSelectionCollection
    if args.skimSelection == 'Old':
        object_selection = objectSelectionCollection('HNL', 'cutbased', 'loose', 'loose', 'loose', True, analysis='HNL')
    elif args.skimSelection == 'Luka':
        object_selection = objectSelectionCollection('HNL', 'Luka', 'loose', 'loose', 'loose', False, analysis='HNL')
    elif args.skimSelection == 'TTT':
        object_selection = objectSelectionCollection('HNL', 'TTT', 'loose', 'loose', 'loose', False, analysis='HNL')
    else:
        object_selection = objectSelectionCollection('HNL', 'leptonMVAtop', 'loose', 'loose', 'loose', False, analysis='HNL')
    chain.obj_sel = object_selection

    from HNL.Tools.helpers import progress
    from HNL.EventSelection.eventSelectionTools import calculateThreeLepVariables, calculateGeneralVariables, selectLeptonsGeneral, selectGenLeptonsGeneral
    from HNL.EventSelection.eventCategorization import EventCategory
    for entry in event_range:
        chain.GetEntry(entry)
        progress(entry - event_range[0], len(event_range))
    
        cutter.cut(True, 'Total')

        if args.removeOverlap:
            if 'DYJets' in sample.name and chain._zgEventType>=3: continue
            if sample.name == 'ZG' and chain._hasInternalConversion: continue

        if args.genSkim:
            # if not selectGenLeptonsGeneral(chain, new_vars, 3):      continue
            if not selectGenLeptonsGeneral(chain, chain, 3):      continue
        else:
            selectLeptonsGeneral(chain, chain, 3, cutter = cutter)
            if len(chain.leptons) < 3:       continue

        
        # # ec = EventCategory(new_vars)
        # ec = EventCategory(chain)
        # c = ec.returnCategory()
        # # new_vars.event_category = c
        # chain.event_category = c

        # calculateGeneralVariables(chain, new_vars, is_reco_level=not args.genSkim)
        # calculateThreeLepVariables(chain, new_vars, is_reco_level=not args.genSkim)
        new_vars.lumiweight = lw.getLumiWeight()
        output_tree.Fill()

    # print output_name.split('.')[-1]+'_cutflow.root'
    cutter.saveCutFlow(output_name.split('.')[-1]+'_cutflow.root')


    output_tree.AutoSave()
    # if hcounter is not None:
    #    hcounter.Write()
        
    output_file.Close()

    closeLogger(log)

else:
    from HNL.Tools.jobSubmitter import checkCompletedJobs, submitJobs, cleanJobFiles

    failed_jobs = checkCompletedJobs(__file__, jobs, argParser)
    if failed_jobs is not None and len(failed_jobs) != 0:   
        should_resubmit = raw_input("Would you like to resubmit the failed jobs? (y/n) \n")
        if should_resubmit == 'y' or should_resubmit == 'Y':
            print 'resubmitting:'
            submitJobs(__file__, ('sample', 'subJob'), failed_jobs, argParser, resubmission=True)
        else:
            pass    
        exit(0)