#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--year',     action='store', nargs='*',       default=None,   help='Select year', required=True)
submission_parser.add_argument('--era',     action='store',       default='UL', choices = ['UL', 'prelegacy'],   help='Select era', required=True)
submission_parser.add_argument('--masses', type=int, nargs='*',  help='Only run or plot signal samples with mass given in this list')
submission_parser.add_argument('--flavor', action='store', default='',  help='Which coupling should be active?' , choices=['tau', 'e', 'mu', '2l'])
submission_parser.add_argument('--asymptotic',   action='store_true', default=False,  help='Use the -M AsymptoticLimits option in Combine')
submission_parser.add_argument('--blind',   action='store_true', default=False,  help='activate --blind option of combine')
submission_parser.add_argument('--useExistingLimits',   action='store_true', default=False,  help='Dont run combine, just plot')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
submission_parser.add_argument('--strategy',   action='store', default='cutbased',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA', 'custom'])
submission_parser.add_argument('--datacard', action='store', default='', type=str,  help='What type of analysis do you want to run?', choices=['MaxOneTau', 'Combined', 'Ditau', 'NoTau', 'SingleTau', 'TauFinalStates', 'EEE-Mu'])
submission_parser.add_argument('--compareToCards',   type=str, nargs='*',  help='Compare to a specific card if it exists. If you want different selection use "selection/card" otherwise just "card"')
submission_parser.add_argument('--lod',   type=str,  help='"Level of detail": Describes how binned you want you analysis categories to be.', choices = ['analysis', 'super'])
submission_parser.add_argument('--message', type = str, default=None,  help='Add a file with a message in the plotting folder')
submission_parser.add_argument('--tag', type = str, default=None,  help='Add a file with a message in the plotting folder')
argParser.add_argument('--dryplot', action='store_true', default=False,  help='Add a file with a message in the plotting folder')
args = argParser.parse_args()


import glob
from HNL.Stat.combineTools import runCombineCommand, extractScaledLimitsPromptHNL, makeGraphs, saveGraphs
from HNL.Tools.helpers import makeDirIfNeeded, makePathTimeStamped, getObjFromFile
from HNL.Analysis.analysisTypes import signal_couplingsquared
from numpy import sqrt

def runAsymptoticLimit(card_manager, signal_name, cardname):
    datacard = card_manager.getDatacardPath(signal_name, cardname)
    print datacard

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

def runHybridNew(mass):
    datacard_massbase = os.path.join(datacards_base, 'HNL-'+args.flavor+'-m'+str(mass), 'shapes')
    #TODO: Finish this
    return datacard_massbase

cards_to_read = [args.datacard] if args.datacard != '' else ['NoTau', 'SingleTau']

# Create datacard manager
from HNL.Stat.datacardManager import DatacardManager
datacard_manager = DatacardManager(args.year, args.era, args.strategy, args.flavor, args.selection)

if not args.useExistingLimits:
    for card in cards_to_read:
        print '\x1b[6;30;42m', 'Processing datacard "' +str(card)+ '"', '\x1b[0m'
        for mass in args.masses:
            if not datacard_manager.checkMassAvailability(mass): continue
            print '\x1b[6;30;42m', 'Processing mN =', str(mass), 'GeV', '\x1b[0m'
            signal_name = 'HNL-'+args.flavor+'-m'+str(mass)
            datacard_manager.prepareAllCards(signal_name, card, args.lod, args.strategy)

            if args.asymptotic: runAsymptoticLimit(datacard_manager, signal_name, card)
            else:
                print 'To be implemented'
                exit(0)

compare_dict = {
    'cutbased-AN2017014': 'Replicated AN2017014 selection',
    'cutbased-default': 'Search region binning',
    'cutbased-leptonMVAtop': 'top lepton MVA',
    'MVA-default': 'BDT',
    'custom-default' : '',
}

asymptotic_str = 'asymptotic' if args.asymptotic else ''

year_to_read = args.year[0] if len(args.year) == 1 else '-'.join(args.year)
for card in cards_to_read:

    passed_masses = []
    passed_couplings = []
    limits = {}
    for mass in args.masses:
        if not datacard_manager.checkMassAvailability(mass): continue
        from HNL.Stat.datacardManager import getRegionFromMass
        input_folder = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'output', args.era+str(year_to_read), args.selection+'-'+getRegionFromMass(mass), args.flavor, 'HNL-'+args.flavor+'-m'+str(mass), 'shapes', args.strategy, asymptotic_str, card+(('-'+args.tag) if args.tag is not None else ''))
        tmp_coupling = sqrt(signal_couplingsquared[args.flavor][mass])

        tmp_limit = extractScaledLimitsPromptHNL(input_folder + '/higgsCombineTest.AsymptoticLimits.mH120.root', tmp_coupling)
        if tmp_limit is not None and len(tmp_limit) > 4 and mass != 5: 
            passed_masses.append(mass)
            passed_couplings.append(tmp_coupling)
            limits[mass] = tmp_limit
            
    graphs = makeGraphs(passed_masses, couplings = passed_couplings, limits=limits)

    out_path_base = lambda sample, era, sname, cname, tag : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'output', era, sname, args.flavor, 
                                        sample, 'shapes', asymptotic_str+'/'+cname+(('-'+tag) if tag is not None else ''))
    saveGraphs(graphs, out_path_base('Combined', args.era+year_to_read, args.strategy +'-'+ args.selection, card, args.tag)+"/limits.root")

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

    if args.flavor == 'e':
        #observed_AN = getObjFromFile(os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'StateOfTheArt', 'limitsElectronMixing.root'), 'observed_promptDecays')
        observed_AN = None
        expected_AN = getObjFromFile(os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'StateOfTheArt', 'limitsElectronMixing.root'), 'expected_central')
    #    tex_names = ['observed (EXO-17-012)', 'expected (EXO-17-012)']
        tex_names = ['expected (EXO-17-012)']
    elif args.flavor == 'mu':
        #observed_AN = getObjFromFile(os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'StateOfTheArt', 'limitsMuonMixing.root'), 'observed_promptDecays')
        observed_AN = None
        expected_AN = getObjFromFile(os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'StateOfTheArt', 'limitsMuonMixing.root'), 'expected_central')
        #tex_names = ['observed (EXO-17-012)', 'expected (EXO-17-012)']
        tex_names = ['expected (EXO-17-012)']
    else:
        observed_AN = None
        expected_AN = None
        tex_names = None


    coupling_dict = {'tau':'#tau', 'mu':'#mu', 'e':'e', '2l':'l'}
    from HNL.Plotting.plot import Plot
    destination = makePathTimeStamped(os.path.expandvars('$CMSSW_BASE/src/HNL/Stat/data/Results/runAsymptoticLimits/'+args.strategy+'-'+args.selection+(('-'+args.tag) if args.tag is not None else '')+'/'+args.flavor+'/'+card+'/'+ args.era+year_to_read))
    if (observed_AN is None and expected_AN is None) or args.dryplot:
        bkgr_hist = None
    else:
        #bkgr_hist = [observed_AN, expected_AN]
        bkgr_hist = [expected_AN]

    if args.compareToCards is not None:
        for compare_key in compare_graphs.keys():
            compare_sel, compare_reg, compare_era = compare_key.split(' ')
            if bkgr_hist is None:
                bkgr_hist = [compare_graphs[compare_key]]
                tex_names = [compare_era+ ' ' +compare_dict[compare_sel] + ' ' +compare_reg]
            else:
                bkgr_hist.append(compare_graphs[compare_key])
                tex_names.append(compare_era+ ' ' +compare_dict[compare_sel] + ' ' +compare_reg)

    if len(args.year) == 1:
        year = args.year[0]
    elif all(['2016' in y for y in args.year]):
        year = '2016'
    else:
        year = 'all'
    
    p = Plot(graphs, tex_names, 'limits', bkgr_hist = bkgr_hist, y_log = True, x_log=True, x_name = 'm_{N} [GeV]', y_name = '|V_{'+coupling_dict[args.flavor]+' N}|^{2}', era = 'UL', year = year)
    p.drawBrazilian(output_dir = destination, ignore_bands = args.dryplot)
