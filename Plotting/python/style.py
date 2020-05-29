from ROOT import gROOT, gStyle, kIsland, TColor
import ROOT
import HNL.Plotting.tdrstyle as tdr

def setDefault(paintformat = "4.2f"):
    gROOT.SetBatch(True)
    gStyle.SetOptStat(0)
    tdr.setTDRStyle()
    gStyle.SetPaintTextFormat(paintformat)
    gROOT.ProcessLine( "gErrorIgnoreLevel = 1001;")
    # gROOT.ForceStyle()

def setDefault2D():
    setDefault()
    gStyle.SetPalette(kIsland) 
    gStyle.SetPadRightMargin(0.15) 
    #gROOT.ForceStyle()

def getColor(palette, index):
    if palette == 'Stack':
        return getStackColor(index)
    elif palette == 'StackTauPOG':
        return getStackColorTauPOG(index)
    elif palette == 'StackTauPOGbyName':
        return getStackColorTauPOGbyName(index)
    elif palette == 'Didar':
        return getHistDidar(index)
    elif palette == "Lines":
        return getLineColor(index)
    elif palette == "HNL":
        return getHNLColor(index)
    elif palette == 'WorkingPoints':
        return getWPcolor(index)
    elif palette == 'Black':
        return getBlackColor(index)
    else:
        return getHistColor(index)

def getPaletteIndex(palette, index, tex_name):
    if palette == 'StackTauPOGbyName' or palette == 'WorkingPoints':
        return tex_name
    else:
        return index

def getStackColor(index):
    if index == 0:      return TColor.GetColor("#4C5760")
    if index == 1:      return TColor.GetColor("#93A8AC")
    if index == 2:      return TColor.GetColor("#D7CEB2")
    if index == 3:      return TColor.GetColor("#F4FDD9")
    if index == 4:      return TColor.GetColor("#AA767C")
    if index == 5:      return TColor.GetColor("#D6A184")

def getStackColorTauPOG(index):
    if index == 0:      return TColor.GetColor("#18252a")
    if index == 1:      return TColor.GetColor("#de5a6a")
    if index == 2:      return TColor.GetColor("#9999cc")
    if index == 3:      return TColor.GetColor("#4496c8")
    if index == 4:      return TColor.GetColor("#e5b7e5")
    if index == 5:      return TColor.GetColor("#ffcc66")
    if index == 6:      return TColor.GetColor("#87F1FF")
    if index == 7:      return TColor.GetColor("#AAFAC8")
    if index == 8:      return TColor.GetColor("#6B717E")
    if index == 9:      return TColor.GetColor("#360568")
    if index == 10:      return TColor.GetColor("#F7C59F")
    if index == 11:      return TColor.GetColor("#9F4A54")
    if index == 12:      return TColor.GetColor("#51A3A3")

def getStackColorTauPOGbyName(name):
    if 'triboson' in name:           return TColor.GetColor("#87F1FF")
    elif 'TT' in name:            return TColor.GetColor("#18252a")
    elif 'WZ' in name:          return TColor.GetColor("#de5a6a")
    elif 'ZZ' in name:          return TColor.GetColor("#AAFAC8")
    elif 'WW' in name:          return TColor.GetColor("#514B23")
    elif 'ST' in name:          return TColor.GetColor("#9999cc")
    elif 'WJets' in name:       return TColor.GetColor("#4496c8")
    elif 'QCD' in name:         return TColor.GetColor("#e5b7e5")
    elif 'DY' in name:          return TColor.GetColor("#ffcc66")
    elif 'ttX' in name:         return TColor.GetColor("#6B717E") 
    elif 'XG' in name:          return TColor.GetColor("#360568")
    
    elif '600' in name:   return TColor.GetColor("#F7C59F")
    elif '400' in name:   return TColor.GetColor("#A8C256")
    elif '200' in name:   return TColor.GetColor("#9F4A54")
    elif '150' in name:   return TColor.GetColor("#51A3A3")
    elif '120' in name:   return TColor.GetColor("#D1D1D1")
    elif '100' in name:   return TColor.GetColor("#EAD94C")
    elif '80' in name:   return TColor.GetColor("#3B3561")
    elif '60' in name:   return TColor.GetColor("#DD7373")
    elif '40' in name:   return TColor.GetColor("#3454D1")
    elif '20' in name:   return TColor.GetColor("#9368B7")
    elif '10' in name:   return TColor.GetColor("#610F7F")
    elif '5' in name:   return TColor.GetColor("#613DC1")
#    elif 'H' in name:           return "#87F1FF"
    else:                       return ROOT.kGreen

def getHistColor(index):        
    if index == 0:      return TColor.GetColor("#000075")
    if index == 1:      return TColor.GetColor("#800000")
    if index == 2:      return TColor.GetColor("#f58231")
    if index == 3:      return TColor.GetColor("#3cb44d")
    if index == 4:      return TColor.GetColor("#ffe119")
    if index == 5:      return TColor.GetColor("#87F1FF")
    if index == 6:      return TColor.GetColor("#F4F1BB")

def getWPcolor(index):        
    if index == 'medium':      return ROOT.kBlack
    if index == 'None':      return ROOT.kRed
    if index == 'vvvloose':      return ROOT.kBlue
    if index == 'vvloose':      return ROOT.kGreen
    if index == 'loose':      return ROOT.kCyan
    if index == 'vloose':      return ROOT.kYellow
    if index == 'tight':      return ROOT.kMagenta
    if index == 'vtight':      return ROOT.kPink
    if index == 'vvtight':      return ROOT.kOrange
    if index == 'vvvtight':      return ROOT.kAzure

def getHistDidar(index):        
    if index == 5:      return ROOT.kBlack
    if index == 0:      return ROOT.kGreen
    if index == 1:      return ROOT.kBlue
    if index == 2:      return ROOT.kMagenta
    if index == 4:      return ROOT.kCyan
    if index == 3:      return ROOT.kRed
    if index == 6:      return ROOT.kOrange
    if index == 7:      return ROOT.kPink
    if index == 8:      return ROOT.kAzure
    if index == 9:      return ROOT.kYellow
    else:               return ROOT.kBlack
def getHNLColor(name):
    if '200' in name:   return TColor.GetColor("#9F4A54")
    elif '150' in name:   return TColor.GetColor("#51A3A3")
    elif '120' in name:   return TColor.GetColor("#D1D1D1")
    elif '100' in name:   return TColor.GetColor("#EAD94C")
    elif '80' in name:   return TColor.GetColor("#3B3561")
    elif '60' in name:   return TColor.GetColor("#DD7373")
    elif '40' in name:   return TColor.GetColor("#3454D1")
    elif '20' in name:   return TColor.GetColor("#9368B7")
    elif '10' in name:   return TColor.GetColor("#610F7F")
    elif '5' in name:   return TColor.GetColor("#613DC1")
    else:               return TColor.GetColor("#000000")

def getLineColor(index):
    if index == 3:      return TColor.GetColor("#000000")
    if index == 4:      return TColor.GetColor("#e6194B")
    if index == 5:      return TColor.GetColor("#4363d8")
    if index == 0:      return TColor.GetColor("#B9BAA3")
    if index == 1:      return TColor.GetColor("#685762")
    if index == 2:      return TColor.GetColor("#E8C547")

def getBlackColor(index):
    return ROOT.kBlack

def getMarker(index):
    if index == 0:      return 20
    if index == 1:      return 21
    if index == 2:      return 22
    if index == 3:      return 23
    if index == 4:      return 24
    if index == 5:      return 25
    if index == 6:      return 26

def returnSignalLegendName(name):
    split_name = name.split('-M')

