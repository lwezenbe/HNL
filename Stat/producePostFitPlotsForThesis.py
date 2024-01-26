from producePostFitPlotsForPaper import loadHistograms, loadExtraText, drawPlot, cleanUp, input_base, output_base, combineLateralyList
import os

###############
# Figure 7.26 #
###############

def plotFig26a():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/e/HNL-e-m30-Vsq4.0em06-prompt/shapes/custom-lowestmass/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    channels = ['ch3', 'ch4']
    
    signal_files = {
        'HNL-e-m20-Vsq4.0em06-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/C-EEE-Mu-lowestmasse.shapes.root', 'C-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/D-EEE-Mu-lowestmasse.shapes.root', 'D-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt']],
        'HNL-e-m40-Vsq6.0em06-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/C-EEE-Mu-lowestmasse.shapes.root', 'C-EEE-Mu/HNL-e-m40-Vsq6.0em06-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/D-EEE-Mu-lowestmasse.shapes.root', 'D-EEE-Mu/HNL-e-m40-Vsq6.0em06-prompt']],
        'HNL-e-m60-Vsq2.0em05-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/C-EEE-Mu-lowestmasse.shapes.root', 'C-EEE-Mu/HNL-e-m60-Vsq2.0em05-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/D-EEE-Mu-lowestmasse.shapes.root', 'D-EEE-Mu/HNL-e-m60-Vsq2.0em05-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 6.0e-6)
    
    extra_text = loadExtraText('eee/ee#mu', 'e', 6.0e-6)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig26', None, 'BDT(10#minus40, e, 0#tau_{h}) score', extra_text, '26a', for_paper= 'thesis')
    cleanUp(original_file)

def plotFig26b():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/e/HNL-e-m30-Vsq4.0em06-prompt/shapes/custom-lowmass/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    channels = ['ch3', 'ch4']
    
    signal_files = {
        'HNL-e-m20-Vsq4.0em06-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/C-EEE-Mu-lowmasse.shapes.root', 'C-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/D-EEE-Mu-lowmasse.shapes.root', 'D-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt']],
        'HNL-e-m40-Vsq6.0em06-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/C-EEE-Mu-lowmasse.shapes.root', 'C-EEE-Mu/HNL-e-m40-Vsq6.0em06-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/D-EEE-Mu-lowmasse.shapes.root', 'D-EEE-Mu/HNL-e-m40-Vsq6.0em06-prompt']],
        'HNL-e-m60-Vsq2.0em05-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/C-EEE-Mu-lowmasse.shapes.root', 'C-EEE-Mu/HNL-e-m60-Vsq2.0em05-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/D-EEE-Mu-lowmasse.shapes.root', 'D-EEE-Mu/HNL-e-m60-Vsq2.0em05-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 6.0e-6)
    
    extra_text = loadExtraText('eee/ee#mu', 'e', 6.0e-6)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig26', None, 'BDT(50#minus75, e, 0#tau_{h}) score', extra_text, '26b', for_paper = 'thesis')
    cleanUp(original_file)

def plotFig26c():
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
       'HNL-e-m20-Vsq4.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/A-EEE-Mu-searchregion.shapes.root', 'A-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt']],
       'HNL-e-m40-Vsq6.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/A-EEE-Mu-searchregion.shapes.root', 'A-EEE-Mu/HNL-e-m40-Vsq6.0em06-prompt']],
       'HNL-e-m60-Vsq2.0em05-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/A-EEE-Mu-searchregion.shapes.root', 'A-EEE-Mu/HNL-e-m60-Vsq2.0em05-prompt']],
    }
    hist_dict_A = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-6)
    
    #Stepwise L5-8
    channels = ['ch3']
    signal_files = {
       'HNL-e-m20-Vsq4.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/B-EEE-Mu-searchregion.shapes.root', 'B-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt']],
       'HNL-e-m40-Vsq6.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/B-EEE-Mu-searchregion.shapes.root', 'B-EEE-Mu/HNL-e-m40-Vsq6.0em06-prompt']],
       'HNL-e-m60-Vsq2.0em05-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/B-EEE-Mu-searchregion.shapes.root', 'B-EEE-Mu/HNL-e-m60-Vsq2.0em05-prompt']],
    }
    hist_dict_B = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-6)
    
    #Stepwise L5-8
    channels = ['ch2']
    signal_files = {
       'HNL-e-m20-Vsq4.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/C-EEE-Mu-searchregion.shapes.root', 'C-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt']],
       'HNL-e-m40-Vsq6.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/C-EEE-Mu-searchregion.shapes.root', 'C-EEE-Mu/HNL-e-m40-Vsq6.0em06-prompt']],
       'HNL-e-m60-Vsq2.0em05-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/C-EEE-Mu-searchregion.shapes.root', 'C-EEE-Mu/HNL-e-m60-Vsq2.0em05-prompt']],
    }
    hist_dict_C = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-6)
    
    #Stepwise L5-8
    channels = ['ch4']
    signal_files = {
       'HNL-e-m20-Vsq4.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/D-EEE-Mu-searchregion.shapes.root', 'D-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt']],
       'HNL-e-m40-Vsq6.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m40-Vsq6.0em06-prompt/Majorana/D-EEE-Mu-searchregion.shapes.root', 'D-EEE-Mu/HNL-e-m40-Vsq6.0em06-prompt']],
       'HNL-e-m60-Vsq2.0em05-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m60-Vsq2.0em05-prompt/Majorana/D-EEE-Mu-searchregion.shapes.root', 'D-EEE-Mu/HNL-e-m60-Vsq2.0em05-prompt']],
    }
    hist_dict_D = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-6)
    
    #Combine
    hist_dict = combineLateralyList([hist_dict_A, hist_dict_B, hist_dict_C, hist_dict_D])
    extra_text = loadExtraText('eee/ee#mu', 'e', 6e-6)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig26', ['La{0}'.format(x) for x in xrange(1, 9)]+['Lb{0}'.format(x) for x in xrange(1, 9)], 'Search region', extra_text, '26c', for_paper='thesis')
    cleanUp(original_file)

###############
# Figure 7.27 #
###############

