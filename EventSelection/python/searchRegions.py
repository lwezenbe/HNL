#
# Class to get search regions
# The input name will decide what the search regions for the analysis are
#
import ROOT

class SearchRegionManager:

    def __init__(self, name = None):
        self.name = name
        if self.name is not None and self.name not in LIST_OF_SR_NAMES:
            print 'You specified a SR name but it does not correspond to any I know. Will continue with a single search region.'

    def getNumberOfSearchRegions(self):
        if self.name == 'lowMassSR':
            return 8
        if self.name == 'lowMassSRloose':
            return 16
        elif self.name == 'highMassSR':
            return 25
        else:
            return 1

    def getListOfSearchRegionGroups(self):
        if self.name is None or self.name not in LIST_OF_SR_NAMES:
            return []
        else:
            return region_groups[self.name].keys()

    def getGroupValues(self, k):
        if self.name is None or self.name not in LIST_OF_SR_NAMES:
            return []
        else:
            return region_groups[self.name][k]

    def getSearchRegionGroup(self, sr):
        if self.name is None or self.name not in LIST_OF_SR_NAMES:
            return None
        else:
            for group in region_groups[self.name].keys():
                if sr in region_groups[self.name][group]: return group
        return None

    #
    # Function to retrieve the search region label
    # If self.name is recognized, it picks one of the search regions defined
    # If not, no search regions are made and a single search region label is defined to which all events will be assigned
    #
    def getSearchRegion(self, chain):
        if self.name == 'lowMassSR':
            return getLowMassRegion(chain)
        elif self.name == 'lowMassSRloose':
            return getLowMassLooseRegion(chain)
        elif self.name == 'highMassSR':
            return getHighMassRegion(chain)
        else:
            return 1

#
# constants and functions
#

LIST_OF_SR_NAMES = ['lowMassSR', 'lowMassSRloose', 'highMassSR']
region_groups = {} 

#
# List of search region functions
#
region_groups['lowMassSRloose'] = {
    'A' : [1, 2, 3, 4],
    'B' : [5, 6, 7, 8],
    'C' : [9, 10, 11, 12],
    'D' : [13, 14, 15, 16]
}
def getLowMassLooseRegion(chain):
    if not chain.hasOSSF:
        if chain.l_pt[0] < 30:
            if chain.minMos < 10:
                return 1
            elif chain.minMos < 20:
                return 2
            elif chain.minMos < 30:
                return 3
            else:
                return 4
        elif chain.l_pt[0] < 55:
            if chain.minMos < 10:
                return 5
            elif chain.minMos < 20:
                return 6
            elif chain.minMos < 30:
                return 7
            else:
                return 8
    else:
        if chain.l_pt[0] < 30:
            if chain.minMos < 10:
                return 9
            elif chain.minMos < 20:
                return 10
            elif chain.minMos < 30:
                return 11
            else:
                return 12
        elif chain.l_pt[0] < 55:
            if chain.minMos < 10:
                return 13
            elif chain.minMos < 20:
                return 14
            elif chain.minMos < 30:
                return 15
            else:
                return 16

region_groups['lowMassSR'] = {
    'A' : [1, 2, 3, 4],
    'B' : [5, 6, 7, 8]
}
def getLowMassRegion(chain):
    if chain.l_pt[0] < 30:
        if chain.minMos < 10:
            return 1
        elif chain.minMos < 20:
            return 2
        elif chain.minMos < 30:
            return 3
        else:
            return 4
    elif chain.l_pt[0] < 55:
        if chain.minMos < 10:
            return 5
        elif chain.minMos < 20:
            return 6
        elif chain.minMos < 30:
            return 7
        else:
            return 8

region_groups['highMassSR'] = {
    'E' : range(1, 17),
    'F' : range(17, 26)
}
def getHighMassRegion(chain):
    if chain.hasOSSF:
        if chain.M3l < 100:
            if chain.mtOther < 100:
                return 1
            elif chain.mtOther < 200:
                return 2
            else:
                return 3
        else:
            if chain.minMos < 100:
                if chain.mtOther < 100:
                    return 4
                elif chain.mtOther < 200:
                    return 5
                elif chain.mtOther < 300:
                    return 6
                elif chain.mtOther < 400:
                    return 7
                else:
                    return 8
            if chain.minMos < 200:
                if chain.mtOther < 100:
                    return 9
                elif chain.mtOther < 200:
                    return 10
                elif chain.mtOther < 300:
                    return 11
                else:
                    return 12
            else:
                if chain.mtOther < 100:
                    return 13
                elif chain.mtOther < 200:
                    return 14
                elif chain.mtOther < 300:
                    return 15
                else:
                    return 16
    
    else:
        if chain.M3l < 100:
            if chain.mtOther < 100:
                return 17
            else:
                return 18
        else:
            if chain.minMos < 100:
                if chain.mtOther < 100:
                    return 19
                if chain.mtOther < 150:
                    return 20
                if chain.mtOther < 250:
                    return 21
                else:
                    return 22
            if chain.minMos < 200:
                if chain.mtOther < 100:
                    return 23
                else:
                    return 24
            else:
                return 25



