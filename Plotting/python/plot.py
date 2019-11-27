#
# Plot class
#
import HNL.Plotting.plottingTools as pt
import HNL.Plotting.tdrstyle as tdr
#
# Define some general functions to use later
#
def generalSettings(paintformat = "4.2f"):
    ROOT.gROOT.SetBatch(True)
    ROOT.gStyle.SetOptStat(0)
    tdr.setTDRStyle()
    ROOT.gStyle.SetPaintTextFormat(paintformat)
    ROOT.gROOT.ProcessLine( "gErrorIgnoreLevel = 1001;")

def makeList(item):
    if not isinstance(item, (list,)):
        item = [item]
    return item

#
# Define class
#
import HNL.Plotting.CMS_lumi as cl
import os
import ROOT
from HNL.Tools.helpers import isTimeStampFormat, makeDirIfNeeded
from HNL.Plotting.style import setDefault, setDefault2D
class Plot:
    
    def __init__(self, signal_hist, tex_names, name = None, x_name = None, y_name = None, bkgr_hist = None, extra_text = None, x_log = None, y_log = None):
        self.s = makeList(signal_hist)
        self.tex_names = tex_names
        self.name = name if name else self.s[0].GetTitle()
        self.b = bkgr_hist
        self.x_name = x_name if x_name else self.s[0].getXaxis().GetTitle()
        self.y_name = y_name if y_name else self.s[0].getYaxis().GetTitle()
        self.pad = None #Can not be created until gROOT and gStyle settings are set
        self.x_log = x_log
        self.y_log = y_log
        self.extra_text = extra_text
 
    def setAxisLog(self, is2D = False):
        if not is2D:
            overall_max = pt.getOverallMaximum(self.s)
            overall_min = pt.getOverallMinimum(self.s)

        if self.x_log:
            self.pad.SetLogx()
        if self.y_log:
            self.pad.SetLogy()
            if not is2D: self.s[0].GetYaxis().SetRangeUser(0.3*overall_min, 30*overall_max)
        else:
            if not is2D: self.s[0].GetYaxis().SetRangeUser(0.7*overall_min, 1.3*overall_max)

    def drawExtraText(self):
        self.pad.cd()
        #Write extra text
        if self.extra_text is not None:
            last_y_pos = 0.8
            last_corrected_y_pos = None
            last_x_pos = 0.2
            extra_text = ROOT.TLatex()
            for info in self.extra_text:
                try :
                    extra_text_string = info[0]
                    extra_text_x_pos = info[1]
                    extra_text_y_pos = info[2]
                    extra_text_size = info[3]
                except:
                    print("Wrong Format for self.extra_text. Stopping")

                if extra_text_size is None:
                    extra_text_size = 0.03
                
                correction_term = extra_text_size*(5./3.)

                if extra_text_x_pos is None:
                    if extra_text_y_pos is None:
                        extra_text_x_pos = last_x_pos
                    else:
                        extra_text_x_pos = 0.2
                if extra_text_y_pos is None:
                    if last_y_pos is None:
                        extra_text_y_pos = last_corrected_y_pos - correction_term
                    else: extra_text_y_pos = last_y_pos - correction_term
                
                extra_text.SetNDC()
                extra_text.SetTextAlign(info[4])
                extra_text.SetTextSize(extra_text_size)
                extra_text.DrawLatex(extra_text_x_pos, extra_text_y_pos, extra_text_string)
                
                last_x_pos = extra_text_x_pos
                last_y_pos = info[2]
                last_corrected_y_pos = extra_text_y_pos

        else:
            print 'Please provide the text to draw'

        self.pad.Update()
    
    def savePlot(self, destination):
        makeDirIfNeeded(destination)
        destination_components = destination.split('/')
        cleaned_components = [x for x in destination_components if not isTimeStampFormat(x)]
        try:
            index_for_php = cleaned_components.index('src')
        except:
            index_for_php = None

        if index_for_php:
            php_destination = '/user/lwezenbe/public_html/'
            php_destination += '/'.join([comp for comp in cleaned_components[index_for_php+1:] if (comp != 'data' and comp != 'Results')])
            makeDirIfNeeded(php_destination)    
            os.system('cp -rf $CMSSW_BASE/src/HNL/Tools/php/index.php '+ php_destination.rsplit('/', 1)[0]+'/index.php')    


        self.pad.SaveAs(destination + ".pdf")
        self.pad.SaveAs(destination + ".png")
        self.pad.SaveAs(destination + ".root")
        print destination + ".png"
        #Clean out the php directory you want to write to if it is already filled, otherwise things go wrong with updating the file on the website
        #os.system("rm "+php_destination.rsplit('/')[0]+"/*")

        if index_for_php:
            self.pad.SaveAs(php_destination + ".pdf")
            self.pad.SaveAs(php_destination + ".png")
            self.pad.SaveAs(php_destination + ".root")
    
    #
    # Functions to do actual plotting
    #

    def drawHist(self, output_dir = None):

        setDefault()
        #Create Canvas
        self.pad = ROOT.TCanvas("Canv"+self.name, "Canv"+self.name, 1000, 1000)

        #Set Histogram Styles
        for h in self.s:
            h.SetLineColor(ROOT.TColor.GetColor(pt.getLineColor(self.s.index(h))))
            h.SetLineWidth(3)
            h.SetMarkerStyle(8)
            h.SetMarkerColor(ROOT.TColor.GetColor(pt.getLineColor(self.s.index(h))))
        title = " ;" +self.x_name+ " ; "+self.y_name+' / ' +str(self.s[0].GetBinWidth(1)) +' '+ pt.getUnit(self.x_name)
        self.s[0].SetTitle(title)

        self.setAxisLog()

        #Start Drawing
        for h in self.s:
            if(self.s.index(h) == 0) :
                h.Draw("EP")
            else:
                h.Draw("EPSAME")

        #Create Legend
        legend = ROOT.TLegend(0.5, .8, .9, .9)
        legend.SetNColumns(2)
        for h, n in zip(self.s, self.tex_names):
            legend.AddEntry(h, n)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        legend.Draw()

        #CMS lumi
        cl.CMS_lumi(self.pad, 4, 11, 'Preliminary', False)

        #Save everything
        print output_dir +'/'+ self.name
        self.savePlot(output_dir +'/'+ self.name)


    def draw2D(self, option='ETextColz', output_dir = None):
     
        setDefault2D()    
        self.pad = ROOT.TCanvas("Canv"+self.name, "Canv"+self.name, 1000, 1000)
        self.setAxisLog(is2D=True)
        
        for h in self.s:
            h.SetTitle(';'+self.x_name+';'+self.y_name) 
            h.Draw(option)
            output_name = output_dir +'/'+h.GetName() #Not using name here because loop over things with different names
            cl.CMS_lumi(self.pad, 4, 0, 'Preliminary', True)
            self.savePlot(output_name)
            self.pad.Clear()
        return

    def drawGraph(self, output_dir = None):
        
        setDefault()
        
        #Create Canvas
        self.pad = ROOT.TCanvas("Canv"+self.name, "Canv"+self.name, 1000, 1000)

        #Create TGraph
        mgraph = ROOT.TMultiGraph()
       
        print self.s 
        for i, graph in enumerate(self.s):
            graph.SetMarkerSize(1.5)
            graph.SetLineColor(ROOT.TColor.GetColor(pt.getLineColor(i)))
            graph.SetMarkerColor(ROOT.TColor.GetColor(pt.getLineColor(i)))
            graph.SetMarkerStyle(pt.getMarker(i))
            mgraph.Add(graph)

        mgraph.Draw("APLine")
        mgraph.SetTitle(";" + self.x_name + ";" + self.y_name)
        
        
        #self.setAxisLog() 
        #Write extra text
        if self.extra_text is not None:
            self.drawExtraText()
        
        #Create Legend
        legend = ROOT.TLegend(0.5, .8, .9, .9)
        for h, n in zip(self.s, self.tex_names):
            legend.AddEntry(h, n)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        legend.Draw()
        
        cl.CMS_lumi(self.pad, 4, 11, 'Simulation', False)

        #Save everything
        print output_dir +'/'+ self.name
        self.savePlot(output_dir +'/'+ self.name)