def plotFig27a():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/mu/HNL-mu-m30-Vsq2.0em06-prompt/shapes/custom-lowestmass/postfit/NoTau')
    #ch7 = MuMuMu-E L9-12
    #ch8 = MuMuMu-E L13-16
    channels = ['ch7', 'ch8']
    
    signal_files = {
        'HNL-mu-m20-Vsq2.0em06-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/C-MuMuMu-E-lowestmassmu.shapes.root', 'C-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/D-MuMuMu-E-lowestmassmu.shapes.root', 'D-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt']],
        'HNL-mu-m40-Vsq2.0em06-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/C-MuMuMu-E-lowestmassmu.shapes.root', 'C-MuMuMu-E/HNL-mu-m40-Vsq2.0em06-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/D-MuMuMu-E-lowestmassmu.shapes.root', 'D-MuMuMu-E/HNL-mu-m40-Vsq2.0em06-prompt']],
        'HNL-mu-m60-Vsq6.0em06-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/C-MuMuMu-E-lowestmassmu.shapes.root', 'C-MuMuMu-E/HNL-mu-m60-Vsq6.0em06-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/D-MuMuMu-E-lowestmassmu.shapes.root', 'D-MuMuMu-E/HNL-mu-m60-Vsq6.0em06-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 2.0e-6)
    
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'mu', 2e-6)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig27', None, 'BDT(10#minus40, #mu, 0#tau_{h}) score', extra_text, '27a', for_paper = 'thesis')
    cleanUp(original_file)

def plotFig27b():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/mu/HNL-mu-m30-Vsq2.0em06-prompt/shapes/custom-lowmass/postfit/NoTau')
    #ch7 = MuMuMu-E L9-12
    #ch8 = MuMuMu-E L13-16
    channels = ['ch7', 'ch8']
    
    signal_files = {
        'HNL-mu-m20-Vsq2.0em06-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/C-MuMuMu-E-lowmassmu.shapes.root', 'C-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/D-MuMuMu-E-lowmassmu.shapes.root', 'D-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt']],
        'HNL-mu-m40-Vsq2.0em06-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/C-MuMuMu-E-lowmassmu.shapes.root', 'C-MuMuMu-E/HNL-mu-m40-Vsq2.0em06-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/D-MuMuMu-E-lowmassmu.shapes.root', 'D-MuMuMu-E/HNL-mu-m40-Vsq2.0em06-prompt']],
        'HNL-mu-m60-Vsq6.0em06-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/C-MuMuMu-E-lowmassmu.shapes.root', 'C-MuMuMu-E/HNL-mu-m60-Vsq6.0em06-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/D-MuMuMu-E-lowmassmu.shapes.root', 'D-MuMuMu-E/HNL-mu-m60-Vsq6.0em06-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 2.0e-6)
    
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'mu', 2e-6)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig27', None, 'BDT(50#minus75, #mu, 0#tau_{h}) score', extra_text, '27b', for_paper = 'thesis')
    cleanUp(original_file)

def plotFig27c():
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
    channels = ['ch5']
    signal_files = {
       'HNL-mu-m20-Vsq2.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/A-MuMuMu-E-searchregion.shapes.root', 'A-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt']],
       'HNL-mu-m40-Vsq2.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/A-MuMuMu-E-searchregion.shapes.root', 'A-MuMuMu-E/HNL-mu-m40-Vsq2.0em06-prompt']],
       'HNL-mu-m60-Vsq6.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/A-MuMuMu-E-searchregion.shapes.root', 'A-MuMuMu-E/HNL-mu-m60-Vsq6.0em06-prompt']]
    }
    hist_dict_A = loadHistograms(original_file, channels, signal_files, target_coupling = 2e-6)

    #Stepwise L5-8
    channels = ['ch7']
    signal_files = {
       'HNL-mu-m20-Vsq2.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/B-MuMuMu-E-searchregion.shapes.root', 'B-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt']],
       'HNL-mu-m40-Vsq2.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/B-MuMuMu-E-searchregion.shapes.root', 'B-MuMuMu-E/HNL-mu-m40-Vsq2.0em06-prompt']],
       'HNL-mu-m60-Vsq6.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/B-MuMuMu-E-searchregion.shapes.root', 'B-MuMuMu-E/HNL-mu-m60-Vsq6.0em06-prompt']]
    }
    hist_dict_B = loadHistograms(original_file, channels, signal_files, target_coupling = 2e-6)
    
    #Stepwise L5-8
    channels = ['ch6']
    signal_files = {
       'HNL-mu-m20-Vsq2.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/C-MuMuMu-E-searchregion.shapes.root', 'C-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt']],
       'HNL-mu-m40-Vsq2.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/C-MuMuMu-E-searchregion.shapes.root', 'C-MuMuMu-E/HNL-mu-m40-Vsq2.0em06-prompt']],
       'HNL-mu-m60-Vsq6.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/C-MuMuMu-E-searchregion.shapes.root', 'C-MuMuMu-E/HNL-mu-m60-Vsq6.0em06-prompt']]
    }
    hist_dict_C = loadHistograms(original_file, channels, signal_files, target_coupling = 2e-6)
    
    #Stepwise L5-8
    channels = ['ch8']
    signal_files = {
       'HNL-mu-m20-Vsq2.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/D-MuMuMu-E-searchregion.shapes.root', 'D-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt']],
       'HNL-mu-m40-Vsq2.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m40-Vsq2.0em06-prompt/Majorana/D-MuMuMu-E-searchregion.shapes.root', 'D-MuMuMu-E/HNL-mu-m40-Vsq2.0em06-prompt']],
       'HNL-mu-m60-Vsq6.0em06-prompt' :
           [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m60-Vsq6.0em06-prompt/Majorana/D-MuMuMu-E-searchregion.shapes.root', 'D-MuMuMu-E/HNL-mu-m60-Vsq6.0em06-prompt']]
    }
    hist_dict_D = loadHistograms(original_file, channels, signal_files, target_coupling = 2e-6)
    
    #Combine
    hist_dict = combineLateralyList([hist_dict_A, hist_dict_B, hist_dict_C, hist_dict_D])
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'mu', 2e-6)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig27', ['La{0}'.format(x) for x in xrange(1, 9)]+['Lb{0}'.format(x) for x in xrange(1, 9)], 'Search region', extra_text, '27c', for_paper = 'thesis')
    cleanUp(original_file)

def plotFig28a():
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
    extra_text = loadExtraText('eee/ee#mu', 'tau', 6e-4)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig28', ['La{0}'.format(x) for x in xrange(1, 9)]+['Lb{0}'.format(x) for x in xrange(1, 9)], 'Search region', extra_text, '28a', True, for_paper = 'thesis')
    cleanUp(original_file)

def plotFig28b():
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
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'mu', 6e-4)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig28', ['La{0}'.format(x) for x in xrange(1, 9)]+['Lb{0}'.format(x) for x in xrange(1, 9)], 'Search region', extra_text, '28b', True, for_paper = 'thesis')
    cleanUp(original_file)

