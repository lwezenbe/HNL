#
# Class to get search regions
# The input name will decide what the search regions for the analysis are
#
import ROOT

class SearchRegionManager:

    def __init__(self, name = None):
        self.name = name
        #Exception
        if self.name == 'HighMassWithInvertedPt':
            self.name = 'highMassSR'
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


    def getSearchRegionBinning(self, searchregion = None, final_state = None):
        import numpy as np
 
        if searchregion is not None and isinstance(searchregion, list):
            total = self.getSearchRegionBinning(searchregion[0], final_state = final_state)
            for x in searchregion[1:]:
                total = np.append(total, self.getSearchRegionBinning(x, final_state = final_state))
            return total

        if final_state is not None and self.name in bins_to_merge.keys():
            from HNL.EventSelection.eventCategorization import isLightLeptonFinalState
            #Check if there are bins to be merged
            for final_state_to_merge in bins_to_merge[self.name].keys():
                from HNL.EventSelection.eventCategorization import isPartOfCategory
                if not isPartOfCategory(final_state_to_merge, final_state): continue
                #First check if a specific search region is defined
                if searchregion is not None and all([x in self.getGroupValues(searchregion) for x in bins_to_merge[self.name][final_state_to_merge]]):
                    return np.array([x-0.5 for x in self.getGroupValues(searchregion) if x not in bins_to_merge[self.name][final_state_to_merge][1:]]+[self.getGroupValues(searchregion)[-1]+0.5])
                #Else adapt full range if none specified
                elif searchregion is None:
                    return self.getSearchRegionBinning(searchregion = self.getListOfSearchRegionGroups(), final_state = final_state)
                     
        if searchregion is not None:
            return np.arange(self.getGroupValues(searchregion)[0]-0.5, self.getGroupValues(searchregion)[-1]+1.5, 1.)
        else:
            return np.arange(0.5, self.getNumberOfSearchRegions()+1.5, 1.)


#
# constants and functions
#

LIST_OF_SR_NAMES = ['lowMassSR', 'lowMassSRloose', 'highMassSR']
region_groups = {} 
bins_to_merge = {}

#
# Dictionary for translating to tex
#
searchregion_tex = {
    'A' : 'L1-4',
    'B' : 'L5-8',
    'C' : 'L9-12',
    'D' : 'L13-16',
    'E' : 'Hb',
    'F' : 'Ha'
}