# Plotting functions specific to different search region definitions
# Input should always be a list of signal and background histograms where the x-bins are the different SR
from HNL.Plotting.plot import Plot
from HNL.Plotting.plottingTools import extraTextFormat, drawLineFormat

#
# plotGeneralGroups is a function that just makes bare plots without lines or extra text, it is meant to be used with tables when you're in a hurry
#
def collectGroupHist(signal_hist, bkgr_hist, region_name):
    grouped_signal_hist = {}
    grouped_bkgr_hist = {}

    import HNL.Tools.histogram
    for group in region_groups[region_name].keys():
        grouped_signal_hist[group] = [] 
        grouped_bkgr_hist[group] = []
        if signal_hist is not None:
            for ish, sh in enumerate(signal_hist):
                grouped_signal_hist[group].append(ROOT.TH1D('tmp_signal_'+str(ish)+'_'+group, 'tmp_signal', len(region_groups[region_name][group]), 0.5, len(region_groups[region_name][group])+0.5))
                for ib, b in enumerate(region_groups[region_name][group]):
                    if isinstance(sh, HNL.Tools.histogram.Histogram):
                        grouped_signal_hist[group][ish].SetBinContent(ib+1, sh.getHist().GetBinContent(b))
                        grouped_signal_hist[group][ish].SetBinError(ib+1, sh.getHist().GetBinError(b))
                    else:
                        grouped_signal_hist[group][ish].SetBinContent(ib+1, sh.GetBinContent(b))
                        grouped_signal_hist[group][ish].SetBinError(ib+1, sh.GetBinError(b))                        
        
        if bkgr_hist is not None:
            for ish, sh in enumerate(bkgr_hist):
                grouped_bkgr_hist[group].append(ROOT.TH1D('tmp_bkgr_'+str(ish)+'_'+group, 'tmp_bkgr', len(region_groups[region_name][group]), 0.5, len(region_groups[region_name][group])+0.5))
                for ib, b in enumerate(region_groups[region_name][group]):
                    if isinstance(sh, HNL.Tools.histogram.Histogram):
                        grouped_bkgr_hist[group][ish].SetBinContent(ib+1, sh.getHist().GetBinContent(b))
                        grouped_bkgr_hist[group][ish].SetBinError(ib+1, sh.getHist().GetBinError(b))
                    else:
                        grouped_bkgr_hist[group][ish].SetBinContent(ib+1, sh.GetBinContent(b))
                        grouped_bkgr_hist[group][ish].SetBinError(ib+1, sh.GetBinError(b))                        
    return grouped_signal_hist, grouped_bkgr_hist 

def plotGeneralGroups(group_signal_hist, group_bkgr_hist, tex_names, out_path, region_name, year, era, extra_text = None):
    for group in region_groups[region_name].keys():
        draw_ratio = 'errorsOnly' if len(group_signal_hist[group]) > 0 and len(group_bkgr_hist[group]) > 0 else None
        tmp_signal = [x for x in group_signal_hist[group]]
        tmp_bkgr = [x for x in group_bkgr_hist[group]]
        p = Plot(tmp_signal if len(tmp_signal) > 0 else None, tex_names, bkgr_hist = tmp_bkgr if len(tmp_bkgr) > 0 else None, name = group, x_name = 'Search region', y_name = 'Events', y_log=True, 
                extra_text = extra_text, color_palette = 'HNL', color_palette_bkgr = 'HNLfromTau', syst_hist = 0.1, draw_ratio = draw_ratio, year = year, era = era)
        p.drawHist(output_dir = out_path, min_cutoff = 1., normalize_signal = 'med')
        #p.drawHist(output_dir = out_path, min_cutoff = 1.)

tdrStyle_Left_Margin = 0.16
tdrStyle_Right_Margin = 0.02
plotsize = 1-tdrStyle_Left_Margin-tdrStyle_Right_Margin