def plotFig28c():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowestmass/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    #ch7 = MuMuMu-E L9-12
    #ch8 = MuMuMu-E L13-16
    channels = ['ch3', 'ch4']
    
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-EEE-Mu-lowestmasstaulep.shapes.root', 'C-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-EEE-Mu-lowestmasstaulep.shapes.root', 'D-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-EEE-Mu-lowestmasstaulep.shapes.root', 'C-EEE-Mu/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-EEE-Mu-lowestmasstaulep.shapes.root', 'D-EEE-Mu/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-EEE-Mu-lowestmasstaulep.shapes.root', 'C-EEE-Mu/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-EEE-Mu-lowestmasstaulep.shapes.root', 'D-EEE-Mu/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 6.0e-4)
    
    extra_text = loadExtraText('eee/ee#mu', 'tau', 6.0e-4)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig28', None, 'BDT(10#minus40, #tau, 0#tau_{h}) score', extra_text, '28c', for_paper = 'thesis')
    cleanUp(original_file)
    
def plotFig28d():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowestmass/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    #ch7 = MuMuMu-E L9-12
    #ch8 = MuMuMu-E L13-16
    channels = ['ch7', 'ch8']
    
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-MuMuMu-E-lowestmasstaulep.shapes.root', 'C-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-MuMuMu-E-lowestmasstaulep.shapes.root', 'D-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-MuMuMu-E-lowestmasstaulep.shapes.root', 'C-MuMuMu-E/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-MuMuMu-E-lowestmasstaulep.shapes.root', 'D-MuMuMu-E/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-MuMuMu-E-lowestmasstaulep.shapes.root', 'C-MuMuMu-E/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-MuMuMu-E-lowestmasstaulep.shapes.root', 'D-MuMuMu-E/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 6.0e-4)
    
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'tau', 6.0e-4)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig28', None, 'BDT(10#minus40, #tau, 0#tau_{h}) score', extra_text, '28d', for_paper = 'thesis')
    cleanUp(original_file)
    
def plotFig28e():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowmass/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    #ch7 = MuMuMu-E L9-12
    #ch8 = MuMuMu-E L13-16
    channels = ['ch3', 'ch4']
    
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-EEE-Mu-lowmasstaulep.shapes.root', 'C-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-EEE-Mu-lowmasstaulep.shapes.root', 'D-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-EEE-Mu-lowmasstaulep.shapes.root', 'C-EEE-Mu/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-EEE-Mu-lowmasstaulep.shapes.root', 'D-EEE-Mu/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-EEE-Mu-lowmasstaulep.shapes.root', 'C-EEE-Mu/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-EEE-Mu-lowmasstaulep.shapes.root', 'D-EEE-Mu/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 6.0e-4)
    
    extra_text = loadExtraText('eee/ee#mu', 'tau', 6.0e-4)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig28', None, 'BDT(50#minus75, #tau, 0#tau_{h}) score', extra_text, '28e', for_paper = 'thesis')
    cleanUp(original_file)

def plotFig28f():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowmass/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    #ch7 = MuMuMu-E L9-12
    #ch8 = MuMuMu-E L13-16
    channels = ['ch7', 'ch8']
    
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-MuMuMu-E-lowmasstaulep.shapes.root', 'C-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-MuMuMu-E-lowmasstaulep.shapes.root', 'D-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-MuMuMu-E-lowmasstaulep.shapes.root', 'C-MuMuMu-E/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-MuMuMu-E-lowmasstaulep.shapes.root', 'D-MuMuMu-E/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-MuMuMu-E-lowmasstaulep.shapes.root', 'C-MuMuMu-E/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-MuMuMu-E-lowmasstaulep.shapes.root', 'D-MuMuMu-E/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 6.0e-4)
    
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'tau', 6.0e-4)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig28', None, 'BDT(50#minus75, #tau, 0#tau_{h}) score', extra_text, '28f', for_paper = 'thesis')
    cleanUp(original_file)

###############
# Figure 7.29 #
###############

def plotFig29a():
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
    cleanUp(original_file)

def plotFig29b():
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
    channels = ['ch7']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/A-TauMuMu-searchregion.shapes.root', 'A-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/A-TauMuMu-searchregion.shapes.root', 'A-TauMuMu/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/A-TauMuMu-searchregion.shapes.root', 'A-TauMuMu/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_A = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    cleanUp(original_file)
    
    #Stepwise L5-8
    channels = ['ch9']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/B-TauMuMu-searchregion.shapes.root', 'B-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/B-TauMuMu-searchregion.shapes.root', 'B-TauMuMu/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/B-TauMuMu-searchregion.shapes.root', 'B-TauMuMu/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_B = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    cleanUp(original_file)
    
    #Stepwise L9-12
    channels = ['ch8']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-TauMuMu-searchregion.shapes.root', 'C-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-TauMuMu-searchregion.shapes.root', 'C-TauMuMu/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-TauMuMu-searchregion.shapes.root', 'C-TauMuMu/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_C = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    cleanUp(original_file)
    
    #Stepwise L13-16
    channels = ['ch10']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-TauMuMu-searchregion.shapes.root', 'D-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-TauMuMu-searchregion.shapes.root', 'D-TauMuMu/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-TauMuMu-searchregion.shapes.root', 'D-TauMuMu/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_D = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    
    #Combine
    hist_dict = combineLateralyList([hist_dict_A, hist_dict_B, hist_dict_C, hist_dict_D])
    extra_text = loadExtraText('#mu#mu#tau_{h}', 'tau', 6e-4)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig29', ['La{0}'.format(x) for x in xrange(1, 9)]+['Lb{0}'.format(x) for x in xrange(1, 9)], 'Search region', extra_text, '29b', True, for_paper = 'thesis')
    cleanUp(original_file)

def plotFig29c():
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
    channels = ['ch5']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/A-TauEMu-searchregion.shapes.root', 'A-TauEMu/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/A-TauEMu-searchregion.shapes.root', 'A-TauEMu/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/A-TauEMu-searchregion.shapes.root', 'A-TauEMu/HNL-tau-m60-Vsq2.0em03-prompt'],]
    }
    hist_dict_A = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    cleanUp(original_file)
    
    #Stepwise L5-8
    channels = ['ch6']
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/B-TauEMu-searchregion.shapes.root', 'B-TauEMu/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/B-TauEMu-searchregion.shapes.root', 'B-TauEMu/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/B-TauEMu-searchregion.shapes.root', 'B-TauEMu/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    hist_dict_B = loadHistograms(original_file, channels, signal_files, target_coupling = 6e-4)
    cleanUp(original_file)

    
    #Combine
    hist_dict = combineLateralyList([hist_dict_A, hist_dict_B])
    extra_text = loadExtraText('e#mu#tau_{h}', 'tau', 6e-4)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig29', ['La{0}'.format(x) for x in xrange(1, 9)], 'Search region', extra_text, '29c', True, for_paper = 'thesis')
    cleanUp(original_file)


