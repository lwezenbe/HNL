
# Argument parser and logging
#
import os, argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
submission_parser = argParser.add_argument_group('submission', 'Arguments for submission. Any arguments not in this group will not be regarded for submission.')
submission_parser.add_argument('--datacards', nargs = '*', default=None, type=str,  help='What final state datacards should be used?')
submission_parser.add_argument('--output',   type=str, help='Compare to a specific card if it exists. If you want different selection use "selection/card" otherwise just "card"')
args = argParser.parse_args()

from HNL.Tools.multigraph import MultiGraph

graph_names = ['expected_central', 'expected_1sigma', 'expected_2sigma', 'observed']

from HNL.Tools.helpers import getObjFromFile
in_base_folder = os.path.join(os.path.expandvars('$CMSSW_BASE'), 'src', 'HNL', 'Stat', 'data', 'output')

mgraphs = {}
for dc in args.datacards:
    for gn in graph_names:
        try:
            graph = getObjFromFile(os.path.join(in_base_folder, dc, 'limits.root'), gn)
        except:
            graph = None
            
        if graph is not None:
            if gn not in mgraphs.keys():
                mgraphs[gn] = MultiGraph()

            mgraphs[gn].Add(graph)

from HNL.Tools.helpers import makeDirIfNeeded
from ROOT import TFile
outpath = in_base_folder + '/'+args.output+'/limits.root'
makeDirIfNeeded(outpath)
for ign, gn in enumerate(mgraphs.keys()):
    mgraphs[gn].write(outpath, gn, append = ign > 0)


