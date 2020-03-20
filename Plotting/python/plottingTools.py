from ROOT import TMath
import numpy as np
from HNL.Tools.helpers import sortByOtherList, getMaxWithErr, getMinWithErr

def getOverallMaximum(hist):
    current_max = 0
    for h in hist:
        loc_max = getMaxWithErr(h)
        if loc_max > current_max :    current_max = loc_max
    return current_max

def getOverallMinimum(hist, zero_not_allowed = False):
    current_min = 999999
    for h in hist:
        loc_min = getMinWithErr(h, zero_not_allowed)
        if loc_min < current_min:    current_min = loc_min
    return current_min

def getNestedMin(arr):
    local_min = []
    for a in arr:
        local_min.append(np.min(a))
    return np.min(local_min)

def getNestedMax(arr):
    local_max = []
    for a in arr:
        local_max.append(np.max(a))
    return np.max(local_max)

def getXMin(graphs):
    xmin = 99999.
    for graph in graphs:
        if TMath.MinElement(graph.GetN(), graph.GetX()) < xmin:
            xmin = TMath.MinElement(graph.GetN(), graph.GetX())
    return xmin

def getXMax(graphs):
    xmax = -99999.
    for graph in graphs:
        if TMath.MaxElement(graph.GetN(), graph.GetX()) > xmax:
            xmax = TMath.MaxElement(graph.GetN(), graph.GetX())
    return xmax

def getYMin(graphs):
    ymin = 99999.
    for graph in graphs:
        if TMath.MinElement(graph.GetN(), graph.GetY()) < ymin:
            ymin = TMath.MinElement(graph.GetN(), graph.GetY())
    return ymin

def getYMax(graphs):
    ymax = -99999.
    for graph in graphs:
        if TMath.MaxElement(graph.GetN(), graph.GetY()) > ymax:
            ymax = TMath.MaxElement(graph.GetN(), graph.GetY())
    return ymax

def orderHist(hist, names, lowest_first = False):
    weight = -1.
    if lowest_first: weight = 1.
    sof = [h.GetSumOfWeights()*weight for h in hist]
    return sortByOtherList(hist, sof), sortByOtherList(names, sof)

def extraTextFormat(text, xpos = None, ypos = None, textsize = None, align = 12):
    return [text, xpos, ypos, textsize, align]

def removeNegativeErrors(h):
    for xbin in xrange(1, th1.GetSize()-1):                     #GetSize returns nbins + 2 (for overflow and underflow bin)
        if (h.GetBinContent(xbin) - h.GetBinErrorLow(xbin)) < 0:
            h.SetBinError

def getUnit(x):
    if x.find('[') == -1:
        return ''
    else:
        return x[x.find('[')+len('['):x.rfind(']')]

def allBinsSameWidth(hist):
    bin_array = [hist.GetBinWidth(b) for b in xrange(hist.GetNbinsX())]
    return bin_array.count(bin_array[0]) == len(bin_array)

def writeMessage(output_dir, message):
    out_file = open(output_dir + '/note.txt', 'w')
    out_file.write(message)
    out_file.close()