def plotFig30a():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowestmass/postfit/SingleTau')
    #ch3 = TauEE L9-12
    #ch4 = TauEE L13-16
    #ch9 = TauMuMu L9-12
    #ch10 = TauMuMu L13-16
    channels = ['ch3', 'ch4']
    
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-TauEE-lowestmasstauhad.shapes.root', 'C-TauEE/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-TauEE-lowestmasstauhad.shapes.root', 'D-TauEE/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-TauEE-lowestmasstauhad.shapes.root', 'C-TauEE/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-TauEE-lowestmasstauhad.shapes.root', 'D-TauEE/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-TauEE-lowestmasstauhad.shapes.root', 'C-TauEE/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-TauEE-lowestmasstauhad.shapes.root', 'D-TauEE/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 6.0e-4)
    
    extra_text = loadExtraText('ee#tau_{h}', 'tau', 6.0e-4)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig30', None, 'BDT(10#minus40, #tau, 1#tau_{h}) score', extra_text, '30a', for_paper = 'thesis')
    cleanUp(original_file)

def plotFig30b():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowestmass/postfit/SingleTau')
    #ch3 = TauEE L9-12
    #ch4 = TauEE L13-16
    #ch9 = TauMuMu L9-12
    #ch10 = TauMuMu L13-16
    channels = ['ch9', 'ch10']
    
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-TauMuMu-lowestmasstauhad.shapes.root', 'C-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-TauMuMu-lowestmasstauhad.shapes.root', 'D-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-TauMuMu-lowestmasstauhad.shapes.root', 'C-TauMuMu/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-TauMuMu-lowestmasstauhad.shapes.root', 'D-TauMuMu/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-TauMuMu-lowestmasstauhad.shapes.root', 'C-TauMuMu/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-TauMuMu-lowestmasstauhad.shapes.root', 'D-TauMuMu/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 6.0e-4)
    
    extra_text = loadExtraText('#mu#mu#tau_{h}', 'tau', 6.0e-4)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig30', None, 'BDT(10#minus40, #tau, 1#tau_{h}) score', extra_text, '30b', for_paper = 'thesis')
    cleanUp(original_file)

def plotFig30c():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowmass/postfit/SingleTau')
    #ch3 = TauEE L9-12
    #ch4 = TauEE L13-16
    #ch9 = TauMuMu L9-12
    #ch10 = TauMuMu L13-16
    channels = ['ch3', 'ch4']
    
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-TauEE-lowmasstauhad.shapes.root', 'C-TauEE/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-TauEE-lowmasstauhad.shapes.root', 'D-TauEE/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-TauEE-lowmasstauhad.shapes.root', 'C-TauEE/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-TauEE-lowmasstauhad.shapes.root', 'D-TauEE/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-TauEE-lowmasstauhad.shapes.root', 'C-TauEE/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-TauEE-lowmasstauhad.shapes.root', 'D-TauEE/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 6.0e-4)
    
    extra_text = loadExtraText('ee#tau_{h}', 'tau', 6.0e-4)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig30', None, 'BDT(50#minus75, #tau, 1#tau_{h}) score', extra_text, '30c', for_paper = 'thesis')
    cleanUp(original_file)

def plotFig30d():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowmass/postfit/SingleTau')
    #ch3 = TauEE L9-12
    #ch4 = TauEE L13-16
    #ch9 = TauMuMu L9-12
    #ch10 = TauMuMu L13-16
    channels = ['ch9', 'ch10']
    
    signal_files = {
        'HNL-tau-m20-Vsq5.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-TauMuMu-lowmasstauhad.shapes.root', 'C-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-TauMuMu-lowmasstauhad.shapes.root', 'D-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt']],
        'HNL-tau-m40-Vsq6.0em04-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/C-TauMuMu-lowmasstauhad.shapes.root', 'C-TauMuMu/HNL-tau-m40-Vsq6.0em04-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m40-Vsq6.0em04-prompt/Majorana/D-TauMuMu-lowmasstauhad.shapes.root', 'D-TauMuMu/HNL-tau-m40-Vsq6.0em04-prompt']],
        'HNL-tau-m60-Vsq2.0em03-prompt' :
            [['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/C-TauMuMu-lowmasstauhad.shapes.root', 'C-TauMuMu/HNL-tau-m60-Vsq2.0em03-prompt'],
            ['default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m60-Vsq2.0em03-prompt/Majorana/D-TauMuMu-lowmasstauhad.shapes.root', 'D-TauMuMu/HNL-tau-m60-Vsq2.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 6.0e-4)
    
    extra_text = loadExtraText('#mu#mu#tau_{h}', 'tau', 6.0e-4)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig30', None, 'BDT(50#minus75, #tau, 1#tau_{h}) score', extra_text, '30d', for_paper = 'thesis')
    cleanUp(original_file)

def plotFig31a():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/e/HNL-e-m200-Vsq5.0em03-prompt/shapes/custom-mediummass85100/postfit/NoTau')
    #ch1 = EEE-Mu E
    #ch2 = EEE-Mu F
    channels = ['ch1']
    
    signal_files = {
        'HNL-e-m85-Vsq1.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m85-Vsq1.0em03-prompt/Majorana/E-EEE-Mu-mediummass85100e.shapes.root', 'E-EEE-Mu/HNL-e-m85-Vsq1.0em03-prompt']],
        'HNL-e-m150-Vsq3.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m150-Vsq3.0em03-prompt/Majorana/E-EEE-Mu-mediummass85100e.shapes.root', 'E-EEE-Mu/HNL-e-m150-Vsq3.0em03-prompt']],
        'HNL-e-m300-Vsq1.0em02-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m300-Vsq1.0em02-prompt/Majorana/E-EEE-Mu-mediummass85100e.shapes.root', 'E-EEE-Mu/HNL-e-m300-Vsq1.0em02-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 3e-3)
    
    extra_text = loadExtraText('eee/ee#mu', 'e', 3e-3)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig31', None, 'BDT(85#minus150, e, 0#tau_{h}) score', extra_text, '31a', for_paper = 'thesis')
    cleanUp(original_file)

def plotFig31b():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/e/HNL-e-m200-Vsq5.0em03-prompt/shapes/custom-mediummass85100/postfit/NoTau')
    #ch1 = EEE-Mu E
    #ch2 = EEE-Mu F
    channels = ['ch2']
    
    signal_files = {
        'HNL-e-m85-Vsq1.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m85-Vsq1.0em03-prompt/Majorana/F-EEE-Mu-mediummass85100e.shapes.root', 'F-EEE-Mu/HNL-e-m85-Vsq1.0em03-prompt']],
        'HNL-e-m150-Vsq3.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m150-Vsq3.0em03-prompt/Majorana/F-EEE-Mu-mediummass85100e.shapes.root', 'F-EEE-Mu/HNL-e-m150-Vsq3.0em03-prompt']],
        'HNL-e-m300-Vsq1.0em02-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m300-Vsq1.0em02-prompt/Majorana/F-EEE-Mu-mediummass85100e.shapes.root', 'F-EEE-Mu/HNL-e-m300-Vsq1.0em02-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 3e-3)
    
    extra_text = loadExtraText('eee/ee#mu', 'e', 3e-3)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig31', None, 'BDT(85#minus150, e, 0#tau_{h}) score', extra_text, '31b', for_paper = 'thesis')
    cleanUp(original_file)

def plotFig31c():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/e/HNL-e-m200-Vsq5.0em03-prompt/shapes/custom-mediummass150200/postfit/NoTau')
    #ch3 = EEE-Mu E
    #ch4 = EEE-Mu F
    channels = ['ch1']
    
    signal_files = {
        'HNL-e-m85-Vsq1.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m85-Vsq1.0em03-prompt/Majorana/E-EEE-Mu-mediummass150200e.shapes.root', 'E-EEE-Mu/HNL-e-m85-Vsq1.0em03-prompt']],
        'HNL-e-m150-Vsq3.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m150-Vsq3.0em03-prompt/Majorana/E-EEE-Mu-mediummass150200e.shapes.root', 'E-EEE-Mu/HNL-e-m150-Vsq3.0em03-prompt']],
        'HNL-e-m300-Vsq1.0em02-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m300-Vsq1.0em02-prompt/Majorana/E-EEE-Mu-mediummass150200e.shapes.root', 'E-EEE-Mu/HNL-e-m300-Vsq1.0em02-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 3e-3)
    
    extra_text = loadExtraText('eee/ee#mu', 'e', 3e-3)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig31', None, 'BDT(200#minus250, e, 0#tau_{h}) score', extra_text, '31c', for_paper = 'thesis')
    cleanUp(original_file)

def plotFig31d():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/e/HNL-e-m200-Vsq5.0em03-prompt/shapes/custom-mediummass150200/postfit/NoTau')
    #ch3 = EEE-Mu E
    #ch4 = EEE-Mu F
    channels = ['ch2']
    
    signal_files = {
        'HNL-e-m85-Vsq1.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m85-Vsq1.0em03-prompt/Majorana/F-EEE-Mu-mediummass150200e.shapes.root', 'F-EEE-Mu/HNL-e-m85-Vsq1.0em03-prompt']],
        'HNL-e-m150-Vsq3.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m150-Vsq3.0em03-prompt/Majorana/F-EEE-Mu-mediummass150200e.shapes.root', 'F-EEE-Mu/HNL-e-m150-Vsq3.0em03-prompt']],
        'HNL-e-m300-Vsq1.0em02-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m300-Vsq1.0em02-prompt/Majorana/F-EEE-Mu-mediummass150200e.shapes.root', 'F-EEE-Mu/HNL-e-m300-Vsq1.0em02-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 3e-3)
    
    extra_text = loadExtraText('eee/ee#mu', 'e', 3e-3)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig31', None, 'BDT(200#minus250, e, 0#tau_{h}) score', extra_text, '31d', for_paper = 'thesis')
    cleanUp(original_file)

def plotFig31e():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/e/HNL-e-m200-Vsq5.0em03-prompt/shapes/custom-mediummass250400/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    channels = ['ch1']
    
    signal_files = {
        'HNL-e-m85-Vsq1.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m85-Vsq1.0em03-prompt/Majorana/E-EEE-Mu-mediummass250400e.shapes.root', 'E-EEE-Mu/HNL-e-m85-Vsq1.0em03-prompt']],
        'HNL-e-m150-Vsq3.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m150-Vsq3.0em03-prompt/Majorana/E-EEE-Mu-mediummass250400e.shapes.root', 'E-EEE-Mu/HNL-e-m150-Vsq3.0em03-prompt']],
        'HNL-e-m300-Vsq1.0em02-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m300-Vsq1.0em02-prompt/Majorana/E-EEE-Mu-mediummass250400e.shapes.root', 'E-EEE-Mu/HNL-e-m300-Vsq1.0em02-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 3e-3)
    
    extra_text = loadExtraText('eee/ee#mu', 'e', 3e-3)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig31', None, 'BDT(300#minus400, e, 0#tau_{h}) score', extra_text, '31e', for_paper = 'thesis')
    cleanUp(original_file)

def plotFig31f():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/e/HNL-e-m200-Vsq5.0em03-prompt/shapes/custom-mediummass250400/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    channels = ['ch2']
    
    signal_files = {
        'HNL-e-m85-Vsq1.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m85-Vsq1.0em03-prompt/Majorana/F-EEE-Mu-mediummass250400e.shapes.root', 'F-EEE-Mu/HNL-e-m85-Vsq1.0em03-prompt']],
        'HNL-e-m150-Vsq3.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m150-Vsq3.0em03-prompt/Majorana/F-EEE-Mu-mediummass250400e.shapes.root', 'F-EEE-Mu/HNL-e-m150-Vsq3.0em03-prompt']],
        'HNL-e-m300-Vsq1.0em02-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m300-Vsq1.0em02-prompt/Majorana/F-EEE-Mu-mediummass250400e.shapes.root', 'F-EEE-Mu/HNL-e-m300-Vsq1.0em02-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 3e-3)
    
    extra_text = loadExtraText('eee/ee#mu', 'e', 3e-3)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig31', None, 'BDT(300#minus400, e, 0#tau_{h}) score', extra_text, '31f', for_paper = 'thesis')
    cleanUp(original_file)

def plotFig32a():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/mu/HNL-mu-m200-Vsq4.0em03-prompt/shapes/custom-mediummass85100/postfit/NoTau')
    #ch3 = MuMuMu-E E
    #ch4 = MuMuMu-E F
    channels = ['ch3']
    
    signal_files = {
        'HNL-mu-m85-Vsq7.0em04-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m85-Vsq7.0em04-prompt/Majorana/E-MuMuMu-E-mediummass85100mu.shapes.root', 'E-MuMuMu-E/HNL-mu-m85-Vsq7.0em04-prompt']],
        'HNL-mu-m150-Vsq2.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m150-Vsq2.0em03-prompt/Majorana/E-MuMuMu-E-mediummass85100mu.shapes.root', 'E-MuMuMu-E/HNL-mu-m150-Vsq2.0em03-prompt']],
        'HNL-mu-m300-Vsq8.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m300-Vsq8.0em03-prompt/Majorana/E-MuMuMu-E-mediummass85100mu.shapes.root', 'E-MuMuMu-E/HNL-mu-m300-Vsq8.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 2e-3)
    
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'mu', 2e-3)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig32', None, 'BDT(85#minus150, mu, 0#tau_{h}) score', extra_text, '32a', for_paper = 'thesis')
    cleanUp(original_file)

    

def plotFig32b():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/mu/HNL-mu-m200-Vsq4.0em03-prompt/shapes/custom-mediummass85100/postfit/NoTau')
    #ch3 = MuMuMu-E E
    #ch4 = MuMuMu-E F
    channels = ['ch4']
    
    signal_files = {
        'HNL-mu-m85-Vsq7.0em04-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m85-Vsq7.0em04-prompt/Majorana/F-MuMuMu-E-mediummass85100mu.shapes.root', 'F-MuMuMu-E/HNL-mu-m85-Vsq7.0em04-prompt']],
        'HNL-mu-m150-Vsq2.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m150-Vsq2.0em03-prompt/Majorana/F-MuMuMu-E-mediummass85100mu.shapes.root', 'F-MuMuMu-E/HNL-mu-m150-Vsq2.0em03-prompt']],
        'HNL-mu-m300-Vsq8.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m300-Vsq8.0em03-prompt/Majorana/F-MuMuMu-E-mediummass85100mu.shapes.root', 'F-MuMuMu-E/HNL-mu-m300-Vsq8.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 2e-3)
    
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'mu', 2e-3)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig32', None, 'BDT(85#minus150, mu, 0#tau_{h}) score', extra_text, '32b', for_paper = 'thesis')
    cleanUp(original_file)

def plotFig32c():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/mu/HNL-mu-m200-Vsq4.0em03-prompt/shapes/custom-mediummass150200/postfit/NoTau')
    #ch3 = MuMuMu-E E
    #ch4 = MuMuMu-E F
    channels = ['ch3']
    
    signal_files = {
        'HNL-mu-m85-Vsq7.0em04-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m85-Vsq7.0em04-prompt/Majorana/E-MuMuMu-E-mediummass150200mu.shapes.root', 'E-MuMuMu-E/HNL-mu-m85-Vsq7.0em04-prompt']],
        'HNL-mu-m150-Vsq2.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m150-Vsq2.0em03-prompt/Majorana/E-MuMuMu-E-mediummass150200mu.shapes.root', 'E-MuMuMu-E/HNL-mu-m150-Vsq2.0em03-prompt']],
        'HNL-mu-m300-Vsq8.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m300-Vsq8.0em03-prompt/Majorana/E-MuMuMu-E-mediummass150200mu.shapes.root', 'E-MuMuMu-E/HNL-mu-m300-Vsq8.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 2e-3)
    
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'mu', 2e-3)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig32', None, 'BDT(200#minus250, mu, 0#tau_{h}) score', extra_text, '32c', for_paper = 'thesis')
    cleanUp(original_file)

def plotFig32d():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/mu/HNL-mu-m200-Vsq4.0em03-prompt/shapes/custom-mediummass150200/postfit/NoTau')
    #ch3 = MuMuMu-E E
    #ch4 = MuMuMu-E F
    channels = ['ch4']
    
    signal_files = {
        'HNL-mu-m85-Vsq7.0em04-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m85-Vsq7.0em04-prompt/Majorana/F-MuMuMu-E-mediummass150200mu.shapes.root', 'F-MuMuMu-E/HNL-mu-m85-Vsq7.0em04-prompt']],
        'HNL-mu-m150-Vsq2.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m150-Vsq2.0em03-prompt/Majorana/F-MuMuMu-E-mediummass150200mu.shapes.root', 'F-MuMuMu-E/HNL-mu-m150-Vsq2.0em03-prompt']],
        'HNL-mu-m300-Vsq8.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m300-Vsq8.0em03-prompt/Majorana/F-MuMuMu-E-mediummass150200mu.shapes.root', 'F-MuMuMu-E/HNL-mu-m300-Vsq8.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 2e-3)
    
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'mu', 2e-3)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig32', None, 'BDT(200#minus250, mu, 0#tau_{h}) score', extra_text, '32d', for_paper = 'thesis')
    cleanUp(original_file)

def plotFig32e():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/mu/HNL-mu-m200-Vsq4.0em03-prompt/shapes/custom-mediummass250400/postfit/NoTau')
    #ch3 = MuMuMu-E E
    #ch4 = MuMuMu-E F
    channels = ['ch3']
    
    signal_files = {
        'HNL-mu-m85-Vsq7.0em04-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m85-Vsq7.0em04-prompt/Majorana/E-MuMuMu-E-mediummass250400mu.shapes.root', 'E-MuMuMu-E/HNL-mu-m85-Vsq7.0em04-prompt']],
        'HNL-mu-m150-Vsq2.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m150-Vsq2.0em03-prompt/Majorana/E-MuMuMu-E-mediummass250400mu.shapes.root', 'E-MuMuMu-E/HNL-mu-m150-Vsq2.0em03-prompt']],
        'HNL-mu-m300-Vsq8.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m300-Vsq8.0em03-prompt/Majorana/E-MuMuMu-E-mediummass250400mu.shapes.root', 'E-MuMuMu-E/HNL-mu-m300-Vsq8.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 2e-3)
    
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'mu', 2e-3)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig32', None, 'BDT(300#minus400, mu, 0#tau_{h}) score', extra_text, '32e', for_paper = 'thesis')
    cleanUp(original_file)

def plotFig32f():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/mu/HNL-mu-m200-Vsq4.0em03-prompt/shapes/custom-mediummass250400/postfit/NoTau')
    #ch3 = MuMuMu-E E
    #ch4 = MuMuMu-E F
    channels = ['ch4']
    
    signal_files = {
        'HNL-mu-m85-Vsq7.0em04-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m85-Vsq7.0em04-prompt/Majorana/F-MuMuMu-E-mediummass250400mu.shapes.root', 'F-MuMuMu-E/HNL-mu-m85-Vsq7.0em04-prompt']],
        'HNL-mu-m150-Vsq2.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m150-Vsq2.0em03-prompt/Majorana/F-MuMuMu-E-mediummass250400mu.shapes.root', 'F-MuMuMu-E/HNL-mu-m150-Vsq2.0em03-prompt']],
        'HNL-mu-m300-Vsq8.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m300-Vsq8.0em03-prompt/Majorana/F-MuMuMu-E-mediummass250400mu.shapes.root', 'F-MuMuMu-E/HNL-mu-m300-Vsq8.0em03-prompt']]
    }
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 2e-3)
    
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'mu', 2e-3)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig32', None, 'BDT(300#minus400, mu, 0#tau_{h}) score', extra_text, '32f', for_paper = 'thesis')
    cleanUp(original_file)

def plotFig33a():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
    #ch1 = EEE-Mu Hb
    #ch2 = EEE-Mu Ha
    #ch3 = MuMuMu-E Hb
    #ch4 = MuMuMu-E Ha
    #ch5 = TauEE Hb
    #ch6 = TauEE Ha
    #ch7 = TauEMu Ha
    #ch8 = TauMuMu Hb
    #ch9 = TauMuMu Ha
    
    #Stepwise first L1-4
    channels = ['ch2']
    signal_files = {
        'HNL-e-m85-Vsq1.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m85-Vsq1.0em03-prompt/Majorana/F-EEE-Mu-searchregion.shapes.root', 'F-EEE-Mu/HNL-e-m85-Vsq1.0em03-prompt']],
        'HNL-e-m150-Vsq3.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m150-Vsq3.0em03-prompt/Majorana/F-EEE-Mu-searchregion.shapes.root', 'F-EEE-Mu/HNL-e-m150-Vsq3.0em03-prompt']],
        'HNL-e-m300-Vsq1.0em02-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m300-Vsq1.0em02-prompt/Majorana/F-EEE-Mu-searchregion.shapes.root', 'F-EEE-Mu/HNL-e-m300-Vsq1.0em02-prompt']]
    }
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 4e-1)
    
    extra_text = loadExtraText('eee/ee#mu', 'tau', 4e-1)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig33', ['Ha{0}'.format(x) for x in xrange(1, 10)], 'Search region', extra_text, '33a', True, for_paper = 'thesis')
    cleanUp(original_file)

