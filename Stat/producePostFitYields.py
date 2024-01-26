from producePostFitPlotsForPaper import loadHistograms, loadExtraText, drawPlot, cleanUp, input_base, combineLateralyList
from HNL.HEPData.createYields import writePostfitYieldJson
import os
output_base = '/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/HEPDATA'

#base_folder should be a lambda function in which to insert the signal_name and dist_to_merge
def gatherSignalDict(base_folder, signal_names, dist_to_merge):
    signal_files = {}
    for s in signal_names:
        signal_files[s] = []
        from HNL.Samples.sample import Sample
        flavor = Sample.getSignalFlavor(s)
        for dtm in dist_to_merge:
            shortened = dtm.rsplit('-', 1)[0]
            signal_files[s].append([base_folder(flavor, s, dtm), shortened+'/'+s])
    return signal_files

signal_names_lowmass = ['HNL-e-m10-Vsq2.5em05-displaced', 'HNL-e-m12.5-Vsq2.5em05-displaced', 'HNL-e-m15-Vsq2.5em05-displaced', 'HNL-e-m17.5-Vsq2.5em05-displaced', 'HNL-e-m20-Vsq2.5em05-displaced', 'HNL-e-m25-Vsq2.5em05-displaced', 'HNL-e-m30-Vsq2.5em06-displaced', 'HNL-e-m40-Vsq6.0em06-prompt', 'HNL-e-m50-Vsq1.0em05-prompt', 'HNL-e-m60-Vsq2.0em05-prompt', 'HNL-e-m70-Vsq6.0em05-prompt', 'HNL-e-m75-Vsq5.0em04-prompt', 'HNL-mu-m10-Vsq2.5em05-displaced', 'HNL-mu-m12.5-Vsq2.5em05-displaced', 'HNL-mu-m15-Vsq2.5em05-displaced', 'HNL-mu-m17.5-Vsq2.5em05-displaced', 'HNL-mu-m20-Vsq2.5em05-displaced', 'HNL-mu-m25-Vsq2.5em05-displaced', 'HNL-mu-m30-Vsq2.5em05-displaced', 'HNL-mu-m40-Vsq2.0em06-prompt', 'HNL-mu-m50-Vsq3.0em06-prompt', 'HNL-mu-m60-Vsq6.0em06-prompt', 'HNL-mu-m70-Vsq5.0em05-prompt', 'HNL-mu-m75-Vsq1.0em04-prompt', 'HNL-tau-m10-Vsq5.0em04-displaced', 'HNL-tau-m12.5-Vsq5.0em04-displaced', 'HNL-tau-m15-Vsq5.0em04-displaced', 'HNL-tau-m17.5-Vsq5.0em04-displaced', 'HNL-tau-m20-Vsq5.0em04-displaced', 'HNL-tau-m25-Vsq5.0em04-displaced', 'HNL-tau-m30-Vsq5.0em04-displaced', 'HNL-tau-m40-Vsq6.0em04-prompt', 'HNL-tau-m50-Vsq7.0em04-prompt', 'HNL-tau-m60-Vsq2.0em03-prompt', 'HNL-tau-m75-Vsq3.0em02-prompt']

