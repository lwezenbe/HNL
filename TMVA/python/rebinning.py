#By default set to range -1. to 1.

def getCustomBins(tree, vname, binning_func, condition = None, weight = None):
    from np import arange
    probe_hist = tree.getHistFromTree(vname, 'probe_hist', arange(-1.0, 1.001, 0.001))
    if binning_func == 'ewkino':
        return getEwkinoBinning(probe_hist)

def getEwkinoBinning(in_hist, final_bin_target = 2):
    n_bins = in_hist.getHist().GetNbinsX()
    x_axis = in_hist.getHist().GetXaxis()
    new_edges_inverted = [x_axis.GetBinUpEdge(n_bins)]
    current_target = float(final_bin_target)
    current_total = 0.
    last_total = 0.
    for b in reversed(range(1, n_bins+1)):
        current_total += in_hist.getHist().GetBinContent(b)
        #print b, current_total, current_target
        if current_total >= current_target or b == 1:
            #reached goal for this bin
            if b == 1 and last_total > current_total:
                new_edges_inverted.pop(-1)
            
            new_edges_inverted.append(x_axis.GetBinLowEdge(b))
            last_total = current_total
            current_total = 0
            current_target *= 2.
            #print x_axis.GetBinLowEdge(b)
    return [x for x in reversed(new_edges_inverted)]
        
