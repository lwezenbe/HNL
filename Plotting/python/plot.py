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
    if item is None or (isList(item) and not isinstance(item[0], HNL.Tools.histogram.Histogram)) or (not isList(item) and not isinstance(item, HNL.Tools.histogram.Histogram)):
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
    
    def __init__(self, signal_hist, tex_names, name = None, x_name = None, y_name = None, bkgr_hist = None, extra_text = None, x_log = None, y_log = None, draw_ratio = False, draw_significance = False, color_palette = 'Didar', color_palette_bkgr = 'StackTauPOGbyName', year = 2016):
        self.name = name if name else self.s[0].GetTitle()
        self.year = int(year)

        self.s = makeList(getHistList(signal_hist))
        self.total_s = self.s[0].Clone('total_sig')
        for i, h in enumerate(self.s):
            if i != 0:      self.total_s.Add(h)

        self.b = makeList(getHistList(bkgr_hist)) if bkgr_hist is not None else None
        self.total_b = None
        if self.b is not None:
            self.total_b = self.b[0].Clone('total_bkgr')
            for i, h in enumerate(self.b):
                if i != 0:      self.total_b.Add(h)

        self.tex_names = makeList(tex_names)
        self.s_tex_names = self.tex_names[:len(self.s)] 
        self.b_tex_names = self.tex_names[len(self.s):] 

        self.hs = None  #hist stack

        self.x_name = x_name if x_name is not None else self.s[0].GetXaxis().GetTitle()
        self.y_name = y_name if y_name is not None else self.s[0].GetYaxis().GetTitle()
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

    def createErrorHist(self):
        self.stat_signal_errors = [s.Clone(s.GetName()+'_statError') for s in self.s]
        self.stat_totsignal_error = self.total_s.Clone('totalSignalStatError')
        self.stat_bkgr_errors = [b.Clone(b.GetName()+'_statError') for b in self.b] if self.b is not None else None
        self.stat_totbkgr_error = self.total_b.Clone('totalSignalStatError') if self.total_b is not None else None


    def setAxisLog(self, is2D = False, stacked = True, min_cutoff = None, include_errors = True):

        if is2D:
            if self.x_log:
                self.plotpad.SetLogx()  
            if self.y_log:
                self.plotpad.SetLogy()      
        else:      

            #
            # Calculate range
            #
            to_check_min = [j for j in self.s]
            if stacked and self.b is None:
                to_check_max = [self.total_s]
            else:
                to_check_max = [j for j in self.s]
                if self.b is not None:
                    if stacked:
                        to_check_max += [self.total_b]
                    else:
                        to_check_max += [k for k in self.b]
            

            self.overall_max = max([pt.getOverallMaximum(to_check_max), 1])
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
                self.max_to_set = 1.25*self.overall_max
                self.min_to_set = min_cutoff if min_cutoff is not None else 0.7*self.overall_min

            #
            # Set min and max
            #
            if stacked:
                self.hs.SetMinimum(self.min_to_set)
                self.hs.SetMaximum(self.max_to_set)
            elif self.b is None: 
                self.s[0].SetMinimum(self.min_to_set)
                self.s[0].SetMaximum(self.max_to_set)
            else:
                self.b[0].SetMinimum(self.min_to_set)
                self.b[0].SetMaximum(self.max_to_set)

            self.plotpad.Update()

    from HNL.Plotting.plottingTools import allBinsSameWidth
    def getYName(self):   
        add_x_width = allBinsSameWidth(self.s[0])
        if '[' in self.y_name:
            return
        elif add_x_width: 
            self.y_name +=  ' / ' +str(self.s[0].GetBinWidth(1)) +' '+ pt.getUnit(self.x_name)

        return

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

    def drawRatio(self, ratios, custom_labels = None):
        self.ratio_pad.cd()        

        #Set axis: if significance is also drawn, no x-axis
        if self.draw_significance:
            ratios[0].SetTitle('; ; S/B')
        else:
            ratios[0].SetTitle(';'+ self.x_name+'; S/B')
            if custom_labels is not None:
                for i, n in enumerate(custom_labels):
                    ratios[0].GetXaxis().SetBinLabel(i+1, n)
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
    
    def drawSignificance(self, significances, custom_labels = None, line=None):
        self.sig_pad.cd()

        #Set axis: if significance is also drawn, no x-axis
        significances[0].SetTitle(';'+ self.x_name+'; S/#sqrt{S+B}')
        significances[0].SetMinimum(0.)
        significances[0].SetMaximum(1.3*pt.getOverallMaximum(significances))
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

        if signal_draw_option == 'Stack':
            self.stat_totsignal_error.SetFillStyle(3013)
            self.stat_totsignal_error.SetFillColor(ROOT.kGray+2)
            self.stat_totsignal_error.SetMarkerStyle(0)
            self.stat_totsignal_error.Draw("E2 Same")
        elif 'E' in signal_draw_option:
            for i, s in enumerate(self.s):
                self.stat_signal_errors[i].Draw("E Same")


        if self.b is not None:
            if bkgr_draw_option == 'Stack':
                self.stat_totbkgr_error.SetFillStyle(3013)
                self.stat_totbkgr_error.SetFillColor(ROOT.kGray+2)
                self.stat_totbkgr_error.SetMarkerStyle(0)
                self.stat_totbkgr_error.Draw("E2 Same")
            elif 'E' in bkgr_draw_option:
                for i, s in enumerate(self.s):
                    self.stat_bkgr_errors[i].Draw("E Same")


    def drawHist(self, output_dir = None, normalize_signal = False, draw_option = 'EHist', bkgr_draw_option = 'Stack', draw_cuts = None, custom_labels = None, draw_lines = None, message = None, min_cutoff = None):

        #
        # Some default settings
        #
        setDefault()

        #
        # Create Canvas and pads
        #
        self.canvas = ROOT.TCanvas("Canv"+self.name, "Canv"+self.name, 1000, 1000)
        self.setPads()
        self.plotpad.Draw()
        self.plotpad.cd()

        #
        # Throw some errors in case of faulty input
        #
        if isinstance(self.x_name, list):
            raise RuntimeError('invalid x_names')

        if custom_labels is not None and len(custom_labels) != self.s[0].GetNbinsX():
            raise RuntimeError("Inconsistent number of bins ("+str(self.s[0].GetNbinsX())+") compared to number of labels given ("+len(custom_labels)+")")

        if draw_option == 'Stack' and self.b is not None:
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
                    h.SetLineColor(ps.getColor(self.color_palette, color_index))
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
        if self.b is not None:
            self.total_b = self.b[0].Clone('total_bkgr')

            # Generic settings
            for i, (h, n) in enumerate(zip(self.b, self.b_tex_names)):
                color_index = ps.getPaletteIndex(self.color_palette_bkgr, i, n)
                h.SetLineColor(ps.getColor(self.color_palette_bkgr, color_index))
                h.SetLineWidth(3)
                if i != 0:      self.total_b.Add(h)
            
            # Prepare for stacking (Can not conflict with signal stacks due to runtimeError raise at the beginning)
            if bkgr_draw_option == 'Stack':
                self.b, self.b_tex_names = pt.orderHist(self.b, self.b_tex_names, lowest_first = True)
                self.hs = ROOT.THStack("hs", "hs")
                for i, (h, n) in enumerate(zip(self.b, self.b_tex_names)):
                    color_index = ps.getPaletteIndex(self.color_palette_bkgr, i, n)
                    h.SetFillColor(ps.getColor(self.color_palette_bkgr, color_index))
                    self.hs.Add(h)

        self.tex_names = self.s_tex_names + self.b_tex_names

        #
        # Set title (background is drawn first so it gets dibs)
        #
        if self.draw_ratio or self.draw_significance:
            title = " ; ; "+self.y_name
        else:
            title = " ;" +self.x_name+ " ; "+self.y_name   

        if self.b is not None:
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
        tmp_bkgr_draw_option = bkgr_draw_option.split('E')[-1]
        if self.b is not None:
            if bkgr_draw_option == 'Stack':
                self.hs.Draw("Hist")                                                            #Draw before using GetHistogram, see https://root-forum.cern.ch/t/thstack-gethistogram-null-pointer-error/12892/4
                if self.draw_ratio or self.draw_significance: 
                    self.hs.GetHistogram().GetXaxis().SetLabelOffset(9999999)
            else:
                for i, b in enumerate(self.b):
                    if i == 0:
                        b.Draw(tmp_bkgr_draw_option)
                        if self.draw_ratio or self.draw_significance: 
                            b.GetXaxis().SetLabelOffset(9999999)
                    else:
                        b.Draw(tmp_bkgr_draw_option + 'Same')


        #
        # Draw signal
        #
        tmp_draw_option = draw_option.split('E')[-1]

        if draw_option == "Stack":
            self.hs.Draw("Hist")                                                            #Draw before using GetHistogram, see https://root-forum.cern.ch/t/thstack-gethistogram-null-pointer-error/12892/4
            if self.draw_ratio or self.draw_significance: 
                self.hs.GetHistogram().GetXaxis().SetLabelOffset(9999999)
        else:
            for h in self.s:
                if h.GetSumOfWeights() == 0: continue
                if normalize_signal:
                    if self.b is None:
                        raise RuntimeError("Trying to normalize a signal to a nonexisting background in drawHist")
                    else:
                        h.Scale(self.total_b.GetSumOfWeights()/h.GetSumOfWeights())

                if(self.s.index(h) == 0 and self.b is None):
                    h.Draw(tmp_draw_option)
                else:
                    h.Draw(tmp_draw_option+'Same')

        self.drawErrors(draw_option, bkgr_draw_option)

        tdr.setTDRStyle()                       #TODO: Find out why we need a setTDRStyle after drawing the stack

        #
        # Calculate ranges of axis and set to log if requested
        #
        self.setAxisLog(stacked = (self.b is not None and 'Stack' in bkgr_draw_option) or 'Stack' in draw_option, min_cutoff = min_cutoff)

        #
        # Set custom labels if needed
        #
        if custom_labels is not None and not self.draw_ratio and not self.draw_significance:
            if self.b is not None:
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
        legend = ROOT.TLegend(0.5, .7, .9, .9)
        legend.SetNColumns(3)
       
        loop_obj = [item for item in self.s]
        if self.b is not None: loop_obj.extend(self.b)
        for h, n in zip(loop_obj, self.tex_names):
            legend.AddEntry(h, n)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        legend.Draw()

        if self.draw_ratio:
            if self.b is None:                 raise RuntimeError("Cannot ask ratio or significance if no background is given")
            ratios = self.calculateRatio()
            self.drawRatio(ratios, custom_labels)
            self.ratio_pad.Update()
        if self.draw_significance:
            if self.b is None:                 raise RuntimeError("Cannot ask ratio or significance if no background is given")
            significance_lines = []
            for s in self.s:
                significance_lines.append(ROOT.TLine(s.GetBinLowEdge(1), 0, s.GetBinLowEdge(self.s[0].GetNbinsX()+1), 0))
            significances = self.calculateSignificance(cumulative=True)
            self.drawSignificance(significances, custom_labels, significance_lines)
            self.sig_pad.Update()

        ROOT.gPad.Update() 
        self.canvas.Update()
        #CMS lumi
        cl.CMS_lumi(self.canvas, 4, 11, 'Preliminary', self.year)

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
                output_name = output_dir +'/'+names[ih] #Not using name here because loop over things with different names
            else:
                output_name = output_dir +'/'+h.GetName() #Not using name here because loop over things with different names
            cl.CMS_lumi(self.canvas, 4, 0, 'Preliminary', self.year)
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
        cl.CMS_lumi(self.canvas, 4, 11, 'Simulation', self.year)

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
     
            self.hs.Draw('B')                                                            #Draw before using GetHistogram, see https://root-forum.cern.ch/t/thstack-gethistogram-null-pointer-error/12892/4
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
            
        #Create Legend
        legend = ROOT.TLegend(0.5, .75, .95, .9)
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
        cl.CMS_lumi(self.canvas, 4, 11, 'Preliminary', self.year)

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
        ROOT.SetOwnership(self.canvas, self.year)
        return

    def close(self):
        del self.canvas         
