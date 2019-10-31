import ROOT
from ROOT import TLine, THStack, TColor, TCanvas, TLegend, gROOT, gStyle, TH1, TMultiGraph, TGraphErrors, TGraph, TLatex, TPad, TMath
import HNL.Plotting.CMS_lumi as cl
import HNL.Plotting.tdrstyle as tdr
import numpy as np
from HNL.Tools.helpers import makeDirIfNeeded, isTimeStampFormat, sortByOtherList, getMaxWithErr, getMinWithErr
import os

def GeneralSettings(paintformat = "4.2f"):
    gROOT.SetBatch(True)
    gStyle.SetOptStat(0)
    tdr.setTDRStyle()
    gStyle.SetPaintTextFormat(paintformat)
    gROOT.ProcessLine( "gErrorIgnoreLevel = 1001;")

def GetStackColor(index):
    if index == 0:      return "#4C5760"
    if index == 1:      return "#93A8AC"
    if index == 2:      return "#D7CEB2"
    if index == 3:      return "#F4FDD9"
    if index == 4:      return "#AA767C"
    if index == 5:      return "#D6A184"

def GetStackColorTauPOG(index):
    if index == 0:      return "#18252a"
    if index == 1:      return "#de5a6a"
    if index == 2:      return "#9999cc"
    if index == 3:      return "#4496c8"
    if index == 4:      return "#e5b7e5"
    if index == 5:      return "#ffcc66"

def GetStackColorTauPOGbyName(name):
    if 'VVV' in name:           return "#87F1FF"
    elif 'TT' in name:            return "#18252a"
    elif 'VV' in name:          return "#de5a6a"
    elif 'ST' in name:          return "#9999cc"
    elif 'WJets' in name:       return "#4496c8"
    elif 'QCD' in name:         return "#e5b7e5"
    elif 'DY' in name:          return "#ffcc66"
#    elif 'H' in name:           return "#87F1FF"
    else:                       return "#F4F1BB"

def GetHistColor(index):        
    if index == 0:      return "#000000"
    if index == 1:      return "#000075"
    if index == 2:      return "#800000"
    if index == 3:      return "#f58231"
    if index == 4:      return "#3cb44d"
    if index == 5:      return "#ffe119"
    if index == 6:      return "#87F1FF"
    if index == 7:      return "#F4F1BB"

def GetLineColor(index):
    if index == 3:      return "#000000"
    if index == 4:      return "#e6194B"
    if index == 5:      return "#4363d8"
    if index == 0:      return "#B9BAA3"
    if index == 1:      return "#685762"
    if index == 2:      return "#E8C547"

def GetMarker(index):
    if index == 0:      return 20
    if index == 1:      return 21
    if index == 2:      return 22
    if index == 3:      return 23
    if index == 4:      return 24
    if index == 5:      return 25

def GetOverallMaximum(hist):
    current_max = 0
    for h in hist:
        loc_max = getMaxWithErr(h)
        if loc_max > current_max :    current_max = loc_max
    return current_max

def GetOverallMinimum(hist, zero_not_allowed = False):
    current_min = 999999
    for h in hist:
        loc_min = getMinWithErr(h)
        if loc_min <= 0 and zero_not_allowed: continue
        if loc_min < current_min:    current_min = loc_min
    return current_min

def GetNestedMin(arr):
    localMin = []
    for a in arr:
        localMin.append(np.min(a))
    return np.min(localMin)

def GetNestedMax(arr):
    localMax = []
    for a in arr:
        localMax.append(np.max(a))
    return np.max(localMax)

def GetXMin(graphs):
    xmin = 99999.
    for graph in graphs:
        if TMath.MinElement(graph.GetN(),graph.GetX()) < xmin:
            xmin = TMath.MinElement(graph.GetN(),graph.GetX())
    return xmin

def GetXMax(graphs):
    xmax = -99999.
    for graph in graphs:
        if TMath.MaxElement(graph.GetN(),graph.GetX()) > xmax:
            xmax = TMath.MaxElement(graph.GetN(),graph.GetX())
    return xmax

def GetYMin(graphs):
    ymin = 99999.
    for graph in graphs:
        if TMath.MinElement(graph.GetN(),graph.GetY()) < ymin:
            ymin = TMath.MinElement(graph.GetN(),graph.GetY())
    return ymin

def GetYMax(graphs):
    ymax = -99999.
    for graph in graphs:
        if TMath.MaxElement(graph.GetN(),graph.GetY()) > ymax:
            ymax = TMath.MaxElement(graph.GetN(),graph.GetY())
    return ymax

def orderHist(hist, names, lowestFirst = False):
    weight = -1.
    if lowestFirst: weight = 1.
    sof = [h.GetSumOfWeights()*weight for h in hist]
    return sortByOtherList(hist, sof), sortByOtherList(names, sof)

