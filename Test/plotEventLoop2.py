import numpy as np
variables = {
    'l1pt':  (lambda c : c.l_pt[0],       np.arange(0., 52.5, 2.5),       ('p_{T} (l1) [GeV]', 'Events')),
    'l2pt':  (lambda c : c.l_pt[1],       np.arange(0., 52.5, 2.5),       ('p_{T} (l2) [GeV]', 'Events')),
    'l3pt':  (lambda c : c.l_pt[2],       np.arange(0., 52.5, 2.5),       ('p_{T} (l3) [GeV]', 'Events')),
    'ctauHN':  (lambda c : c.l_pt[2],       np.arange(0., .05, 0.005),       ('c_{#tau}', 'Events')),
    'HNLpt':  (lambda c : c.l_pt[2],       np.arange(0., 52.5, 2.5),       ('p_{T} (N) [GeV]', 'Events')),
}

import os
out_dir = os.path.join(os.getcwd(), 'data', 'Results', 'eventLoopLhe')

from HNL.Tools.outputTree import OutputTree
in_tree_prompt = OutputTree('events', 'data/eventLoopLhe/events.root')
in_tree_displaced = OutputTree('events', 'data/eventLoopLhe/backup_events-displaced.root')
#in_tree_displaced = OutputTree('events', 'data/eventLoopLhe/events.root')

def normalize_hist(hist, norm = 1.):
    hist.scale(norm/hist.getHist().GetSumOfWeights())
    return hist

from HNL.Tools.histogram import Histogram
from HNL.Plotting.plot import Plot
from HNL.Plotting.plottingTools import extraTextFormat
var_hist = {'prompt' : {'ossf' : {}, 'nossf' : {}}, 'displaced' : {'ossf' : {}, 'nossf' : {}}}
for v in variables:
    var_hist['prompt']['ossf'][v] = normalize_hist(Histogram(in_tree_prompt.getHistFromTree(v, v+'-prompt-ossf', variables[v][1], condition = 'isDiracType', weight = '1.')))
    var_hist['prompt']['nossf'][v] = normalize_hist(Histogram(in_tree_prompt.getHistFromTree(v, v+'-prompt-nossf', variables[v][1], condition = '!isDiracType', weight = '1.')))
    var_hist['displaced']['ossf'][v] = normalize_hist(Histogram(in_tree_displaced.getHistFromTree(v, v+'-displaced-ossf', variables[v][1], condition = 'isDiracType', weight = '1.')))
    var_hist['displaced']['nossf'][v] = normalize_hist(Histogram(in_tree_displaced.getHistFromTree(v, v+'-displaced-nossf', variables[v][1], condition = '!isDiracType', weight = '1.')))

    if v=='l3pt': 
        print var_hist['prompt']['ossf'][v].getHist().GetBinContent(3)
        print var_hist['prompt']['nossf'][v].getHist().GetBinContent(3)

    #Prompt plot
    p = Plot([var_hist['prompt']['ossf'][v], var_hist['prompt']['nossf'][v]], ['OSSF', 'SSSF'], color_palette = 'Didar', x_name = variables[v][2][0], y_name = variables[v][2][1], draw_ratio = 'from_signal')
    p.drawHist(out_dir + '/prompt')
    p = Plot([var_hist['displaced']['ossf'][v], var_hist['displaced']['nossf'][v]], ['OSSF', 'SSSF'], color_palette = 'Didar', x_name = variables[v][2][0], y_name = variables[v][2][1], draw_ratio = 'from_signal')
    p.drawHist(out_dir +'/displaced')

