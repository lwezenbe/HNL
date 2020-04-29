#! /usr/bin/env python

#
# Code to calculate trigger efficiency
#

import numpy as np
import ROOT

#
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--isChild',  action='store_true', default=False,  help='mark as subjob, will never submit subjobs by itself')
argParser.add_argument('--year',     action='store',      default=None,   help='Select year', choices=['2016', '2017', '2018'])
argParser.add_argument('--subJob',   action='store',      default=None,   help='The number of the subjob for this sample')
argParser.add_argument('--sample',   action='store',      default=None,   help='Select sample by entering the name as defined in the conf file')
argParser.add_argument('--isTest',   action='store_true', default=False,  help='Run a small test')
argParser.add_argument('--runLocal', action='store_true', default=False,  help='use local resources instead of Cream02')
argParser.add_argument('--dryRun',   action='store_true', default=False,  help='do not launch subjobs, only show them')
argParser.add_argument('--includeReco',   action='store_true', default=False,  help='look at the efficiency for a gen tau to be both reconstructed and identified. Currently just fills the efficiency for isolation')
argParser.add_argument('--onlyReco',   action='store_true', default=False,  help='look at the efficiency for a gen tau to be reconstructed. Currently just fills the efficiency for isolation')
argParser.add_argument('--processExistingFiles',   action='store', default=None,  help='Process the existing files. Leave empty for all choices', choices = ['', 'text', 'plots'])
argParser.add_argument('--masses', type=int, nargs='*',  help='Only run or plot signal samples with mass given in this list')
args = argParser.parse_args()

#
# Change some settings if this is a test
#
if args.isTest:
    args.isChild = True
    # args.sample = 'WZTo3LNu'
    # args.sample = 'HNLtau-60'
    args.sample = 'HNLtau-m60'
    args.subJob = '0'
    args.year = '2016'

#
# All ID's and WP we want to test
# If you want to add a new algorithm, add a line below
# Make sure all algo keys and WP have a corresponding entry in HNL.ObjectSelection.tauSelector
#
algos = {'MVA2017v2': ['vloose', 'loose', 'medium', 'tight', 'vtight'],
                'MVA2017v2New': ['vloose', 'loose', 'medium', 'tight', 'vtight'],
                'deeptauVSjets': ['vvvloose', 'vvloose', 'vloose', 'loose', 'medium', 'tight', 'vtight', 'vvtight']
                }

def getEleWPs(iso_algo):
    if 'deeptau' in iso_algo:
        return ['vvvloose', 'vvloose', 'vloose', 'loose', 'medium', 'tight', 'vtight', 'vvtight']
    else:
        return ['loose', 'tight']

def getMuWPs(iso_algo):
    if 'deeptau' in iso_algo:
        return ['vloose', 'loose', 'medium', 'tight']
    else:
        return ['loose', 'tight']

#
# Load in the sample list 
#
from HNL.Samples.sampleManager import SampleManager
sample_manager = SampleManager(args.year, 'noskim', 'compareTauIdList_'+str(args.year))

from HNL.Tools.helpers import getFourVec