def extraTextFormat(text, xpos = None, ypos = None, textsize = None, align = 12):
    return [text, xpos, ypos, textsize, align]

def DrawExtraText(pad, additionalInformation):
    pad.cd()
    #Write extra text
    if additionalInformation is not None:
        lastYpos = 0.8
        lastCorrectedYpos = None
        lastXpos = 0.2
        extraText = TLatex()
        for info in additionalInformation:
            try :
                extraTextString = info[0]
                extraTextXpos = info[1]
                extraTextYpos = info[2]
                extraTextSize = info[3]
            except:
                print("Wrong Format for additionalInformation. Stopping")
                pass

            if extraTextSize is None:
                extraTextSize = 0.03
            
            correction_term = extraTextSize*(5./3.)

            if extraTextXpos is None:
                if extraTextYpos is None:
                    extraTextXpos = lastXpos
                else:
                    extraTextXpos = 0.2
            if extraTextYpos is None:
                if lastYpos is None:
                    extraTextYpos = lastCorrectedYpos - correction_term
                else: extraTextYpos = lastYpos - correction_term
            
            extraText.SetNDC()
            extraText.SetTextAlign(info[4])
            extraText.SetTextSize(extraTextSize)
            extraText.DrawLatex(extraTextXpos, extraTextYpos, extraTextString)
            
            lastXpos = extraTextXpos
            lastYpos = info[2]
            lastCorrectedYpos = extraTextYpos

    else:
        print 'Please provide the text to draw'

    pad.Update()

def getUnit(x):
    if x.find('[') == -1:
        return ''
    else:
        return x[x.find('[')+len('['):x.rfind(']')]

def savePlot(pad,  destination):
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


    pad.SaveAs(destination + ".pdf")
    pad.SaveAs(destination + ".png")
    pad.SaveAs(destination + ".root")

    #Clean out the php directory you want to write to if it is already filled, otherwise things go wrong with updating the file on the website
    #os.system("rm "+php_destination.rsplit('/')[0]+"/*")

    if index_for_php:
        pad.SaveAs(php_destination + ".pdf")
        pad.SaveAs(php_destination + ".png")
        pad.SaveAs(php_destination + ".root")


def savePlots(Canv, destination):
    destination_components = destination.split('/')
    cleaned_components = [x for x in destination_components if not isTimeStampFormat(x)]
    try:
        index_for_php = cleaned_components.index('Results')
    except:
        index_for_php = None

    if index_for_php:
        php_destination = '/user/lwezenbe/public_html/'
        php_destination += '/'.join(cleaned_components[index_for_php+1:])
        makeDirIfNeeded(php_destination.rsplit('/', 1)[0])    
        os.system('cp -rf /user/lwezenbe/private/PhD/index.php '+ php_destination.rsplit('/', 1)[0]+'/index.php')    

    print destination

    Canv.SaveAs(destination + ".pdf")
    Canv.SaveAs(destination + ".png")
    Canv.SaveAs(destination + ".root")

    #Clean out the php directory you want to write to if it is already filled, otherwise things go wrong with updating the file on the website
    #os.system("rm "+php_destination.rsplit('/')[0]+"/*")

    if index_for_php:
        Canv.SaveAs(php_destination + ".pdf")
        Canv.SaveAs(php_destination + ".png")
        Canv.SaveAs(php_destination + ".root")

def plotDataVSMC(DataHist, MCHist, xtitle, legendNames, DataName, destination, ytitle_bottom = 'Data/MC', ylog=False):
    GeneralSettings()
    
    Canv = TCanvas("Canv"+destination, "Canv"+destination, 1000, 1000)
    
    #Set Histogram Styles
    for i, h in enumerate(MCHist) :
        h.SetFillColor(TColor.GetColor(GetStackColorTauPOGbyName(legendNames[i]))) 
        h.SetLineColor(TColor.GetColor(GetStackColorTauPOGbyName(legendNames[i])))
    
    DataHist.SetMarkerColor(ROOT.kBlack)
    DataHist.SetLineColor(ROOT.kBlack)    
    DataHist.SetMarkerStyle(20)    
    
    #Add all MC samples to use in ratios
    totBkgr = MCHist[0].Clone("totBkgr")
    for h in MCHist[1:]:
        totBkgr.Add(h)
    DataOverMC = DataHist.Clone("DataOverMC")
    DataOverMC.Divide(totBkgr)

    #Errors
    predStatError = totBkgr.Clone("PredictedStatError")
    predSystError = totBkgr.Clone("PredictedSystError")
    predTotError = totBkgr.Clone("PredictedTotalError")
    for b in xrange(predSystError.GetNbinsX()+1):
        predSystError.SetBinError(b, 0.3*totBkgr.GetBinContent(b))
        syst = predSystError.GetBinError(b)
        stat = predStatError.GetBinError(b)
        predTotError.SetBinError(b, np.sqrt(stat*stat+syst*syst))

    #predTotError.SetFillStyle(3013)
    #predTotError.SetFillColor(ROOT.kGray+2)
    #predTotError.SetMarkerStyle(0)
    #predTotError.Draw("E2 Same")

    #First pad
    plotpad = TPad("plotpad", "plotpad", 0, .3, 1, 0.98)
    plotpad.SetBottomMargin(0.025)
    plotpad.Draw()
    plotpad.cd()


    #Create Stack (Change with most logical ordering)
    hs = THStack("hs", "hs")
    for h in MCHist:
        hs.Add(h)
    hs.Draw("EHist")                                                            #Draw before using GetHistogram, see https://root-forum.cern.ch/t/thstack-gethistogram-null-pointer-error/12892/4
    title = " ; ; Events / " +str(MCHist[0].GetBinWidth(1)) + " GeV"
    hs.SetTitle(title)
