import os
from HNL.Tools.helpers import getObjFromFile
from HNL.Tools.histogram import Histogram

workspace_base = '/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/residuals'

input_base = '/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output'
output_base = '/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output'

observed_name = 'data_obs'
bkgr_names = ['Other', 'TT-T+X', 'WZ', 'XG', 'ZZ-H', 'charge-misid', 'non-prompt', 'triboson']
year = '2016post-2016pre-2017-2018'
era = 'UL'


def calculateResiduals(prefit, postfit, chi2 = False):
    out_residuals = []
    for b in xrange(1, prefit.GetNbinsX()+1):
        if not chi2:
            out_residuals.append((prefit.GetBinContent(b)-postfit.GetBinContent(b))/prefit.GetBinError(b))
        else:
            out_residuals.append(abs(prefit.GetBinContent(b)-postfit.GetBinContent(b))**2/prefit.GetBinContent(b))
    return out_residuals

def getResiduals(input_file, chi2 = False):
    # Find all channels
    from HNL.Tools.helpers import rootFileContent
    from ROOT import TFile
    root_input_file = TFile(input_file, 'read')
    all_channels = [x[0] for x in rootFileContent(root_input_file)]
    prefit_channels = [x for x in all_channels if 'ch' in x and 'prefit' in x]
    postfit_channels = [x for x in all_channels if 'ch' in x and 'postfit' in x]
    root_input_file.Close()

    from HNL.Tools.helpers import getObjFromFile
    all_residuals = []
    for prefit, postfit in zip(prefit_channels, postfit_channels):
        prefit_hist = getObjFromFile(input_file, prefit+'/TotalBkg')
        postfit_hist = getObjFromFile(input_file, postfit+'/TotalBkg')
        all_residuals.extend(calculateResiduals(prefit_hist, postfit_hist, chi2 = chi2))
    
    return all_residuals


def getChi2(input_file):
    # Find all channels
    from HNL.Tools.helpers import rootFileContent
    from ROOT import TFile
    root_input_file = TFile(input_file, 'read')
    all_channels = [x[0] for x in rootFileContent(root_input_file)]
    postfit_channels = [x for x in all_channels if 'ch' in x and 'postfit' in x]
    root_input_file.Close()
    
    all_residuals = []
    for postfit in postfit_channels:
        postfit_hist = getObjFromFile(input_file, postfit+'/TotalBkg')
        observed = getObjFromFile(input_file, postfit+'/data_obs')
        all_residuals.extend(calculateResiduals(postfit_hist, observed, chi2 = True))
    
    return sum(all_residuals)/len(all_residuals)

def plotResiduals(residuals):
    from ROOT import TH1F
    out_hist = TH1F('residuals', 'residuals', 20, min(residuals), max(residuals))
    for r in residuals:
        out_hist.Fill(r)
    from HNL.Plotting.plot import Plot
    p = Plot(None, "residuals", "residuals", "residual", "number of bins", bkgr_hist = out_hist, era = 'UL', year = '2016post-2016pre-2017-2018')
    p.drawHist(output_dir = output_base + '/Residuals', bkgr_draw_option = 'Hist')


all_residuals = []
#residuals.extend(getResiduals(input_base+'/Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau/postfitshapes.root'))
all_residuals.extend(getResiduals(input_base+'/Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/cutbased/postfit/NoTau/postfitshapes.root'))
all_residuals.extend(getResiduals(input_base+'/Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/cutbased/postfit/SingleTau/postfitshapes.root'))
plotResiduals(all_residuals)

print getChi2(input_base+'/Majorana/UL2016post-2016pre-2017-2018/default-highMassSR/tau/HNL-tau-m200-Vsq4.0em01-prompt/shapes/cutbased/postfit/MaxOneTau/postfitshapes.root')
        
        

