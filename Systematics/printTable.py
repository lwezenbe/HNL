years = ['2016pre', '2016post', '2017', '2018']
era = 'UL'
regions = {
#    'lowMassSRloose' : ['A', 'B', 'C', 'D'], 
    'highMassSR': ['E', 'F']
}
masses = {
    'lowMassSRloose' : ['10', '20', '30', '40', '50', '60', '70', '75'],
    'highMassSR' : ['85', '100', '150', '200', '250', '300', '350', '400', '450', '500', '600', '700', '800', '900', '1000', '1200', '1500']
}

backgrounds = ['triboson', 'WZ', 'TT-T+X', 'XG', 'Other', 'ZZ-H', 'non-prompt']

from HNL.EventSelection.eventCategorization import ANALYSIS_CATEGORIES
from HNL.Systematics.systematics import SystematicJSONreader
reader = SystematicJSONreader(datadriven_processes = 'non-prompt')

import os
shape_loc = lambda region, era, year, coupling, sample, sr, cat: os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'shapes', 'default-{0}'.format(region), era+year, coupling, sample, sr+'-'+cat+'-searchregion.shapes.root')

list_of_syst = {}

from HNL.Tools.helpers import getObjFromFile
for year in years:
    for syst in reader.getFlats(year, split_correlations=False):
        val = abs(1.-reader.getValue(syst, year))
        group = reader.getDescription(syst, year)
        if group in list_of_syst.keys():
            list_of_syst[group].append(val)
        else:
            list_of_syst[group] = [val]

    for region in regions.keys():
        for sr in regions[region]:
            for cat in ANALYSIS_CATEGORIES:
                for mass in masses[region]:
                    for bkgr in backgrounds:
                        try:
                            #nominal_hist  = getObjFromFile(shape_loc(region, era, year, 'e', 'HNL-e-m{0}'.format(mass), sr, cat), sr+'-'+cat+'/'+b).GetSumOfWeights()
                            nominal_hist  = getObjFromFile(shape_loc(region, era, year, 'e', 'HNL-e-m{0}'.format(mass), sr, cat), sr+'-'+cat+'/'+bkgr)
                            nominal_hist.GetSumOfWeights()
                        except:
#                            print 'error', shape_loc(region, era, year, 'e', 'HNL-e-m{0}'.format(mass), sr, cat), sr+'-'+cat
                            continue

                        #print b, shape_loc(region, era, year, 'e', 'HNL-e-m{0}'.format(mass), sr, cat)
                        #print nominal_hist

                        for syst, uncorr_syst in zip(reader.getWeights(year, split_correlations=True)+reader.getReruns(year, split_correlations=True), reader.getWeights(year, split_correlations=False)+reader.getReruns(year, split_correlations=False)):
                            try:
                                #syst_hist_up = getObjFromFile(shape_loc(region, era, year, 'e', 'HNL-e-m{0}'.format(mass), sr, cat), sr+'-'+cat+str(syst)+'Up/'+b).GetSumOfWeights()
                                #syst_hist_down = getObjFromFile(shape_loc(region, era, year, 'e', 'HNL-e-m{0}'.format(mass), sr, cat), sr+'-'+cat+str(syst)+'Down/'+b).GetSumOfWeights()
                                syst_hist_up = getObjFromFile(shape_loc(region, era, year, 'e', 'HNL-e-m{0}'.format(mass), sr, cat), sr+'-'+cat+str(syst)+'Up/'+bkgr)
                                syst_hist_down = getObjFromFile(shape_loc(region, era, year, 'e', 'HNL-e-m{0}'.format(mass), sr, cat), sr+'-'+cat+str(syst)+'Down/'+bkgr)
                                
                                group = reader.getDescription(uncorr_syst, year)
                                
                                if group not in list_of_syst.keys():
                                    list_of_syst[group] = []
                                for b in xrange(1, nominal_hist.GetNbinsX()+1):
                                    up_var =  abs(syst_hist_up.GetBinContent(b)-nominal_hist.GetBinContent(b))/nominal_hist.GetBinContent(b)
                                    down_var =  abs(syst_hist_down.GetBinContent(b)-nominal_hist.GetBinContent(b))/nominal_hist.GetBinContent(b)
                                    if up_var > 0.9:
                                        print up_var, b, bkgr, syst, shape_loc(region, era, year, 'e', 'HNL-e-m{0}'.format(mass), sr, cat)
                                    if 0. < up_var < 1.: list_of_syst[group].append(up_var)
                                    if 0. < down_var < 1.: list_of_syst[group].append(down_var)
                            except:
                                pass
            

import numpy

def getPercent(val):
    return 100*val

for syst in list_of_syst.keys():
    print syst, '\t', getPercent(min(list_of_syst[syst])), '\t', getPercent(max(list_of_syst[syst])), '\t', getPercent(numpy.median(list_of_syst[syst])), '\t', getPercent(numpy.average(list_of_syst[syst]))
