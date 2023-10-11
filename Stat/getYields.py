from HNL.Tools.helpers import getObjFromFile
import os

def getYield(in_hist):
    tot_yield = 0.
    for h in in_hist:
        tot_yield += h.GetSumOfWeights()
    return tot_yield
        
        
base_file = '/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/shapes'
#Mu 10GeV Prompt
in_hist = []
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m10-Vsq2.0em06-prompt/Majorana/A-EEE-Mu-searchregion.shapes.root'), 'A-EEE-Mu/HNL-mu-m10-Vsq2.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m10-Vsq2.0em06-prompt/Majorana/B-EEE-Mu-searchregion.shapes.root'), 'B-EEE-Mu/HNL-mu-m10-Vsq2.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m10-Vsq2.0em06-prompt/Majorana/C-EEE-Mu-searchregion.shapes.root'), 'C-EEE-Mu/HNL-mu-m10-Vsq2.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m10-Vsq2.0em06-prompt/Majorana/D-EEE-Mu-searchregion.shapes.root'), 'D-EEE-Mu/HNL-mu-m10-Vsq2.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m10-Vsq2.0em06-prompt/Majorana/A-MuMuMu-E-searchregion.shapes.root'), 'A-MuMuMu-E/HNL-mu-m10-Vsq2.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m10-Vsq2.0em06-prompt/Majorana/B-MuMuMu-E-searchregion.shapes.root'), 'B-MuMuMu-E/HNL-mu-m10-Vsq2.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m10-Vsq2.0em06-prompt/Majorana/C-MuMuMu-E-searchregion.shapes.root'), 'C-MuMuMu-E/HNL-mu-m10-Vsq2.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m10-Vsq2.0em06-prompt/Majorana/D-MuMuMu-E-searchregion.shapes.root'), 'D-MuMuMu-E/HNL-mu-m10-Vsq2.0em06-prompt'))

print 'Mu prompt 10 GeV:', '\t\t\t', getYield(in_hist) * 1.25

#Mu 10GeV Displaced
in_hist = []
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m10-Vsq2.5em06-displaced/Majorana/A-EEE-Mu-searchregion.shapes.root'), 'A-EEE-Mu/HNL-mu-m10-Vsq2.5em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m10-Vsq2.5em06-displaced/Majorana/B-EEE-Mu-searchregion.shapes.root'), 'B-EEE-Mu/HNL-mu-m10-Vsq2.5em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m10-Vsq2.5em06-displaced/Majorana/C-EEE-Mu-searchregion.shapes.root'), 'C-EEE-Mu/HNL-mu-m10-Vsq2.5em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m10-Vsq2.5em06-displaced/Majorana/D-EEE-Mu-searchregion.shapes.root'), 'D-EEE-Mu/HNL-mu-m10-Vsq2.5em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m10-Vsq2.5em06-displaced/Majorana/A-MuMuMu-E-searchregion.shapes.root'), 'A-MuMuMu-E/HNL-mu-m10-Vsq2.5em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m10-Vsq2.5em06-displaced/Majorana/B-MuMuMu-E-searchregion.shapes.root'), 'B-MuMuMu-E/HNL-mu-m10-Vsq2.5em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m10-Vsq2.5em06-displaced/Majorana/C-MuMuMu-E-searchregion.shapes.root'), 'C-MuMuMu-E/HNL-mu-m10-Vsq2.5em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m10-Vsq2.5em06-displaced/Majorana/D-MuMuMu-E-searchregion.shapes.root'), 'D-MuMuMu-E/HNL-mu-m10-Vsq2.5em06-displaced'))

print 'Mu displaced 10 GeV:', '\t\t\t', getYield(in_hist)

