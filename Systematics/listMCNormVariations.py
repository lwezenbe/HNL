import ROOT

class MCnormalisationSyst(object):
    
    def __init__(self, syst_name, counter_name, indices, sample):
        self.syst_name = syst_name
        self.indices = indices
        self.hcounter = sample.getHist('hCounter')
        self.hCount = self.hcounter.GetSumOfWeights()
        self.syst_counter = sample.getHist(counter_name)

    def getValues(self):
        return [self.syst_counter.GetBinContent(index+1) for index in self.indices]

    def getEnvelope(self, method='minmax'):
        if method == 'minmax':
           return self.getMinMaxEnvelope()
        if method == 'rms':
            return self.getRMSEnvelope() 

    def getMinMaxEnvelope(self):
        all_values = self.getValues()
        max_val = max(all_values)
        min_val = min(all_values)
        return (self.getRelativeSyst(min_val, self.hCount, 'down'), self.getRelativeSyst(max_val, self.hCount, 'up'))

    def getRMSEnvelope(self):
        all_values = self.getValues()
        rms_value = 0.
        for val in all_values:
            rms_value += self.getRelativeSyst(val, self.hCount, 'down')**2
        import numpy as np
        rms_value = np.sqrt(rms_value/len(all_values)) 
        return (rms_value, rms_value)
        
    @staticmethod
    def getRelativeSyst(syst_val, nom_val, syst):
        if syst == 'up':
            #return (syst_val-nom_val)*100/nom_val
            return (syst_val-nom_val)*1/nom_val
        elif syst == 'down':
            return (nom_val-syst_val)*1/nom_val
        else:
            return 0.
    
   
class MEnormalisation(MCnormalisationSyst):
    
    def __init__(self, sample):
        super(MEnormalisation, self).__init__('MEnormalisation', 'lheCounter', [1, 2, 3, 4, 6, 8], sample)

    def getEnvelope(self):
        return super(MEnormalisation, self).getEnvelope(method='minmax')

class PDFnormalisation(MCnormalisationSyst):
    
    def __init__(self, sample):
        super(PDFnormalisation, self).__init__('PDFnormalisation', 'lheCounter', range(10, 112), sample)

    def getEnvelope(self):
        return super(PDFnormalisation, self).getEnvelope(method='rms')


from HNL.Plotting.style import setDefault
from HNL.Plotting.plot import Plot
import HNL.Plotting.plottingTools as pt
import HNL.Plotting.style as ps
import HNL.Plotting.tdrstyle as tdr
import array as arr
import numpy as np
import HNL.Plotting.CMS_lumi as cl