#    hs.GetHistogram().GetXaxis().SetTickLength(0)
    hs.GetHistogram().GetXaxis().SetLabelOffset(9999999)
    hs.GetHistogram().SetMaximum(1)    

    #Set range
    overallMin = GetOverallMinimum(MCHist+[DataHist])
    overallMax = GetOverallMaximum([totBkgr]+[DataHist])
    if ylog:
        plotpad.SetLogy()
        hs.SetMinimum(0.3*overallMin)
        hs.SetMaximum(10*overallMax)
    else:
        hs.SetMinimum(0.5*overallMin)
        hs.SetMaximum(1.7*overallMax)

    DataHist.Draw("EPSame")

    predTotError.SetFillStyle(3013)
    predTotError.SetFillColor(ROOT.kGray+2)
    predTotError.SetMarkerStyle(0)
    predTotError.Draw("E2 Same")
     
    #Create Legend
    legend = TLegend(0.7, .7, .9, .9)
    for h, n in zip(MCHist, legendNames):
        legend.AddEntry(h, n)
    legend.AddEntry(DataHist, DataName)  
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)

    legend.Draw()

    #Return to canvas
    Canv.cd()

    #Second pad
    ratiopad = TPad("ratiopad", "ratiopad", 0, 0.05, 1, .3)
    ratiopad.SetTopMargin(0.05)
    ratiopad.SetBottomMargin(0.25)
    ratiopad.Draw()
    ratiopad.cd()
    
    #Errors
    StatErrorRatio = predStatError.Clone("StatErrorRatio")
    StatErrorRatio.SetFillStyle(1001)
    StatErrorRatio.SetFillColor(TColor.GetColor('#6EF9F5'))
    TotErrorRatio = predTotError.Clone("SystErrorRatio")
    TotErrorRatio.SetFillColor(TColor.GetColor('#63E2C6'))
    TotErrorRatio.SetFillStyle(1001)
    for b in xrange(StatErrorRatio.GetNbinsX()+1):
        if(StatErrorRatio.GetBinContent(b) != 0):
            StatErrorRatio.SetBinError(b, StatErrorRatio.GetBinError(b)/StatErrorRatio.GetBinContent(b))
            TotErrorRatio.SetBinError(b, TotErrorRatio.GetBinError(b)/TotErrorRatio.GetBinContent(b))
            StatErrorRatio.SetBinContent(b, 1.)
            TotErrorRatio.SetBinContent(b, 1.)
        else:
            StatErrorRatio.SetBinContent(b, 0)
            TotErrorRatio.SetBinContent(b, 0)
    
    #Set Style for bottom plot
    DataOverMC.SetTitle(";" + xtitle + "; "+ytitle_bottom)
    DataOverMC.GetXaxis().SetTitleSize(.12)
    DataOverMC.GetYaxis().SetTitleSize(.12)
    DataOverMC.GetYaxis().SetTitleOffset(.6)
    DataOverMC.GetXaxis().SetLabelSize(.12)
    DataOverMC.GetYaxis().SetLabelSize(.12)
    DataOverMC.SetMinimum(0.3)
    DataOverMC.SetMaximum(1.7)
    DataOverMC.Draw("EP")
    TotErrorRatio.Draw("E2 same")
    StatErrorRatio.Draw("E2 same")
    DataOverMC.Draw("EPsame")

    #Draw a guide for the eye
    line = TLine(DataOverMC.GetXaxis().GetXmin(),1,DataOverMC.GetXaxis().GetXmax(),1)
    line.SetLineColor(ROOT.kRed)
    line.SetLineWidth(1)
    line.SetLineStyle(1)
    line.Draw("Same")

    #Create Legend
    legend_bottom = TLegend(0.2, .8, .9, .9)
    legend_bottom.SetNColumns(3)
    legend_bottom.AddEntry(DataOverMC, "Obs./Pred.")  
    legend_bottom.AddEntry(StatErrorRatio, "Stat. Unc.")  
    legend_bottom.AddEntry(TotErrorRatio, "Tot. Unc.")  
    legend_bottom.SetFillStyle(0)
    legend_bottom.SetBorderSize(0)

    legend_bottom.Draw()
   
    #Throw CMs lumi at it
    cl.CMS_lumi(Canv, 4, 11, 'Preliminary', True)
    print 'save'
 
    #Save everything
    savePlots(Canv, destination)
    print 'saved'

