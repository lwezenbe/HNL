#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--year',     action='store', nargs='*',       default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='UL', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--mass', type=float,  help='Only run or plot signal sample with mass given in this list')
submission_parser.add_argument('--massRange', nargs='*', type=float,  help='masses to include in global fit')
submission_parser.add_argument('--flavor', action='store', default='',  help='Which coupling should be active?' , choices=['tau', 'e', 'mu', '2l'])
submission_parser.add_argument('--blind',   action='store_true', default=False,  help='activate --blind option of combine')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
submission_parser.add_argument('--strategy',   action='store', default='cutbased',  help='Select the strategy to use to separate signal from background. Traditionally a choice between "custom", "cutbased" and "MVA". If custom or MVA you can add a "-$mvaname" to force it to use a specific mva')
submission_parser.add_argument('--datacards', nargs = '*', default=None, type=str,  help='What final state datacards should be used?')

submission_parser.add_argument('--masstype', type = str, default=None,  help='Choose what type of limits you want', choices = ['Dirac', 'Majorana'])
submission_parser.add_argument('--displaced', action='store_true', default=False,  help='run limit for displaced sample')
submission_parser.add_argument('--logLevel',  action='store', default='INFO',  help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--dryRun',   action='store_true',       default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--subJob',   action='store',            default="0",   help='The number of the subjob for this sample')
submission_parser.add_argument('--isChild',  action='store_true',   default=False,  help='mark as subjob, will never submit subjobs by itself')

submission_parser.add_argument('--ntoys',  action='store',   type=int,    default=100,  help='mark as subjob, will never submit subjobs by itself')

argParser.add_argument('--checkLogs', action='store_true', default=False,  help='Add a file with a message in the plotting folder')
argParser.add_argument('--makePlots', action='store_true', default=False,  help='Make plots')
argParser.add_argument('--dryplot', action='store_true', default=False,  help='Add a file with a message in the plotting folder')
argParser.add_argument('--submit', action='store_true', default=False,  help='Submit the fits to condor')
args = argParser.parse_args()

from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)

# Create datacard manager for main mass
from HNL.Stat.datacardManager import DatacardManager, getOutDataCardName
tag = 'displaced' if args.displaced else 'prompt'
datacard_manager = DatacardManager(args.year, args.era, args.strategy, args.flavor, args.selection, args.masstype)

from HNL.Analysis.analysisTypes import signal_couplingsquared
coupling = signal_couplingsquared[args.flavor][args.mass]
mass_str = str(args.mass) if not args.mass.is_integer() else str(int(args.mass))
signal_name = 'HNL-'+args.flavor+'-m'+str(mass_str)+'-Vsq'+('{:.1e}'.format(coupling).replace('-', 'm'))+'-'+ ('prompt' if not args.displaced else 'displaced')

from HNL.Stat.combineTools import runCombineCommand, displaced_mass_threshold
if len(args.datacards) == 1 and '/' in args.datacards[0]:
    datacard = args.datacards[0]
    cardname = datacard.rsplit('/', 1)[1].split('.')[0]
else:
    datacard_manager.prepareAllCards(signal_name, args.datacards, args.strategy)
    cardname = getOutDataCardName(args.datacards)
    datacard = datacard_manager.getDatacardPath(signal_name, cardname)

out_folder =  datacard.replace('dataCards', 'runGlobalSignificance').rsplit('/', 1)[0] +'/'+signal_name

def getJobRanges():
    max_n_toys_per_job = 50.
    import numpy as np
    njobs = int(np.ceil(float(args.ntoys/max_n_toys_per_job)))
    job_ranges = []
    for i in range(njobs):
        job_ranges.append(range(int(i*max_n_toys_per_job+1), int((i+1)*max_n_toys_per_job+1)))
    return job_ranges

if args.submit and not args.isChild:
    jobs = []
    job_ranges = getJobRanges()
    for mass in args.massRange:
        for sub_job in range(len(job_ranges)):
            jobs += [(mass, sub_job)]


if not args.makePlots:
    #Prepare baseline to be used in each subjob
    if not args.isChild:
        runCombineCommand('text2workspace.py '+datacard+ ' -o ws-{0}.root'.format(args.mass), out_folder)
        
        #First run the significance to get the baseline
        runCombineCommand('combine ws-{0}.root -M Significance'.format(args.mass), out_folder)
        
        #Generate background-only toys
        runCombineCommand('combine ../ws-{0}.root -M GenerateOnly --toysFrequentist -m {1} -t {2} --saveToys --expectSignal=0'.format(args.mass, args.mass, args.ntoys), out_folder+'/toys')
    
    if args.submit and not args.isChild:
        from HNL.Tools.jobSubmitter import submitJobs
        submitJobs(__file__, ['massRange', 'subJob'], jobs, argParser, jobLabel='runGlobalSignificance') 
        exit(0)
    
    #For each mass point in range, create a workspace and run the fits
    toy_range = range(1, args.ntoys+1)
    if args.isChild:
        job_ranges = getJobRanges()
        toy_range = job_ranges[int(args.subJob)]

    for mass in args.massRange:
        mass_coupling = signal_couplingsquared[args.flavor][mass]
        mass_name = 'HNL-'+args.flavor+'-m'+str(int(mass))+'-Vsq'+('{:.1e}'.format(mass_coupling).replace('-', 'm'))+'-'+ ('prompt' if not args.displaced else 'displaced')
        datacard_manager.prepareAllCards(mass_name, args.datacards, args.strategy)
        mass_datacard = datacard_manager.getDatacardPath(mass_name, cardname)
        runCombineCommand('text2workspace.py '+mass_datacard+ ' -o ws-{0}-{1}.root'.format(mass, args.subJob), out_folder+'/'+str(mass))
   
        #For each toy, run background-only fit
        for i in toy_range:
            print 'Running toy #{0}'.format(i)
            runCombineCommand('combine ws-{0}-{3}.root -M Significance -m {0} -n toy_{1} -D ../toys/higgsCombineTest.GenerateOnly.mH{2}.123456.root:toys/toy_{1}'.format(mass, i, int(args.mass), args.subJob), out_folder+'/'+str(mass))
    closeLogger(log)

else:
    from HNL.Tools.jobSubmitter import checkAndResubmit
    checkAndResubmit(__file__, jobs, ['massRange', 'subJob'], argParser)

    import ROOT
    def extractSignificance(input_file_path):
        in_file = ROOT.TFile(input_file_path, 'read')
        tree = in_file.Get('limit')
        tree.GetEntry(0)
        return tree.limit  

    local_value = extractSignificance(out_folder+'/higgsCombineTest.Significance.mH120.root') 
    
    nmore = 0
    ntot = 0
    for mass in args.massRange:
        for i in range(1, args.ntoys+1):
            try:
                test_value = extractSignificance(out_folder+'/'+str(mass)+'/higgsCombinetoy_{0}.Significance.mH{1}.root'.format(i, int(mass)))
                ntot += 1.
                if test_value >= local_value:
                    nmore += 1.
            except:
                continue

    print 'Local significance: \t', local_value
    print 'Global pvalue: \t\t', nmore/ntot, '\t\t ({0} out of {1})'.format(nmore, ntot) 
    print 'Global significance: \t', ROOT.RooStats.PValueToSignificance(nmore/ntot)