def plotFig33b():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
    #ch1 = EEE-Mu Hb
    #ch2 = EEE-Mu Ha
    #ch3 = MuMuMu-E Hb
    #ch4 = MuMuMu-E Ha
    #ch5 = TauEE Hb
    #ch6 = TauEE Ha
    #ch7 = TauEMu Ha
    #ch8 = TauMuMu Hb
    #ch9 = TauMuMu Ha
    
    #Stepwise first L1-4
    channels = ['ch1']
    signal_files = {
        'HNL-e-m85-Vsq1.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m85-Vsq1.0em03-prompt/Majorana/E-EEE-Mu-searchregion.shapes.root', 'E-EEE-Mu/HNL-e-m85-Vsq1.0em03-prompt']],
        'HNL-e-m150-Vsq3.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m150-Vsq3.0em03-prompt/Majorana/E-EEE-Mu-searchregion.shapes.root', 'E-EEE-Mu/HNL-e-m150-Vsq3.0em03-prompt']],
        'HNL-e-m300-Vsq1.0em02-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/e/HNL-e-m300-Vsq1.0em02-prompt/Majorana/E-EEE-Mu-searchregion.shapes.root', 'E-EEE-Mu/HNL-e-m300-Vsq1.0em02-prompt']]
    }
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 4e-1)
    
    extra_text = loadExtraText('eee/ee#mu', 'tau', 4e-1)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig33', ['Hb{0}'.format(x) for x in xrange(1, 17)], 'Search region', extra_text, '33b', True, for_paper = 'thesis')
    cleanUp(original_file)

