BASE_FOLDER = "/user/lwezenbe/Testing/"

import glob
import os
from ROOT import TFile
from HNL.Tools.helpers import rootFileContent, getObjFromFile, makeDirIfNeeded
from HNL.Tools.histogram import Histogram
# import uproot

def compareHist(path, name, withinerrors=False):
    hist_prev = Histogram(getObjFromFile(path, name))
    try:
        hist_latest_base_object  = getObjFromFile(path.replace("Previous", "Latest"), name)
    except:
        return "Error while trying to access file with path {}".format(path.replace("Previous", "Latest"))
    if hist_latest_base_object is None:
        return "Histogram with name '{0}' in file '{1}' is not present in Latest test".format(name, path)
    hist_latest = Histogram(hist_latest_base_object)

    if hist_prev.isTH2 and not hist_latest.isTH2:
        return "Histograms are different type"

    if hist_prev.isTH2:
        x_bins = hist_prev.getHist().GetNbinsX()
        y_bins = hist_prev.getHist().GetNbinsY()
        if x_bins != hist_latest.getHist().GetNbinsX():
            return "Different number of bins"
        if y_bins != hist_latest.getHist().GetNbinsY():
            return "Different number of bins"

        for xb in xrange(1, x_bins+1):
            for yb in xrange(1, y_bins+1):
                if hist_prev.getHist().GetBinContent(xb, yb) != hist_latest.getHist().GetBinContent(xb, yb):
                    return "Different content values in bin ({0}, {1})".format(xb, yb)
                if hist_prev.getHist().GetBinError(xb, yb) != hist_latest.getHist().GetBinError(xb, yb):
                    return "Different error values in bin ({0}, {1})".format(xb, yb)

    else:
        x_bins = hist_prev.getHist().GetNbinsX()
        if x_bins != hist_latest.getHist().GetNbinsX():
            return "Different number of bins"

        for xb in xrange(1, x_bins+1):
            if not withinerrors:
                if hist_prev.getHist().GetBinContent(xb) != hist_latest.getHist().GetBinContent(xb):
                    we = compareHist(path, name, withinerrors=True)
                    if we is None:
                        return "Different content values in bin {0} \t \t \t WITHIN ERROR FOR ALL BINS".format(xb)
                    else:
                        return "Different content values in bin {0}".format(xb)
                if hist_prev.getHist().GetBinError(xb) != hist_latest.getHist().GetBinError(xb):
                    return "Different error values in bin {0}".format(xb)
            elif hist_prev.getHist().GetBinError(xb) > 0:
                if abs( hist_prev.getHist().GetBinContent(xb)-hist_latest.getHist().GetBinContent(xb))/hist_prev.getHist().GetBinError(xb) > 1:
                    return  "Out of error bounds"

    return None

# def compareHistUproot(path, name, withinerrors=False):
#     test_hist_prev = Histogram(getObjFromFile(path, name))

#     if test_hist_prev.isTH2:
#         return compareHist(path, name)

#     f_prev = uproot.open(path)
#     try:
#         f_latest = uproot.open(path.replace("Previous", "Latest"))
#     except:
#         return "Error while trying to access file with path {}".format(path.replace("Previous", "Latest"))


#     hist_prev = f_prev[name]
#     try:
#         hist_latest = f_latest[name]
#     except:
#         return "Histogram with name '{0}' in file '{1}' is not present in Latest test".format(name, path)

#     # latest_val = hist_latest.values()
#     latest_val = hist_latest.values
#     previous_val = hist_prev.values

#     if len(latest_val) != len(previous_val):
#         return "Different number of bins"

#     latest_err = hist_latest.errors()
#     previous_err = hist_prev.errors()

