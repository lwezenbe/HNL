import numpy as np
variables = {
    'l1pt':  (lambda c : c.l_pt[0],       np.arange(0., 52.5, 2.5),       ('p_{T} (l1) [GeV]', 'Events')),
    'l2pt':  (lambda c : c.l_pt[1],       np.arange(0., 52.5, 2.5),       ('p_{T} (l2) [GeV]', 'Events')),
    'l3pt':  (lambda c : c.l_pt[2],       np.arange(0., 52.5, 2.5),       ('p_{T} (l3) [GeV]', 'Events')),
    'ctauHN':  (lambda c : c.l_pt[2],       np.arange(0., .05, 0.005),       ('c_{#tau} [mm]', 'Events')),
    'HNLpt':  (lambda c : c.l_pt[2],       np.arange(0., 52.5, 2.5),       ('p_{T} (HNL) [GeV]', 'Events')),
    'isLNC':  (lambda c : c.l_pt[2],       np.arange(0., 3, 1),       ('isLNC', 'Events')),
}

import os
out_dir = os.path.join(os.getcwd(), 'data', 'Results', 'eventLoopLhe') 

from HNL.Tools.outputTree import OutputTree
in_tree_prompt = OutputTree('events', 'data/eventLoopLhe/events-prompt-nofilter.root')
#in_tree_prompt = OutputTree('events', 'data/eventLoopLhe/events.root')
in_tree_displaced = OutputTree('events', 'data/eventLoopLhe/events-displaced-nofilter-frankenstein.root')
#in_tree_displaced = OutputTree('events', 'data/eventLoopLhe/events.root')

def normalize_hist(hist, norm = 1.):
    if norm is None:
        return hist
    else:
        hist.scale(norm/hist.getHist().GetSumOfWeights())
        return hist

from HNL.Tools.histogram import Histogram
from HNL.Plotting.plot import Plot
from HNL.Plotting.plottingTools import extraTextFormat
var_hist = {'prompt' : {'LNC' : {}, 'LNV' : {}}, 'displaced' : {'LNC' : {}, 'LNV' : {}}}
for v in variables:
    var_hist['prompt']['LNC'][v] = normalize_hist(Histogram(in_tree_prompt.getHistFromTree(v, v+'-prompt-LNC', variables[v][1], condition = 'isLNC', weight = '1.')), norm = 1. if v != 'isLNC' else None)
    var_hist['prompt']['LNV'][v] = normalize_hist(Histogram(in_tree_prompt.getHistFromTree(v, v+'-prompt-LNV', variables[v][1], condition = '!isLNC', weight = '1.')), norm = 1. if v != 'isLNC' else None)
    var_hist['displaced']['LNC'][v] = normalize_hist(Histogram(in_tree_displaced.getHistFromTree(v, v+'-displaced-LNC', variables[v][1], condition = 'isLNC', weight = '1.')), norm = 1. if v != 'isLNC' else None)
    var_hist['displaced']['LNV'][v] = normalize_hist(Histogram(in_tree_displaced.getHistFromTree(v, v+'-displaced-LNV', variables[v][1], condition = '!isLNC', weight = '1.')), norm = 1. if v != 'isLNC' else None)

    #Prompt plot
    coords_x = 0.6 if v in ['ctauHN', 'l2pt', 'l3pt'] else None 
    extra_text = [extraTextFormat('#mu#mue', xpos = coords_x, ypos = 0.65)]
    extra_text.append(extraTextFormat('|V_{#muN}|^{2} = 2.5e-6'))
    extra_text.append(extraTextFormat('|V_{eN}|^{2} = |V_{#tauN}|^{2} = 0'))
    extra_text.append(extraTextFormat('HNL mass = 30 GeV'))
    p = Plot([var_hist['prompt']['LNC'][v], var_hist['prompt']['LNV'][v]], ['LNC events', 'LNV events'], color_palette = 'Lines', x_name = variables[v][2][0], y_name = variables[v][2][1], draw_ratio = 'from_signal', extra_text = extra_text, for_paper = True)
    p.drawHist(out_dir + '/prompt', draw_option = 'EHist')
    p = Plot([var_hist['displaced']['LNC'][v], var_hist['displaced']['LNV'][v]], ['LNC events', 'LNV events'], color_palette = 'Lines', x_name = variables[v][2][0], y_name = variables[v][2][1], draw_ratio = 'from_signal', extra_text = extra_text, for_paper = True)
    p.drawHist(out_dir +'/displaced', draw_option = 'EHist')
