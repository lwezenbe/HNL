#
# PU reweighting class
#
import ROOT, sys, os
from HNL.Tools.helpers import getObjFromFile

dataDir = '$CMSSW_BASE/src/HNL/Weights/data/puReweightingData/'

#Define a functio that returns a reweighting-function according to the data 
def getReweightingFunction(era, year, variation='central', useMC=None):
    if era == 'prelegacy':
        if   year == '2016': data = {'central' : "PU_2016_36000_XSecCentral", 'up' : "PU_2016_36000_XSecUp", 'down' : "PU_2016_36000_XSecDown"}
        elif year == '2017': data = {'central' : "PU_2017_41500_XSecCentral", 'up' : "PU_2017_41500_XSecUp", 'down' : "PU_2017_41500_XSecDown"}
        elif year == '2018': data = {'central' : "PU_2018_60000_XSecCentral", 'up' : "PU_2018_60000_XSecUp", 'down' : "PU_2018_60000_XSecDown"}
        histoData = getObjFromFile(dataDir + data[variation] + '.root', 'pileup')
    elif era == 'UL':
        if '2016' in year:   data = {'central' : "PileupHistogram-goldenJSON-13tev-2016-69200ub-99bins", 'up' : "PileupHistogram-goldenJSON-13tev-2016-72400ub-99bins", 'down' : "PileupHistogram-goldenJSON-13tev-2016-66000ub-99bins"}
        elif year == '2017': data = {'central' : "PileupHistogram-goldenJSON-13tev-2016-69200ub-99bins", 'up' : "PileupHistogram-goldenJSON-13tev-2016-72400ub-99bins", 'down' : "PileupHistogram-goldenJSON-13tev-2016-66000ub-99bins"}
        elif year == '2018': data = {'central' : "PileupHistogram-goldenJSON-13tev-2016-69200ub-99bins", 'up' : "PileupHistogram-goldenJSON-13tev-2016-72400ub-99bins", 'down' : "PileupHistogram-goldenJSON-13tev-2016-66000ub-99bins"}
        histoData = getObjFromFile(dataDir + '/UL/' + data[variation] + '.root', 'pileup')
    else:
        raise RuntimeError("era {0} not known",format(era))

    # Data
    histoData.Scale(1./histoData.Integral())

    # MC
    mcProfile = ROOT.TH1D('mc', 'mc', 100, 0, 100)
    if era == 'prelegacy':
        if not useMC:
            sys.stdout = open(os.devnull, 'w')
            if year == '2016':   from SimGeneral.MixingModule.mix_2016_25ns_Moriond17MC_PoissonOOTPU_cfi import mix
            elif year == '2017': from SimGeneral.MixingModule.mix_2017_25ns_WinterMC_PUScenarioV1_PoissonOOTPU_cfi import mix
            elif year == '2018': from SimGeneral.MixingModule.mix_2018_25ns_JuneProjectionFull18_PoissonOOTPU_cfi import mix         
            sys.stdout = sys.__stdout__
            for i, value in enumerate(mix.input.nbPileupEvents.probValue): mcProfile.SetBinContent(i+1, value)   # pylint: disable=E1103
        else:
            mcProfile = useMC
    elif era == 'UL':
        if year == '2016pre':   mcProfile = getObjFromFile(dataDir + '/UL/pileup_2016BF.root', 'pileup')
        if year == '2016post':  mcProfile = getObjFromFile(dataDir + '/UL/pileup_2016GH.root', 'pileup')
        elif year == '2017':    mcProfile = getObjFromFile(dataDir + '/UL/pileup_2017_shifts.root', 'pileup')
        elif year == '2018':    mcProfile = getObjFromFile(dataDir + '/UL/pileup_2018_shifts.root', 'pileup')    
        # if not useMC:
        #     sys.stdout = open(os.devnull, 'w')
        #     if '2016' in year:   from SimGeneral.MixingModule.mix_2016_25ns_UltraLegacy_PoissonOOTPU_cfi import mix
        #     elif year == '2017': from SimGeneral.MixingModule.mix_2017_25ns_UltraLegacy_PoissonOOTPU_cfi import mix
        #     elif year == '2018': from SimGeneral.MixingModule.mix_2018_25ns_UltraLegacy_PoissonOOTPU_cfi import mix         
        #     sys.stdout = sys.__stdout__
        #     for i, value in enumerate(mix.input.nbPileupEvents.probValue): mcProfile.SetBinContent(i+1, value)   # pylint: disable=E1103
        # else:
        #     mcProfile = useMC
    
    # tmp_mcProfile.Scale(1./tmp_mcProfile.Integral())
    # print [tmp_mcProfile.GetBinContent(a) for a in xrange(1, tmp_mcProfile.GetNbinsX()+1)]
    mcProfile.Scale(1./mcProfile.Integral())

    # # Create reweighting histo
    # reweightingHisto = histoData.Clone('reweightingHisto')
    # reweightingHisto.Divide(mcProfile)

    # Define reweightingFunc
    def reweightingFunc(nTrueInt):
        # return reweightingHisto.GetBinContent(reweightingHisto.FindBin(nTrueInt))
        return histoData.GetBinContent(histoData.FindBin(nTrueInt))/mcProfile.GetBinContent(mcProfile.FindBin(nTrueInt))
    return reweightingFunc

if __name__ == '__main__':
    from HNL.Samples.sample import createSampleList, getSampleFromList
    from HNL.Tools.logger import getLogger, closeLogger
    log = getLogger('INFO')

    bins = {'2016pre':60, '2016post':60, '2016': 60, '2017': 60, '2018': 75}
    years = {'UL': ['2016pre', '2016post', '2017', '2018'],
                'prelegacy' : ['2016', '2017', '2018']}

    for era in ['UL', 'prelegacy']:
        for year in years[era]:
                print year, era
                pu = getReweightingFunction(era, year, 'central')
                testhist = ROOT.TH1D('mc', 'mc', bins[year], 0, bins[year])
                for i in xrange(1, testhist.GetNbinsX()+1):
                    testhist.SetBinContent(i, pu(i))
                from HNL.Plotting.plot import Plot
                p = Plot(testhist, 'PU weights', 'PUWeights_'+era+year, x_name='_nTrueInt', y_name = 'weight')
                p.drawHist(output_dir='PUweights')
    closeLogger(log)