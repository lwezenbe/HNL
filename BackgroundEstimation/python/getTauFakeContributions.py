import argparse, os

from HNL.EventSelection.eventCategorization import ANALYSIS_CATEGORIES
from HNL.Tools.helpers import getObjFromFile

in_file_path = lambda era, y, s, r, sample, strategy : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 
                                                'data', 'runAnalysis', 'HNL-TauFakes', '-'.join([strategy, s, r, 'reco']), era+'-'+y, 'bkgr', sample, 'variables.root')
out_file_path = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Weights', 'data', 'tauFakeContributions', 'weights.json')

import json

cat_dict = {
    'highMassSR' : ['TauEE', 'TauMuMu', 'TauEMu', 39],
    'HighMassWithB' : ['TauEE', 'TauMuMu', 'TauEMu', 39],
    'HighMassWithInvertedPt' : ['TauEE', 'TauMuMu', 'TauEMu', 39],
    'lowMassSR' : ['TauEE', 'TauMuMu', 'TauEMu', 39],
    'lowMassSRloose' : ['TauEE', 'TauMuMu', 'TauEMu', 39],
    'WZCR' : ['TauEE', 'TauMuMu', 'TauEMu', 39],
    'ConversionCR' : ['TauEE', 'TauMuMu', 'TauEMu', 39],
    'ZZCR' : [39],
    'MCCT' : [39],
    'DataCT' : [39],
    'TauMixCT' : [39],
    'TauMixCTM3lcutInverted' : [39],
    'TauFakesTT' : [39],
    'TauFakesDYCT' : [39],
    'TauFakesDY' : [39]
}

TT_contributions = ['TT-T+X']
DY_contributions = ['XG', 'WZ', 'ZZ-H', 'Other', 'triboson']

def determineWeights(eras, years, selections, regions, strategy):
    from ROOT import TFile
    from HNL.Tools.helpers import getHistFromTree
    import numpy as np

    try:
        f = open(out_file_path,)
        weights = json.load(f)
        f.close()
    except:
        weights = {}
    for era in eras:
        if era not in weights.keys():   weights[era] = {}
        for year in years:
            if year not in weights[era].keys(): weights[era][year] = {}
            for selection in selections:
                if selection not in weights[era][year].keys():  weights[era][year][selection] = {}
                for region in regions:
                    weights[era][year][selection][region] = {}
                    for c in cat_dict[region]:
                        tt_tot = 0.
                        dy_tot = 0.
                        if isinstance(c, int):
                            condition = 'category=={0}'.format(c)
                        else:
                            condition = '('+'||'.join(['category=={0}'.format(x) for x in ANALYSIS_CATEGORIES[c]])+')'
                        for tt_c in TT_contributions:
                            infile = TFile(in_file_path(era, year, selection, region, tt_c, strategy), 'read')
                            intree = infile.Get('events_nominal')
                            tmp_tt_hist = getHistFromTree(intree, 'searchregion', tt_c, np.arange(0., 2., 1.), '('+condition+'&&!isprompt)')
                            tt_tot += tmp_tt_hist.GetSumOfWeights()
                            infile.Close()

                        for dy_c in DY_contributions:
                            infile = TFile(in_file_path(era, year, selection, region, dy_c, strategy), 'read')
                            intree = infile.Get('events_nominal')
                            tmp_dy_hist = getHistFromTree(intree, 'searchregion', dy_c, np.arange(0., 2., 1.), '('+condition+'&&!isprompt)')
                            dy_tot += tmp_dy_hist.GetSumOfWeights()
                            infile.Close()
                        weights[era][year][selection][region][c] = {'DY' : dy_tot/(tt_tot+dy_tot), 'TT' : tt_tot/(tt_tot+dy_tot)}            

    json_f = json.dumps(weights)
    out_file = open(out_file_path, 'w')
    out_file.write(json_f)
    out_file.close() 

def getWeights(era, year, selection, region):
    if selection == 'corrMet': selection = 'default'
    f = open(out_file_path,)
    weights = json.load(f)
    f.close()
    return weights[era][year][selection][region]


if __name__ == '__main__':

    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--eras',     action='store',      default=['UL'], nargs='*',    help='Select years', choices=['UL', 'prelegacy'])
    argParser.add_argument('--years',     action='store',      default=['2016pre', '2016post', '2017', '2018'], nargs='*',    help='Select years')
    argParser.add_argument('--selections',   action='store', nargs='*', default=['default'],  help='Select the type of selection for objects', 
                                choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
    argParser.add_argument('--strategy',   action='store', default='MVA',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA'])
    argParser.add_argument('--regions',   action='store', nargs='*', default=['highMassSR', 'lowMassSRloose'],  help='Choose the selection region')
    args = argParser.parse_args()

    determineWeights(args.eras, args.years, args.selections, args.regions, args.strategy)
