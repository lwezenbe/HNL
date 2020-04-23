from HNL.Tools.ROC import ROC
from HNL.Tools.efficiency import Efficiency
from HNL.Tools.mergeFiles import merge
import os
import glob
from HNL.Tools.helpers import makePathTimeStamped, getObjFromFile, rootFileContent
from ROOT import TFile

#
# Argument parser and logging
#
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('bkgr',     action='store',      default=None,   help='Select bkgr')
argParser.add_argument('--signal',     action='store',      default=None,   help='Select signal')
argParser.add_argument('--makeCombinations',     action='store',      default=None,   help='Make combinations of iso and lepton discriminators')
argParser.add_argument('--includeReco',   action='store', default=None,  help='look at the efficiency for a gen tau to be both reconstructed and identified. Currently just fills the efficiency for isolation', choices = ['iso', 'noIso'])
argParser.add_argument('--overlaySignalAndBackground',   action='store_true', default=False,  help='Only applies when includeReco argument is given. This will overlay signal and background')
argParser.add_argument('--discriminators', nargs='*', default=['iso', 'ele','mu'],  help='Which discriminators do you want to test?', choices = ['iso', 'ele', 'mu'])
argParser.add_argument('--year', action='store', required=True, default=None,  help='Select year')
args = argParser.parse_args()

reco_names = {None:'NoReco', 'iso': 'IncludeReco', 'noIso': 'OnlyReco'}
default_iso_algo = 'deeptauVSjets'

#
# Make sure it doesnt load in nonexistent files
#
if args.includeReco is not None:
    if args.discriminators != ['iso']:
        print 'In this mode, only iso will be used. Removing "ele" and/or "mu" from the discriminator list.'
    args.discriminators = ['iso']

#Merges subfiles if needed
merge_files = []
for d in args.discriminators:
    merge_files.extend(glob.glob(os.path.join(os.getcwd(),'data', 'compareTauID', args.year, reco_names[args.includeReco], d, '*', '*', '*')))
for mf in merge_files:
    if "Results" in mf: continue
    merge(mf)

input_base = os.path.join(os.getcwd(),'data', 'compareTauID', args.year, reco_names[args.includeReco])
input_paths = {}
for sob in ['signal', 'background']:
    input_paths[sob] = {}
    for d in args.discriminators:
        if sob == 'signal' and args.signal is not None:
            input_paths[sob][d] = glob.glob(os.path.join(input_base, d, args.signal))
        elif sob == 'signal':
            input_paths[sob][d] = glob.glob(os.path.join(input_base, d, '*HNL*'))
        elif sob == 'background':
            input_paths[sob][d] = glob.glob(os.path.join(input_base, d, args.bkgr))

from HNL.Plotting.plot import Plot
from HNL.Plotting.plottingTools import extraTextFormat

def getCommonElements(lists):
    if not isinstance(lists, list):
        print "getCommonElements needs a list instead of a ", type(lists)
    elif not isinstance(lists[0], list):
        return lists
    else:
        if len(lists) == 2:
            out = [value for value in lists[0] if value in lists[1]]
            return out
        elif len(lists) > 2:
            first_two_common = getCommonElements([lists[0], lists[1]])
            new_lists = [first_two_common] + lists[2:]
            return getCommonElements(new_lists)
        else:
            print "lonely list"


