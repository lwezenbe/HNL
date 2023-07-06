import os
in_path = lambda year, signal: os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Analysis', 'data', 'runAnalysis', 'HNL', 'MVA-default-highMassSR-reco', 'UL-'+year, 'signal', signal) 
out_path = lambda signal: os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Test', 'data', 'plotVBFcontribution', signal)

masses = [600, 700, 800, 900, 1000, 1200, 1500]
coupling_types = {'e' : 'e', 
                'mu' : 'mu', 
                'taulep' : 'tau',
                'tauhad' : 'tau'}
years = ['2016pre', '2016post', '2017', '2018']

import ROOT
ROOT.gROOT.SetBatch(True)

list_of_numbers = {}
for ct in coupling_types:
    print 'Loading coupling type', ct
    list_of_numbers[ct] = {}
    for mass in masses:
        print '\t M(N) =', mass
        if 'tau' in ct and mass > 1000: continue
        list_of_numbers[ct][mass] = {}
        for year in years:
            from HNL.Tools.helpers import isValidRootFile
            if not isValidRootFile(in_path(year, 'HNL-{0}-m{1}'.format(coupling_types[ct], mass))+'/variables-HNL-{0}-m{1}.root'.format(ct, mass)) or not isValidRootFile(in_path(year, 'HNL-{0}-m{1}'.format(coupling_types[ct], mass))+'/variables-HNLvbf-{0}-m{1}.root'.format(ct, mass)): continue
            list_of_numbers[ct][mass][year] = {}
            from HNL.Tools.outputTree import OutputTree
            import numpy as np
            intree = OutputTree('events_nominal', in_path(year, 'HNL-{0}-m{1}'.format(coupling_types[ct], mass))+'/variables-HNL-{0}-m{1}.root'.format(ct, mass))
            inhist = intree.getHistFromTree('searchregion', 'htemp', np.arange(0.5, 2.5))
            list_of_numbers[ct][mass][year]['gluglu'] = inhist.GetSumOfWeights()         
            del inhist   
            intree = OutputTree('events_nominal', in_path(year, 'HNL-{0}-m{1}'.format(coupling_types[ct], mass))+'/variables-HNLvbf-{0}-m{1}.root'.format(ct, mass))
            inhist = intree.getHistFromTree('searchregion', 'htemp', np.arange(0.5, 2.5))
            list_of_numbers[ct][mass][year]['vbf'] = inhist.GetSumOfWeights()       
            del inhist     

#from array import array
#for ct in coupling_types: 
#    xaxis = array('d')
#    yaxis = {'gluglu' : array('d'), 'vbf' : array('d')}
#    npoints = 0
#    for imass, mass in enumerate(sorted(list_of_numbers[ct].keys())):
#        xaxis.append(mass/1000.)
#        yaxis['gluglu'].append(0.)
#        yaxis['vbf'].append(0.)
#        for year in years:
#            if year not in list_of_numbers[ct][mass].keys(): continue
#            yaxis['gluglu'][imass] += list_of_numbers[ct][mass][year]['gluglu']
#            yaxis['vbf'][imass] += list_of_numbers[ct][mass][year]['vbf']
#        tot = yaxis['gluglu'][imass] + yaxis['vbf'][imass]
#        yaxis['gluglu'][imass] /= tot
#        yaxis['vbf'][imass] /= tot
#        npoints += 1
#
#    out_graph_gluglu = ROOT.TGraph(npoints, xaxis, yaxis['gluglu'])
#    out_graph_vbf = ROOT.TGraph(npoints, xaxis, yaxis['vbf'])
#
#    from HNL.Plotting.plot import Plot
#    p = Plot([out_graph_gluglu, out_graph_vbf], ['qq->W', 'VBF'], x_name = 'HNL mass [TeV]', y_name = 'Relative contribution', year = 'all')
#    p.drawGraph(output_dir = out_path(ct))

#Save json
from HNL.Tools.helpers import makeDirIfNeeded
combined_numbers = {}
for ct in list_of_numbers.keys():
    if coupling_types[ct] not in combined_numbers.keys(): combined_numbers[coupling_types[ct]] = {}
    for mass in list_of_numbers[ct].keys():
        if mass not in combined_numbers[coupling_types[ct]].keys(): combined_numbers[coupling_types[ct]][mass] = {}
        for year in list_of_numbers[ct][mass].keys():
            if 'gluglu' not in combined_numbers[coupling_types[ct]][mass].keys():
                combined_numbers[coupling_types[ct]][mass]['gluglu'] = list_of_numbers[ct][mass][year]['gluglu']
            else:    
                combined_numbers[coupling_types[ct]][mass]['gluglu'] += list_of_numbers[ct][mass][year]['gluglu']
            
            if 'vbf' not in combined_numbers[coupling_types[ct]][mass].keys():
                combined_numbers[coupling_types[ct]][mass]['vbf'] = list_of_numbers[ct][mass][year]['vbf']
            else:    
                combined_numbers[coupling_types[ct]][mass]['vbf'] += list_of_numbers[ct][mass][year]['vbf']
    
    import json
    for k in combined_numbers.keys():
        out_path_json = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Systematics', 'data', 'VBFcontributions', k+'.json')
        makeDirIfNeeded(out_path_json)
        fractions = {}
        for mass in combined_numbers[k].keys():
            fractions[mass] = combined_numbers[k][mass]['vbf']/(combined_numbers[k][mass]['vbf'] + combined_numbers[k][mass]['gluglu'])

        json_object = json.dumps(fractions)
        with open(out_path_json, "w") as outfile:
            outfile.write(json_object)
