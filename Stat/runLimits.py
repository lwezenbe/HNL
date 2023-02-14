#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--year',     action='store', nargs='*',       default=None,   help='Select year')
submission_parser.add_argument('--era',     action='store',       default='UL', choices = ['UL', 'prelegacy'],   help='Select era')
submission_parser.add_argument('--masses', type=float, nargs='*',  help='Only run or plot signal samples with mass given in this list')
submission_parser.add_argument('--couplings', nargs='*', type=float,  help='Only run or plot signal samples with coupling squared given in this list')
submission_parser.add_argument('--flavor', action='store', default='',  help='Which coupling should be active?' , choices=['tau', 'e', 'mu', '2l'])
submission_parser.add_argument('--asymptotic',   action='store_true', default=False,  help='Use the -M AsymptoticLimits option in Combine')
submission_parser.add_argument('--blind',   action='store_true', default=False,  help='activate --blind option of combine')
submission_parser.add_argument('--useExistingLimits',   action='store_true', default=False,  help='Dont run combine, just plot')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
submission_parser.add_argument('--strategy',   action='store', default='cutbased',  help='Select the strategy to use to separate signal from background. Traditionally a choice between "custom", "cutbased" and "MVA". If custom or MVA you can add a "-$mvaname" to force it to use a specific mva')
submission_parser.add_argument('--datacards', nargs = '*', default=None, type=str,  help='What final state datacards should be used?')

submission_parser.add_argument('--compareToExternal',   type=str, nargs='*',  help='Compare to a specific experiment')
submission_parser.add_argument('--compareToCards',   type=str, nargs='*',  help='Compare to a specific card if it exists. If you want different selection use "selection/card" otherwise just "card"')
submission_parser.add_argument('--message', type = str, default=None,  help='Add a file with a message in the plotting folder')
submission_parser.add_argument('--tag', type = str, default=None,  help='Add a tag to your output')
submission_parser.add_argument('--masstype', type = str, default=None,  help='Choose what type of limits you want', choices = ['Dirac', 'Majorana'])
submission_parser.add_argument('--displaced', action='store_true', default=False,  help='run limit for displaced sample')
submission_parser.add_argument('--logLevel',  action='store', default='INFO',  help='Log level for logging', nargs='?', choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE'])
submission_parser.add_argument('--batchSystem', action='store',         default='HTCondor',  help='choose batchsystem', choices=['local', 'HTCondor', 'Cream02'])
submission_parser.add_argument('--dryRun',   action='store_true',       default=False,  help='do not launch subjobs, only show them')
submission_parser.add_argument('--subJob',   action='store',            default=None,   help='The number of the subjob for this sample')
submission_parser.add_argument('--isChild',  action='store_true',       default=False,  help='mark as subjob, will never submit subjobs by itself')

argParser.add_argument('--checkLogs', action='store_true', default=False,  help='Add a file with a message in the plotting folder')
argParser.add_argument('--dryplot', action='store_true', default=False,  help='Add a file with a message in the plotting folder')
argParser.add_argument('--submitPlotting', action='store_true', default=False,  help='Submit the fits to condor')
args = argParser.parse_args()

from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)

if args.masstype is None:
    raise RuntimeError("Forgot to specify masstype")

if args.displaced and not args.useExistingLimits and args.couplings is None:
    raise RuntimeError("Please specify couplings for the displaced samples")

import glob
from HNL.Stat.combineTools import runCombineCommand, extractScaledLimitsPromptHNL, extractScaledLimitsDisplacedHNL, makeGraphs, saveGraphs, displaced_mass_threshold
from HNL.Tools.helpers import makeDirIfNeeded, makePathTimeStamped, getObjFromFile
from HNL.Analysis.analysisTypes import signal_couplingsquared
from HNL.Stat.datacardManager import getOutDataCardName
from numpy import sqrt

def runAsymptoticLimit(card_manager, signal_name, cardname):
    datacard = card_manager.getDatacardPath(signal_name, cardname)

    output_folder = datacard.replace('dataCards', 'output').rsplit('/', 1)[0] +'/asymptotic/'+cardname
    if args.tag is not None: output_folder += '-'+args.tag
    makeDirIfNeeded(output_folder+'/x')
    print 'Running Combine for {0}'.format(signal_name)

    if args.blind:
        runCombineCommand('combine -M AsymptoticLimits '+datacard+ ' --run blind', output_folder)
    else:
        runCombineCommand('combine -M AsymptoticLimits '+datacard, output_folder)
    
    print 'Finished running asymptotic limits for {0}'.format(signal_name)
    return