def plotClosure(observed, predicted, xtitle, ytitle, DataName, additionalInfo, destination, yLog = False):
    GeneralSettings()
    
    Canv = TCanvas("Canv"+destination, "Canv"+destination, 1000, 1000)
 
    observed.SetMarkerColor(ROOT.kBlack)
    observed.SetLineColor(ROOT.kBlack)    
    observed.SetMarkerStyle(20)    
   
    predicted.SetFillColor(TColor.GetColor('#3399ff'))
    predicted.SetLineColor(TColor.GetColor('#3399ff'))
 
    #First pad
    plotpad = TPad("plotpad", "plotpad", 0, .3, 1, 0.98)
    plotpad.SetBottomMargin(0.025)
    plotpad.Draw()
    plotpad.cd()

    predicted.Draw("Hist")                                                            #Draw before using GetHistogram, see https://root-forum.cern.ch/t/thstack-gethistogram-null-pointer-error/12892/4
    title = " ; ; "+ytitle+" / " +str(predicted.GetBinWidth(1)) +' '+ getUnit(xtitle)
    predicted.SetTitle(title)
    predicted.GetXaxis().SetLabelOffset(9999999)
    
    predStatError = predicted.Clone("PredictedStatError")
    predSystError = predicted.Clone("PredictedSystError")
    predTotError = predicted.Clone("PredictedTotalError")
    for b in xrange(predSystError.GetNbinsX()+1):
        predSystError.SetBinError(b, 0.3*predicted.GetBinContent(b))
        syst = predSystError.GetBinError(b)
        stat = predStatError.GetBinError(b)
#        print syst, stat, np.sqrt(stat*stat+syst*syst)
        predTotError.SetBinError(b, np.sqrt(stat*stat+syst*syst))

    predTotError.SetFillStyle(3013)
    predTotError.SetFillColor(ROOT.kGray+2)
    predTotError.SetMarkerStyle(0)
    predTotError.Draw("E2 Same")

    #Set range
    overallMin = GetOverallMinimum([observed, predicted], yLog)
    overallMax = GetOverallMaximum([observed, predicted])

    if yLog:
        plotpad.SetLogy()
        predicted.SetMinimum(0.3*overallMin)    
        predicted.SetMaximum(10*overallMax)    
    else:
        predicted.SetMinimum(0.5*overallMin)    
        predicted.SetMaximum(1.7*overallMax)    
    observed.Draw("EPSame")
     
    #Create Legend
    legend = TLegend(0.7, .7, .9, .9)
    legend.AddEntry(observed, DataName + ' (observed)')  
    legend.AddEntry(predicted, DataName + ' (predicted)')  
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)

    legend.Draw()

    #Draw extra text
    DrawExtraText(plotpad, additionalInfo)

    #Return to canvas
    Canv.cd()

    #Second pad
    ratiopad = TPad("ratiopad", "ratiopad", 0, 0.05, 1, .3)
    ratiopad.SetTopMargin(0.05)
    ratiopad.SetBottomMargin(0.25)
    ratiopad.Draw()
    ratiopad.cd()
   
    ratio = observed.Clone('ratio')
    ratio.Divide(predicted)

    StatErrorRatio = predStatError.Clone("StatErrorRatio")
    StatErrorRatio.SetFillStyle(1001)
    StatErrorRatio.SetFillColor(TColor.GetColor('#6EF9F5'))
    TotErrorRatio = predTotError.Clone("SystErrorRatio")
    TotErrorRatio.SetFillColor(TColor.GetColor('#63E2C6'))
    TotErrorRatio.SetFillStyle(1001)
    for b in xrange(StatErrorRatio.GetNbinsX()+1):
        if(StatErrorRatio.GetBinContent(b) != 0):
            StatErrorRatio.SetBinError(b, StatErrorRatio.GetBinError(b)/StatErrorRatio.GetBinContent(b))
            TotErrorRatio.SetBinError(b, TotErrorRatio.GetBinError(b)/TotErrorRatio.GetBinContent(b))
            StatErrorRatio.SetBinContent(b, 1.)
            TotErrorRatio.SetBinContent(b, 1.)
        else:
            StatErrorRatio.SetBinContent(b, 0)
            TotErrorRatio.SetBinContent(b, 0)

    #Set Style for bottom plot
    ratio.SetTitle(";" + xtitle + "; Obs./pred.")
    ratio.GetXaxis().SetTitleSize(.12)
    ratio.GetYaxis().SetTitleSize(.12)
    ratio.GetYaxis().SetTitleOffset(.6)
    ratio.GetXaxis().SetLabelSize(.12)
    ratio.GetYaxis().SetLabelSize(.12)
    ratio.SetMinimum(0.3)
    ratio.SetMaximum(1.7)
    ratio.Draw("EP")    
    TotErrorRatio.Draw("E2 same")
    StatErrorRatio.Draw("E2 same")
    ratio.Draw("EPsame")

    #Create Legend
    legend_bottom = TLegend(0.2, .8, .9, .9)
    legend_bottom.SetNColumns(3)
    legend_bottom.AddEntry(ratio, "Obs./Pred.")  
    legend_bottom.AddEntry(StatErrorRatio, "Stat. Unc.")  
    legend_bottom.AddEntry(TotErrorRatio, "Tot. Unc.")  
    legend_bottom.SetFillStyle(0)
    legend_bottom.SetBorderSize(0)

    legend_bottom.Draw()

    #Draw a guide for the eye
    line = TLine(ratio.GetXaxis().GetXmin(),1,ratio.GetXaxis().GetXmax(),1)
    line.SetLineColor(ROOT.kRed)
    line.SetLineWidth(1)
    line.SetLineStyle(1)
    line.Draw("Same")
   
    #Throw CMs lumi at it
    cl.CMS_lumi(Canv, 4, 11, 'Preliminary', True)
 
    #Save everything
    savePlots(Canv, destination)