signal_names_highmass = ['HNL-e-m85-Vsq1.0em03-prompt', 'HNL-e-m100-Vsq1.0em03-prompt', 'HNL-e-m125-Vsq2.0em03-prompt', 'HNL-e-m150-Vsq3.0em03-prompt', 'HNL-e-m200-Vsq5.0em03-prompt', 'HNL-e-m250-Vsq5.0em03-prompt', 'HNL-e-m300-Vsq1.0em02-prompt', 'HNL-e-m350-Vsq2.0em02-prompt', 'HNL-e-m400-Vsq2.0em02-prompt', 'HNL-e-m450-Vsq5.0em02-prompt', 'HNL-e-m500-Vsq5.0em02-prompt', 'HNL-e-m600-Vsq6.0em02-prompt', 'HNL-e-m700-Vsq1.0em01-prompt', 'HNL-e-m800-Vsq2.0em01-prompt', 'HNL-e-m900-Vsq2.0em01-prompt', 'HNL-e-m1000-Vsq3.0em01-prompt', 'HNL-e-m1200-Vsq1.0e+00-prompt', 'HNL-e-m1500-Vsq1.0e+00-prompt', 'HNL-mu-m85-Vsq7.0em04-prompt', 'HNL-mu-m100-Vsq8.0em04-prompt', 'HNL-mu-m125-Vsq1.0em03-prompt', 'HNL-mu-m150-Vsq2.0em03-prompt', 'HNL-mu-m200-Vsq4.0em03-prompt', 'HNL-mu-m250-Vsq5.0em03-prompt', 'HNL-mu-m300-Vsq8.0em03-prompt', 'HNL-mu-m350-Vsq1.0em02-prompt', 'HNL-mu-m400-Vsq2.0em02-prompt', 'HNL-mu-m450-Vsq2.0em02-prompt', 'HNL-mu-m500-Vsq3.0em02-prompt', 'HNL-mu-m600-Vsq4.0em02-prompt', 'HNL-mu-m700-Vsq7.0em02-prompt', 'HNL-mu-m800-Vsq1.0em01-prompt', 'HNL-mu-m900-Vsq2.0em01-prompt', 'HNL-mu-m1000-Vsq2.0em01-prompt', 'HNL-mu-m1200-Vsq1.0e+00-prompt', 'HNL-mu-m1500-Vsq1.0e+00-prompt', 'HNL-tau-m85-Vsq1.0e+00-prompt', 'HNL-tau-m100-Vsq2.0em01-prompt', 'HNL-tau-m125-Vsq2.0em01-prompt', 'HNL-tau-m150-Vsq2.0em01-prompt', 'HNL-tau-m200-Vsq4.0em01-prompt', 'HNL-tau-m250-Vsq5.0em01-prompt', 'HNL-tau-m300-Vsq7.0em01-prompt', 'HNL-tau-m350-Vsq9.0em01-prompt', 'HNL-tau-m400-Vsq1.0e+00-prompt', 'HNL-tau-m450-Vsq1.0e+00-prompt', 'HNL-tau-m500-Vsq1.0e+00-prompt', 'HNL-tau-m600-Vsq1.0e+00-prompt', 'HNL-tau-m700-Vsq1.0e+00-prompt', 'HNL-tau-m800-Vsq1.0e+00-prompt', 'HNL-tau-m900-Vsq1.0e+00-prompt', 'HNL-tau-m1000-Vsq1.0e+00-prompt']

def filteredNames(names, keyword):
    return [x for x in names if keyword in x]

###############
# Figure 7.26 #
###############

def plotFig26a():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/e/HNL-e-m30-Vsq4.0em06-prompt/shapes/custom-lowestmass/postfit/NoTau')
    print original_file
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    channels = ['ch3', 'ch4']

    dist_names = ['C-EEE-Mu-lowestmasse', 'D-EEE-Mu-lowestmasse']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-e-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-e-lowestmass/EEE-Mu')
    
    cleanUp(original_file)
    
    channels = ['ch3']

    dist_names = ['C-EEE-Mu-lowestmasse']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-e-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-e-lowestmass-C/EEE-Mu')
    
    cleanUp(original_file)
    
    channels = ['ch4']

    dist_names = ['D-EEE-Mu-lowestmasse']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-e-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-e-lowestmass-D/EEE-Mu')
    
    cleanUp(original_file)