if args.processExistingFiles is None:
#
# Submit Jobs
#
    if not args.isChild:

        from HNL.Tools.jobSubmitter import submitJobs
        jobs = []
        for sample_name in sample_manager.sample_names:
            sample = sample_manager.getSample(sample_name)
            for njob in xrange(sample.split_jobs):
                jobs += [(sample.name, str(njob))]

        submitJobs(__file__, ('sample', 'subJob'), jobs, argParser, jobLabel = 'compareTauID')
        exit(0) 

    #
    #Initialize chain
    #
    sample = sample_manager.getSample(args.sample)
    chain = sample.initTree()
    chain.year = int(args.year)
    isBkgr = not 'HNL' in sample.name

    #
    # Initialize Histograms
    #
    list_of_hist = {}
    for algo in algos.keys():
        list_of_hist[algo] = {}
        for iso_wp in algos[algo]:
            list_of_hist[algo][iso_wp] = {}
            for ele_wp in getEleWPs(algo):
                list_of_hist[algo][iso_wp][ele_wp] = {}
                for mu_wp in getMuWPs(algo):
                    list_of_hist[algo][iso_wp][ele_wp][mu_wp] = {}
                    for channel in ['Ditau', 'SingleTau']:
                        list_of_hist[algo][iso_wp][ele_wp][mu_wp][channel] = ROOT.TH1D('_'.join([channel, algo, iso_wp, ele_wp, mu_wp]), '_'.join([channel, algo, iso_wp, ele_wp, mu_wp]),1, 0, 1)
                        list_of_hist[algo][iso_wp][ele_wp][mu_wp][channel].Sumw2()

    #
    # Get luminosity weight
    #
    from HNL.Weights.lumiweight import LumiWeight
    lw = LumiWeight(sample, sample_manager)

    from HNL.EventSelection.eventSelection import bVeto
    def passCuts(chain, indices):
        if len(indices) != 3:   return False
        if chain._lCharge[indices[0]] == chain._lCharge[indices[1]] and chain._lCharge[indices[2]] == chain._lCharge[indices[1]]: return False
        if bVeto(chain, 'Deep'): return False
        vectors = []
        for l in indices:
            vectors.append(getFourVec(chain._lPt[l], chain._lEta[l], chain._lPhi[l], chain._lE[l]))
        Mlll = (vectors[0] + vectors[1] + vectors[2]).M()
        if abs(Mlll-91.19) < 15 :  return False

        return True

    #
    # Loop Over Events
    #
    if args.isTest:
        event_range = xrange(10000)
    else:
        event_range = sample.getEventRange(int(args.subJob))

    from HNL.ObjectSelection.leptonSelector import isTightLightLepton
    from HNL.ObjectSelection.tauSelector import tau_DMfinding, isCleanFromLightLeptons, tau_id_WP, passedElectronDiscr, passedMuonDiscr
    from HNL.Tools.helpers import progress, makeDirIfNeeded

    for entry in event_range:
        chain.GetEntry(entry)
        progress(entry - event_range[0], len(event_range))

        lepton_indices = []
        for l in xrange(chain._nLight):
            if isTightLightLepton(chain, l): lepton_indices.append(l)
        if len(lepton_indices) > 2: continue 
        if len(lepton_indices) == 0: continue
        if len(lepton_indices) == 2 and chain._lFlavor[lepton_indices[0]] == chain._lFlavor[lepton_indices[1]] and chain._lCharge[lepton_indices[0]] != chain._lCharge[lepton_indices[1]]:
                v0 = getFourVec(chain._lPt[lepton_indices[0]], chain._lEta[lepton_indices[0]], chain._lPhi[lepton_indices[0]], chain._lE[lepton_indices[0]])
                v1 = getFourVec(chain._lPt[lepton_indices[1]], chain._lEta[lepton_indices[1]], chain._lPhi[lepton_indices[1]], chain._lE[lepton_indices[1]])
                if abs((v0+v1).M()-91.19) < 15 :  continue

        #pre-filtering tau with common cuts to decrease time later on
        base_tau_indices_per_algo = {}
        for algo in algos.keys():
            base_tau_indices_per_algo[algo] = []

        for index in xrange(chain._nLight, chain._nL):
            if chain._lFlavor[index] != 2:              continue
            if chain._lPt[index] < 20:                  continue
            if chain._lEta[index] > 2.3:                continue
            if not isCleanFromLightLeptons(chain, index):       continue
            if chain._tauDecayMode[index] == 5 or chain._tauDecayMode[index] == 6: continue
            for algo in algos.keys():
                if tau_DMfinding[algo](chain)[index]:   base_tau_indices_per_algo[algo].append(index)

        for algo in algos.keys():
            for iso_wp in algos[algo]:
                for ele_wp in getEleWPs(algo):
                    for mu_wp in getMuWPs(algo):
                        tau_indices = []
                        for t in base_tau_indices_per_algo[algo]:
                            if not tau_id_WP[(algo, iso_wp)](chain)[t]:             continue
                            if not passedElectronDiscr(chain, t, algo, ele_wp):     continue
                            if not passedMuonDiscr(chain, t, algo, mu_wp):          continue
                            tau_indices.append(t)



                        if not passCuts(chain, lepton_indices+tau_indices): continue
                        if len(tau_indices) == 2:
                            list_of_hist[algo][iso_wp][ele_wp][mu_wp]['Ditau'].Fill(.5, lw.getLumiWeight())
                        elif len(tau_indices) == 1:
                            list_of_hist[algo][iso_wp][ele_wp][mu_wp]['SingleTau'].Fill(.5, lw.getLumiWeight())


    #
    # Write
    #
    if args.isTest: exit(0)
        
    subjobAppendix = '_subJob' + args.subJob if args.subJob else ''
    signalOrBkgr = 'Signal' if 'HNL' in sample.name else 'Background'
    output_name = os.path.join(os.getcwd(), 'data', __file__.split('.')[0], args.year, signalOrBkgr, sample.output)
    if args.isChild:
        output_name += '/tmp_'+sample.output
    output_name += '/'+ sample.name +'_events' +subjobAppendix+ '.root'
    makeDirIfNeeded(output_name)


    out_file = ROOT.TFile(output_name, 'recreate')
    out_file.cd()
    for channel in ['SingleTau', 'Ditau']:
        out_file.mkdir(channel)
        out_file.cd(channel)
        for algo in algos.keys():
            for iso_wp in algos[algo]:
                for ele_wp in getEleWPs(algo):
                    for mu_wp in getMuWPs(algo):
                        list_of_hist[algo][iso_wp][ele_wp][mu_wp][channel].Write()
        out_file.cd()