def plotROC(xdata, ydata, xlabel, ylabel, legendNames,destination, xerror = None, yerror = None, xlog = False, ylog = False, additionalInformation = None):
    GeneralSettings()
    #Make sure single curves also pass
    try:
        len(xdata[0])
    except:
        xdata = [xdata]
        ydata = [ydata]
        legendNames = [legendNames]
        xerror = [xerror]
        yerror = [yerror]
    
    #Create Canvas
    Canv = TCanvas("Canv"+destination, "Canv"+destination, 1000, 1000)
    
    tdr.setTDRStyle()
    
    #Create TGraph
    graphs = []
    for x, y, xe, ye in zip(xdata, ydata, xerror, yerror):
        tmpgraph = None
        if xe is None and ye is None: 
            tmpgraph = TGraph(len(x), x, y)
        elif xe is None or ye is None:
            NullErrors = np.zeros(len(x))
            if xe is not None:      tmpgraph = TGraphErrors(len(x), x, y, xe, NullErrors)
            if ye is not None:      tmpgraph = TGraphErrors(len(x), x, y, NullErrors, ye)
        else:
            tmpgraph = TGraphErrors(len(x), x, y, xe, ye)
        graphs.append(tmpgraph)
    
    mgraph = TMultiGraph()
    
    for i, graph in enumerate(graphs):
        graph.SetMarkerSize(1.5)
        graph.SetLineColor(TColor.GetColor(GetLineColor(graphs.index(graph))))
        graph.SetMarkerColor(TColor.GetColor(GetLineColor(graphs.index(graph))))
        graph.SetMarkerStyle(GetMarker(graphs.index(graph)))
        mgraph.Add(graph)

    mgraph.Draw("APLine")
    mgraph.SetTitle(";" + xlabel + ";" + ylabel)
    
    cl.CMS_lumi(Canv, 4, 11, 'Simulation', False)
 
    if xlog :
        Canv.SetLogx()
        mgraph.GetXaxis().SetRangeUser(0.3*GetNestedMin(xdata), 30*GetNestedMax(xdata))
    else :
        mgraph.GetXaxis().SetRangeUser(0.7*GetNestedMin(xdata[0]), 1.3*GetNestedMax(xdata))
    
    if ylog :
        Canv.SetLogy()
        mgraph.GetYaxis().SetRangeUser(0.3*GetNestedMin(ydata), 10*GetNestedMax(ydata))
    else :
        mgraph.GetYaxis().SetRangeUser(0.5*GetNestedMin(ydata), 1.2*GetNestedMax(ydata))
   
    #Write extra text
    if additionalInformation is not None:
        lastYpos = 0.8
        lastCorrectedYpos = None
        extraText = TLatex()
        for info in additionalInformation:
            try :
                extraTextString = info[0]
                extraTextXpos = info[1]
                extraTextYpos = info[2]
                extraTextSize = info[3]
            except:
                print("Wrong Format for additionalInformation. Stopping")
                pass
            
            if extraTextSize is None:
                extraTextSize = 0.03
            if extraTextXpos is None:
                extraTextXpos = 0.2
            if extraTextYpos is None:
                if lastYpos is None:
                    extraTextYpos = lastCorrectedYpos -0.05 
                else: extraTextYpos = 0.8
            
            extraText.SetNDC()
            extraText.SetTextAlign(12)
            extraText.SetTextSize(extraTextSize)
            extraText.DrawLatex(extraTextXpos, extraTextYpos, extraTextString)
            
            lastYpos = info[2]
            lastCorrectedYpos = extraTextYpos

    if legendNames:
        legend = TLegend(0.7, .7, .9, .9)
        for g, n in zip(graphs, legendNames):
            legend.AddEntry(g, n)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        legend.Draw() 

    #Save everything
    savePlots(Canv, destination)

