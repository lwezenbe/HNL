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
    ROOT.gErrorIgnoreLevel = ROOT.kWarning
    ROOT.TGaxis.SetMaxDigits(2)

def isList(item):
    if isinstance(item, (list,)) or isinstance(item, set): return True
    return False

def makeList(item):
    # if not isinstance(item, (list,)) and not isinstance(item, set):
    if not isList(item):
        item = [item]
    return item

import HNL.Tools.histogram
from  HNL.Tools.histogram import returnSqrt
def getHistList(item):
    if item is None or item == [] or (isList(item) and not isinstance(item[0], HNL.Tools.histogram.Histogram)) or (not isList(item) and not isinstance(item, HNL.Tools.histogram.Histogram)):
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
    
    def __init__(self, signal_hist = None, tex_names = None, name = None, x_name = None, y_name = None, bkgr_hist = None, observed_hist = None, syst_hist = None, extra_text = None, 
        x_log = None, y_log = None, draw_ratio = None, draw_significance = None, color_palette = 'HNLfromTau', color_palette_bkgr = 'HNLfromTau', year = '2016', era = 'prelegacy'):

        self.s = makeList(getHistList(signal_hist)) if signal_hist is not None else []
        try:
            self.total_s = self.s[0].Clone('total_sig')
            for i, h in enumerate(self.s):
                if i != 0:      self.total_s.Add(h)
        except:
            self.total_s = None

        self.name = name if name else self.s[0].GetTitle()
        self.era = era
        self.year = year

        self.b = makeList(getHistList(bkgr_hist)) if bkgr_hist is not None else []
        self.total_b = None
        if len(self.b) > 0:
            try:
                self.total_b = self.b[0].Clone('total_bkgr')
                for i, h in enumerate(self.b):
                    if i != 0:      self.total_b.Add(h)
            except:
                self.total_b = None

        self.tex_names = makeList(tex_names)
        self.s_tex_names = self.tex_names[:len(self.s)] 
        self.b_tex_names = self.tex_names[len(self.s):] 

        self.observed = getHistList(observed_hist)

        self.syst_hist = syst_hist

        self.hs = None  #hist stack

        self.x_name = x_name
        self.y_name = y_name
        if self.x_name is None:
            if len(self.s) > 0:
                self.x_name = self.s[0].GetXaxis().GetTitle()
            elif len(self.b) > 0:
                self.x_name = self.b[0].GetXaxis().GetTitle()
        if self.y_name is None:
            if len(self.s) > 0:
                self.y_name = self.s[0].GetYaxis().GetTitle()
            elif len(self.b) > 0:
                self.y_name = self.b[0].GetYaxis().GetTitle()
        try:
            if not isinstance(self.x_name, list) and not isinstance(self.x_name, dict): self.y_name = self.getYName()
        except:
            pass

        self.canvas = None #Can not be created until gROOT and gStyle settings are set
        self.plotpad = None
        self.x_log = x_log
        self.y_log = y_log

        self.extra_text = [i for i in extra_text] if extra_text is not None else None

        self.draw_ratio = draw_ratio
        self.draw_significance = draw_significance

        self.overall_max = None
        self.overall_min = None

        self.color_palette = color_palette
        self.color_palette_bkgr = color_palette_bkgr

        self.setLegend()


    def createErrorHist(self):
        if len(self.s) > 0:
            self.stat_signal_errors = [s.Clone(s.GetName()+'_statError') for s in self.s]
            self.stat_totsignal_error = self.total_s.Clone('totalSignalStatError')
        if len(self.b) > 0:
            self.stat_bkgr_errors = [b.Clone(b.GetName()+'_statError') for b in self.b] if len(self.b) > 0 else None
            self.stat_totbkgr_error = self.total_b.Clone('totalSignalStatError') if self.total_b is not None else None

            #
            # Add syst and stat together
            #
            self.tot_totbkgr_error = self.stat_totbkgr_error.Clone('Total Error on background')

            if self.syst_hist is not None:
                syst_factor = self.syst_hist
                #If the syst_hist is not a histogram but a float it will make a hist with systematic unc == float
                if isinstance(self.syst_hist, float):
                    self.syst_hist = self.stat_totbkgr_error.Clone('Systematic Error on background')
                    for b in xrange(1, self.syst_hist.GetNbinsX()+1):
                        self.syst_hist.SetBinError(b, syst_factor * self.syst_hist.GetBinContent(b))

                if self.syst_hist:
                    for b in xrange(1, self.tot_totbkgr_error.GetNbinsX()+1):
                        bin_stat_error = self.stat_totbkgr_error.GetBinError(b)
                        bin_syst_error = self.syst_hist.GetBinError(b)
                        self.tot_totbkgr_error.SetBinError(b, np.sqrt(bin_stat_error ** 2 + bin_syst_error ** 2))

    def setAxisLog(self, is2D = False, stacked = True, min_cutoff = None, max_cutoff = None):

        if is2D:
            if self.x_log:
                self.canvas.SetLogx()  
            if self.y_log:
                self.canvas.SetLogy()      
        else:      

            #
            # Calculate range
            #
            to_check_min = [j for j in self.s] if len(self.s) > 0 else [j for j in self.b]
            if stacked and (self.b is None or len(self.b) == 0) and self.total_s is not None:
                to_check_max = [self.total_s]
            else:
                to_check_max = [j for j in self.s]
                if len(self.b) > 0:
                    if stacked and len(self.b) > 0:
                        to_check_max += [self.total_b]
                    else:
                        to_check_max += [k for k in self.b]

            # self.overall_max = max([pt.getOverallMaximum(to_check_max), 1])
            self.overall_max = max([pt.getOverallMaximum(to_check_max)])
            self.overall_min = pt.getOverallMinimum(to_check_min, zero_not_allowed=True)

            if self.x_log:
                self.plotpad.SetLogx()

            # 
            # Set y log and calculate min and max
            if self.y_log:
                self.plotpad.SetLogy()

                if min_cutoff is None:
                    self.max_to_set = self.overall_max*10**((np.log10(self.overall_max)-np.log10(self.overall_min))/2)*3
                else:
                    self.max_to_set = self.overall_max*10**((np.log10(self.overall_max)-np.log10(min_cutoff))/2)*3

                self.min_to_set = min_cutoff if min_cutoff is not None else 0.3*self.overall_min
            else:
                self.max_to_set = 1.7*self.overall_max if max_cutoff is None else max_cutoff
                # self.max_to_set = 23
                self.min_to_set = min_cutoff if min_cutoff is not None else 0.7*self.overall_min

            #
            # Set min and max
            #
            if stacked:
                print self.hs
                print self.hs.GetXaxis()
                self.hs.SetMinimum(self.min_to_set)
                self.hs.SetMaximum(self.max_to_set)
                self.hs.GetXaxis().SetTitleSize(.06)
                self.hs.GetYaxis().SetTitleSize(.06)
                self.hs.GetXaxis().SetLabelSize(.06)
                self.hs.GetYaxis().SetLabelSize(.06)
                self.hs.GetYaxis().SetTitleOffset(1)
            elif len(self.b) == 0: 
                self.s[0].SetMinimum(self.min_to_set)
                self.s[0].SetMaximum(self.max_to_set)
                self.s[0].GetXaxis().SetTitleSize(.06)
                self.s[0].GetYaxis().SetTitleSize(.06)
                self.s[0].GetXaxis().SetLabelSize(.06)
                self.s[0].GetYaxis().SetLabelSize(.06)
                self.s[0].GetYaxis().SetTitleOffset(1)
            else:
                # self.b[0].SetMinimum(1e-5)
                self.b[0].SetMinimum(self.min_to_set)
                self.b[0].SetMaximum(self.max_to_set)
                # self.b[0].GetXaxis().SetRangeUser(15., 900.)
                self.b[0].GetXaxis().SetTitleSize(.06)
                self.b[0].GetYaxis().SetTitleSize(.06)
                self.b[0].GetXaxis().SetLabelSize(.06)
                self.b[0].GetYaxis().SetLabelSize(.06)
                self.b[0].GetYaxis().SetTitleOffset(1)

            self.plotpad.Update()

    def setLegend(self, x1=0.4, y1=.7, x2=.9, y2=.9, ncolumns = 2):
        self.legend = ROOT.TLegend(x1, y1, x2, y2)
        self.legend.SetNColumns(ncolumns)
        self.legend.SetTextSize(.03)
        self.legend.SetFillStyle(0)
        self.legend.SetBorderSize(0)
        return self.legend

    def getYName(self): 
        from HNL.Plotting.plottingTools import allBinsSameWidth
        test_hist = self.s[0] if len(self.s) > 0 else self.b[0]

        add_x_width = allBinsSameWidth(test_hist)


        if '[' in self.y_name:
            return self.y_name
        elif add_x_width and not '/' in self.y_name: 
            self.y_name +=  ' / ' +str(test_hist.GetBinWidth(1)) +' '+ pt.getUnit(self.x_name)

        return self.y_name

    def drawExtraText(self, pad = None):
        if pad is None: pad = self.canvas
        pad.cd()

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
        if self.draw_significance and self.draw_ratio is not None:
            self.sig_pad = ROOT.TPad('sig_pad', 'sig_pad', 0, 0.05, 1, 0.25)
            self.ratio_pad = ROOT.TPad('ratio_pad', 'ratio_pad', 0, 0.25, 1, 0.45)
            self.ratio_pad.SetBottomMargin(0.05)
            plot_pad_y = 0.45
        elif self.draw_ratio is not None:
            self.ratio_pad = ROOT.TPad('ratio_pad', 'ratio_pad', 0, 0.05, 1, 0.25)
            plot_pad_y = 0.25
        elif self.draw_significance:
            self.sig_pad = ROOT.TPad('sig_pad', 'sig_pad', 0, 0.05, 1, 0.25)
            plot_pad_y = 0.25
             
        self.plotpad = ROOT.TPad('plotpad', 'plotpad', 0, plot_pad_y, 1, 0.98)

        self.plotpad.Draw()
        if self.draw_ratio is not None:
            self.plotpad.SetBottomMargin(0.)
            self.ratio_pad.SetTopMargin(0.05)
            self.ratio_pad.SetBottomMargin(0.38)
            if self.x_log: self.ratio_pad.SetLogx()  
            self.ratio_pad.Draw()

        if self.draw_significance:
            self.plotpad.SetBottomMargin(0.)
            self.sig_pad.SetTopMargin(0.05)
            self.sig_pad.SetBottomMargin(0.1)
            self.sig_pad.Draw()

        return        

    def calculateRatio(self):
        ratios = []
        if self.observed is not None:
            ratios.append(self.observed.Clone('ratio'))
            ratios[0].Divide(self.total_b)
            #To be implemented once we start using observed in histograms as well
        for i, s in enumerate(self.s):
            ratios.append(s.Clone('ratio'))
            ratios[i].Divide(self.total_b)

        return ratios

    def drawRatio(self, ratios, custom_labels = None, just_errors = False, ref_line = 1.):
        self.ratio_pad.cd()        

        for r in ratios:
            r.SetMarkerStyle(20)
            r.SetMarkerColor(r.GetLineColor())

        if self.observed is not None:
            ytitle = 'obs./pred.'
        else:
            ytitle = 'S/B'

       #Draw errors
        self.stat_err = self.tot_totbkgr_error.Clone('stat bkgr')
        self.tot_err = self.tot_totbkgr_error.Clone('tot bkgr')
        for b in xrange(1, self.stat_err.GetNbinsX()+1):
            self.stat_err.SetBinContent(b, 1.)
            self.tot_err.SetBinContent(b, 1.)
            if self.tot_totbkgr_error.GetBinContent(b) != 0:
                self.stat_err.SetBinError(b, self.stat_totbkgr_error.GetBinError(b)/self.stat_totbkgr_error.GetBinContent(b))
                self.tot_err.SetBinError(b, self.tot_totbkgr_error.GetBinError(b)/self.tot_totbkgr_error.GetBinContent(b))
            else:
                self.stat_err.SetBinError(b, 0.)
                self.tot_err.SetBinError(b, 0.)
        self.stat_err.SetFillStyle(3001)
        self.tot_err.SetFillStyle(3001)
        self.stat_err.SetFillColor(ROOT.kCyan - 4)
        self.stat_err.SetLineColor(ROOT.kBlack)
        self.stat_err.SetLineWidth(1)
        self.stat_err.SetMarkerStyle(0)
        self.tot_err.SetFillColor(ROOT.kGray + 2)
        self.tot_err.SetLineColor(ROOT.kBlack)
        self.tot_err.SetLineWidth(1)
        self.tot_err.SetMarkerStyle(0)

        #Set axis: if significance is also drawn, no x-axis
        # self.tot_err.SetMinimum(0.3)
        # self.tot_err.SetMaximum(1.7)
        self.tot_err.SetMinimum(0.)
        self.tot_err.SetMaximum(2.)
        # self.tot_err.SetMaximum(max(2., 1.3*pt.getOverallMaximum(ratios, include_error=False)))
        # self.tot_err.GetXaxis().SetRangeUser(15., 900.)
        self.tot_err.GetXaxis().SetTitleSize(.18)
        self.tot_err.GetYaxis().SetTitleSize(.18)
        self.tot_err.GetXaxis().SetLabelSize(.18)
        self.tot_err.GetYaxis().SetLabelSize(.18)
        self.tot_err.GetYaxis().SetTitleOffset(.3)
        self.tot_err.GetYaxis().SetNdivisions(505)
        if self.draw_significance:
            self.tot_err.GetXaxis().SetLabelOffset(999999)
        else:
            self.tot_err.GetXaxis().SetTitleOffset(0.95)
        if self.draw_significance:
            self.tot_err.SetTitle('; ; '+ytitle)
        else:
            self.tot_err.SetTitle(';'+ self.x_name+'; '+ytitle)
            if custom_labels is not None:
                for i, n in enumerate(custom_labels):
                    self.tot_err.GetXaxis().SetBinLabel(i+1, n)


        self.tot_err.Draw("E2")
        self.stat_err.Draw("E2Same")


        #Draw a guide for the eye
        x_val = [-9999., -9999.]
        if len(ratios) > 0:
            x_val = [ratios[0].GetXaxis().GetXmin(), ratios[0].GetXaxis().GetXmax()]
            # self.line = ROOT.TLine(ratios[0].GetXaxis().GetXmin(),1,ratios[0].GetXaxis().GetXmax(),1)
        elif len(self.s) > 0:
            x_val = [self.s[0].GetXaxis().GetXmin(), self.s[0].GetXaxis().GetXmax()]
        elif len(self.b) > 0:
            x_val = [self.b[0].GetXaxis().GetXmin(), self.b[0].GetXaxis().GetXmax()]

        self.line = ROOT.TLine(x_val[0], ref_line, x_val[1], ref_line)
        self.line.SetLineColor(ROOT.kBlack)
        self.line.SetLineWidth(1)
        self.line.SetLineStyle(3)

        draw_text = 'EPSame'
        if self.draw_ratio == 'text': draw_text += 'Text'
        if not just_errors and len(ratios) > 0:
            for r in ratios:
                r.SetMarkerSize(1.)
                r.Draw(draw_text)

       
        self.line.Draw()

        self.ratio_legend = ROOT.TLegend(0.2, .75, .6, .9)
        self.ratio_legend.SetNColumns(3)
        self.ratio_legend.AddEntry(self.stat_err, 'Stat. Pred. Error', 'F')
        self.ratio_legend.AddEntry(self.tot_err, 'Tot. Pred. Error', 'F')
        # if self.observed is not None:
        #     self.ratio_legend.AddEntry(ratios[0], 'Obs./pred.', 'F')

        
        self.ratio_legend.SetFillStyle(0)
        self.ratio_legend.SetBorderSize(0)
        self.ratio_legend.Draw()

        if len(ratios) == 1:
            extra_text = ROOT.TLatex()
            avg = 0.
            nbins = ratios[0].GetNbinsX()
            full_range = ratios[0].GetBinLowEdge(nbins + 1) - ratios[0].GetBinLowEdge(1)
            for b in xrange(1, nbins + 1):
                if ratios[0].GetBinContent(b) == 0.:
                    full_range -= ratios[0].GetBinLowEdge(b+1) - ratios[0].GetBinLowEdge(b)
                else:
                    avg += ratios[0].GetBinContent(b) * (ratios[0].GetBinLowEdge(b+1) - ratios[0].GetBinLowEdge(b))
            if full_range > 0.: 
                avg /= full_range
                extra_text_string = "Avg. Rat. = {:.3}".format(avg)
                extra_text.SetNDC()
                extra_text.SetTextSize(0.1)
                extra_text.DrawLatex(0.55, 0.78, extra_text_string)
        
        self.ratio_pad.Update() 
        self.canvas.cd() 
        self.canvas.Update() 
        return self.ratio_pad
   
    def calculateSignificance(self, cumulative=False):
        significances = []
        if cumulative:
            significances = [s.Clone(s.GetName()+'_significance') for s in self.s]
            nbins = self.total_b.GetNbinsX() + 1
            for b in xrange(nbins):
                bkgr_val, bkgr_err = pt.getCumulativeValue(self.total_b, b)
                for i, s in enumerate(self.s):
                    signal_val, signal_err = pt.getCumulativeValue(s, b)
                    if signal_val+ bkgr_val > 0:
                        significances[i].SetBinContent(b, signal_val / np.sqrt(signal_val + bkgr_val))
                        # significances[i].SetBinError(b, 0.5 * (np.sqrt(signal_err ** 2 + bkgr_err ** 2))/np.sqrt(signal_val + bkgr_val))
                        significances[i].SetBinError(b, 0)
                    else:
                        significances[i].SetBinContent(b, 0.)
                        # sig.SetBinError(b, 0.5 * (np.sqrt(signal_err ** 2 + bkgr_err ** 2))/np.sqrt(signal_val + bkgr_val))
                        significances[i].SetBinError(b, 0)
        else:
            for i, s in enumerate(self.s):
                num = s.Clone('num')
                tot = s.Clone('tot')
                tot.Add(self.total_b)
                sqrtTot = returnSqrt(tot)
                num.Divide(sqrtTot)

                significances.append(num)

        return significances
    
    def drawSignificance(self, significances, custom_labels = None):
        self.sig_pad.cd()

        #Set axis: if significance is also drawn, no x-axis
        significances[0].SetTitle(';'+ self.x_name+'; S/#sqrt{S+B}')
        significances[0].SetMinimum(0.)
        significances[0].SetMaximum(1.3*pt.getOverallMaximum(significances, include_error=False))
        significances[0].GetXaxis().SetTitleSize(.12)
        significances[0].GetYaxis().SetTitleSize(.12)
        significances[0].GetXaxis().SetTitleOffset(1.0)
        significances[0].GetXaxis().SetLabelSize(.12)
        significances[0].GetYaxis().SetLabelSize(.12)
        significances[0].GetYaxis().SetTitleOffset(0.6)

        if custom_labels is not None:
            for i, n in enumerate(custom_labels):
                significances[0].GetXaxis().SetBinLabel(i+1, n)
        
        for r in significances:
            r.SetMarkerStyle(20)
            r.SetMarkerColor(r.GetLineColor())

        significances[0].Draw('Hist')
        for r in significances[1:]:
            r.Draw('HistSame')

        # if line is not None:
        #     for l, s in zip(line, significances):
        #         max_significance = pt.getOverallMaximum([s], include_error = False)
        #         l.SetY1(max_significance)
        #         l.SetY2(max_significance)
        #         l.SetLineColor(s.GetLineColor())
        #         l.SetLineWidth(2)
        #         l.SetLineStyle(9)
        #         l.Draw('same')

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

            cmssw_version = os.path.expandvars('$CMSSW_BASE').rsplit('/', 1)[-1]
            central_destination =  '/user/lwezenbe/private/Backup/'+cmssw_version+'/'
            central_destination += '/'.join([comp for comp in destination_components[index_for_php+1:]])
            makeDirIfNeeded(central_destination)    



        self.canvas.SaveAs(destination + ".pdf")
        self.canvas.SaveAs(destination + ".png")
        self.canvas.SaveAs(destination + ".root")

        #Clean out the php directory you want to write to if it is already filled, otherwise things go wrong with updating the file on the website
        #os.system("rm "+php_destination.rsplit('/')[0]+"/*")

        if index_for_php:
            self.canvas.SaveAs(php_destination + ".pdf")
            self.canvas.SaveAs(php_destination + ".png")
            self.canvas.SaveAs(php_destination + ".root")

        #
        # Save to a central, local backup that you can return to also after you switched CMSSW
        #
        if index_for_php:
            self.canvas.SaveAs(central_destination + ".pdf")
            self.canvas.SaveAs(central_destination + ".png")
            self.canvas.SaveAs(central_destination + ".root")

        if message is not None:
            pt.writeMessage(destination.rsplit('/', 1)[0], message)

    #
    # Functions to do actual plotting
    #

    def drawErrors(self, signal_draw_option, bkgr_draw_option):
        self.createErrorHist()

        if len(self.s) > 0:
            if signal_draw_option == 'Stack':
                self.stat_totsignal_error.SetFillStyle(3013)
                self.stat_totsignal_error.SetFillColor(ROOT.kGray+2)
                self.stat_totsignal_error.SetMarkerStyle(0)
                self.stat_totsignal_error.Draw("E2 Same")
            elif 'E' in signal_draw_option:
                for i, s in enumerate(self.s):
                    self.stat_signal_errors[i].Draw("E Same")

        if len(self.b) > 0:
            if bkgr_draw_option == 'Stack':
                self.stat_totbkgr_error.SetFillStyle(3013)
                self.stat_totbkgr_error.SetFillColor(ROOT.kGray+2)
                self.stat_totbkgr_error.SetMarkerStyle(0)
                self.stat_totbkgr_error.Draw("E2 Same")
            elif 'E' in bkgr_draw_option:
                for i in xrange(len(self.b)):
                    self.stat_bkgr_errors[i].Draw("E Same")


    def drawHist(self, output_dir = None, normalize_signal = False, draw_option = 'EHist', bkgr_draw_option = 'Stack', draw_cuts = None, 
        custom_labels = None, draw_lines = None, message = None, min_cutoff = None, max_cutoff = None, ref_line = 1., observed_name = 'Data'):

        #
        # Some default settings
        #
        setDefault()

        #
        # Create Canvas and pads
        #
        from random import randint
        rand_int = randint(0, 10000)  #Nasty trick to suppress warnings of canvas with same name
        self.canvas = ROOT.TCanvas("Canv"+self.name+str(rand_int), "Canv"+self.name+str(rand_int), 1000, 1000)
        self.setPads()
        self.plotpad.Draw()
        self.plotpad.cd()

        #
        # Throw some errors in case of faulty input
        #
        if isinstance(self.x_name, list):
            raise RuntimeError('invalid x_names')

        try:
            if custom_labels is not None and len(custom_labels) != self.s[0].GetNbinsX():
                raise RuntimeError("Inconsistent number of bins ("+str(self.s[0].GetNbinsX())+") compared to number of labels given ("+len(custom_labels)+")")
        except:
            if custom_labels is not None and len(custom_labels) != self.b[0].GetNbinsX():
                raise RuntimeError("Inconsistent number of bins ("+str(self.b[0].GetNbinsX())+") compared to number of labels given ("+len(custom_labels)+")")

        if draw_option == 'Stack' and len(self.b) > 0:
            raise RuntimeError('The "Stack" option for signal is meant to be used when there is no background. In case of background, input the hist to stack as background.')
        
        #
        # Set Signal Histogram Styles
        #
        for h, n in zip(self.s, self.tex_names):

            # Prepare for stacked signal
            if draw_option == "Stack":
                # Order signals from lowest to highest
                self.s, self.s_tex_names = pt.orderHist(self.s, self.s_tex_names, lowest_first=True)       

                self.hs = ROOT.THStack("hs", "hs")
                for i, (h, n) in enumerate(zip(self.s, self.s_tex_names)):
                    color_index = ps.getPaletteIndex(self.color_palette, self.s.index(h), n)
                    h.SetFillColor(ps.getColor(self.color_palette, color_index))
                    h.SetLineColor(ROOT.kBlack)
                    self.hs.Add(h)
            
            # Prepare for very basic signal
            elif draw_option == "HNL":
                # Order signals so those with 0 sum of weights come last and arent skipped (which causes the axis to not be updated)
                self.s, self.s_tex_names = pt.orderHist(self.s, self.s_tex_names)       

                h.SetLineColor(ps.getHNLColor(n))
                h.SetLineWidth(4)

            # Otherwise generic settings
            else:
                # Order signals so those with 0 sum of weights come last and arent skipped (which causes the axis to not be updated)
                self.s, self.s_tex_names = pt.orderHist(self.s, self.s_tex_names)       

                color_index = ps.getPaletteIndex(self.color_palette, self.s.index(h), n)
                h.SetLineColor(ps.getColor(self.color_palette, color_index))
                h.SetLineWidth(4)
                h.SetMarkerStyle(0)
                h.SetMarkerColor(ps.getColor(self.color_palette, color_index))

        #
        # Set Bkgr Histogram Styles
        #
        if len(self.b) > 0:
            self.total_b = self.b[0].Clone('total_bkgr')

            # Generic settings
            for i, (h, n) in enumerate(zip(self.b, self.b_tex_names)):
                color_index = ps.getPaletteIndex(self.color_palette_bkgr, i, n)
                if 'Filled' in bkgr_draw_option: 
                    h.SetLineColorAlpha(ps.getColor(self.color_palette_bkgr, color_index), 0.35)
                    h.SetFillColorAlpha(ps.getColor(self.color_palette_bkgr, color_index), 0.35)
                else:
                    h.SetLineWidth(3)
                    h.SetLineColor(ps.getColor(self.color_palette_bkgr, color_index))
                if i != 0:      self.total_b.Add(h)
            
            # Prepare for stacking (Can not conflict with signal stacks due to runtimeError raise at the beginning)
            if bkgr_draw_option == 'Stack':
                self.b, self.b_tex_names = pt.orderHist(self.b, self.b_tex_names, lowest_first = True)
                self.hs = ROOT.THStack("hs", "hs")
                for i, (h, n) in enumerate(zip(self.b, self.b_tex_names)):
                    color_index = ps.getPaletteIndex(self.color_palette_bkgr, i, n)
                    h.SetFillColor(ps.getColor(self.color_palette_bkgr, color_index))
                    h.SetLineColor(ROOT.kBlack)
                    h.SetLineWidth(1)
                    self.hs.Add(h)

        self.tex_names = self.s_tex_names + self.b_tex_names

        #
        # Set title (background is drawn first so it gets dibs)
        #
        if self.draw_ratio is not None or self.draw_significance:
            title = " ; ; "+self.y_name
        else:
            title = " ;" +self.x_name+ " ; "+self.y_name   

        if len(self.b) > 0:
            if bkgr_draw_option == 'Stack':
                self.hs.SetTitle(title)
            else:
                self.b[0].SetTitle(title)
        else:
            if draw_option == "Stack":
                self.hs.SetTitle(title)
            else:
                self.s[0].SetTitle(title)


        #
        # Draw background first
        #

        tmp_bkgr_draw_option = bkgr_draw_option.split('E')[-1].replace('Filled', '')
        if len(self.b) > 0:
            if bkgr_draw_option == 'Stack':
                self.hs.Draw("Hist")                                     #Draw before using GetHistogram, see https://root-forum.cern.ch/t/thstack-gethistogram-null-pointer-error/12892/4
                if self.draw_ratio is not None or self.draw_significance: 
                    self.hs.GetHistogram().GetXaxis().SetLabelOffset(9999999)
            else:
                for i, b in enumerate(self.b):
                    if i == 0:
                        b.Draw(tmp_bkgr_draw_option)
                        if self.draw_ratio is not None or self.draw_significance is not None: 
                            b.GetXaxis().SetLabelOffset(9999999)
                    else:
                        b.Draw(tmp_bkgr_draw_option + 'Same')


        #
        # Draw signal
        #
        tmp_draw_option = draw_option.split('E')[-1]

        if draw_option == "Stack":
            self.hs.Draw("Hist")                                           #Draw before using GetHistogram, see https://root-forum.cern.ch/t/thstack-gethistogram-null-pointer-error/12892/4
            if self.draw_ratio is not None or self.draw_significance: 
                self.hs.GetHistogram().GetXaxis().SetLabelOffset(9999999)
        else:
            for ih, h in enumerate(self.s):
                if h.GetSumOfWeights() == 0: continue
                if normalize_signal:
                    if len(self.b) == 0:
                        # raise RuntimeError("Trying to normalize a signal to a nonexisting background in drawHist")
                        #Normalize everything to the first histogram
                        if ih > 0:
                            h.Scale(self.s[0].GetSumOfWeights()/h.GetSumOfWeights())
                    else:
                        h.Scale(self.total_b.GetSumOfWeights()/h.GetSumOfWeights())

                if(self.s.index(h) == 0 and self.b is None):
                    h.Draw(tmp_draw_option)
                else:
                    h.Draw(tmp_draw_option+'Same')

        self.drawErrors(draw_option, bkgr_draw_option)

        #Draw observed
        if self.observed is not None:
            self.observed.SetLineColor(ROOT.kBlack)
            self.observed.SetMarkerColor(ROOT.kBlack)
            self.observed.SetMarkerStyle(8)
            self.observed.SetMarkerSize(1)
            self.observed.Draw("EPSame")


        #tdr.setTDRStyle()                       #TODO: Find out why we need a setTDRStyle after drawing the stack

        #
        # Calculate ranges of axis and set to log if requested
        #
        self.setAxisLog(stacked = (len(self.b) > 0 and 'Stack' in bkgr_draw_option) or 'Stack' in draw_option, min_cutoff = min_cutoff, max_cutoff = max_cutoff)

        #
        # Set custom labels if needed
        #
        if custom_labels is not None and not self.draw_ratio and not self.draw_significance:
            if len(self.b) > 0:
                if bkgr_draw_option == 'Stack':
                    for i, n in enumerate(custom_labels):
                        self.hs.GetHistogram().GetXaxis().SetBinLabel(i+1, n)
                else:
                    for i, n in enumerate(custom_labels):
                        self.b[0].GetXaxis().SetBinLabel(i+1, n)
            else:
                if draw_option == "Stack": 
                    for i, n in enumerate(custom_labels):
                        self.hs.GetHistogram().GetXaxis().SetBinLabel(i+1, n)
                else:
                    for i, n in enumerate(custom_labels):
                        self.s[0].GetXaxis().SetBinLabel(i+1, n)

        #
        # Option only used in plotVariables.py
        #
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

        if draw_lines is not None:
            line_collection = []
            #Multiple lines
            if isinstance(draw_lines[0], list):
                for il, l in enumerate(draw_lines):
                    x0 = l[0] if l[0] is not None else self.overall_min*0.001
                    x1 = l[1] if l[1] is not None else self.overall_max*3000
                    y0 = l[2] if l[2] is not None else self.min_to_set*0.01
                    y1 = l[3] if l[3] is not None else self.max_to_set*300
                    color = l[4] if l[4] is not None else ROOT.kBlack
                    line_collection.append(ROOT.TLine(x0, y0, x1, y1))
                    line_collection[il].SetLineColor(color)
                    line_collection[il].SetLineWidth(l[5])
                    line_collection[il].SetLineStyle(l[6])

            for l in line_collection:
                l.Draw('same')

        #Write extra text
        if self.extra_text is not None:
            self.drawExtraText()

        
        self.canvas.cd()
        #Create Legend
        # legend = ROOT.TLegend(0.4, .7, .9, .9)
        # legend.SetNColumns(1)

       
        loop_obj = [item for item in self.s]
        if len(self.b) > 0: loop_obj.extend(self.b)
        for h, n in zip(loop_obj, self.tex_names):
            self.legend.AddEntry(h, n, 'F' if not 'HNL' in n else 'L')
        if self.observed is not None:
            self.legend.AddEntry(self.observed, observed_name, 'EP')

        self.legend.Draw()

        if self.draw_ratio is not None:
            just_errors = self.draw_ratio == 'errorsOnly'
            if self.b is None:                 raise RuntimeError("Cannot ask ratio or significance if no background is given")
            ratios = self.calculateRatio()
            self.drawRatio(ratios, custom_labels, just_errors, ref_line = ref_line)
            self.ratio_pad.Update()
        if self.draw_significance is not None:
            existing_significances = isinstance(self.draw_significance, list)
            if not existing_significances and self.b is None:                 raise RuntimeError("Cannot ask ratio or significance if no background is given")
            significance_lines = []
            for s in self.s:
                significance_lines.append(ROOT.TLine(s.GetBinLowEdge(1), 0, s.GetBinLowEdge(self.s[0].GetNbinsX()+1), 0))
            
            if not existing_significances: significances = self.calculateSignificance(cumulative=True)
            else: 
                significances = self.draw_significance

            # self.drawSignificance(significances, custom_labels, significance_lines)
            self.drawSignificance(significances, custom_labels)
            self.sig_pad.Update()

        ROOT.gPad.Update() 
        self.canvas.Update()
        #CMS lumi
        cl.CMS_lumi(self.canvas, 4, 11, 'Preliminary', self.era+self.year)

        #Save everything
        self.savePlot(output_dir +'/'+ self.name, message)
        ROOT.SetOwnership(self.canvas, False)
        return


    def draw2D(self, option='ETextColz', output_dir = None, message = None, names = None):
     
        setDefault2D()    
        self.canvas = ROOT.TCanvas("Canv"+self.name, "Canv"+self.name, 1000, 1000)
        self.setAxisLog(is2D=True)
        
        if isinstance(self.x_name, list):
            print 'invalid x_names'
            return
        
        for ih, h in enumerate(self.s):
            h.SetTitle(';'+self.x_name+';'+self.y_name) 
            h.Draw(option)
            if names is not None:
                print ih, names, names[ih], output_dir
                output_name = output_dir +'/'+names[ih] #Not using name here because loop over things with different names
            else:
                output_name = output_dir +'/'+h.GetName() #Not using name here because loop over things with different names
            cl.CMS_lumi(self.canvas, 4, 0, 'Preliminary', self.era+self.year)
            self.savePlot(output_name, message)
            self.canvas.Clear()
        return

    def drawGraph(self, output_dir = None, draw_style = "APLine"):
        
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

        mgraph.Draw(draw_style)
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
        cl.CMS_lumi(self.canvas, 4, 11, 'Simulation', self.era+self.year)

        #Save everything
        self.savePlot(output_dir +'/'+ self.name, message = None)
        ROOT.SetOwnership(self.canvas, False)
        
    def drawBarChart(self, output_dir = None, parallel_bins=False, message = None, index_colors = False):
        
        #
        # Make sure hist dont have errors, otherwise style breaks down
        #

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
            for i, (hist, name) in enumerate(zip(self.s, self.tex_names)):
                if index_colors: color = ps.getStackColorTauPOG(i)
                else: color = ps.getStackColorTauPOGbyName(name)
                hist.SetFillColor(color)
                hist.SetLineColor(color)
                hist.SetBarWidth(0.8)
                hist.SetBarOffset(0.1)
                self.hs.Add(hist)
     
            self.hs.Draw('B')                     #Draw before using GetHistogram, see https://root-forum.cern.ch/t/thstack-gethistogram-null-pointer-error/12892/4
            self.hs.SetTitle(title)

        else:
            for i, (hist, name) in enumerate(zip(self.s, self.tex_names)):
                if index_colors: color = ps.getStackColorTauPOG(i)
                else: color = ps.getStackColorTauPOGbyName(name)
                hist.SetFillColor(color)
                hist.SetLineColor(color)
                hist.SetMarkerColor(color)
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
           
       #Draw observed
        if self.observed is not None:
            self.observed.SetLineColor(ROOT.kBlack)
            self.observed.SetMarkerColor(ROOT.kBlack)
            self.observed.SetMarkerStyle(8)
            self.observed.SetMarkerSize(1)
            self.observed.Draw("EPSame")
 
        #Create Legend
        legend = ROOT.TLegend(0.5, .75, .95, .9)
        legend.SetNColumns(2)
       
        loop_obj = [item for item in self.s]
        if len(self.b) > 0: loop_obj.extend(self.b)
        for h, n in zip(loop_obj, self.tex_names):
            legend.AddEntry(h, n)
        if self.observed is not None:
            legend.AddEntry(self.observed, 'data')
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        legend.Draw()



        ROOT.gPad.Update() 
        self.canvas.Update()
        #CMS lumi
        cl.CMS_lumi(self.canvas, 4, 11, 'Preliminary', self.era+self.year)

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


    #
    # For the brazilian, the expected should be contained in a list of length 3 containing the median, 68% and 95% respectively
    # or a list of length 4 also containing the observed
    # If you want to add observed and expected from prevous analysis to compare to, add those to background
    #
    def drawBrazilian(self, output_dir, ignore_bands = False):
        setDefault()
        
        #Create Canvas
        self.canvas = ROOT.TCanvas("Canv"+self.name, "Canv"+self.name, 1000, 1000)

        self.setPads()
        self.plotpad.Draw()
        self.plotpad.cd()

        median = self.s[0]
        green = self.s[1]
        yellow = self.s[2]
        try:
            observed = self.s[3]
        except:
            observed = None

        val_to_check = [v for v in yellow.GetY()]
        if self.b is not None:
            for b in self.b:
                val_to_check.extend([v for v in b.GetY()])
        max_y = max(val_to_check)
        min_y = min(val_to_check)
        values = [x for x in median.GetX()]

        frame = self.plotpad.DrawFrame(1.4, 0.001, 410, 10)
        frame.GetXaxis().SetNdivisions(508)
        frame.GetYaxis().SetTitle(self.y_name)
        frame.GetXaxis().SetTitle(self.x_name)
        frame.SetMinimum(0.3*min_y)
        frame.SetMaximum(max_y*100)
        frame.GetXaxis().SetLimits(0.95*min(values), 1.05*max(values))


        yellow.SetFillColor(ROOT.kOrange)
        yellow.SetLineColor(ROOT.kOrange)
        yellow.SetFillStyle(1001)
        if not ignore_bands: yellow.Draw('F')
    
        green.SetFillColor(ROOT.kGreen+1)
        green.SetLineColor(ROOT.kGreen+1)
        green.SetFillStyle(1001)
        if not ignore_bands: green.Draw('Fsame')
    
        median.SetLineColor(1)
        median.SetLineWidth(2)
        median.SetLineStyle(2)
        median.Draw('Lsame')

        if observed is not None:
            observed.SetLineColor(ROOT.kBlack)
            observed.SetLineWidth(2)
            observed.Draw('Lsame')

        if len(self.b) > 0:
            for i_bkgr, bkgr in enumerate(self.b):
                bkgr.SetLineColor(ps.getColor('StackTauPOG', i_bkgr))
                bkgr.SetLineWidth(2)
                bkgr.Draw('Lsame')

        frame.Draw('sameaxis')

        if self.x_log :
            self.plotpad.SetLogx()
        
        if self.y_log:
            self.plotpad.SetLogy()
        
        #Create Legend
        self.canvas.cd()
        legend = ROOT.TLegend(0.5, .7, .9, .9)
        legend.AddEntry(median, "Asymptotic CL_{s} expected",'L')
        legend.AddEntry(green, "#pm 1 std. deviation",'f')
        legend.AddEntry(yellow, "#pm 2 std. deviation",'f')
        if self.tex_names is not None and len(self.b) > 0:
            for l, b in zip(self.tex_names, self.b):
                legend.AddEntry(b, l)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        legend.Draw()
       
 
        ROOT.gPad.Update() 
        self.canvas.Update()
        cl.CMS_lumi(self.canvas, 4, 11, 'Simulation', self.era+self.year)

        #Save everything
        self.savePlot(output_dir +'/'+ self.name, message = None)
        ROOT.SetOwnership(self.canvas, False)

    def close(self):
        del self.canvas         
