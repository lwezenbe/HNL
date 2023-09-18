BASE_FOLDER = "/user/lwezenbe/Testing/"

import glob
import os
from ROOT import TFile, TTree
import ROOT
from HNL.Tools.helpers import rootFileContent, getObjFromFile, makeDirIfNeeded
from HNL.Tools.histogram import Histogram
# import uproot

def loadObjects(path, name):
    obj_prev = getObjFromFile(path, name)
    try:
        obj_latest  = getObjFromFile(path.replace("Previous", "Latest"), name)
    except:
        return "Error while trying to access file with path {}".format(path.replace("Previous", "Latest"))
    if obj_latest is None:
        return "Histogram with name '{0}' in file '{1}' is not present in Latest test".format(name, path)
    return (obj_prev, obj_latest)


def compareHist(hist_prev, hist_latest, withinerrors=False):
    if not isinstance(hist_prev, Histogram):
        hist_prev = Histogram(hist_prev)
    if not isinstance(hist_latest, Histogram):
        hist_latest = Histogram(hist_latest)

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
                val_prev = hist_prev.getHist().GetBinContent(xb, yb)
                val_latest = hist_latest.getHist().GetBinContent(xb, yb)
                err_prev = hist_prev.getHist().GetBinError(xb, yb)
                err_latest = hist_latest.getHist().GetBinError(xb, yb)
                if val_prev != val_latest:
                    return "Different content values in bin ({0}, {1}) \n \t {2} += {3} \t ---> \t {4} +- {5}".format(xb, yb, val_prev, err_prev, val_latest, err_latest)
                    
                if err_prev != err_latest:
                    return "Different error values in bin ({0}, {1})".format(xb, yb)

    else:
        x_bins = hist_prev.getHist().GetNbinsX()
        if x_bins != hist_latest.getHist().GetNbinsX():
            return "Different number of bins"

        for xb in xrange(1, x_bins+1):
            if not withinerrors:
                if hist_prev.getHist().GetBinContent(xb) != hist_latest.getHist().GetBinContent(xb):
                    we = compareHist(hist_prev, hist_latest, withinerrors=True)
                    if we is None:
                        return "Different content values in bin {0} \t \t \t WITHIN ERROR FOR ALL BINS. \n \t {1} +- {2} \t ---> \t {3} +- {4}".format(xb, hist_prev.getHist().GetMean(), hist_prev.getHist().GetMeanError(), hist_latest.getHist().GetMean(), hist_latest.getHist().GetMeanError())
                    else:
                        return "Different content values in bin {0} \n \t {1} +- {2} \t ---> \t {3} +- {4}".format(xb, hist_prev.getHist().GetMean(), hist_prev.getHist().GetMeanError(), hist_latest.getHist().GetMean(), hist_latest.getHist().GetMeanError())
                if hist_prev.getHist().GetBinError(xb) != hist_latest.getHist().GetBinError(xb):
                    return "Different error values in bin {0} \n \t {1} +- {2} \t ---> \t {3} +- {4}".format(xb, hist_prev.getHist().GetMean(), hist_prev.getHist().GetMeanError(), hist_latest.getHist().GetMean(), hist_latest.getHist().GetMeanError())
            elif hist_prev.getHist().GetBinError(xb) > 0:
                if abs( hist_prev.getHist().GetBinContent(xb)-hist_latest.getHist().GetBinContent(xb))/hist_prev.getHist().GetBinError(xb) > 1:
                    return  "Out of error bounds"
    
    return None

def compareTrees(tree_prev, tree_latest, withinerrors=False):
    import ROOT
    ROOT.gROOT.SetBatch(True)

    branches_prev = tree_prev.GetListOfBranches()
    branches_latest = tree_latest.GetListOfBranches()
    branches_latest_names = [x.GetName() for x in branches_latest]

    changed_branches = []

    for b in branches_prev:
        if b.GetName() not in branches_latest_names: 
            changed_branches.append('\t'+b.GetName() + ' not in new tree')
            continue
        tree_prev.Draw(b.GetName()+'>>tmp_prev')
        tree_latest.Draw(b.GetName()+'>>tmp_latest')
        try:
            mean_prev = ROOT.gDirectory.Get('tmp_prev').GetMean()
            err_prev = ROOT.gDirectory.Get('tmp_prev').GetMeanError()   
            mean_latest = ROOT.gDirectory.Get('tmp_latest').GetMean()
            err_latest = ROOT.gDirectory.Get('tmp_latest').GetMeanError()
        except:
            print '\t \t branch {0} gives None object'.format(b.GetName())
            continue

        if mean_prev != mean_latest:
            if withinerrors and abs(mean_prev-mean_latest) < err_prev:
                continue
            else:
                changed_branches.append('\t {0}: \t {1} +- {2} \t ---> \t {3} +- {4}'.format(b.GetName(), mean_prev, err_prev, mean_latest, err_latest))

        ROOT.gDirectory.Clear()
    
    if len(changed_branches) == 0:
        return None
    else:
        return  ' \n '.join(changed_branches)

