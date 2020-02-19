from HNL.Samples.sample import getListOfPathsWithSameOutput 
LUMINOSITY_MAP = {2016 : 35546.}

class LumiWeight:

    def __init__(self, sample, chain, input_file = None):
        self.sample = sample
        self.chain = chain
        self.lumi_weight = 1.  
 
        self.total_hcount = self.sample.hcount
        if input_file is not None:
            for path_name in getListOfPathsWithSameOutput(input_file, self.sample.name):
                self.total_hcount += self.sample.getHist('hCounter', path_name).GetSumOfWeights()

    def getLumiWeight(self):
        print self.sample.name, self.sample.hcount
        print self.chain._weight, self.sample.xsec, LUMINOSITY_MAP[self.chain.year], self.total_hcount
        self.lumi_weight = self.chain._weight*(self.sample.xsec*LUMINOSITY_MAP[self.chain.year])/self.total_hcount
        print self.lumi_weight
        return self.lumi_weight 

if __name__ == '__main__':
    from HNL.Samples.sample import createSampleList, getSampleFromList
    import os
    input_file = os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/compareTauIdList_2016.conf')
    sample_list = createSampleList(input_file)

    for sample in sample_list:
        chain = sample.initTree()
        lw = LumiWeight(sample, chain)
        chain.GetEntry(5)
        chain.year = 2016
        print sample, sample.hcount, lw.total_hcount
