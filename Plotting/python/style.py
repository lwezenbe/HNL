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
    ROOT.gErrorIgnoreLevel = ROOT.kWarning 
    ROOT.TGaxis.SetMaxDigits(3)


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
        return getBlackColor()
    elif palette == 'AN2017':
        return getAN2017Colors(index)
    elif palette == 'tZq':
        return gettZqColors(index)
    elif palette == 'HNLfromTau':
        return getHNLfromTau(index)
    elif palette == 'Large':
        return getLargeArrayColors(index)
    elif palette == 'Syst':
        return getSystColors(index)
    elif palette == 'Limit':
        return getLimitColors(index)
    else:
        return getHistColor(index)

pallete_by_tex = ['StackTauPOGbyName', 'WorkingPoints', 'AN2017', 'HNL', 'tZq', 'HNLfromTau', 'Syst']
def getPaletteIndex(palette, index, tex_name):
    if palette in pallete_by_tex:
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
    else:               return ROOT.kBlack

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
    elif 'Data' in name:          return TColor.GetColor("#77BFA3")
    
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
    if '700' in name:   return TColor.GetColor("#9A4C95")
    if '600' in name:   return TColor.GetColor("#0000bd")
    if '500' in name:   return TColor.GetColor("#262626")
    if '400' in name:   return TColor.GetColor("#5d0016")
    if '300' in name:   return TColor.GetColor("#f20019")
    elif '200' in name:   return TColor.GetColor("#06AED5")
    elif '150' in name:   return TColor.GetColor("#8f00c7")
    elif '120' in name:   return TColor.GetColor("#0086fe")
    elif '100' in name:   return TColor.GetColor("#D741A7")
    elif '80' in name:   return TColor.GetColor("#00fefe")
    elif '60' in name:   return TColor.GetColor("#fe68fe")
    elif '40' in name:   return TColor.GetColor("#fe8420")
    elif '20' in name:   return TColor.GetColor("#70fe00")
    elif '10' in name:   return TColor.GetColor("#fefe00")
    elif '5' in name:   return TColor.GetColor("#fed38b")
    else:               return TColor.GetColor("#a0d681")


def getHNLfromTau(name):
    if 'triboson' in name or 'Triboson' in name:           return TColor.GetColor("#87F1FF")
    #elif 'Charge' in name:          return TColor.GetColor("#D7BCE8")
    #elif 'Charge' in name:          return TColor.GetColor("#BAB700")
    elif 'Charge' in name:          return TColor.GetColor("#F6F5AE")
    elif 'WZ' in name:          return TColor.GetColor("#de5a6a")
    elif 'ZZ-H' in name or 'ZZ' in name:          return TColor.GetColor("#AAFAC8")
    elif 'non-prompt' in name or 'Nonprompt' in name:       return TColor.GetColor("#4496c8")
    elif 'QCD' in name:         return TColor.GetColor("#e5b7e5")
    elif 'XG' in name or 'V#gamma' in name:          return TColor.GetColor("#ffcc66")
    elif 'TT-T+X' in name or 't(#bar{t})X' in name:         return TColor.GetColor("#6B717E") 
    elif 'Other' in name:          return TColor.GetColor("#77BFA3")
    #elif 'Predicted' in name:           return TColor.GetColor("#f4f1bb")
    elif 'Predicted' in name:           return TColor.GetColor("#E4BE9E")
    #elif 'Predicted' in name:           return TColor.GetColor("#D5D8A7")
 
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


def getAN2017Colors(name):
    if name == 'WZ': return TColor.GetColor("#ff6666")
    elif name == 'triboson': return TColor.GetColor("#6666ff")
    elif name == 'TT-T+X': return TColor.GetColor("#ff66ff")
    elif name == 'ZZ-H': return TColor.GetColor("#ff9966")
    elif name == 'XG': return TColor.GetColor("#00cc00")
    elif name == 'non-prompt': return TColor.GetColor("#3399ff")
    elif '-m100' in name: return TColor.GetColor("#ff0000")
    elif '-m130' in name: return TColor.GetColor("#0000ff")
    elif '-m150' in name: return TColor.GetColor("#00ff00")
    elif '-m200' in name: return TColor.GetColor("#ffff00")
    elif '-m400' in name: return TColor.GetColor("#00ffff")
    elif '-m600' in name: return TColor.GetColor("#ff00ff")
    elif '-m20' in name: return TColor.GetColor("#00ff00")
    elif '-m40' in name: return TColor.GetColor("#ffff00")
    elif '-m60' in name: return TColor.GetColor("#ff00ff")
    else:               return TColor.GetColor("#012A36")