def compareObjects(obj_prev, obj_latest, withinerrors=False):
    if type(obj_prev) != type(obj_latest):
        raise RuntimeError("Types of two objects to compare is different: {0} and {1}".format(type(obj_prev), type(obj_latest)))

    if isinstance(obj_prev, ROOT.TTree):
        return compareTrees(obj_prev, obj_latest, withinerrors = withinerrors)
    else:
        return compareHist(obj_prev, obj_latest, withinerrors = withinerrors)
    

def plotComparison(path, name):
    if getObjFromFile(path.replace("Previous", "Latest"), name) is None: return
    hist_prev = Histogram(getObjFromFile(path, name))
    if not hist_prev.isTH2:
        try:
            hist_latest = Histogram(getObjFromFile(path.replace("Previous", "Latest"), name))
        except:
            return


        from HNL.Plotting.plot import Plot
        p = Plot(hist_prev, ['Previous', 'Latest'], name, bkgr_hist=hist_latest, draw_ratio = True, year = '2016', era='prelegacy',
                                    color_palette = 'Didar', color_palette_bkgr = 'Lines')
        p.drawHist(path.replace("Previous", "Plots").rsplit('/', 1)[0], bkgr_draw_option = "EHist")

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
    print '\t Checking', f
    in_file = TFile(f, "read")
    list_of_hist_names = []
    for c in rootFileContent(in_file, basepath='', getNested=True):
        list_of_hist_names.append(c[0])
    in_file.Close()

    out_file_name = '/user/lwezenbe/Testing/LOG'+f.split('Previous')[-1].split('.')[0]+'.txt'

    #out_file_name = f.replace('Previous', 'LOG').split('.')[0]+'.txt'
    makeDirIfNeeded(out_file_name)
    out_file = open(out_file_name, 'w')
    everything_clear = True
    faulty_hn = []
    
    for hn in list_of_hist_names:
        if 'cutflow' in hn: continue
        obj = loadObjects(f, hn)
        if isinstance(obj, str):
            everything_clear = False
            out_file.write(hn+': '+obj+'\n')
            faulty_hn.append('\t ' +hn+': '+obj+'\n')
            continue
        
        obj_prev, obj_latest = obj
        test_result = compareObjects(obj_prev, obj_latest)
        if test_result is not None:
            if withinerrors and 'WITHIN ERROR' in test_result:
                continue
            everything_clear = False
            out_file.write(hn+': '+test_result+'\n')
            faulty_hn.append('\t ' +hn+': '+test_result+'\n')
#            try:
#                if not isinstance(obj_prev, TTree): plotComparison(f, hn)
#            except:
#                pass

        del obj_prev, obj_latest

    if everything_clear:
        out_file.write("EVERYTHING CLEAR")
        out_file.close()
    else:
        out_file.close()
        return faulty_hn
    
    return None

def checkSubdirOutput(subdir, withinerrors=False):
    list_of_files_to_test = []
    for root, dirs, files in os.walk(BASE_FOLDER+'Previous/'+subdir, topdown=False):
        if len(files) > 0: 
            for f in files:
                list_of_files_to_test.append(root+'/'+f)
    faulty_files = {}
    for ft in list_of_files_to_test:
        cf = compareFiles(ft, withinerrors)
        if compareFiles(ft, withinerrors) is not None: faulty_files[ft] = [x for x in cf]

    return faulty_files


def checkAllOutput(withinerrors=False):
    subdir_list = glob.glob(BASE_FOLDER+'Previous/*')
    subdir_list = [s.split('/')[-1] for s in subdir_list]

    faulty_sd = []
    for sd in subdir_list:
        print "Checking", sd
        makeDirIfNeeded(BASE_FOLDER+'LOG/'+sd+'/x')
        faulty_files = checkSubdirOutput(sd, withinerrors)
        out_file = open(BASE_FOLDER+'LOG/'+sd+'/FULLREPORT.txt', 'w')
        if len(faulty_files.keys()) == 0:
            out_file.write("EVERYTHING CLEAR")
        else:
            faulty_sd.append(sd)
            out_file.write("Problems in the following files: \n")
            for f in faulty_files.keys():
                out_file.write(f+' \n')
                for cf in faulty_files[f]:
                    out_file.write(cf)
        out_file.close()

    tot_file = open(BASE_FOLDER+'/totalreport.txt', 'w')
    if len(faulty_sd) == 0:
        tot_file.write("EVERYTHING CLEAR")
    else:
        tot_file.write("Problems in the following scripts: \n")
        for fsd in faulty_sd:
            tot_file.write(fsd+' \n')
    tot_file.close()

def copyFiles():
    os.system('rm -r '+BASE_FOLDER+'Previous/*')
    os.system('rm -r '+BASE_FOLDER+'Plots/*')
    os.system('rm -r '+BASE_FOLDER+'LOG/*')

    subdir_list = glob.glob(BASE_FOLDER+'Latest/*')
    subdir_list = [s.split('/')[-1] for s in subdir_list]

    for sd in subdir_list:
        for root, dirs, files in os.walk(BASE_FOLDER+'Latest/'+sd, topdown=False):
            if len(files) > 0: 
                for f in files:
                    makeDirIfNeeded(root.replace('Latest','Previous')+'/'+f)
                    os.system("scp "+root+'/'+f+" "+root.replace('Latest','Previous')+'/'+f)

    os.system('rm -r '+BASE_FOLDER+'Latest/*')

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
