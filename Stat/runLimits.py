from HNL.Stat.combineTools import runCombineCommand, extractScaledLimitsPromptHNL, extractRawLimits, makeGraphs
from HNL.Tools.helpers import makeDirIfNeeded, makePathTimeStamped
import ROOT
import numpy as np

#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018'])
argParser.add_argument('--masses', type=int, nargs='*',  help='Only run or plot signal samples with mass given in this list')
argParser.add_argument('--flavor', action='store', default='',  help='Which coupling should be active?' , choices=['tau', 'e', 'mu', '2l'])
argParser.add_argument('--asymptotic',   action='store_true', default=False,  help='Use the -M AsymptoticLimits option in Combine')
argParser.add_argument('--blind',   action='store_true', default=False,  help='activate --blind option of combine')
argParser.add_argument('--useExistingLimits',   action='store_true', default=False,  help='Dont run combine, just plot')
argParser.add_argument('--message', type = str, default=None,  help='Add a file with a message in the plotting folder')
args = argParser.parse_args()

datacards_base = os.path.expandvars('$CMSSW_BASE/src/HNL/Stat/data/dataCards/'+args.year+'/'+args.flavor)
import glob
all_signal = glob.glob(datacards_base+'/*')

def getDataCard(mass):
    datacard_massbase = os.path.join(datacards_base, 'HNL-'+args.flavor+'-m'+str(mass), 'shapes')
    categories = [el for el in glob.glob(datacard_massbase+'/*') if not 'total' in el and not 'Combined' in el and not 'NoTau' in el]
    # categories = [el for el in glob.glob(datacard_massbase+'/*') if not 'total' in el and not 'Combined' in el]
    if args.flavor == 'tau':
        print 'Combining datacards'
        runCombineCommand('combineCards.py '+' '.join(categories)+' > '+datacard_massbase+'/Combined.txt')
        return datacard_massbase+'/Combined.txt'
    else:
        return datacard_massbase+ '/NoTau.txt'


def runAsymptoticLimit(mass):
    datacard = getDataCard(mass)
    output_folder = datacard.replace('dataCards', 'output').rsplit('/', 1)[0] +'/asymptotic'
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


masses = sorted([int(signal.split('/')[-1].split('-m')[-1]) for signal in all_signal])
passed_masses = []
passed_couplings = []
limits = {}

for mass in masses:
    print '\x1b[6;30;42m', 'Processing mN =', str(mass), 'GeV', '\x1b[0m'

    if not args.useExistingLimits:
        if args.asymptotic: runAsymptoticLimit(mass)
        else:
            print 'To be implemented'
            exit(0)


    asymptotic_str = 'asymptotic' if args.asymptotic else ''
    input_folder = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'output', str(args.year), args.flavor, 'HNL-'+args.flavor+'-m'+str(mass), 'shapes', asymptotic_str)
    tmp_coupling = 0.01
    # tmp_coupling = 0.01 if mass <= 80 else .1
    tmp_limit = extractScaledLimitsPromptHNL(input_folder + '/higgsCombineTest.AsymptoticLimits.mH120.root', tmp_coupling)
    if tmp_limit is not None and len(tmp_limit) > 4 and mass != 5: 
        passed_masses.append(mass)
        passed_couplings.append(tmp_coupling)
        limits[mass] = tmp_limit

graphs = makeGraphs(passed_masses, couplings = passed_couplings, limits=limits)

coupling_dict = {'tau':'#tau', 'mu':'#mu', 'e':'e', '2l':'l'}
from HNL.Plotting.plot import Plot
destination = makePathTimeStamped(os.path.expandvars('$CMSSW_BASE/src/HNL/Stat/data/Results/runAsymptoticLimits/'+args.flavor))
p = Plot(graphs, ['2#sigma', '1#sigma', 'expected'], 'expected', y_log = True, x_log=True, x_name = 'm_{N} [GeV]', y_name = 'V_{'+coupling_dict[args.flavor]+' N}^{2}')
p.drawBrazilian(output_dir = destination)

