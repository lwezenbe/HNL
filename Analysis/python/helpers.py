def removeEmptyBins(in_hist):

    n_bins = in_hist[0].getHist().GetNbinsX()
    x_axis = in_hist[0].getHist().GetXaxis()
    new_range = [x_axis.GetBinLowEdge(1)]

    for b in xrange(1, n_bins + 1):
        new_range.append(x_axis.GetBinUpEdge(b))

    print [in_hist[0].getHist().GetBinContent(b) for b in xrange(1, n_bins + 1)]
    #remove empty bins in the front
    for b in xrange(1, n_bins + 1):
        is_zero = all([h.getHist().GetBinContent(b) < 0.2 for h in in_hist])
        if is_zero:
            new_range.pop(0)
        else:
            break

    #remove empty bins in the back
    for b in reversed(xrange(1, n_bins + 1)):
        print [h.getHist().GetBinContent(b) for h in in_hist]
        print new_range
        if len(new_range) == 0: break
        is_zero = all([h.getHist().GetBinContent(b) < 0.2 for h in in_hist])
        if is_zero:
            new_range.pop(-1)
        else:
            break

    return new_range
    