def plotFig34a():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
    #ch1 = EEE-Mu Hb
    #ch2 = EEE-Mu Ha
    #ch3 = MuMuMu-E Hb
    #ch4 = MuMuMu-E Ha
    #ch5 = TauEE Hb
    #ch6 = TauEE Ha
    #ch7 = TauEMu Ha
    #ch8 = TauMuMu Hb
    #ch9 = TauMuMu Ha
    
    #Stepwise first L1-4
    channels = ['ch4']
    signal_files = {
        'HNL-mu-m85-Vsq7.0em04-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m85-Vsq7.0em04-prompt/Majorana/F-MuMuMu-E-searchregion.shapes.root', 'F-MuMuMu-E/HNL-mu-m85-Vsq7.0em04-prompt']],
        'HNL-mu-m150-Vsq2.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m150-Vsq2.0em03-prompt/Majorana/F-MuMuMu-E-searchregion.shapes.root', 'F-MuMuMu-E/HNL-mu-m150-Vsq2.0em03-prompt']],
        'HNL-mu-m300-Vsq8.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m300-Vsq8.0em03-prompt/Majorana/F-MuMuMu-E-searchregion.shapes.root', 'F-MuMuMu-E/HNL-mu-m300-Vsq8.0em03-prompt']]
    }
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 4e-1)
    
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'tau', 4e-1)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig34', ['Ha{0}'.format(x) for x in xrange(1, 10)], 'Search region', extra_text, '34a', True, for_paper = 'thesis')
    cleanUp(original_file)

def plotFig34b():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
    #ch1 = EEE-Mu Hb
    #ch2 = EEE-Mu Ha
    #ch3 = MuMuMu-E Hb
    #ch4 = MuMuMu-E Ha
    #ch5 = TauEE Hb
    #ch6 = TauEE Ha
    #ch7 = TauEMu Ha
    #ch8 = TauMuMu Hb
    #ch9 = TauMuMu Ha
    
    #Stepwise first L1-4
    channels = ['ch3']
    signal_files = {
        'HNL-mu-m85-Vsq7.0em04-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m85-Vsq7.0em04-prompt/Majorana/E-MuMuMu-E-searchregion.shapes.root', 'E-MuMuMu-E/HNL-mu-m85-Vsq7.0em04-prompt']],
        'HNL-mu-m150-Vsq2.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m150-Vsq2.0em03-prompt/Majorana/E-MuMuMu-E-searchregion.shapes.root', 'E-MuMuMu-E/HNL-mu-m150-Vsq2.0em03-prompt']],
        'HNL-mu-m300-Vsq8.0em03-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/mu/HNL-mu-m300-Vsq8.0em03-prompt/Majorana/E-MuMuMu-E-searchregion.shapes.root', 'E-MuMuMu-E/HNL-mu-m300-Vsq8.0em03-prompt']]
    }
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 4e-1)
    
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'tau', 4e-1)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig34', ['Hb{0}'.format(x) for x in xrange(1, 17)], 'Search region', extra_text, '34b', True, for_paper = 'thesis')
    cleanUp(original_file)

