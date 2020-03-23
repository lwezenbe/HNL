from HNL.Tools.logger import getLogger
log = getLogger()

#
# PU reweighting class
#
import ROOT, sys, os
from HNL.Tools.helpers import getObjFromFile

dataDir = '$CMSSW_BASE/src/HNL/Weights/data/puReweightingData/'

#Define a functio that returns a reweighting-function according to the data 
def getReweightingFunction(year, variation='central', useMC=None):

  if   year == '2016': data = {'central' : "PU_2016_36000_XSecCentral", 'up' : "PU_2016_36000_XSecUp", 'down' : "PU_2016_36000_XSecDown"}
  elif year == '2017': data = {'central' : "PU_2017_41500_XSecCentral", 'up' : "PU_2017_41500_XSecUp", 'down' : "PU_2017_41500_XSecDown"}
  elif year == '2018': data = {'central' : "PU_2018_60000_XSecCentral", 'up' : "PU_2018_60000_XSecUp", 'down' : "PU_2018_60000_XSecDown"}

  # Data
  histoData = getObjFromFile(dataDir + data[variation] + '.root', 'pileup')
  histoData.Scale(1./histoData.Integral())

  # MC
  if not useMC:
    mcProfile = ROOT.TH1D('mc', 'mc', 100, 0, 100)
    sys.stdout = open(os.devnull, 'w')
    if year == '2016':   from SimGeneral.MixingModule.mix_2016_25ns_Moriond17MC_PoissonOOTPU_cfi import mix
    elif year == '2017': from SimGeneral.MixingModule.mix_2017_25ns_WinterMC_PUScenarioV1_PoissonOOTPU_cfi import mix
    elif year == '2018': from SimGeneral.MixingModule.mix_2018_25ns_JuneProjectionFull18_PoissonOOTPU_cfi import mix
      
    sys.stdout = sys.__stdout__
    for i, value in enumerate(mix.input.nbPileupEvents.probValue): mcProfile.SetBinContent(i+1, value)   # pylint: disable=E1103
  else:
    mcProfile = useMC
  mcProfile.Scale(1./mcProfile.Integral())

  # Create reweighting histo
  reweightingHisto = histoData.Clone('reweightingHisto')
  reweightingHisto.Divide(mcProfile)

  # Define reweightingFunc
  def reweightingFunc(nTrueInt):
    return reweightingHisto.GetBinContent(reweightingHisto.FindBin(nTrueInt))
  return reweightingFunc

if __name__ == '__main__':
    from HNL.Samples.sample import createSampleList, getSampleFromList
    import os
    input_file = os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/samples_for_testing.conf')
    sample_list = createSampleList(input_file)
    sample = getSampleFromList(sample_list, 'DYJetsToLL-M-10to50')

    chain = sample.initTree()
    chain.GetEntry(5)
    chain.year = '2016'
    pu = getReweightingFunction(chain.year, 'central')
    print pu(chain._nTrueInt)