def plotROCfromgraph(graphs, xlabel, ylabel, legendNames,destination, xlog = False, ylog = False, additionalInformation = None):
    GeneralSettings()
    #Make sure single curves also pass
    try:
        len(graphs)
    except:
        graphs = [graphs]    

    #Create Canvas
    Canv = TCanvas("Canv"+destination, "Canv"+destination, 1000, 1000)
    
    tdr.setTDRStyle()
    
    #Create TGraph
    mgraph = TMultiGraph()
    
    for i, graph in enumerate(graphs):
        graph.SetMarkerSize(1.5)
        graph.SetLineColor(TColor.GetColor(GetLineColor(graphs.index(graph))))
        graph.SetMarkerColor(TColor.GetColor(GetLineColor(graphs.index(graph))))
        graph.SetMarkerStyle(GetMarker(graphs.index(graph)))
        mgraph.Add(graph)

    mgraph.Draw("APLine")
    mgraph.SetTitle(";" + xlabel + ";" + ylabel)
    
    cl.CMS_lumi(Canv, 4, 11, 'Simulation', False)
    
    xmax = GetXMax(graphs)
    xmin = GetXMin(graphs)
    ymax = GetYMax(graphs)
    ymin = GetYMin(graphs)

    if xlog :
        Canv.SetLogx()
        mgraph.GetXaxis().SetRangeUser(0.3*xmin, 30*xmax)
    else :
        mgraph.GetXaxis().SetRangeUser(0.7*xmin, 1.3*xmax)
    
    if ylog :
        Canv.SetLogy()
        mgraph.GetYaxis().SetRangeUser(0.3*ymin, 10*ymax)
    else :
        mgraph.GetYaxis().SetRangeUser(0.5*ymin, 1.2*ymax)
   
    #Write extra text
    if additionalInformation is not None:
        lastYpos = 0.8
        lastCorrectedYpos = None
        extraText = TLatex()
        for info in additionalInformation:
            try :
                extraTextString = info[0]
                extraTextXpos = info[1]
                extraTextYpos = info[2]
                extraTextSize = info[3]
            except:
                print("Wrong Format for additionalInformation. Stopping")
                pass
            
            if extraTextSize is None:
                extraTextSize = 0.03
            if extraTextXpos is None:
                extraTextXpos = 0.2
            if extraTextYpos is None:
                if lastYpos is None:
                    extraTextYpos = lastCorrectedYpos -0.05 
                else: extraTextYpos = 0.8
            
            extraText.SetNDC()
            extraText.SetTextAlign(12)
            extraText.SetTextSize(extraTextSize)
            extraText.DrawLatex(extraTextXpos, extraTextYpos, extraTextString)
            
            lastYpos = info[2]
            lastCorrectedYpos = extraTextYpos

    if legendNames:
        legend = TLegend(0.7, .7, .9, .9)
        for g, n in zip(graphs, legendNames):
            legend.AddEntry(g, n)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        legend.Draw() 

    #Save everything
    savePlots(Canv, destination)

def DrawHist(hist, xlabel, ylabel, legendNames, destination, ylog = False):
    GeneralSettings()

    #Create Canvas
    Canv = TCanvas("Canv"+destination, "Canv"+destination, 1000, 1000)

    tdr.setTDRStyle()

    #Set Histogram Styles
    for h in hist:
        h.SetLineColor(TColor.GetColor(GetHistColor(hist.index(h))))
    title = " ;" +xlabel+ " ; "+ylabel+" / " +str(hist[0].GetBinWidth(1)) + " GeV"
    hist[0].SetTitle(title)
    
    OverallMax = GetOverallMaximum(hist)
    OverallMin = GetOverallMinimum(hist)

    if ylog :
        Canv.SetLogy()
        hist[0].GetYaxis().SetRangeUser(0.3*OverallMin, 30*OverallMax)
    else :
        hist[0].GetYaxis().SetRangeUser(0.7*OverallMin, 1.3*OverallMax)

    #Start Drawing
    for h in hist:
        if(hist.index(h) == 0) :
            h.Draw("HIST")
        else:
            h.Draw("HISTSAME")
    #Create Legend
    if legendNames :
        legend = TLegend(0.7, .7, .9, .9)
        for h, n in zip(hist, legendNames):
            legend.AddEntry(h, n)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        legend.Draw()
    
    #CMS lumi
    cl.CMS_lumi(Canv, 4, 11, 'Simulation', False)

    #Save everything
    savePlots(Canv, destination)