#E 10GeV Prompt
in_hist = []
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m10-Vsq4.0em06-prompt/Majorana/A-EEE-Mu-searchregion.shapes.root'), 'A-EEE-Mu/HNL-e-m10-Vsq4.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m10-Vsq4.0em06-prompt/Majorana/B-EEE-Mu-searchregion.shapes.root'), 'B-EEE-Mu/HNL-e-m10-Vsq4.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m10-Vsq4.0em06-prompt/Majorana/C-EEE-Mu-searchregion.shapes.root'), 'C-EEE-Mu/HNL-e-m10-Vsq4.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m10-Vsq4.0em06-prompt/Majorana/D-EEE-Mu-searchregion.shapes.root'), 'D-EEE-Mu/HNL-e-m10-Vsq4.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m10-Vsq4.0em06-prompt/Majorana/A-MuMuMu-E-searchregion.shapes.root'), 'A-MuMuMu-E/HNL-e-m10-Vsq4.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m10-Vsq4.0em06-prompt/Majorana/B-MuMuMu-E-searchregion.shapes.root'), 'B-MuMuMu-E/HNL-e-m10-Vsq4.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m10-Vsq4.0em06-prompt/Majorana/C-MuMuMu-E-searchregion.shapes.root'), 'C-MuMuMu-E/HNL-e-m10-Vsq4.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m10-Vsq4.0em06-prompt/Majorana/D-MuMuMu-E-searchregion.shapes.root'), 'D-MuMuMu-E/HNL-e-m10-Vsq4.0em06-prompt'))

print 'e prompt 10 GeV:', '\t\t\t', getYield(in_hist) * 1.25

#E 10GeV Displaced
in_hist = []
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m10-Vsq5.0em06-displaced/Majorana/A-EEE-Mu-searchregion.shapes.root'), 'A-EEE-Mu/HNL-e-m10-Vsq5.0em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m10-Vsq5.0em06-displaced/Majorana/B-EEE-Mu-searchregion.shapes.root'), 'B-EEE-Mu/HNL-e-m10-Vsq5.0em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m10-Vsq5.0em06-displaced/Majorana/C-EEE-Mu-searchregion.shapes.root'), 'C-EEE-Mu/HNL-e-m10-Vsq5.0em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m10-Vsq5.0em06-displaced/Majorana/D-EEE-Mu-searchregion.shapes.root'), 'D-EEE-Mu/HNL-e-m10-Vsq5.0em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m10-Vsq5.0em06-displaced/Majorana/A-MuMuMu-E-searchregion.shapes.root'), 'A-MuMuMu-E/HNL-e-m10-Vsq5.0em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m10-Vsq5.0em06-displaced/Majorana/B-MuMuMu-E-searchregion.shapes.root'), 'B-MuMuMu-E/HNL-e-m10-Vsq5.0em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m10-Vsq5.0em06-displaced/Majorana/C-MuMuMu-E-searchregion.shapes.root'), 'C-MuMuMu-E/HNL-e-m10-Vsq5.0em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m10-Vsq5.0em06-displaced/Majorana/D-MuMuMu-E-searchregion.shapes.root'), 'D-MuMuMu-E/HNL-e-m10-Vsq5.0em06-displaced'))

print 'e displaced 10 GeV:', '\t\t\t', getYield(in_hist)

#Mu 20GeV Prompt
in_hist = []
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/A-EEE-Mu-searchregion.shapes.root'), 'A-EEE-Mu/HNL-mu-m20-Vsq2.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/B-EEE-Mu-searchregion.shapes.root'), 'B-EEE-Mu/HNL-mu-m20-Vsq2.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/C-EEE-Mu-searchregion.shapes.root'), 'C-EEE-Mu/HNL-mu-m20-Vsq2.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/D-EEE-Mu-searchregion.shapes.root'), 'D-EEE-Mu/HNL-mu-m20-Vsq2.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/A-MuMuMu-E-searchregion.shapes.root'), 'A-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/B-MuMuMu-E-searchregion.shapes.root'), 'B-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/C-MuMuMu-E-searchregion.shapes.root'), 'C-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.0em06-prompt/Majorana/D-MuMuMu-E-searchregion.shapes.root'), 'D-MuMuMu-E/HNL-mu-m20-Vsq2.0em06-prompt'))

print 'Mu prompt 20 GeV:', '\t\t\t', getYield(in_hist) * 1.25

