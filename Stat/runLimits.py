#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--year',     nargs='*',      default=[],   help='Select year', choices=['2016', '2017', '2018'])
submission_parser.add_argument('--masses', type=int, nargs='*',  help='Only run or plot signal samples with mass given in this list')
submission_parser.add_argument('--flavor', action='store', default='',  help='Which coupling should be active?' , choices=['tau', 'e', 'mu', '2l'])
submission_parser.add_argument('--asymptotic',   action='store_true', default=False,  help='Use the -M AsymptoticLimits option in Combine')
submission_parser.add_argument('--blind',   action='store_true', default=False,  help='activate --blind option of combine')
submission_parser.add_argument('--useExistingLimits',   action='store_true', default=False,  help='Dont run combine, just plot')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
submission_parser.add_argument('--strategy',   action='store', default='cutbased',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA'])
submission_parser.add_argument('--datacard', action='store', default='', type=str,  help='What type of analysis do you want to run?', choices=['Combined', 'Ditau', 'NoTau', 'SingleTau', 'TauCombined'])
submission_parser.add_argument('--message', type = str, default=None,  help='Add a file with a message in the plotting folder')
args = argParser.parse_args()

datacards_base = lambda year : os.path.expandvars('$CMSSW_BASE/src/HNL/Stat/data/dataCards/'+year+'/'+args.selection+'/'+args.flavor)
import glob
from HNL.Stat.combineTools import runCombineCommand, extractScaledLimitsPromptHNL, makeGraphs
from HNL.Tools.helpers import makeDirIfNeeded, makePathTimeStamped, getObjFromFile
from HNL.Analysis.analysisTypes import signal_couplingsquared
from numpy import sqrt

def getDataCard(mass, cardname, year):
    datacard_massbase = os.path.join(datacards_base(year), 'HNL-'+args.flavor+'-m'+str(mass), 'shapes')
    return datacard_massbase+ '/'+cardname+'.txt'

def combineSets(mass, year):
    datacard_massbase = os.path.join(datacards_base(year), 'HNL-'+args.flavor+'-m'+str(mass), 'shapes')
    #Combined
    categories = [el for el in glob.glob(datacard_massbase+'/*') if not 'total' in el and not 'Combined' in el and not 'TauCombined' in el]
    runCombineCommand('combineCards.py '+' '.join(categories)+' > '+datacard_massbase+'/Combined.txt')
    #TauCombined
    categories = [el for el in glob.glob(datacard_massbase+'/*') if not 'total' in el and not 'Combined' in el and not 'TauCombined' in el and not 'NoTau' in el]
    runCombineCommand('combineCards.py '+' '.join(categories)+' > '+datacard_massbase+'/TauCombined.txt')

def combineYears(mass, cardname):
    if len(args.year) == 1:
        return
    else:
        datacard_massbase = os.path.join(datacards_base('-'.join(args.year)), 'HNL-'+args.flavor+'-m'+str(mass), 'shapes')
        datacard_path = lambda year : os.path.join(datacards_base(year), 'HNL-'+args.flavor+'-m'+str(mass), 'shapes', cardname+'.txt')
        categories = [datacard_path(y) for y in args.year if os.path.isfile(datacard_path(year))]
        makeDirIfNeeded(datacard_massbase+'/'+cardname+'.txt')
        runCombineCommand('combineCards.py '+' '.join(categories)+' > '+datacard_massbase+'/'+cardname+'.txt')


def runAsymptoticLimit(mass, cardname, year):
    if '-' in year:
        split_year = year.split('-')
    else:
        split_year = [year]

    for y in split_year:
        datacard = getDataCard(mass, cardname, y)
        combineSets(mass, y)
    combineYears(mass, cardname)
    datacard = getDataCard(mass, cardname, year)

    output_folder = datacard.replace('dataCards', 'output').rsplit('/', 1)[0] +'/asymptotic/'+cardname
    print 'Running Combine for mass', str(mass), 'GeV'

    if args.blind:
        runCombineCommand('combine -M AsymptoticLimits '+datacard+ ' --run blind')
    else:
        runCombineCommand('combine -M AsymptoticLimits '+datacard)

    makeDirIfNeeded(output_folder+'/x')
    os.system('scp '+os.path.expandvars('$CMSSW_BASE/src/HNL/Stat/data/output/tmp/*root')+ ' ' +output_folder+'/.')
    os.system('rm '+os.path.expandvars('$CMSSW_BASE/src/HNL/Stat/data/output/tmp/*root'))
    print 'Finished running asymptotic limits for mass', str(mass), 'GeV'
    return

def runHybridNew(mass):
    datacard_massbase = os.path.join(datacards_base, 'HNL-'+args.flavor+'-m'+str(mass), 'shapes')
    #TODO: Finish this
    return datacard_massbase

year_to_read = args.year[0] if len(args.year) == 1 else '-'.join(args.year)
cards_to_read = [args.datacard] if args.datacard != '' else ['Combined', 'Ditau', 'NoTau', 'SingleTau', 'TauCombined']

all_signal = {}
masses_py = {}
for year in args.year:
    all_signal[year] = glob.glob(datacards_base(year)+'/*')
    masses_py[year] = [int(signal.split('/')[-1].split('-m')[-1]) for signal in all_signal[year]]
masses = []
# for year in args.year:
#     masses += (list(set(masses_py[year])-set(masses)))
masses = masses_py['2016']
masses = sorted(masses)

if not args.useExistingLimits:
    for card in cards_to_read:
        print '\x1b[6;30;42m', 'Processing datacard "' +str(card)+ '"', '\x1b[0m'
        for mass in masses:
            if mass not in args.masses: continue
            print '\x1b[6;30;42m', 'Processing mN =', str(mass), 'GeV', '\x1b[0m'

            if args.asymptotic: runAsymptoticLimit(mass, card, year_to_read)
            else:
                print 'To be implemented'
                exit(0)

compare_dict = {
    'cut-based': 'Search regions (tight WP)',
    'Luka': 'Search regions',
    'MVA': 'BDT'
}

for card in cards_to_read:

    passed_masses = []
    passed_couplings = []
    limits = {}
    for mass in masses:
        if mass not in args.masses: continue
        asymptotic_str = 'asymptotic' if args.asymptotic else ''
        input_folder = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'output', str(year_to_read), args.selection, args.flavor, 'HNL-'+args.flavor+'-m'+str(mass), 'shapes', asymptotic_str, card)
        tmp_coupling = sqrt(signal_couplingsquared[args.flavor][mass])

        tmp_limit = extractScaledLimitsPromptHNL(input_folder + '/higgsCombineTest.AsymptoticLimits.mH120.root', tmp_coupling)
        if tmp_limit is not None and len(tmp_limit) > 4 and mass != 5: 
            passed_masses.append(mass)
            passed_couplings.append(tmp_coupling)
            limits[mass] = tmp_limit
            
    graphs = makeGraphs(passed_masses, couplings = passed_couplings, limits=limits)
    compare_graphs = {}

    if args.compareToCards is not None:
        for cc in args.compareToCards:
            if '/' in cc:
                sname, cname = cc.split('/')
            else:
                sname = cc
                cname = card

            file_list = []
            for m in passed_masses:
                file_name  = glob.glob(os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'output', str(year_to_read), sname, args.flavor, 
                                        'HNL-'+args.flavor+'-m'+str(m), 'shapes', asymptotic_str+'/'+cname+'/*'))
                if len(file_name) == 0:
                    file_list.append(None)
                else:
                    file_list.append(file_name[0])
            compare_graphs[sname + ' ' +cname] = makeGraphs(passed_masses, couplings = passed_couplings, limits=None, input_paths = file_list)

    if args.flavor == 'e':
        observed_AN = getObjFromFile(os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'StateOfTheArt', 'limitsElectronMixing.root'), 'observed_promptDecays')
        expected_AN = getObjFromFile(os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'StateOfTheArt', 'limitsElectronMixing.root'), 'expected_central')
        tex_names = ['observed (EXO-17-012)']
    elif args.flavor == 'mu':
        observed_AN = getObjFromFile(os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'StateOfTheArt', 'limitsMuonMixing.root'), 'observed_promptDecays')
        expected_AN = getObjFromFile(os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'StateOfTheArt', 'limitsMuonMixing.root'), 'expected_central')
        tex_names = ['observed (EXO-17-012)']

    else:
        observed_AN = None
        expected_AN = None
        tex_names = None

    print 'graphs', graphs
    print 'compare_graphs', compare_graphs

    coupling_dict = {'tau':'#tau', 'mu':'#mu', 'e':'e', '2l':'l'}
    from HNL.Plotting.plot import Plot
    destination = makePathTimeStamped(os.path.expandvars('$CMSSW_BASE/src/HNL/Stat/data/Results/runAsymptoticLimits/'+args.selection+'/'+args.flavor+'/'+card+'/'+ year_to_read))
    if observed_AN is None and expected_AN is None:
        bkgr_hist = None
    else:
        bkgr_hist = [observed_AN]

    if args.compareToCards is not None:
        for compare_key in compare_graphs.keys():
            compare_sel, compare_reg = compare_key.split(' ')
            if bkgr_hist is None:
                bkgr_hist = [compare_graphs[compare_key][0]]
                tex_names = [compare_dict[compare_sel] + ' ' +compare_reg]
            else:
                bkgr_hist.append(compare_graphs[compare_key][0])
                tex_names.append(compare_dict[compare_sel] + ' ' +compare_reg)

    year = args.year[0] if len(args.year) == 1 else 'all'
    p = Plot(graphs, tex_names, 'limits', bkgr_hist = bkgr_hist, y_log = True, x_log=True, x_name = 'm_{N} [GeV]', y_name = '|V_{'+coupling_dict[args.flavor]+' N}|^{2}', year = year)
    p.drawBrazilian(output_dir = destination)