for d in args.discriminators:
    signal_names = []
    for ip in input_paths['signal'][d]:

        signal_name = ip.split('/')[-1]
        bkgr_name = input_paths['background'][d][0].split('/')[-1]
        if signal_name in signal_names:
            print "Double check names of output. "+signal_name+" is used more than once"
        signal_names.append(signal_name)

        ##################
        # Plot ROC curves#
        ##################
        
        #
        # Not applicable when running on reco only
        #
        if args.includeReco != 'noIso':

            #
            # Read content of file
            #
            # rf = TFile(ip+'/ROC.root')
            # key_names = [k[0] for k in rootFileContent(rf)]
            # algos = {k.split('/')[1].split('-')[0] for k in key_names}
            algos = {k.split('/')[-1] for k in glob.glob(ip+'/*')}

            extra_text = []
            signal_str = 'HNL ; M_{HNL} = '+signal_name.split('-m')[-1]+ ' GeV' if 'HNL' in signal_name else signal_name
            extra_text.append(extraTextFormat('Signal: '+signal_str, 0.2, 0.78))
            extra_text.append(extraTextFormat('Background: '+bkgr_name))
            extra_text.append(extraTextFormat('p_{T}^{#tau} > 20 GeV'))
            extra_text.append(extraTextFormat('|#eta_{#tau}| < 2.3'))

            if d == 'iso' and args.makeCombinations:
                ele_wp = {}
                mu_wp = {}
                curves = []
                ordered_names = []
                for algo in algos:
                    signal_path = os.path.join(ip, algo, 'all','ROC.root')
                    bkgr_path = os.path.join(input_paths['background'][d][0], algo, 'all','ROC.root')
                    rf = TFile(signal_path)
                    key_names = [k[0] for k in rootFileContent(rf)]
                    ele_wp[algo] = {k.split('/')[1].split('-')[1] for k in key_names if algo in k}
                    mu_wp[algo] = {k.split('/')[1].split('-')[2] for k in key_names if algo in k}
                    rf.Close()
                    for ewp in ele_wp[algo]:
                        for mwp in mu_wp[algo]:
                            roc_curve = ROC('-'.join([algo, ewp, mwp]), signal_path , misid_path = bkgr_path)
                            p = Plot(roc_curve.returnGraph(), algo, '-'.join([algo, ewp, mwp]), 'efficiency', 'misid', y_log=True, extra_text = extra_text)
                            output_path = os.path.join(os.getcwd(),'data', 'Results', 'compareTauID', reco_names[args.includeReco], d, signal_name+'-'+bkgr_name, algo)
                            p.drawGraph(output_dir = output_path)
                    curves.append(ROC('-'.join([algo, 'None', 'None']), signal_path , misid_path = bkgr_path).returnGraph()) 
                    ordered_names.append(algo)
                p = Plot(curves, ordered_names, 'ROC', 'efficiency', 'misid', y_log=True, extra_text = extra_text)
                output_path = os.path.join(os.getcwd(),'data', 'Results', 'compareTauID', args.year, reco_names[args.includeReco], d, signal_name+'-'+bkgr_name)
                p.drawGraph(output_dir = output_path)
            else:
                curves = []
                ordered_names = []
                for algo in algos:
                    signal_path = os.path.join(ip, algo, 'all','ROC.root')
                    bkgr_path = os.path.join(input_paths['background'][d][0], algo, 'all','ROC.root')
                    curves.append(ROC(algo, signal_path , misid_path = bkgr_path).returnGraph()) 
                    ordered_names.append(algo)
                p = Plot(curves, ordered_names, 'ROC', 'efficiency', 'misid', y_log=True, extra_text = extra_text)
                output_path = os.path.join(os.getcwd(),'data', 'Results', 'compareTauID', args.year, reco_names[args.includeReco], d, signal_name+'-'+bkgr_name)
                p.drawGraph(output_dir = output_path)
            

        ####################
        # Plot Efficiencies#
        ####################

        #
        # Read content of file
        #
        # rf = TFile(ip+'/efficiency.root')
        # var = [k[0].split('/')[1] for k in rootFileContent(rf)]
        # key_names = [k[0] for k in rootFileContent(rf, starting_dir = var[0])]
        # algos = {k.split('/')[2].split('-')[0] for k in key_names}
        # iso_wp = {}

        algos = {k.split('/')[-1] for k in glob.glob(ip+'/*')}
        iso_wp = {}
        for algo in algos:
            iso_wp[algo] = [s for s in {k.split('/')[-1] for k in glob.glob(ip+'/'+algo+'/*') if not 'all' in k}]


        if args.includeReco == 'noIso' and d == 'iso':
            rf = TFile(ip+'/'+default_iso_algo+'/None/efficiency.root')
            var = [k[0].split('/')[1] for k in rootFileContent(rf)]
            rf.Close()

            for v in var:
                list_of_eff = []
                var_hist = []
                eff_signal = Efficiency('efficiency', None, None, ip+'/'+default_iso_algo+'/None/efficiency.root', subdirs = [v, default_iso_algo+'-None'])
                list_of_eff.append(eff_signal.getEfficiency())
                var_hist_signal = eff_signal.getDenominator()
                var_hist_signal.Scale(1./var_hist_signal.GetSumOfWeights())
                var_hist.append(var_hist_signal)
                if args.overlaySignalAndBackground:
                    eff_bkgr = Efficiency('efficiency', None, None, input_paths['background'][d][0]+'/'+default_iso_algo+'/None/efficiency.root', subdirs = [v, default_iso_algo+'-None'])
                    var_hist_bkgr = eff_bkgr.getDenominator()
                    var_hist_bkgr.Scale(1./var_hist_bkgr.GetSumOfWeights())
                    list_of_eff.append(eff_bkgr.getEfficiency())
                    var_hist.append(var_hist_bkgr)

                if args.overlaySignalAndBackground:
                    names = ['efficiency in '+signal_name, 'efficiency in '+bkgr_name, 'normalized distribution in '+signal_name, 'normalized distribution in '+bkgr_name]
                else:                    
                    names = ['efficiency in '+signal_name, 'efficiency in '+bkgr_name, 'normalized distribution in '+signal_name, 'normalized distribution in '+bkgr_name]
                                        
                p = Plot(list_of_eff, names, bkgr_hist = var_hist)
                output_path = os.path.join(os.getcwd(),'data', 'Results', 'compareTauID', args.year, reco_names[args.includeReco], 'efficiency', signal_name)
                p.drawHist(output_dir = output_path, draw_option = 'Hist')

        elif d == 'iso' and args.makeCombinations:
            ele_wp = {}
            mu_wp = {}
            for algo in algos:
                rf = TFile(os.path.join(ip, algo, 'None', 'efficiency.root'))
                var = [k[0].split('/')[1] for k in rootFileContent(rf)]
                key_names = [k[0] for k in rootFileContent(rf, starting_dir = var[0])]
                rf.Close()
                ele_wp[algo] = {k.split('-')[-1].split('(')[1].split(',')[0] for k in key_names if algo in k}
                mu_wp[algo] = {k.split('-')[-1].split('(')[1].split(',')[1].split(' ')[1].split(')')[0] for k in key_names if algo in k}
                for ewp in ele_wp[algo]:
                    for mwp in mu_wp[algo]:
                        for eff_or_fake in ['efficiency', 'fakerate']:
                            for v in var:
                                list_of_eff = []
                                ordered_names = []
                                for iwp in iso_wp[algo]:
                                    eff = Efficiency(eff_or_fake, None, None, os.path.join(ip, algo, iwp, eff_or_fake+'.root'), subdirs = [v, algo+'-('+ewp+', '+mwp+')'])
                                    list_of_eff.append(eff.getEfficiency())
                                    ordered_names.append(iwp)
                                var_hist = eff.getDenominator()
                                var_hist.Scale(1./var_hist.GetSumOfWeights())
                                ordered_names.append('event distribution')
                                extra_text = []
                                extra_text.append(extraTextFormat(algo, 0.2, 0.6))
                                extra_text.append(extraTextFormat(ewp+' e discr.'))
                                extra_text.append(extraTextFormat(mwp+' #mu discr.'))
                                p = Plot(list_of_eff, ordered_names, name=eff_or_fake+'-'+ewp+'_'+mwp, bkgr_hist = var_hist, extra_text = extra_text)
                                output_path = os.path.join(os.getcwd(),'data', 'Results', 'compareTauID', args.year, reco_names[args.includeReco], d, eff_or_fake, signal_name, algo, v)
                                p.drawHist(output_dir = output_path, draw_option = 'Hist', color_palette = 'WorkingPoints')
            rf = TFile(os.path.join(ip, [a for a in algos][0], 'None', 'efficiency.root'))
            var = [k[0].split('/')[1] for k in rootFileContent(rf)]
            rf.Close()
            for iwp in getCommonElements(iso_wp.values()):
                for eff_or_fake in ['efficiency', 'fakerate']:
                    for v in var:
                            list_of_eff = []
                            ordered_names = []
                            for algo in [a for a in algos]:
                                eff = Efficiency(eff_or_fake, None, None, os.path.join(ip, algo, iwp, eff_or_fake+'.root'), subdirs = [v, algo+'-(None, None)'])
                                list_of_eff.append(eff.getEfficiency())
                                ordered_names.append(algo)
                            var_hist = eff.getDenominator()
                            var_hist.Scale(list_of_eff[0].GetSumOfWeights()/var_hist.GetSumOfWeights())
                            ordered_names.append('event distribution')
                            extra_text = []
                            # p = Plot(list_of_eff, ordered_names, name=eff_or_fake+'-'+iwp, bkgr_hist = var_hist, extra_text = extra_text, y_log = True)
                            p = Plot(list_of_eff, ordered_names, name=eff_or_fake+'-'+iwp, extra_text = extra_text, y_log = True)
                            output_path = os.path.join(os.getcwd(),'data', 'Results', 'compareTauID', args.year, reco_names[args.includeReco], d, eff_or_fake, signal_name, 'all-gos', v)
                            p.drawHist(output_dir = output_path, draw_option = 'Hist')
                            p.close()



        else:
            for algo in algos:
                rf = TFile(os.path.join(ip, algo, 'None', 'efficiency.root'))
                var = [k[0].split('/')[1] for k in rootFileContent(rf)]
                rf.Close()
                for eff_or_fake in ['efficiency', 'fakerate']:
                    for v in var:
                        list_of_eff = []
                        ordered_names = []
                        for iwp in iso_wp[algo]:
                            eff = Efficiency(eff_or_fake, None, None, os.path.join(ip, algo, iwp, eff_or_fake+'.root'), subdirs = [v, algo+'-'+iwp])
                            list_of_eff.append(eff.getEfficiency())
                            ordered_names.append(iwp)
                        var_hist = eff.getDenominator()
                        var_hist.Scale(1./var_hist.GetSumOfWeights())
                        extra_text = []
                        extra_text.append(extraTextFormat(algo, 0.2, 0.6))
                        # p = Plot(list_of_eff, ordered_names, bkgr_hist = var_hist)
                        p = Plot(list_of_eff, ordered_names, y_log = True)
                        output_path = os.path.join(os.getcwd(),'data', 'Results', 'compareTauID', args.year, reco_names[args.includeReco], d, eff_or_fake, algo, signal_name)
                        p.drawHist(output_dir = output_path, draw_option = 'Hist', color_palette = 'WorkingPoints')