#Mu 20GeV Displaced
in_hist = []
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.5em06-displaced/Majorana/A-EEE-Mu-searchregion.shapes.root'), 'A-EEE-Mu/HNL-mu-m20-Vsq2.5em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.5em06-displaced/Majorana/B-EEE-Mu-searchregion.shapes.root'), 'B-EEE-Mu/HNL-mu-m20-Vsq2.5em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.5em06-displaced/Majorana/C-EEE-Mu-searchregion.shapes.root'), 'C-EEE-Mu/HNL-mu-m20-Vsq2.5em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.5em06-displaced/Majorana/D-EEE-Mu-searchregion.shapes.root'), 'D-EEE-Mu/HNL-mu-m20-Vsq2.5em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.5em06-displaced/Majorana/A-MuMuMu-E-searchregion.shapes.root'), 'A-MuMuMu-E/HNL-mu-m20-Vsq2.5em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.5em06-displaced/Majorana/B-MuMuMu-E-searchregion.shapes.root'), 'B-MuMuMu-E/HNL-mu-m20-Vsq2.5em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.5em06-displaced/Majorana/C-MuMuMu-E-searchregion.shapes.root'), 'C-MuMuMu-E/HNL-mu-m20-Vsq2.5em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/mu/HNL-mu-m20-Vsq2.5em06-displaced/Majorana/D-MuMuMu-E-searchregion.shapes.root'), 'D-MuMuMu-E/HNL-mu-m20-Vsq2.5em06-displaced'))

print 'Mu displaced 20 GeV:', '\t\t\t', getYield(in_hist)

#E 20GeV Prompt
in_hist = []
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/A-EEE-Mu-searchregion.shapes.root'), 'A-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/B-EEE-Mu-searchregion.shapes.root'), 'B-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/C-EEE-Mu-searchregion.shapes.root'), 'C-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/D-EEE-Mu-searchregion.shapes.root'), 'D-EEE-Mu/HNL-e-m20-Vsq4.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/A-MuMuMu-E-searchregion.shapes.root'), 'A-MuMuMu-E/HNL-e-m20-Vsq4.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/B-MuMuMu-E-searchregion.shapes.root'), 'B-MuMuMu-E/HNL-e-m20-Vsq4.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/C-MuMuMu-E-searchregion.shapes.root'), 'C-MuMuMu-E/HNL-e-m20-Vsq4.0em06-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq4.0em06-prompt/Majorana/D-MuMuMu-E-searchregion.shapes.root'), 'D-MuMuMu-E/HNL-e-m20-Vsq4.0em06-prompt'))

print 'e prompt 20 GeV:', '\t\t\t', getYield(in_hist) * 1.25

#E 20GeV Displaced
in_hist = []
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq5.0em06-displaced/Majorana/A-EEE-Mu-searchregion.shapes.root'), 'A-EEE-Mu/HNL-e-m20-Vsq5.0em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq5.0em06-displaced/Majorana/B-EEE-Mu-searchregion.shapes.root'), 'B-EEE-Mu/HNL-e-m20-Vsq5.0em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq5.0em06-displaced/Majorana/C-EEE-Mu-searchregion.shapes.root'), 'C-EEE-Mu/HNL-e-m20-Vsq5.0em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq5.0em06-displaced/Majorana/D-EEE-Mu-searchregion.shapes.root'), 'D-EEE-Mu/HNL-e-m20-Vsq5.0em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq5.0em06-displaced/Majorana/A-MuMuMu-E-searchregion.shapes.root'), 'A-MuMuMu-E/HNL-e-m20-Vsq5.0em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq5.0em06-displaced/Majorana/B-MuMuMu-E-searchregion.shapes.root'), 'B-MuMuMu-E/HNL-e-m20-Vsq5.0em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq5.0em06-displaced/Majorana/C-MuMuMu-E-searchregion.shapes.root'), 'C-MuMuMu-E/HNL-e-m20-Vsq5.0em06-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/e/HNL-e-m20-Vsq5.0em06-displaced/Majorana/D-MuMuMu-E-searchregion.shapes.root'), 'D-MuMuMu-E/HNL-e-m20-Vsq5.0em06-displaced'))

print 'e displaced 20 GeV:', '\t\t\t', getYield(in_hist)

#taulep 20 GeV Prompt
in_hist = []
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/A-EEE-Mu-searchregion.shapes.root'), 'A-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/B-EEE-Mu-searchregion.shapes.root'), 'B-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-EEE-Mu-searchregion.shapes.root'), 'C-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-EEE-Mu-searchregion.shapes.root'), 'D-EEE-Mu/HNL-tau-m20-Vsq5.0em04-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/A-MuMuMu-E-searchregion.shapes.root'), 'A-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/B-MuMuMu-E-searchregion.shapes.root'), 'B-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-MuMuMu-E-searchregion.shapes.root'), 'C-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-MuMuMu-E-searchregion.shapes.root'), 'D-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-prompt'))

print 'taulep prompt 20 GeV:', '\t\t\t', getYield(in_hist)

