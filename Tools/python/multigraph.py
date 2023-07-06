from ROOT import TMultiGraph
import numpy as np
import array as array
from ROOT import TFile

class MultiGraph():

    def __init__(self, graphs = None):
        if graphs is None:
            self.graphs = []
        else:
            self.graphs = graphs

    def LoadGraphs(self, in_path, in_name):
        from HNL.Tools.helpers import getObjFromFile, rootFileContent
        in_file = TFile(in_path, 'read')
        in_names = [x[0].split('/')[-1] for x in rootFileContent(in_file, starting_dir = in_name+'_dir')]
        for iname in in_names:
            self.graphs.append(getObjFromFile(in_path, in_name+'_dir/'+iname))
        self.OrderGraphs()

    def OrderGraphs(self):
        def getSortKey(graphs): 
            from HNL.Plotting.plottingTools import getXMin 
            return getXMin([graphs])  
        self.graphs = sorted(self.graphs, key = getSortKey)

    def Add(self, graph):
        self.graphs.append(graph)
        self.OrderGraphs()
    
    def GetN(self):
        ntot = 0
        for g in self.graphs:
            ntot += g.GetN()
        return ntot

    def GetX(self):
        out_list = []
        for g in self.graphs:
            out_list.extend(g.GetX())
        out_list =  array.array('d', out_list)
        return out_list
    
    def GetY(self):
        out_list = []
        for g in self.graphs:
            out_list.extend(g.GetY())
        out_list =  array.array('d', out_list)
        return out_list

    def SetFillColor(self, color):
        for g in self.graphs:
            g.SetFillColor(color)
    
    def SetFillStyle(self, style):
        for g in self.graphs:
            g.SetFillStyle(style)
    
    def SetLineColor(self, color):
        for g in self.graphs:
            g.SetLineColor(color)
    
    def SetLineStyle(self, style):
        for g in self.graphs:
            g.SetLineStyle(style)

    def SetLineWidth(self, width):
        for g in self.graphs:
            g.SetLineWidth(width)

    def SetMarkerStyle(self, style):
        for g in self.graphs:
            g.SetMarkerStyle(style)

    def GetMultiGraph(self):
        out_obj = TMultiGraph()
        for g in self.graphs:
            out_obj.Add(g)
        return out_obj

    def write(self, out_name, obj_name, append=False):
        out_file = TFile(out_name , 'recreate' if not append else 'update')
        mgraph = self.GetMultiGraph()
        mgraph.Write(obj_name)
        out_file.mkdir(obj_name+'_dir')
        out_file.cd(obj_name+'_dir')    
        for i, g in enumerate(self.graphs):
            g.Write(str(i))
        out_file.Close() 
