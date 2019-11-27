from ROOT import TMath
import numpy as np
from HNL.Tools.helpers import sortByOtherList, getMaxWithErr, getMinWithErr

def getStackColor(index):
    if index == 0:      return "#4C5760"
    if index == 1:      return "#93A8AC"
    if index == 2:      return "#D7CEB2"
    if index == 3:      return "#F4FDD9"
    if index == 4:      return "#AA767C"
    if index == 5:      return "#D6A184"

def getStackColorTauPOG(index):
    if index == 0:      return "#18252a"
    if index == 1:      return "#de5a6a"
    if index == 2:      return "#9999cc"
    if index == 3:      return "#4496c8"
    if index == 4:      return "#e5b7e5"
    if index == 5:      return "#ffcc66"

def getStackColorTauPOGbyName(name):
    if 'VVV' in name:           return "#87F1FF"
    elif 'TT' in name:            return "#18252a"
    elif 'VV' in name:          return "#de5a6a"
    elif 'ST' in name:          return "#9999cc"
    elif 'WJets' in name:       return "#4496c8"
    elif 'QCD' in name:         return "#e5b7e5"
    elif 'DY' in name:          return "#ffcc66"
#    elif 'H' in name:           return "#87F1FF"
    else:                       return "#F4F1BB"

def getHistColor(index):        
    if index == 0:      return "#000000"
    if index == 1:      return "#000075"
    if index == 2:      return "#800000"
    if index == 3:      return "#f58231"
    if index == 4:      return "#3cb44d"
    if index == 5:      return "#ffe119"
    if index == 6:      return "#87F1FF"
    if index == 7:      return "#F4F1BB"

def getLineColor(index):
    if index == 3:      return "#000000"
    if index == 4:      return "#e6194B"
    if index == 5:      return "#4363d8"
    if index == 0:      return "#B9BAA3"
    if index == 1:      return "#685762"
    if index == 2:      return "#E8C547"

def getMarker(index):
    if index == 0:      return 20
    if index == 1:      return 21
    if index == 2:      return 22
    if index == 3:      return 23
    if index == 4:      return 24
    if index == 5:      return 25

def getOverallMaximum(hist):
    current_max = 0
    for h in hist:
        loc_max = getMaxWithErr(h)
        if loc_max > current_max :    current_max = loc_max
    return current_max

def getOverallMinimum(hist, zero_not_allowed = False):
    current_min = 999999
    for h in hist:
        loc_min = getMinWithErr(h)
        if loc_min <= 0 and zero_not_allowed: continue
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

def getUnit(x):
    if x.find('[') == -1:
        return ''
    else:
        return x[x.find('[')+len('['):x.rfind(']')]