else:

    from HNL.Tools.mergeFiles import merge
    from HNL.ObjectSelection.tauSelector import getCorrespondingLightLepDiscr
    import glob
    list_to_merge =   glob.glob(os.path.join(os.getcwd(), 'data', __file__.split('.')[0], args.year, '*', '*'))  
    for f in list_to_merge:
        if 'TextResults' in f: continue
        merge(f)

    def sortkey(c):
        mass_dir = c.split('/')[-2]
        # return int(mass_dir.split('-M')[-1])
        return int(mass_dir.split('-m')[-1])

    list_of_input = {'Signal': sorted(glob.glob(os.path.join(os.getcwd(), 'data', __file__.split('.')[0], args.year, 'Signal', '*', 'events.root')), key=sortkey),
                    'Background': glob.glob(os.path.join(os.getcwd(), 'data', __file__.split('.')[0], args.year, 'Background', '*', 'events.root'))
    }

    from math import sqrt
    from HNL.Tools.helpers import getObjFromFile, makeDirIfNeeded
    # def calcSignificance(S, B):
    #     try:
    #         return S/sqrt(S+B)
    #     except:
    #         return 0.

    from  HNL.Tools.histogram import returnSqrt
    def calcSignificance(S, B):

        num = S.Clone('num')
        tot = S.Clone('tot')
        tot.Add(B)
        sqrtTot = returnSqrt(B)
        num.Divide(sqrtTot)


        return num.GetBinContent(1), num.GetBinError(1)

    #
    #  Make Text Files with significance
    #
    if args.processExistingFiles == 'text':
        
        list_of_tot_bkgr = {}
        for algo in algos.keys():
            list_of_tot_bkgr[algo] = {}
            for iso_wp in algos[algo]:
                list_of_tot_bkgr[algo][iso_wp] = {}
                for ele_wp in getEleWPs(algo):
                    list_of_tot_bkgr[algo][iso_wp][ele_wp] = {}
                    for mu_wp in getMuWPs(algo):
                        list_of_tot_bkgr[algo][iso_wp][ele_wp][mu_wp] = {}
                        for channel in ['Ditau', 'SingleTau']:
                            list_of_tot_bkgr[algo][iso_wp][ele_wp][mu_wp][channel] = None
                            for i, bkgr in enumerate(list_of_input['Background']):
                                if i == 0: list_of_tot_bkgr[algo][iso_wp][ele_wp][mu_wp][channel] = getObjFromFile(bkgr, channel+'/'+channel+'_'+algo+'_'+iso_wp+'_'+ele_wp+'_'+mu_wp)
                                else: list_of_tot_bkgr[algo][iso_wp][ele_wp][mu_wp][channel].Add(getObjFromFile(bkgr, channel+'/'+channel+'_'+algo+'_'+iso_wp+'_'+ele_wp+'_'+mu_wp))


        # for signal in list_of_input['Signal']:
        #     for channel in ['Ditau', 'SingleTau']:
        #         out_name = os.path.join(os.getcwd(), 'data', 'Results', __file__.split('.')[0], args.year, 'TextResults', signal.split('/')[-2]+'_'+channel+'.txt')
        #         makeDirIfNeeded(out_name)
        #         out_file = open(out_name, 'w')
        #         list_of_significances = []
        #         for algo in algos.keys():
        #             for iso_wp in algos[algo]:
        #                 for ele_wp in getEleWPs(algo):
        #                     for mu_wp in getMuWPs(algo):
        #                         h = getObjFromFile(signal, channel+'/'+channel+'_'+algo+'_'+iso_wp+'_'+ele_wp+'_'+mu_wp)
        #                         v = h.GetSumOfWeights()
        #                         sig = calcSignificance(v, list_of_tot_bkgr[algo][iso_wp][ele_wp][mu_wp][channel].GetSumOfWeights())
        #                         list_of_significances.append((algo+'_'+iso_wp+'_'+ele_wp+'_'+mu_wp, sig))
        #                         out_file.write(algo+'_'+iso_wp+'_'+ele_wp+'_'+mu_wp + '\t' + str(sig) +'\n')
        #         out_file.write('\n')
        #         ordered_cuts = sorted(list_of_significances, key=lambda c:c[1], reverse=True)
        #         out_file.write('OPTIMAL: '+ ordered_cuts[0][0]+ '\t'+ str(ordered_cuts[0][1]))
        
        #shortlists
        for channel in ['Ditau', 'SingleTau']:
            for algo in algos.keys():
                mass_str = '-'.join([str(m) for m in args.masses])
                out_name_tex = os.path.join(os.getcwd(), 'data', 'Results', __file__.split('.')[0], args.year, 'TextResults', 'tex', mass_str,  channel+'_'+algo+'.txt')
                makeDirIfNeeded(out_name_tex)
                out_file_tex = open(out_name_tex, 'w')
                out_file_tex.write('\\begin{table}[] \n')
                column_str = '|'.join(['c' for _ in args.masses])
                out_file_tex.write("\\begin{tabular}{|c|"+column_str+"|} \n")
                out_file_tex.write("\hline \n")
                out_file_tex.write('& '+'&'.join(['$M_N = $'+str(m)+ ' GeV' for m in args.masses])+' \\\\ \n')
                out_file_tex.write("\hline \n")
                print channel, algo
                for ele_wp in getEleWPs(algo):
                    out_file_tex.write(ele_wp)
                    for signal in list_of_input['Signal']:
                        if not any(['M'+str(m)+'/' in signal for m in args.masses]): continue
                        list_of_significances = []
                        for iso_wp in algos[algo]:
                            for mu_wp in getMuWPs(algo):
                                h = getObjFromFile(signal, channel+'/'+channel+'_'+algo+'_'+iso_wp+'_'+ele_wp+'_'+mu_wp)
                                sig, err = calcSignificance(h, list_of_tot_bkgr[algo][iso_wp][ele_wp][mu_wp][channel])
                                list_of_significances.append((iso_wp+'_'+mu_wp, sig, err))
                        ordered_cuts = sorted(list_of_significances, key=lambda c:c[1], reverse=True)
                        out_file_tex.write(' & %.2E'%ordered_cuts[0][1] +' $\pm$ %.2E'%ordered_cuts[0][2])
                        # out_file_tex.write(' & %.3f'%ordered_cuts[0][1] +' $\pm$ %.3f'%float('%.1g' % ordered_cuts[0][2]))
                        # out_file_tex.write(' & '+ str(ordered_cuts[0][1]) +' $\pm$ '+str(ordered_cuts[0][2]))
                    out_file_tex.write('\\\\ \hline \n')
                out_file_tex.write('\end{tabular} \n')
                out_file_tex.write('\end{table} \n')
                out_file_tex.close()



    #
    #   Plot the significance
    #   For each channel, different plots for different electron MVA and different algorithms
    #
    if args.processExistingFiles == 'plots':
        from HNL.Plotting.plot import Plot
        from HNL.Plotting.plottingTools import drawLineFormat, extraTextFormat

        tdrStyle_Left_Margin = 0.16
        tdrStyle_Right_Margin = 0.02
        plot_size_hor = 1 - tdrStyle_Left_Margin - tdrStyle_Right_Margin

        list_of_hist = {}
        for channel in ['Ditau', 'SingleTau']:
            list_of_hist[channel] = {}
            for algo in algos.keys():
                list_of_hist[channel][algo] = {}
                for ele_wp in getEleWPs(algo):
                    list_of_hist[channel][algo][ele_wp] = {}
                    tex_names = []
                    main_bins = len(getMuWPs(algo))
                    sub_bins = len(algos[algo])
                    total_bins = main_bins*sub_bins
                    for hist_key in ['Signal', 'Background']:
                        list_of_hist[channel][algo][ele_wp][hist_key] = []
                        global_index = 0
                        for signal in list_of_input[hist_key]:
                            s_name = signal.split('/')[-2]
                            # if args.masses is not None and 'HNL' in s_name and int(s_name.split('_')[0].split('-M')[1]) not in args.masses: continue
                            if args.masses is not None and 'HNL' in s_name and int(s_name.split('_')[0].split('-m')[1]) not in args.masses: continue
                            tex_names.append(signal.split('/')[-2])

                            list_of_hist[channel][algo][ele_wp][hist_key].append(ROOT.TH1D('_'.join([signal.split('/')[-2], channel, algo, ele_wp]), '_'.join([signal.split('/')[-2], channel, algo, ele_wp]), total_bins, 0, total_bins))
                            for mu, mu_wp in enumerate(getMuWPs(algo)):
                                for iso, iso_wp in enumerate(algos[algo]):
                                    h = getObjFromFile(signal, channel+'/'+channel+'_'+algo+'_'+iso_wp+'_'+ele_wp+'_'+mu_wp)
                                    # if hist_key == 'Signal':
                                    #     list_of_hist[channel][algo][ele_wp][hist_key][global_index].SetBinContent(iso+1+(mu*sub_bins), h.GetEntries())
                                    # else:
                                    list_of_hist[channel][algo][ele_wp][hist_key][global_index].SetBinContent(iso+1+(mu*sub_bins), h.GetBinContent(1)) #h only has 1 bin
                                    list_of_hist[channel][algo][ele_wp][hist_key][global_index].SetBinError(iso+1+(mu*sub_bins), h.GetBinError(1))
                            global_index += 1
                    custom_labels = algos[algo]*main_bins
                    lines_to_draw = []
                    extra_text = []
                    for l in xrange(1, main_bins):
                        lx = l*sub_bins
                        lines_to_draw.append(drawLineFormat(x0=lx, x1=lx, color = ROOT.kRed))
                    main_bin_length = plot_size_hor/(2*main_bins)
                    for l in xrange(main_bins):
                        tx = tdrStyle_Left_Margin + main_bin_length*(1+2*l)
                        extra_text.append(extraTextFormat(getMuWPs(algo)[l], tx, 0.32, None, 22) )
                        extra_text.append(extraTextFormat(getCorrespondingLightLepDiscr(algo)[1], tx, None, None, 22))

                    extra_text.append(extraTextFormat(algo, 0.2, 0.8))
                    extra_text.append(extraTextFormat(ele_wp + ' ' + getCorrespondingLightLepDiscr(algo)[0]))

                    p = Plot(list_of_hist[channel][algo][ele_wp]['Signal'], tex_names, name = '_'.join([channel, algo, ele_wp]), bkgr_hist = list_of_hist[channel][algo][ele_wp]['Background'], y_log = True, draw_significance = True, extra_text = extra_text)   
                    out_dir = os.path.join(os.getcwd(), 'data', 'Results', __file__.split('.')[0], args.year, 'Plots') 
                    if args.masses: out_dir = os.path.join(out_dir, '-'.join([str(m) for m in args.masses]))
                    p.drawHist(output_dir = out_dir, signal_style = True, custom_labels = custom_labels, draw_lines = lines_to_draw)                










