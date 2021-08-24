#
# PU reweighting class
#
import ROOT, sys, os
from HNL.Tools.helpers import getObjFromFile


efficiency_dir = os.path.expandvars('$CMSSW_BASE/src/HNL/ObjectSelection/data/btagEfficiencies/')
sf_dir = os.path.expandvars('$CMSSW_BASE/src/HNL/Weights/data/btagging/')

sf_files = {
    ('prelegacy2016', 'Deep') : 'DeepFlavour_94XSF_WP_V3_B_F.csv',
    ('prelegacy2016', 'CSV') : 'DeepCSV_94XSF_WP_V4_B_F.csv',
    ('prelegacy2017', 'Deep') : 'DeepFlavour_94XSF_WP_V3_B_F.csv',
    ('prelegacy2017', 'CSV') : 'DeepCSV_94XSF_WP_V4_B_F.csv',
    ('prelegacy2018', 'Deep') : 'DeepJet_102XSF_WP_V1.csv',
    ('prelegacy2018', 'CSV') : 'DeepCSV_102XSF_WP_V1.csv',
    ('UL2017', 'Deep') : 'DeepJet_106XUL17SF_WPonly_V2p1.csv',
    ('UL2017', 'CSV') : 'DeepCSV_106XUL17SF_WPonly_V2p1.csv',
    ('UL2018', 'Deep') : 'DeepJet_106XUL18SF_WPonly.csv',
    ('UL2018', 'CSV') : 'DeepCSV_106XUL18SF_WPonly.csv'
}

workingpoint_dict = {
    'loose'     : ROOT.BTagEntry.OP_LOOSE,
    'medium'    : ROOT.BTagEntry.OP_MEDIUM,
    'tight'     : ROOT.BTagEntry.OP_TIGHT,
}

flavor_dict = {
    'b' : ROOT.BTagEntry.FLAV_B,
    'c' : ROOT.BTagEntry.FLAV_C,
    'other' : ROOT.BTagEntry.FLAV_UDSG
}

from HNL.ObjectSelection.bTagWP import getFlavor

class ScaleFactorReader:

    def __init__(self, algo, era, year, workingpoint):
        ROOT.gSystem.Load('libCondFormatsBTauObjects') 
        ROOT.gSystem.Load('libCondToolsBTau') 

        self.calib = ROOT.BTagCalibration(algo, sf_dir+sf_files[(era+year, algo)])

        self.v_sys = getattr(ROOT, 'vector<string>')()
        self.v_sys.push_back('up')
        self.v_sys.push_back('down')

        self.reader = ROOT.BTagCalibrationReader(
                        workingpoint_dict[workingpoint],              # 0 is for loose op, 1: medium, 2: tight, 3: discr. reshaping
                        "central",      # central systematic type
                        self.v_sys,          # vector of other sys. types
                    )    
        self.reader.load(
                    self.calib, 
                    0,          # 0 is for b flavour, 1: FLAV_C, 2: FLAV_UDSG 
                    "comb"      # measurement type
                ) 
        self.reader.load(
                    self.calib, 
                    1,          # 0 is for b flavour, 1: FLAV_C, 2: FLAV_UDSG 
                    "comb"      # measurement type
                ) 
        self.reader.load(
                    self.calib, 
                    2,          # 0 is for b flavour, 1: FLAV_C, 2: FLAV_UDSG 
                    "incl"      # measurement type
                ) 

    #flavor refers to output of getFlavor function
    def readValue(self, flavor, pt, eta, syst = 'central'):
        return self.reader.eval_auto_bounds(
                syst,                       # systematic (here also 'up'/'down' possible)
                flavor_dict[flavor],        # jet flavor
                eta,                        # absolute value of eta
                pt                          # pt
            )



#Define a functio that returns a reweighting-function according to the data 
def getReweightingFunction(algo, era, year, workingpoint, selection, variation='central'):

    sf_reader = ScaleFactorReader(algo, era, year, workingpoint)
    try:
        from HNL.Tools.efficiency import Efficiency
        in_path = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'ObjectSelection', 'data', 'btagEfficiencies', era+'-'+year, selection, 'events.root')
        eff_mc = {
            'b' : Efficiency('btag_efficiencies', lambda c, i: [c._jetSmearedPt[i], c._jetEta[i]], ('p_{T} [GeV]', '|#eta|'), in_path, subdirs=[algo, 'b', workingpoint]),
            'c' : Efficiency('btag_efficiencies', lambda c, i: [c._jetSmearedPt[i], c._jetEta[i]], ('p_{T} [GeV]', '|#eta|'), in_path, subdirs=[algo, 'c', workingpoint]),
            'other' : Efficiency('btag_efficiencies', lambda c, i: [c._jetSmearedPt[i], c._jetEta[i]], ('p_{T} [GeV]', '|#eta|'), in_path, subdirs=[algo, 'other', workingpoint])
        }
    except:
        raise RuntimeError('efficiency output not there for algo {0}, era {1}, year {2} and working point {3}'.format(algo, era, year, workingpoint))

    # Define reweightingFunc
    from HNL.ObjectSelection.jetSelector import isGoodBJet
    def reweightingFunc(chain):
        p_mc = 1.
        p_data = 1.
        for j in xrange(chain._nJets):
            if not isGoodBJet(chain, j, 'base'): continue
            from HNL.ObjectSelection.bTagWP import passBtag, getFlavor
            if passBtag(chain, j, workingpoint, algo):
                p_mc *= eff_mc[getFlavor(chain, j)].evaluateEfficiency(chain, index = j)
                p_data *= sf_reader.readValue(getFlavor(chain, j), chain._jetSmearedPt[j], chain._jetEta[j])*eff_mc[getFlavor(chain, j)].evaluateEfficiency(chain, index = j)
            else:
                p_mc *= 1. - eff_mc[getFlavor(chain, j)].evaluateEfficiency(chain, index = j)
                p_data *= 1. - (sf_reader.readValue(getFlavor(chain, j), chain._jetSmearedPt[j], chain._jetEta[j])* eff_mc[getFlavor(chain, j)].evaluateEfficiency(chain, index = j))
        return p_data/p_mc

    return reweightingFunc

