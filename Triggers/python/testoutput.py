base = '/storage_mnt/storage/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Triggers/data/calcTriggerEfficiency/UL2016post/allTriggers/default-HNL-NoRef/WZ/tmp_WZ'

from glob import glob
all_files = glob(base+'/*')

from HNL.Tools.helpers import getObjFromFile
tot_val = 0
tot_val_denom = 0
for f in all_files:
    # hist1 = getObjFromFile(f, '6/l2l3-2D/15.0to30.0/l2l3-2D-6-15.0to30.0_num') 
    # hist2 = getObjFromFile(f, '6/l2l3-2D/15.0to30.0/l2l3-2D-6-15.0to30.0_denom') 
    # for bx in range(1, hist1.GetNbinsX()+1):
    #     for by in range(1, hist1.GetNbinsY()+1):
    #         hc1 = hist1.GetBinContent(bx, by)
    #         hc2 = hist2.GetBinContent(bx, by)
            # if hc1 > hc2: 
            #     print 'Problem in', f
                # exit(0)

    # hc1 = hist1.GetBinContent(3, 3)
    # hc2 = hist2.GetBinContent(3, 3)
    # tot_val += hc1
    # tot_val_denom += hc2

    # try:
    #     print hc1, hc2, tot_val, tot_val_denom, tot_val/tot_val_denom
    # except:
    #     print hc1, hc2, tot_val, tot_val_denom

    # for b in range(1, hist1.GetNcells()+1):
    #     hc1 = hist1.GetBinContent(b)
    #     hc2 = hist2.GetBinContent(b)
    #     if hc1 > hc2: 
    #         print 'Problem in', f

    hist = getObjFromFile(f, '9/l2l3-2D/30.0to55.0/l2l3-2D-9-30.0to55.0_num') 
    b = hist.FindBin(12., 17.)
    if hist.GetBinContent(b) != 0.: print f