def combineGroupHist(signal_hist, bkgr_hist, region_name, groups):
    tot_n_bins = 0
    for group in groups:
        tot_n_bins += len(region_groups[region_name][group])

    def getBinsNb(group_index, ind_index):
        base_index = 0
        for igroup, group in enumerate(groups):
            if igroup >= group_index: continue
            base_index += len(region_groups[region_name][group])
        return int(base_index + ind_index + 1)

    import HNL.Tools.histogram
    if signal_hist is not None:
        grouped_signal_hist = []
        for igroup, group in enumerate(groups):
            for ish, sh in enumerate(signal_hist[group]):
                if igroup == 0: grouped_signal_hist.append(ROOT.TH1D('tmp_signal_'+str(ish), 'tmp_signal', tot_n_bins, 0.5, tot_n_bins+0.5))
                for ib, b in enumerate(region_groups[region_name][group]):
                    if isinstance(sh, HNL.Tools.histogram.Histogram):
                        grouped_signal_hist[ish].SetBinContent(getBinsNb(igroup, ib), sh.getHist().GetBinContent(ib+1))
                        grouped_signal_hist[ish].SetBinError(getBinsNb(igroup, ib), sh.getHist().GetBinError(ib+1))
                    else:
                        grouped_signal_hist[ish].SetBinContent(getBinsNb(igroup, ib), sh.GetBinContent(ib+1))
                        grouped_signal_hist[ish].SetBinError(getBinsNb(igroup, ib), sh.GetBinError(ib+1))

    if bkgr_hist is not None:
        grouped_bkgr_hist = []
        for igroup, group in enumerate(groups):
            for ish, sh in enumerate(bkgr_hist[group]):
                if igroup == 0: grouped_bkgr_hist.append(ROOT.TH1D('tmp_bkgr_'+str(ish), 'tmp_bkgr', tot_n_bins, 0.5, tot_n_bins+0.5))
                for ib, b in enumerate(region_groups[region_name][group]):
                    if isinstance(sh, HNL.Tools.histogram.Histogram):
                        grouped_bkgr_hist[ish].SetBinContent(getBinsNb(igroup, ib), sh.getHist().GetBinContent(ib+1))
                        grouped_bkgr_hist[ish].SetBinError(getBinsNb(igroup, ib), sh.getHist().GetBinError(ib+1))
                    else:
                        grouped_bkgr_hist[ish].SetBinContent(getBinsNb(igroup, ib), sh.GetBinContent(ib+1))
                        grouped_bkgr_hist[ish].SetBinError(getBinsNb(igroup, ib), sh.GetBinError(ib+1))

    return grouped_signal_hist, grouped_bkgr_hist

def plotLowMassRegions(signal_hist, bkgr_hist, tex_names, out_path, year, era, extra_text = None):
    #Plot per grouping
    plotGeneralGroups(signal_hist, bkgr_hist, tex_names, out_path, 'lowMassSR', year, era, extra_text=extra_text)

    #
    # All groups in 1 plot
    # Need a line to distinguish leading pt regions (so at 4.5)
    #
    line_collection = [drawLineFormat(x0 = 4.5, color = ROOT.kRed)]
    #
    # Accompanying extra text
    #
    if extra_text is None: extra_text = []
    extra_text.append(extraTextFormat('p_{T}(leading) < 30 GeV', tdrStyle_Left_Margin+(plotsize/4.) , 0.68, None, 22))
    extra_text.append(extraTextFormat('30 GeV < p_{T}(leading) < 55 GeV', tdrStyle_Left_Margin+(plotsize*3/4.) , 0.68, None, 22))
    
    # Custom labels
    custom_labels = ['0-10', '10-20', '20-30', '> 30']*2

    draw_ratio = 'errorsOnly' if signal_hist is not None and bkgr_hist is not None else None
    p = Plot(signal_hist, tex_names, bkgr_hist = bkgr_hist, name = 'All', x_name = 'M_{2lOS}^{min} [GeV]', y_name = 'Events', extra_text = extra_text, y_log=True, 
            color_palette = 'HNL', color_palette_bkgr = 'HNLfromTau', syst_hist = 0.1, draw_ratio = draw_ratio, year = year, era = era)
 
    p.drawHist(output_dir = out_path, draw_lines = line_collection, min_cutoff = 0.1, custom_labels = custom_labels, normalize_signal = 'med')

def plotHighMassRegions(signal_hist, bkgr_hist, tex_names, out_path, year, era, extra_text = None):

    #Plot per grouping

    grouped_signal_hist, grouped_bkgr_hist = collectGroupHist(signal_hist, bkgr_hist, 'highMassSR')
    plotGeneralGroups(grouped_signal_hist, grouped_bkgr_hist, tex_names, out_path, 'highMassSR', year, era, extra_text = extra_text)
    