def plotFig35a():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
    #ch1 = EEE-Mu Hb
    #ch2 = EEE-Mu Ha
    #ch3 = MuMuMu-E Hb
    #ch4 = MuMuMu-E Ha
    #ch5 = TauEE Hb
    #ch6 = TauEE Ha
    #ch7 = TauEMu Ha
    #ch8 = TauMuMu Hb
    #ch9 = TauMuMu Ha
    
    #Stepwise first L1-4
    channels = ['ch2']
    signal_files = {
        'HNL-tau-m85-Vsq1.0e+00-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m85-Vsq1.0e+00-prompt/Majorana/F-EEE-Mu-searchregion.shapes.root', 'F-EEE-Mu/HNL-tau-m85-Vsq1.0e+00-prompt']],
        'HNL-tau-m200-Vsq4.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m200-Vsq4.0em01-prompt/Majorana/F-EEE-Mu-searchregion.shapes.root', 'F-EEE-Mu/HNL-tau-m200-Vsq4.0em01-prompt']],
        'HNL-tau-m300-Vsq7.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m300-Vsq7.0em01-prompt/Majorana/F-EEE-Mu-searchregion.shapes.root', 'F-EEE-Mu/HNL-tau-m300-Vsq7.0em01-prompt']]
    }
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 4e-1)
    
    extra_text = loadExtraText('eee/ee#mu', 'tau', 4e-1)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig35', ['Ha{0}'.format(x) for x in xrange(1, 10)], 'Search region', extra_text, '35a', True, for_paper = 'thesis')
    cleanUp(original_file)


def plotFig35c():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
    #ch1 = EEE-Mu Hb
    #ch2 = EEE-Mu Ha
    #ch3 = MuMuMu-E Hb
    #ch4 = MuMuMu-E Ha
    #ch5 = TauEE Hb
    #ch6 = TauEE Ha
    #ch7 = TauEMu Ha
    #ch8 = TauMuMu Hb
    #ch9 = TauMuMu Ha
    
    #Stepwise first L1-4
    channels = ['ch4']
    signal_files = {
        'HNL-tau-m85-Vsq1.0e+00-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m85-Vsq1.0e+00-prompt/Majorana/F-MuMuMu-E-searchregion.shapes.root', 'F-MuMuMu-E/HNL-tau-m85-Vsq1.0e+00-prompt']],
        'HNL-tau-m200-Vsq4.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m200-Vsq4.0em01-prompt/Majorana/F-MuMuMu-E-searchregion.shapes.root', 'F-MuMuMu-E/HNL-tau-m200-Vsq4.0em01-prompt']],
        'HNL-tau-m300-Vsq7.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m300-Vsq7.0em01-prompt/Majorana/F-MuMuMu-E-searchregion.shapes.root', 'F-MuMuMu-E/HNL-tau-m300-Vsq7.0em01-prompt']]
    }
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 4e-1)
    
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'tau', 4e-1)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig35', ['Ha{0}'.format(x) for x in xrange(1, 10)], 'Search region', extra_text, '35c', True, for_paper = 'thesis')
    cleanUp(original_file)

def plotFig35b():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
    #ch1 = EEE-Mu Hb
    #ch2 = EEE-Mu Ha
    #ch3 = MuMuMu-E Hb
    #ch4 = MuMuMu-E Ha
    #ch5 = TauEE Hb
    #ch6 = TauEE Ha
    #ch7 = TauEMu Ha
    #ch8 = TauMuMu Hb
    #ch9 = TauMuMu Ha
    
    #Stepwise first L1-4
    channels = ['ch1']
    signal_files = {
        'HNL-tau-m85-Vsq1.0e+00-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m85-Vsq1.0e+00-prompt/Majorana/E-EEE-Mu-searchregion.shapes.root', 'E-EEE-Mu/HNL-tau-m85-Vsq1.0e+00-prompt']],
        'HNL-tau-m200-Vsq4.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m200-Vsq4.0em01-prompt/Majorana/E-EEE-Mu-searchregion.shapes.root', 'E-EEE-Mu/HNL-tau-m200-Vsq4.0em01-prompt']],
        'HNL-tau-m300-Vsq7.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m300-Vsq7.0em01-prompt/Majorana/E-EEE-Mu-searchregion.shapes.root', 'E-EEE-Mu/HNL-tau-m300-Vsq7.0em01-prompt']]
    }
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 4e-1)
    
    extra_text = loadExtraText('eee/ee#mu', 'tau', 4e-1)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig35', ['Hb{0}'.format(x) for x in xrange(1, 17)], 'Search region', extra_text, '35b', True, for_paper = 'thesis')
    cleanUp(original_file)


def plotFig35d():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
    #ch1 = EEE-Mu Hb
    #ch2 = EEE-Mu Ha
    #ch3 = MuMuMu-E Hb
    #ch4 = MuMuMu-E Ha
    #ch5 = TauEE Hb
    #ch6 = TauEE Ha
    #ch7 = TauEMu Ha
    #ch8 = TauMuMu Hb
    #ch9 = TauMuMu Ha
    
    #Stepwise first L1-4
    channels = ['ch3']
    signal_files = {
        'HNL-tau-m85-Vsq1.0e+00-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m85-Vsq1.0e+00-prompt/Majorana/E-MuMuMu-E-searchregion.shapes.root', 'E-MuMuMu-E/HNL-tau-m85-Vsq1.0e+00-prompt']],
        'HNL-tau-m200-Vsq4.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m200-Vsq4.0em01-prompt/Majorana/E-MuMuMu-E-searchregion.shapes.root', 'E-MuMuMu-E/HNL-tau-m200-Vsq4.0em01-prompt']],
        'HNL-tau-m300-Vsq7.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m300-Vsq7.0em01-prompt/Majorana/E-MuMuMu-E-searchregion.shapes.root', 'E-MuMuMu-E/HNL-tau-m300-Vsq7.0em01-prompt']]
    }
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 4e-1)
    
    extra_text = loadExtraText('#mu#mu#mu/#mu#mue', 'tau', 4e-1)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig35', ['Hb{0}'.format(x) for x in xrange(1, 17)], 'Search region', extra_text, '35d', True, for_paper = 'thesis')
    cleanUp(original_file)

def plotFig36a():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
    #ch1 = EEE-Mu Hb
    #ch2 = EEE-Mu Ha
    #ch3 = MuMuMu-E Hb
    #ch4 = MuMuMu-E Ha
    #ch5 = TauEE Hb
    #ch6 = TauEE Ha
    #ch7 = TauEMu Ha
    #ch8 = TauMuMu Hb
    #ch9 = TauMuMu Ha
    
    channels = ['ch6']
    signal_files = {
        'HNL-tau-m85-Vsq1.0e+00-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m85-Vsq1.0e+00-prompt/Majorana/F-TauEE-searchregion.shapes.root', 'F-TauEE/HNL-tau-m85-Vsq1.0e+00-prompt']],
        'HNL-tau-m200-Vsq4.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m200-Vsq4.0em01-prompt/Majorana/F-TauEE-searchregion.shapes.root', 'F-TauEE/HNL-tau-m200-Vsq4.0em01-prompt']],
        'HNL-tau-m300-Vsq7.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m300-Vsq7.0em01-prompt/Majorana/F-TauEE-searchregion.shapes.root', 'F-TauEE/HNL-tau-m300-Vsq7.0em01-prompt']]
    }
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 4e-1)
    
    extra_text = loadExtraText('ee#tau_{h}', 'tau', 4e-1)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig36', ['Ha{0}'.format(x) for x in xrange(1, 10)], 'Search region', extra_text, '36a', True, for_paper = 'thesis')
    cleanUp(original_file)