def runHybridNew(card_manager, signal_name, cardname):
    datacard = card_manager.getDatacardPath(signal_name, cardname)

    output_folder = datacard.replace('dataCards', 'output').rsplit('/', 1)[0] +'/hybridNew/'+cardname
    if args.tag is not None: output_folder += '-'+args.tag
    makeDirIfNeeded(output_folder+'/x')
    print 'Running Combine for {0}'.format(signal_name)

    if args.blind:
        runCombineCommand('combine -M HybridNew -t 50 -d'+datacard+ ' --run blind', output_folder)
    else:
        runCombineCommand('combine -M HybridNew -t 50 -d'+datacard, output_folder)
    
    print 'Finished running toy limits for {0}'.format(signal_name)
    return


def runLimit(card_manager, signal_name, cardnames):
    datacard_manager.prepareAllCards(signal_name, cardnames, args.strategy)
    
    if args.asymptotic:
        runAsymptoticLimit(datacard_manager, signal_name, getOutDataCardName(cardnames))
    else:
        runHybridNew(datacard_manager, signal_name, getOutDataCardName(cardnames))

# Create datacard manager
from HNL.Stat.datacardManager import DatacardManager
tag = 'displaced' if args.displaced else 'prompt'
datacard_manager = DatacardManager(args.year, args.era, args.strategy, args.flavor, args.selection, args.masstype)

def returnCouplings(mass):
    if args.couplings is None or mass > displaced_mass_threshold:
        return [signal_couplingsquared[args.flavor][mass]]
    else:
        return [x for x in args.couplings]

from HNL.Analysis.analysisTypes import signal_couplingsquared
if not args.useExistingLimits:

    #Prepare to submit jobs
    if args.submitPlotting:
        jobs = []
        for mass in args.masses:
            couplings = returnCouplings(mass)
            for coupling in couplings:
                jobs += [(mass, coupling, 0)]

        if not args.isChild and not args.checkLogs:
            from HNL.Tools.jobSubmitter import submitJobs
            submitJobs(__file__, ['masses', 'couplings', 'subJob'], jobs, argParser, jobLabel = 'runlimits-{0}-{1}'.format(args.flavor, args.strategy))
            exit(0)

        if args.checkLogs:
            from HNL.Tools.jobSubmitter import checkCompletedJobs, disableShouldMerge
            failed_jobs = checkCompletedJobs(__file__, jobs, argParser)
            if failed_jobs is not None and len(failed_jobs) != 0:   
                should_resubmit = raw_input("Would you like to resubmit the failed jobs? (y/n) \n")
                if should_resubmit == 'y' or should_resubmit == 'Y':
                    print 'resubmitting:'
                    submitJobs(__file__, ('sample', 'subJob'), failed_jobs, argParser, jobLabel = 'skim', resubmission=True)
                else:
                    pass    
                exit(0)
            else:
                remove_logs = raw_input("Would you like to remove log files? (y/n) \n")
                if remove_logs in ['y', 'Y']:
                    from HNL.Tools.jobSubmitter import cleanJobFiles
                    cleanJobFiles(argParser, __file__)
                    disableShouldMerge(__file__, argParser)
            exit(0)

    for mass in args.masses:
        couplings = returnCouplings(mass)
        for coupling in couplings:
            mass_str = str(mass) if not mass.is_integer() else str(int(mass))
            signal_name = 'HNL-'+args.flavor+'-m'+mass_str+'-Vsq'+('{:.1e}'.format(coupling).replace('-', 'm'))+'-'+ ('prompt' if not args.displaced else 'displaced')
            if not datacard_manager.checkMassAvailability(signal_name): continue
            print '\x1b[6;30;42m', 'Processing mN =', str(mass), 'GeV with V2 = ', str(coupling), '\x1b[0m'
            runLimit(datacard_manager, signal_name, args.datacards)

    closeLogger(log)


if args.submitPlotting or args.isChild:
    exit(0)    

compare_dict = {
    'cutbased-AN2017014': 'Replicated AN2017014 selection',
    'cutbased-default': 'Search region binning',
    'cutbased-leptonMVAtop': 'top lepton MVA',
    'MVA-default': 'BDT',
    'custom-default' : '',
}
compare_era_dict = {
    'UL2016pre-2016post-2017-2018': 'Full Run-II',
    'UL2016pre-2016post': '2016',
    'UL2016pre': '2016 Pre VFP',
    'UL2016post': '2016 Post VFP',
    'UL2017': '2017',
    'UL2018': '2018',
}

asymptotic_str = 'asymptotic' if args.asymptotic else ''

year_to_read = args.year[0] if len(args.year) == 1 else '-'.join(args.year)

card = getOutDataCardName(args.datacards) 
method_name = 'runAsymptoticLimits' if args.asymptotic else 'HybridNew'
destination = makePathTimeStamped(os.path.expandvars('$CMSSW_BASE/src/HNL/Stat/data/Results/runAsymptoticLimits/'+args.masstype+'-'+('prompt' if not args.displaced else 'displaced')+'/'+args.strategy+'-'+args.selection+(('-'+args.tag) if args.tag is not None else '')+'/'+args.flavor+'/'+card+'/'+ args.era+year_to_read))