#     for pv, lv, pe, le in zip(previous_val, latest_val, previous_err, latest_err):
#         if not withinerrors:
#             if pv != lv :
#                 we = compareHistUproot(path, name, withinerrors=True)
#                 if we is None:
#                     return "Different content values in bin {0} \t \t \t WITHIN ERROR FOR ALL BINS".format(xb)
#                 else:
#                     return "Different content values in bin {0}".format(xb)
#             if pe != le :
#                 return "Different error values in bin {0}".format(xb)
#         else:
#            if abs(pv-lv)/pe > 0.5:
#                return  "Out of error bounds"
#     return None


def compareFiles(f, withinerrors=False):
    in_file = TFile(f, "read")
    list_of_hist_names = []
    for c in rootFileContent(in_file, basepath='', getNested=True):
        list_of_hist_names.append(c[0])
    in_file.Close()

    out_file_name = f.replace('Previous', 'LOG').split('.')[0]+'.txt'
    makeDirIfNeeded(out_file_name)
    out_file = open(out_file_name, 'w')
    everything_clear = True
    for hn in list_of_hist_names:
        test_result = compareHist(f, hn)
        if test_result is not None:
            if withinerrors and 'WITHIN ERROR' in test_result:
                continue
            everything_clear = False
            out_file.write(hn+': '+test_result+'\n')

    if everything_clear:
        out_file.write("EVERYTHING CLEAR")
        out_file.close()
    else:
        out_file.close()
        return False
    
    return True

def checkSubdirOutput(subdir, withinerrors=False):
    list_of_files_to_test = []
    for root, dirs, files in os.walk(BASE_FOLDER+'Previous/'+subdir, topdown=False):
        if len(files) > 0: 
            for f in files:
                list_of_files_to_test.append(root+'/'+f)
    faulty_files = []
    for ft in list_of_files_to_test:
        if not compareFiles(ft, withinerrors): faulty_files.append(ft)

    return faulty_files


def checkAllOutput(withinerrors=False):
    subdir_list = glob.glob(BASE_FOLDER+'Previous/*')
    subdir_list = [s.split('/')[-1] for s in subdir_list]

    faulty_sd = []
    for sd in subdir_list:
        # if sd != 'closureTest': continue
        print "Checking", sd
        makeDirIfNeeded(BASE_FOLDER+'LOG/'+sd+'/x')
        faulty_files = checkSubdirOutput(sd, withinerrors)
        out_file = open(BASE_FOLDER+'LOG/'+sd+'/FULLREPORT.txt', 'w')
        if len(faulty_files) == 0:
            out_file.write("EVERYTHING CLEAR")
        else:
            faulty_sd.append(sd)
            out_file.write("Problems in the following files: \n")
            for f in faulty_files:
                out_file.write(f+' \n')
        out_file.close()

    tot_file = open(BASE_FOLDER+'totalreport.txt', 'w')
    if len(faulty_sd) == 0:
        tot_file.write("EVERYTHING CLEAR")
    else:
        tot_file.write("Problems in the following scripts: \n")
        for fsd in faulty_sd:
            tot_file.write(fsd+' \n')
    tot_file.close()

def copyFiles():
    os.system('rm -r '+BASE_FOLDER+'Previous/*')

    subdir_list = glob.glob(BASE_FOLDER+'Latest/*')
    subdir_list = [s.split('/')[-1] for s in subdir_list]

    for sd in subdir_list:
        for root, dirs, files in os.walk(BASE_FOLDER+'Latest/'+sd, topdown=False):
            if len(files) > 0: 
                for f in files:
                    makeDirIfNeeded(root.replace('Latest','Previous')+'/'+f)
                    os.system("scp "+root+'/'+f+" "+root.replace('Latest','Previous')+'/'+f)


if __name__ == "__main__":
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--overwrite',  action='store_true', default=False,  help='overwrite all existing plots in "Previous" folder by the output in "Latest"')
    argParser.add_argument('--withinerrors',  action='store_true', default=False,  help='Allow for differences within error')
    args = argParser.parse_args()
    if args.overwrite:
        copyFiles()
    else:
        checkAllOutput(args.withinerrors)