#
# List of search region functions
#
region_groups['lowMassSRloose'] = {
    'A' : [1, 2, 3, 4],
    'B' : [5, 6, 7, 8],
    'C' : [9, 10, 11, 12],
    'D' : [13, 14, 15, 16]
}
bins_to_merge['lowMassSRloose'] = {}
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
bins_to_merge['highMassSR'] = {
    'TauEE' : [2, 3],
    'TauMuMu' : [2, 3] 
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


def collectGroupHist(signal_hist, bkgr_hist, syst_hist, region_name, observed_hist = None, category = None):
    grouped_signal_hist = {}
    grouped_bkgr_hist = {}
    grouped_observed_hist = {}
    grouped_syst_hist = {}

    import HNL.Tools.histogram
    for group in region_groups[region_name].keys():
        srm = SearchRegionManager(region_name)
        bins = srm.getSearchRegionBinning(group, category)        

        grouped_signal_hist[group] = [] 
        grouped_bkgr_hist[group] = []
        if signal_hist is not None:
            for ish, sh in enumerate(signal_hist):
                grouped_signal_hist[group].append(ROOT.TH1D('tmp_signal_'+str(ish)+'_'+group, 'tmp_signal', len(bins)-1, bins))
                for ib, b in enumerate([x-1+region_groups[region_name][group][0] for x in range(1, len(bins))]):
                    if isinstance(sh, HNL.Tools.histogram.Histogram):
                        grouped_signal_hist[group][ish].SetBinContent(ib+1, sh.getHist().GetBinContent(b))
                        grouped_signal_hist[group][ish].SetBinError(ib+1, sh.getHist().GetBinError(b))
                    else:
                        grouped_signal_hist[group][ish].SetBinContent(ib+1, sh.GetBinContent(b))
                        grouped_signal_hist[group][ish].SetBinError(ib+1, sh.GetBinError(b))                        
        
        if bkgr_hist is not None:
            for ish, sh in enumerate(bkgr_hist):
                grouped_bkgr_hist[group].append(ROOT.TH1D('tmp_bkgr_'+str(ish)+'_'+group, 'tmp_bkgr', len(bins)-1, bins))
                #for ib, b in enumerate(region_groups[region_name][group]):
                for ib, b in enumerate([x-1+region_groups[region_name][group][0] for x in range(1, len(bins))]):
                    if isinstance(sh, HNL.Tools.histogram.Histogram):
                        grouped_bkgr_hist[group][ish].SetBinContent(ib+1, sh.getHist().GetBinContent(b))
                        grouped_bkgr_hist[group][ish].SetBinError(ib+1, sh.getHist().GetBinError(b))
                    else:
                        grouped_bkgr_hist[group][ish].SetBinContent(ib+1, sh.GetBinContent(b))
                        grouped_bkgr_hist[group][ish].SetBinError(ib+1, sh.GetBinError(b))                        
        
        if observed_hist is not None and grouped_observed_hist is not None:
            grouped_observed_hist[group] = ROOT.TH1D('tmp_observed_'+group, 'tmp_observed', len(bins)-1, bins)
            #for ib, b in enumerate(region_groups[region_name][group]):
            for ib, b in enumerate([x-1+region_groups[region_name][group][0] for x in range(1, len(bins))]):
                if isinstance(sh, HNL.Tools.histogram.Histogram):
                    grouped_observed_hist[group].SetBinContent(ib+1, observed_hist.getHist().GetBinContent(b))
                    grouped_observed_hist[group].SetBinError(ib+1, observed_hist.getHist().GetBinError(b))
                else:
                    grouped_observed_hist[group].SetBinContent(ib+1, observed_hist.GetBinContent(b))
                    grouped_observed_hist[group].SetBinError(ib+1, observed_hist.GetBinError(b))                        
        else:
            grouped_observed_hist = None

        if syst_hist is not None and grouped_syst_hist is not None:
            grouped_syst_hist[group] = []
            for ish, sh in enumerate(syst_hist):
                grouped_syst_hist[group].append(ROOT.TH1D('tmp_syst_'+str(ish)+'_'+group, 'tmp_syst', len(bins)-1, bins))
                #for ib, b in enumerate(region_groups[region_name][group]):
                for ib, b in enumerate([x-1+region_groups[region_name][group][0] for x in range(1, len(bins))]):
                    if isinstance(sh, HNL.Tools.histogram.Histogram):
                        grouped_syst_hist[group][ish].SetBinContent(ib+1, sh.getHist().GetBinContent(b))
                        grouped_syst_hist[group][ish].SetBinError(ib+1, sh.getHist().GetBinError(b))
                    else:
                        grouped_syst_hist[group][ish].SetBinContent(ib+1, sh.GetBinContent(b))
                        grouped_syst_hist[group][ish].SetBinError(ib+1, sh.GetBinError(b))    
        else:
            grouped_syst_hist = None 
                    
    return grouped_signal_hist, grouped_bkgr_hist, grouped_syst_hist, grouped_observed_hist

def plotGeneralGroups(group_signal_hist, group_bkgr_hist, group_syst_hist, tex_names, out_path, region_name, year, era, extra_text = None, observed_hist = None):
    for group in region_groups[region_name].keys():
        if observed_hist is not None:
            draw_ratio = True
        elif len(group_signal_hist[group]) > 0 and len(group_bkgr_hist[group]) > 0:
            draw_ratio = 'errorsOnly'
        else:
            draw_ratio = None
        if observed_hist is not None: draw_ratio = True
        tmp_signal = [x for x in group_signal_hist[group]]
        tmp_bkgr = [x for x in group_bkgr_hist[group]]
        tmp_syst = [x for x in group_syst_hist[group]] if group_syst_hist is not None else None
        p = Plot(tmp_signal if len(tmp_signal) > 0 else None, tex_names, bkgr_hist = tmp_bkgr if len(tmp_bkgr) > 0 else None, observed_hist = observed_hist[group] if observed_hist is not None else None, syst_hist = tmp_syst, name = group, x_name = 'Search region', y_name = 'Events', y_log=True, 
                extra_text = extra_text, color_palette = 'HNL', color_palette_bkgr = 'HNLfromTau', draw_ratio = draw_ratio, year = year, era = era)
        p.drawHist(output_dir = out_path, min_cutoff = 1., normalize_signal = 'med')
        #p.drawHist(output_dir = out_path, min_cutoff = 1.)

tdrStyle_Left_Margin = 0.16
tdrStyle_Right_Margin = 0.02
plotsize = 1-tdrStyle_Left_Margin-tdrStyle_Right_Margin

def combineGroupHist(signal_hist, bkgr_hist, syst_hist, region_name, groups, observed_hist = None):
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

    if syst_hist is not None:
        grouped_syst_hist = []
        for igroup, group in enumerate(groups):
            for ish, sh in enumerate(syst_hist[group]):
                if igroup == 0: grouped_syst_hist.append(ROOT.TH1D('tmp_syst_'+str(ish), 'tmp_syst', tot_n_bins, 0.5, tot_n_bins+0.5))
                for ib, b in enumerate(region_groups[region_name][group]):
                    if isinstance(sh, HNL.Tools.histogram.Histogram):
                        grouped_syst_hist[ish].SetBinContent(getBinsNb(igroup, ib), sh.getHist().GetBinContent(ib+1))
                        grouped_syst_hist[ish].SetBinError(getBinsNb(igroup, ib), sh.getHist().GetBinError(ib+1))
                    else:
                        grouped_syst_hist[ish].SetBinContent(getBinsNb(igroup, ib), sh.GetBinContent(ib+1))
                        grouped_syst_hist[ish].SetBinError(getBinsNb(igroup, ib), sh.GetBinError(ib+1))
    else:
        grouped_syst_hist = None

    if observed_hist is not None:
        for igroup, group in enumerate(groups):
            if igroup == 0: grouped_observed_hist = ROOT.TH1D('tmp_observed', 'tmp_bkgr', tot_n_bins, 0.5, tot_n_bins+0.5)
            for ib, b in enumerate(region_groups[region_name][group]):
                if isinstance(observed_hist, HNL.Tools.histogram.Histogram):
                    grouped_observed_hist.SetBinContent(getBinsNb(igroup, ib), observed_hist[group].getHist().GetBinContent(ib+1))
                    grouped_observed_hist.SetBinError(getBinsNb(igroup, ib), observed_hist[group].getHist().GetBinError(ib+1))
                else:
                    grouped_observed_hist.SetBinContent(getBinsNb(igroup, ib), observed_hist[group].GetBinContent(ib+1))
                    grouped_observed_hist.SetBinError(getBinsNb(igroup, ib), observed_hist[group].GetBinError(ib+1))
    else:
        grouped_observed_hist = None
    
    return grouped_signal_hist, grouped_bkgr_hist, grouped_syst_hist, grouped_observed_hist

def plotLowMassRegions(signal_hist, bkgr_hist, syst_hist, tex_names, out_path, year, era, extra_text = None, observed_hist = None):
    #Plot per grouping
    plotGeneralGroups(signal_hist, bkgr_hist, tex_names, out_path, 'lowMassSR', year, era, extra_text=extra_text, observed_hist = observed_hist)

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
    p = Plot(signal_hist, tex_names, bkgr_hist = bkgr_hist, syst_hist = syst_hist, name = 'All', x_name = 'M_{2lOS}^{min} [GeV]', y_name = 'Events', extra_text = extra_text, y_log=True, 
            color_palette = 'HNL', color_palette_bkgr = 'HNLfromTau', draw_ratio = draw_ratio, year = year, era = era)
 
    p.drawHist(output_dir = out_path, draw_lines = line_collection, min_cutoff = 0.1, custom_labels = custom_labels, normalize_signal = 'med')
    #p.drawHist(output_dir = out_path, draw_lines = line_collection, min_cutoff = 0.1, custom_labels = custom_labels, normalize_signal = 'bkgr')

def plotHighMassRegions(signal_hist, bkgr_hist, syst_hist, tex_names, out_path, year, era, extra_text = None, observed_hist = None, final_state = None):

    #Plot per grouping

    grouped_signal_hist, grouped_bkgr_hist, grouped_syst_hist, grouped_observed_hist = collectGroupHist(signal_hist, bkgr_hist, syst_hist, 'highMassSR', observed_hist = observed_hist, category = final_state)
    plotGeneralGroups(grouped_signal_hist, grouped_bkgr_hist, grouped_syst_hist, tex_names, out_path, 'highMassSR', year, era, extra_text = extra_text, observed_hist = grouped_observed_hist)
    
#    draw_ratio = 'errorsOnly' if signal_hist is not None and bkgr_hist is not None else None
#    p = Plot(signal_hist, tex_names, bkgr_hist = bkgr_hist, name = 'All', x_name = 'Search region', y_name = 'Events', y_log=True, extra_text = extra_text, 
#            color_palette = 'HNL', color_palette_bkgr = 'HNLfromTau', syst_hist = 0.1, draw_ratio = draw_ratio, year = year, era = era)
#    p.drawHist(output_dir = out_path, min_cutoff = 1., bkgr_draw_option="HistText", normalize_signal = 'med')
                    
def plotLowMassRegionsLoose(signal_hist, bkgr_hist, syst_hist, tex_names, out_path, year, era, extra_text = None, observed_hist = None):

    #Plot per grouping
    grouped_signal_hist, grouped_bkgr_hist, grouped_syst_hist, grouped_observed_hist = collectGroupHist(signal_hist, bkgr_hist, syst_hist, 'lowMassSRloose', observed_hist = observed_hist)
    #plotGeneralGroups(grouped_signal_hist, grouped_bkgr_hist, tex_names, out_path, 'lowMassSRloose', extra_text = extra_text)
    
    if observed_hist is not None:
        draw_ratio = True
    elif len(group_signal_hist[group]) > 0 and len(group_bkgr_hist[group]) > 0:
        draw_ratio = 'errorsOnly'
    else:
        draw_ratio = None
    p = Plot(signal_hist, tex_names, bkgr_hist = bkgr_hist, observed_hist = observed_hist, syst_hist = grouped_syst_hist, name = 'All', x_name = 'Search region', y_name = 'Events', y_log=True, extra_text = extra_text,
            color_palette = 'HNL', color_palette_bkgr = 'HNLfromTau', draw_ratio = draw_ratio, year = year, era = era)
    p.drawHist(output_dir = out_path, min_cutoff = 1., normalize_signal = 'med')
    #p.drawHist(output_dir = out_path, min_cutoff = 1., normalize_signal = 'bkgr')
    
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
    if observed_hist is not None: draw_ratio = True
    tmp_signal_hist, tmp_bkgr_hist, tmp_syst, tmp_observed_hist = combineGroupHist(grouped_signal_hist, grouped_bkgr_hist, grouped_syst_hist, 'lowMassSRloose', ['A', 'B'], observed_hist = grouped_observed_hist)
    p = Plot(tmp_signal_hist, tex_names, bkgr_hist = tmp_bkgr_hist, observed_hist = tmp_observed_hist, syst_hist = tmp_syst, name = 'AB', x_name = 'M_{2lOS}^{min} [GeV]', y_name = 'Events', extra_text = extra_text, y_log=True, 
            color_palette = 'HNL', color_palette_bkgr = 'HNLfromTau', draw_ratio = draw_ratio, year = year, era = era)
 
    p.drawHist(output_dir = out_path, draw_lines = line_collection, min_cutoff = 0.1, custom_labels = custom_labels)
    
    tmp_signal_hist, tmp_bkgr_hist, tmp_syst, tmp_observed_hist = combineGroupHist(grouped_signal_hist, grouped_bkgr_hist, grouped_syst_hist, 'lowMassSRloose', ['C', 'D'], observed_hist = grouped_observed_hist)
    p = Plot(tmp_signal_hist, tex_names, bkgr_hist = tmp_bkgr_hist, observed_hist = tmp_observed_hist, name = 'CD', x_name = 'M_{2lOS}^{min} [GeV]', y_name = 'Events', extra_text = extra_text, y_log=True, 
            color_palette = 'HNL', color_palette_bkgr = 'HNLfromTau', syst_hist = tmp_syst, draw_ratio = draw_ratio, year = year, era = era)
 
    p.drawHist(output_dir = out_path, draw_lines = line_collection, min_cutoff = 0.1, custom_labels = custom_labels)
                   

#def getHEPjson(signal_hist, bkgr_hist, syst_hist, tex_names, out_path, year, era, region, observed_hist = None, combine_bkgr = True):
#    import numpy as np
#    if combine_bkgr:
#        tmp_bkgr = []
#        tmp_syst = []
#        for i, (b,s) in enumerate(zip(bkgr_hist, syst_hist)):
#            if i == 0:
#                tmp_bkgr.append(b.clone())
#                tmp_syst.append(s.clone())
#            else:
#                tmp_bkgr[0].add(b)
#                for syst_bin in xrange(0, tmp_syst[0].getHist().GetNbinsX()+1):
#                    tmp_syst[0].getHist().SetBinError(syst_bin, np.sqrt(tmp_syst[0].getHist().GetBinError(b)** 2 + s.getHist()GetBinError(b) ** 2))
#
#    if region == 'highMassSR':
        
            
        


 
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