#Make and save graph objects
passed_masses = []
limits = {}
print 'start'
for mass in args.masses:
    mass_str = str(mass) if not mass.is_integer() else str(int(mass))
    couplings = returnCouplings(mass)
    input_folders = []
    for c in couplings:
        tmp_folder = datacard_manager.getDatacardPath('HNL-'+args.flavor+'-m'+mass_str+'-Vsq'+('{:.1e}'.format(c).replace('-', 'm'))+'-'+('prompt' if not args.displaced else 'displaced'), card)
        tmp_folder = tmp_folder.replace('dataCards', 'output').rsplit('/', 1)[0] +'/'+asymptotic_str+'/'+card
        if args.tag is not None: tmp_folder += '-'+args.tag
        tmp_folder += '/higgsCombineTest.AsymptoticLimits.mH120.root'
        input_folders.append(tmp_folder)

    if args.displaced and mass <= displaced_mass_threshold:
        tmp_limit = extractScaledLimitsDisplacedHNL(input_folders, couplings, blind=args.blind)
        #from HNL.Stat.combineTools import drawSignalStrengthPerCouplingDisplaced
        #drawSignalStrengthPerCouplingDisplaced(input_folders, couplings, destination+'/components', 'm'+mass_str, year_to_read, args.flavor, blind=args.blind)
    else:
        tmp_limit = extractScaledLimitsPromptHNL(input_folders[0], couplings[0])
        #from HNL.Stat.combineTools import drawSignalStrengthPerCouplingPrompt
        #drawSignalStrengthPerCouplingPrompt(input_folders[0], couplings[0], destination+'/components', 'm'+mass_str, year_to_read, args.flavor, blind=args.blind)

    if tmp_limit is not None and len(tmp_limit) > 4: 
        passed_masses.append(mass)
        limits[mass] = tmp_limit
        
print 'made graphs'
graphs = makeGraphs(passed_masses, limits=limits)

out_path_base = lambda era, sname, cname, tag : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'output', args.masstype+'-'+('prompt' if not args.displaced else 'displaced'), era, sname+'-'+args.flavor+'-'+asymptotic_str+'/'+cname+(('-'+tag) if tag is not None else ''))
saveGraphs(graphs, out_path_base(args.era+year_to_read, args.strategy +'-'+ args.selection, card, args.tag)+"/limits.root")

print 'loading compare graphs'
#Load in other graph objects to compare
compare_graphs = {}
if args.compareToCards is not None:
    for cc in args.compareToCards:
        if '/' in cc:
            components = cc.split('/')
            era = components[0]
            sname = components[1]
            cname = components[2]
            try:
                tag = components[3]
            except:
                tag =  None
        else:
            sname = cc
            cname = card
            era = args.era
            tag = args.tag

        file_list = []
        # for m in passed_masses:
        #     file_name  = glob.glob(os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'output', args.era+str(year_to_read), sname, args.flavor, 
        #                             'HNL-'+args.flavor+'-m'+str(m), 'shapes', asymptotic_str+'/'+cname+'/*'))
        #     if len(file_name) == 0:
        #         file_list.append(None)
        #     else:
        #         file_list.append(file_name[0])
        era_to_read = era if '201' in era else era+year_to_read
        file_name  = out_path_base('Combined', era_to_read, sname, cname, tag) +'/limits.root'       
        compare_graphs[sname + ' ' +cname+ ' ' + era] = getObjFromFile(file_name, 'expected_central')
print 'loaded all compare graphs'

bkgr_hist = None
tex_names = None
if args.compareToExternal is not None:
    from HNL.Stat.stateOfTheArt import makeGraphList
    bkgr_hist, tex_names = makeGraphList(args.flavor, args.compareToExternal, args.masses)

from HNL.Stat.combineTools import coupling_dict
from HNL.Plotting.plot import Plot
if args.compareToCards is not None:
    for compare_key in compare_graphs.keys():
        compare_sel, compare_reg, compare_era = compare_key.split(' ')
        if bkgr_hist is None:
            bkgr_hist = [compare_graphs[compare_key]]
            tex_names = [compare_era_dict[compare_era]+ ' ' +compare_dict[compare_sel] + ' ' +compare_reg_dict[compare_reg]]
        else:
            bkgr_hist.append(compare_graphs[compare_key])
            tex_names.append(compare_era_dict[compare_era]+ ' ' +compare_dict[compare_sel] + ' ' +compare_reg_dict[compare_reg])

if len(args.year) == 1:
    year = args.year[0]
elif all(['2016' in y for y in args.year]):
    year = '2016'
else:
    year = 'all'

print 'Plotting' 
p = Plot(graphs, tex_names, 'limits', bkgr_hist = bkgr_hist, y_log = True, x_log=True, x_name = 'm_{N} [GeV]', y_name = '|V_{'+coupling_dict[args.flavor]+' N}|^{2}', era = 'UL', year = year)
p.drawBrazilian(output_dir = destination, ignore_bands = args.dryplot)