def plotFig36b():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
    #ch1 = EEE-Mu Hb
    #ch2 = EEE-Mu Ha
    #ch3 = MuMuMu-E Hb
    #ch4 = MuMuMu-E Ha
    #ch5 = TauEE Hb
    #ch6 = TauEE Ha
    #ch7 = TauEMu Ha
    #ch8 = TauMuMu Hb
    #ch9 = TauMuMu Ha
    
    channels = ['ch5']
    signal_files = {
        'HNL-tau-m85-Vsq1.0e+00-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m85-Vsq1.0e+00-prompt/Majorana/E-TauEE-searchregion.shapes.root', 'E-TauEE/HNL-tau-m85-Vsq1.0e+00-prompt']],
        'HNL-tau-m200-Vsq4.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m200-Vsq4.0em01-prompt/Majorana/E-TauEE-searchregion.shapes.root', 'E-TauEE/HNL-tau-m200-Vsq4.0em01-prompt']],
        'HNL-tau-m300-Vsq7.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m300-Vsq7.0em01-prompt/Majorana/E-TauEE-searchregion.shapes.root', 'E-TauEE/HNL-tau-m300-Vsq7.0em01-prompt']]
    }
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 4e-1)
    
    extra_text = loadExtraText('ee#tau_{h}', 'tau', 4e-1)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig36', ['Hb{0}'.format(x) for x in [1, '2-3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', 15, 16]], 'Search region', extra_text, '36b', True, for_paper = 'thesis')
    cleanUp(original_file)

def plotFig36c():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
    #ch1 = EEE-Mu Hb
    #ch2 = EEE-Mu Ha
    #ch3 = MuMuMu-E Hb
    #ch4 = MuMuMu-E Ha
    #ch5 = TauEE Hb
    #ch6 = TauEE Ha
    #ch7 = TauEMu Ha
    #ch8 = TauMuMu Hb
    #ch9 = TauMuMu Ha
    
    channels = ['ch9']
    signal_files = {
        'HNL-tau-m85-Vsq1.0e+00-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m85-Vsq1.0e+00-prompt/Majorana/F-TauMuMu-searchregion.shapes.root', 'F-TauMuMu/HNL-tau-m85-Vsq1.0e+00-prompt']],
        'HNL-tau-m200-Vsq4.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m200-Vsq4.0em01-prompt/Majorana/F-TauMuMu-searchregion.shapes.root', 'F-TauMuMu/HNL-tau-m200-Vsq4.0em01-prompt']],
        'HNL-tau-m300-Vsq7.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m300-Vsq7.0em01-prompt/Majorana/F-TauMuMu-searchregion.shapes.root', 'F-TauMuMu/HNL-tau-m300-Vsq7.0em01-prompt']]
    }
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 4e-1)
    
    extra_text = loadExtraText('#mu#mu#tau_{h}', 'tau', 4e-1)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig36', ['Ha{0}'.format(x) for x in xrange(1, 10)], 'Search region', extra_text, '36c', True, for_paper = 'thesis')
    cleanUp(original_file)

def plotFig36d():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
    #ch1 = EEE-Mu Hb
    #ch2 = EEE-Mu Ha
    #ch3 = MuMuMu-E Hb
    #ch4 = MuMuMu-E Ha
    #ch5 = TauEE Hb
    #ch6 = TauEE Ha
    #ch7 = TauEMu Ha
    #ch8 = TauMuMu Hb
    #ch9 = TauMuMu Ha
    
    channels = ['ch8']
    signal_files = {
        'HNL-tau-m85-Vsq1.0e+00-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m85-Vsq1.0e+00-prompt/Majorana/E-TauMuMu-searchregion.shapes.root', 'E-TauMuMu/HNL-tau-m85-Vsq1.0e+00-prompt']],
        'HNL-tau-m200-Vsq4.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m200-Vsq4.0em01-prompt/Majorana/E-TauMuMu-searchregion.shapes.root', 'E-TauMuMu/HNL-tau-m200-Vsq4.0em01-prompt']],
        'HNL-tau-m300-Vsq7.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m300-Vsq7.0em01-prompt/Majorana/E-TauMuMu-searchregion.shapes.root', 'E-TauMuMu/HNL-tau-m300-Vsq7.0em01-prompt']]
    }
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 4e-1)
    
    extra_text = loadExtraText('#mu#mu#tau_{h}', 'tau', 4e-1)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig36', ['Hb{0}'.format(x) for x in [1, '2-3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', 15, 16]], 'Search region', extra_text, '36d', True, for_paper = 'thesis')
    cleanUp(original_file)

def plotFig37():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
    #ch1 = EEE-Mu Hb
    #ch2 = EEE-Mu Ha
    #ch3 = MuMuMu-E Hb
    #ch4 = MuMuMu-E Ha
    #ch5 = TauEE Hb
    #ch6 = TauEE Ha
    #ch7 = TauEMu Ha
    #ch8 = TauMuMu Hb
    #ch9 = TauMuMu Ha
    
    channels = ['ch7']
    signal_files = {
        'HNL-tau-m85-Vsq1.0e+00-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m85-Vsq1.0e+00-prompt/Majorana/F-TauEMu-searchregion.shapes.root', 'F-TauEMu/HNL-tau-m85-Vsq1.0e+00-prompt']],
        'HNL-tau-m200-Vsq4.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m200-Vsq4.0em01-prompt/Majorana/F-TauEMu-searchregion.shapes.root', 'F-TauEMu/HNL-tau-m200-Vsq4.0em01-prompt']],
        'HNL-tau-m300-Vsq7.0em01-prompt' :
            [['default-highMassSR/UL2016post-2016pre-2017-2018/tau/HNL-tau-m300-Vsq7.0em01-prompt/Majorana/F-TauEMu-searchregion.shapes.root', 'F-TauEMu/HNL-tau-m300-Vsq7.0em01-prompt']]
    }
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = 4e-1)
    
    extra_text = loadExtraText('e#mu#tau_{h}', 'tau', 4e-1)
    drawPlot(hist_dict, output_base+'/PostFitPlotsForThesis/fig37', ['Ha{0}'.format(x) for x in xrange(1, 10)], 'Search region', extra_text, '37', True, for_paper = 'thesis')
    cleanUp(original_file)

if __name__ == '__main__':
    plotFig26a()
    #plotFig26b()
    #plotFig26c()
    
    #plotFig27a()
    #plotFig27b()
    #plotFig27c()

    #plotFig28a()
    #plotFig28b()
    #plotFig28c()
    #plotFig28d()
    #plotFig28e()
    #plotFig28f()

    #plotFig29a()
    #plotFig29b()
    #plotFig29c()
    #
    #plotFig30a()
    #plotFig30b()
    #plotFig30c()
    #plotFig30d()
    #
    #plotFig31a()
    #plotFig31b()
    #plotFig31c()
    #plotFig31d()
    #plotFig31e()
    #plotFig31f()
    #
    #plotFig32a()
    #plotFig32b()
    #plotFig32c()
    #plotFig32d()
    #plotFig32e()
    #plotFig32f()
    #
    #plotFig33a()
    #plotFig33b()
    #
    #plotFig34a()
    #plotFig34b()
    #
    #plotFig35a()
    #plotFig35b()
    #plotFig35c()
    #plotFig35d()
    #
    #plotFig36a()
    #plotFig36b()
    #plotFig36c()
    #plotFig36d()

    #plotFig37()