#    draw_ratio = 'errorsOnly' if signal_hist is not None and bkgr_hist is not None else None
#    p = Plot(signal_hist, tex_names, bkgr_hist = bkgr_hist, name = 'All', x_name = 'Search region', y_name = 'Events', y_log=True, extra_text = extra_text, 
#            color_palette = 'HNL', color_palette_bkgr = 'HNLfromTau', syst_hist = 0.1, draw_ratio = draw_ratio, year = year, era = era)
#    p.drawHist(output_dir = out_path, min_cutoff = 1., bkgr_draw_option="HistText", normalize_signal = 'med')
                    
def plotLowMassRegionsLoose(signal_hist, bkgr_hist, tex_names, out_path, year, era, extra_text = None):

    #Plot per grouping
    grouped_signal_hist, grouped_bkgr_hist = collectGroupHist(signal_hist, bkgr_hist, 'lowMassSRloose')
    #plotGeneralGroups(grouped_signal_hist, grouped_bkgr_hist, tex_names, out_path, 'lowMassSRloose', extra_text = extra_text)
    
    draw_ratio = 'errorsOnly' if signal_hist is not None and bkgr_hist is not None else None
    p = Plot(signal_hist, tex_names, bkgr_hist = bkgr_hist, name = 'All', x_name = 'Search region', y_name = 'Events', y_log=True, extra_text = extra_text,
            color_palette = 'HNL', color_palette_bkgr = 'HNLfromTau', syst_hist = 0.1, draw_ratio = draw_ratio, year = year, era = era)
    p.drawHist(output_dir = out_path, min_cutoff = 1., normalize_signal = 'med')
    
    #
    # A and B in 1 plot
    # Need a line to distinguish leading pt regions (so at 4.5)
    #
    line_collection = [drawLineFormat(x0 = 4.5, color = ROOT.kRed)]
    #
    # Accompanying extra text
    #
    if extra_text is None: extra_text = []
    extra_text.append(extraTextFormat('p_{T}(leading) < 30 GeV', tdrStyle_Left_Margin+(plotsize/4.) , None, None, 22))
#    extra_text.append(extraTextFormat('(SR A)'))
    extra_text.append(extraTextFormat('30 GeV < p_{T}(leading) < 55 GeV', tdrStyle_Left_Margin+(plotsize*3/4.) , 'last', None, 22))
#    extra_text.append(extraTextFormat('(SR B)'))
    
    # Custom labels
    custom_labels = ['0-10', '10-20', '20-30', '> 30']*2

    draw_ratio = 'errorsOnly' if signal_hist is not None and bkgr_hist is not None else None
    tmp_signal_hist, tmp_bkgr_hist = combineGroupHist(grouped_signal_hist, grouped_bkgr_hist, 'lowMassSRloose', ['A', 'B'])
    p = Plot(tmp_signal_hist, tex_names, bkgr_hist = tmp_bkgr_hist, name = 'AB', x_name = 'M_{2lOS}^{min} [GeV]', y_name = 'Events', extra_text = extra_text, y_log=True, 
            color_palette = 'HNL', color_palette_bkgr = 'HNLfromTau', syst_hist = 0.1, draw_ratio = draw_ratio, year = year, era = era)
 
    p.drawHist(output_dir = out_path, draw_lines = line_collection, min_cutoff = 0.1, custom_labels = custom_labels)
    
    tmp_signal_hist, tmp_bkgr_hist = combineGroupHist(grouped_signal_hist, grouped_bkgr_hist, 'lowMassSRloose', ['C', 'D'])
    p = Plot(tmp_signal_hist, tex_names, bkgr_hist = tmp_bkgr_hist, name = 'CD', x_name = 'M_{2lOS}^{min} [GeV]', y_name = 'Events', extra_text = extra_text, y_log=True, 
            color_palette = 'HNL', color_palette_bkgr = 'HNLfromTau', syst_hist = 0.1, draw_ratio = draw_ratio, year = year, era = era)
 
    p.drawHist(output_dir = out_path, draw_lines = line_collection, min_cutoff = 0.1, custom_labels = custom_labels)
                   

 
class RegionCollection:

    def __init__(self, list_of_names):
        self.list_of_names = list_of_names
        self.list_of_regions = {}
        for name in self.list_of_names:
            self.list_of_regions[name] = SearchRegionManager(name)

    def getRegion(self, name):
        return self.list_of_regions[name]

    def getRegionNames(self):
        return self.list_of_names