def getSystColors(name):
    if name == 'nominal': return TColor.GetColor("#3D405B")
    elif name == 'up': return TColor.GetColor("#E07A5F")
    elif name == 'down': return TColor.GetColor("#81B29A")
    else: return TColor.GetColor("#F2CC8F")

def gettZqColors(name):
    if name == 'WZ': return TColor.GetColor("#81efd7")
    elif name == 'triboson': return TColor.GetColor("#c6ff00")
    elif name == 'TT-T+X': return TColor.GetColor("#d6a2e8")
    elif name == 'ZZ-H': return TColor.GetColor("#2fbc6c")
    elif name == 'XG': return TColor.GetColor("#9c88ff")
    elif name == 'non-prompt': return TColor.GetColor("#ffe380")
    elif name == 'QCD': return TColor.GetColor("#DBB68F")
    elif name == 'Other': return TColor.GetColor("#336fce")
    elif '-m100' in name: return TColor.GetColor("#ff0000")
    elif '-m130' in name: return TColor.GetColor("#0000ff")
    elif '-m150' in name: return TColor.GetColor("#00ff00")
    elif '-m200' in name: return TColor.GetColor("#ffff00")
    elif '-m400' in name: return TColor.GetColor("#00ffff")
    elif '-m600' in name: return TColor.GetColor("#ff00ff")
    elif '-m20' in name: return TColor.GetColor("#00ff00")
    elif '-m40' in name: return TColor.GetColor("#ffff00")
    elif '-m60' in name: return TColor.GetColor("#ff00ff")
    else:               return TColor.GetColor("#012A36")

def getLargeArrayColors(index):
    if index == 0:           return TColor.GetColor("#87F1FF")
    if index == 1:            return TColor.GetColor("#18252a")
    if index == 2:          return TColor.GetColor("#de5a6a")
    if index == 3:          return TColor.GetColor("#AAFAC8")
    if index == 4:          return TColor.GetColor("#514B23")
    if index == 5:          return TColor.GetColor("#9999cc")
    if index == 6:       return TColor.GetColor("#4496c8")
    if index == 7:         return TColor.GetColor("#e5b7e5")
    if index == 8:          return TColor.GetColor("#ffcc66")
    if index == 9:         return TColor.GetColor("#6B717E") 
    if index == 10:          return TColor.GetColor("#360568")
    if index == 11:          return TColor.GetColor("#77BFA3")
    
    if index == 12:   return TColor.GetColor("#F7C59F")
    if index == 13:   return TColor.GetColor("#A8C256")
    if index == 14:   return TColor.GetColor("#9F4A54")
    if index == 15:   return TColor.GetColor("#51A3A3")
    if index == 16:   return TColor.GetColor("#D1D1D1")
    if index == 17:   return TColor.GetColor("#EAD94C")
    if index == 18:   return TColor.GetColor("#3B3561")
    if index == 19:   return TColor.GetColor("#DD7373")
    if index == 20:   return TColor.GetColor("#3454D1")
    if index == 21:   return TColor.GetColor("#9368B7")
    if index == 22:   return TColor.GetColor("#610F7F")
    if index == 23:   return TColor.GetColor("#613DC1")
#    elif 'H' in name:           return "#87F1FF"
    else:                       return ROOT.kGreen

def getLineColor(index):
    if index == 3:      return TColor.GetColor("#000000")
    if index == 4:      return TColor.GetColor("#e6194B")
    if index == 5:      return TColor.GetColor("#4363d8")
    if index == 0:      return TColor.GetColor("#B9BAA3")
    if index == 1:      return TColor.GetColor("#685762")
    if index == 2:      return TColor.GetColor("#E8C547")

def getLimitColors(index):
    if index == 1:      return TColor.GetColor("#ED474A")
    if index == 0:      return TColor.GetColor("#FF00FF")
    if index == 2:      return TColor.GetColor("#72DDF7")
    if index == 3:      return TColor.GetColor("#0000ff")
    if index == 4:      return TColor.GetColor("#685762")
    if index == 5:      return TColor.GetColor("#E8C547")

def getBlackColor():
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
    #TODO : Finish this function