#taulep 20 GeV Displaced
in_hist = []
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-displaced/Majorana/A-EEE-Mu-searchregion.shapes.root'), 'A-EEE-Mu/HNL-tau-m20-Vsq5.0em04-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-displaced/Majorana/B-EEE-Mu-searchregion.shapes.root'), 'B-EEE-Mu/HNL-tau-m20-Vsq5.0em04-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-displaced/Majorana/C-EEE-Mu-searchregion.shapes.root'), 'C-EEE-Mu/HNL-tau-m20-Vsq5.0em04-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-displaced/Majorana/D-EEE-Mu-searchregion.shapes.root'), 'D-EEE-Mu/HNL-tau-m20-Vsq5.0em04-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-displaced/Majorana/A-MuMuMu-E-searchregion.shapes.root'), 'A-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-displaced/Majorana/B-MuMuMu-E-searchregion.shapes.root'), 'B-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-displaced/Majorana/C-MuMuMu-E-searchregion.shapes.root'), 'C-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-displaced/Majorana/D-MuMuMu-E-searchregion.shapes.root'), 'D-MuMuMu-E/HNL-tau-m20-Vsq5.0em04-displaced'))

print 'taulep displaced 20 GeV:', '\t\t\t', getYield(in_hist)

#tauhad 20 GeV Prompt
in_hist = []
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/A-TauEE-searchregion.shapes.root'), 'A-TauEE/HNL-tau-m20-Vsq5.0em04-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/B-TauEE-searchregion.shapes.root'), 'B-TauEE/HNL-tau-m20-Vsq5.0em04-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-TauEE-searchregion.shapes.root'), 'C-TauEE/HNL-tau-m20-Vsq5.0em04-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-TauEE-searchregion.shapes.root'), 'D-TauEE/HNL-tau-m20-Vsq5.0em04-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/A-TauEMu-searchregion.shapes.root'), 'A-TauEMu/HNL-tau-m20-Vsq5.0em04-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/B-TauEMu-searchregion.shapes.root'), 'B-TauEMu/HNL-tau-m20-Vsq5.0em04-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/A-TauMuMu-searchregion.shapes.root'), 'A-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/B-TauMuMu-searchregion.shapes.root'), 'B-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/C-TauMuMu-searchregion.shapes.root'), 'C-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-prompt/Majorana/D-TauMuMu-searchregion.shapes.root'), 'D-TauMuMu/HNL-tau-m20-Vsq5.0em04-prompt'))

print 'tauhad prompt 20 GeV:', '\t\t\t', getYield(in_hist)

#tauhad 20 GeV Displaced
in_hist = []
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-displaced/Majorana/A-TauEE-searchregion.shapes.root'), 'A-TauEE/HNL-tau-m20-Vsq5.0em04-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-displaced/Majorana/B-TauEE-searchregion.shapes.root'), 'B-TauEE/HNL-tau-m20-Vsq5.0em04-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-displaced/Majorana/C-TauEE-searchregion.shapes.root'), 'C-TauEE/HNL-tau-m20-Vsq5.0em04-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-displaced/Majorana/D-TauEE-searchregion.shapes.root'), 'D-TauEE/HNL-tau-m20-Vsq5.0em04-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-displaced/Majorana/A-TauEMu-searchregion.shapes.root'), 'A-TauEMu/HNL-tau-m20-Vsq5.0em04-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-displaced/Majorana/B-TauEMu-searchregion.shapes.root'), 'B-TauEMu/HNL-tau-m20-Vsq5.0em04-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-displaced/Majorana/A-TauMuMu-searchregion.shapes.root'), 'A-TauMuMu/HNL-tau-m20-Vsq5.0em04-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-displaced/Majorana/B-TauMuMu-searchregion.shapes.root'), 'B-TauMuMu/HNL-tau-m20-Vsq5.0em04-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-displaced/Majorana/C-TauMuMu-searchregion.shapes.root'), 'C-TauMuMu/HNL-tau-m20-Vsq5.0em04-displaced'))
in_hist.append(getObjFromFile(os.path.join(base_file, 'default-lowMassSRloose/UL2016post-2016pre-2017-2018/tau/HNL-tau-m20-Vsq5.0em04-displaced/Majorana/D-TauMuMu-searchregion.shapes.root'), 'D-TauMuMu/HNL-tau-m20-Vsq5.0em04-displaced'))

print 'tauhad displaced 20 GeV:', '\t\t\t', getYield(in_hist)






