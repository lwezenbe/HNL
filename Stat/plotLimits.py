
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--datacard', default=None, type=str,  help='What final state datacard should be used?')
submission_parser.add_argument('--compareToExternal',   type=str, nargs='*',  help='Compare to a specific experiment')
submission_parser.add_argument('--compareToCards', default = None,  type=str, nargs='*',  help='Compare to a specific card if it exists. If you want different selection use "selection/card" otherwise just "card"')
submission_parser.add_argument('--output',   type=str, help='Compare to a specific card if it exists. If you want different selection use "selection/card" otherwise just "card"')
submission_parser.add_argument('--extratext',   type=str, help='Add extra text to plot')
submission_parser.add_argument('--signalTexName',   type=str, help='Add extra text to plot')
submission_parser.add_argument('--bkgrTexNames',   nargs = '*', default = None, type=str, help='Define tex names')
submission_parser.add_argument('--flavor', action='store', default='',  help='Which coupling should be active?' , choices=['tau', 'e', 'mu'])
submission_parser.add_argument('--blind', action='store_true', default=False,  help='Do not plot observed')
submission_parser.add_argument('--plotSingleBackground', action='store', default=None,  help='if "compareToCards" needs to be plotted as a single entry, give legend name here')
submission_parser.add_argument('--ignoreExpected', action='store_true', default=False,  help='Only plot observed')
submission_parser.add_argument('--ignoreBands', action='store_true', default=False,  help='Only plot observed')
submission_parser.add_argument('--yaxis', action='store', default=None,  help='custom y axis label')
argParser.add_argument('--paperPlots',   action='store_true',     default=False,  help='Slightly adapt the plots to be paper-approved')
args = argParser.parse_args()

import os
in_base_folder = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'output')

comparegraph_dict = {
    'cutbased'      :       'Cutbased',
    'NoTau-prompt'  :       'Prompt',
    'MaxOneTau-prompt'  :       'Prompt',
    'Dirac'             :       'Dirac'
}

def getCompareCardTex(in_name):
    for cck in comparegraph_dict.keys():
        if cck in in_name:
            return comparegraph_dict[cck]
    return in_name

#Load in the main graphs
from ROOT import TMultiGraph
from HNL.Tools.multigraph import MultiGraph
from HNL.Tools.helpers import getObjFromFile
def getGraphObjFromFile(in_name, obj_name):
    obj = getObjFromFile(in_name, obj_name)
    if isinstance(obj, TMultiGraph):
        out_obj = MultiGraph()
        out_obj.LoadGraphs(in_name, obj_name)
        return out_obj
    else:
        return obj


main_graphs = []
print os.path.join(in_base_folder, args.datacard, 'limits.root')
main_graphs.append(getGraphObjFromFile(os.path.join(in_base_folder, args.datacard, 'limits.root'), 'expected_central'))
main_graphs.append(getGraphObjFromFile(os.path.join(in_base_folder, args.datacard, 'limits.root'), 'expected_1sigma'))
main_graphs.append(getGraphObjFromFile(os.path.join(in_base_folder, args.datacard, 'limits.root'), 'expected_2sigma'))
if not args.blind:
    observed = getGraphObjFromFile(os.path.join(in_base_folder, args.datacard, 'limits.root'), 'observed')
    if observed is not None:
        main_graphs.append(observed)

main_masses = set([x for x in main_graphs[0].GetX()])
main_masses = sorted([x for x in main_masses])

from HNL.Plotting.plottingTools import extraTextFormat
if args.flavor == 'e':
    coupling_text = 'V_{eN}:V_{#muN}:V_{#tauN} = 1:0:0'
elif args.flavor == 'mu':
    coupling_text = 'V_{eN}:V_{#muN}:V_{#tauN} = 0:1:0'
elif args.flavor == 'tau':
    coupling_text = 'V_{eN}:V_{#muN}:V_{#tauN} = 0:0:1'
extra_text = [extraTextFormat(coupling_text)]
if args.extratext is not None:
    extra_text.append(extraTextFormat(args.extratext))

bkgr_hist = None
tex_names = None
#Prepare external limit contributions
if args.compareToExternal is not None:
    from HNL.Stat.stateOfTheArt import makeGraphList
    bkgr_hist, tex_names = makeGraphList(args.flavor, args.compareToExternal, sorted([x for x in main_masses]))

