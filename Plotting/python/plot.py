#
# Plot class
#
import HNL.Plotting.plottingTools as pt
import HNL.Plotting.style as ps
import HNL.Plotting.tdrstyle as tdr
import array as arr
import numpy as np
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
    if not isinstance(item, (list,)) and not isinstance(item, set):
        item = [item]
    return item

import HNL.Tools.histogram
from  HNL.Tools.histogram import returnSqrt
def getHistList(item):
    if item is None or not isinstance(item[0], HNL.Tools.histogram.Histogram):
        return item
    else:
        try:
            return [h.getHist() for h in item]
        except:
            return item.getHist()
    

#
# Define class
#
import HNL.Plotting.CMS_lumi as cl
import os
import ROOT
from HNL.Tools.helpers import isTimeStampFormat, makeDirIfNeeded
from HNL.Plotting.style import setDefault, setDefault2D
class Plot:
    
    def __init__(self, signal_hist, tex_names, name = None, x_name = None, y_name = None, bkgr_hist = None, extra_text = None, x_log = None, y_log = None, draw_ratio = False, draw_significance = False):
        self.s = makeList(getHistList(signal_hist))
        self.tex_names = makeList(tex_names)
        self.s_tex_names = self.tex_names[:len(self.s)] 
        self.b_tex_names = self.tex_names[len(self.s):] 
        self.name = name if name else self.s[0].GetTitle()
        self.b = makeList(getHistList(bkgr_hist)) if bkgr_hist is not None else None
        if self.b is not None:
            self.total_b = self.b[0].Clone('total_bkgr')
            for i, h in enumerate(self.b):
                if i != 0:      self.total_b.Add(h)
        else:
            self.total_b = None
        self.hs = None  #hist stack for bkgr
        self.x_name = x_name if x_name is not None else self.s[0].GetXaxis().GetTitle()
        self.y_name = y_name if y_name is not None else self.s[0].GetYaxis().GetTitle()
        self.canvas = None #Can not be created until gROOT and gStyle settings are set
        self.plotpad = None
        self.x_log = x_log
        self.y_log = y_log
        self.extra_text = [i for i in extra_text] if extra_text is not None else None
        self.draw_ratio = draw_ratio
        self.draw_significance = draw_significance



    def setAxisLog(self, is2D = False, stacked = True):
        to_check_min = [j for j in self.s]
        if stacked and self.b is None: 
            self.total_s = self.s[0].Clone('total_sig')
            for i, h in enumerate(self.s):
                if i != 0:      self.total_s.Add(h)
            to_check_max = [self.total_s]
        else:
            to_check_max = [j for j in self.s]
        if self.b is not None:  
            to_check_min += self.b
            if stacked: to_check_max += [self.total_b]
            else: to_check_max += self.b

        if not is2D:
            overall_max = pt.getOverallMaximum(to_check_max)
            overall_min = pt.getOverallMinimum(to_check_min, zero_not_allowed=True)

        if self.x_log:
            #self.canvas.SetLogx()
            self.plotpad.SetLogx()
        if self.y_log:
            #self.canvas.SetLogy()
            self.plotpad.SetLogy()
            if not is2D:
                if stacked:
                    self.hs.SetMinimum(0.3*overall_min)
                    self.hs.SetMaximum(30*overall_max)
                    # self.hs.SetMinimum(0.3*pt.getOverallMinimum([self.s[0]], zero_not_allowed=True))
                    # self.hs.SetMaximum(30*overall_max)
                elif self.b is None: 
                    self.s[0].SetMinimum(0.3*overall_min)
                    self.s[0].SetMaximum(30*overall_max)
                else:
                    self.b[0].SetMinimum(0.3*overall_min)
                    self.b[0].SetMaximum(30*overall_max)
        else:
            if not is2D:
                if self.b is None: 
                    if not stacked: self.s[0].GetYaxis().SetRangeUser(0.7*overall_min, 1.5*overall_max)
                    else: 
                        self.hs.SetMinimum(0.7*overall_min)
                        self.hs.SetMaximum(1.5*overall_max)
                        # self.hs.GetHistogram().GetYaxis().SetRangeUser(0.7*overall_min, 1.5*overall_max)
                else: 
                    if not stacked: self.b[0].GetYaxis().SetRangeUser(0.7*overall_min, 1.5*overall_max)
                    else: 
                        self.hs.SetMinimum(0.7*overall_min)
                        self.hs.SetMaximum(1.5*overall_max)
                        # self.hs.GetHistogram().GetYaxis().SetRangeUser(0.7*overall_min, 1.5*overall_max)


        self.plotpad.Update()

    from HNL.Plotting.plottingTools import allBinsSameWidth
    def getYName(self):   
        add_x_width = allBinsSameWidth(self.s[0])
        if '[' in self.y_name:
            return
        elif add_x_width: 
            self.y_name +=  ' / ' +str(self.s[0].GetBinWidth(1)) +' '+ pt.getUnit(self.x_name)

        return

    def drawExtraText(self):
        self.canvas.cd()

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
        #self.plotpad.Update()

        return

    def setPads(self):
        plot_pad_y = 0.05
        if self.draw_significance and self.draw_ratio:
            self.sig_pad = ROOT.TPad('sig_pad', 'sig_pad', 0, 0.05, 1, 0.25)
            self.ratio_pad = ROOT.TPad('ratio_pad', 'ratio_pad', 0, 0.25, 1, 0.45)
            self.ratio_pad.SetBottomMargin(0.05)
            plot_pad_y = 0.45
        elif self.draw_ratio:
            self.ratio_pad = ROOT.TPad('ratio_pad', 'ratio_pad', 0, 0.05, 1, 0.25)
            self.ratio_pad.SetBottomMargin(0.3)
            plot_pad_y = 0.25
        elif self.draw_significance:
            self.sig_pad = ROOT.TPad('sig_pad', 'sig_pad', 0, 0.05, 1, 0.25)
            plot_pad_y = 0.25
             
        self.plotpad = ROOT.TPad('plotpad', 'plotpad', 0, plot_pad_y, 1, 0.98)

        self.plotpad.Draw()
        if self.draw_ratio:
            self.plotpad.SetBottomMargin(0.)
            self.ratio_pad.SetTopMargin(0.05)
            self.ratio_pad.Draw()

        if self.draw_significance:
            self.plotpad.SetBottomMargin(0.)
            self.sig_pad.SetTopMargin(0.05)
            self.sig_pad.SetBottomMargin(0.3)
            self.sig_pad.Draw()

        return        

    def calculateRatio(self):
        ratios = []
        for i, s in enumerate(self.s):
            ratios.append(s.Clone('ratio'))
            ratios[i].Divide(self.total_b)

        return ratios

    def drawRatio(self, ratios):
        self.ratio_pad.cd()        

        #Set axis: if significance is also drawn, no x-axis
        if self.draw_significance:
            ratios[0].SetTitle('; ; S/B')
        else:
            ratios[0].SetTitle(';'+ self.x_name+'; S/B')
        ratios[0].SetMinimum(0.3)
        ratios[0].SetMaximum(1.7)
        ratios[0].GetXaxis().SetTitleSize(.12)
        ratios[0].GetYaxis().SetTitleSize(.12)
        ratios[0].GetXaxis().SetLabelSize(.12)
        ratios[0].GetYaxis().SetLabelSize(.12)
        ratios[0].GetYaxis().SetTitleOffset(.6)
        if self.draw_significance:
            ratios[0].GetXaxis().SetLabelOffset(999999)
        else:
            ratios[0].GetXaxis().SetTitleOffset(1.0)
            

        for r in ratios:
            r.SetMarkerStyle(20)
            r.SetMarkerColor(r.GetLineColor())

        #Draw a guide for the eye
        self.line = ROOT.TLine(ratios[0].GetXaxis().GetXmin(),1,ratios[0].GetXaxis().GetXmax(),1)
        self.line.SetLineColor(ROOT.kBlack)
        self.line.SetLineWidth(1)
        self.line.SetLineStyle(3)
        
        ratios[0].Draw('EP')
        for r in ratios[1:]:
            r.Draw('EPSame')
       
        self.line.Draw()
        
        self.ratio_pad.Update() 
        self.canvas.cd() 
        self.canvas.Update() 
        return self.ratio_pad
   
    def calculateSignificance(self):
        significances = []
        for i, s in enumerate(self.s):
            tot = s.Clone('tot')
            tot.Add(self.total_b)
            significances.append(returnSqrt(tot))

        return significances
    
    def drawSignificance(self, significances):
        self.sig_pad.cd()

        #Set axis: if significance is also drawn, no x-axis
        significances[0].SetTitle(';'+ self.x_name+'; S/#sqrt{S+B}')
        significances[0].SetMinimum(0.)
        significances[0].GetXaxis().SetTitleSize(.12)
        significances[0].GetYaxis().SetTitleSize(.12)
        significances[0].GetXaxis().SetTitleOffset(1.0)
        significances[0].GetXaxis().SetLabelSize(.12)
        significances[0].GetYaxis().SetLabelSize(.12)
        significances[0].GetYaxis().SetTitleOffset(0.6)
        
        for r in significances:
            r.SetMarkerStyle(20)
            r.SetMarkerColor(r.GetLineColor())

        significances[0].Draw('EP')
        for r in significances[1:]:
            r.Draw('EPSame')

        self.sig_pad.Update()
        self.canvas.cd()
        self.canvas.Update() 
        return self.sig_pad

    def savePlot(self, destination, message = None):
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


        self.canvas.SaveAs(destination + ".pdf")
        self.canvas.SaveAs(destination + ".png")
        self.canvas.SaveAs(destination + ".root")
        #Clean out the php directory you want to write to if it is already filled, otherwise things go wrong with updating the file on the website
        #os.system("rm "+php_destination.rsplit('/')[0]+"/*")

        if index_for_php:
            self.canvas.SaveAs(php_destination + ".pdf")
            self.canvas.SaveAs(php_destination + ".png")
            self.canvas.SaveAs(php_destination + ".root")

        if message is not None:
            pt.writeMessage(destination.rsplit('/', 1)[0], message)
    
    #Width
    # Functions to do actual plotting
    #

    def drawHist(self, output_dir = None, normalize_signal = False, signal_style = False, draw_option = 'EHist', bkgr_draw_option = 'Stack', draw_cuts = None, message = None):

        setDefault()
        #Create Canvas
        self.canvas = ROOT.TCanvas("Canv"+self.name, "Canv"+self.name, 1000, 1000)
        self.setPads()
        #self.plotpad = ROOT.TPad('plotpad', 'plotpad', 0, 0.01, 1, 0.98)
        self.plotpad.Draw()
        self.plotpad.cd()

        if isinstance(self.x_name, list):
            print 'invalid x_names'
            return
        
        if self.draw_ratio or self.draw_significance:
            title = " ; ; "+self.y_name
        else:
            title = " ;" +self.x_name+ " ; "+self.y_name
        
        #Set Bkgr Histogram Styles
        #Do this first so it is not overlapping the signal
        if self.b is not None:
            self.total_b = self.b[0].Clone('total_bkgr')
            for i, (h, n) in enumerate(zip(self.b, self.b_tex_names)):
                h.SetLineColor(ps.getStackColorTauPOGbyName(n))
                h.SetLineWidth(3)
                if i != 0:      self.total_b.Add(h)
            
            if bkgr_draw_option == 'Stack':
                self.b, self.b_tex_names = pt.orderHist(self.b, self.b_tex_names, lowest_first = True)
                self.hs = ROOT.THStack("hs", "hs")
                for i, (h, n) in enumerate(zip(self.b, self.b_tex_names)):
                    h.SetFillColor(ps.getStackColorTauPOGbyName(n))
                    self.hs.Add(h)
        
        self.s, self.s_tex_names = pt.orderHist(self.s, self.s_tex_names) #Order signals so those with 0 sum of weights come last and arent skipped (which cause the axis to not be updated)
        self.tex_names = self.s_tex_names + self.b_tex_names
     
        if self.b is not None:
            if bkgr_draw_option == 'Stack':
                self.hs.Draw(draw_option)                                                            #Draw before using GetHistogram, see https://root-forum.cern.ch/t/thstack-gethistogram-null-pointer-error/12892/4
                self.hs.SetTitle(title)
                if self.draw_ratio or self.draw_significance: 
                    self.hs.GetHistogram().GetXaxis().SetLabelOffset(9999999)

            else:
                for i, b in enumerate(self.b):
                    if i == 0:
                        b.Draw(bkgr_draw_option)
                        b.SetTitle(title)
                        if self.draw_ratio or self.draw_significance: 
                            b.GetXaxis().SetLabelOffset(9999999)
                    else:
                        b.Draw(bkgr_draw_option + 'Same')
            #self.hs.GetHistogram().SetMaximum(1)   
        tdr.setTDRStyle()                       #TODO: Find out why we need a setTDRStyle after drawing the stack
 
        #Set Signal Histogram Styles
        for h, n in zip(self.s, self.tex_names):
            if signal_style:
                h.SetLineColor(ps.getHNLColor(n))
                h.SetLineWidth(4)
            else:
                # print self.s.index(h)
                h.SetLineColor(ps.getHistDidar(self.s.index(h)))
                #h.SetLineColor(ps.getLineColor(self.s.index(h)))
                h.SetLineWidth(4)
                h.SetMarkerStyle(8)
                h.SetMarkerColor(ps.getHistDidar(self.s.index(h)))
                #h.SetMarkerColor(ps.getLineColor(self.s.index(h)))
        if self.b is None:      self.s[0].SetTitle(title)       #If no bkgr was given, the SetTitle was not done yet
        
        #print 'e'
        #Start Drawing
        for h in self.s:
            if h.GetSumOfWeights() == 0: continue
            if normalize_signal and self.b is not None:
                h.Scale(self.total_b.GetSumOfWeights()/h.GetSumOfWeights())

            if(self.s.index(h) == 0 and self.b is None):
                h.Draw(draw_option)
                if self.draw_ratio or self.draw_significance: 
                    h.GetXaxis().SetLabelOffset(9999999)
            else:
                h.Draw(draw_option+'Same')
           # h.Draw("EHistSAME")
        self.setAxisLog(stacked = self.b is not None and 'Stack' in bkgr_draw_option)

        #Option only used in plotVariables.py
        if draw_cuts is not None:
            if self.extra_text is None: self.extra_text = []
            lines = []
            i = 0 #Cant use enumerate because of if statement, first filled value might be at i=2 but lines[2] doesnt exist then
            for j, (h, l) in enumerate(zip(self.s, draw_cuts[0])):
                if l is not None:
                    lines.append(ROOT.TLine(l, 0, l, self.s[0].GetMaximum()))
                    lines[i].SetLineColor(self.s[j].GetLineColor())
                    lines[i].SetLineStyle(10)
                    lines[i].SetLineWidth(2)
                    lines[i].Draw('Same')
                    self.extra_text.append(pt.extraTextFormat('p_{T}(l'+str(j+1)+') < '+str(l) +' GeV'))
                    i += 1
            self.extra_text.append(pt.extraTextFormat('Eff: %.4g' % draw_cuts[1]+'%'))

        #Write extra text
        if self.extra_text is not None:
            self.drawExtraText()

        
        self.canvas.cd()
        #Create Legend
        legend = ROOT.TLegend(0.5, .8, .9, .9)
        legend.SetNColumns(3)
       
        loop_obj = [item for item in self.s]
        if self.b is not None: loop_obj.extend(self.b)
        for h, n in zip(loop_obj, self.tex_names):
            legend.AddEntry(h, n)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        legend.Draw()

        if self.draw_ratio:
            ratios = self.calculateRatio()
            self.drawRatio(ratios)
            self.ratio_pad.Update()
        if self.draw_significance:
            significances = self.calculateSignificance()
            self.drawSignificance(significances)
            self.sig_pad.Update()

        ROOT.gPad.Update() 
        self.canvas.Update()
        #CMS lumi
        cl.CMS_lumi(self.canvas, 4, 11, 'Preliminary', False)

        #Save everything
        self.savePlot(output_dir +'/'+ self.name, message)
        ROOT.SetOwnership(self.canvas, False)
        return


    def draw2D(self, option='ETextColz', output_dir = None, message = None):
     
        setDefault2D()    
        self.canvas = ROOT.TCanvas("Canv"+self.name, "Canv"+self.name, 1000, 1000)
        self.setAxisLog(is2D=True)
        
        if isinstance(self.x_name, list):
            print 'invalid x_names'
            return
        
        for h in self.s:
            h.SetTitle(';'+self.x_name+';'+self.y_name) 
            h.Draw(option)
            output_name = output_dir +'/'+h.GetName() #Not using name here because loop over things with different names
            cl.CMS_lumi(self.canvas, 4, 0, 'Preliminary', True)
            self.savePlot(output_name, message)
            self.canvas.Clear()
        return

    def drawGraph(self, output_dir = None, message = None):
        
        setDefault()
        
        #Create Canvas
        self.canvas = ROOT.TCanvas("Canv"+self.name, "Canv"+self.name, 1000, 1000)

        self.setPads()
        self.plotpad.Draw()
        self.plotpad.cd()

        #Create TGraph
        mgraph = ROOT.TMultiGraph()
       
        for i, graph in enumerate(self.s):
            graph.SetMarkerSize(1.5)
            graph.SetLineColor(ps.getLineColor(i))
            graph.SetMarkerColor(ps.getLineColor(i))
            graph.SetMarkerStyle(ps.getMarker(i))
            mgraph.Add(graph)

        mgraph.Draw("APLine")
        if isinstance(self.x_name, list):
            print 'invalid x_names'
            return
        mgraph.SetTitle(";" + self.x_name + ";" + self.y_name)
 
        xmax = pt.getXMax(self.s)
        xmin = pt.getXMin(self.s)
        ymax = pt.getYMax(self.s)
        ymin = pt.getYMin(self.s)

        if self.x_log :
            self.plotpad.SetLogx()
            mgraph.GetXaxis().SetRangeUser(0.3*xmin, 30*xmax)
        else :
            mgraph.GetXaxis().SetRangeUser(0.7*xmin, 1.3*xmax)
        
        if self.y_log:
            self.plotpad.SetLogy()
            mgraph.GetYaxis().SetRangeUser(0.3*ymin, 10*ymax)
        else :
            mgraph.GetYaxis().SetRangeUser(0.5*ymin, 1.2*ymax)       

 
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
        cl.CMS_lumi(self.canvas, 4, 11, 'Simulation', False)

        #Save everything
        self.savePlot(output_dir +'/'+ self.name, message = None)
        ROOT.SetOwnership(self.canvas, False)
        
    def drawBarChart(self, output_dir = None, parallel_bins=False, message = None):
        
        setDefault()
        #Create Canvas
        self.canvas = ROOT.TCanvas("Canv"+self.name, "Canv"+self.name, 1000, 1000)
        self.setPads()
        self.plotpad.Draw()
        self.plotpad.cd()
        
        # self.s, self.s_tex_names = pt.orderHist(self.s, self.s_tex_names, lowest_first=True) 
        # self.tex_names = self.s_tex_names + self.b_tex_names

        title = " ; ; "+self.y_name
        if isinstance(self.x_name, list) and len(self.x_name) == self.s[0].GetNbinsX():
            for i, n in enumerate(self.x_name):
                self.s[0].GetXaxis().SetBinLabel(i+1, n)

        if not parallel_bins:
            self.hs = ROOT.THStack("hs", "hs")
            #Set style
            for hist, name in zip(self.s, self.tex_names):
                hist.SetFillColor(ps.getStackColorTauPOGbyName(name))
                hist.SetLineColor(ps.getStackColorTauPOGbyName(name))
                hist.SetBarWidth(0.8)
                hist.SetBarOffset(0.1)
                self.hs.Add(hist)
     
            self.hs.Draw('B')                                                            #Draw before using GetHistogram, see https://root-forum.cern.ch/t/thstack-gethistogram-null-pointer-error/12892/4
            self.hs.SetTitle(title)

        else:
            for i, (hist, name) in enumerate(zip(self.s, self.tex_names)):
                hist.SetFillColor(ps.getStackColorTauPOGbyName(name))
                hist.SetLineColor(ps.getStackColorTauPOGbyName(name))
                hist.SetMarkerColor(ps.getStackColorTauPOGbyName(name))
                hist.SetBarWidth(0.8/len(self.s))
                hist.SetBarOffset(0.1+i*hist.GetBarWidth())
                if i == 0:
                    hist.Draw('B')
                else:
                    hist.Draw('BSame')
            self.s[0].SetTitle(title)

        self.setAxisLog(stacked = not parallel_bins)
        if not parallel_bins:
            self.hs.Draw('B')                                                        
            
        #Create Legend
        legend = ROOT.TLegend(0.7, .8, .95, .9)
        legend.SetNColumns(2)
       
        loop_obj = [item for item in self.s]
        if self.b is not None: loop_obj.extend(self.b)
        for h, n in zip(loop_obj, self.tex_names):
            legend.AddEntry(h, n)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        legend.Draw()



        ROOT.gPad.Update() 
        self.canvas.Update()
        #CMS lumi
        cl.CMS_lumi(self.canvas, 4, 11, 'Preliminary', False)

        #Save everything
        self.savePlot(output_dir +'/'+ self.name, message)
        ROOT.SetOwnership(self.canvas, False)
        return

    def drawPieChart(self, output_dir, draw_percent=False, message = None):
        setDefault()
        #Create Canvas
        self.canvas = ROOT.TCanvas("Canv"+self.name, "Canv"+self.name, 2000, 2000)
       
        colors = []
        nvals = self.s[0].GetNbinsX()
        vals = []
        for b, sample_name in enumerate(self.tex_names):
            vals.append(self.s[0].GetBinContent(b+1))
            colors.append(ps.getStackColorTauPOGbyName(sample_name)) 

        pie = ROOT.TPie('pie', 'pie', nvals, arr.array('d', vals), arr.array('i', colors))        
        
        for b, sample_name in enumerate(self.tex_names):
            label = sample_name
            #if draw_percent:
            #    label += ' ('+str(vals[b]/self.s[0].GetSumOfWeights())+'%)'
            pie.SetEntryLabel(b, label)
       
        #pie.SetLabelSize(0.8)  
        if draw_percent: pie.SetLabelFormat('%txt (%perc)')
        pie.SetCircle(0.5, 0.45, 0.25)
        pie.SetTextSize(0.04)
        #pie.Draw('rsc')
        pie.Draw('nol rsc')

        #Write extra text
        if self.extra_text is not None:
            self.drawExtraText()
        
        self.canvas.Update()

        #Save everything
        self.savePlot(output_dir +'/'+ self.name, message)
        ROOT.SetOwnership(self.canvas, False)
        return

         
