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
        self.lumi_weight = self.chain._weight*(self.sample.xsec*LUMINOSITY_MAP[self.chain.year])/self.total_hcount
        return self.lumi_weight 

if __name__ == '__main__':
    from HNL.Samples.sample import createSampleList, getSampleFromList
    import os
    input_file = os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/sampleList_2016_noskim.conf')
    sample_list = createSampleList(input_file)

    for sample in sample_list:
        chain = sample.initTree()
        lw = LumiWeight(sample, chain)
        chain.GetEntry(5)
        chain.year = 2016
        print sample.name
        print lw.getLumiWeight() 
        print 'chain._weight: ', chain._weight, lw.chain._weight
        print 'xsec ', sample.xsec, lw.sample.xsec
        print 'luminosity ', LUMINOSITY_MAP[chain.year]
        print 'hCount ', sample.hcount, lw.total_hcount
