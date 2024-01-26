def extractCovariance(original_file, out_name, channel_dict = None, custom_labels = None):
    from ROOT import TFile
    in_file = TFile(original_file, 'read')

    from HNL.Tools.helpers import rootFileContent
    rfc = rootFileContent(in_file, starting_dir = 'shapes_fit_b') 
    channels = [x[0].split('/')[-1] for x in rfc] 
    in_file.Close()

    from HNL.HEPData.settings import hepdata_folder
    new_file_name = hepdata_folder + '/data/Covar/'+out_name+'.root'
    from HNL.Tools.helpers import makeDirIfNeeded
    makeDirIfNeeded(new_file_name)
    out_file = TFile(new_file_name, 'recreate')

    from HNL.Tools.helpers import getObjFromFile
    for ch in channels:
        tmp_obj = getObjFromFile(original_file, 'shapes_fit_b/{0}/total_covar'.format(ch))

        if custom_labels is not None:
            for i, n in enumerate(custom_labels):
                tmp_obj.GetXaxis().SetBinLabel(i+1, n)
                tmp_obj.GetYaxis().SetBinLabel(i+1, n)

        try:
            out_name = channel_dict[ch]
        except:
            out_name = ch
        out_file.WriteObject(tmp_obj, out_name)
        

    out_file.Close()

if __name__ == '__main__':
    extractCovariance('/ada_mnt/ada/user/lwezenbe/private/PhD/Analysis_CMSSW_10_2_22/CMSSW_10_2_22/src/HNL/Stat/data/output/Majorana/UL2016post-2016pre-2017-2018/default-lowMassSRloose/tau/HNL-tau-m30-Vsq5.0em04-prompt/shapes/singlecard/postfit/MaxOneTau/fitDiagnosticsTest.root', 'test', custom_labels = ['La{0}'.format(x) for x in range(1, 9)] + ['Lb{0}'.format(x) for x in range(1, 9)])