#Prepare internal limit contributions
if args.compareToCards is not None:
    for cc in args.compareToCards:
        cc_graph = getGraphObjFromFile(os.path.join(in_base_folder, cc, 'limits.root'), 'observed') if not args.blind else None
        if cc_graph is None:
            print os.path.join(in_base_folder, cc, 'limits.root')
            cc_graph = getGraphObjFromFile(os.path.join(in_base_folder, cc, 'limits.root'), 'expected_central')
           
        tex_name = getCompareCardTex(cc) 
        if args.blind:
            tex_name += ' (Expected)' 
        if bkgr_hist is None:
            bkgr_hist = [cc_graph]
            tex_names = [tex_name]
        else:
            bkgr_hist.append(cc_graph)
            tex_names.append(tex_name)

if args.bkgrTexNames is not None:
    tex_names = args.bkgrTexNames


def getRatio(graph1, graph2):
    x_values_1 = [x for x in graph1.GetX()]
    x_values_2 = [x for x in graph2.GetX()]
    y_values_1 = [y for y in graph1.GetY()]
    y_values_2 = [y for y in graph2.GetY()]

    new_x_values = []
    new_graph1_y_values = []
    new_graph2_y_values = []
    second_index = 0
    for first_index, first_value in enumerate(x_values_1):
        if second_index >= len(x_values_2):
            break
        
        # Case 1, both lists have the same value at the same index
        if first_value == x_values_2[second_index]:
            new_x_values.append(first_value)
            new_graph1_y_values.append(y_values_1[first_index])
            new_graph2_y_values.append(y_values_2[second_index])
            second_index += 1
            continue
        # Case 2, value 1 is lower than value 2
        if first_value < x_values_2[second_index]:
            if first_value not in x_values_2:
                continue
            # Case 2.1, There are multiple entries for value 1
            # Case 2.2. there is just one entry but it is not in x_values_2, just skip it
            if x_values_1.count(first_value) > 1:
                #Just add it again
                new_x_values.append(first_value)
                new_graph1_y_values.append(y_values_1[first_index])
                new_graph2_y_values.append(y_values_2[second_index-1])
            continue
        #Case 3: value 1 is higher than value 2
        if first_value > x_values_2[second_index]:
            # Case 3.1, value 2 is not in x_values_1 but value 1 is in x_values_2, jump forward to correct index
            # Case 3.2, value 2 is not in x_values_1 and vice versa, 
            if x_values_2[second_index] not in x_values_1 and first_value in x_values_2:
                second_index = x_values_2.index(first_value)
                new_x_values.append(first_value)
                new_graph1_y_values.append(y_values_1[first_index])
                new_graph2_y_values.append(y_values_2[second_index])
                second_index += 1
            elif x_values_2[second_index] not in x_values_1 and first_value not in x_values_2:
                second_index += 1
            else:
                print 'Weird'
            continue

    from ROOT import TGraph
    graph = TGraph(len(new_x_values))
    for ix, x_val in enumerate(new_x_values):
        graph.SetPoint(ix, x_val, new_graph1_y_values[ix]/new_graph2_y_values[ix])
    return graph

if args.paperPlots: 
    ratios = None
else:
    ratios = []
    if tex_names is not None and bkgr_hist is not None:
        for tn, bh in zip(tex_names, bkgr_hist):
            ratios.append(getRatio(main_graphs[0], bh))
    if len(ratios) < 1:
        ratios = None

from HNL.Plotting.plot import Plot
from HNL.Stat.combineTools import coupling_dict
year = args.datacard.split('UL')[1].split('/')[0]
y_axis_label = args.yaxis if args.yaxis is not None else '|V_{'+coupling_dict[args.flavor]+' N}|^{2}'
p = Plot(main_graphs, tex_names, 'limits', extra_text = extra_text, bkgr_hist = bkgr_hist, y_log = True, x_log=True, x_name = 'm_{N} [GeV]', y_name = y_axis_label, era = 'UL', year = year, draw_ratio = ratios, for_paper = args.paperPlots)
p.drawBrazilian(output_dir = os.path.join(in_base_folder, args.output), ignore_expected = args.ignoreExpected, signal_legend=args.signalTexName, ignore_bands = args.ignoreBands)
