class DisplacementReweighter:
    
    def __init__(self, original_samples, **kwargs):
        from HNL.Tools.helpers import makeList
        self.original_samples = makeList(original_samples)

        masstype = kwargs.get('masstype', 'Majorana')

        self.original_ntot = []   
        self.original_meanctau = []
        self.original_coupling_squared = []
        self.original_xsec = []
        for sample in self.original_samples:
            if masstype == 'Majorana':
                self.original_ntot.append(sample.getHist('hCounter'))
            elif masstype == 'Dirac':
                self.original_ntot.append(sample.getHist('hCounterDirac'))
            else:
                raise RuntimeError('masstype {0} not allowed in displacementReweighter'.format(masstype))
            
            self.original_meanctau.append(self.getMeanLifetime(sample.name))
            self.original_xsec.append(sample.xsec)
            
            from HNL.Samples.sample import Sample
            self.original_coupling_squared.append(Sample.getSignalCouplingSquared(sample.name))

    def getMeanLifetimeDict(self): 
        import os, json
        in_file_path = os.path.expandvars(os.path.join('$CMSSW_BASE', 'src', 'HNL', 'Weights', 'data', 'meanCtaulist.json'))
        with open(in_file_path, 'r') as read_file:
            self.mean_ctau_list = json.load(read_file)
        return self.mean_ctau_list  

    def getMeanLifetime(self, sample_name):
        try:
            return self.mean_ctau_list[sample_name]
        except:
            self.getMeanLifetimeDict()
            return self.getMeanLifetime(sample_name)

    def calculateNewLumiWeightBase(self, target_coupling_squared, ct):
    #    print 'NEW:'
    #    print '---'
    #    print 'V2: \t', self.original_coupling_squared[0], '->', target_coupling_squared
        new_mean_ctau = self.original_meanctau[0] * self.original_coupling_squared[0] / target_coupling_squared
        new_xsec = self.original_xsec[0] * target_coupling_squared / self.original_coupling_squared[0]
    #    print 'ctau \t', self.original_meanctau[0], '->', new_mean_ctau
    #    print 'xsec \t', self.original_xsec[0], '->', new_xsec  
    #    print 'ct \t', ct
        exp_sum = 0.
        from math import exp
        for i in xrange(len(self.original_samples)):
            exp_sum = self.original_ntot[i].GetSumOfWeights() / self.original_meanctau[i] * exp(-ct / self.original_meanctau[i])
    #    print exp_sum, exp( -ct / new_mean_ctau), new_xsec / new_mean_ctau * exp( -ct / new_mean_ctau) / exp_sum, '\n'
        return new_xsec / new_mean_ctau * exp( -ct / new_mean_ctau) / exp_sum
        

    def getRangeOfNewLumiWeights(self, ct, lumi, range_of_targets = None):
        if range_of_targets is None:
            range_of_targets = [1e-1, 2.5e-1, 5e-1, 7.5e-1, 1e-2, 2.5e-2, 5e-2, 7.5e-2, 1e-3, 2.5e-3, 5e-3, 7.5e-3, 1e-4, 2.5e-4, 5e-4, 7.5e-4, 1e-5, 2.5e-5, 5e-5, 7.5e-5, 1e-6, 2.5e-6, 5e-6, 1e-7, 5e-7, 1e-8, 5e-8]
    
        range_of_targets = sorted(range_of_targets)
        lumi_weights = [self.calculateNewLumiWeightBase(target, ct)*lumi for target in range_of_targets]
        return range_of_targets, lumi_weights