def plotFig26b():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/e/HNL-e-m30-Vsq4.0em06-prompt/shapes/custom-lowmass/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    channels = ['ch3', 'ch4']
    
    dist_names = ['C-EEE-Mu-lowmasse', 'D-EEE-Mu-lowmasse']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-e-'), dist_names)
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-e-lowmass/EEE-Mu')
    cleanUp(original_file)
    
    channels = ['ch3']
    
    dist_names = ['C-EEE-Mu-lowmasse']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-e-'), dist_names)
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-e-lowmass-C/EEE-Mu')
    cleanUp(original_file)
    
    channels = ['ch4']
    
    dist_names = ['D-EEE-Mu-lowmasse']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-e-'), dist_names)
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-e-lowmass-D/EEE-Mu')
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
    dist_names = ['A-EEE-Mu-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_lowmass, dist_names)
    hist_dict_A = loadHistograms(original_file, channels, signal_files, None)
    
    #Stepwise L5-8
    channels = ['ch3']
    dist_names = ['B-EEE-Mu-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_lowmass, dist_names)
    hist_dict_B = loadHistograms(original_file, channels, signal_files, None)
    
    #Stepwise L5-8
    channels = ['ch2']
    dist_names = ['C-EEE-Mu-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_lowmass, dist_names)
    hist_dict_C = loadHistograms(original_file, channels, signal_files, None)
    
    #Stepwise L5-8
    channels = ['ch4']
    dist_names = ['D-EEE-Mu-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_lowmass, dist_names)
    hist_dict_D = loadHistograms(original_file, channels, signal_files, None)
    
    #Combine
    hist_dict = combineLateralyList([hist_dict_A, hist_dict_B, hist_dict_C, hist_dict_D])
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/SR/EEE-Mu')
    cleanUp(original_file)

###############
# Figure 7.27 #
###############

def plotFig27a():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/mu/HNL-mu-m30-Vsq2.0em06-prompt/shapes/custom-lowestmass/postfit/NoTau')
    #ch7 = MuMuMu-E L9-12
    #ch8 = MuMuMu-E L13-16
    channels = ['ch7', 'ch8']
    
    dist_names = ['C-MuMuMu-E-lowestmassmu', 'D-MuMuMu-E-lowestmassmu']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-mu-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-mu-lowestmass/MuMuMu-E')
    cleanUp(original_file)
    
    channels = ['ch7']
    
    dist_names = ['C-MuMuMu-E-lowestmassmu']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-mu-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-mu-lowestmass-C/MuMuMu-E')
    cleanUp(original_file)
    
    channels = ['ch8']
    
    dist_names = ['D-MuMuMu-E-lowestmassmu']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-mu-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-mu-lowestmass-D/MuMuMu-E')
    cleanUp(original_file)

def plotFig27b():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/mu/HNL-mu-m30-Vsq2.0em06-prompt/shapes/custom-lowmass/postfit/NoTau')
    #ch7 = MuMuMu-E L9-12
    #ch8 = MuMuMu-E L13-16
    channels = ['ch7', 'ch8']
    
    dist_names = ['C-MuMuMu-E-lowmassmu', 'D-MuMuMu-E-lowmassmu']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-mu-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-mu-lowmass/MuMuMu-E')
    cleanUp(original_file)
    
    channels = ['ch7']
    
    dist_names = ['C-MuMuMu-E-lowmassmu']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-mu-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-mu-lowmass-C/MuMuMu-E')
    cleanUp(original_file)
    
    channels = ['ch8']
    
    dist_names = ['D-MuMuMu-E-lowmassmu']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-mu-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-mu-lowmass-D/MuMuMu-E')
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
    dist_names = ['A-MuMuMu-E-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_lowmass, dist_names)
    hist_dict_A = loadHistograms(original_file, channels, signal_files, None)

    #Stepwise L5-8
    channels = ['ch7']
    dist_names = ['B-MuMuMu-E-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_lowmass, dist_names)
    hist_dict_B = loadHistograms(original_file, channels, signal_files, None)
    
    #Stepwise L5-8
    channels = ['ch6']
    dist_names = ['C-MuMuMu-E-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_lowmass, dist_names)
    hist_dict_C = loadHistograms(original_file, channels, signal_files, None)
    
    #Stepwise L5-8
    channels = ['ch8']
    dist_names = ['D-MuMuMu-E-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_lowmass, dist_names)
    hist_dict_D = loadHistograms(original_file, channels, signal_files, None)
    
    #Combine
    hist_dict = combineLateralyList([hist_dict_A, hist_dict_B, hist_dict_C, hist_dict_D])
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/SR/MuMuMu-E')
    cleanUp(original_file)


def plotFig28c():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowestmass/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    #ch7 = MuMuMu-E L9-12
    #ch8 = MuMuMu-E L13-16
    channels = ['ch3', 'ch4']
    dist_names = ['C-EEE-Mu-lowestmasstaulep', 'D-EEE-Mu-lowestmasstaulep']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-taulep-lowestmass/EEE-Mu')
    
    cleanUp(original_file)
    
    channels = ['ch3']
    dist_names = ['C-EEE-Mu-lowestmasstaulep']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-taulep-lowestmass-C/EEE-Mu')
    
    cleanUp(original_file)
    
    channels = ['ch4']
    dist_names = ['D-EEE-Mu-lowestmasstaulep']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-taulep-lowestmass-D/EEE-Mu')
    
    cleanUp(original_file)
    
def plotFig28d():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowestmass/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    #ch7 = MuMuMu-E L9-12
    #ch8 = MuMuMu-E L13-16
    channels = ['ch7', 'ch8']
    dist_names = ['C-MuMuMu-E-lowestmasstaulep', 'D-MuMuMu-E-lowestmasstaulep']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-taulep-lowestmass/MuMuMu-E')
    cleanUp(original_file)
    
    channels = ['ch7']
    dist_names = ['C-MuMuMu-E-lowestmasstaulep']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-taulep-lowestmass-C/MuMuMu-E')
    cleanUp(original_file)
    
    channels = ['ch8']
    dist_names = ['D-MuMuMu-E-lowestmasstaulep']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-taulep-lowestmass-D/MuMuMu-E')
    cleanUp(original_file)
    
def plotFig28e():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowmass/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    #ch7 = MuMuMu-E L9-12
    #ch8 = MuMuMu-E L13-16
    channels = ['ch3', 'ch4']
    dist_names = ['C-EEE-Mu-lowmasstaulep', 'D-EEE-Mu-lowmasstaulep']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-taulep-lowmass/EEE-Mu')
    
    cleanUp(original_file)
    
    channels = ['ch3']
    dist_names = ['C-EEE-Mu-lowmasstaulep']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-taulep-lowmass-C/EEE-Mu')
    
    cleanUp(original_file)
    
    channels = ['ch4']
    dist_names = ['D-EEE-Mu-lowmasstaulep']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-taulep-lowmass-D/EEE-Mu')
    
    cleanUp(original_file)

def plotFig28f():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowmass/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    #ch7 = MuMuMu-E L9-12
    #ch8 = MuMuMu-E L13-16
    channels = ['ch7', 'ch8']
    dist_names = ['C-MuMuMu-E-lowmasstaulep', 'D-MuMuMu-E-lowmasstaulep']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-taulep-lowmass/MuMuMu-E')
    
    cleanUp(original_file)
    
    channels = ['ch7']
    dist_names = ['C-MuMuMu-E-lowmasstaulep']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-taulep-lowmass-C/MuMuMu-E')
    
    cleanUp(original_file)
    
    channels = ['ch8']
    dist_names = ['D-MuMuMu-E-lowmasstaulep']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-taulep-lowmass-D/MuMuMu-E')
    
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
    dist_names = ['A-TauEE-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_lowmass, dist_names)
    hist_dict_A = loadHistograms(original_file, channels, signal_files, None)
    cleanUp(original_file)
    
    #Stepwise L5-8
    channels = ['ch3']
    dist_names = ['B-TauEE-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_lowmass, dist_names)
    hist_dict_B = loadHistograms(original_file, channels, signal_files, None)
    cleanUp(original_file)
    
    #Stepwise L9-12
    channels = ['ch2']
    dist_names = ['C-TauEE-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_lowmass, dist_names)
    hist_dict_C = loadHistograms(original_file, channels, signal_files, None)
    cleanUp(original_file)
    
    #Stepwise L13-16
    channels = ['ch4']
    dist_names = ['D-TauEE-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_lowmass, dist_names)
    hist_dict_D = loadHistograms(original_file, channels, signal_files, None)
    
    #Combine
    hist_dict = combineLateralyList([hist_dict_A, hist_dict_B, hist_dict_C, hist_dict_D])
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/SR/TauEE')
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
    dist_names = ['A-TauMuMu-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_lowmass, dist_names)
    hist_dict_A = loadHistograms(original_file, channels, signal_files, None)
    cleanUp(original_file)
    
    #Stepwise L5-8
    channels = ['ch9']
    dist_names = ['B-TauMuMu-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_lowmass, dist_names)
    hist_dict_B = loadHistograms(original_file, channels, signal_files, None)
    cleanUp(original_file)
    
    #Stepwise L9-12
    channels = ['ch8']
    dist_names = ['C-TauMuMu-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_lowmass, dist_names)
    hist_dict_C = loadHistograms(original_file, channels, signal_files, None)
    cleanUp(original_file)
    
    #Stepwise L13-16
    channels = ['ch10']
    dist_names = ['D-TauMuMu-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_lowmass, dist_names)
    hist_dict_D = loadHistograms(original_file, channels, signal_files, None)
    
    #Combine
    hist_dict = combineLateralyList([hist_dict_A, hist_dict_B, hist_dict_C, hist_dict_D])
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/SR/TauMuMu')
    cleanUp(original_file)

def setNaBins(in_hist):
    from HNL.Tools.histogram import Histogram
    hist = in_hist.getHist()
    n_bins = hist.GetNbinsX()
    from ROOT import TH1F
    new_hist = Histogram(TH1F(hist.GetName(), hist.GetTitle(), n_bins, 0, n_bins))
    for b in xrange(1, new_hist.getHist().GetNbinsX()+1):
        new_hist.getHist().SetBinContent(b, -999.)
        new_hist.getHist().SetBinError(b, 0.)
    return new_hist

def setNaBinsAll(hist_dict):
    out_dict = {}
    out_dict['bkgr_names'] = [x for x in hist_dict['bkgr_names']]
    out_dict['signal_names'] = [x for x in hist_dict['signal_names']]
    out_dict['bkgr_hist'] = []
    out_dict['signal_hist'] = []

    for b in hist_dict['bkgr_hist']:
        out_dict['bkgr_hist'].append(setNaBins(b))
    for s in hist_dict['signal_hist']:
        out_dict['signal_hist'].append(setNaBins(s))
    out_dict['observed'] = setNaBins(hist_dict['observed'])
    out_dict['syst'] = setNaBins(hist_dict['syst'])

    return out_dict

def addEmptyBin(hist, b):
    from HNL.Tools.histogram import Histogram
    n_bins = hist.getHist().GetNbinsX()
    from ROOT import TH1F
    new_hist = Histogram(TH1F(hist.getHist().GetName(), hist.getHist().GetTitle(), n_bins+1, 0, n_bins+1))
    for o_b in xrange(1, n_bins+2):
        if o_b < b:
            new_hist.getHist().SetBinContent(o_b, hist.getHist().GetBinContent(o_b))
            new_hist.getHist().SetBinError(o_b, hist.getHist().GetBinError(o_b))
        elif o_b == b:
            new_hist.getHist().SetBinContent(o_b, -1.)
            new_hist.getHist().SetBinError(o_b, 0)
        else:
            new_hist.getHist().SetBinContent(o_b, hist.getHist().GetBinContent(o_b-1))
            new_hist.getHist().SetBinError(o_b, hist.getHist().GetBinError(o_b-1))
    return new_hist

def addEmptyBinList(list_of_hist, b):
    out_dict = {}
    out_dict['bkgr_names'] = [x for x in list_of_hist['bkgr_names']]
    out_dict['signal_names'] = [x for x in list_of_hist['signal_names']]
    out_dict['bkgr_hist'] = []
    out_dict['signal_hist'] = []
    
    out_dict['observed'] = addEmptyBin(list_of_hist['observed'], b)
    out_dict['syst'] = addEmptyBin(list_of_hist['syst'], b)

    for s in list_of_hist['signal_hist']:
        out_dict['signal_hist'].append(addEmptyBin(s, b))
    for s in list_of_hist['bkgr_hist']:
        out_dict['bkgr_hist'].append(addEmptyBin(s, b))
    return out_dict


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
    dist_names = ['A-TauEMu-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_lowmass, dist_names)
    hist_dict_A = loadHistograms(original_file, channels, signal_files, None)
    cleanUp(original_file)
    
    #Stepwise L5-8
    channels = ['ch6']
    dist_names = ['B-TauEMu-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_lowmass, dist_names)
    hist_dict_B = loadHistograms(original_file, channels, signal_files, None)
    cleanUp(original_file)

    #Stepwise L9-12
    channels = ['ch8']
    dist_names = ['C-TauMuMu-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_lowmass, dist_names)
    hist_dict_C = loadHistograms(original_file, channels, signal_files, None)
    hist_dict_C = setNaBinsAll(hist_dict_C)
    cleanUp(original_file)

    #Stepwise L13-16
    channels = ['ch10']
    dist_names = ['D-TauMuMu-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_lowmass, dist_names)
    hist_dict_D = loadHistograms(original_file, channels, signal_files, None)
    hist_dict_D = setNaBinsAll(hist_dict_D)
   
 
    #Combine
    hist_dict = combineLateralyList([hist_dict_A, hist_dict_B, hist_dict_C, hist_dict_D])
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/SR/TauEMu')
    cleanUp(original_file)


def plotFig30a():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowestmass/postfit/SingleTau')
    #ch3 = TauEE L9-12
    #ch4 = TauEE L13-16
    #ch9 = TauMuMu L9-12
    #ch10 = TauMuMu L13-16

    channels = ['ch3', 'ch4']
    dist_names = ['C-TauEE-lowestmasstauhad', 'D-TauEE-lowestmasstauhad']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-tauhad-lowestmass/TauEE')
    
    cleanUp(original_file)
    
    channels = ['ch3']
    dist_names = ['C-TauEE-lowestmasstauhad']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-tauhad-lowestmass-C/TauEE')
    
    cleanUp(original_file)
    
    channels = ['ch4']
    dist_names = ['D-TauEE-lowestmasstauhad']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-tauhad-lowestmass-D/TauEE')
    
    cleanUp(original_file)

def plotFig30b():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowestmass/postfit/SingleTau')
    #ch3 = TauEE L9-12
    #ch4 = TauEE L13-16
    #ch9 = TauMuMu L9-12
    #ch10 = TauMuMu L13-16

    channels = ['ch9', 'ch10']
    dist_names = ['C-TauMuMu-lowestmasstauhad', 'D-TauMuMu-lowestmasstauhad']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-tauhad-lowestmass/TauMuMu')
    
    cleanUp(original_file)
    
    channels = ['ch9']
    dist_names = ['C-TauMuMu-lowestmasstauhad']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-tauhad-lowestmass-C/TauMuMu')
    
    cleanUp(original_file)
    
    channels = ['ch10']
    dist_names = ['D-TauMuMu-lowestmasstauhad']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-tauhad-lowestmass-D/TauMuMu')
    
    cleanUp(original_file)

def plotFig30c():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowmass/postfit/SingleTau')
    #ch3 = TauEE L9-12
    #ch4 = TauEE L13-16
    #ch9 = TauMuMu L9-12
    #ch10 = TauMuMu L13-16

    channels = ['ch3', 'ch4']
    dist_names = ['C-TauEE-lowmasstauhad', 'D-TauEE-lowmasstauhad']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-tauhad-lowmass/TauEE')
    
    cleanUp(original_file)
    
    channels = ['ch3']
    dist_names = ['C-TauEE-lowmasstauhad']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-tauhad-lowmass-C/TauEE')
    
    cleanUp(original_file)
    
    channels = ['ch4']
    dist_names = ['D-TauEE-lowmasstauhad']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-tauhad-lowmass-D/TauEE')
    
    cleanUp(original_file)

def plotFig30d():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/custom-lowmass/postfit/SingleTau')
    #ch3 = TauEE L9-12
    #ch4 = TauEE L13-16
    #ch9 = TauMuMu L9-12
    #ch10 = TauMuMu L13-16

    channels = ['ch9', 'ch10']
    dist_names = ['C-TauMuMu-lowmasstauhad', 'D-TauMuMu-lowmasstauhad']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-tauhad-lowmass/TauMuMu')
    
    cleanUp(original_file)
   
    channels = ['ch9']
    dist_names = ['C-TauMuMu-lowmasstauhad']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-tauhad-lowmass-C/TauMuMu')
    
    cleanUp(original_file)
    
    channels = ['ch10']
    dist_names = ['D-TauMuMu-lowmasstauhad']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_lowmass, '-tau-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/LowMass/bdt-tauhad-lowmass-D/TauMuMu')
    
    cleanUp(original_file)

def plotFig31a():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/e/HNL-e-m200-Vsq5.0em03-prompt/shapes/custom-mediummass85100/postfit/NoTau')
    #ch1 = EEE-Mu E
    #ch2 = EEE-Mu F
    channels = ['ch1']
    dist_names = ['E-EEE-Mu-mediummass85100e']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_highmass, '-e-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/HighMass/bdt-e-medium85100mass-Hb/EEE-Mu')
    
    cleanUp(original_file)

def plotFig31b():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/e/HNL-e-m200-Vsq5.0em03-prompt/shapes/custom-mediummass85100/postfit/NoTau')
    #ch1 = EEE-Mu E
    #ch2 = EEE-Mu F
    channels = ['ch2']
    dist_names = ['F-EEE-Mu-mediummass85100e']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_highmass, '-e-'), dist_names)
    
    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/HighMass/bdt-e-medium85100mass-Ha/EEE-Mu')
    
    cleanUp(original_file)

def plotFig31c():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/e/HNL-e-m200-Vsq5.0em03-prompt/shapes/custom-mediummass150200/postfit/NoTau')
    #ch3 = EEE-Mu E
    #ch4 = EEE-Mu F
    channels = ['ch1']
    dist_names = ['E-EEE-Mu-mediummass150200e']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_highmass, '-e-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/HighMass/bdt-e-medium150200mass-Hb/EEE-Mu')
    
    cleanUp(original_file)

def plotFig31d():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/e/HNL-e-m200-Vsq5.0em03-prompt/shapes/custom-mediummass150200/postfit/NoTau')
    #ch3 = EEE-Mu E
    #ch4 = EEE-Mu F
    channels = ['ch2']
    dist_names = ['F-EEE-Mu-mediummass150200e']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_highmass, '-e-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/HighMass/bdt-e-medium150200mass-Ha/EEE-Mu')
    
    cleanUp(original_file)

def plotFig31e():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/e/HNL-e-m200-Vsq5.0em03-prompt/shapes/custom-mediummass250400/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    channels = ['ch1']
    dist_names = ['E-EEE-Mu-mediummass250400e']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_highmass, '-e-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/HighMass/bdt-e-medium250400mass-Hb/EEE-Mu')
    
    cleanUp(original_file)

def plotFig31f():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/e/HNL-e-m200-Vsq5.0em03-prompt/shapes/custom-mediummass250400/postfit/NoTau')
    #ch3 = EEE-Mu L9-12
    #ch4 = EEE-Mu L13-16
    channels = ['ch2']
    dist_names = ['F-EEE-Mu-mediummass250400e']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_highmass, '-e-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/HighMass/bdt-e-medium250400mass-Ha/EEE-Mu')
    
    cleanUp(original_file)

def plotFig32a():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/mu/HNL-mu-m200-Vsq4.0em03-prompt/shapes/custom-mediummass85100/postfit/NoTau')
    #ch3 = MuMuMu-E E
    #ch4 = MuMuMu-E F
    channels = ['ch3']
    dist_names = ['E-MuMuMu-E-mediummass85100mu']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_highmass, '-mu-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/HighMass/bdt-mu-medium85100mass-Hb/MuMuMu-E')
    
    cleanUp(original_file)

    

def plotFig32b():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/mu/HNL-mu-m200-Vsq4.0em03-prompt/shapes/custom-mediummass85100/postfit/NoTau')
    #ch3 = MuMuMu-E E
    #ch4 = MuMuMu-E F
    channels = ['ch4']
    dist_names = ['F-MuMuMu-E-mediummass85100mu']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_highmass, '-mu-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/HighMass/bdt-mu-medium85100mass-Ha/MuMuMu-E')
    
    cleanUp(original_file)

def plotFig32c():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/mu/HNL-mu-m200-Vsq4.0em03-prompt/shapes/custom-mediummass150200/postfit/NoTau')
    #ch3 = MuMuMu-E E
    #ch4 = MuMuMu-E F
    channels = ['ch3']
    dist_names = ['E-MuMuMu-E-mediummass150200mu']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_highmass, '-mu-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/HighMass/bdt-mu-medium150200mass-Hb/MuMuMu-E')
    
    cleanUp(original_file)

def plotFig32d():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/mu/HNL-mu-m200-Vsq4.0em03-prompt/shapes/custom-mediummass150200/postfit/NoTau')
    #ch3 = MuMuMu-E E
    #ch4 = MuMuMu-E F
    channels = ['ch4']
    dist_names = ['F-MuMuMu-E-mediummass150200mu']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_highmass, '-mu-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/HighMass/bdt-mu-medium150200mass-Ha/MuMuMu-E')
    
    cleanUp(original_file)

def plotFig32e():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/mu/HNL-mu-m200-Vsq4.0em03-prompt/shapes/custom-mediummass250400/postfit/NoTau')
    #ch3 = MuMuMu-E E
    #ch4 = MuMuMu-E F
    channels = ['ch3']
    dist_names = ['E-MuMuMu-E-mediummass250400mu']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_highmass, '-mu-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/HighMass/bdt-mu-medium250400mass-Hb/MuMuMu-E')
    
    cleanUp(original_file)

def plotFig32f():
    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/mu/HNL-mu-m200-Vsq4.0em03-prompt/shapes/custom-mediummass250400/postfit/NoTau')
    #ch3 = MuMuMu-E E
    #ch4 = MuMuMu-E F
    channels = ['ch4']
    dist_names = ['F-MuMuMu-E-mediummass250400mu']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', filteredNames(signal_names_highmass, '-mu-'), dist_names)

    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    writePostfitYieldJson(hist_dict, output_base+'/HighMass/bdt-mu-medium250400mass-Hb/MuMuMu-E')
    
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
    dist_names = ['F-EEE-Mu-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_highmass, dist_names)
    hist_dict_F = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    
    channels = ['ch1']
    dist_names = ['E-EEE-Mu-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_highmass, dist_names)
    hist_dict_E = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    
    hist_dict = combineLateralyList([hist_dict_F, hist_dict_E])
    writePostfitYieldJson(hist_dict, output_base+'/HighMass/SR/EEE-Mu')
    
    cleanUp(original_file)


#def plotFig33b():
#    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
#    #ch1 = EEE-Mu Hb
#    #ch2 = EEE-Mu Ha
#    #ch3 = MuMuMu-E Hb
#    #ch4 = MuMuMu-E Ha
#    #ch5 = TauEE Hb
#    #ch6 = TauEE Ha
#    #ch7 = TauEMu Ha
#    #ch8 = TauMuMu Hb
#    #ch9 = TauMuMu Ha
#    
#    #Stepwise first L1-4
#    channels = ['ch1']
#    dist_names = ['E-EEE-Mu-searchregion']
#    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_highmass, dist_names)
#
#    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
#    writePostfitYieldJson(hist_dict, output_base+'/HighMass/SR-Hb/EEE-Mu')
#    
#    cleanUp(original_file)

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
    dist_names = ['F-MuMuMu-E-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_highmass, dist_names)
    hist_dict_F = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    
    channels = ['ch3']
    dist_names = ['E-MuMuMu-E-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_highmass, dist_names)
    hist_dict_E = loadHistograms(original_file, channels, signal_files, target_coupling = None)

    hist_dict = combineLateralyList([hist_dict_F, hist_dict_E])
    print hist_dict
    writePostfitYieldJson(hist_dict, output_base+'/HighMass/SR/MuMuMu-E')
    
    cleanUp(original_file)

#def plotFig34b():
#    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
#    #ch1 = EEE-Mu Hb
#    #ch2 = EEE-Mu Ha
#    #ch3 = MuMuMu-E Hb
#    #ch4 = MuMuMu-E Ha
#    #ch5 = TauEE Hb
#    #ch6 = TauEE Ha
#    #ch7 = TauEMu Ha
#    #ch8 = TauMuMu Hb
#    #ch9 = TauMuMu Ha
#    
#    #Stepwise first L1-4
#    channels = ['ch3']
#    dist_names = ['E-MuMuMu-E-searchregion']
#    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_highmass, dist_names)
#
#    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
#    writePostfitYieldJson(hist_dict, output_base+'/HighMass/SR-Hb/MuMuMu-E')
#    
#    cleanUp(original_file)

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
    dist_names = ['F-TauEE-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_highmass, dist_names)
    hist_dict_F = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    
    channels = ['ch5']
    dist_names = ['E-TauEE-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_highmass, dist_names)
    hist_dict_E = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    hist_dict_E = addEmptyBinList(hist_dict_E, 2)

    hist_dict = combineLateralyList([hist_dict_F, hist_dict_E])
    writePostfitYieldJson(hist_dict, output_base+'/HighMass/SR/TauEE')
    
    cleanUp(original_file)

#def plotFig36b():
#    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
#    #ch1 = EEE-Mu Hb
#    #ch2 = EEE-Mu Ha
#    #ch3 = MuMuMu-E Hb
#    #ch4 = MuMuMu-E Ha
#    #ch5 = TauEE Hb
#    #ch6 = TauEE Ha
#    #ch7 = TauEMu Ha
#    #ch8 = TauMuMu Hb
#    #ch9 = TauMuMu Ha
#    
#    channels = ['ch5']
#    dist_names = ['E-TauEE-searchregion']
#    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_highmass, dist_names)
#    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
#    writePostfitYieldJson(hist_dict, output_base+'/HighMass/SR-Hb/TauEE')
#    
#    cleanUp(original_file)

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
    dist_names = ['F-TauMuMu-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_highmass, dist_names)
    hist_dict_F = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    
    channels = ['ch8']
    dist_names = ['E-TauMuMu-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_highmass, dist_names)
    hist_dict_E = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    hist_dict_E = addEmptyBinList(hist_dict_E, 2)
    
    hist_dict = combineLateralyList([hist_dict_F, hist_dict_E])
    writePostfitYieldJson(hist_dict, output_base+'/HighMass/SR/TauMuMu')
    
    cleanUp(original_file)

#def plotFig36d():
#    original_file = os.path.join(input_base, 'Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau')
#    #ch1 = EEE-Mu Hb
#    #ch2 = EEE-Mu Ha
#    #ch3 = MuMuMu-E Hb
#    #ch4 = MuMuMu-E Ha
#    #ch5 = TauEE Hb
#    #ch6 = TauEE Ha
#    #ch7 = TauEMu Ha
#    #ch8 = TauMuMu Hb
#    #ch9 = TauMuMu Ha
#    
#    channels = ['ch8']
#    dist_names = ['E-TauMuMu-searchregion']
#    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_highmass, dist_names)
#    hist_dict = loadHistograms(original_file, channels, signal_files, target_coupling = None)
#    
#    writePostfitYieldJson(hist_dict, output_base+'/HighMass/SR-Hb/TauMuMu')
#    
#    cleanUp(original_file)

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
    dist_names = ['F-TauEMu-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_highmass, dist_names)
    hist_dict_F = loadHistograms(original_file, channels, signal_files, target_coupling = None)
   
    channels = ['ch8']
    dist_names = ['E-TauMuMu-searchregion']
    signal_files = gatherSignalDict(lambda f,s,d : 'default-highMassSR/UL2016post-2016pre-2017-2018/'+f+'/'+s+'/Majorana/'+d+'.shapes.root', signal_names_highmass, dist_names)
    hist_dict_E = loadHistograms(original_file, channels, signal_files, target_coupling = None)
    hist_dict_E = addEmptyBinList(hist_dict_E, 2)
    hist_dict_E = setNaBinsAll(hist_dict_E)
 
    hist_dict = combineLateralyList([hist_dict_F, hist_dict_E])
    writePostfitYieldJson(hist_dict, output_base+'/HighMass/SR/TauEMu')
    
    cleanUp(original_file)

if __name__ == '__main__':
    #plotFig26a()
    #plotFig26b()
    #plotFig26c()
    
    #plotFig27a()
    #plotFig27b()
    #plotFig27c()

    #plotFig28c()
    #plotFig28d()
    #plotFig28e()
    #plotFig28f()
#
#    plotFig29a()
#    plotFig29b()
#    plotFig29c()
    
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
    plotFig33a()
    #plotFig33b()
    #
    plotFig34a()
    #plotFig34b()
    #
    plotFig36a()
    #plotFig36b()
    plotFig36c()
    #plotFig36d()

    plotFig37()
