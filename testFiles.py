import glob
all_files = glob.glob("/pnfs/iihe/cms/store/user/lwezenbe/skimmedTuples/HNL/default/UL2017/Reco/tmp_ZGToLLG_01J_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8/*root")
#all_files = glob.glob("/pnfs/iihe/cms/store/user/lwezenbe/skimmedTuples/HNL/default/UL2017/Reco/tmp_ZZTo4L*/*root")
#all_files = glob.glob("/pnfs/iihe/cms/store/user/lwezenbe/skimmedTuples/HNL/default/UL2017/Reco/tmp_TTWJetsToLNu*/*root")
import ROOT
for f in sorted(all_files):
    print f
    in_file = ROOT.TFile(f, 'r')
    in_tree = in_file.Get('blackJackAndHookers/blackJackAndHookersTree')
    in_tree.GetEntry(10)
