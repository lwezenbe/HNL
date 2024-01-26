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
submission_parser.add_argument('--method',   action='store', default='',  help='What method should we use?', choices = ['asymptotic', 'hybrid', 'significance', 'covariance', 'impact', 'gof', 'postfit', 'groupedimpact'])
submission_parser.add_argument('--blind',   action='store_true', default=False,  help='activate --blind option of combine')
submission_parser.add_argument('--useExistingLimits',   action='store_true', default=False,  help='Dont run combine, just plot')
submission_parser.add_argument('--selection',   action='store', default='default',  help='Select the type of selection for objects', choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
submission_parser.add_argument('--strategy',   action='store', default='cutbased',  help='Select the strategy to use to separate signal from background. Traditionally a choice between "custom", "cutbased" and "MVA". If custom or MVA you can add a "-$mvaname" to force it to use a specific mva')
submission_parser.add_argument('--datacards', nargs = '*', default=None, type=str,  help='What final state datacards should be used?')
submission_parser.add_argument('--outputfolder', default=None, type=str,  help='Define a custom outputfolder')
submission_parser.add_argument('--inputTag', type = str, default=None,  help='Add a tag to your input')
submission_parser.add_argument('--regions', nargs = '*', default=None, type=str,  help='If you want a specific region, define here')
submission_parser.add_argument('--searchregions', nargs = '*', default=None, type=str,  help='If you want a specific signal region, define here')

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
argParser.add_argument('--xseclimit', action='store_true', default=False,  help='save limits as function of xsec')
args = argParser.parse_args()

from HNL.Tools.logger import getLogger, closeLogger
log = getLogger(args.logLevel)

if args.masstype is None:
    raise RuntimeError("Forgot to specify masstype")

if args.displaced and not args.useExistingLimits and args.couplings is None:
    raise RuntimeError("Please specify couplings for the displaced samples")

import glob
from HNL.Stat.combineTools import runCombineCommand, extractScaledLimitsPromptHNL, extractScaledLimitsDisplacedHNL, makeGraphs, saveGraphs, displaced_mass_threshold, saveTextFiles, saveJsonFile
from HNL.Tools.helpers import makeDirIfNeeded, makePathTimeStamped, getObjFromFile
from HNL.Analysis.analysisTypes import signal_couplingsquared
from HNL.Stat.datacardManager import getOutDataCardName
from numpy import sqrt

def getOutputFolder(base_folder):
    if args.outputfolder is None:
        output_folder = base_folder
        if args.tag is not None: output_folder += '-'+args.tag
    else:
        output_folder = '/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/'+args.outputfolder
    return output_folder

def runAsymptoticLimit(datacard, cardname):
#    datacard = card_manager.getDatacardPath(signal_name, cardname)

    output_folder = getOutputFolder(datacard.replace('dataCards', 'output').rsplit('/', 1)[0] +'/asymptotic/'+cardname)
    makeDirIfNeeded(output_folder+'/x')

    runCombineCommand('text2workspace.py '+datacard+ ' -o ws.root', output_folder)
    if args.blind:
        runCombineCommand('combine ws.root -M AsymptoticLimits --run blind', output_folder)
    else:
        runCombineCommand('combine ws.root -M AsymptoticLimits', output_folder)

    return

def runHybridNew(datacard, cardname):
#    datacard = card_manager.getDatacardPath(signal_name, cardname)

    output_folder = getOutputFolder(datacard.replace('dataCards', 'output').rsplit('/', 1)[0] +'/hybridNew/'+cardname)
    makeDirIfNeeded(output_folder+'/x')

    if args.blind:
        runCombineCommand('combine -M HybridNew -t 50 -d'+datacard+ ' --run blind', output_folder)
    else:
        runCombineCommand('combine -M HybridNew -t 50 -d'+datacard, output_folder)
    
    return

def runSignificance(datacard, cardname):
#    datacard = card_manager.getDatacardPath(signal_name, cardname)

    output_folder = getOutputFolder(datacard.replace('dataCards', 'output').rsplit('/', 1)[0] +'/Significance/'+cardname)
    makeDirIfNeeded(output_folder+'/x')

    if args.blind:
        runCombineCommand('combine -M Significance -t 50 -d'+datacard+ ' --run blind', output_folder)
    else:
        #runCombineCommand('combine -M Significance -t 100 -d'+datacard, output_folder)
        #runCombineCommand('combine -M Significance -d'+datacard, output_folder)
        runCombineCommand('combine -M HybridNew -d '+datacard+ ' --LHCmode LHC-significance  --saveToys --fullBToys --saveHybridResult -T 100 -i 5', output_folder)
    
    return

def runImpacts(datacard, cardname):
    output_folder = getOutputFolder(datacard.replace('dataCards', 'output').rsplit('/', 1)[0] +'/Impacts/'+cardname)
    #extra_conditions = '--rMin 0 --rMax 5'
    #extra_conditions = '--rMin 0 --rMax 5 --robustFit=1'
    #extra_conditions = '--rMin -10 '
    #extra_conditions = '--rMin -10  --robustFit=1 '
    extra_conditions = '--rMin -1 --rMax 5 --cminDefaultMinimizerStrategy 0'
    #extra_conditions = '--rMin -2 --rMax 2 --cminDefaultMinimizerStrategy 0'
    #extra_conditions = '--rMin -10 --rMax 5 --cminDefaultMinimizerStrategy 0'
    #extra_conditions = '--robustFit=1 '
    #extra_conditions = '--robustFit=1 --stepSize=0.05 --setRobustFitAlgo migrad'
    print datacard
    runCombineCommand(  'text2workspace.py '+datacard+ ' -o ws.root ; '
                        + 'combineTool.py -M Impacts -d ws.root -m 100 {0} --doInitialFit --expectSignal 0; '.format(extra_conditions)
                        + 'combineTool.py -M Impacts -d ws.root -m 100 {0} --doFits --parallel 10 --expectSignal 0; '.format(extra_conditions)
                        + 'combineTool.py -M Impacts -d ws.root -m 100 {0} -o impacts.json --expectSignal 0; '.format(extra_conditions)
                        + 'plotImpacts.py -i  impacts.json -o  impacts', 
                    output_folder)
    print output_folder
    #runCombineCommand( 'plotImpacts.py -i  impacts.json -o  impacts', output_folder)
    
    from HNL.Tools.helpers import getPublicHTMLfolder, makeDirIfNeeded
    public_html = getPublicHTMLfolder(output_folder)
    makeDirIfNeeded(public_html+'/x')
    os.system('scp '+output_folder+'/impacts.pdf '+public_html+'/impacts.pdf')
    return

#def runGroupedImpacts(datacard, cardname):
#    output_folder = getOutputFolder(datacard.replace('dataCards', 'output').rsplit('/', 1)[0] +'/GroupedImpacts/'+cardname)
#    
#    command = ''
#    # initial fit:
#    command += 'combine --saveWorkspace --redefineSignalPOIs r --setParameters r=1 -M MultiDimFit -d {0} -n hnl.postfit ; '.format(datacard)
#    # scan 1:
#    command += 'combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit --algo grid --snapshotName MultiDimFit --setParameterRanges r=-1,1 --redefineSignalPOIs r --setParameters r=1 ; '
#
#    # increasingly freezing groups:
#    command += 'combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit --algo grid --snapshotName MultiDimFit --setParameterRanges r=-1,1 --redefineSignalPOIs r --setParameters r=1 --freezeNuisanceGroups luminosity -n hnl.freeze_lumi; '
#    command += 'combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit --algo grid --snapshotName MultiDimFit --setParameterRanges r=-1,1 --redefineSignalPOIs r --setParameters r=1 --freezeNuisanceGroups luminosity,theory -n hnl.freeze_lumi_theory; '
#    command += 'combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit --algo grid --snapshotName MultiDimFit --setParameterRanges r=-1,1 --redefineSignalPOIs r --setParameters r=1 --freezeNuisanceGroups luminosity,theory,trigger -n hnl.freeze_lumi_theory_trigger; '
#    command += 'combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit --algo grid --snapshotName MultiDimFit --setParameterRanges r=-1,1 --redefineSignalPOIs r --setParameters r=1 --freezeNuisanceGroups luminosity,theory,trigger,WZ_norm -n hnl.freeze_lumi_theory_trigger_WZ; '
#    command += 'combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit --algo grid --snapshotName MultiDimFit --setParameterRanges r=-1,1 --redefineSignalPOIs r --setParameters r=1 --freezeNuisanceGroups luminosity,theory,trigger,WZ_norm,ZZ_norm -n hnl.freeze_lumi_theory_trigger_WZ_ZZ; '
#    command += 'combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit --algo grid --snapshotName MultiDimFit --setParameterRanges r=-1,1 --redefineSignalPOIs r --setParameters r=1 --freezeNuisanceGroups luminosity,theory,trigger,WZ_norm,ZZ_norm,conv_norm -n hnl.freeze_lumi_theory_trigger_WZ_ZZ_conv; '
#    command += 'combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit --algo grid --snapshotName MultiDimFit --setParameterRanges r=-1,1 --redefineSignalPOIs r --setParameters r=1 --freezeNuisanceGroups luminosity,theory,trigger,WZ_norm,ZZ_norm,conv_norm,prompt_norm -n hnl.freeze_lumi_theory_trigger_WZ_ZZ_conv_otherprompt; '
#    command += 'combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit --algo grid --snapshotName MultiDimFit --setParameterRanges r=-1,1 --redefineSignalPOIs r --setParameters r=1 --freezeNuisanceGroups luminosity,theory,trigger,WZ_norm,ZZ_norm,conv_norm,prompt_norm,nonprompt_light -n hnl.freeze_lumi_theory_trigger_WZ_ZZ_conv_otherprompt_nonpromptlight; '
#    command += 'combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit --algo grid --snapshotName MultiDimFit --setParameterRanges r=-1,1 --redefineSignalPOIs r --setParameters r=1 --freezeNuisanceGroups luminosity,theory,trigger,WZ_norm,ZZ_norm,conv_norm,prompt_norm,nonprompt_light,nonprompt_tau -n hnl.freeze_lumi_theory_trigger_WZ_ZZ_conv_otherprompt_nonpromptlight_nonprompttau; '
#    command += 'combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit --algo grid --snapshotName MultiDimFit --setParameterRanges r=-1,1 --redefineSignalPOIs r --setParameters r=1 --freezeNuisanceGroups luminosity,theory,trigger,WZ_norm,ZZ_norm,conv_norm,prompt_norm,nonprompt_light,nonprompt_tau,electron -n hnl.freeze_lumi_theory_trigger_WZ_ZZ_conv_otherprompt_nonpromptlight_nonprompttau_electron; '
#    command += 'combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit --algo grid --snapshotName MultiDimFit --setParameterRanges r=-1,1 --redefineSignalPOIs r --setParameters r=1 --freezeNuisanceGroups luminosity,theory,trigger,WZ_norm,ZZ_norm,conv_norm,prompt_norm,nonprompt_light,nonprompt_tau,electron,muon -n hnl.freeze_lumi_theory_trigger_WZ_ZZ_conv_otherprompt_nonpromptlight_nonprompttau_electron_muon; '
#    command += 'combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit --algo grid --snapshotName MultiDimFit --setParameterRanges r=-1,1 --redefineSignalPOIs r --setParameters r=1 --freezeNuisanceGroups luminosity,theory,trigger,WZ_norm,ZZ_norm,conv_norm,prompt_norm,nonprompt_light,nonprompt_tau,electron,muon,tau -n hnl.freeze_lumi_theory_trigger_WZ_ZZ_conv_otherprompt_nonpromptlight_nonprompttau_electron_muon_tau; '
#    command += 'combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit --algo grid --snapshotName MultiDimFit --setParameterRanges r=-1,1 --redefineSignalPOIs r --setParameters r=1 --freezeNuisanceGroups luminosity,theory,trigger,WZ_norm,ZZ_norm,conv_norm,prompt_norm,nonprompt_light,nonprompt_tau,electron,muon,tau,jets -n hnl.freeze_lumi_theory_trigger_WZ_ZZ_conv_otherprompt_nonpromptlight_nonprompttau_electron_muon_tau_jets; '
#    command += 'combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit --algo grid --snapshotName MultiDimFit --setParameterRanges r=-1,1 --redefineSignalPOIs r --setParameters r=1 --freezeNuisanceGroups allConstrainedNuisances -n hnl.freeze_all; '
#
#    # plot
#    command += 'plot1DScan.py higgsCombineTest.MultiDimFit.mH120.root --main-label "Total Uncert." --POI r --others'
#    command += ' higgsCombinehnl.freeze_lumi.MultiDimFit.mH120.root:"freeze lum":13'
#    command += ' higgsCombinehnl.freeze_lumi_theory.MultiDimFit.mH120.root:"freeze lum_theo":12'
#    command += ' higgsCombinehnl.freeze_lumi_theory_trigger.MultiDimFit.mH120.root:"freeze lum_theo_trig":11'
#    command += ' higgsCombinehnl.freeze_lumi_theory_trigger_WZ.MultiDimFit.mH120.root:"freeze lum_theo_trig_WZ":10'
#    command += ' higgsCombinehnl.freeze_lumi_theory_trigger_WZ_ZZ.MultiDimFit.mH120.root:"freeze lum_theo_trig_WZ_ZZ":9'
#    command += ' higgsCombinehnl.freeze_lumi_theory_trigger_WZ_ZZ_conv.MultiDimFit.mH120.root:"freeze lum_theo_trig_WZ_ZZ_conv":8'
#    command += ' higgsCombinehnl.freeze_lumi_theory_trigger_WZ_ZZ_conv_otherprompt.MultiDimFit.mH120.root:"freeze lum_theo_trig_WZ_ZZ_conv_p":7'
#    command += ' higgsCombinehnl.freeze_lumi_theory_trigger_WZ_ZZ_conv_otherprompt_nonpromptlight.MultiDimFit.mH120.root:"freeze lum_theo_trig_WZ_ZZ_conv_p_npl":6'
#    command += ' higgsCombinehnl.freeze_lumi_theory_trigger_WZ_ZZ_conv_otherprompt_nonpromptlight_nonprompttau.MultiDimFit.mH120.root:"freeze lum_theo_trig_WZ_ZZ_conv_p_npl_npt":5'
#    command += ' higgsCombinehnl.freeze_lumi_theory_trigger_WZ_ZZ_conv_otherprompt_nonpromptlight_nonprompttau_electron.MultiDimFit.mH120.root:"freeze lum_theo_trig_WZ_ZZ_conv_p_npl_npt_e":4'
#    command += ' higgsCombinehnl.freeze_lumi_theory_trigger_WZ_ZZ_conv_otherprompt_nonpromptlight_nonprompttau_electron_muon.MultiDimFit.mH120.root:"freeze lum_theo_trig_WZ_ZZ_conv_p_npl_npt_e_m":3'
#    command += ' higgsCombinehnl.freeze_lumi_theory_trigger_WZ_ZZ_conv_otherprompt_nonpromptlight_nonprompttau_electron_muon_tau.MultiDimFit.mH120.root:"freeze lum_theo_trig_WZ_ZZ_conv_p_npl_npt_e_m_t":2'
#    command += ' higgsCombinehnl.freeze_lumi_theory_trigger_WZ_ZZ_conv_otherprompt_nonpromptlight_nonprompttau_electron_muon_tau_jets.MultiDimFit.mH120.root:"freeze lum_theo_trig_WZ_ZZ_conv_p_npl_npt_e_m_t_j":1'
#    #command += ' higgsCombinehnl.freeze_all.MultiDimFit.mH120.root:"freeze all":1'
#    command += ' --output breakdown --y-max 10 --y-cut 40 --breakdown "lumi,theory,trig,WZ,ZZ,ZG,other prompt,nonprompt light,nonprompt tau,e,mu,tau,jets,stat"'
#    command += ' ;'
#    
#    runCombineCommand(command, output_folder)
#
#    from HNL.Tools.helpers import getPublicHTMLfolder
#    public_html = getPublicHTMLfolder(output_folder)
#    makeDirIfNeeded(public_html+'/x')
#    ##os.system('scp '+output_folder+'/scan.png '+public_html+'/scan.png')
#    ##os.system('scp '+output_folder+'/scan.pdf '+public_html+'/scan.pdf')
#    os.system('scp '+output_folder+'/breakdown.png '+public_html+'/breakdown.png')
#    os.system('scp '+output_folder+'/breakdown.pdf '+public_html+'/breakdown.pdf')

def runGroupedImpacts(datacard, cardname):
    output_folder = getOutputFolder(datacard.replace('dataCards', 'output').rsplit('/', 1)[0] +'/GroupedImpacts/'+cardname)
    common_parts = '--algo grid --snapshotName MultiDimFit --redefineSignalPOIs r --setParameterRanges r=-1,2 --setParameters r=1'
    #common_parts = '--algo grid --snapshotName MultiDimFit --freezeParameters r=1'
    #common_parts = '--algo fixed --snapshotName MultiDimFit --fixedPointPOIs r=1'
    #common_parts = '--algo fixed --snapshotName MultiDimFit --skipInitialFit --setParameterRanges r=0,3'
 
    command = ''
    # initial fit:
    command += 'combine --saveWorkspace --redefineSignalPOIs r --setParameters r=0 -M MultiDimFit -d {0} -n hnl.postfit ; '.format(datacard)
    #command += 'combine --saveWorkspace --redefineSignalPOIs r --fixedPointPOIs r=1 -M MultiDimFit -d {0} -n hnl.postfit ; '.format(datacard)
    # scan 1:
    command += 'combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit {0} ; '.format(common_parts)
    command += "combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit {0} --freezeNuisanceGroups nonprompt_tau -n hnl.freeze_nonprompttau; ".format(common_parts)
    command += "combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit {0} --freezeNuisanceGroups nonprompt_tau,tau -n hnl.freeze_nonprompttau_tau; ".format(common_parts)
    command += "combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit {0} --freezeNuisanceGroups nonprompt_tau,tau,nonprompt_light -n hnl.freeze_nonprompttau_tau_nonpromptlight; ".format(common_parts)
    command += "combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit {0} --freezeNuisanceGroups nonprompt_tau,tau,nonprompt_light,WZ_norm -n hnl.freeze_nonprompttau_tau_nonpromptlight_WZ; ".format(common_parts)
    command += "combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit {0} --freezeNuisanceGroups nonprompt_tau,tau,nonprompt_light,WZ_norm,ZZ_norm -n hnl.freeze_nonprompttau_tau_nonpromptlight_WZ_ZZ; ".format(common_parts)
    command += "combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit {0} --freezeNuisanceGroups nonprompt_tau,tau,nonprompt_light,WZ_norm,ZZ_norm,conv_norm -n hnl.freeze_nonprompttau_tau_nonpromptlight_WZ_ZZ_conv; ".format(common_parts)
    command += "combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit {0} --freezeNuisanceGroups nonprompt_tau,tau,nonprompt_light,WZ_norm,ZZ_norm,conv_norm,prompt_norm -n hnl.freeze_nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother; ".format(common_parts)
    command += "combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit {0} --freezeNuisanceGroups nonprompt_tau,tau,nonprompt_light,WZ_norm,ZZ_norm,conv_norm,prompt_norm,trigger -n hnl.freeze_nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother_trig; ".format(common_parts)
    command += "combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit {0} --freezeNuisanceGroups nonprompt_tau,tau,nonprompt_light,WZ_norm,ZZ_norm,conv_norm,prompt_norm,trigger,luminosity -n hnl.freeze_nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother_trig_lumi; ".format(common_parts)
    command += "combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit {0} --freezeNuisanceGroups nonprompt_tau,tau,nonprompt_light,WZ_norm,ZZ_norm,conv_norm,prompt_norm,trigger,luminosity,theory -n hnl.freeze_nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother_trig_lumi_theo; ".format(common_parts)
    command += "combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit {0} --freezeNuisanceGroups nonprompt_tau,tau,nonprompt_light,WZ_norm,ZZ_norm,conv_norm,prompt_norm,trigger,luminosity,theory,electron -n hnl.freeze_nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother_trig_lumi_theo_e; ".format(common_parts)
    command += "combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit {0} --freezeNuisanceGroups nonprompt_tau,tau,nonprompt_light,WZ_norm,ZZ_norm,conv_norm,prompt_norm,trigger,luminosity,theory,electron,muon -n hnl.freeze_nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother_trig_lumi_theo_e_mu; ".format(common_parts)
    command += "combine higgsCombinehnl.postfit.MultiDimFit.mH120.root -M MultiDimFit {0} --freezeNuisanceGroups nonprompt_tau,tau,nonprompt_light,WZ_norm,ZZ_norm,conv_norm,prompt_norm,trigger,luminosity,theory,electron,muon,jets -n hnl.freeze_nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother_trig_lumi_theo_e_mu_jets; ".format(common_parts)
    
    command += 'plot1DScan.py higgsCombineTest.MultiDimFit.mH120.root --main-label "Total Uncert." --POI r --others'
    command += ' higgsCombinehnl.freeze_nonprompttau.MultiDimFit.mH120.root:"freeze nonprompttau":13'
    command += ' higgsCombinehnl.freeze_nonprompttau_tau.MultiDimFit.mH120.root:"freeze nonprompttau_tau":12'
    command += ' higgsCombinehnl.freeze_nonprompttau_tau_nonpromptlight.MultiDimFit.mH120.root:"freeze nonprompttau_tau_nonpromptlight":11'
    command += ' higgsCombinehnl.freeze_nonprompttau_tau_nonpromptlight_WZ.MultiDimFit.mH120.root:"freeze nonprompttau_tau_nonpromptlight_WZ":10'
    command += ' higgsCombinehnl.freeze_nonprompttau_tau_nonpromptlight_WZ_ZZ.MultiDimFit.mH120.root:"freeze nonprompttau_tau_nonpromptlight_WZ_ZZ":9'
    command += ' higgsCombinehnl.freeze_nonprompttau_tau_nonpromptlight_WZ_ZZ_conv.MultiDimFit.mH120.root:"freeze nonprompttau_tau_nonpromptlight_WZ_ZZ_conv":8'
    command += ' higgsCombinehnl.freeze_nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother.MultiDimFit.mH120.root:"freeze nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother":7'
    command += ' higgsCombinehnl.freeze_nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother_trig.MultiDimFit.mH120.root:"freeze nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother_trig":6'
    command += ' higgsCombinehnl.freeze_nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother_trig_lumi.MultiDimFit.mH120.root:"freeze nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother_trig_lumi":5'
    command += ' higgsCombinehnl.freeze_nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother_trig_lumi_theo.MultiDimFit.mH120.root:"freeze nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother_trig_lumi_theo":4'
    command += ' higgsCombinehnl.freeze_nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother_trig_lumi_theo_e.MultiDimFit.mH120.root:"freeze nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother_trig_lumi_theo_e":3'
    command += ' higgsCombinehnl.freeze_nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother_trig_lumi_theo_e_mu.MultiDimFit.mH120.root:"freeze nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother_trig_lumi_theo_e_mu":2'
    command += ' higgsCombinehnl.freeze_nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother_trig_lumi_theo_e_mu_jets.MultiDimFit.mH120.root:"freeze nonprompttau_tau_nonpromptlight_WZ_ZZ_conv_promptother_trig_lumi_theo_e_mu_jets":1'
    command += ' --output breakdown --y-max 10 --y-cut 40 --breakdown "nonprompttau,tau,nonpromptlight,WZ,ZZ,conv,promptother,trig,lumi,theo,e,mu,jets,stat"'

    command += ' ;'
    
    runCombineCommand(command, output_folder)

    from HNL.Tools.helpers import getPublicHTMLfolder
    public_html = getPublicHTMLfolder(output_folder)
    makeDirIfNeeded(public_html+'/x')
    ##os.system('scp '+output_folder+'/scan.png '+public_html+'/scan.png')
    ##os.system('scp '+output_folder+'/scan.pdf '+public_html+'/scan.pdf')
    print public_html+'/breakdown.pdf'
    print output_folder
    os.system('scp '+output_folder+'/breakdown.png '+public_html+'/breakdown.png')
    os.system('scp '+output_folder+'/breakdown.pdf '+public_html+'/breakdown.pdf')


def runGoodnessOfFit(datacard, cardname):    
    output_folder = getOutputFolder(datacard.replace('dataCards', 'output').rsplit('/', 1)[0] +'/GOF/'+cardname)
    makeDirIfNeeded(output_folder+'/x')

    runCombineCommand('combine -M GoodnessOfFit {0} --algo saturated ; '.format(datacard)
                    + 'combine -M GoodnessOfFit {0} --algo saturated -t 500 ; '.format(datacard)
                    + 'combineTool.py -M CollectGoodnessOfFit --input higgsCombineTest.GoodnessOfFit.mH120.root higgsCombineTest.GoodnessOfFit.mH120.123456.root -o gof.json ; '
                    + 'plotGof.py gof.json --statistic saturated -o gof_plot --mass 120.0',
                output_folder)
    
    from HNL.Tools.helpers import getPublicHTMLfolder
    public_html = getPublicHTMLfolder(output_folder)
    makeDirIfNeeded(public_html+'/x')
    os.system('scp '+output_folder+'/gof_plot.png '+public_html+'/gof_plot.png')
    os.system('scp '+output_folder+'/gof_plot.pdf '+public_html+'/gof_plot.pdf')
    
def producePostFit(datacard, cardname):
    output_folder = getOutputFolder(datacard.replace('dataCards', 'output').rsplit('/', 1)[0] +'/postfit/'+cardname)
    print output_folder
    #runCombineCommand('text2workspace.py '+datacard+ ' -o ws.root ; combine ws.root -M FitDiagnostics --saveWithUnc', output_folder)    
    #runCombineCommand('text2workspace.py '+datacard+ ' -o ws.root ; combine ws.root -M FitDiagnostics --saveWithUnc --cminDefaultMinimizerStrategy 0 --expectSignal 0 ', output_folder)    
    #runCombineCommand('text2workspace.py '+datacard+ ' -o ws.root ; combine ws.root -M FitDiagnostics --saveWithUnc --rMin -10 --robustFit=1 --rMax 5 --cminDefaultMinimizerStrategy 0 --expectSignal 0', output_folder)    
    #runCombineCommand('text2workspace.py '+datacard+ ' -o ws.root ; combine ws.root -M FitDiagnostics  --rMin -1 --robustFit=1 --rMax 1 --expectSignal 0 --setRobustFitAlgo 1 --setRobustFitStrategy 1 --saveWithUnc', output_folder)    
    #runCombineCommand('text2workspace.py '+datacard+ ' -o ws.root ; combine ws.root -M FitDiagnostics  --rMin -10 --robustFit=1 --rMax 5 --expectSignal 0 --setRobustFitAlgo 1 --setRobustFitStrategy 1', output_folder)    
    runCombineCommand('text2workspace.py '+datacard+ ' -o ws.root ; combine ws.root -M FitDiagnostics  --rMin -1 --robustFit=1 --rMax 5 --expectSignal 0 --setRobustFitAlgo 3 --setRobustFitStrategy 2 --saveShapes --saveWithUncertainties', output_folder)    
    print datacard
    os.system('scp '+datacard+' '+output_folder+'/datacard.txt')
    #runCombineCommand('PostFitShapesFromWorkspace -d datacard.txt -w ws.root --output postfitshapes.root -f fitDiagnosticsTest.root:fit_s --postfit --sampling --total-shapes', output_folder)    
    runCombineCommand('PostFitShapesFromWorkspace -d datacard.txt -w ws.root --output postfitshapes_bkgr.root -f fitDiagnosticsTest.root:fit_b --postfit --sampling --total-shapes', output_folder)    
    #runCombineCommand('python '+os.path.expandvars('$CMSSW_BASE')+'/../CMSSW_11_3_4/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py fitDiagnosticsTest.root', output_folder)

def getCovarianceMatrix(datacard, cardname):
    output_folder = getOutputFolder(datacard.replace('dataCards', 'output').rsplit('/', 1)[0] +'/covariance/'+cardname)
    runCombineCommand('text2workspace.py '+datacard+ ' -o ws.root --X-allow-no-signal --X-allow-no-background', output_folder)
    runCombineCommand('combine -M FitDiagnostics --saveShapes --saveWithUnc --numToysForShape 10 --saveOverall --preFitValue 0 ws.root', output_folder)
    from HNL.Tools.helpers import getPublicHTMLfolder, makeDirIfNeeded
    public_html = getPublicHTMLfolder(output_folder)
    makeDirIfNeeded(public_html+'/x')
    os.system('scp '+output_folder+'/fitDiagnostics.root '+public_html+'/fitDiagnostics.root')
    print 'stored in', output_folder
    return
    

def runLimit(card_manager, signal_name, cardnames):
    if len(cardnames) == 1 and '/' in cardnames[0]:
        datacard = cardnames[0]
        cardname = datacard.rsplit('/', 1)[1].split('.')[0] 
    else:
        card_manager.prepareAllCards(signal_name, cardnames)
        cardname = getOutDataCardName(cardnames, args.searchregions)
        datacard = card_manager.getDatacardPath(signal_name, cardname, card_manager.combineRegionNames(signal_name))
   
    print 'Running Combine for {0}'.format(signal_name)
    if args.method == 'asymptotic':
        runAsymptoticLimit(datacard, cardname)
    elif args.method == 'hybrid':
        runHybridNew(datacard, cardname)
    elif args.method == 'significance':
        runSignificance(datacard, cardname)
    elif args.method == 'covariance':
        getCovarianceMatrix(datacard, cardname)
    elif args.method == 'impact':
        runImpacts(datacard, cardname)
    elif args.method == 'groupedimpact':
        runGroupedImpacts(datacard, cardname)
    elif args.method == 'gof':
        runGoodnessOfFit(datacard, cardname)
    elif args.method == 'postfit':
        producePostFit(datacard, cardname)
    print 'Finished running toy limits for {0}'.format(signal_name)


# Create datacard manager
from HNL.Stat.datacardManager import DatacardManager
tag = 'displaced' if args.displaced else 'prompt'
datacard_manager = DatacardManager(args.year, args.era, args.strategy, args.flavor, args.selection, args.regions, args.masstype, args.inputTag, args.searchregions)

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
            print "Mass of {0} available?".format(mass), datacard_manager.checkMassAvailability(signal_name)
            if not (len(args.datacards) == 1 and '/' in args.datacards[0]) and not datacard_manager.checkMassAvailability(signal_name): continue
            print '\x1b[6;30;42m', 'Processing mN =', str(mass), 'GeV with V2 = ', str(coupling), '\x1b[0m'
            runLimit(datacard_manager, signal_name, args.datacards)

    closeLogger(log)


if args.submitPlotting or args.isChild or args.method in ['covariance', 'impact', 'gof']:
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

asymptotic_str = args.method

year_to_read = args.year[0] if len(args.year) == 1 else '-'.join(args.year)

card = getOutDataCardName(args.datacards, args.searchregions) 
method_name = args.method
destination = makePathTimeStamped(os.path.expandvars('$CMSSW_BASE/src/HNL/Stat/data/Results/runAsymptoticLimits/'+args.masstype+'-'+('prompt' if not args.displaced else 'displaced')+'/'+args.strategy+'-'+args.selection+(('-'+args.tag) if args.tag is not None else '')+'/'+args.flavor+'/'+card+'/'+ args.era+year_to_read))

#Make and save graph objects
passed_masses = []
limits = {}
print 'start'
for mass in args.masses:
    mass_str = str(mass) if not mass.is_integer() else str(int(mass))
    print mass_str
    couplings = returnCouplings(mass)
    input_folders = []
    for c in couplings:
        signal_name = 'HNL-'+args.flavor+'-m'+mass_str+'-Vsq'+('{:.1e}'.format(c).replace('-', 'm'))+'-'+('prompt' if not args.displaced else 'displaced')
        tmp_folder = datacard_manager.getDatacardPath(signal_name, card, datacard_manager.combineRegionNames(signal_name))
        tmp_folder = tmp_folder.replace('dataCards', 'output').rsplit('/', 1)[0] +'/'+asymptotic_str+'/'+card
        if args.tag is not None: tmp_folder += '-'+args.tag
        tmp_folder += '/higgsCombineTest.AsymptoticLimits.mH120.root'
        input_folders.append(tmp_folder)

    if args.displaced and mass <= displaced_mass_threshold:
        tmp_limit = extractScaledLimitsDisplacedHNL(input_folders, couplings, blind=args.blind)
        from HNL.Stat.combineTools import drawSignalStrengthPerCouplingDisplaced
        drawSignalStrengthPerCouplingDisplaced(input_folders, couplings, destination+'/components', 'm'+mass_str, year_to_read, args.flavor, blind=args.blind)
    else:
        from HNL.Stat.combineTools import getCrossSection
        if not args.xseclimit:
            tmp_limit = extractScaledLimitsPromptHNL(input_folders[0], couplings[0])
        else:
            tmp_limit = extractScaledLimitsPromptHNL(input_folders[0], getCrossSection(args.flavor, mass, couplings[0]))
        from HNL.Stat.combineTools import drawSignalStrengthPerCouplingPrompt
        #print destination+'/components'
        #drawSignalStrengthPerCouplingPrompt(input_folders[0], couplings[0], destination+'/components', 'm'+mass_str, year_to_read, args.flavor, blind=args.blind)

    if tmp_limit is not None and len(tmp_limit) > 4: 
        passed_masses.append(mass)
        limits[mass] = tmp_limit

print 'made graphs'
graphs = makeGraphs(passed_masses, limits=limits)
if args.xseclimit:
    if args.tag is None:
        args.tag = 'xsec'
    else:
        args.tag += '-xsec'
        
out_path_base = lambda era, sname, cname, tag : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'output', args.masstype+'-'+('prompt' if not args.displaced else 'displaced'), era, sname+'-'+args.flavor+'-'+asymptotic_str+'/'+cname+(('-'+args.inputTag) if args.inputTag is not None else '')+(('-'+tag) if tag is not None else ''))
out_path = (args.outputfolder) if args.outputfolder is not None else out_path_base(args.era+year_to_read, args.strategy +'-'+ args.selection, card, args.tag)
if args.regions is not None:
    out_path += '/'+'-'.join(sorted(args.regions))
out_path += "/limits.root"
saveGraphs(graphs, out_path)
saveJsonFile(limits, args.outputfolder if args.outputfolder is not None else out_path_base(args.era+year_to_read, args.strategy +'-'+ args.selection, card, args.tag))

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
