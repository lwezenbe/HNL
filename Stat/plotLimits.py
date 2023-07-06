
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--datacards', nargs = '*', default=None, type=str,  help='What final state datacards should be used?')
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
for dc in args.datacards:
    tmp_list = []
    tmp_list.append(getGraphObjFromFile(os.path.join(in_base_folder, dc, 'limits.root'), 'expected_central'))
    tmp_list.append(getGraphObjFromFile(os.path.join(in_base_folder, dc, 'limits.root'), 'expected_1sigma'))
    tmp_list.append(getGraphObjFromFile(os.path.join(in_base_folder, dc, 'limits.root'), 'expected_2sigma'))
    if not args.blind:
        observed = getGraphObjFromFile(os.path.join(in_base_folder, dc, 'limits.root'), 'observed')
        if observed is not None:
            tmp_list.append(observed)
    main_graphs.append([x for x in tmp_list])
    del tmp_list
    try:
        del observed
    except:
        pass

def getSortKey(graphs):
    from HNL.Plotting.plottingTools import getXMin
    return getXMin([graphs[0]]) 

main_graphs = sorted(main_graphs, key = getSortKey)
#Get set of masses contained in main_graphs

main_masses = set()
for mg in main_graphs:
    main_masses.update([x for x in mg[0].GetX()])

from HNL.Plotting.plottingTools import extraTextFormat
if args.flavor == 'e':
    coupling_text = 'V_{Ne}:V_{N#mu}:V_{N#tau} = 1:0:0'
elif args.flavor == 'mu':
    coupling_text = 'V_{Ne}:V_{N#mu}:V_{N#tau} = 0:1:0'
elif args.flavor == 'tau':
    coupling_text = 'V_{Ne}:V_{N#mu}:V_{N#tau} = 0:0:1'
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
        
from HNL.Plotting.plot import Plot
from HNL.Stat.combineTools import coupling_dict
year = args.datacards[0].split('UL')[1].split('/')[0]
y_axis_label = args.yaxis if args.yaxis is not None else '|V_{'+coupling_dict[args.flavor]+' N}|^{2}'
p = Plot(main_graphs, tex_names, 'limits', extra_text = extra_text, bkgr_hist = bkgr_hist, y_log = True, x_log=True, x_name = 'm_{N} [GeV]', y_name = y_axis_label, era = 'UL', year = year)
p.drawBrazilian(output_dir = os.path.join(in_base_folder, args.output), multiple_signals = True, ignore_expected = args.ignoreExpected, signal_legend=args.signalTexName, ignore_bands = args.ignoreBands)
