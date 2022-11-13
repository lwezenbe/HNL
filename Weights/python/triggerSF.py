class TriggerSF(object):

    def __init__(self, era, year):
        from HNL.Tools.helpers import getObjFromFile
        import os
        input_file_location = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Weights', 'data', 'triggerSF', era+year, 'triggerSF.root'))
        self.sf_hist_leadingmuon = getObjFromFile(input_file_location, 'LeadingLightLepMuon') 
        self.sf_hist_leadingelectron = getObjFromFile(input_file_location, 'LeadingLightLepElectron') 

        self.leading_muon_max = self.sf_hist_leadingmuon.GetBinLowEdge(self.sf_hist_leadingmuon.FindLastBinAbove() + 1)
        self.leading_muon_min = self.sf_hist_leadingmuon.GetBinLowEdge(self.sf_hist_leadingmuon.FindFirstBinAbove())
        self.leading_electron_max = self.sf_hist_leadingelectron.GetBinLowEdge(self.sf_hist_leadingelectron.FindLastBinAbove() + 1)
        self.leading_electron_min = self.sf_hist_leadingelectron.GetBinLowEdge(self.sf_hist_leadingelectron.FindFirstBinAbove())

    def getSF(self, chain, syst='nominal'):
        pt_to_use = chain.light_pt[0]
        flavor_to_use = chain.light_flavor[0]
        if flavor_to_use == 0:
            pt_to_use = max(self.leading_electron_min + 0.001, min(self.leading_electron_max-0.001, pt_to_use))                    
            return self.sf_hist_leadingelectron.GetBinContent(self.sf_hist_leadingelectron.FindBin(pt_to_use))
        elif flavor_to_use == 1:
            pt_to_use = max(self.leading_muon_min + 0.001, min(self.leading_muon_max-0.001, pt_to_use))                    
            return self.sf_hist_leadingmuon.GetBinContent(self.sf_hist_leadingmuon.FindBin(pt_to_use))
        else:
            return 1.

class CombinedTriggerSF(object):
    
    def __init__(self):
        from HNL.Tools.helpers import getObjFromFile
        import os
        input_file_location = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Weights', 'data', 'triggerSF', 'triggerSF.root'))
        self.sf_hist_nominal = getObjFromFile(input_file_location, 'sf_nominal')
        self.sf_hist_up = getObjFromFile(input_file_location, 'sf_up')
        self.sf_hist_down = getObjFromFile(input_file_location, 'sf_down')
    
        self.leading_max = self.sf_hist_nominal.GetBinLowEdge(self.sf_hist_nominal.FindLastBinAbove() + 1)
        self.leading_min = self.sf_hist_nominal.GetBinLowEdge(self.sf_hist_nominal.FindFirstBinAbove())
    
    def getSF(self, chain, syst='nominal'):
        pt_to_use = chain.light_pt[0]
        pt_to_use = max(self.leading_min + 0.001, min(self.leading_max-0.001, pt_to_use))        
        if syst == 'nominal':   
            return 1.         
            #return self.sf_hist_nominal.GetBinContent(self.sf_hist_nominal.FindBin(pt_to_use)) 
        elif syst == 'statup':
            return 1+self.sf_hist_up.GetBinContent(self.sf_hist_up.FindBin(pt_to_use)) 
        elif syst == 'statdown':
            return 1-self.sf_hist_down.GetBinContent(self.sf_hist_down.FindBin(pt_to_use)) 
        else:
            raise RuntimeError('Unknown syst')
