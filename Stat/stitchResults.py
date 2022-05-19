selection = 'default'
flavor = 'tau'
era = 'UL'
year_to_read = '2016pre-2016post-2017-2018'
asymptotic_str = 'asymptotic'

mass_strat_dict = {
    20 : ['custom', 'MaxOneTau'],
    30 : ['custom', 'MaxOneTau'],
    40 : ['custom', 'MaxOneTau'],
    50 : ['custom', 'MaxOneTau'],
    60 : ['custom', 'MaxOneTau'],
    70 : ['custom', 'MaxOneTau'],
    75 : ['custom', 'MaxOneTau'],
    85 : ['cutbased', 'NoTau'],
    100 : ['cutbased', 'NoTau'],
    125 : ['cutbased', 'NoTau'],
    150 : ['cutbased', 'NoTau'],
    200 : ['cutbased', 'NoTau'],
    250 : ['cutbased', 'NoTau'],
    300 : ['cutbased', 'NoTau'],
    350 : ['cutbased', 'NoTau'],
    400 : ['cutbased', 'NoTau'],
    450 : ['cutbased', 'NoTau'],
    500 : ['cutbased', 'NoTau'],
    600 : ['cutbased', 'NoTau'],
    700 : ['cutbased', 'NoTau'],
    800 : ['cutbased', 'NoTau'],
    900 : ['cutbased', 'NoTau'],
    1000 : ['cutbased', 'NoTau'],
}

from HNL.Tools.helpers import makeDirIfNeeded, makePathTimeStamped, getObjFromFile
from HNL.Analysis.analysisTypes import signal_couplingsquared
from numpy import sqrt
import os

coupling_dict = {'tau':'#tau', 'mu':'#mu', 'e':'e', '2l':'l'}
from HNL.Plotting.plot import Plot
destination = makePathTimeStamped(os.path.expandvars('$CMSSW_BASE/src/HNL/Stat/data/Results/runAsymptoticLimits/stitched-'+selection+'/'+flavor+'/'+ era+year_to_read))

from HNL.Stat.combineTools import runCombineCommand, extractScaledLimitsPromptHNL, makeGraphs, saveGraphs
passed_masses = []
passed_couplings = []
limits = {}
for mass in sorted(mass_strat_dict.keys()):
    from HNL.Stat.datacardManager import getRegionFromMass
    input_folder = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'output', era+year_to_read, selection+'-'+getRegionFromMass(mass), flavor, 'HNL-'+flavor+'-m'+str(mass), 'shapes', mass_strat_dict[mass][0], asymptotic_str, mass_strat_dict[mass][1])
    tmp_coupling = sqrt(signal_couplingsquared[flavor][mass])

    tmp_limit = extractScaledLimitsPromptHNL(input_folder + '/higgsCombineTest.AsymptoticLimits.mH120.root', tmp_coupling)
    if tmp_limit is not None and len(tmp_limit) > 4 and mass != 5:
        passed_masses.append(mass)
        passed_couplings.append(tmp_coupling)
        limits[mass] = tmp_limit

graphs = makeGraphs(passed_masses, couplings = passed_couplings, limits=limits)
out_path_base = lambda sample, era, sname, cname : os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'output', era, sname, flavor,
                                   sample, 'shapes', asymptotic_str+'/'+cname)
file_name  = out_path_base('Combined', era+year_to_read, 'custom-default', 'SingleTau') +'/limits.root'
compare_graph = getObjFromFile(file_name, 'expected_central')

tex_names = ['Final states containing 1#tau_{h} only']
bkgr_hist = [compare_graph]
p = Plot(graphs, tex_names, 'limits', bkgr_hist = bkgr_hist, y_log = True, x_log=True, x_name = 'm_{N} [GeV]', y_name = '|V_{'+coupling_dict[flavor]+' N}|^{2}', era = 'UL', year = 'all')
p.drawBrazilian(output_dir = destination)