def calcAndDrawSignificance(SignalHist, BkgrHist, xtitle, legendNames, DataName, destination, ylog = False, customLabels = None, extraText = None, scaleSignalToBkgr = False, DivideByLine = None):
    GeneralSettings()

    #Make sure the code works for single backgrounds
    if not isinstance(BkgrHist,(list,)):    
        BkgrHist = [BkgrHist]
    if not isinstance(SignalHist,(list,)):
        SignalHist = [SignalHist]

    BkgrHist, legendNames = orderHist(BkgrHist, legendNames)

    #Add all backgrounds
    totBkgr = BkgrHist[0].Clone("TotBkgr")
    for h in BkgrHist[1:]:
        totBkgr.Add(h)
   
    #Normalize signal to background if needed
    if scaleSignalToBkgr:
        for h in SignalHist:
            h.scale(totBkgr.GetSumOfWeights()/h.GetSumOfWeights)

    #Define a canvas
    Canv = TCanvas("Canv"+destination, "Canv"+destination, 1500, 1000)

    #Set Histogram Styles
    for h, n in zip(BkgrHist, legendNames):
        h.SetFillColor(TColor.GetColor(GetStackColorTauPOGbyName(n)))
        h.SetLineColor(TColor.GetColor(GetStackColorTauPOGbyName(n)))

    for i, h in enumerate(SignalHist):
        h.SetMarkerColor(TColor.GetColor(GetLineColor(i)))
        h.SetLineColor(TColor.GetColor(GetLineColor(i)))
        h.SetMarkerStyle(GetMarker(i))

    list_of_significance_hists = []
    for i, sh in enumerate(SignalHist):
        #Calculate significance
        total = totBkgr.Clone("Total")
        total.Add(sh)
        sqrt_total = total.Clone('Sqrt_Total')
        for xbin in xrange(1, total.GetSize()-1):                     #GetSize returns nbins + 2 (for overflow and underflow bin)
            sqrt_x = np.sqrt(total.GetBinContent(xbin))
            sqrt_total.SetBinContent(xbin, sqrt_x)
            sqrt_total.SetBinError(xbin, 0.5*total.GetBinError(xbin)/sqrt_x)
        
        significance = sh.Clone('Signal'+str(i))
        significance.Divide(sqrt_total)
        list_of_significance_hists.append(significance)

    #First pad
    plotpad = TPad("plotpad", "plotpad", 0, .3, 1, 0.98)
    plotpad.SetBottomMargin(0.025)
    plotpad.Draw()
    plotpad.cd()

    #Create Stack (Change with most logical ordering)
    hs = THStack("hs", "hs")
    for h in BkgrHist:
        hs.Add(h)
    hs.Draw("EHist")                                                            #Draw before using GetHistogram, see https://root-forum.cern.ch/t/thstack-gethistogram-null-pointer-error/12892/4
    title = " ; ; Events"
    hs.SetTitle(title)
