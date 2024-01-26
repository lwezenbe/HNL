from producePostFitPlotsForPaper import loadHistograms, loadExtraText, drawPlot, cleanUp, input_base, combineLateralyList
from HNL.HEPData.createYields import writePostfitYieldJson
import os
output_base = '/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/HEPDATA'

############################################################
##########              PLOTTING                ############
############################################################

#
# Low mass SR: NoTau
#
def lowMassNoTau():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/cutbased/postfit/NoTau')
    #ch1 = EEE-Mu L1-4
    #ch2 = EEE-Mu L9-12
    #ch3 = EEE-Mu L5-8
    #ch4 = EEE-Mu L13-16
    #ch5 = MuMuMu-E L1-4
    #ch6 = MuMuMu-E L9-12
    #ch7 = MuMuMu-E L5-8
    #ch8 = MuMuMu-E L13-16
    
    #Stepwise first L1-4
    channels = ['ch1']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/A-EEE-Mu-searchregion.shapes.root', 'A-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/A-EEE-Mu-searchregion.shapes.root', 'A-EEE-Mu/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/A-EEE-Mu-searchregion.shapes.root', 'A-EEE-Mu/HNL-tau-m60-Vsq2.0em03-prompt']],
    }
    hist_dict_A = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
 
    #Stepwise L5-8
    channels = ['ch3']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/B-EEE-Mu-searchregion.shapes.root', 'B-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/B-EEE-Mu-searchregion.shapes.root', 'B-EEE-Mu/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/B-EEE-Mu-searchregion.shapes.root', 'B-EEE-Mu/HNL-tau-m60-Vsq2.0em03-prompt']],
    }
    hist_dict_B = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    
    #Stepwise L5-8
    channels = ['ch2']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-EEE-Mu-searchregion.shapes.root', 'C-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-EEE-Mu-searchregion.shapes.root', 'C-EEE-Mu/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-EEE-Mu-searchregion.shapes.root', 'C-EEE-Mu/HNL-tau-m60-Vsq2.0em03-prompt']],
    }
    hist_dict_C = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    
    #Stepwise L5-8
    channels = ['ch4']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-EEE-Mu-searchregion.shapes.root', 'D-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-EEE-Mu-searchregion.shapes.root', 'D-EEE-Mu/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-EEE-Mu-searchregion.shapes.root', 'D-EEE-Mu/HNL-tau-m60-Vsq2.0em03-prompt']],
    }
    hist_dict_D = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    
    #Combine
    hist_dict = combineLateralyList([hist_dict_A, hist_dict_B, hist_dict_C, hist_dict_D])
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/SR/EEE-Mu')

    #MuMuMu-E

    #Stepwise first L1-4
    channels = ['ch5']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/A-MuMuMu-E-searchregion.shapes.root', 'A-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/A-MuMuMu-E-searchregion.shapes.root', 'A-MuMuMu-E/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/A-MuMuMu-E-searchregion.shapes.root', 'A-MuMuMu-E/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_A = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
 
    #Stepwise L5-8
    channels = ['ch7']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/B-MuMuMu-E-searchregion.shapes.root', 'B-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/B-MuMuMu-E-searchregion.shapes.root', 'B-MuMuMu-E/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/B-MuMuMu-E-searchregion.shapes.root', 'B-MuMuMu-E/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_B = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    
    #Stepwise L5-8
    channels = ['ch6']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-MuMuMu-E-searchregion.shapes.root', 'C-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-MuMuMu-E-searchregion.shapes.root', 'C-MuMuMu-E/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-MuMuMu-E-searchregion.shapes.root', 'C-MuMuMu-E/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_C = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    
    #Stepwise L5-8
    channels = ['ch8']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-MuMuMu-E-searchregion.shapes.root', 'D-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-MuMuMu-E-searchregion.shapes.root', 'D-MuMuMu-E/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-MuMuMu-E-searchregion.shapes.root', 'D-MuMuMu-E/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_D = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    
    #Combine
    hist_dict = combineLateralyList([hist_dict_A, hist_dict_B, hist_dict_C, hist_dict_D])
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/SR/MuMuMu-E')
    cleanUp(original_file)

#
# Figure 8.2
#

def LowMassTau():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/cutbased/postfit/SingleTau')
    #ch1 = TauEE L1-4
    #ch2 = TauEE L9-12
    #ch3 = TauEE L5-8
    #ch4 = TauEE L13-16
    #ch5 = TauEMu L1-4
    #ch6 = TauEMu L5-8
    #ch7 = TauMuMu L1-4
    #ch8 = TauMuMu L9-12
    #ch9 = TauMuMu L5-8
    #ch10 = TauMuMu L13-16

    #Stepwise first L1-4
    channels = ['ch1']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/A-TauEE-searchregion.shapes.root', 'A-TauEE/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/A-TauEE-searchregion.shapes.root', 'A-TauEE/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/A-TauEE-searchregion.shapes.root', 'A-TauEE/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_A = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    cleanUp(original_file)

    #Stepwise L5-8
    channels = ['ch3']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/B-TauEE-searchregion.shapes.root', 'B-TauEE/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/B-TauEE-searchregion.shapes.root', 'B-TauEE/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/B-TauEE-searchregion.shapes.root', 'B-TauEE/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_B = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    cleanUp(original_file)

    #Stepwise L9-12
    channels = ['ch2']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-TauEE-searchregion.shapes.root', 'C-TauEE/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-TauEE-searchregion.shapes.root', 'C-TauEE/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-TauEE-searchregion.shapes.root', 'C-TauEE/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_C = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    cleanUp(original_file)

    #Stepwise L13-16
    channels = ['ch4']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-TauEE-searchregion.shapes.root', 'D-TauEE/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-TauEE-searchregion.shapes.root', 'D-TauEE/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-TauEE-searchregion.shapes.root', 'D-TauEE/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_D = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)

    #Combine
    hist_dict = combineLateralyList([hist_dict_A, hist_dict_B, hist_dict_C, hist_dict_D])
    extra_text = loadExtraText('ee#tau_{h}', 'tau', 6e-4)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig29', ['La{0}'.format(x) for x in xrange(1, 9)]+['Lb{0}'.format(x) for x in xrange(1, 9)], 'Search region', extra_text, '29a', True, for_paper = 'thesis')


if __name__ == '__main__':
    plotFig8p1() 
    #plotFig8p2() 
    #plotFig8p3() 
    #plotFig8p4() 
    #plotFig8p5() 
    #plotFig8p6() 
    #
    #plotFig9p1() 
    #plotFig9p2() 
    #plotFig9p3() 
    #plotFig9p4() 
    #
    #plotFig10p1() 
    #plotFig10p2() 
    #plotFig10p3() 
    #plotFig10p4() 
    #
    #plotFig11p1() 
    #plotFig11p2() 
    #plotFig11p3() 
    #plotFig11p4() 
    #plotFig11p5() 
    #plotFig11p6() 
    
    #plotFig8p1Electron() 
    #plotFig8p1Muon() 
    #plotFig11p3Alternative() 