class BandPlotter(Plot):

    def __init__(self, signal_hist = None, tex_names = None, name = None, x_name = None, y_name = None, bkgr_hist = None, observed_hist = None, syst_hist = None, extra_text = None,
        x_log = None, y_log = None, draw_ratio = None, draw_significance = None, color_palette = 'HNLfromTau', color_palette_bkgr = 'HNLfromTau', year = '2016', era = 'prelegacy'):

        super(BandPlotter, self).__init__(signal_hist, tex_names, name, x_name, y_name, bkgr_hist, observed_hist, syst_hist, extra_text, x_log, y_log, draw_ratio, draw_significance, color_palette, color_palette_bkgr, year, era)


    def drawGraph(self, output_dir = None):

        setDefault()

        #Create Canvas
        self.canvas = ROOT.TCanvas("Canv"+self.name, "Canv"+self.name, 1000, 1000)

        self.setPads()
        self.plotpad.Draw()
        self.plotpad.cd()

        graphs = self.s
        values = set()
        for graph in graphs:
            for x in graph.GetX():
                values.add(x)
        values = list(values)
        frame = self.plotpad.DrawFrame(1.4, 0.001, 410, 10)
        frame.GetXaxis().SetNdivisions(508)
        frame.GetYaxis().SetTitle(self.y_name)
        frame.GetXaxis().SetTitle(self.x_name)
        frame.GetXaxis().SetLimits(0.95*min(values), 1.05*max(values))

        from ROOT import TColor
        colors = [TColor.GetColor('#78CAD2'), TColor.GetColor('#FFAC81')]

        for igraph, graph in enumerate(graphs):
            graph.SetMarkerSize(1.5)
            graph.SetLineColor(colors[igraph])
            graph.SetFillColorAlpha(colors[igraph], 0.5)
            #graph.SetMarkerColor(TColor.GetColor('#78CAD2'))
            graph.SetFillStyle(1001)
            #graph.SetFillStyle(3017)

        graphs[0].Draw('F')
        for igraph, graph in enumerate(graphs):
            if igraph == 0: continue
            graph.Draw('FSame')
        if isinstance(self.x_name, list):
            print 'invalid x_names'
            return
        graphs[0].SetTitle(";" + self.x_name + ";" + self.y_name)

        #Guide for the eye
        self.line = ROOT.TLine(min(values), 1.0, max(values), 1.0)
        self.line.SetLineColor(ROOT.kBlack)
        self.line.SetLineWidth(1)
        self.line.SetLineStyle(3)
        self.line.Draw()

        frame.Draw('sameaxis')

        xmax = pt.getXMax(self.s)
        xmin = pt.getXMin(self.s)
        ymax = pt.getYMax(self.s)
        ymin = pt.getYMin(self.s)


        if self.x_log :
            self.plotpad.SetLogx()

        if self.y_log:
            self.plotpad.SetLogy()
            frame.SetMinimum(0.3*ymin)
            frame.SetMaximum(ymax*100)
        else:
            frame.SetMinimum(0.9*ymin)
            frame.SetMaximum(1.1*ymax)

        #self.setAxisLog() 
        #Write extra text
        if self.extra_text is not None:
            self.drawExtraText()

        #Create Legend
        self.canvas.cd()
        legend = ROOT.TLegend(0.5, .8, .9, .9)
        for h, n in zip(self.s, self.tex_names):
            legend.AddEntry(h, n)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        legend.Draw()


        ROOT.gPad.Update()
        self.canvas.Update()
        cl.CMS_lumi(self.canvas, 4, 11, 'Simulation', self.era+self.year)

        #Save everything
        self.savePlot(output_dir +'/'+ self.name, message = None)
        ROOT.SetOwnership(self.canvas, False)


def makePlot(input_dict, output_dir, output_name):
    from ROOT import TGraph
    out_graph = {}
    for typ in input_dict.keys():
        x_points = sorted(input_dict[typ].keys())
        npoints = len(x_points)
        out_graph[typ] = TGraph(npoints*2)
        for i, p in enumerate(x_points):
            out_graph[typ].SetPoint(i, p, 1-input_dict[typ][p][0])
            out_graph[typ].SetPoint(npoints*2-1-i, p, 1+input_dict[typ][p][1])
        from HNL.Plotting.plot import Plot
        p = BandPlotter([out_graph[typ]], [typ], name = output_name, x_name = 'mass [GeV]', y_name = 'unc.', x_log=True)
        p.drawGraph(output_dir+'/'+typ)
    
    keys = input_dict.keys()
    p = BandPlotter([out_graph[k] for k in keys], keys, name = output_name, x_name = 'mass [GeV]', y_name = 'unc.', x_log=True)
    p.drawGraph(output_dir+'/Combined')
    
if __name__ == '__main__':
    year = '2017'
    era = 'UL'
    from HNL.Samples.sampleManager import SampleManager
    sm = SampleManager(era, year, 'noskim', 'fulllist_{0}{1}'.format(era, year))
    samples = sm.createSampleList()
    plotting_dicts = {}
    for sample in samples:
        if not sample.is_signal: continue
        if sample.mass < 80: continue
        #if sample.mass < 900: continue
        print 'Working on', sample.name
        sample_prename = sample.name.rsplit('-', 1)[0]
        if sample_prename not in plotting_dicts.keys(): plotting_dicts[sample_prename] = {}
       
        #ME norm 
        if 'ME' not in plotting_dicts[sample_prename].keys(): plotting_dicts[sample_prename]['ME'] = {}
        men = MEnormalisation(sample)
        plotting_dicts[sample_prename]['ME'][sample.mass] = men.getEnvelope()
        #pdf norm 
        if 'PDF' not in plotting_dicts[sample_prename].keys(): plotting_dicts[sample_prename]['PDF'] = {}
        pdfn = PDFnormalisation(sample)
        plotting_dicts[sample_prename]['PDF'][sample.mass] = pdfn.getEnvelope()
    
    import os
    for sample_prename in plotting_dicts.keys():
        output_dir = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Systematics', 'data', 'Results'))
        makePlot(plotting_dicts[sample_prename], output_dir, sample_prename)
        
        