#    hs.GetHistogram().GetXaxis().SetTickLength(0)
    hs.GetHistogram().GetXaxis().SetLabelOffset(9999999)
    #hs.GetHistogram().SetMaximum(1)
    #Set range
    overallMin = GetOverallMinimum(BkgrHist+SignalHist, True)
    overallMax = GetOverallMaximum([totBkgr]+SignalHist)
  
     
    if ylog :
        if overallMin == 0.:
            overallMin = 0.1
        ymin = 0.3*overallMin
        ymax = 30*overallMax
        plotpad.SetLogy()
    else :
        ymin = 0.7*overallMin
        ymax = 1.3*overallMax
    hs.SetMinimum(ymin)
    hs.SetMaximum(ymax)

    for h in SignalHist:
        h.Draw("EPSame")
    #Create Legend
    legend = TLegend(0.7, .7, .9, .9)
    for h, n in zip(BkgrHist, legendNames):
        legend.AddEntry(h, n)
    for h, n in zip(SignalHist, DataName):
        legend.AddEntry(h, n)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)

    legend.Draw()
    
    #Draw lines if needed
    if DivideByLine is not None:
        tdrStyle_Left_Margin = 0.16
        tdrStyle_Right_Margin = 0.02
        plot_size_hor = 1 - tdrStyle_Left_Margin - tdrStyle_Right_Margin
        #Option one, user provides the number of divisions and we divide equally
        if isinstance(DivideByLine[0], int):
            x_pos = np.linspace(totBkgr.GetXaxis().GetXmin(), totBkgr.GetXaxis().GetXmax(), DivideByLine[0]+1)
        #Option two, user provides the specific boundaries
        if isinstance(DivideByLine[0], (list,)):
            x_pos =  DivideByLine[0]

        #Draw the lines
        lines = []
        for i, x in enumerate(x_pos[1:-1]):
            lines.append(TLine(x, ymin, x, ymax))
            lines[i].SetLineColor(ROOT.kRed)
            lines[i].SetLineStyle(10)
        
        for line in lines:
            line.Draw('same')

        #Add extra text
        for i, name in enumerate(DivideByLine[1]):
            x = ((x_pos[i+1]+x_pos[i])/(2*(x_pos[-1]-x_pos[0])/plot_size_hor)) + tdrStyle_Left_Margin
            extraText.append(extraTextFormat(name, x, 0.1, None, 22))

    #Draw extra text if needed
    if extraText is not None:
        DrawExtraText(plotpad, extraText)
    
    #Return to canvas
    Canv.cd()
    
    #Second pad
    ratiopad = TPad("ratiopad", "ratiopad", 0, 0.05, 1, .3)
    ratiopad.SetTopMargin(0.05)
    ratiopad.SetBottomMargin(0.25)
    ratiopad.Draw()
    ratiopad.cd()

    #print list_of_significance_hists[0].GetMaximum(), list_of_significance_hists[1].GetMaximum(), list_of_significance_hists[2].GetMaximum()
    overallMin = GetOverallMinimum(list_of_significance_hists)
    overallMax = GetOverallMaximum(list_of_significance_hists)

    significance = list_of_significance_hists[0]
    
    #Prepare lines before changing maximum
    lines_bottom = []
    for i, sig in enumerate(list_of_significance_hists):
        lines_bottom.append(TLine(sig.GetXaxis().GetXmin(), sig.GetMaximum(),sig.GetXaxis().GetXmax() , sig.GetMaximum()))
        lines_bottom[i].SetLineColor(TColor.GetColor(GetLineColor(i)))
        lines_bottom[i].SetLineStyle(3)

    #Set Style for bottom plot
    significance.SetTitle(";" + xtitle + "; S/#sqrt{S+B}")
    significance.GetXaxis().SetTitleSize(.12)
    significance.GetYaxis().SetTitleSize(.12)
    significance.GetYaxis().SetTitleOffset(.6)
    significance.GetXaxis().SetLabelSize(.12)
    significance.GetYaxis().SetLabelSize(.12)
    significance.SetMinimum(0.)
    significance.SetMaximum(1.3*overallMax)
    significance.Draw("EP")
    
    for sig in list_of_significance_hists[1:]:
        sig.Draw('EPSame')
    
    for line in lines_bottom:
        line.Draw("same")

    #Set custom x labels
    xaxis = significance.GetXaxis()
    if customLabels != None:
        number_of_bins = significance.GetNbinsX()
        
        if number_of_bins != len(customLabels):
            if DivideByLine is not None:
                for i in range(number_of_bins):
                    xaxis.SetBinLabel(i+1, customLabels[i%len(customLabels)]) #Only works when DivideByLine[0] is an integer
            else:
                print 'Please provide '+str(number_of_bins)+ ' labels instead of '+ str(len(customLabels))
                return
        else:
            for i, label  in zip(range(number_of_bins), customLabels):
                xaxis.SetBinLabel(i+1, label)  
  
    #Throw CMs lumi at it
    cl.CMS_lumi(Canv, 4, 11, 'Simulation Preliminary', True)

    #Save everything
    savePlots(Canv, destination)
    ROOT.SetOwnership(Canv,False)               #https://root-forum.cern.ch/t/tlatex-crashing-in-pyroot-after-many-uses/21638/4
    return

from HNL.Plotting.style import setDefault2D
def draw2DHist(h, xlabel, ylabel, output, option="ETextColz", x_log = False, y_log = False):
    
#    tdr.setTDRStyle()
#    GeneralSettings("4.3f")
#    gStyle.SetPalette(ROOT.kIsland)
#    gStyle.SetPadRightMargin(0.15)
#    setDefault2D()     

    #Create Canvas
    Canv = TCanvas("Canv"+output, "Canv"+output, 1000, 1000)
    if x_log:
        Canv.SetLogx()
    if y_log:
        Canv.SetLogy()

    h.SetTitle(';'+xlabel+';'+ylabel) 
    h.Draw(option)
        
    #Throw CMs lumi at it
    cl.CMS_lumi(Canv, 4, 0, 'Preliminary', True)

    #Save everything
    savePlot(Canv, output)

    ROOT.SetOwnership(Canv,False)               #https://root-forum.cern.ch/t/tlatex-crashing-in-pyroot-after-many-uses/21638/4
    return

    



