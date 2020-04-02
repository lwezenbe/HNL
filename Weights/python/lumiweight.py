from HNL.Samples.sample import getListOfPathsWithSameOutput 
LUMINOSITY_MAP = {2016 : 35546.}

class LumiWeight:

    def __init__(self, sample, input_file):
        self.sample = sample
        self.lumi_weight = 1.  

        self.total_hcount = self.sample.hcount
        for path_name in getListOfPathsWithSameOutput(input_file, self.sample.name):
            self.total_hcount += self.sample.getHist('hCounter', path_name).GetSumOfWeights()

    def getLumiWeight(self):
        self.lumi_weight = self.sample.chain._weight*(self.sample.xsec*LUMINOSITY_MAP[self.sample.chain.year])/self.total_hcount
        return self.lumi_weight 

if __name__ == '__main__':
    from HNL.Samples.sample import createSampleList, getSampleFromList
    import os
    input_file = os.path.expandvars('$CMSSW_BASE/src/HNL/Samples/InputFiles/samples_for_testing.conf')
    sample_list = createSampleList(input_file)
    sample = getSampleFromList(sample_list, 'DYJetsToLL-M-10to50')

    chain = sample.initTree()
    lw = LumiWeight(sample, input_file)
    chain.GetEntry(5)
    chain.year = 2016
    print sample.name
    print lw.getLumiWeight() 
    print 'chain._weight: ', chain._weight, 'expected -41444.199'
    print 'xsec ', sample.xsec, lw.sample.xsec, 'expected 18610'
    print 'luminosity ', LUMINOSITY_MAP[chain.year], 'expected 35546.'
    print 'hCount ', sample.hcount, lw.total_hcount, 'more than 2.05023673303e+12'
