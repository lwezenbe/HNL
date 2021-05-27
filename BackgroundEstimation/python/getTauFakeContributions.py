import argparse, os

from HNL.EventSelection.eventCategorization import SUPER_CATEGORIES
from HNL.Tools.helpers import getObjFromFile

in_file_path = lambda y, s, r, sample, strategy : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 
                                                'data', 'calcYields', y, '-'.join([strategy, s, r, 'TauFakes']), sample, 'nonprompt', 'events.root')
out_file_path = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Weights', 'data', 'tauFakeContributions', 'weights.json')

import json

cat_dict = {
    'highMassSR' : SUPER_CATEGORIES['SingleTau'],
    'lowMassSR' : SUPER_CATEGORIES['SingleTau'],
    'MCCT' : [17],
    'DataCT' : [17],
    'TauMixCT' : [17],
    'TauFakesTT' : [17],
    'TauFakesDY' : [17]
}

TT_contributions = ['TT', 'TG', 'TTG', 'ttX', 'ST', 'TTTT']
DY_contributions = ['DY', 'WJets', 'WZ', 'ZZ', 'WW', 'triboson', 'Higgs']
# TT_contributions = ['TT']
# DY_contributions = ['DY']

def determineWeights(years, selections, regions, strategy):
    weights = {}
    for year in years:
        weights[year] = {}
        for selection in selections:
            weights[year][selection] = {}
            for region in regions:
                print region
                tt_tot = 0.
                dy_tot = 0.
                for c in cat_dict[region]:
                    for tt_c in TT_contributions:
                        tmp_tt_hist = getObjFromFile(in_file_path(year, selection, region, tt_c, strategy), str(c)+'_nonprompt')
                        tt_tot += tmp_tt_hist.GetSumOfWeights()
                    for dy_c in DY_contributions:
                        print in_file_path(year, selection, region, dy_c, strategy), str(c)+'_nonprompt'
                        tmp_dy_hist = getObjFromFile(in_file_path(year, selection, region, dy_c, strategy), str(c)+'_nonprompt')
                        dy_tot += tmp_dy_hist.GetSumOfWeights()
                print tt_tot, dy_tot
                weights[year][selection][region] = {'DY' : dy_tot/(tt_tot+dy_tot), 'TT' : tt_tot/(tt_tot+dy_tot)}            

    json_f = json.dumps(weights)
    out_file = open(out_file_path, 'w')
    out_file.write(json_f)
    out_file.close() 

def getWeights(year, selection, region):
    f = open(out_file_path,)
    weights = json.load(f)
    return weights[year][selection][region]


if __name__ == '__main__':

    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--years',     action='store',      default=['2016', '2017', '2018'], nargs='*',    help='Select years', choices=['2016', '2017', '2018'])
    argParser.add_argument('--selections',   action='store', nargs='*', default=['default'],  help='Select the type of selection for objects', 
                                choices=['leptonMVAtop', 'AN2017014', 'default', 'Luka', 'TTT'])
    argParser.add_argument('--strategy',   action='store', default='MVA',  help='Select the strategy to use to separate signal from background', choices=['cutbased', 'MVA'])
    argParser.add_argument('--regions',   action='store', nargs='*', default=['highMassSR', 'lowMassSR'],  help='Choose the selection region')
    args = argParser.parse_args()

    determineWeights(args.years, args.selections, args.regions, args.strategy)
